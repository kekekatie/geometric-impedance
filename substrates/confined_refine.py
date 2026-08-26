#!/usr/bin/env python3
"""
EXPLORATORY refinement of the within-motif confined-address picture (RESULTS_CONFINED.md),
per GPT's cautions. Three checks, cheap:

1. FINER local control. Does the address effect survive adding the FINE (star/sign) vertex
   type as a nuisance control inside each coarse class? If yes, it is not just residual finer
   local structure.
2. Ill-conditioned classes are marked INCONCLUSIVE (held-out physical R^2 < 0.2), not "noise".
3. Selection-rule test. Does the confined-weight peak sit at the same NORMALIZED perp-space
   depth across motif classes and families (a genuine internal-space band), and is it stable
   across offsets?
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from transport_run import build_features, held_out_r2, OFFSETS, NAME
from confined_address import confined_weight, coarse_motif, phys_block, addr_block
from transport_run import hull_depth

MINR2 = 0.20                                   # below this held-out phys R2 -> inconclusive


def peak_norm_depth(depth, conf, dmax, nb=8):
    """Normalized depth (0..1) of the max-confined-weight bin; None if too few points."""
    if len(depth) < 40:
        return None
    order = np.argsort(depth)
    bins = np.array_split(order, nb)
    centers = [depth[b].mean() for b in bins]
    means = [conf[b].mean() for b in bins]
    return centers[int(np.argmax(means))] / dmax


def run(N, extent=12, offs=None):
    offs = offs or OFFSETS[:4]
    feats = [build_features(N, o, extent=extent, return_dynamics=True) for o in offs]
    coarse_cb, fine_cb = {}, {}
    for f in feats:
        f["cmotif"] = coarse_motif(f)
        for k in f["cmotif"]:
            coarse_cb.setdefault(k, len(coarse_cb))
        for k in f["motif_keys"]:
            fine_cb.setdefault(k, len(fine_cb))
    for f in feats:
        f["cc"] = np.array([coarse_cb[k] for k in f["cmotif"]])
        fine = np.array([fine_cb[k] for k in f["motif_keys"]])
        f["fine_oh"] = np.eye(len(fine_cb))[fine]
        f["conf"] = confined_weight(f)
        f["phys"] = phys_block(f)
        f["physfine"] = np.column_stack([f["phys"], f["fine_oh"]])
        f["physaddr"] = np.column_stack([f["phys"], addr_block(f)])
        f["physfineaddr"] = np.column_stack([f["physfine"], addr_block(f)])
        f["depth"] = hull_depth(f["perp"])
    dmax = max(f["depth"][f["bulk"]].max() for f in feats)

    allc = np.concatenate([f["cc"][f["bulk"]] for f in feats])
    common = [c for c, ct in Counter(allc.tolist()).most_common(10) if ct >= 400]

    y = [f["conf"] for f in feats]
    blocks = [{k: f[k] for k in ("phys", "physfine", "physaddr", "physfineaddr")}
              for f in feats]
    print(f"\n{'='*84}\n{NAME[N]} (N={N})  extent={extent}  {len(offs)} offsets  "
          f"|E|<0.1  (normalized depth by family max {dmax:.2f})\n{'='*84}")
    print(f"  {'coarse':>6} {'n':>6} {'R2phys':>7} {'addr/phys':>10} "
          f"{'addr/phys+fine':>15} {'peakNormDepth(±offs)':>22} {'flag':>12}")
    peaks = []
    for c in common:
        masks = [(f["cc"] == c) & f["bulk"] for f in feats]
        if min(int(m.sum()) for m in masks) < 25:
            continue
        rp = held_out_r2(blocks, y, masks, "phys")[0]
        flag = "inconclusive" if rp < MINR2 else "ok"
        ep = held_out_r2(blocks, y, masks, "physaddr")[0] - rp
        epf = (held_out_r2(blocks, y, masks, "physfineaddr")[0]
               - held_out_r2(blocks, y, masks, "physfine")[0])
        # per-offset peak location for stability
        pk = []
        for f, m in zip(feats, masks):
            p = peak_norm_depth(f["depth"][m], f["conf"][m], dmax)
            if p is not None:
                pk.append(p)
        pkm = np.mean(pk) if pk else float("nan")
        pks = np.std(pk) if len(pk) > 1 else float("nan")
        n = int(sum(m.sum() for m in masks))
        if flag == "ok":
            peaks.append(pkm)
        print(f"  {c:>6} {n:>6} {rp:>7.3f} {ep:>+10.3f} {epf:>+15.3f} "
              f"{pkm:>10.2f} ±{pks:<9.2f} {flag:>12}")
    if peaks:
        sd = np.nanstd(peaks)
        note = ("small → a shared internal-space band" if sd < 0.08
                else "broad → preferred depth is class-specific, not universal")
        print(f"  --> peak normalized depth across OK classes: "
              f"mean {np.nanmean(peaks):.2f}  sd {sd:.2f}  ({note}); "
              f"per-offset stability is the ± column")
    return peaks


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (8, 10, 12)
    allpk = []
    for N in fams:
        allpk += run(N)
    if len(allpk) > 1:
        sd = np.nanstd(allpk)
        note = "clustered (shared band)" if sd < 0.08 else "spread (class-specific depths)"
        print(f"\nACROSS FAMILIES: peak normalized depth mean {np.nanmean(allpk):.2f} "
              f"sd {sd:.2f} → {note}, over {len(allpk)} OK classes")
