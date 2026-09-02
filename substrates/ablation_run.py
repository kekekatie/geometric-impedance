#!/usr/bin/env python3
"""
EXPLORATORY / INTERPRETIVE ablation of the neighbourhood-address (M4) block.
ROADMAP step 5. NOT a sealed, pre-registered study.

Question: within the sealed transport pipeline (transport_run.py, the machinery
that produced RESULTS_TRANSPORT.md / the Part II result), WHICH of the four
neighbourhood-address feature groups actually carry the coherent M4-over-M3
transport increment?

The four groups (exactly the columns transport_run._m4_cols builds):
  * perp   : shell-averaged perp coordinate at shells r = 2, 4, 8   (6 cols)
  * var    : within-shell perp variance at shells r = 2, 4, 8        (3 cols)
  * grad   : local address gradient magnitude                        (1 col)
  * depth  : hull depth (signed distance to the address point cloud) (1 col)

Nothing new is built. We reuse transport_run's build_features / assemble /
_m4_cols / held_out_r2 verbatim, the same OFFSETS, the same bulk mask, the same
codebook + rng(0), the same HistGradientBoosting regressor, and the same
leave-one-offset-out CV. The only change is COLUMN SELECTION inside the M4 block:
  - leave-one-group-out : M4 with one group removed  -> how much of the increment
                          SURVIVES without that group (the "when removed" reading
                          Fable asked for);
  - single-group-add    : M3 + one group only        -> how much that group adds
                          over M3 on its own.
Groups can be redundant, so per-group numbers need not sum to the full increment.

Internal control: the incoherent-t10 null uses the SAME M4 columns and should
read ~0 for every group -> any coherent survival is coherent-specific, not a
feature-count artefact.

Reproduce: python ablation_run.py 8 10 12   (golden is N=10; default runs all)
"""

import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import transport_run as T  # reuse the sealed harness verbatim

# Column layout inside T._m4_cols(...), shell_r = (2, 4, 8):
#   [sm2(0,1) sv2(2) sm4(3,4) sv4(5) sm8(6,7) sv8(8) grad(9) depth(10)]
GROUP_COLS = {
    "perp":  [0, 1, 3, 4, 6, 7],
    "var":   [2, 5, 8],
    "grad":  [9],
    "depth": [10],
}
ALL_COLS = list(range(11))
GROUPS = ("perp", "var", "grad", "depth")

# rungs we evaluate (all share the identical M3 baseline)
LEAVE_OUT = {f"M4_no_{g}": [c for c in ALL_COLS if c not in GROUP_COLS[g]]
             for g in GROUPS}
ONLY = {f"M4_only_{g}": GROUP_COLS[g] for g in GROUPS}


def build_blocks(N):
    """Reproduce run_family's setup exactly, then add column-ablated M4 rungs."""
    feats = [T.build_features(N, off) for off in T.OFFSETS]
    bulk_list = [f["bulk"] for f in feats]
    rng = np.random.default_rng(0)
    codebook = {}
    for f in feats:
        for k in f["motif_keys"]:
            codebook.setdefault(k, len(codebook))
    base = [T.assemble(f, codebook, rng) for f in feats]  # gives sealed M3, M4

    blocks = []
    for f, b in zip(feats, base):
        M3 = b["M3"]
        full_m4 = T._m4_cols(f, f["perp"])                # the exact sealed M4 cols
        rungs = {"M3": M3, "M4": np.column_stack([M3, full_m4])}
        for label, cols in {**LEAVE_OUT, **ONLY}.items():
            rungs[label] = np.column_stack([M3, full_m4[:, cols]])
        blocks.append(rungs)
    # sanity: our reconstructed full M4 must equal the harness's sealed M4
    for b, bl in zip(base, blocks):
        assert np.allclose(b["M4"], bl["M4"]), "reconstructed M4 != sealed M4"
    return feats, bulk_list, blocks


def evaluate(feats, bulk_list, blocks, y_key):
    y = ([f["ret"][10] for f in feats] if y_key is None
         else [f[y_key] for f in feats])
    scores = {}
    for rung in ["M3", "M4", *LEAVE_OUT, *ONLY]:
        scores[rung] = T.held_out_r2(blocks, y, bulk_list, rung)
    return scores


def report(N, scores, label):
    m3 = scores["M3"][0]
    m4 = scores["M4"][0]
    I_full = m4 - m3
    print(f"\n  [{label}]  M3 R2 = {m3:+.4f}   M4 R2 = {m4:+.4f}   "
          f"full M4-over-M3 = {I_full:+.4f}")
    print(f"     {'group':7s} {'leave-out incr':>15s} {'drop(=full-LO)':>15s} "
          f"{'group-alone incr':>17s}")
    for g in GROUPS:
        lo = scores[f"M4_no_{g}"][0] - m3          # increment surviving without g
        drop = I_full - lo                          # increment lost by removing g
        only = scores[f"M4_only_{g}"][0] - m3       # increment from g alone
        print(f"     {g:7s} {lo:+15.4f} {drop:+15.4f} {only:+17.4f}")
    return I_full


def main(families=(8, 10, 12)):
    for N in families:
        feats, bulk_list, blocks = build_blocks(N)
        nb = sum(int(b.sum()) for b in bulk_list)
        print(f"\n{'='*72}\n{T.NAME[N]} (N={N})  {len(T.OFFSETS)} offsets  "
              f"{nb} bulk vertices total\n{'='*72}")
        sc_prim = evaluate(feats, bulk_list, blocks, "ld_primary")
        report(N, sc_prim, "coherent-primary  |E| in [0.8, 2.5]")
        sc_inc = evaluate(feats, bulk_list, blocks, None)
        report(N, sc_inc, "incoherent-t10 null (internal control)")


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (8, 10, 12)
    main(fams)
