#!/usr/bin/env python3
"""
EXPLORATORY — why does each vertex type prefer its own perp-space depth?

Hypothesis: confined-state weight is a smooth FIELD over the acceptance window
(perpendicular space). Each vertex type occupies its own sub-region of the window, so
each type samples a different slice of that field -> a different "preferred depth". If so,
2D perp position should explain confined weight far better than 1D hull-depth alone, and
about as well as the vertex type (which is itself a window sub-region).

Paints confined weight directly onto the window, and compares descriptors by held-out R^2.
"""

import sys
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from transport_run import build_features, held_out_r2, hull_depth, OFFSETS, NAME
from confined_address import confined_weight, coarse_motif

EXT = {8: 14, 10: 14, 12: 13}


def run(N, offs=None):
    offs = offs or OFFSETS[:3]
    feats = [build_features(N, o, extent=EXT[N], return_dynamics=True) for o in offs]
    cb = {}
    for f in feats:
        f["cm"] = coarse_motif(f)
        for k in f["cm"]:
            cb.setdefault(k, len(cb))
    for f in feats:
        f["conf"] = confined_weight(f)
        f["depthv"] = hull_depth(f["perp"])
        code = np.array([cb[k] for k in f["cm"]])
        f["type_oh"] = np.eye(len(cb))[code]
        f["depth"] = f["depthv"][:, None]
        f["perpxy"] = f["perp"]
        f["perptype"] = np.column_stack([f["perp"], f["type_oh"]])

    bulk = [f["bulk"] for f in feats]
    y = [f["conf"] for f in feats]
    B = [{k: f[k] for k in ("depth", "perpxy", "type_oh", "perptype")} for f in feats]
    r_depth = held_out_r2(B, y, bulk, "depth")[0]
    r_perp = held_out_r2(B, y, bulk, "perpxy")[0]
    r_type = held_out_r2(B, y, bulk, "type_oh")[0]
    r_pt = held_out_r2(B, y, bulk, "perptype")[0]

    print(f"\n{'='*66}\n{NAME[N]} (N={N})  extent={EXT[N]}  {len(offs)} offsets  "
          f"predicting E≈0 confined weight (held-out R²)\n{'='*66}")
    print(f"  1D hull-depth (radial only) : {r_depth:.3f}")
    print(f"  2D perp position (the field): {r_perp:.3f}")
    print(f"  vertex type (window region) : {r_type:.3f}")
    print(f"  perp + type                 : {r_pt:.3f}")
    verdict = ("2D window field >> 1D depth, and ≈ type → confined weight is a smooth "
               "field over the window that each type samples"
               if (r_perp - r_depth > 0.1 and abs(r_perp - r_type) < 0.12)
               else "mixed — read the map")
    print(f"  --> {verdict}")

    # ---- the picture: confined weight painted onto perpendicular space (the window) ----
    f0 = feats[0]
    m = f0["bulk"]
    P = f0["perp"][m]; C = f0["conf"][m]
    code0 = np.array([cb[k] for k in f0["cm"]])[m]
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6.6))
    hull = ConvexHull(f0["perp"][m])
    for ax in (axA, axB):
        for s in hull.simplices:
            ax.plot(f0["perp"][m][s, 0], f0["perp"][m][s, 1], color="0.7", lw=.8)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    order = np.argsort(C)
    sc = axA.scatter(P[order, 0], P[order, 1], c=C[order], s=22, cmap="magma",
                     linewidths=0)
    axA.set_title(f"{NAME[N]}: E≈0 confined weight painted onto\nperpendicular space "
                  f"(the acceptance window)")
    fig.colorbar(sc, ax=axA, shrink=0.7, label="confined weight")
    # top vertex types by count, each its own colour -> shows they tile the window
    common = [c for c, _ in Counter(code0.tolist()).most_common(7)]
    palette = plt.get_cmap("tab10")
    axB.scatter(P[:, 0], P[:, 1], s=10, c="0.85", linewidths=0)
    for i, c in enumerate(common):
        sel = code0 == c
        axB.scatter(P[sel, 0], P[sel, 1], s=16, color=palette(i), linewidths=0,
                    label=f"type {c}")
    axB.set_title(f"{NAME[N]}: vertex types tile the window\n(each type = its own region)")
    axB.legend(frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(1, .5))
    fig.suptitle("EXPLORATORY — is 'preferred depth' just a slice of a window-wide field?",
                 fontsize=12)
    out = __file__.rsplit("/", 1)[0] + f"/preferred_depth_{NAME[N]}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"  wrote {out}")

    # ---- second figure: the radial profile, and types as ordered depth-bands ----
    depth_all = np.concatenate([f["depthv"][f["bulk"]] for f in feats])
    conf_all = np.concatenate([f["conf"][f["bulk"]] for f in feats])
    code_all = np.concatenate([np.array([cb[k] for k in f["cm"]])[f["bulk"]] for f in feats])
    fig2, (p1, p2) = plt.subplots(1, 2, figsize=(14, 5.6))
    # global radial profile: mean +/- std of confined weight vs hull depth
    order = np.argsort(depth_all)
    bins = np.array_split(order, 14)
    bx = [depth_all[b].mean() for b in bins]
    bm = [conf_all[b].mean() for b in bins]
    bs = [conf_all[b].std() for b in bins]
    p1.fill_between(bx, np.array(bm) - np.array(bs), np.array(bm) + np.array(bs),
                    color="#e45756", alpha=.18, label="±1 sd (spread)")
    p1.plot(bx, bm, "o-", color="#c23", lw=2, ms=5, label="mean")
    p1.set_xlabel("hull / window depth  (edge → centre)")
    p1.set_ylabel("E≈0 confined weight")
    p1.set_title(f"{NAME[N]}: global radial profile in the window")
    p1.legend(frameon=False)
    # types as ordered depth-bands: each common type's depth distribution
    common2 = [c for c, ct in Counter(code_all.tolist()).most_common(9) if ct >= 200]
    data = [(c, depth_all[code_all == c]) for c in common2]
    data.sort(key=lambda t: np.median(t[1]))
    p2.boxplot([d for _, d in data], vert=False, showfliers=False,
               tick_labels=[f"type {c}" for c, _ in data])
    p2.set_xlabel("hull / window depth of the type's members")
    p2.set_title(f"{NAME[N]}: vertex types occupy ordered depth-bands")
    fig2.suptitle("EXPLORATORY — a radial confined-weight profile, sampled by "
                  "radially-ordered vertex types", fontsize=12)
    out2 = __file__.rsplit("/", 1)[0] + f"/preferred_depth_profile_{NAME[N]}.png"
    fig2.savefig(out2, dpi=130, bbox_inches="tight")
    print(f"  wrote {out2}")
    return dict(depth=r_depth, perp=r_perp, type=r_type)


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (10,)
    for N in fams:
        run(N)
