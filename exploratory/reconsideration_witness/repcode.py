"""Distance-3 repeated-check repetition code: exact GF(2) simulator and linear model.

Frozen by PREREGISTRATION.md (2026-11-12). Bit-flip (X) errors only.

Faults (each a GF(2) bit that is present or absent in a history):
  ('d', j, t)  data-X on data qubit j in {0,1,2} at round t in 0..T-1
  ('m', c, t)  measurement flip on check c in {0,1} at round t in 0..T-1

A loss of the middle qubit d1 at onset round s is, physically and exactly, a
data-X on d1 at round s -- fault ('d', 1, s). The loss *report* (handled in the
decoders) is side information that frees the located faults ('d', 1, s) for
s in O; the true onset and whether a flip actually occurred are scoring-only.

The code is linear over GF(2): the detector signature of any set of faults is
the XOR of the single-fault signatures, and the logical flip is the XOR of the
single-fault logical bits. build_linear_model() returns those signatures and a
self-check confirms composition against the direct simulator.
"""

from itertools import combinations

D = 3                      # data qubits 0,1,2
T = 6                      # check rounds 0..5
CHECKS = [(0, 1), (1, 2)]  # c0 = Z d0 Z d1 ; c1 = Z d1 Z d2
O = (1, 2)                 # plausible onset interval for the d1 loss
REPORT_ROUND = 4           # the delayed report arrives at end of round 4
LOSS_SITE = 1              # d1
COMMIT_C = 3               # streaming commit/core width (rounds 0,1,2)
BUFFER_B = 1               # streaming buffer width (round 3)
WINDOW_W = COMMIT_C + BUFFER_B
CUT = COMMIT_C - 1         # last committed round index = 2 ; cut sits between 2 and 3


def all_fault_ids():
    """The full, ordered list of base fault ids (deterministic order)."""
    faults = []
    for j in range(D):
        for t in range(T):
            faults.append(('d', j, t))
    for c in range(len(CHECKS)):
        for t in range(T):
            faults.append(('m', c, t))
    return faults


def all_detector_ids():
    """Ordered detector list: (c, t) for t in 0..T-1, then closing (c, 'f')."""
    dets = []
    for c in range(len(CHECKS)):
        for t in range(T):
            dets.append((c, t))
    for c in range(len(CHECKS)):
        dets.append((c, 'f'))
    return dets


def simulate(faults):
    """Exact simulation. faults: iterable of fault ids present.

    Returns (detectors, logical_flip):
      detectors: dict det_id -> 0/1
      logical_flip: 0/1, the flip of Z_L on support {d0}
    """
    present = set(faults)

    # Cumulative data-flip x_j(t) = XOR of ('d', j, tau) for tau <= t.
    x = [[0] * T for _ in range(D)]
    for j in range(D):
        acc = 0
        for t in range(T):
            if ('d', j, t) in present:
                acc ^= 1
            x[j][t] = acc

    # Measured check value m[c][t].
    m = [[0] * T for _ in range(len(CHECKS))]
    for c, support in enumerate(CHECKS):
        for t in range(T):
            val = 0
            for j in support:
                val ^= x[j][t]
            if ('m', c, t) in present:
                val ^= 1
            m[c][t] = val

    det = {}
    for c, support in enumerate(CHECKS):
        prev = 0  # perfect prep: all checks read 0 before round 0
        for t in range(T):
            det[(c, t)] = m[c][t] ^ prev
            prev = m[c][t]
        # closing detector: last measured check vs perfect final data readout
        f_c = 0
        for j in support:
            f_c ^= x[j][T - 1]
        det[(c, 'f')] = m[c][T - 1] ^ f_c

    # Z_L on support {d0}: flipped only by d0 data-X faults.
    logical_flip = sum(1 for t in range(T) if ('d', 0, t) in present) % 2
    return det, logical_flip


def build_linear_model():
    """Return (H, L, det_ids, fault_ids).

    H[fault] = frozenset of detector ids that this single fault turns on.
    L[fault] = 0/1 logical bit of this single fault.
    """
    fault_ids = all_fault_ids()
    det_ids = all_detector_ids()
    H = {}
    L = {}
    for f in fault_ids:
        det, lf = simulate([f])
        H[f] = frozenset(d for d in det_ids if det[d])
        L[f] = lf
    return H, L, det_ids, fault_ids


def detectors_of(faults, H):
    """Detector set (frozenset) of a fault collection, via XOR of signatures."""
    acc = set()
    for f in faults:
        acc ^= set(H[f])
    return frozenset(acc)


def logical_of(faults, L):
    return sum(L[f] for f in faults) % 2


def _self_check():
    H, L, det_ids, fault_ids = build_linear_model()
    import random
    rng = random.Random(0)
    # linearity: random subsets must match direct simulation
    for _ in range(2000):
        k = rng.randint(0, 5)
        subset = rng.sample(fault_ids, k)
        det, lf = simulate(subset)
        direct = frozenset(d for d in det_ids if det[d])
        composed = detectors_of(subset, H)
        assert direct == composed, (subset, direct, composed)
        assert lf == logical_of(subset, L)
    # fault-free run is clean
    det, lf = simulate([])
    assert all(v == 0 for v in det.values()) and lf == 0
    # a single d0 error flips the logical
    assert logical_of([('d', 0, 2)], L) == 1
    # a d1 or d2 error does not flip Z_L on {d0}
    assert logical_of([('d', 1, 2)], L) == 0
    assert logical_of([('d', 2, 2)], L) == 0
    rank = _gf2_rank([list(_vec(H[f], det_ids)) for f in fault_ids])
    print("self-check OK")
    print("faults:", len(fault_ids), "detectors:", len(det_ids), "H rank:", rank,
          "null dim:", len(fault_ids) - rank)


def _vec(detset, det_ids):
    return [1 if d in detset else 0 for d in det_ids]


def _gf2_rank(rows):
    rows = [r[:] for r in rows]
    ncol = len(rows[0]) if rows else 0
    rank = 0
    pivot_row = 0
    for col in range(ncol):
        sel = None
        for r in range(pivot_row, len(rows)):
            if rows[r][col]:
                sel = r
                break
        if sel is None:
            continue
        rows[pivot_row], rows[sel] = rows[sel], rows[pivot_row]
        for r in range(len(rows)):
            if r != pivot_row and rows[r][col]:
                rows[r] = [a ^ b for a, b in zip(rows[r], rows[pivot_row])]
        pivot_row += 1
        rank += 1
        if pivot_row == len(rows):
            break
    return rank


if __name__ == '__main__':
    _self_check()
