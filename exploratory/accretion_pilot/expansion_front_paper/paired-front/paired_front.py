#!/usr/bin/env python3
"""
paired_front.py -- Phase-1 of the paired-front pilot (Astra's reframed question).

QUESTION (physical half): from one common saturated state S* where a fork still has two legal options,
commit A in one arm and B in the other, then grow BOTH with ordinary patient-scheduler growth (not a
forced-only burst). Is there a difference at the *current active front*, and does it outlive the moment
the original choice-tiles themselves leave the retained skin?

Honest design, per the handover (HANDOVER_REPLY.md):
  * common state S* = forced-saturated, fork verified to still have 2 options, preserved exactly.
  * ordinary continuing growth in both arms, FIXED reproducible RNG coupling (a declared convention,
    NOT an identity once the fronts diverge -- hence the A-vs-A controls carry the load).
  * active skin = ActiveSkin prune rule (tiles within radius*S of the TRUE frontier); a choice-tile
    "departs" when it is pruned. Equivalence of the derived skin to a real ActiveSkin is asserted.
  * three difference buckets kept SEPARATE:
        (a) decorated differences on SHARED coverage near the fronts   (CD.strip)
        (b) coverage / front-position differences (one covers, other doesn't)
        (c) differences in the broader retained skin no longer at the edge
  * complete stop reasons; right-censoring flagged; nothing called a lifetime if the run ends while live.
  * controls: C1 A-vs-A same stream (must be identical -> alignment test);
              C2 A-vs-A different streams (background from later choices alone);
              C3 A-vs-B across streams (signal beyond C2).

This is a pilot to establish the instrument. No predictor study, no large confirmatory run.

Run:  python3 paired_front.py --worlds 8 --steps 40
"""
from __future__ import annotations
from pathlib import Path
import sys, json, math, cmath, random, argparse, collections
import numpy as np

HERE = Path(__file__).resolve().parent
EFP = HERE.parent
sys.path.insert(0, str(EFP))
import figures as F
import active_skin_engine as E

L, D, S, SN, CD = F.L, F.D, F.S, F.SN, F.CD
cen = CD.cen
dk = lambda t: D.dkey(t)
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
SEED0 = 20262600            # fresh base, unused elsewhere
WEDGE0 = 300               # fresh wedge entries (A/B/C 192-215, branch-diag 216-239, E-prime 240-279)
MINPATCH = 150             # fork must appear after the patch has grown this far (not a seed artifact)
RADIUS = 2                 # active-skin prune radius, in S (matches ActiveSkin default)


def centres(nworlds):
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[WEDGE0:WEDGE0 + nworlds]


# ---------- common state S* and fork selection ----------

def common_state(k, centre):
    """Grow fresh world k with the patient scheduler until the first free-choice round after the patch
    passes MINPATCH. The patient scheduler exhausts all forced placements before any free choice, so that
    round's state is already forced-saturated = S*. The fork is the canonical-first 2-candidate frontier
    edge. Returns (S*, edge, mid, cs, meta) or None."""
    rng = random.Random(SEED0 + k)
    P = L.Patch(L.seed_patch(centre, 3 * S)); n0 = len(P.tris)
    for r in range(1, 4000):
        fr = P.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(dk(cs[0]), cs[0])
        if jam:
            return None
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        # no forced placements left this round -> state is forced-saturated. Look for a fork.
        if len(P.tris) - n0 < MINPATCH:
            # take the scheduler's own free choice and keep growing until big enough
            cs = SN.ordered(D.candidates(P, *fr[0][:3]))
            if len(cs) < 2:
                return None
            P.add(rng.choice(cs)); continue
        # canonical-first edge with exactly two legal candidates
        for e in fr:
            cs = SN.ordered(D.candidates(P, *e[:3]))
            if len(cs) == 2:
                Sstar = list(P.tris); mid = (e[0] + e[1]) / 2
                meta = dict(world=k, patch=len(Sstar), round=r, fork_mid=[mid.real, mid.imag])
                return Sstar, e, mid, cs, meta
        return None
    return None


# ---------- ordinary continuing growth (one arm), full history for the verifier ----------

def grow_arm(Sstar, c, stream, steps):
    """Ordinary patient-scheduler growth from S*+c. Full history kept (verifier). Records each tile's
    birth step and the later free-choice ('guess') steps. Returns per-step snapshots of the full patch."""
    Q = L.Patch(list(Sstar)); Q.add(c)
    rng = random.Random(stream)
    birth = {dk(c): 0}; snaps = [list(Q.tris)]; guesses = []; stop = "steps"
    for s in range(1, steps + 1):
        n0 = len(Q.tris)
        st, n, kind = SN.patient(Q, rng)
        if st == "JAM":
            stop = "jam"; snaps.append(list(Q.tris)); break
        for t in Q.tris[n0:]:
            birth[dk(t)] = s
        if kind == "guess":
            guesses.append(s)
        snaps.append(list(Q.tris))
    return dict(snaps=snaps, birth=birth, guesses=guesses, stop=stop, choice=dk(c))


# ---------- active skin (the observer's world): ActiveSkin prune rule ----------

def skin_of(tiles, radius=RADIUS):
    """The retained active skin: tiles within radius*S of the TRUE frontier boundary points.
    Mirrors ActiveSkin.prune exactly. Returns (skin_tiles, frontier_edges)."""
    P = L.Patch(list(tiles)); fr = P.frontier()
    pts = {L.key(z): z for e in fr for z in e[:2]}
    reach = radius * S + EPS
    skin = [t for t in tiles if any(abs(z - v) <= reach for z in t[1:] for v in pts.values())]
    return skin, fr


def frontier_dist(t, fr):
    pts = [z for e in fr for z in e[:2]]
    c = cen(t)
    return min(abs(c - z) for z in pts) / S if pts else 0.0


def verify_skin_equivalence(Sstar, c, stream, steps):
    """Astra's ask: verify the derived skin equals a genuine ActiveSkin on this new history. Runs a real
    ActiveSkin in lockstep on the same stream and checks the final skin's decorated-tile set matches."""
    P = E.ActiveSkin(list(Sstar) + [c], radius=RADIUS)
    rng = random.Random(stream)
    for s in range(1, steps + 1):
        st, n, kind = SN.patient(P, rng)
        if st == "JAM":
            break
        P.prune()
    skin_live = {dk(t) for t in P.tris}
    # derived skin from the full-history growth
    arm = grow_arm(Sstar, c, stream, steps)
    skin_derived = {dk(t) for t in skin_of(arm["snaps"][-1])[0]}
    return skin_live, skin_derived


# ---------- the paired-front comparison at matched steps ----------

def buckets(skinA, frA, skinB, frB, near=RADIUS):
    """Difference buckets between two skins in the shared coordinate frame, kept SEPARATE and with the
    shared-ground extent reported, so a shrinking overlap is never mistaken for a fading trace.
      shared     = (a) decorated differences on SHARED coverage (CD.strip)
      coverage   = (b) front-displacement: skin tiles one arm covers and the other does not
      co_covered = size of the shared ground (skin tiles each arm places where the other also covers)
      shared_frac= shared / co_covered  -- the trace DENSITY on common ground (the honest signal)
      shared_near= of the shared differences, how many sit within `near`*S of a current front."""
    a_A, a_B = CD.strip(skinA, skinB)            # (a) decorated diff on shared coverage
    kA = {dk(t) for t in skinA}; kB = {dk(t) for t in skinB}
    oA = [t for t in skinA if dk(t) not in kB]; oB = [t for t in skinB if dk(t) not in kA]
    cov = lambda p, others: any(L.inside(p, *u[1:]) for u in others)
    b_A = [t for t in oA if not cov(cen(t), skinB)]   # (b) A covers here, B doesn't
    b_B = [t for t in oB if not cov(cen(t), skinA)]
    # shared ground: skin tiles whose centroid the other arm also covers (same-dkey OR differing)
    co_A = sum(cov(cen(t), skinB) for t in skinA); co_B = sum(cov(cen(t), skinA) for t in skinB)
    co_covered = min(co_A, co_B)
    shared = a_A + a_B
    coverage = b_A + b_B
    near_cnt = sum(min(frontier_dist(t, frA), frontier_dist(t, frB)) <= near for t in shared)
    return dict(shared=len(shared), coverage=len(coverage), co_covered=co_covered,
                shared_frac=(len(shared) / co_covered if co_covered else 0.0),
                shared_near=near_cnt, shared_tiles=shared, coverage_tiles=coverage)


def choice_in_skin(arm, step):
    """Is this arm's original choice-tile still in the retained skin at this step? (departure test)"""
    skin, _ = skin_of(arm["snaps"][step])
    return arm["choice"] in {dk(t) for t in skin}


def compare(armA, armB, steps):
    """Front-difference over matched scheduler steps + choice-tile departure for each arm."""
    nmax = min(len(armA["snaps"]), len(armB["snaps"])) - 1
    rows = []
    departA = departB = None
    for s in range(0, min(steps, nmax) + 1):
        skinA, frA = skin_of(armA["snaps"][s]); skinB, frB = skin_of(armB["snaps"][s])
        b = buckets(skinA, frA, skinB, frB)
        inA = armA["choice"] in {dk(t) for t in skinA}
        inB = armB["choice"] in {dk(t) for t in skinB}
        if departA is None and not inA and s > 0:
            departA = s
        if departB is None and not inB and s > 0:
            departB = s
        rows.append(dict(step=s, placedA=len(armA["snaps"][s]), placedB=len(armB["snaps"][s]),
                         shared=b["shared"], coverage=b["coverage"], co_covered=b["co_covered"],
                         shared_frac=b["shared_frac"], shared_near=b["shared_near"],
                         choiceA_in=inA, choiceB_in=inB))
    return rows, departA, departB


def total_front_diff(rows, s):
    r = rows[s]
    return r["shared"] + r["coverage"]


# ---------- driver: controls C1/C2/C3 + the endurance test ----------

def _curve(pairs, key, s):
    vals = [r[s][key] for r in pairs if s < len(r)]
    return float(np.median(vals)) if vals else 0.0


def run_fork(k, centre, steps, nstreams):
    cs0 = common_state(k, centre)
    if cs0 is None:
        return None
    Sstar, edge, mid, cs, meta = cs0
    A, B = cs[0], cs[1]
    base = SEED0 * 1000 + k * 7919
    streams = [base + 31 * i for i in range(nstreams)]

    live, derived = verify_skin_equivalence(Sstar, A, streams[0], steps)
    meta["skin_equiv"] = (live == derived)

    armsA = [grow_arm(Sstar, A, s, steps) for s in streams]
    armsB = [grow_arm(Sstar, B, s, steps) for s in streams]
    meta["stopA"] = [a["stop"] for a in armsA]; meta["stopB"] = [a["stop"] for a in armsB]
    meta["guessesA"] = [a["guesses"] for a in armsA]; meta["guessesB"] = [a["guesses"] for a in armsB]

    # C1 alignment: A vs A same stream must be identically zero
    c1_rows, _, _ = compare(armsA[0], armsA[0], steps)
    meta["C1_max_shared"] = max(c1_rows[s]["shared"] + c1_rows[s]["coverage"] for s in range(len(c1_rows)))

    # background: SAME option, DIFFERENT streams -- from later free choices alone (both options)
    bg = []
    for arms in (armsA, armsB):
        for i in range(nstreams):
            for j in range(i + 1, nstreams):
                rows, _, _ = compare(arms[i], arms[j], steps); bg.append(rows)
    # signal: A vs B across streams, with coupled-pair departures
    sig = []; departs = []
    for i in range(nstreams):
        for j in range(nstreams):
            rows, dA, dB = compare(armsA[i], armsB[j], steps); sig.append(rows)
            if i == j:
                departs.append((dA, dB))
    dA = [d[0] for d in departs if d[0] is not None]; dB = [d[1] for d in departs if d[1] is not None]
    meta["departA"] = int(np.median(dA)) if dA else None
    meta["departB"] = int(np.median(dB)) if dB else None

    nmax = min([len(r) for r in bg + sig], default=0)
    axis = list(range(nmax))
    curves = dict(
        sig_frac=[_curve(sig, "shared_frac", s) for s in axis],
        sig_shared=[_curve(sig, "shared", s) for s in axis],
        sig_coverage=[_curve(sig, "coverage", s) for s in axis],
        sig_cocov=[_curve(sig, "co_covered", s) for s in axis],
        bg_frac=[_curve(bg, "shared_frac", s) for s in axis],
        bg_shared=[_curve(bg, "shared", s) for s in axis],
    )
    last = nmax - 1
    dep = max([d for d in (meta["departA"], meta["departB"]) if d is not None], default=None)
    # peak readable trace density (signal, on shared ground)
    meta["peak_sig_frac"] = round(max(curves["sig_frac"]), 3) if nmax else None
    meta["peak_bg_frac"] = round(max(curves["bg_frac"]), 3) if nmax else None
    meta["coverage_last"] = round(curves["sig_coverage"][last], 0) if nmax else None   # permanent displacement
    meta["cocov_last"] = round(curves["sig_cocov"][last], 0) if nmax else None         # remaining shared ground
    # endurance verdict (honest): AFTER the choice-tile departs, is signal trace-density above background,
    # WHILE enough shared ground remains to compare (co_covered floor)?
    FLOOR = 8
    if dep is not None and dep < last:
        post = [s for s in axis if s >= dep and curves["sig_cocov"][s] >= FLOOR]
        if post:
            sf = float(np.median([curves["sig_frac"][s] for s in post]))
            bf = float(np.median([curves["bg_frac"][s] for s in post]))
            meta["post_dep_sig_frac"] = round(sf, 3); meta["post_dep_bg_frac"] = round(bf, 3)
            meta["endures_on_shared_ground"] = sf > bf + 1e-9
            meta["post_dep_steps_with_ground"] = len(post)
        else:
            meta["post_dep_sig_frac"] = meta["post_dep_bg_frac"] = None
            meta["endures_on_shared_ground"] = None   # shared ground vanished before/at departure
            meta["post_dep_steps_with_ground"] = 0
        meta["censored"] = False
    else:
        meta["post_dep_sig_frac"] = meta["post_dep_bg_frac"] = None
        meta["endures_on_shared_ground"] = None
        meta["censored"] = True   # choice-tiles never left the skin within the horizon
    return dict(meta=meta, curves=curves, steps_axis=axis, Sstar=Sstar, mid=mid, armsA=armsA, armsB=armsB)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=8)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--nstreams", type=int, default=3)
    args = ap.parse_args()
    cs = centres(args.worlds + 20)
    forks = []
    for k, centre in enumerate(cs):
        if len(forks) >= args.worlds:
            break
        try:
            r = run_fork(k, centre, args.steps, args.nstreams)
        except Exception as e:
            print(f"world {k}: skipped ({type(e).__name__}: {e})", flush=True); continue
        if r is None:
            print(f"world {k}: no qualifying fork", flush=True); continue
        forks.append(r)
        m = r["meta"]
        print(f"world {k}: patch {m['patch']}, equiv={m['skin_equiv']}, dep(A/B)={m['departA']}/{m['departB']}, "
              f"peak trace-density sig={m['peak_sig_frac']} bg={m['peak_bg_frac']}, "
              f"coverage_last={m['coverage_last']} cocov_last={m['cocov_last']}, "
              f"endures_on_shared_ground={m['endures_on_shared_ground']}", flush=True)

    out = []
    out.append("Paired-front pilot (Phase 1): is there a readable trace at the current front, and does it")
    out.append("outlive the choice-tiles? Signal = A-vs-B; background = same option / different later choices.")
    out.append(f"forks: {len(forks)} (fresh worlds from wedge {WEDGE0}, skin radius {RADIUS}*S, {args.steps} steps, {args.nstreams} streams)")
    equivs = [r['meta']['skin_equiv'] for r in forks]
    out.append(f"skin equivalence (derived == real ActiveSkin): {sum(equivs)}/{len(equivs)}")
    c1 = [r['meta']['C1_max_shared'] for r in forks]
    out.append(f"C1 alignment (A-vs-A same stream, MUST be 0): max over forks = {max(c1) if c1 else 'NA'}")
    out.append("")
    out.append("KEY DISTINCTION (Astra #4): 'shared trace-density' = decorated differences per unit SHARED")
    out.append("ground (readable trace); 'coverage_last' = front DISPLACEMENT (the fronts are elsewhere) --")
    out.append("a permanent but different consequence. 'cocov_last' = how much shared ground still remains.")
    out.append("")
    out.append(f"{'world':>5} {'patch':>5} {'depA':>4} {'depB':>4} {'pkSigFr':>7} {'pkBgFr':>6} {'postSig':>7} {'postBg':>6} {'endure':>6} {'cover↑':>6} {'cocov':>6} {'cens':>5}")
    for r in forks:
        m = r['meta']
        out.append(f"{m['world']:>5} {m['patch']:>5} {str(m['departA']):>4} {str(m['departB']):>4} "
                   f"{str(m['peak_sig_frac']):>7} {str(m['peak_bg_frac']):>6} "
                   f"{str(m['post_dep_sig_frac']):>7} {str(m['post_dep_bg_frac']):>6} "
                   f"{str(m['endures_on_shared_ground']):>6} {str(m['coverage_last']):>6} {str(m['cocov_last']):>6} "
                   f"{str(m['censored']):>5}")
    ends = [r['meta']['endures_on_shared_ground'] for r in forks if r['meta']['endures_on_shared_ground'] is not None]
    covs = [r['meta']['coverage_last'] for r in forks if r['meta']['coverage_last'] is not None]
    out.append("")
    if ends:
        out.append(f"forks where the readable trace-density stays above background AFTER the choice-tiles leave "
                   f"the skin (on remaining shared ground): {sum(ends)}/{len(ends)}")
    else:
        out.append("no fork kept comparable shared ground past choice-tile departure -- see 'cens' column "
                   "(the fronts displace faster than the trace can be read on common ground).")
    if covs:
        out.append(f"front DISPLACEMENT at last step (coverage diff, tiles): median {np.median(covs):.0f}, "
                   f"range [{min(covs):.0f}, {max(covs):.0f}] -- a permanent consequence of the choice.")
    cens = sum(1 for r in forks if r['meta'].get('censored'))
    out.append(f"right-censored (choice-tiles still in skin at horizon end): {cens}/{len(forks)}")

    txt = "\n".join(out)
    print("\n" + txt)
    (RES / "report.txt").write_text(txt + "\n")
    (RES / "measurements.json").write_text(json.dumps([dict(
        meta=r['meta'], curves=r['curves'], steps_axis=r['steps_axis']
    ) for r in forks], indent=2, default=float))
    print("\nwrote results/report.txt, results/measurements.json")
    return forks


if __name__ == "__main__":
    main()

