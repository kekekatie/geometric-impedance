#!/usr/bin/env python3
"""
ROADMAP step 1 — nonlinear residualization cross-check.

The sealed transport result reported an M4-over-M3 increment. This asks the cleanest form of
"what does the address know that the physical descriptors do not?": residualize each address
(M4) feature against M3 with the SAME nonlinear model, keep only the part M3 cannot explain,
and test whether that residual address still predicts coherent transport beyond M3.

Cross-fit and honest: for each held-out offset the residuals and the transport model are both
trained only on the other offsets, so the test evaluation never sees itself. If the residualized
increment matches the plain M4-over-M3 increment, the address signal is genuinely the
M3-orthogonal address content, not M3 leaking through the address features.
"""

import sys
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from transport_run import build_features, assemble, OFFSETS, NAME, GBT

EXT = 14


def run(N, offs=None, target="ld_primary"):
    offs = offs or OFFSETS[:4]
    feats = [build_features(N, o, extent=EXT) for o in offs]
    rng = np.random.default_rng(0)
    cb = {}
    for f in feats:
        for k in f["motif_keys"]:
            cb.setdefault(k, len(cb))
    A = [assemble(f, cb, rng) for f in feats]
    for a in A:
        a["m4"] = a["M4"][:, a["M3"].shape[1]:]        # address-only columns
    bulk = [f["bulk"] for f in feats]
    y = [f[target] for f in feats]
    K = len(feats)

    inc_plain, inc_resid, base, addr_pred = [], [], [], []
    for t in range(K):
        tr = [o for o in range(K) if o != t]
        M3tr = np.vstack([A[o]["M3"][bulk[o]] for o in tr])
        M3te = A[t]["M3"][bulk[t]]
        m4tr = np.vstack([A[o]["m4"][bulk[o]] for o in tr])
        m4te = A[t]["m4"][bulk[t]]
        ytr = np.concatenate([y[o][bulk[o]] for o in tr])
        yte = y[t][bulk[t]]
        # residualize each address column against M3 (same nonlinear model)
        Rtr = np.empty_like(m4tr); Rte = np.empty_like(m4te)
        pred_r2 = []
        for j in range(m4tr.shape[1]):
            g = HistGradientBoostingRegressor(**GBT).fit(M3tr, m4tr[:, j])
            Rtr[:, j] = m4tr[:, j] - g.predict(M3tr)
            Rte[:, j] = m4te[:, j] - g.predict(M3te)
            if m4te[:, j].std() > 1e-9:
                pred_r2.append(r2_score(m4te[:, j], g.predict(M3te)))
        addr_pred.append(np.mean(pred_r2))
        r_m3 = r2_score(yte, HistGradientBoostingRegressor(**GBT).fit(M3tr, ytr).predict(M3te))
        r_m4 = r2_score(yte, HistGradientBoostingRegressor(**GBT)
                        .fit(np.column_stack([M3tr, m4tr]), ytr)
                        .predict(np.column_stack([M3te, m4te])))
        r_res = r2_score(yte, HistGradientBoostingRegressor(**GBT)
                         .fit(np.column_stack([M3tr, Rtr]), ytr)
                         .predict(np.column_stack([M3te, Rte])))
        base.append(r_m3); inc_plain.append(r_m4 - r_m3); inc_resid.append(r_res - r_m3)

    print(f"\n{'='*60}\n{NAME[N]} (N={N})  extent={EXT}  {len(offs)} offsets  "
          f"target={target}\n{'='*60}")
    print(f"  address predictable from M3 (held-out R²): {np.mean(addr_pred):.3f}  "
          f"→ residualizing removes this much of the address")
    print(f"  M3 baseline R²                 : {np.mean(base):.4f}")
    print(f"  plain M4-over-M3 increment     : {np.mean(inc_plain):+.4f} ± {np.std(inc_plain):.4f}")
    print(f"  residualized-address increment : {np.mean(inc_resid):+.4f} ± {np.std(inc_resid):.4f}")
    if abs(np.mean(inc_resid)) < 0.4 * abs(np.mean(inc_plain)):
        print(f"  --> residual << plain: the address's transport value is NOT in its "
              f"M3-orthogonal part;\n      it lives in the address structure SHARED with the "
              f"physical descriptors (a re-encoding),\n      consistent with the "
              f"stratified-shuffle kill. Keep the humble language.")
    else:
        print(f"  --> residual ≈ plain: the address carries genuinely M3-orthogonal transport "
              f"content.")
    return np.mean(inc_plain), np.mean(inc_resid)


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (10,)
    for N in fams:
        run(N)
