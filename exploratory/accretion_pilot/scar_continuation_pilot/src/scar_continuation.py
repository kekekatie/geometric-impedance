#!/usr/bin/env python3
"""
scar_continuation.py -- Phase 2: scar-tolerant continuation.

Scar-tolerant scheduling changes ONLY the halt rule of the frozen patient
scheduler (see PROTOCOL.md): a zero-candidate frontier site is pinned as a dormant
`pinned_scar` (removed from the active queue) instead of triggering a global jam;
the remaining growable sites continue under the identical patient logic and the
same PRNG stream. Legality stays 100% strict (frozen Patch.legal / D.candidates).
We replay from step 0 with scar-tolerance enabled throughout, so pre-jam steps are
bit-identical to the baseline and the post-jam run is a new, disclosed trajectory.

Writes results/phase2_scar_continuation.json and .csv.
"""
from __future__ import annotations
import json, csv, math, random, collections
import scar_common as SC
from scar_common import L, D, S, SN, ordered, dk, ekey


def patient_scar(P, rng, scars, verify_legal=True):
    """One scar-tolerant slice. `scars` (set of pinned edge-keys) is mutated.
    Returns (status, n_placed, kind, newly_pinned_list, illegal_count).
    status in {'ok','total_arrest'}."""
    fr = P.frontier()
    forced = {}
    growable = []
    newly = []
    illegal = 0
    for e in fr:
        ek = ekey(e[0], e[1])
        if ek in scars:
            continue
        cs = D.candidates(P, *e[:3])
        if not cs:
            scars.add(ek); newly.append(ek); continue
        growable.append((e, cs))
        if len(cs) == 1:
            forced.setdefault(D.dkey(cs[0]), cs[0])
    if not growable:
        return "total_arrest", 0, None, newly, illegal
    if forced:
        n = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); n += 1
            elif verify_legal:
                pass  # a forced candidate made illegal by a sibling placement is simply skipped (baseline behaviour)
        return "ok", n, "forced", newly, illegal
    e0, cs0 = growable[0]
    t = rng.choice(ordered(cs0))
    if verify_legal and not P.legal(t):
        illegal += 1            # must never happen: candidates come from D.candidates (legal by construction)
    P.add(t)
    return "ok", 1, "guess", newly, illegal


def scar_grow(world, si, steps=44, record_illegal=False):
    """Replay from step 0 with scar-tolerance. Returns the grown full patch, the
    per-step log, the pinned scars, and bookkeeping."""
    forks = SC.RD.load_forks()
    Sstar = forks[world]["Sstar"]; cs = forks[world]["cs"]; B = cs[1]
    stream = SC.PC.streams_for(world)[si]
    Q = L.Patch(list(Sstar)); Q.add(B)
    rng = random.Random(stream)
    scars = set()
    bkey = dk(B)
    jam_step = None
    illegal_total = 0
    log = []
    choice_departs = None
    # retained-band membership of B, tracked under ordinary pruning per step
    for s in range(1, steps + 1):
        n0 = len(Q.tris)
        status, n, kind, newly, illegal = patient_scar(Q, rng, scars, verify_legal=record_illegal)
        illegal_total += illegal
        if newly and jam_step is None:
            jam_step = s                      # first pin == the baseline jam step
        # choice-tile departure under pruning (first step B leaves the retained band)
        if choice_departs is None:
            band_s, _ = SC.PC.skin_of(list(Q.tris))
            if bkey not in {dk(t) for t in band_s}:
                choice_departs = s
        log.append(dict(step=s, placed=n, kind=kind, newly_pinned=len(newly),
                        total_scars=len(scars), n_tiles=len(Q.tris), status=status))
        if status == "total_arrest":
            break
    final_step = log[-1]["step"] if log else 0
    full = list(Q.tris)
    band, _ = SC.PC.skin_of(full)
    return dict(world=world, si=si, stream=stream, Sstar=Sstar, cs=cs, B=B,
                jam_step=jam_step, final_step=final_step,
                reached_44=(final_step == steps and log[-1]["status"] != "total_arrest"),
                total_arrest=(log[-1]["status"] == "total_arrest") if log else False,
                illegal_placements=illegal_total,
                scars=sorted([sorted(list(ek)) for ek in scars]),
                n_scars=len(scars),
                choice_departs_step=choice_departs,
                log=log, full=full, band=band)


def scar_geometry(res):
    """Connected-component count and angular span of the pinned scar edges."""
    scars = [frozenset(map(tuple, ek)) for ek in res["scars"]]
    # components: scar edges sharing a vertex key
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)
    vert_to_edges = collections.defaultdict(list)
    for i, ek in enumerate(scars):
        for v in ek:
            vert_to_edges[v].append(i)
        find(i)
    for v, es in vert_to_edges.items():
        for j in es[1:]:
            union(es[0], j)
    ncomp = len({find(i) for i in range(len(scars))}) if scars else 0
    # angular span around band centroid
    band = res["band"]
    c = sum(z for t in band for z in t[1:]) / (3 * len(band)) if band else 0
    angs = []
    for ek in scars:
        pts = [complex(*v) for v in ek]
        m = sum(pts) / len(pts)
        angs.append(math.atan2((m - c).imag, (m - c).real))
    if len(angs) >= 2:
        angs_sorted = sorted(angs)
        gaps = [angs_sorted[(i + 1) % len(angs_sorted)] - angs_sorted[i] for i in range(len(angs_sorted) - 1)]
        gaps.append(2 * math.pi - (angs_sorted[-1] - angs_sorted[0]))
        span = 2 * math.pi - max(gaps)
    else:
        span = 0.0
    return dict(n_scar_edges=len(scars), n_scar_components=ncomp,
               scar_angular_span=round(span, 4),
               localized=(ncomp <= 2 and span <= math.pi / 2 + 1e-9))


def main(cases=None):
    SC.RESULTS.mkdir(parents=True, exist_ok=True)
    cases = cases or SC.B_JAMS
    out = []
    for (w, si) in cases:
        print(f"[phase2] w{w}-B-s{si} ...", flush=True)
        res = scar_grow(w, si, steps=44, record_illegal=True)
        geo = scar_geometry(res)
        rec = dict(case=f"w{w}-B-s{si}", world=w, si=si, stream=res["stream"],
                   jam_step=res["jam_step"], final_step=res["final_step"],
                   reached_step_44=res["reached_44"], total_arrest=res["total_arrest"],
                   n_tiles_final=len(res["full"]),
                   tiles_added_after_jam=len(res["full"]) - _tiles_at(res, res["jam_step"]),
                   illegal_placements=res["illegal_placements"],
                   n_band_tiles_final=len(res["band"]),
                   choice_departs_step=res["choice_departs_step"],
                   **geo)
        out.append(rec)
        print(f"   jam@{rec['jam_step']} -> final step {rec['final_step']} "
              f"(reached44={rec['reached_step_44']}, arrest={rec['total_arrest']}); "
              f"+{rec['tiles_added_after_jam']} tiles; scars={rec['n_scar_edges']} "
              f"in {rec['n_scar_components']} comp, span {rec['scar_angular_span']}; "
              f"illegal={rec['illegal_placements']}", flush=True)
    (SC.RESULTS / "phase2_scar_continuation.json").write_text(json.dumps(out, indent=2, default=float))
    with open(SC.RESULTS / "phase2_scar_continuation.csv", "w", newline="") as f:
        wtr = csv.writer(f)
        cols = ["case", "jam_step", "final_step", "reached_step_44", "total_arrest",
                "tiles_added_after_jam", "n_scar_edges", "n_scar_components",
                "scar_angular_span", "localized", "choice_departs_step", "illegal_placements"]
        wtr.writerow(cols)
        for r in out:
            wtr.writerow([r.get(k) for k in cols])
    print("wrote results/phase2_scar_continuation.json + .csv")
    return out


def _tiles_at(res, step):
    for e in res["log"]:
        if e["step"] == step:
            return e["n_tiles"]
    return len(res["full"])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--core":
        main(cases=[(7, 0), (5, 0)])
    else:
        main()
