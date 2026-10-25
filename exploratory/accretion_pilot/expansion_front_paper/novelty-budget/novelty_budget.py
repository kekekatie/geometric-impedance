#!/usr/bin/env python3
"""
novelty_budget.py -- Experiment E-prime (the novelty budget or the coiled spring).

Pre-registered in PREREGISTRATION.md. For GENUINE free choices on fresh worlds
(wedge entries 240-279, fresh seed base), measure the counterfactual causal SEAM
(commit A vs commit B, keep only the differing tiles -- ambient growth cancels):
  seam size  = |A-only| + |B-only|   (symmetric difference |A triangle B|)
  seam reach = max distance (in S) from the fork to a differing tile
and relate it, TWO-SIDED, to the fork's birth-decisiveness:
  PRIMARY   fingerprint stiffness (A catalogue) -- clean, age-independent
  SECONDARY wall-nearness min(pA,pB)/F_area     -- age-confounded, used with control
F_area is DROPPED as a predictor (X-axis probe: zero per-choice variance + -0.95 age).

The machinery (forced_arm, diagnose) is imported verbatim from the branch diagnostic
so the seam is the already-validated confound-free measure.

Run:  python3 novelty_budget.py            |   --worlds 40 --need 60 --nadd 700
"""
from __future__ import annotations
from pathlib import Path
import sys, json, math, cmath, random, collections, argparse
import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
EFP = HERE.parent
sys.path.insert(0, str(EFP))
sys.path.insert(0, str(EFP / "corner-response-catalogue"))
sys.path.insert(0, str(EFP / "branch-diagnostic"))
import figures as F
import corner_response as CR
import branch_diagnostic as BD                 # forced_arm, diagnose (confound-free seam)

L, D, S, SN, Sl, CD = F.L, F.D, F.S, F.SN, F.Sl, F.CD
dk = BD.dk; ek = CR.ek
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
SEED0 = BD.SEED0
WEDGE0 = 241                 # fresh: A/B/C used 192-215, branch diagnostic 216-239, E-prime validation 240
SEEDSHIFT = 5000             # fresh seed base so the growth is unpeeked
PER_WORLD = 3                # cap forks per world so a 60-fork target spans ~20 worlds (independence)
SUBSEED = 73                 # deterministic age-spread subsampling within each world
STIFF = json.loads((EFP / "corner-response-catalogue" / "results" / "summary.json").read_text())["stiffness"]


def centres(nworlds):
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[WEDGE0:WEDGE0 + nworlds]


def collect_candidates(k, centre, nadd):
    """Grow one fresh world to its FULL extent and collect EVERY genuine free choice (a tie the
    bounded wave leaves open), across all growth ages -- the caller subsamples a few per world, so
    collecting the whole set (not the first few) is what keeps patch-age variance in the sample."""
    rng = random.Random(SEED0 + SEEDSHIFT + k)
    P = L.Patch(L.seed_patch(centre, 3 * S)); n0 = len(P.tris); seen = set(); out = []
    while len(P.tris) - n0 < nadd:
        fr = P.frontier()
        for e in fr:
            sk = ek(e)
            if sk in seen:
                continue
            cs = D.candidates(P, *e[:3])
            if len(cs) == 2:
                seen.add(sk); before = list(P.tris); mid = (e[0] + e[1]) / 2
                tris0, _ = BD.forced_arm(before, mid, cap=12, R=5)   # cheap screen
                if len(D.candidates(L.Patch(tris0), *e[:3])) == 2:   # bounded wave left it open
                    out.append((before, e, mid))
        forced = {}
        for e in fr:
            c = D.candidates(P, *e[:3])
            if len(c) == 1:
                forced.setdefault(dk(c[0]), c[0])
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        P.add(rng.choice(SN.ordered(D.candidates(P, *fr[0][:3]))))
    return out


def seam_reach(d):
    """Distances (in S) from the fork to each differing tile's centroid.
    Returns (max reach [pre-registered, scored], median reach [reported diagnostic]).
    Max can pin at the R*S measurement radius; the median does not, so it exposes
    whether a seam hugs the fork or spreads to the rim."""
    tA = {dk(t): t for t in d["trisA"]}; tB = {dk(t): t for t in d["trisB"]}
    diff = [tA[k] for k in d["a_spec"]] + [tB[k] for k in d["b_spec"]]
    if not diff:
        return 0.0, 0.0
    mid = d["mid"]
    rs = [abs(sum(t[1:]) / 3 - mid) / S for t in diff]
    return float(max(rs)), float(np.median(rs))


def predictors(before, edge, mid):
    cs = D.candidates(L.Patch(before), *edge[:3])
    if len(cs) != 2:
        return None
    rank = Sl.rank_of(before)
    Fraw = Sl.area(Sl.region(Sl.constraints(before, rank)))
    wall = None
    if Fraw > 0:
        pcs = [Sl.area(Sl.region(CD.after_first(before, c, rank))) for c in cs]
        wall = float(min(pcs) / Fraw)
    fp = CR.fingerprint(before, mid, CR.RPRIMARY)
    stiff = STIFF.get(fp)
    return dict(patch=len(before), wall=wall, stiff=(None if stiff is None else float(stiff)))


def partial_spearman(x, y, z):
    """First-order partial Spearman of x,y controlling for z."""
    rxy = spearmanr(x, y)[0]; rxz = spearmanr(x, z)[0]; ryz = spearmanr(y, z)[0]
    den = math.sqrt(max(1 - rxz ** 2, 1e-12) * max(1 - ryz ** 2, 1e-12))
    return (rxy - rxz * ryz) / den


def cluster_ci(worlds, xs, ys, B=2000, seed=0):
    """World-level cluster bootstrap 90% CI on Spearman(xs, ys)."""
    rng = random.Random(seed)
    by = collections.defaultdict(list)
    for w, x, y in zip(worlds, xs, ys):
        by[w].append((x, y))
    wk = list(by)
    rr = []
    for _ in range(B):
        pts = []
        for _ in range(len(wk)):
            pts += by[rng.choice(wk)]
        if len({p[0] for p in pts}) < 3 or len({p[1] for p in pts}) < 3:
            continue
        rr.append(spearmanr([p[0] for p in pts], [p[1] for p in pts])[0])
    rr.sort()
    return (np.percentile(rr, 5), np.percentile(rr, 95)) if rr else (float("nan"), float("nan"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=40)
    ap.add_argument("--need", type=int, default=60)
    ap.add_argument("--nadd", type=int, default=700)
    args = ap.parse_args()
    cs = centres(args.worlds)
    sub = random.Random(SUBSEED)
    rows = []
    for k, centre in enumerate(cs):
        if len(rows) >= args.need:
            break
        cands = collect_candidates(k, centre, args.nadd)
        picks = sub.sample(cands, min(PER_WORLD, len(cands))) if cands else []   # age-spread, independent
        got = 0
        for before, edge, mid in picks:
            try:
                d = BD.diagnose(before, edge, mid)
                if not d or (d["n_a"] + d["n_b"]) == 0:
                    continue
                pr = predictors(before, edge, mid)
                if pr is None:
                    continue
                rmax, rmed = seam_reach(d)
                rows.append(dict(world=k, size=d["n_a"] + d["n_b"], n_a=d["n_a"], n_b=d["n_b"],
                                 reach=rmax, reach_med=rmed, capA=d["stopA"] == "cap", capB=d["stopB"] == "cap",
                                 **pr))
                got += 1
            except Exception as e:
                print(f"  world {k}: skipped a case ({type(e).__name__})", flush=True)
                continue
        print(f"world {k}: {len(cands)} candidates, kept {got}; cumulative seams {len(rows)}", flush=True)

    scored = [r for r in rows if r["stiff"] is not None]
    out = []
    wc = collections.Counter(r["world"] for r in rows)
    out.append(f"E-prime -- the novelty budget or the coiled spring")
    out.append(f"genuine free choices with a non-degenerate seam: {len(rows)} "
               f"(fresh worlds from wedge {WEDGE0}, <= {PER_WORLD}/world, seam radius {BD.BIG_R}*S cap {BD.BIG_CAP})")
    out.append(f"independence: {len(wc)} distinct worlds, forks/world {dict(sorted(collections.Counter(wc.values()).items()))} "
               f"(count:n_worlds)")
    out.append(f"stiffness coverage (scored set): {len(scored)}/{len(rows)}")
    size = np.array([r["size"] for r in rows]); reach = np.array([r["reach"] for r in rows])
    out.append(f"seam size |A triangle B|: median {np.median(size):.0f} mean {size.mean():.1f} "
               f"p10 {np.percentile(size,10):.0f} p90 {np.percentile(size,90):.0f} max {size.max()}")
    rmed = np.array([r["reach_med"] for r in rows])
    out.append(f"seam reach MAX (S, scored): median {np.median(reach):.1f} p10 {np.percentile(reach,10):.1f} "
               f"p90 {np.percentile(reach,90):.1f} max {reach.max():.1f}  (watch for pinning at R={BD.BIG_R})")
    out.append(f"seam reach MEDIAN-of-differing (S, diagnostic): median {np.median(rmed):.1f} "
               f"p10 {np.percentile(rmed,10):.1f} p90 {np.percentile(rmed,90):.1f}")
    out.append(f"cap-hit rate (truncation risk): A {sum(r['capA'] for r in rows)}/{len(rows)} "
               f"B {sum(r['capB'] for r in rows)}/{len(rows)}")
    na = np.array([r["n_a"] for r in rows]); nb = np.array([r["n_b"] for r in rows])
    out.append(f"per-fork asymmetry |A-only| vs |B-only|: medians {np.median(na):.0f} vs {np.median(nb):.0f}; "
               f"mean |A-only - B-only| {np.abs(na-nb).mean():.1f}")

    if len(scored) >= 3:
        w = [r["world"] for r in scored]
        st = [r["stiff"] for r in scored]; pa = [r["patch"] for r in scored]
        sz = [r["size"] for r in scored]; rc = [r["reach"] for r in scored]
        out.append("")
        out.append("=== age-confound audit (want stiffness ~ 0; the pre-reg's claim) ===")
        out.append(f"  Spearman(patch_age, stiffness) = {spearmanr(pa, st)[0]:+.3f}   (predictor's age-freedom)")
        out.append(f"  Spearman(patch_age, seam size) = {spearmanr(pa, sz)[0]:+.3f}   (outcome's raw age confound)")
        out.append(f"  Spearman(patch_age, seam reach)= {spearmanr(pa, rc)[0]:+.3f}")
        out.append("")
        out.append("=== E1  stiffness -> seam size (two-sided; - = Novelty Budget, + = Coiled Spring) ===")
        r1 = spearmanr(st, sz)[0]; p1 = partial_spearman(st, sz, pa); ci1 = cluster_ci(w, st, sz)
        out.append(f"  Spearman(stiffness, seam size) = {r1:+.3f}   90% cluster CI [{ci1[0]:+.3f}, {ci1[1]:+.3f}]")
        out.append(f"  partial (control patch age)    = {p1:+.3f}")
        verdict = ("NOVELTY BUDGET (free forks diverge more)" if r1 < 0 else "COILED SPRING (pinched forks diverge more)")
        passed = abs(r1) >= 0.2 and abs(p1) >= 0.15 and (r1 < 0) == (p1 < 0)
        out.append(f"  E1 {'PASS' if passed else 'null'} (|rho|>=0.2 & age-robust |partial|>=0.15 same sign): {verdict if passed else 'no robust relationship'}")
        out.append("")
        out.append("=== E2  stiffness -> seam reach (same sign as E1) ===")
        r2 = spearmanr(st, rc)[0]; p2 = partial_spearman(st, rc, pa); ci2 = cluster_ci(w, st, rc)
        out.append(f"  Spearman(stiffness, seam reach) = {r2:+.3f}   90% cluster CI [{ci2[0]:+.3f}, {ci2[1]:+.3f}]")
        out.append(f"  partial (control patch age)     = {p2:+.3f}")
        pass2 = abs(r2) >= 0.2 and abs(p2) >= 0.15 and (r2 < 0) == (p2 < 0) and (r2 < 0) == (r1 < 0)
        out.append(f"  E2 {'PASS' if pass2 else 'null'}"
                   + ("  (NB: if max-reach is pinned at R the scored E2 is uninformative -- read the diagnostic below)" if reach.std() < 0.5 else ""))
        rcm = [r["reach_med"] for r in scored]
        out.append(f"  diagnostic (unpinned): Spearman(stiffness, median-reach-of-differing) = {spearmanr(st, rcm)[0]:+.3f} "
                   f"partial(age) {partial_spearman(st, rcm, pa):+.3f}")
        out.append("")
        out.append("=== secondary (reported, not scored): wall-nearness -> seam size ===")
        sw = [r for r in scored if r["wall"] is not None]
        if len(sw) >= 3:
            wl = [r["wall"] for r in sw]; szw = [r["size"] for r in sw]; paw = [r["patch"] for r in sw]
            out.append(f"  Spearman(wall-nearness, seam size) = {spearmanr(wl, szw)[0]:+.3f}")
            out.append(f"  partial (control patch age)        = {partial_spearman(wl, szw, paw):+.3f}")
            out.append(f"  (wall is -0.68 age-confounded; compare the two partials)")
    else:
        out.append("too few scored cases to correlate")

    txt = "\n".join(out)
    print("\n" + txt)
    (RES / "report.txt").write_text(txt + "\n")
    (RES / "measurements.json").write_text(json.dumps(dict(
        n=len(rows), n_scored=len(scored), wedge0=WEDGE0, rows=rows), indent=2, default=float))
    print("\nwrote results/report.txt, results/measurements.json")


if __name__ == "__main__":
    main()
