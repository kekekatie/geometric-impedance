#!/usr/bin/env python3
"""
soft_claim_22_26.py -- check the draft's one flagged "residual soft claim" (§3.5):
"Pair (22,26) is marked more strongly than several durable pairs and loses everything."

Uses the repository's own depth-3 machinery (../../endogenous_pair_robustness/depth3_criterion.py,
unchanged). For every depth-3 matched pair: D_slice at h = 1, 2, 3 (the expression before erasure)
and the coast limit L. Then rank washout pair (22,26)'s expression against every DURABLE pair's at
the same horizon. The claim holds if (22,26)'s D_slice exceeds that of "several" durable pairs.
Exact rationals. Exit 0 iff the claim holds at h=2 (the draft's quoted horizon); counts reported
at every horizon either way.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "endogenous_pair_robustness"))
os.chdir(os.path.join(HERE, "..", "..", "endogenous_pair_robustness"))
import depth3_criterion as D3

d3 = D3.depth3_classes()
pairs = [(a, b) for a in range(len(d3)) for b in range(a + 1, len(d3))
         if D3.PW.iso(D3.PW.erase(d3[a]), D3.PW.erase(d3[b])) and not D3.PW.iso(d3[a], d3[b])]
rec = {}
for (a, b) in pairs:
    ds = [D3.Dslice(d3[a], d3[b], h) for h in (1, 2, 3)]
    L, shapes, _ = D3.PR.coast_limit(d3[a], d3[b])
    exp_ = any(x > 0 for x in ds)
    rec[(a, b)] = dict(ds=ds, L=L, fate="durable" if L > 0 else ("washout" if exp_ else "inert"))
w = rec[(22, 26)]
dur = {p: r for p, r in rec.items() if r["fate"] == "durable"}
lines = [f"pair (22,26): fate {w['fate']}, D_slice(1,2,3) = {', '.join(map(str, w['ds']))}, L = {w['L']}",
         f"durable pairs: {len(dur)}"]
for i, h in enumerate((1, 2, 3)):
    weaker = sum(1 for r in dur.values() if r["ds"][i] < w["ds"][i])
    lines.append(f"  h={h}: (22,26) D_slice = {w['ds'][i]}; durable pairs with a SMALLER D_slice: "
                 f"{weaker}/{len(dur)}; larger: {sum(1 for r in dur.values() if r['ds'][i] > w['ds'][i])}")
peak = max(w["ds"])
lines.append(f"  peak over h<=3: (22,26) {peak}; durable pairs whose own peak is smaller: "
             f"{sum(1 for r in dur.values() if max(r['ds']) < peak)}/{len(dur)}")
ok = sum(1 for r in dur.values() if r["ds"][1] < w["ds"][1]) >= 3
lines.append("VERDICT: the soft claim HOLDS" if ok else "VERDICT: the soft claim does NOT hold as worded")
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
open(os.path.join(HERE, "results", "soft_claim_22_26.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if ok else 1)
