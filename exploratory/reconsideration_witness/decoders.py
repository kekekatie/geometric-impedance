"""Decoders for the reconsideration-witness search.

Two decoders, frozen by PREREGISTRATION.md:

  * Full-history reference -- keeps every detector, decodes by EXACT MAP
    marginalisation over the whole fault space, returning P(logical=0|evidence)
    and P(logical=1|evidence). Pre-flag: all weights normal. Post-flag: the
    located loss faults ('d',1,s) for s in O are freed (weight 1/2) -- the
    erasure the delayed report licenses.

  * Streaming (sliding window) -- a HARD committer. It decodes the committed
    core [rounds 0..2] by MAP (open right boundary), commits the core logical
    contribution into a one-bit Pauli frame, PRUNES the core detectors keeping
    only (frame_bit, boundary m_c(2), live round-3 detectors, pending), then
    decodes the live region [rounds 3..5]+closers against the carried boundary.
    A delayed report whose interval lies in the pruned core cannot re-open the
    commit: the frozen revision touches only live edges, of which the early
    erasure has none, so the streaming prediction does not move.

All numeric MAP is exact for this tiny instance (null space 2**16).
"""

import numpy as np
from functools import lru_cache

import repcode as rc

H, L, DET_IDS, FAULT_IDS = rc.build_linear_model()
NF = len(FAULT_IDS)          # 30
ND = len(DET_IDS)            # 14
FIDX = {f: i for i, f in enumerate(FAULT_IDS)}
DIDX = {d: i for i, d in enumerate(DET_IDS)}

P_D = 1e-3
P_M = 1e-3
EPS = 1e-12                  # strictness threshold on normalised |P0-P1|

# ---- base linear algebra over GF(2) -----------------------------------------

# A: ND x NF detector-by-fault incidence matrix.
A = np.zeros((ND, NF), dtype=np.uint8)
for f in FAULT_IDS:
    for d in H[f]:
        A[DIDX[d], FIDX[f]] = 1

LVEC = np.array([L[f] for f in FAULT_IDS], dtype=np.uint8)      # logical functional


def base_weight(f):
    return P_D if f[0] == 'd' else P_M


def _gf2_reduce(mat):
    """Return (rref, pivots) for a copy of mat over GF(2)."""
    m = mat.copy().astype(np.uint8)
    rows, cols = m.shape
    pivots = []
    r = 0
    for c in range(cols):
        sel = -1
        for rr in range(r, rows):
            if m[rr, c]:
                sel = rr
                break
        if sel < 0:
            continue
        m[[r, sel]] = m[[sel, r]]
        for rr in range(rows):
            if rr != r and m[rr, c]:
                m[rr, :] ^= m[r, :]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return m, pivots


# Null-space basis of A (16 x NF) and a particular-solution operator.
def _nullspace_and_solver(Amat):
    rows, cols = Amat.shape
    # Augment to track solution operator: reduce [A | I_rows]
    aug = np.concatenate([Amat.copy(), np.eye(rows, dtype=np.uint8)], axis=1)
    m, pivots = _gf2_reduce(aug)
    R = m[:, :cols]
    Tmat = m[:, cols:]          # R = Tmat @ A  (row operations)
    pivset = [p for p in pivots if p < cols]
    free = [c for c in range(cols) if c not in pivset]
    # Null basis: for each free col, set it 1, solve pivots.
    basis = []
    for fcol in free:
        vec = np.zeros(cols, dtype=np.uint8)
        vec[fcol] = 1
        for i, pc in enumerate(pivset):
            # pivot row i expresses pivot var = sum over free of R[i,free]
            vec[pc] = R[i, fcol]
        basis.append(vec)
    N = np.array(basis, dtype=np.uint8) if basis else np.zeros((0, cols), np.uint8)
    # Verify A N^T = 0
    assert np.all((Amat @ N.T) % 2 == 0)

    def particular(bvec):
        # In reduced system R x = Tmat b ; pivots carry the solution.
        rhs = (Tmat @ bvec) % 2
        x = np.zeros(cols, dtype=np.uint8)
        for i, pc in enumerate(pivset):
            x[pc] = rhs[i]
        # unsatisfiable check: rows beyond rank must be zero in rhs
        assert np.all((Amat @ x) % 2 == bvec % 2), "syndrome not in column span"
        return x

    return N, particular


NULL, _particular = _nullspace_and_solver(A)
NULLDIM = NULL.shape[0]                                   # 16

# Enumerate the whole null space ONCE: M is (2**NULLDIM) x NF, fixed forever.
_Z = ((np.arange(1 << NULLDIM, dtype=np.uint32)[:, None] >>
       np.arange(NULLDIM, dtype=np.uint32)[None, :]) & 1).astype(np.uint8)   # 65536 x 16
M = (_Z @ NULL) % 2                                        # 65536 x NF, fixed
M_LPAR = (M @ LVEC) % 2                                    # 65536, fixed logical parity of M rows


def _syndrome_vec(detset):
    b = np.zeros(ND, dtype=np.uint8)
    for d in detset:
        b[DIDX[d]] = 1
    return b


@lru_cache(maxsize=None)
def _marginal_cached(syndrome_key, free_key):
    """Exact (P0, P1) for full-history marginalisation. Memoised.

    syndrome_key: bytes of the 14-bit syndrome.
    free_key: frozenset of fault ids treated as free (weight 1/2).
    """
    b = np.frombuffer(syndrome_key, dtype=np.uint8).copy()
    free = set(free_key)
    # weights -> log-likelihood ratios llr_f = log(w/(1-w)); free faults llr=0.
    llr = np.zeros(NF)
    for i, f in enumerate(FAULT_IDS):
        if f in free:
            llr[i] = 0.0
        else:
            w = base_weight(f)
            llr[i] = np.log(w / (1.0 - w))
    e0 = _particular(b)                                     # NF
    E = M ^ e0[None, :]                                     # 65536 x NF
    logw = E @ llr                                          # 65536
    lpar = M_LPAR ^ (int(e0 @ LVEC) % 2)                   # 65536 logical parity
    mx = logw.max()
    w = np.exp(logw - mx)
    P0 = float(w[lpar == 0].sum())
    P1 = float(w[lpar == 1].sum())
    s = P0 + P1
    return P0 / s, P1 / s


@lru_cache(maxsize=None)
def _free_tables(free_key):
    """Per-free-set precompute: (const, llr, base = M@llr). base is the 65536
    log-weight contribution shared by every syndrome with this free-set."""
    free = set(free_key)
    llr = np.zeros(NF)
    const = 0.0
    for i, f in enumerate(FAULT_IDS):
        w = 0.5 if f in free else base_weight(f)
        const += np.log(1.0 - w)
        llr[i] = 0.0 if f in free else np.log(w / (1.0 - w))
    base = M @ llr                                         # 65536, fixed per free-set
    return const, llr, base


@lru_cache(maxsize=None)
def _marginal_unnorm(syndrome_key, free_key):
    """Exact UNNORMALISED (P0, P1) on a consistent ABSOLUTE scale. Memoised.

    Absolute probability sums (no per-syndrome max subtraction), so results for
    different syndromes or free-sets can be ADDED -- needed for the onset mixture
    and the restorer's sum over discarded completions. Uses the identity
    (M ^ e0) @ llr = base + e0dot - 2 * M[:, e0] @ llr[e0] to avoid a full
    65536 x NF pass per syndrome.
    """
    b = np.frombuffer(syndrome_key, dtype=np.uint8).copy()
    const, llr, base = _free_tables(free_key)
    e0 = _particular(b)
    e0idx = np.nonzero(e0)[0]
    if e0idx.size:
        corr = float(llr[e0idx].sum()) - 2.0 * (M[:, e0idx] @ llr[e0idx])
    else:
        corr = 0.0
    logw = const + base + corr
    lpar = M_LPAR ^ (int(e0 @ LVEC) % 2)
    w = np.exp(logw)
    return float(w[lpar == 0].sum()), float(w[lpar == 1].sum())


# Named onset models (Astra's reconciliation):
#   FREE_BOTH : both located faults ('d',1,1),('d',1,2) freed simultaneously
#               (an independent-erasure region; what Stage 0 actually computed).
#   ONSET_AVG : exactly one onset s in O, uniform prior, marginalised -- only
#               ('d',1,s) freed per term (what the prose described).
FREE_BOTH = 'free_both'
ONSET_AVG = 'onset_avg'


def reference_marginal(detset, flagged, onset_model=FREE_BOTH):
    """Absolute-scale (P0, P1) for the full-history reference under a named model."""
    key = _syndrome_vec(detset).tobytes()
    if not flagged:
        return _marginal_unnorm(key, frozenset())
    if onset_model == FREE_BOTH:
        return _marginal_unnorm(key, frozenset(('d', rc.LOSS_SITE, s) for s in rc.O))
    if onset_model == ONSET_AVG:
        acc0 = acc1 = 0.0
        for s in rc.O:
            p0, p1 = _marginal_unnorm(key, frozenset([('d', rc.LOSS_SITE, s)]))
            acc0 += p0 / len(rc.O)
            acc1 += p1 / len(rc.O)
        return acc0, acc1
    raise ValueError(onset_model)


def reference_predict(detset, flagged, onset_model=FREE_BOTH):
    """Full-history soft decoder. Returns (pred, p0_norm, p1_norm, strict).

    onset_model defaults to FREE_BOTH, reproducing Stage 0 exactly.
    """
    p0, p1 = reference_marginal(detset, flagged, onset_model)
    s = p0 + p1
    p0n, p1n = p0 / s, p1 / s
    pred = 0 if p0n >= p1n else 1
    strict = abs(p0n - p1n) > EPS
    return pred, p0n, p1n, strict


# ---- streaming (sliding-window hard committer) ------------------------------

# Fault partitions by round.
EARLY_FAULTS = [f for f in FAULT_IDS if f[2] <= rc.CUT]          # rounds 0..2
LATE_FAULTS = [f for f in FAULT_IDS if f[2] > rc.CUT]            # rounds 3..5
# Detectors in the committed core: (c,0),(c,1),(c,2) -- functions of early faults only.
CORE_DETS = [(c, t) for c in range(len(rc.CHECKS)) for t in range(rc.COMMIT_C)]
# Live detectors used by the live decode: (c,3),(c,4),(c,5),(c,'f').
LIVE_DETS = ([(c, t) for c in range(len(rc.CHECKS)) for t in range(rc.COMMIT_C, rc.T)]
             + [(c, 'f') for c in range(len(rc.CHECKS))])


def _enumerate_block(block_faults, block_dets, detset, free=frozenset()):
    """Exact MAP over a block. Return (frame-like d0-parity, min_weight, configs...).

    Solve (restricted A) e = b over the block's faults and detectors, enumerate
    the block null space, pick MAP (max weight == min cost); tie-break: smallest
    total weight, then lexicographic by fault index. Returns the MAP config's
    logical (d0) parity, and the exact (w0, w1) block likelihoods split by d0.
    """
    fidx = [FIDX[f] for f in block_faults]
    didx = [DIDX[d] for d in block_dets]
    Ab = A[np.ix_(didx, fidx)]                              # |dets| x |faults|
    bvec = np.array([1 if (DET_IDS[i] in detset) else 0 for i in didx], dtype=np.uint8)
    Nb, particular = _nullspace_and_solver(Ab)
    nd = Nb.shape[0]
    # logical (d0) functional restricted to block faults
    lvec = np.array([L[f] for f in block_faults], dtype=np.uint8)
    # weights
    llr = np.zeros(len(block_faults))
    cost1 = np.zeros(len(block_faults))                     # 'cost' = -log weight contribution
    for i, f in enumerate(block_faults):
        if f in free:
            llr[i] = 0.0
        else:
            w = base_weight(f)
            llr[i] = np.log(w / (1.0 - w))
    e0 = particular(bvec)
    Zb = ((np.arange(1 << nd, dtype=np.uint64)[:, None] >>
           np.arange(nd, dtype=np.uint64)[None, :]) & 1).astype(np.uint8) if nd else \
        np.zeros((1, 0), np.uint8)
    Mb = (Zb @ Nb) % 2 if nd else np.zeros((1, len(block_faults)), np.uint8)
    E = Mb ^ e0[None, :]
    logw = E @ llr
    lpar = (E @ lvec) % 2
    mx = logw.max()
    wexp = np.exp(logw - mx)
    w0 = float(wexp[lpar == 0].sum())
    w1 = float(wexp[lpar == 1].sum())
    # MAP config (max weight); tie-break lexicographic by fault index among argmax
    order = np.lexsort(np.rot90(E))                         # lexicographic on rows
    best = None
    bestlogw = -np.inf
    for idx in range(E.shape[0]):
        if logw[idx] > bestlogw + 1e-15:
            bestlogw = logw[idx]
            best = idx
    # collect all argmax, choose lexicographically smallest fault support
    argmax = [i for i in range(E.shape[0]) if logw[i] > bestlogw - 1e-9]
    argmax.sort(key=lambda i: tuple(int(x) for x in E[i]))
    map_row = E[argmax[0]]
    map_d0 = int((map_row @ lvec) % 2)
    return map_d0, w0, w1


def m2_boundary(detset):
    """Raw measured m_c(2) carried across the cut = det(c,0)^det(c,1)^det(c,2)."""
    out = []
    for c in range(len(rc.CHECKS)):
        v = 0
        for t in range(rc.COMMIT_C):
            if (c, t) in detset:
                v ^= 1
        out.append(v)
    return tuple(out)


def streaming_commit(detset):
    """Commit the core [0..2]: MAP over early faults -> frame_bit (committed d0)."""
    frame_bit, _, _ = _enumerate_block(EARLY_FAULTS, CORE_DETS, detset)
    return frame_bit


def streaming_commit_erasure(detset):
    """Commit the core with the located loss faults freed (weight 1/2).

    This is what a decoder that still HOLDS the core detectors at report time can
    do: re-explain the committed region under the erasure the report licenses.
    Used by the prompt-flag, loss-aware, and wide-window controls -- each of which,
    by construction, retains the core at the moment of decision.
    """
    free = frozenset(('d', rc.LOSS_SITE, s) for s in rc.O)
    frame_bit, _, _ = _enumerate_block(EARLY_FAULTS, CORE_DETS, detset, free=free)
    return frame_bit


def streaming_live(detset):
    """Live decode [3..5]+closers -> live d0 contribution, given carried boundary.

    The live detectors as the streaming decoder sees them already incorporate the
    carried m_c(2) (detector (c,3) = m_c(3) ^ m_c(2)), which is exactly det(c,3)
    in the full record. So decoding over the full LIVE_DETS values is correct.
    """
    live_bit, _, _ = _enumerate_block(LATE_FAULTS, LIVE_DETS, detset)
    return live_bit


def serialized_state(detset):
    """Complete forward-relevant streaming state after committing [0..2], reading r3.

    (frame_bit, boundary m_c(2) per check, live round-3 detectors per check).
    Pending metadata (the report) is attached at flag time, not here.
    """
    frame = streaming_commit(detset)
    m2 = m2_boundary(detset)
    d3 = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in range(len(rc.CHECKS)))
    return {'frame': frame, 'm2': m2, 'd3': d3}


def post_cut_inputs(detset):
    """Inputs arriving after the cut: rounds 4,5 and closing detectors."""
    later = []
    for c in range(len(rc.CHECKS)):
        for t in range(rc.COMMIT_C + rc.BUFFER_B, rc.T):      # rounds 4,5
            later.append(((c, t), 1 if (c, t) in detset else 0))
    for c in range(len(rc.CHECKS)):
        later.append(((c, 'f'), 1 if (c, 'f') in detset else 0))
    return tuple(later)


def streaming_predict(detset):
    """Pre-flag streaming prediction = frame_bit ^ live_bit."""
    return streaming_commit(detset) ^ streaming_live(detset)


def streaming_predict_from_snapshot(state, post_inputs):
    """Reconstruct the streaming prediction from the SNAPSHOT ALONE.

    Rebuilds the live detector set from (boundary + round-3 buffer + post-cut
    inputs), re-runs the live decode, and XORs the committed frame. Confirms the
    snapshot is a complete forward-relevant state.
    """
    live_detset = set()
    # round 3 buffer
    for c in range(len(rc.CHECKS)):
        if state['d3'][c]:
            live_detset.add((c, rc.COMMIT_C))
    for det_id, v in post_inputs:
        if v:
            live_detset.add(det_id)
    live_bit, _, _ = _enumerate_block(LATE_FAULTS, LIVE_DETS, live_detset)
    return state['frame'] ^ live_bit


def streaming_revision(detset, flagged):
    """Post-flag streaming prediction under the frozen cross-cutoff rule.

    The report frees ('d',1,1),('d',1,2), which are EARLY faults in the pruned
    core. The frozen rule applies erasure only to LIVE edges; the early erasure
    has none, so the committed frame and the live decode are unchanged.
    """
    if not flagged:
        return streaming_predict(detset)
    # erasure touches only early faults -> no live edges -> prediction unchanged
    return streaming_predict(detset)


def restoration_bit(detset):
    """Frozen restoration bit b = det(c0,1) ^ det(c1,1): the round-1 d1-leg parity
    of the pruned core syndrome (the bit the earliest-onset erasure consumes)."""
    b = 0
    for c in range(len(rc.CHECKS)):
        if (c, 1) in detset:
            b ^= 1
    return b


def streaming_revision_restored(detset, delta):
    """Restored streaming post-flag prediction = frame ^ live ^ delta(b).

    delta: a callable b -> {0,1} (the frozen correction derived from the one bit).
    """
    b = restoration_bit(detset)
    return streaming_predict(detset) ^ delta(b)


if __name__ == '__main__':
    # sanity: fault-free -> clean, predicts 0 strictly
    empty = rc.detectors_of([], H)
    print("null dim:", NULLDIM, "M shape:", M.shape)
    print("ref empty:", reference_predict(empty, False))
    # single d0 error
    d = rc.detectors_of([('d', 0, 4)], H)
    print("ref d0@4 preflag:", reference_predict(d, False))
    print("stream d0@4:", streaming_predict(d))
    # snapshot round-trip on a mid history
    hist = [('d', 0, 1), ('d', 1, 2), ('m', 0, 4)]
    ds = rc.detectors_of(hist, H)
    st = serialized_state(ds)
    pc = post_cut_inputs(ds)
    cont = streaming_predict(ds)
    snap = streaming_predict_from_snapshot(st, pc)
    print("snapshot round-trip:", cont, snap, "OK" if cont == snap else "MISMATCH")
