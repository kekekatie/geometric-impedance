#!/usr/bin/env python3
"""
EXPLORATORY — split the confined-address effect into a RADIAL part (depth in the window)
and a NON-RADIAL part (angular + finer placement). GPT's sharpening of the onion result.

Three questions, held-out:
  1. how much confined weight does radial depth alone predict?
  2. how much does non-radial address add AFTER depth is in?  (angular, then finer)
  3. within a fixed FINE vertex type, does non-radial address still help beyond depth?

Radial = |perp - window_centre|. Angular = its direction. Finer = the neighbourhood
address-organization features (shell-averaged perp, variance, gradient, hull depth).
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from transport_run import build_features, held_out_r2, _m4_cols, hull_depth, OFFSETS, NAME
from confined_address import confined_weight

EXT = {8: 14, 10: 14, 12: 13}


def blocks_for(f):
    P = f["perp"]
    c = P[f["bulk"]].mean(0)                      # window centre (this realization)
    rel = P - c
    rad = np.hypot(rel[:, 0], rel[:, 1])
    ang = np.arctan2(rel[:, 1], rel[:, 0])
    co, si = np.cos(ang), np.sin(ang)
    hd = hull_depth(P)                            # proper window-depth (distance to edge)
    nbr = _m4_cols(f, P)[:, :-1]                  # shell-perp means/vars + gradient; drop
    #                                              the last col (hull depth) -> in RAD already
    RAD = np.column_stack([hd, rad])                             # radial: window-depth
    RADANG = np.column_stack([RAD, co, si, rad*co, rad*si])      # + angular = own 2D position
    FULL = np.column_stack([RADANG, nbr])                        # + neighbourhood address org
    return {"RAD": RAD, "RADANG": RADANG, "FULL": FULL}


def run(N, offs=None):
    offs = offs or OFFSETS[:3]
    feats = [build_features(N, o, extent=EXT[N], return_dynamics=True) for o in offs]
    fine_cb = {}
    for f in feats:
        for k in f["motif_keys"]:
            fine_cb.setdefault(k, len(fine_cb))
    for f in feats:
        f.update(blocks_for(f))
        f["conf"] = confined_weight(f)
        f["fine"] = np.array([fine_cb[k] for k in f["motif_keys"]])
    bulk = [f["bulk"] for f in feats]
    y = [f["conf"] for f in feats]
    B = [{k: f[k] for k in ("RAD", "RADANG", "FULL")} for f in feats]

    r_rad = held_out_r2(B, y, bulk, "RAD")[0]
    r_ra = held_out_r2(B, y, bulk, "RADANG")[0]
    r_full = held_out_r2(B, y, bulk, "FULL")[0]
    print(f"\n{'='*66}\n{NAME[N]} (N={N})  extent={EXT[N]}  {len(offs)} offsets  "
          f"predicting E≈0 confined weight (held-out R²)\n{'='*66}")
    print(f"  radial window-depth only        : {r_rad:.3f}")
    print(f"  + angular (own 2D position)     : {r_ra:.3f}   (angular adds {r_ra-r_rad:+.3f})")
    print(f"  + neighbourhood address org     : {r_full:.3f}   (nbhd adds {r_full-r_ra:+.3f})")
    print(f"  --> non-radial address beyond depth = {r_full-r_rad:+.3f}  "
          f"(of {r_full:.3f} total)")

    # within fixed fine type: does non-radial address help beyond depth?
    allfine = np.concatenate([f["fine"][f["bulk"]] for f in feats])
    common = [c for c, ct in Counter(allfine.tolist()).most_common(30) if ct >= 300]
    incs = []
    print(f"  within fixed FINE type (n>=300): non-radial-address increment over depth")
    for c in common[:6]:
        masks = [(f["fine"] == c) & f["bulk"] for f in feats]
        if min(int(m.sum()) for m in masks) < 25:
            continue
        rr = held_out_r2(B, y, masks, "RAD")[0]
        rf = held_out_r2(B, y, masks, "FULL")[0]
        n = int(sum(m.sum() for m in masks))
        incs.append(rf - rr)
        print(f"     fine {c:>4}  n={n:>4}  depth {rr:+.3f} -> full {rf:+.3f}  "
              f"non-radial {rf-rr:+.3f}")
    if incs:
        print(f"  --> median within-fine-type non-radial increment: {np.median(incs):+.3f}")
    return dict(rad=r_rad, radang=r_ra, full=r_full)


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (10,)
    for N in fams:
        run(N)
