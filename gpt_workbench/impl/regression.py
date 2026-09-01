"""
Frozen regressor and increment machinery (physical v7 §1/§2/§5; conditional-null v4.1 §1).

Regressor is HistGradientBoostingRegressor with the sealed hyper-parameters. Increments are
ΔR² = R²(X_r + •) − R²(X_r), held out. Inner CV uses the frozen PC1-slab construction.

NOTE (governance): this module supplies the mechanism only. It is exercised on SYNTHETIC arrays in
the test-suite; it is NOT run against study targets/addresses/outcomes (that is the prohibited
confirmatory run).
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from . import constants as C


def make_regressor():
    return HistGradientBoostingRegressor(**C.REGRESSOR)


def gbt_r2(Xtr, ytr, Xte, yte):
    """Fit the frozen regressor on train, return out-of-sample R^2 on test."""
    m = make_regressor().fit(Xtr, ytr)
    pred = m.predict(Xte)
    ss_res = np.sum((yte - pred) ** 2)
    ss_tot = np.sum((yte - yte.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0


def increment(X, Xadd, y, train_idx, test_idx):
    """ΔR² = R²([X,Xadd]) − R²(X), held out on test_idx (trained on train_idx)."""
    base = gbt_r2(X[train_idx], y[train_idx], X[test_idx], y[test_idx])
    aug = np.column_stack([X, Xadd])
    full = gbt_r2(aug[train_idx], y[train_idx], aug[test_idx], y[test_idx])
    return full - base


def pc1_slabs(coords, lifts, n_slabs=C.N_SLABS):
    """Frozen inner-CV slabs (physical v7 §5): PC1 of centred r16 coords -> project -> n contiguous
    equal-count slabs. PC1 sign: PC1[0] >= 0 (else PC1[1] >= 0). Ties broken by lexicographic order
    of the integer lift coordinates. Remainder vertices go to the lowest-index slabs."""
    coords = np.asarray(coords, float)
    Xc = coords - coords.mean(0)
    cov = np.cov(Xc.T)
    w, V = np.linalg.eigh(cov)
    pc1 = V[:, int(np.argmax(w))].copy()
    if pc1[0] < 0 or (pc1[0] == 0 and pc1[1] < 0):     # frozen sign convention
        pc1 = -pc1
    proj = Xc @ pc1
    lifts = np.asarray(lifts)
    keys = [(proj[i],) + tuple(int(x) for x in lifts[i]) for i in range(len(proj))]
    order = sorted(range(len(proj)), key=lambda i: keys[i])
    n = len(order); base = n // n_slabs; rem = n % n_slabs
    sizes = [base + (1 if s < rem else 0) for s in range(n_slabs)]  # remainder -> lowest-index slabs
    labels = np.empty(n, int); pos = 0
    for s, sz in enumerate(sizes):
        for j in order[pos:pos + sz]:
            labels[j] = s
        pos += sz
    return labels
