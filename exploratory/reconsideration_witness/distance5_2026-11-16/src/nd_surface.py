"""General-distance rotated surface code: geometry, logicals, simulator, sector tables.

Parameterized port of stage2_surface.py (which is hard-wired to d=3). A Surface(d)
object exposes exactly the pieces the tractable decoder needs, for any odd d. Validated
at d=3 to reproduce stage2_surface's data/stabs/logicals/detectors/simulate bit-for-bit.
"""
import itertools
import numpy as np
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import stage2_retention_accounting as geo    # build_code(d) geometry


def _rref(mat):
    m = [row[:] for row in mat]
    rows = len(m); cols = len(m[0]) if rows else 0; piv = []; r = 0
    for c in range(cols):
        sel = next((i for i in range(r, rows) if m[i][c]), None)
        if sel is None:
            continue
        m[r], m[sel] = m[sel], m[r]
        for i in range(rows):
            if i != r and m[i][c]:
                m[i] = [a ^ b for a, b in zip(m[i], m[r])]
        piv.append(c); r += 1
        if r == rows:
            break
    return m[:r], piv


def _nullspace(mat, nd):
    if not mat:
        return [[1 if i == j else 0 for i in range(nd)] for j in range(nd)]
    rr, piv = _rref(mat); ps = set(piv); free = [c for c in range(nd) if c not in ps]; B = []
    for f in free:
        v = [0] * nd; v[f] = 1
        for i, pc in enumerate(piv):
            v[pc] = rr[i][f]
        B.append(v)
    return B


def _in_rowspace(vec, mat):
    r1 = len(_rref([row[:] for row in mat])[0])
    r2 = len(_rref([row[:] for row in mat] + [vec[:]])[0])
    return r2 == r1


class Surface:
    def __init__(self, d, T=5, p=1e-3):
        self.d = d; self.T = T; self.P = p
        self.DATA, self.STABS, self.STAR = geo.build_code(d)
        self.NDATA = len(self.DATA)
        self.DIDX = {q: i for i, q in enumerate(self.DATA)}
        self.XSTABS = [k for k, s in enumerate(self.STABS) if s['type'] == 'X']
        self.ZSTABS = [k for k, s in enumerate(self.STABS) if s['type'] == 'Z']
        self.NSTAB = len(self.STABS)
        self.ZDETS = [(k, t) for k in self.ZSTABS for t in range(T)]   # X-sector detectors
        self.XDETS = [(k, t) for k in self.XSTABS for t in range(T)]   # Z-sector detectors
        self.LZ, self.XL = self._logicals()
        assert self._dot(self.LZ, self.XL) == 1

    def _support_matrix(self, ids):
        M = []
        for k in ids:
            row = [0] * self.NDATA
            for q in self.STABS[k]['support']:
                row[self.DIDX[q]] = 1
            M.append(row)
        return M

    @staticmethod
    def _dot(a, b):
        return sum(x & y for x, y in zip(a, b)) % 2

    def _logicals(self):
        HZ = self._support_matrix(self.ZSTABS); HX = self._support_matrix(self.XSTABS)

        def pick(ker, row):
            for v in _nullspace(ker, self.NDATA):
                if not _in_rowspace(v, row):
                    return v
            raise RuntimeError('no logical')
        return pick(HX, HZ), pick(HZ, HX)        # Z_L support, X_L support

    def simulate(self, xf, zf, mzf, mxf):
        T, ND = self.T, self.NDATA
        cumx = np.zeros((ND, T), dtype=np.uint8); cumz = np.zeros((ND, T), dtype=np.uint8)
        for (q, t) in xf:
            cumx[self.DIDX[q], t:] ^= 1
        for (q, t) in zf:
            cumz[self.DIDX[q], t:] ^= 1
        DZ, DX = {}, {}
        for k in self.ZSTABS:
            prev = 0
            for t in range(T):
                s = 0
                for q in self.STABS[k]['support']:
                    s ^= int(cumx[self.DIDX[q], t])
                if (k, t) in mzf:
                    s ^= 1
                DZ[(k, t)] = s ^ prev; prev = s
        for k in self.XSTABS:
            prev = 0
            for t in range(T):
                s = 0
                for q in self.STABS[k]['support']:
                    s ^= int(cumz[self.DIDX[q], t])
                if (k, t) in mxf:
                    s ^= 1
                DX[(k, t)] = s ^ prev; prev = s
        zl = sum(int(cumx[i, T - 1]) for i in range(ND) if self.LZ[i]) % 2
        xl = sum(int(cumz[i, T - 1]) for i in range(ND) if self.XL[i]) % 2
        return DZ, DX, zl, xl

    def sector_faults(self, sector):
        if sector == 'X':
            return ([('X', q, t) for q in self.DATA for t in range(self.T)] +
                    [('MZ', k, t) for k in self.ZSTABS for t in range(self.T)])
        return ([('Z', q, t) for q in self.DATA for t in range(self.T)] +
                [('MX', k, t) for k in self.XSTABS for t in range(self.T)])

    def positions(self, sector):
        return self.ZDETS if sector == 'X' else self.XDETS

    def stabs(self, sector):
        return self.ZSTABS if sector == 'X' else self.XSTABS

    @lru_cache(None)
    def unit_sig(self, sector, fault):
        q_or_k, t = fault[1], fault[2]
        if fault[0] in ('X', 'Z'):
            if sector == 'X':
                DZ, _, zl, _ = self.simulate({(q_or_k, t)}, set(), set(), set())
            else:
                _, DX, _, xl = self.simulate(set(), {(q_or_k, t)}, set(), set())
        else:
            if sector == 'X':
                DZ, _, zl, _ = self.simulate(set(), set(), {(q_or_k, t)}, set())
            else:
                _, DX, _, xl = self.simulate(set(), set(), set(), {(q_or_k, t)})
        dets = self.positions(sector); stabs = self.stabs(sector)
        D = DZ if sector == 'X' else DX
        logical = zl if sector == 'X' else xl
        sig = np.array([D[dd] for dd in dets], dtype=np.uint8)
        bnd = np.array([D[(k, 0)] ^ D[(k, 1)] ^ D[(k, 2)] for k in stabs], dtype=np.uint8)
        return sig, int(logical), bnd

    @lru_cache(None)
    def build_tables(self, sector, w_dec):
        faults = self.sector_faults(sector)
        usig = {f: self.unit_sig(sector, f) for f in faults}
        ndet = len(self.positions(sector)); nst = len(self.stabs(sector))
        sigs, logs, bnds, pri = [], [], [], []
        for w in range(w_dec + 1):
            for combo in itertools.combinations(faults, w):
                s = np.zeros(ndet, dtype=np.uint8); b = np.zeros(nst, dtype=np.uint8); lg = 0
                for f in combo:
                    us, ul, ub = usig[f]
                    s ^= us; b ^= ub; lg ^= ul
                sigs.append(s); bnds.append(b); logs.append(lg); pri.append(w)
        return dict(SIG=np.array(sigs), BND=np.array(bnds),
                    LOG=np.array(logs, dtype=np.uint8), W=np.array(pri, dtype=np.int8),
                    faults=faults, ndet=ndet, nst=nst)


if __name__ == '__main__':
    import stage2_surface as s3
    s = Surface(3)
    assert s.DATA == s3.DATA and s.XSTABS == s3.XSTABS and s.ZSTABS == s3.ZSTABS
    assert s.ZDETS == s3.ZDETS and s.XDETS == s3.XDETS
    assert list(s.LZ) == list(s3.LZ) and list(s.XL) == list(s3.XL)
    import random
    rng = random.Random(0)
    allx = [(q, t) for q in s.DATA for t in range(s.T)]
    allmz = [(k, t) for k in s.ZSTABS for t in range(s.T)]
    for _ in range(300):
        xs = set(rng.sample(allx, 3)); ms = set(rng.sample(allmz, 2))
        a = s.simulate(xs, set(), ms, set()); b = s3.simulate(xs, set(), ms, set())
        assert a[0] == b[0] and a[2] == b[2]
    print('d=3 Surface matches stage2_surface: OK')
    for d in (3, 5):
        s = Surface(d)
        print(f'  d={d}: {s.NDATA} data, {s.NSTAB} stabs, '
              f'prefix bits/sector={len(s.stabs("X"))*4}, '
              f'faults/sector={len(s.sector_faults("X"))}')
