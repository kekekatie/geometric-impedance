#!/usr/bin/env python3
"""
EXPLORATORY — "address made physical": within a fixed local motif, does confined-state
weight vary with perpendicular-space placement? (GPT's within-motif design.)

If two vertices with the SAME local motif but different address (perp-space depth/location)
carry systematically different E~0 confined-state weight, then local physical identity does
NOT fully determine spectral role — global quasiperiodic placement matters. That is the
visual manifestation of "the reading lives in the coherent stationary spectral structure".

Rigour (per GPT): within each common motif class, the effect size is the held-out-offset
R^2 gain of adding ADDRESS features over a baseline of PHYSICAL features INCLUDING
long-range ones (so we don't rediscover the M3-far issue), predicting confined weight.
"""

import sys
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from transport_run import (build_features, held_out_r2, _m4_cols, hull_depth,
                           OFFSETS, NAME)

ECONF = 0.1                                    # |E| < ECONF = confined/pseudogap window


def confined_weight(f):
    ev, w2 = f["evals"], f["w2"]
    return w2[:, np.abs(ev) < ECONF].sum(1)


def coarse_motif(f):
    """Rotation/reflection-invariant vertex type: sorted angular gaps between
    consecutive incident edges (the standard ~handful of vertex configurations),
    so classes are large enough for a within-motif test."""
    par, adj, n = f["par"], f["adj"], f["n"]
    keys = []
    for i in range(n):
        nb = adj[i]
        if len(nb) < 2:
            keys.append((len(nb),)); continue
        d = par[nb] - par[i]
        th = np.sort(np.arctan2(d[:, 1], d[:, 0]))
        gaps = np.diff(np.concatenate([th, [th[0] + 2 * np.pi]]))
        keys.append((len(nb),) + tuple(np.round(np.sort(gaps), 1).tolist()))
    return keys


def phys_block(f):                             # physical only, incl. long-range, NO address
    return np.column_stack([f["dens"], f["deg"], f["edge_len_mean"], f["edge_len_var"],
                            f["g_small"][0], f["g_small"][1], f["g_med"][0], f["g_med"][1],
                            f["g_far"][0], f["g_far"][1], f["nbr_deg"][0], f["nbr_deg"][1],
                            f["cg_psi"][0], f["cg_psi"][1]])


def addr_block(f):
    return np.column_stack([f["perp"], _m4_cols(f, f["perp"])])


def run(N, extent=12, offs=None, make_fig=True):
    offs = offs or OFFSETS[:4]
    feats = [build_features(N, o, extent=extent, return_dynamics=True) for o in offs]
    codebook = {}
    for f in feats:
        f["cmotif"] = coarse_motif(f)
        for k in f["cmotif"]:
            codebook.setdefault(k, len(codebook))
    for f in feats:
        f["motif_code"] = np.array([codebook[k] for k in f["cmotif"]])
        f["conf"] = confined_weight(f)
        f["phys"] = phys_block(f)
        f["physaddr"] = np.column_stack([f["phys"], addr_block(f)])
        f["depth"] = hull_depth(f["perp"])

    allcodes = np.concatenate([f["motif_code"][f["bulk"]] for f in feats])
    common = [c for c, ct in Counter(allcodes.tolist()).most_common(10) if ct >= 400]

    print(f"\n{'='*72}\n{NAME[N]} (N={N})  extent={extent}  {len(offs)} offsets  "
          f"confined window |E|<{ECONF}\n{'='*72}")
    print(f"  {'motif':>6} {'n(bulk)':>8} {'R2(phys)':>9} {'R2(phys+addr)':>14} "
          f"{'within-motif addr effect':>26}")
    y = [f["conf"] for f in feats]
    blocks = [{"phys": f["phys"], "physaddr": f["physaddr"]} for f in feats]
    results = []
    for c in common:
        masks = [(f["motif_code"] == c) & f["bulk"] for f in feats]
        if min(int(m.sum()) for m in masks) < 25:
            continue
        rp = held_out_r2(blocks, y, masks, "phys")[0]
        rpa = held_out_r2(blocks, y, masks, "physaddr")[0]
        n = int(sum(m.sum() for m in masks))
        results.append((c, n, rp, rpa))
        print(f"  {c:>6} {n:>8} {rp:>9.3f} {rpa:>14.3f} {rpa-rp:>+26.3f}")

    if make_fig and results:
        # figure for the most common motif: same motif, different address
        c0 = max(results, key=lambda r: r[1])[0]
        depth = np.concatenate([f["depth"][(f["motif_code"] == c0) & f["bulk"]] for f in feats])
        conf = np.concatenate([f["conf"][(f["motif_code"] == c0) & f["bulk"]] for f in feats])
        f0 = feats[0]
        mask0 = (f0["motif_code"] == c0) & f0["bulk"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        ax1.scatter(f0["par"][:, 0], f0["par"][:, 1], s=3, c="0.85", linewidths=0)
        sc = ax1.scatter(f0["par"][mask0, 0], f0["par"][mask0, 1],
                         c=f0["conf"][mask0], s=34, cmap="magma", linewidths=0)
        ax1.set_aspect("equal"); ax1.set_xticks([]); ax1.set_yticks([])
        ax1.set_title(f"{NAME[N]}: one motif class (#{c0}) in physical space,\n"
                      f"coloured by E≈0 confined weight")
        fig.colorbar(sc, ax=ax1, shrink=0.7, label="confined weight")
        ax2.scatter(depth, conf, s=10, c="#e45756", alpha=0.5, linewidths=0)
        # binned trend
        order = np.argsort(depth)
        b = np.array_split(order, 12)
        bx = [depth[i].mean() for i in b]; by = [conf[i].mean() for i in b]
        ax2.plot(bx, by, "k-o", lw=2, ms=5, label="binned mean")
        ax2.set_xlabel("hull / window depth (address: deeper = more interior)")
        ax2.set_ylabel("E≈0 confined weight")
        ax2.set_title(f"same motif (#{c0}, n={len(conf)}), different address\n"
                      f"→ different confined weight?")
        ax2.legend(frameon=False)
        out = __file__.rsplit("/", 1)[0] + f"/confined_address_{NAME[N]}.png"
        fig.suptitle("EXPLORATORY — is local motif enough to fix spectral role, "
                     "or does global address matter?", fontsize=12)
        fig.savefig(out, dpi=130, bbox_inches="tight")
        print(f"  wrote {out}")
    return results


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (10,)
    for N in fams:
        run(N, make_fig=True)
