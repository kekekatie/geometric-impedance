#!/usr/bin/env python3
"""
phase3_repair.py -- Phase 3: legal single-move repair feasibility.

Frozen protocol: protocol/PHASE3_PROTOCOL.md. For each reconstructible B jam:
  * faithfully REPLAY the arm on the frozen ActiveSkin engine to the jam trigger;
  * locate the dead (zero-candidate) frontier sites;
  * enumerate three-rhombus hexagon flips in the retained skin;
  * classify each: flip-exists-as-phason (alternative dissection legal in
    isolation) vs fully-legal-in-context; and eligible (cluster shares a vertex
    with a dead site, and the hexagon's 6 boundary edges are all interior so the
    true frontier bookkeeping is unchanged);
  * attempt the FIRST fully-legal eligible flip under the frozen deterministic
    order; test whether it un-jams (dead sites gain candidates); resume growth
    with the original scheduler + RNG to the step-44 horizon; compare with the
    no-repair replay (which re-jams immediately).

Outputs under ../results/phase3/: per-case JSON + phase3_report.txt.
No matching rule is relaxed; legality is the frozen engine's.
"""
from __future__ import annotations
import json, pickle, random
from pathlib import Path
import pilot_common as PC
from pilot_common import L, D, S, SN, Sl
import engine_bridge as EB
import active_skin_engine as ASE
import hexflip as HF

OUT = Path(__file__).resolve().parent.parent / "results" / "phase3"
FORKS = Path(__file__).resolve().parent.parent / "results" / "baseline" / "forks.pkl"
JAMDIR = Path(__file__).resolve().parent.parent / "results" / "baseline" / "jam_cases"

# the 11 reconstructible B jams: (world, stream_idx, jam_step)
B_JAMS = [(5, 0, 42), (7, 0, 23), (7, 1, 23), (15, 0, 39), (19, 0, 39),
          (19, 1, 43), (21, 0, 42), (21, 1, 42), (28, 0, 39), (28, 1, 43), (29, 1, 43)]


def load_forks():
    data = pickle.loads(FORKS.read_bytes())
    return {w: dict(Sstar=[(int(t[0]),) + tuple(t[1:]) for t in d["Sstar"]],
                    cs=[(int(c[0]),) + tuple(c[1:]) for c in d["cs"]]) for w, d in data.items()}


def replay_to_trigger(Sstar, B, stream, jam_step):
    """Replay the arm on the frozen ActiveSkin engine through jam_step-1 successful
    steps. Returns (P, rng) at the jam trigger. Asserts the next patient step JAMs."""
    P = ASE.ActiveSkin(list(Sstar) + [B], radius=2)
    rng = random.Random(stream)
    for s in range(1, jam_step):
        st, n, kind = SN.patient(P, rng)
        assert st != "JAM", f"unexpected early jam at step {s} (expected {jam_step})"
        P.prune()
    return P, rng


def dead_sites(P):
    out = []
    for e in P.frontier():
        if len(D.candidates(P, *e[:3])) == 0:
            out.append(e)
    return out


def local(tiles, centre, r=4.0):
    return [t for t in tiles if abs(HF.tile_centroid(t) - centre) < r * S]


def classify_hexagon(h, skin_tiles, dead_vkeys, true_frontier_edgekeys):
    """Return a dict classifying a flip hexagon: interior (boundary all interior),
    eligible (shares a vertex with a dead site), flip_phason (alt legal in
    isolation), legal_in_context (alt legal in full skin), unjam-ability deferred."""
    hext = h["tiles"]
    sdk = {HF.dkey(u) for u in hext}
    bverts = set(h["bverts"])
    boundary, _ = HF._hexagon_boundary(hext)
    # interior: none of the 6 boundary edges is on the true frontier
    interior = not any(ek in true_frontier_edgekeys for ek in boundary)
    eligible = interior and bool(bverts & dead_vkeys)
    hc = sum(complex(*k) for k in h["bverts"]) / 6
    base = [t for t in skin_tiles if HF.dkey(t) not in sdk]
    surr_full = local(base, hc)
    # phason: relax external star constraint by dropping surround tiles that touch
    # the hexagon boundary vertices (the alternative dissection as a Penrose pattern)
    surr_relaxed = [t for t in surr_full
                    if not any(L.key(z) in bverts for z in HF.tile_vertices(t))]
    orig = tuple(sorted(HF.dkey(t) for t in hext))
    sols_r, look_r = HF.enumerate_hexagon_fillings(hext, surr_relaxed, legality="engine", max_solutions=8)
    sols_f, look_f = HF.enumerate_hexagon_fillings(hext, surr_full, legality="engine", max_solutions=8)
    flip_phason = any(s != orig for s in sols_r)
    alts_legal = [s for s in sols_f if s != orig]
    return dict(h=h, interior=interior, eligible=eligible, flip_phason=flip_phason,
                legal_in_context=bool(alts_legal), alts_legal=alts_legal,
                lookup_full=look_f, orig=orig, boundary=boundary)


def apply_flip(P, old6_dks, new6_tiles):
    """Swap the hexagon's 6 tiles in the ActiveSkin tile index, keeping the true
    frontier boundary dict unchanged (the hexagon's outer boundary is interior)."""
    newtiles = [t for t in P.tris if HF.dkey(t) not in old6_dks] + list(new6_tiles)
    idx = L.Patch(newtiles)
    P.tris, P.edges, P.V = idx.tris, idx.edges, idx.V
    # P.boundary unchanged


def run_case(world, stream_idx, jam_step, forks):
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[stream_idx]
    tag = f"w{world}-B-s{stream_idx}"

    # ---- replay to trigger (faithful) ----
    P, rng = replay_to_trigger(Sstar, B, stream, jam_step)
    rng_state = rng.getstate()
    skin_tiles = list(P.tris)
    fr = P.frontier()
    true_fr_keys = {frozenset((L.key(e[0]), L.key(e[1]))) for e in fr}
    deads = dead_sites(P)
    dead_vkeys = set()
    for e in deads:
        dead_vkeys.add(L.key(e[0])); dead_vkeys.add(L.key(e[1]))

    # no-repair baseline: the next patient step must JAM at the dead site
    P_nr, rng_nr = replay_to_trigger(Sstar, B, stream, jam_step)
    st_nr, _, _ = SN.patient(P_nr, rng_nr)
    norepair_jams = (st_nr == "JAM")

    # ---- enumerate flip hexagons near the dead sites ----
    dead_mids = [(e[0] + e[1]) / 2 for e in deads]
    search_tiles = [t for t in skin_tiles
                    if any(abs(HF.tile_centroid(t) - m) < 3 * S for m in dead_mids)]
    # detect hexagons in a neighbourhood that includes the search tiles' context
    nbhd = [t for t in skin_tiles
            if any(abs(HF.tile_centroid(t) - m) < 5 * S for m in dead_mids)]
    hexes = HF.find_flip_hexagons(nbhd)

    classified = [classify_hexagon(h, skin_tiles, dead_vkeys, true_fr_keys) for h in hexes]
    n_geom = sum(1 for c in classified if c["flip_phason"])
    n_legal = sum(1 for c in classified if c["legal_in_context"])
    n_interior = sum(1 for c in classified if c["interior"])
    n_eligible_geom = sum(1 for c in classified if c["eligible"] and c["flip_phason"])
    eligibles = [c for c in classified if c["eligible"] and c["legal_in_context"]]

    result = dict(
        case=tag, world=world, stream_idx=stream_idx, jam_step=jam_step, horizon=PC.STEPS,
        n_skin_tiles=len(skin_tiles), n_dead_sites=len(deads),
        norepair_jams_immediately=norepair_jams,
        n_flip_hexagons=len(hexes),
        n_flip_phason=n_geom,          # geometric candidates (phason flip exists in isolation)
        n_interior=n_interior,         # closed hexagons whose 6 edges are all interior
        n_eligible_geom=n_eligible_geom,  # eligible geometric moves (interior & touch a dead site)
        n_legal_in_context=n_legal,    # fully legal candidates (in surrounding skin)
        n_eligible_legal=len(eligibles),  # legal AND touch a dead site (could un-jam)
        outcome=None, repair=None,
    )

    if not eligibles:
        # (a) no eligible geometric move, or (b) geometric but none legal
        if n_eligible_geom == 0:
            result["outcome"] = "a_no_eligible_geometric_move"
        elif n_legal == 0:
            result["outcome"] = "b_geometric_but_none_legal"
        else:
            result["outcome"] = "b2_legal_but_none_eligible"
        return result

    # ---- frozen deterministic order over eligible legal moves ----
    def order_key(c):
        vkey = c["h"]["vertex"]
        vz = complex(*vkey)
        dmin = min(abs(vz - m) for m in dead_mids)
        return (round(dmin, 9), vkey, tuple(sorted(c["alts_legal"][0])))
    eligibles.sort(key=order_key)
    chosen = eligibles[0]
    alt = chosen["alts_legal"][0]
    new6 = [chosen["lookup_full"][dk] for dk in alt]
    old6 = {HF.dkey(t) for t in chosen["h"]["tiles"]}

    # ---- apply + un-jam test + resume ----
    apply_flip(P, old6, new6)
    rng.setstate(rng_state)
    deads_after = dead_sites(P)
    unjammed = len(deads_after) == 0
    result["repair"] = dict(
        flip_vertex=list(chosen["h"]["vertex"]),
        n_dead_before=len(deads), n_dead_after=len(deads_after),
        unjammed_local=unjammed,
    )
    if not unjammed:
        result["outcome"] = "c_repair_attempted_no_unjam"  # legal flip applied but dead site persists
        return result

    # resume growth with original scheduler + RNG to the horizon
    steps_done = 0; rejam_at = None; reached = False
    for s in range(jam_step, PC.STEPS + 1):
        st, n, kind = SN.patient(P, rng)
        if st == "JAM":
            rejam_at = s; break
        P.prune()
        steps_done += 1
        if s == PC.STEPS:
            reached = True
    result["repair"].update(dict(resume_steps=steps_done, rejam_at=rejam_at, reached_horizon=reached))
    if rejam_at is not None:
        result["outcome"] = "e_later_rejam"
    elif reached:
        result["outcome"] = "f_reached_horizon"
    else:
        result["outcome"] = "d_growth_restored"
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    forks = load_forks()
    results = []
    for (w, si, js) in B_JAMS:
        print(f"[phase3] {w}-B-s{si} (jam {js})...", flush=True)
        r = run_case(w, si, js, forks)
        results.append(r)
        (OUT / f"{r['case']}.json").write_text(json.dumps(r, indent=2, default=float))
        print(f"    outcome={r['outcome']} dead={r['n_dead_sites']} "
              f"hex={r['n_flip_hexagons']} phason={r['n_flip_phason']} "
              f"legal={r['n_legal_in_context']} eligible_legal={r['n_eligible_legal']}", flush=True)

    # report
    from collections import Counter
    oc = Counter(r["outcome"] for r in results)
    lines = []
    lines.append("Phase 3 -- legal single-move (three-rhombus hexagon flip) repair feasibility")
    lines.append(f"cases (reconstructible B jams): {len(results)}")
    lines.append("")
    lines.append(f"{'case':>12} {'dead':>4} {'hex':>4} {'phason':>6} {'intr':>4} {'eligG':>5} {'legal':>5} {'eligL':>5} {'outcome':>28}")
    for r in results:
        lines.append(f"{r['case']:>12} {r['n_dead_sites']:>4} {r['n_flip_hexagons']:>4} "
                     f"{r['n_flip_phason']:>6} {r.get('n_interior',0):>4} {r.get('n_eligible_geom',0):>5} "
                     f"{r['n_legal_in_context']:>5} {r['n_eligible_legal']:>5} "
                     f"{str(r['outcome']):>28}")
    lines.append("")
    lines.append("outcome tally:")
    for k, v in sorted(oc.items()):
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("Legend: phason = alt dissection legal in isolation (geometric candidate); intr = closed")
    lines.append("hexagons (6 interior edges); eligG = geometric & eligible (interior & touches a dead site);")
    lines.append("legal = fully legal in the surrounding skin; eligL = legal AND eligible (could un-jam).")
    lines.append("no-repair baseline re-jams immediately for all cases: "
                 f"{all(r['norepair_jams_immediately'] for r in results)}")
    txt = "\n".join(lines)
    (OUT / "phase3_report.txt").write_text(txt + "\n")
    print("\n" + txt)


if __name__ == "__main__":
    main()
