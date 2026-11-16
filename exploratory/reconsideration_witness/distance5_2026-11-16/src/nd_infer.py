"""Tractable general-distance decoder: bounded-weight frame + bounded marginal.

The only piece of Astra's d=3 E_frame decoder that does not scale is the frame: she
tabulates the exact independent-Bernoulli committed-logical MAP over a dense 2^(prefix)
index (2^17 convolution per sector at d=3 -> 2^49 at d=5). This module replaces it with a
BOUNDED-WEIGHT committed-logical MAP, computed as a SPARSE table over only the prefix
syndromes reachable by <= w_frame ordinary faults. Everything else (bounded marginal,
shared-onset inference, four arms, serialization, accounting) mirrors Astra exactly.

The bounded frame is approximate relative to Astra's exact frame; the d=3 validation here
measures the deviation (the frozen tolerance), and the SAME method is used at d=3 and d=5
so the distance comparison is apples-to-apples. Report routing and arms are general-d.
"""
import itertools
import numpy as np
from functools import lru_cache
import nd_surface

ARMS = ('thick', 'thin', 'diamond', 'whole')
EPS = 1e-12


class Decoder:
    def __init__(self, d, site, w_dec=3, w_frame=3, onsets=(1, 2), p=1e-3):
        self.s = nd_surface.Surface(d, p=p)
        self.site = tuple(site)
        self.onsets = tuple(onsets)
        self.w_dec = w_dec
        self.w_frame = w_frame
        self.odds = p / (1 - p)
        self.NST = self.s.NSTAB
        self.star = sorted(self.s.STAR[self.site])
        self.query = len(self.star) * len(self.onsets)
        self._prep()

    # ---- prefix encoding (rounds 0-3 detectors) ----
    def _prefix_idx(self, sector):
        return [i for i, (_, t) in enumerate(self.s.positions(sector)) if t <= 3]

    def _code_of(self, sector, sigrow):
        idx = self._pidx[sector]
        return int(sum(int(sigrow[i]) << j for j, i in enumerate(idx)))

    def _prep(self):
        self._pidx = {sec: self._prefix_idx(sec) for sec in ('X', 'Z')}
        self._tab = {}
        self._frame_table = {}
        self._erasure = {}
        self._epref = {}
        self._frame_col = {}        # (sector, onset) -> frame bit per candidate config
        self._mcache = {}           # memoized marginals (key = permitted evidence)
        for sector in ('X', 'Z'):
            t = self.s.build_tables(sector, self.w_dec)
            SIG, BND, LOG, W = t['SIG'], t['BND'], t['LOG'], t['W']
            ODDS = self.odds ** W
            # prefix detector code per candidate config (vectorized)
            idx = self._pidx[sector]
            powers = (1 << np.arange(len(idx), dtype=np.int64))
            CODE = (SIG[:, idx].astype(np.int64) @ powers)
            # pack each config's detector signature and boundary into one uint64
            ndet = SIG.shape[1]; nst = BND.shape[1]
            SIGP = (SIG.astype(np.uint64) << np.arange(ndet, dtype=np.uint64)).sum(1)
            BNDP = (BND.astype(np.uint64) << np.arange(nst, dtype=np.uint64)).sum(1)
            t.update(SIG=SIG, BND=BND, LOG=LOG, ODDS=ODDS, CODE=CODE, SIGP=SIGP, BNDP=BNDP)
            self._tab[sector] = t
            self._frame_table[sector] = self._build_frame_table(sector)
            # erasure signature at each onset (free fault on the loss site)
            faulttag = 'X' if sector == 'X' else 'Z'
            for onset in self.onsets:
                esig, elog, ebnd = self.s.unit_sig(sector, (faulttag, self.site, onset))
                self._erasure[(sector, onset)] = (esig, elog, ebnd)
                epref = self._code_of(sector, esig)
                self._epref[(sector, onset)] = epref
                # precompute frame bit for (candidate code ^ epref) per candidate
                ftab = self._frame_table[sector]
                shifted = CODE ^ epref
                self._frame_col[(sector, onset, 1)] = np.array(
                    [ftab.get(int(c), 0) for c in shifted], dtype=np.uint8)
            self._frame_col[(sector, 0)] = np.array(
                [self._frame_table[sector].get(int(c), 0) for c in CODE], dtype=np.uint8)

    def _build_frame_table(self, sector):
        """Sparse {prefix_detector_code: committed-logical argmax} over configs <= w_frame.
        Committed logical = XOR of logical bits of faults in rounds 0-2."""
        faults = [f for f in self.s.sector_faults(sector) if f[2] <= 3]
        unit = {}
        for f in faults:
            sig, logical, _ = self.s.unit_sig(sector, f)
            unit[f] = (self._code_of(sector, sig), int(logical) if f[2] < 3 else 0)
        acc = {}
        for w in range(self.w_frame + 1):
            ow = self.odds ** w
            for combo in itertools.combinations(faults, w):
                c = 0; lg = 0
                for f in combo:
                    uc, ul = unit[f]
                    c ^= uc; lg ^= ul
                a = acc.get(c)
                if a is None:
                    acc[c] = [0.0, 0.0]
                    a = acc[c]
                a[lg] += ow
        return {c: (1 if (v[1] - v[0]) > EPS * (v[0] + v[1]) else 0) for c, v in acc.items()}

    def observed_frames(self, DZ, DX):
        out = []
        for sector, dets in (('X', DZ), ('Z', DX)):
            idx = self._pidx[sector]; pos = self.s.positions(sector)
            code = int(sum(int(dets[pos[i]]) << j for j, i in enumerate(idx)))
            out.append(int(self._frame_table[sector].get(code, 0)))
        return out

    # ---- bounded marginal (mirrors Astra), memoized by permitted evidence ----
    def _marginal(self, sector, cond_dets, cond_bnd, frame, onset, split):
        key = (sector, cond_dets, cond_bnd, frame, onset, split)
        hit = self._mcache.get(key)
        if hit is None:
            hit = self._marginal_compute(sector, cond_dets, cond_bnd, frame, onset, split)
            self._mcache[key] = hit
        return hit

    def _marginal_compute(self, sector, cond_dets, cond_bnd, frame, onset, split):
        # Packed conditioning: all conditioned detector bits tested in ONE masked
        # uint64 compare over all configs; same for boundary. The free-erasure term
        # (e=1) shifts the target value by the erasure's packed bits.
        t = self._tab[sector]
        SIGP, BNDP, LOG, ODDS = t['SIGP'], t['BNDP'], t['LOG'], t['ODDS']
        pos = self.s.positions(sector); stabs = self.s.stabs(sector)
        didx = {dd: i for i, dd in enumerate(pos)}; sidx = {k: i for i, k in enumerate(stabs)}
        esig, elog, ebnd = self._erasure[(sector, onset)]
        dmask = dval = np.uint64(0)
        for dd, v in cond_dets:
            c = didx[dd]; dmask |= np.uint64(1) << np.uint64(c)
            if v:
                dval |= np.uint64(1) << np.uint64(c)
        bmask = bval = np.uint64(0)
        for k, v in cond_bnd:
            c = sidx[k]; bmask |= np.uint64(1) << np.uint64(c)
            if v:
                bval |= np.uint64(1) << np.uint64(c)
        espack = np.uint64(sum(int(esig[didx[dd]]) << didx[dd] for dd, _ in cond_dets))
        ebpack = np.uint64(sum(int(ebnd[sidx[k]]) << sidx[k] for k, _ in cond_bnd))
        w0 = w1 = 0.0
        for e in (0, 1):
            tv = dval ^ (espack if e else np.uint64(0))
            bt = bval ^ (ebpack if e else np.uint64(0))
            mask = (SIGP & dmask) == tv
            if bmask:
                mask &= (BNDP & bmask) == bt
            if frame is not None:
                fcol = self._frame_col[(sector, onset, 1)] if e else self._frame_col[(sector, 0)]
                mask &= fcol == frame
            pr = ODDS[mask]
            lg = LOG[mask] ^ (int(elog) if e else 0)
            w0 += float(pr[lg == 0].sum()) * 0.5
            w1 += float(pr[lg == 1].sum()) * 0.5
        return (w0, w1) if split else (w0 + w1)

    def decide(self, az, ax, bz, bx, frames):
        p0 = p1 = 0.0
        for onset in self.onsets:
            q0, q1 = self._marginal('X', tuple(sorted(az.items())), tuple(sorted(bz.items())),
                                    frames[0], onset, True)
            r = self._marginal('Z', tuple(sorted(ax.items())), tuple(sorted(bx.items())),
                               frames[1], onset, False)
            p0 += r * q0; p1 += r * q1
        tot = p0 + p1
        if tot <= 0:
            raise ValueError('zero evidence')
        p0n, p1n = p0 / tot, p1 / tot
        tie = abs(p0n - p1n) <= EPS
        label = 0 if (tie or p0n >= p1n) else 1
        return dict(label=label, p0=p0n, p1=p1n, tie=bool(tie))

    # ---- arms (direct, from the full record) ----
    def direct(self, DZ, DX, arm):
        frames = self.observed_frames(DZ, DX)
        if arm == 'thick':
            return self.decide(DZ, DX, {}, {}, frames)
        ZS, XS = self.s.ZSTABS, self.s.XSTABS
        bz = {k: DZ[k, 0] ^ DZ[k, 1] ^ DZ[k, 2] for k in ZS}
        bx = {k: DX[k, 0] ^ DX[k, 1] ^ DX[k, 2] for k in XS}
        keep = {(k, t) for k in range(self.NST) for t in (3, 4)}
        if arm == 'diamond':
            keep |= {(k, t) for k in self.star for t in self.onsets}
        if arm == 'whole':
            keep |= {(k, t) for k in range(self.NST) for t in range(3)}
        az = {d: v for d, v in DZ.items() if d in keep}
        ax = {d: v for d, v in DX.items() if d in keep}
        return self.decide(az, ax, bz, bx, frames)

    # ---- serialized state + restore-from-state decode ----
    def serialize(self, DZ, DX, arm):
        ZS, XS = self.s.ZSTABS, self.s.XSTABS
        rec = {**DZ, **DX}
        state = dict(arm=arm)
        if arm == 'thick':
            state['dense'] = {f'{k},{t}': rec[k, t] for k in range(self.NST) for t in range(5)}
            return state
        state['live'] = {f'{k},{t}': rec[k, t] for k in range(self.NST) for t in (3, 4)}
        state['boundary'] = {str(k): rec[k, 0] ^ rec[k, 1] ^ rec[k, 2] for k in range(self.NST)}
        state['frame'] = self.observed_frames(DZ, DX)
        if arm in ('diamond', 'whole'):
            state['archive'] = [[k, t] for k in range(self.NST) for t in range(3) if rec[k, t]]
        return state

    def decode_state(self, state):
        arm = state['arm']; ZS, XS = self.s.ZSTABS, self.s.XSTABS
        if arm == 'thick':
            rec = {(int(a), int(b)): v for key, v in state['dense'].items()
                   for a, b in [key.split(',')]}
            DZ = {d: v for d, v in rec.items() if d[0] in ZS}
            DX = {d: v for d, v in rec.items() if d[0] in XS}
            return self.decide(DZ, DX, {}, {}, self.observed_frames(DZ, DX))
        live = {(int(a), int(b)): v for key, v in state['live'].items()
                for a, b in [key.split(',')]}
        az = {d: v for d, v in live.items() if d[0] in ZS}
        ax = {d: v for d, v in live.items() if d[0] in XS}
        bnd = {int(k): v for k, v in state['boundary'].items()}
        bz = {k: v for k, v in bnd.items() if k in ZS}
        bx = {k: v for k, v in bnd.items() if k in XS}
        frames = state.get('frame', [None, None])
        if arm in ('diamond', 'whole'):
            arch = {tuple(x) for x in state['archive']}
            q = ([(k, t) for k in self.star for t in self.onsets] if arm == 'diamond'
                 else [(k, t) for k in range(self.NST) for t in range(3)])
            for (k, t) in q:
                (az if k in ZS else ax)[(k, t)] = 1 if (k, t) in arch else 0
        return self.decide(az, ax, bz, bx, frames)

    def payload_bits(self, arm, state=None):
        coord = int(np.ceil(np.log2(self.NST))) + int(np.ceil(np.log2(3)))  # 5 at d=3, 7 at d=5
        if arm == 'thick':
            return self.NST * 5                        # dense window: NST stabs x 5 rounds
        base = self.NST * 2 + self.NST + 2             # live(2 rounds) + boundary + 2 frame
        if arm == 'thin':
            return base
        return base + coord * (len(state.get('archive', [])) if state else 0)
