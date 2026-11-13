"""Stage 2, Component 2: does the diamond query recover the same-deadline decision?

Frozen by PREREGISTRATION_2D.md Amendment A (commit d22dbe9). d=3 rotated surface
code, bulk loss at (1,1). Two decoupled-except-through-onset sectors:
  X-sector: X-errors on data, seen by Z-stabs {0,2,5,7}, flip the scored logical Z_L.
  Z-sector: Z-errors on data, seen by X-stabs {1,3,4,6}, flip X_L (informs onset only).

Exact bounded-weight marginal per sector; onset-averaged two-sector decision routine
shared by all arms. This file = foundation + self-checks; decoders/arms/run below.
"""

import itertools
import numpy as np

import stage2_retention_accounting as geo

D = 3
T = 5                                  # rounds 0..4 (deadline round 4; no readout/round5)
DATA, STABS, STAR = geo.build_code(D)
NDATA = len(DATA)
DIDX = {q: i for i, q in enumerate(DATA)}
XSTABS = [k for k, s in enumerate(STABS) if s['type'] == 'X']     # {1,3,4,6}
ZSTABS = [k for k, s in enumerate(STABS) if s['type'] == 'Z']     # {0,2,5,7}
LOSS_SITE = (1, 1)
ONSET = (1, 2)
COMMIT_CUT = 3                          # commit rounds 0,1,2 ; live 3,4
REPORT_ROUND = 4
P = 1e-3
EPS = 1e-12


# ---------- GF(2) linear algebra ----------
def _rref(mat):
    m = [row[:] for row in mat]
    rows = len(m)
    cols = len(m[0]) if rows else 0
    piv = []
    r = 0
    for c in range(cols):
        sel = next((i for i in range(r, rows) if m[i][c]), None)
        if sel is None:
            continue
        m[r], m[sel] = m[sel], m[r]
        for i in range(rows):
            if i != r and m[i][c]:
                m[i] = [a ^ b for a, b in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == rows:
            break
    return m[:r], piv


def _nullspace(mat, ncols):
    if not mat:
        return [[1 if i == j else 0 for i in range(ncols)] for j in range(ncols)]
    rr, piv = _rref(mat)
    pivset = set(piv)
    free = [c for c in range(ncols) if c not in pivset]
    basis = []
    for f in free:
        v = [0] * ncols
        v[f] = 1
        for i, pc in enumerate(piv):
            v[pc] = rr[i][f]
        basis.append(v)
    return basis


def _in_rowspace(vec, mat):
    test = [row[:] for row in mat] + [vec[:]]
    r1 = len(_rref([row[:] for row in mat])[0])
    r2 = len(_rref(test)[0])
    return r2 == r1


def _dot(a, b):
    return sum(x & y for x, y in zip(a, b)) % 2


# ---------- derive the logical operators ----------
def _support_matrix(stab_ids):
    M = []
    for k in stab_ids:
        row = [0] * NDATA
        for q in STABS[k]['support']:
            row[DIDX[q]] = 1
        M.append(row)
    return M


HZ = _support_matrix(ZSTABS)      # Z-stab incidence (X-error detection)
HX = _support_matrix(XSTABS)      # X-stab incidence (Z-error detection)


def _pick_logical(ker_mat, rowspace_mat):
    """A vector in ker(ker_mat) but not in rowspace(rowspace_mat)."""
    for v in _nullspace(ker_mat, NDATA):
        if not _in_rowspace(v, rowspace_mat):
            return v
    raise RuntimeError("no logical found")


LZ = _pick_logical(HX, HZ)        # Z_L support: commutes with X-stabs, nontrivial
XL = _pick_logical(HZ, HX)        # X_L support: commutes with Z-stabs, nontrivial
assert _dot(LZ, XL) == 1, "Z_L and X_L must anticommute"


# ---------- exact simulator ----------
def simulate(xf, zf, mzf, mxf):
    """xf/zf: sets of (q, t) data X/Z faults. mzf/mxf: sets of (k, t) measurement
    faults on Z/X stabs. Returns (DZ, DX, zl_flip, xl_flip).
    DZ[k][t], DX[k][t] detectors (rounds 0..T-1). zl_flip = Z_L flip (from X-errors)."""
    cumx = np.zeros((NDATA, T), dtype=np.uint8)
    cumz = np.zeros((NDATA, T), dtype=np.uint8)
    for (q, t) in xf:
        cumx[DIDX[q], t:] ^= 1
    for (q, t) in zf:
        cumz[DIDX[q], t:] ^= 1
    DZ, DX = {}, {}
    for k in ZSTABS:
        prev = 0
        for t in range(T):
            s = 0
            for q in STABS[k]['support']:
                s ^= int(cumx[DIDX[q], t])
            if (k, t) in mzf:
                s ^= 1
            DZ[(k, t)] = s ^ prev
            prev = s
    for k in XSTABS:
        prev = 0
        for t in range(T):
            s = 0
            for q in STABS[k]['support']:
                s ^= int(cumz[DIDX[q], t])
            if (k, t) in mxf:
                s ^= 1
            DX[(k, t)] = s ^ prev
            prev = s
    zl = sum(int(cumx[i, T - 1]) for i in range(NDATA) if LZ[i]) % 2
    xl = sum(int(cumz[i, T - 1]) for i in range(NDATA) if XL[i]) % 2
    return DZ, DX, zl, xl


# ---------- self-checks ----------
def _self_check():
    # fault-free -> clean, no logical
    DZ, DX, zl, xl = simulate(set(), set(), set(), set())
    assert all(v == 0 for v in DZ.values()) and all(v == 0 for v in DX.values())
    assert zl == 0 and xl == 0
    # a single data-X error flips its Z-stabs' detectors at that round, and Z_L iff
    # the qubit is in LZ support
    for q in DATA:
        DZ, DX, zl, xl = simulate({(q, 2)}, set(), set(), set())
        fired = {k for (k, t), v in DZ.items() if v}
        exp = {k for k in ZSTABS if q in STABS[k]['support']}
        assert fired == exp, (q, fired, exp)
        assert zl == (1 if LZ[DIDX[q]] else 0)
        assert all(v == 0 for v in DX.values())      # X-errors don't touch X-stabs
    # linearity: random fault sets compose by XOR
    rng = np.random.default_rng(1)
    allxf = [(q, t) for q in DATA for t in range(T)]
    allmz = [(k, t) for k in ZSTABS for t in range(T)]
    for _ in range(300):
        xs = {allxf[i] for i in rng.choice(len(allxf), 3, replace=False)}
        ms = {allmz[i] for i in rng.choice(len(allmz), 2, replace=False)}
        DZ, _, zl, _ = simulate(xs, set(), ms, set())
        # compose from singles
        comp = {}
        zlc = 0
        for f in xs:
            d, _, z, _ = simulate({f}, set(), set(), set())
            for key, v in d.items():
                comp[key] = comp.get(key, 0) ^ v
            zlc ^= z
        for f in ms:
            d, _, _, _ = simulate(set(), set(), {f}, set())
            for key, v in d.items():
                comp[key] = comp.get(key, 0) ^ v
        assert all(DZ[key] == comp.get(key, 0) for key in DZ), "X-sector nonlinear?"
        assert zl == zlc
    print("self-check OK")
    print(f"  data={NDATA} Xstabs={XSTABS} Zstabs={ZSTABS}")
    print(f"  Z_L support (LZ): {[DATA[i] for i in range(NDATA) if LZ[i]]}")
    print(f"  X_L support (XL): {[DATA[i] for i in range(NDATA) if XL[i]]}")
    print(f"  loss site {LOSS_SITE} star stabs {STAR[LOSS_SITE]} "
          f"types {[STABS[k]['type'] for k in STAR[LOSS_SITE]]}")


# ---------- per-sector exact bounded-weight marginal ----------
W_DEC = 3

# sector detector positions (ordered) and stab list
ZDETS = [(k, t) for k in ZSTABS for t in range(T)]     # X-sector detectors
XDETS = [(k, t) for k in XSTABS for t in range(T)]     # Z-sector detectors


def _unit_sig(sector, fault):
    """Detector signature, logical bit, round-2 boundary syndrome of a single fault."""
    if sector == 'X':
        q_or_k, t = fault[1], fault[2]
        if fault[0] == 'X':
            DZ, _, zl, _ = simulate({(q_or_k, t)}, set(), set(), set())
        else:
            DZ, _, zl, _ = simulate(set(), set(), {(q_or_k, t)}, set())
        sig = np.array([DZ[d] for d in ZDETS], dtype=np.uint8)
        bnd = np.array([DZ[(k, 0)] ^ DZ[(k, 1)] ^ DZ[(k, 2)] for k in ZSTABS], dtype=np.uint8)
        return sig, zl, bnd
    else:
        q_or_k, t = fault[1], fault[2]
        if fault[0] == 'Z':
            _, DX, _, xl = simulate(set(), {(q_or_k, t)}, set(), set())
        else:
            _, DX, _, xl = simulate(set(), set(), set(), {(q_or_k, t)})
        sig = np.array([DX[d] for d in XDETS], dtype=np.uint8)
        bnd = np.array([DX[(k, 0)] ^ DX[(k, 1)] ^ DX[(k, 2)] for k in XSTABS], dtype=np.uint8)
        return sig, xl, bnd


def _sector_faults(sector):
    if sector == 'X':
        return ([('X', q, t) for q in DATA for t in range(T)] +
                [('MZ', k, t) for k in ZSTABS for t in range(T)])
    return ([('Z', q, t) for q in DATA for t in range(T)] +
            [('MX', k, t) for k in XSTABS for t in range(T)])


def _build_tables(sector):
    faults = _sector_faults(sector)
    usig = {f: _unit_sig(sector, f) for f in faults}
    ndet = len(ZDETS if sector == 'X' else XDETS)
    nst = len(ZSTABS if sector == 'X' else XSTABS)
    sigs, logs, bnds, pri = [], [], [], []
    for w in range(0, W_DEC + 1):
        for combo in itertools.combinations(faults, w):
            s = np.zeros(ndet, dtype=np.uint8)
            b = np.zeros(nst, dtype=np.uint8)
            lg = 0
            for f in combo:
                us, ul, ub = usig[f]
                s ^= us
                b ^= ub
                lg ^= ul
            sigs.append(s)
            bnds.append(b)
            logs.append(lg)
            pri.append(P ** w)
    return {'SIG': np.array(sigs), 'BND': np.array(bnds),
            'LOG': np.array(logs, dtype=np.uint8), 'PRI': np.array(pri),
            'faults': faults, 'ndet': ndet, 'nst': nst}


_TAB = {}


def _tab(sector):
    if sector not in _TAB:
        _TAB[sector] = _build_tables(sector)
    return _TAB[sector]


def _erasure_sig(sector, onset):
    f = ('X', LOSS_SITE, onset) if sector == 'X' else ('Z', LOSS_SITE, onset)
    return _unit_sig(sector, f)


_MARG = {}


def sector_marginal_cached(sector, cond_dets, cond_bnd, onset, split):
    key = (sector, tuple(sorted(cond_dets.items())), tuple(sorted(cond_bnd.items())),
           onset, split)
    if key not in _MARG:
        _MARG[key] = sector_marginal(sector, cond_dets, cond_bnd, onset, split)
    return _MARG[key]


def sector_marginal(sector, cond_dets, cond_bnd, onset, split):
    """Exact marginal over weight<=W_DEC configs + the free erasure at `onset`.

    cond_dets: dict detpos->val (positions the arm conditions on).
    cond_bnd: dict stab->val (round-2 boundary; {} if not carried).
    Returns (w0, w1) if split else total weight."""
    tab = _tab(sector)
    SIG, BND, LOG, PRI = tab['SIG'], tab['BND'], tab['LOG'], tab['PRI']
    dets = ZDETS if sector == 'X' else XDETS
    stabs = ZSTABS if sector == 'X' else XSTABS
    didx = {d: i for i, d in enumerate(dets)}
    sidx = {k: i for i, k in enumerate(stabs)}
    esig, elog, ebnd = _erasure_sig(sector, onset)
    w0 = w1 = 0.0
    for e in (0, 1):                      # free erasure fault absent / present (weight 0.5 each)
        sig = SIG ^ (esig if e else 0)
        bnd = BND ^ (ebnd if e else 0)
        log = LOG ^ (elog if e else 0)
        mask = np.ones(len(PRI), dtype=bool)
        for d, v in cond_dets.items():
            mask &= (sig[:, didx[d]] == v)
        for k, v in cond_bnd.items():
            mask &= (bnd[:, sidx[k]] == v)
        pr = PRI[mask] * 0.5
        lg = log[mask]
        w0 += float(pr[lg == 0].sum())
        w1 += float(pr[lg == 1].sum())
    return (w0, w1) if split else (w0 + w1)


def decide(availZ, availX, bndZ, bndX):
    """Onset-averaged two-sector decision. availZ/availX: dict detpos->val the arm sees
    for Z-stabs / X-stabs; bndZ/bndX: carried round-2 boundary. Returns (zl_hat,P0,P1)."""
    P0 = P1 = 0.0
    for s in ONSET:
        q0, q1 = sector_marginal_cached('X', availZ, bndZ, s, True)
        r = sector_marginal_cached('Z', availX, bndX, s, False)
        P0 += r * q0
        P1 += r * q1
    tot = P0 + P1
    return (0 if P0 >= P1 else 1), P0 / tot if tot else 0.5, P1 / tot if tot else 0.5


# ---------- the four arms: which detectors each conditions on ----------
STAR_Z = [k for k in STAR[LOSS_SITE] if k in ZSTABS]    # {2,5}
STAR_X = [k for k in STAR[LOSS_SITE] if k in XSTABS]    # {1,6}
LIVE = [3, 4]
DIAMOND_ROUNDS = list(ONSET)                            # {1,2}


def arm_evidence(DZ, DX, arm):
    """Return (availZ, availX, bndZ, bndX) for an arm from the full actual record."""
    bndZ = {k: DZ[(k, 0)] ^ DZ[(k, 1)] ^ DZ[(k, 2)] for k in ZSTABS}
    bndX = {k: DX[(k, 0)] ^ DX[(k, 1)] ^ DX[(k, 2)] for k in XSTABS}
    if arm in ('thick', 'whole'):
        az = {(k, t): DZ[(k, t)] for k in ZSTABS for t in range(T)}
        ax = {(k, t): DX[(k, t)] for k in XSTABS for t in range(T)}
        return az, ax, {}, {}                 # full record implies boundary
    # thin arms: live rounds + carried boundary
    az = {(k, t): DZ[(k, t)] for k in ZSTABS for t in LIVE}
    ax = {(k, t): DX[(k, t)] for k in XSTABS for t in LIVE}
    if arm == 'diamond':
        for k in STAR_Z:
            for t in DIAMOND_ROUNDS:
                az[(k, t)] = DZ[(k, t)]
        for k in STAR_X:
            for t in DIAMOND_ROUNDS:
                ax[(k, t)] = DX[(k, t)]
    return az, ax, bndZ, bndX


ARMS = ['thick', 'thin', 'diamond', 'whole']


def decode_arm(DZ, DX, arm):
    az, ax, bz, bx = arm_evidence(DZ, DX, arm)
    return decide(az, ax, bz, bx)


if __name__ == '__main__':
    _self_check()
    # decoder sanity: fault-free -> 0; a logical-X chain on LZ support -> predicts 1
    DZ, DX, zl, xl = simulate(set(), set(), set(), set())
    print("decode fault-free thick:", decode_arm(DZ, DX, 'thick')[0], "(expect 0)")
    chain = {(q, 2) for q in [(0, 0), (1, 0), (2, 0)]}     # = LZ support (a logical X)
    DZ, DX, zl, xl = simulate(chain, set(), set(), set())
    print("logical-X chain: truth zl =", zl, " thick decode =", decode_arm(DZ, DX, 'thick')[0])

