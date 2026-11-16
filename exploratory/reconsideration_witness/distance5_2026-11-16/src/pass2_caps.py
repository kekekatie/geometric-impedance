"""Efficient weight-<=4 packed table builder + CapDecoder for Pass 2 cap sensitivity.

nd_infer.Decoder's table build materializes Python lists of per-config arrays, which
is fine at w=3 (~1M configs) but blows up at w=4 (47M marginal / 19M frame combos per
sector). This module builds the SAME packed structures the marginal query needs
(SIGP, BNDP, LOG, ODDS, CODE) by CHUNKED combination enumeration straight into
preallocated numpy arrays, and an efficient frame table. CapDecoder reuses all of
nd_infer.Decoder's query/decode logic but swaps in this builder, so (w_frame,w_dec)
in {(3,3),(4,3),(3,4),(4,4)} are tractable in ~15 GB. Validated to reproduce the
stock decoder exactly at (3,3).
"""
import itertools
import numpy as np
from math import comb
import nd_infer, nd_surface


def _unit_packed(s, sector):
    """Per-fault packed detector sig (uint64), boundary (uint64), logical (uint8)."""
    faults = s.sector_faults(sector)
    pos = s.positions(sector); stabs = s.stabs(sector)
    ndet = len(pos); nst = len(stabs)
    usp = np.zeros(len(faults), np.uint64); ubp = np.zeros(len(faults), np.uint64)
    ulg = np.zeros(len(faults), np.uint8)
    for fi, f in enumerate(faults):
        sig, logical, bnd = s.unit_sig(sector, f)
        usp[fi] = int(sum(int(sig[i]) << i for i in range(ndet)))
        ubp[fi] = int(sum(int(bnd[i]) << i for i in range(nst)))
        ulg[fi] = int(logical) & 1
    return faults, usp, ubp, ulg, ndet, nst


def _total(n, wmax):
    return sum(comb(n, w) for w in range(wmax + 1))


def enumerate_packed(usp, ubp, ulg, wmax, odds):
    """All fault combinations of weight 0..wmax, as packed arrays (SIGP,BNDP,LOG,ODDS).
    Chunked: weight-4 uses C(n,3) vectorized inner blocks, no Python per-combo lists."""
    n = len(usp)
    N = _total(n, wmax)
    SIGP = np.empty(N, np.uint64); BNDP = np.empty(N, np.uint64)
    LOG = np.empty(N, np.uint8); WT = np.empty(N, np.uint8)
    o = 0
    # w=0
    SIGP[0] = 0; BNDP[0] = 0; LOG[0] = 0; WT[0] = 0; o = 1
    if wmax >= 1:
        m = n
        SIGP[o:o + m] = usp; BNDP[o:o + m] = ubp; LOG[o:o + m] = ulg; WT[o:o + m] = 1; o += m
    if wmax >= 2:
        for i in range(n - 1):
            j = np.arange(i + 1, n)
            m = len(j)
            SIGP[o:o + m] = usp[i] ^ usp[j]
            BNDP[o:o + m] = ubp[i] ^ ubp[j]
            LOG[o:o + m] = ulg[i] ^ ulg[j]
            WT[o:o + m] = 2; o += m
    if wmax >= 3:
        for i in range(n - 2):
            si, bi, li = usp[i], ubp[i], ulg[i]
            for j in range(i + 1, n - 1):
                k = np.arange(j + 1, n); m = len(k)
                SIGP[o:o + m] = si ^ usp[j] ^ usp[k]
                BNDP[o:o + m] = bi ^ ubp[j] ^ ubp[k]
                LOG[o:o + m] = li ^ ulg[j] ^ ulg[k]
                WT[o:o + m] = 3; o += m
    if wmax >= 4:
        for i in range(n - 3):
            si, bi, li = usp[i], ubp[i], ulg[i]
            for j in range(i + 1, n - 2):
                sj = si ^ usp[j]; bj = bi ^ ubp[j]; lj = li ^ ulg[j]
                for k in range(j + 1, n - 1):
                    l = np.arange(k + 1, n); m = len(l)
                    SIGP[o:o + m] = sj ^ usp[k] ^ usp[l]
                    BNDP[o:o + m] = bj ^ ubp[k] ^ ubp[l]
                    LOG[o:o + m] = lj ^ ulg[k] ^ ulg[l]
                    WT[o:o + m] = 4; o += m
    assert o == N, (o, N)
    ODDS = odds ** WT.astype(np.float64)
    return SIGP, BNDP, LOG, ODDS, WT


def _code_from_sigp(SIGP, prefix_bits):
    """Prefix detector code per config, derived from the packed sig (vectorized)."""
    CODE = np.zeros(len(SIGP), np.int64)
    for j, i in enumerate(prefix_bits):
        CODE |= (((SIGP >> np.uint64(i)) & np.uint64(1)).astype(np.int64) << j)
    return CODE


def build_frame_table(s, sector, w_frame, odds, prefix_bits, ndet):
    """Sparse {prefix_code: committed-logical argmax} over configs <= w_frame, built
    by chunked enumeration. Committed logical = XOR of logical bits of faults in
    rounds 0-2 (t<3); faults at t==3 contribute to the prefix code but not the bit."""
    faults = [f for f in s.sector_faults(sector) if f[2] <= 3]
    nf = len(faults)
    ucode = np.zeros(nf, np.int64); ulog = np.zeros(nf, np.uint8)
    for fi, f in enumerate(faults):
        sig, logical, _ = s.unit_sig(sector, f)
        c = 0
        for j, i in enumerate(prefix_bits):
            c |= (int(sig[i]) & 1) << j
        ucode[fi] = c
        ulog[fi] = (int(logical) & 1) if f[2] < 3 else 0
    EPS = nd_infer.EPS
    acc = {}

    def add(codes, logs, w):
        ow = odds ** w
        # group by (code, log) accumulation
        for c, lg in zip(codes.tolist(), logs.tolist()):
            a = acc.get(c)
            if a is None:
                a = acc[c] = [0.0, 0.0]
            a[lg] += ow
    add(np.array([0]), np.array([0], np.uint8), 0)
    if w_frame >= 1:
        add(ucode, ulog, 1)
    if w_frame >= 2:
        for i in range(nf - 1):
            j = np.arange(i + 1, nf)
            add(ucode[i] ^ ucode[j], ulog[i] ^ ulog[j], 2)
    if w_frame >= 3:
        for i in range(nf - 2):
            for j in range(i + 1, nf - 1):
                k = np.arange(j + 1, nf)
                add(ucode[i] ^ ucode[j] ^ ucode[k], ulog[i] ^ ulog[j] ^ ulog[k], 3)
    if w_frame >= 4:
        for i in range(nf - 3):
            for j in range(i + 1, nf - 2):
                cj = ucode[i] ^ ucode[j]; lj = ulog[i] ^ ulog[j]
                for k in range(j + 1, nf - 1):
                    l = np.arange(k + 1, nf)
                    add(cj ^ ucode[k] ^ ucode[l], lj ^ ulog[k] ^ ulog[l], 4)
    return {c: (1 if (v[1] - v[0]) > EPS * (v[0] + v[1]) else 0) for c, v in acc.items()}


class CapDecoder(nd_infer.Decoder):
    def __init__(self, d, site, w_frame, w_dec, onsets=(1, 2), p=1e-3):
        self.s = nd_surface.Surface(d, p=p)
        self.site = tuple(site); self.onsets = tuple(onsets)
        self.w_dec = w_dec; self.w_frame = w_frame
        self.odds = p / (1 - p); self.NST = self.s.NSTAB
        self.star = sorted(self.s.STAR[self.site]); self.query = len(self.star) * len(self.onsets)
        self._prep_eff()

    def _prep_eff(self):
        self._pidx = {sec: self._prefix_idx(sec) for sec in ('X', 'Z')}
        self._tab = {}; self._frame_table = {}; self._erasure = {}; self._epref = {}
        self._frame_col = {}; self._mcache = {}
        for sector in ('X', 'Z'):
            faults, usp, ubp, ulg, ndet, nst = _unit_packed(self.s, sector)
            SIGP, BNDP, LOG, ODDS, WT = enumerate_packed(usp, ubp, ulg, self.w_dec, self.odds)
            prefix_bits = self._pidx[sector]
            CODE = _code_from_sigp(SIGP, prefix_bits)
            self._tab[sector] = dict(SIGP=SIGP, BNDP=BNDP, LOG=LOG, ODDS=ODDS, CODE=CODE,
                                     ndet=ndet, nst=nst, faults=faults)
            self._frame_table[sector] = build_frame_table(self.s, sector, self.w_frame,
                                                          self.odds, prefix_bits, ndet)
            faulttag = 'X' if sector == 'X' else 'Z'
            for onset in self.onsets:
                esig, elog, ebnd = self.s.unit_sig(sector, (faulttag, self.site, onset))
                self._erasure[(sector, onset)] = (esig, elog, ebnd)
                epref = self._code_of(sector, esig); self._epref[(sector, onset)] = epref
                ftab = self._frame_table[sector]; shifted = CODE ^ epref
                self._frame_col[(sector, onset, 1)] = np.array(
                    [ftab.get(int(c), 0) for c in shifted], dtype=np.uint8)
            self._frame_col[(sector, 0)] = np.array(
                [self._frame_table[sector].get(int(c), 0) for c in CODE], dtype=np.uint8)

    # prefix absence accounting: observed prefix codes not in the frame table
    def prefix_absent(self, DZ, DX):
        out = {}
        for sector, dets in (('X', DZ), ('Z', DX)):
            idx = self._pidx[sector]; pos = self.s.positions(sector)
            code = int(sum(int(dets[pos[i]]) << j for j, i in enumerate(idx)))
            out[sector] = code not in self._frame_table[sector]
        return out


if __name__ == '__main__':
    import time
    # validate (3,3) matches the stock decoder bit-for-bit on a few histories
    import nd_run
    D0 = nd_infer.Decoder(5, (2, 2)); Dc = CapDecoder(5, (2, 2), 3, 3)
    s = D0.s
    rng = __import__('random').Random(1)
    pool = [(tag, q, t) for q in s.DATA for t in range(5) for tag in ('X', 'Z')]
    pool += [('MZ', k, t) for k in s.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in s.XSTABS for t in range(5)]
    mism = 0
    for _ in range(200):
        ex = rng.sample(pool, 3)
        fts = tuple(ex) + ((('X', (2, 2), 1),))
        DZ, DX, truth, _ = s.simulate(*nd_run.compose(fts))
        for arm in nd_infer.ARMS:
            a = D0.direct(DZ, DX, arm); b = Dc.direct(DZ, DX, arm)
            if a['label'] != b['label'] or abs(a['p0'] - b['p0']) > 1e-9:
                mism += 1
    print('(3,3) CapDecoder vs stock: mismatches', mism, '/ 800')
