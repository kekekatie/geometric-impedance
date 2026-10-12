#!/usr/bin/env python3
"""EXPLORATORY follow-up (after the registered run; no predictions): what does the zip look like?
For every distinct situation of front_activation.py, regrow both siblings for 40 slices (same streams) and record, per
slice, WHERE along the front the active edges lie: the angle of each active edge's midpoint around the world's seed
centre, relative to the choice point, converted to edges of arc at the base patch's mean radius. From that:
  * zip extent: the arc spanned so far by all active edges (furthest left to furthest right, in edges);
  * tip speed: extent growth per slice over the matched slices;
  * outward distance of active edges from the base patch (are the decided future's new tiles mostly sideways?).
Writes results/zip_EXPLORATORY.txt and figures/zip.png (kymograph of one pair)."""
import os, math, cmath, random, json, collections
from multiprocessing import Pool
import numpy as np
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import front_activation as FA
SN, Sl, L, D, S = FA.SN, FA.Sl, FA.L, FA.D, FA.S
SLICES = 40
BG, INK, MUTED, GOLD, BLUE = "#07080d", "#ece8dc", "#8f8b80", "#f2b84b", "#5b8fe0"


def trace(job):
    key, base, cs, c0, zc = job
    stream = FA.SEED0 * 1000 + int(key, 16) % (2 ** 31)
    rad = float(np.mean([abs(FA.cen(t) - c0) for t in base]))
    phi0 = cmath.phase(zc - c0)
    tree = cKDTree([[FA.cen(t).real / S, FA.cen(t).imag / S] for t in base])
    out = []
    for c in cs:
        Q = L.Patch(list(base)); Q.add(c); rng = random.Random(stream); rows = []
        for s in range(1, SLICES + 1):
            fr = [(ek, ts) for ek, ts in Q.edges.items() if len(ts) == 1]
            st, n, kind = SN.patient(Q, rng)
            if st == "JAM":
                break
            act = []
            for ek, _ in fr:
                if len(Q.edges[ek]) == 2:
                    a, b = list(ek); m = (complex(*a) + complex(*b)) / 2
                    arc = (cmath.phase((m - c0) / (zc - c0))) * rad / S
                    act.append((arc, float(tree.query([m.real / S, m.imag / S])[0])))
            rows.append(dict(kind=kind, act=act))
        out.append(rows)
    return dict(key=key, sibs=out)


def main():
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(FA.world, range(FA.N_WORLDS))
    jobs = {}; meta = {}
    for w in W:
        c0 = FA.centres()[w["world"]]
        for c in w["choices"]:
            if c["key"] not in jobs:
                zc = sum(c["cs"][0][1:]) / 3
                jobs[c["key"]] = (c["key"], c["base"], c["cs"], c0, zc); meta[c["key"]] = c["pieces"]
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(trace, list(jobs.values()), chunksize=1)
    lines = [f"EXPLORATORY zip: {len(R)} distinct situations, {SLICES} slices each"]
    tipsp = {"sm": [], "lg": []}; side = {"sm": [], "lg": []}; ext20 = {"sm": [], "lg": []}
    for r in R:
        pcs = meta[r["key"]]; i = 0 if pcs[0] < pcs[1] else 1
        for nm, rows in (("sm", r["sibs"][i]), ("lg", r["sibs"][1 - i])):
            lo = hi = 0.0; ext = []
            for x in rows:
                for arc, d in x["act"]:
                    lo, hi = min(lo, arc), max(hi, arc)
                ext.append(hi - lo)
            burst = next((k for k, x in enumerate(rows) if x["kind"] == "guess"), len(rows))
            if burst >= 3:
                tipsp[nm].append(ext[burst - 1] / burst)
            if len(ext) >= 20:
                ext20[nm].append(ext[19])
            ds = [d for x in rows[:burst] for _, d in x["act"]]
            if ds:
                side[nm].append(float(np.mean([d <= 1.0 for d in ds])))
    for nm, lab in (("sm", "smaller piece"), ("lg", "larger piece")):
        lines.append(f"  {lab}: zip extent growth during its burst, median {np.median(tipsp[nm]):.2f} edges of arc per slice "
                     f"(IQR {np.quantile(tipsp[nm], .25):.2f}-{np.quantile(tipsp[nm], .75):.2f}, n {len(tipsp[nm])}); extent after 20 slices median "
                     f"{np.median(ext20[nm]):.1f} edges; share of active edges within 1 edge of the old boundary {np.median(side[nm]):.2f}")
    print("\n".join(lines))
    open(os.path.join(FA.RES, "zip_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
    # kymograph of the situation with the largest burst contrast among the first few
    r = max(R, key=lambda r: abs(len(r["sibs"][0]) and sum(len(x["act"]) for x in r["sibs"][0][:20]) - sum(len(x["act"]) for x in r["sibs"][1][:20])))
    pcs = meta[r["key"]]; i = 0 if pcs[0] < pcs[1] else 1
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor=BG, sharey=True)
    for ax, rows, col, lab in ((axes[0], r["sibs"][i], GOLD, f"keeps {min(pcs):.3f} of F"), (axes[1], r["sibs"][1 - i], BLUE, f"keeps {max(pcs):.3f} of F")):
        ax.set_facecolor(BG); ax.tick_params(colors=MUTED)
        for sp in ax.spines.values():
            sp.set_color(MUTED)
        for s, x in enumerate(rows, 1):
            if x["act"]:
                ax.scatter([a for a, _ in x["act"]], [s] * len(x["act"]), s=7, color=col, alpha=0.8, edgecolors="none")
            if x["kind"] == "guess":
                ax.axhline(s, color=MUTED, lw=0.6, ls=":")
        ax.set_xlabel("position along the front, edges of arc from the choice point", color=INK)
        ax.set_title(f"option that {lab}", color=INK, fontsize=12)
    axes[0].set_ylabel("slice after the choice (dotted = a guess)", color=INK); axes[0].invert_yaxis()
    fig.suptitle("the zip: where along the front tiles are being laid, slice by slice", color=INK, fontsize=14, family="serif", style="italic")
    os.makedirs(os.path.join(FA.HERE, "figures"), exist_ok=True)
    plt.savefig(os.path.join(FA.HERE, "figures", "zip.png"), dpi=105, facecolor=BG, bbox_inches="tight")


if __name__ == "__main__":
    main()
