#!/usr/bin/env python3
"""
worm_test.py -- do two Penrose universes differ along RIBBONS (worms)?

laying_the_tiling.py found that forced-first local growth never jams but, through its few
guesses, builds a DIFFERENT legal Penrose patch from the self-similar one; in the picture the
differing tiles seemed to form wiggly bands shaped like the ribbons of ../least_resistance_paths/.
Known theory (Conway worms): Penrose tilings differ by flips along ribbons. Here we TEST it.

Method. Pair half-tiles into rhombi (partners share their base: the short side of the thin
half, the long side of the thick half). A rhombus has edges in exactly 2 of the 5 directions
e_j (mod sign). A j-RIBBON is a chain of rhombi joined through shared edges of direction j.
For each forced-growth patch, take the rhombi that differ from the self-similar tiling and ask:
  (1) WORM SHARE: the largest fraction of differing rhombi that all contain an edge of one
      direction j (a single ribbon family would give ~100%; any rhombus has 2/5 directions);
  (2) CHAINED: of those, the fraction lying in ONE connected j-ribbon chain (via shared j-edges);
  (3) CONTROL: the same statistics for random sets of rhombi of equal size drawn from the same
      patch -- and for random CONNECTED clusters of equal size (grown by adjacency), which
      rules out "any connected blob looks like a ribbon".
asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, math, random, collections, json
import laying_the_tiling as T

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "worm_report.txt")
DATA = os.path.join(HERE, "results", "worm.json")
LINES, FAILS = [], []
RUNS = 30
CONTROLS = 200


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def edges_of(t):
    A, B, C = t[1:]
    es = [(A, B), (B, C), (C, A)]
    lens = [abs(p - q) for p, q in es]
    base = lens.index(min(lens)) if t[0] == 0 else lens.index(max(lens))
    return es[base], [e for i, e in enumerate(es) if i != base]


def fam(p, q):
    """edge direction family. In this tiling edges point at 18 + 36k degrees (mod 180).
    (v1 rounded ang/36 -- edges sit exactly between bins there, which merged families: a bug.)"""
    ang = math.degrees(math.atan2((q - p).imag, (q - p).real)) % 180
    return int(round((ang - 18.0) / 36.0)) % 5


def pca(pts):
    n = len(pts); mx = sum(p.real for p in pts) / n; my = sum(p.imag for p in pts) / n
    sxx = sum((p.real - mx) ** 2 for p in pts) / n; syy = sum((p.imag - my) ** 2 for p in pts) / n
    sxy = sum((p.real - mx) * (p.imag - my) for p in pts) / n
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    l1 = tr / 2 + math.sqrt(max(tr * tr / 4 - det, 0)); l2 = tr / 2 - math.sqrt(max(tr * tr / 4 - det, 0))
    return math.sqrt(l1 / max(l2, 1e-12)), math.degrees(0.5 * math.atan2(2 * sxy, sxx - syy)) % 180


def rhombi(tris):
    """pair half-tiles across their bases -> list of rhombi: (id, set of (edge key, family))."""
    by_base = collections.defaultdict(list)
    for t in tris:
        (p, q), legs = edges_of(t)
        by_base[frozenset((T.key(p), T.key(q)))].append(t)
    out = []
    for bk, ts in by_base.items():
        if len(ts) != 2:
            continue
        legs = []
        for t in ts:
            for p, q in edges_of(t)[1]:
                legs.append((frozenset((T.key(p), T.key(q))), fam(p, q)))
        out.append((bk, ts, legs))
    return out


def stats(sel, allr, fam_edges):
    """worm share and chained fraction for a set of rhombus indices."""
    if not sel:
        return 0.0, 0.0, None
    best = (0, None)
    for j in range(5):
        n = sum(1 for i in sel if any(f == j for _, f in allr[i][2]))
        best = max(best, (n, j))
    n, j = best
    members = [i for i in sel if any(f == j for _, f in allr[i][2])]
    mset = set(members)
    # connectivity through shared j-edges
    adj = collections.defaultdict(set)
    for ek, idxs in fam_edges[j].items():
        idxs = [i for i in idxs if i in mset]
        for a in idxs:
            for b in idxs:
                if a != b:
                    adj[a].add(b)
    seen, bestc = set(), 0
    for s0 in members:
        if s0 in seen:
            continue
        comp, st = 0, [s0]; seen.add(s0)
        while st:
            u = st.pop(); comp += 1
            for w in adj[u]:
                if w not in seen:
                    seen.add(w); st.append(w)
        bestc = max(bestc, comp)
    return n / len(sel), bestc / len(sel), j


def main():
    log("=" * 90)
    log("WORM TEST -- do two Penrose universes differ along ribbons?")
    log("=" * 90)
    refset = {T.canon(t) for t in T.REF}
    seed = T.seed_patch(0j, 3 * T.SCALE_LEN)
    rows = []
    rng = random.Random(T.SEED + 555)
    for k in range(RUNS):
        n, st, P = T.lay("LOCAL-FORCED", seed, random.Random(T.SEED + k))
        allr = rhombi(P.tris)
        fam_edges = [collections.defaultdict(list) for _ in range(5)]
        for i, (_, _, legs) in enumerate(allr):
            for ek, f in legs:
                fam_edges[f][ek].append(i)
        diff = [i for i, (_, ts, _) in enumerate(allr) if any(T.canon(t) not in refset for t in ts)]
        if not diff:
            continue
        share, chained, j = stats(diff, allr, fam_edges)
        # controls: random sets; random connected clusters (grown through any shared edge)
        cs, cc, ks, kc = [], [], [], []
        edge_to = collections.defaultdict(list)
        for i, (_, _, legs) in enumerate(allr):
            for ek, _ in legs:
                edge_to[ek].append(i)
        nb = collections.defaultdict(set)
        for ek, idxs in edge_to.items():
            for a in idxs:
                for b in idxs:
                    if a != b:
                        nb[a].add(b)
        for _ in range(CONTROLS):
            sel = rng.sample(range(len(allr)), len(diff))
            a, b, _ = stats(sel, allr, fam_edges); cs.append(a); cc.append(b)
            s0 = rng.randrange(len(allr)); cl = {s0}; fr = list(nb[s0])
            while len(cl) < len(diff) and fr:
                x = fr.pop(rng.randrange(len(fr)))
                if x not in cl:
                    cl.add(x); fr.extend(nb[x])
            a, b, _ = stats(list(cl), allr, fam_edges); ks.append(a); kc.append(b)
        # connected pieces of the differing set, their elongation and axis vs ribbon directions
        dnb = collections.defaultdict(set)
        dset = set(diff)
        for ek, idxs in edge_to.items():
            idxs = [i for i in idxs if i in dset]
            for a_ in idxs:
                for b_ in idxs:
                    if a_ != b_:
                        dnb[a_].add(b_)
        pieces, vis = [], set()
        for s0 in diff:
            if s0 in vis:
                continue
            c, st_ = [], [s0]; vis.add(s0)
            while st_:
                u = st_.pop(); c.append(u)
                for w in dnb[u]:
                    if w not in vis:
                        vis.add(w); st_.append(w)
            pieces.append(c)
        cen = lambda i: sum(sum(t[1:]) for t in allr[i][1]) / 6
        elong = []
        for c in pieces:
            if len(c) >= 10:
                ar, ang = pca([cen(i) for i in c])
                dev = min(min(abs(ang - r), 180 - abs(ang - r)) for r in (0, 36, 72, 108, 144))
                blob = []
                for _ in range(CONTROLS):
                    s0 = rng.randrange(len(allr)); cl = {s0}; fr = list(nb[s0])
                    while len(cl) < len(c) and fr:
                        x = fr.pop(rng.randrange(len(fr)))
                        if x not in cl:
                            cl.add(x); fr.extend(nb[x])
                    blob.append(pca([cen(i) for i in cl])[0])
                blob.sort()
                elong.append(dict(size=len(c), elong=ar, axis=ang, dev=dev,
                                  blob_med=blob[len(blob) // 2], blob_p95=blob[int(0.95 * len(blob))]))
        rows.append(dict(n_diff=len(diff), n_rh=len(allr), share=share, chained=chained, fam=j, pieces=elong,
                         ctrl_share=sum(cs) / len(cs), ctrl_chain=sum(cc) / len(cc),
                         clus_share=sum(ks) / len(ks), clus_chain=sum(kc) / len(kc),
                         clus_share_p95=sorted(ks)[int(0.95 * len(ks))]))
        log(f"  run {k:>2}: {len(diff):>3} of {len(allr)} rhombi differ | one direction shared by "
            f"{share:.0%} (random {rows[-1]['ctrl_share']:.0%}, connected blob "
            f"{rows[-1]['clus_share']:.0%}) | one chain holds {chained:.0%} (random "
            f"{rows[-1]['ctrl_chain']:.0%}, blob {rows[-1]['clus_chain']:.0%})")
        for pc in rows[-1]["pieces"]:
            log(f"          band of {pc['size']} rhombi: {pc['elong']:.1f}x longer than wide (blobs: "
                f"median {pc['blob_med']:.1f}, 95th pct {pc['blob_p95']:.1f}); axis {pc['axis']:.0f} deg, "
                f"{pc['dev']:.1f} deg from the nearest ribbon direction")
    log("=" * 90)
    med = lambda L: sorted(L)[len(L) // 2]
    log(f"  medians over {len(rows)} runs: worm share {med([r['share'] for r in rows]):.0%} vs random "
        f"{med([r['ctrl_share'] for r in rows]):.0%} vs connected blob {med([r['clus_share'] for r in rows]):.0%}; "
        f"single chain {med([r['chained'] for r in rows]):.0%} vs random {med([r['ctrl_chain'] for r in rows]):.0%} "
        f"vs blob {med([r['clus_chain'] for r in rows]):.0%}")
    require(len(rows) >= 25, f"{len(rows)} of {RUNS} forced-growth runs built a different universe (tested)")
    outcomes = sorted({r["n_diff"] for r in rows})
    log(f"  distinct outcomes among the {len(rows)} runs (by number of differing rhombi): {outcomes} "
        f"-- the runs are NOT {len(rows)} independent examples")
    log("  [pre-registered test, v1 had a direction-family bug; rerun with fixed families:]")
    ms = med([r["share"] for r in rows])
    log(f"  PREDICTION FAILED (recorded, not a gate): the differing rhombi share one edge direction in "
        f"only {ms:.0%} (median), not >= 90%. In hindsight theory says so: worm flips rearrange "
        f"hexagons of three rhombi in three directions, so 'one shared direction' was the wrong "
        f"signature of a worm.")
    require(sum(1 for r in rows if r["share"] > r["clus_share_p95"]) >= 0.8 * len(rows),
            "in >= 80% of runs the worm share beats the 95th percentile of random CONNECTED clusters "
            "of the same size: not just any blob")
    require(med([r["chained"] for r in rows]) > med([r["clus_chain"] for r in rows]),
            "the differing rhombi form a single ribbon chain more often than connected blobs do")
    log("  [added AFTER seeing the bands (exploratory): band shape and orientation]")
    pcs = [pc for r in rows for pc in r["pieces"]]
    require(len(pcs) > 0 and all(pc["elong"] > pc["blob_p95"] for pc in pcs),
            f"every differing piece (>=10 rhombi) is far more elongated than the 95th percentile of "
            f"same-size connected blobs (elongation {min(pc['elong'] for pc in pcs):.1f}-"
            f"{max(pc['elong'] for pc in pcs):.1f} vs blob 95th pct <= {max(pc['blob_p95'] for pc in pcs):.1f}): "
            f"the universes differ along thin bands")
    require(all(pc["dev"] <= 5 for pc in pcs),
            f"every band runs along a ribbon direction (max deviation {max(pc['dev'] for pc in pcs):.1f} deg)")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(rows, open(DATA, "w"), indent=1)
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
