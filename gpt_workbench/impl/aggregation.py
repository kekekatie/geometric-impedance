"""
Six-offset aggregation and multiplicity (conditional-null v4.1 §4/§6; MSD v8.1 §8/§12).

M9      : per-offset median across the NINE configs, then median across the six offsets.
M_perm,7: the same over the SEVEN permutation-feasible configs.
Membership is FIXED a priori and is NEVER changed by observed fit quality or outcomes: a failing
config is never dropped and the statistic is never recomputed over a surviving subset.
"""
import numpy as np
from . import constants as C


def _nested_median(values):
    """values: (n_configs, 6) -> median over configs per offset, then median over the six offsets."""
    values = np.asarray(values, float)
    assert values.shape[1] == C.N_OFFSETS, f"need 6 offsets, got {values.shape[1]}"
    per_offset = np.median(values, axis=0)      # median across configs, per offset
    return float(np.median(per_offset))         # median across the six offsets


def M9(values_9x6):
    """M9 over ALL nine configs. Asserts membership is exactly nine (no dropping)."""
    v = np.asarray(values_9x6, float)
    assert v.shape[0] == 9, f"M9 must span exactly 9 configs, got {v.shape[0]} (no cell-dropping allowed)"
    assert not np.isnan(v).any(), "M9 inputs must be defined for all nine configs"
    return _nested_median(v)


def M_perm7(values_7x6):
    """M_perm,7 over exactly the seven permutation-feasible configs."""
    v = np.asarray(values_7x6, float)
    assert v.shape[0] == 7, f"M_perm,7 must span exactly 7 feasible cells, got {v.shape[0]}"
    return _nested_median(v)


def delta_cap(capacity_draws_9x6):
    """delta_cap = 95th percentile of the 200-draw M9 capacity distribution (physical v7 §6).
    Input: (200, 9, 6) capacity increments -> M9 per draw -> 95th percentile."""
    draws = np.asarray(capacity_draws_9x6, float)
    assert draws.shape[0] == C.CAPACITY_DRAWS, f"need {C.CAPACITY_DRAWS} capacity draws"
    assert draws.shape[1:] == (9, C.N_OFFSETS)
    per_draw = np.array([M9(draws[d]) for d in range(draws.shape[0])])
    return float(np.percentile(per_draw, 95))


def R_kill(plain_9x6, shuf_9x6, dcap):
    """Paired shuffle-kill (MSD v8.1 §12 G4). red_{c,o}=(plain-shuf)/plain built BEFORE aggregating.
    Any required fold/config with plain <= delta_cap or <= 0 => red undefined => GLOBAL G4 undefined
    => returns None (mixed/undetectable). Never recomputed over a surviving subset."""
    plain = np.asarray(plain_9x6, float); shuf = np.asarray(shuf_9x6, float)
    assert plain.shape == shuf.shape == (9, C.N_OFFSETS)
    undefined = (plain <= dcap) | (plain <= 0)
    if undefined.any():
        return None
    red = (plain - shuf) / plain
    return _nested_median(red)


def sign_support(values_6):
    """>= 5/6 offsets positive is a supporting criterion (not the test)."""
    v = np.asarray(values_6, float)
    assert v.size == C.N_OFFSETS
    return int(np.sum(v > 0)) >= C.SIGN_STABLE_MIN


def westfall_young(obs_T7, null_T7xB):
    """Step-down max-T over the SEVEN feasible cells (conditional-null v4.1 §4).
    obs_T7: (7,) signed one-sided per-config statistics. null_T7xB: (7, B) raw permutation increments.
    Returns q-tilde per config (extremeness under the algorithmic reference), monotone-enforced."""
    obs = np.asarray(obs_T7, float); null = np.asarray(null_T7xB, float)
    assert obs.shape == (7,), f"Westfall-Young obs must be shape (7,), got {obs.shape}"
    assert null.shape == (7, C.B_PERM), f"Westfall-Young null must be shape (7, {C.B_PERM}), got {null.shape}"
    B = null.shape[1]
    order = np.argsort(-obs)                 # descending observed
    q = np.zeros(7)
    prev = 0.0
    for rank, ci in enumerate(order):
        tail = order[rank:]                  # {(i),...,(7)}
        maxnull = null[tail].max(0)          # max over the remaining hypotheses, per b
        qi = (1 + int(np.sum(maxnull >= obs[ci]))) / (B + 1)
        prev = max(prev, qi)                 # enforce monotone non-decreasing
        q[ci] = prev
    return q
