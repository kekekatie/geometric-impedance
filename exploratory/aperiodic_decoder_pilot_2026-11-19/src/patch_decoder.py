"""PatchDecoder: the audited bounded (w_frame,w_dec) decoder (nd_infer.Decoder) driven by
a PatchCode geometry adapter. Reuses nd_infer's sparse frame table, bounded marginal,
four arms, serialize/restore and payload accounting unchanged; only the construction is
specialized (inject a pre-built, shared PatchCode so the big w_dec table and the frame
table are built once per patch and reused across its six edges)."""
import sys
from pathlib import Path

_D5_SRC = (Path(__file__).resolve().parents[2]
           / 'reconsideration_witness' / 'distance5_2026-11-16' / 'src')
sys.path.insert(0, str(_D5_SRC))
import nd_infer  # noqa: E402
import pass2_caps  # noqa: E402  (chunked packed w<=4 table builder + CapDecoder)

ARMS = nd_infer.ARMS
EPS = nd_infer.EPS


class PatchDecoder(nd_infer.Decoder):
    def __init__(self, code, site, w_dec=3, w_frame=3, onsets=(1, 2), p=1e-3):
        self.s = code                         # shared PatchCode (caches build_tables/unit_sig)
        self.site = site                      # lost data-qubit index (int)
        self.onsets = tuple(onsets)
        self.w_dec = w_dec
        self.w_frame = w_frame
        self.odds = p / (1 - p)
        self.NST = self.s.NSTAB
        self.star = sorted(self.s.STAR[self.site])
        self.query = len(self.star) * len(self.onsets)
        self._prep()

    def _build_frame_table(self, sector):
        """Cache the sparse committed-logical MAP frame table on the shared PatchCode:
        it depends only on (patch geometry, sector, w_frame), not the loss site."""
        key = (sector, self.w_frame)
        hit = self.s._frame_cache.get(key)
        if hit is None:
            hit = super()._build_frame_table(sector)
            self.s._frame_cache[key] = hit
        return hit


class PatchCapDecoder(pass2_caps.CapDecoder):
    """Cap-sensitivity decoder on a patch: the audited chunked packed (w<=4) builder
    (pass2_caps) driven by a PatchCode. The heavy per-(sector,caps) tables and frame
    tables are cached on the shared PatchCode, so a patch's six edges reuse one build."""

    def __init__(self, code, site, w_frame, w_dec, onsets=(1, 2), p=1e-3):
        self.s = code
        self.site = site                       # int qubit index (not tuple)
        self.onsets = tuple(onsets)
        self.w_dec = w_dec
        self.w_frame = w_frame
        self.odds = p / (1 - p)
        self.NST = self.s.NSTAB
        self.star = sorted(self.s.STAR[self.site])
        self.query = len(self.star) * len(self.onsets)
        if not hasattr(self.s, '_cap_tab'):
            self.s._cap_tab = {}
            self.s._cap_frame = {}
        self._prep_eff()

    def _prep_eff(self):
        import numpy as np
        self._pidx = {sec: self._prefix_idx(sec) for sec in ('X', 'Z')}
        self._tab = {}
        self._frame_table = {}
        self._erasure = {}
        self._epref = {}
        self._frame_col = {}
        self._mcache = {}
        for sector in ('X', 'Z'):
            tkey = (sector, self.w_dec)
            tab = self.s._cap_tab.get(tkey)
            if tab is None:
                faults, usp, ubp, ulg, ndet, nst = pass2_caps._unit_packed(self.s, sector)
                SIGP, BNDP, LOG, ODDS, WT = pass2_caps.enumerate_packed(
                    usp, ubp, ulg, self.w_dec, self.odds)
                prefix_bits = self._pidx[sector]
                CODE = pass2_caps._code_from_sigp(SIGP, prefix_bits)
                tab = dict(SIGP=SIGP, BNDP=BNDP, LOG=LOG, ODDS=ODDS, CODE=CODE,
                           ndet=ndet, nst=nst, faults=faults)
                self.s._cap_tab[tkey] = tab
            self._tab[sector] = tab
            fkey = (sector, self.w_frame)
            ft = self.s._cap_frame.get(fkey)
            if ft is None:
                ft = pass2_caps.build_frame_table(self.s, sector, self.w_frame, self.odds,
                                                  self._pidx[sector], tab['ndet'])
                self.s._cap_frame[fkey] = ft
            self._frame_table[sector] = ft
            CODE = tab['CODE']
            faulttag = 'X' if sector == 'X' else 'Z'
            for onset in self.onsets:
                esig, elog, ebnd = self.s.unit_sig(sector, (faulttag, self.site, onset))
                self._erasure[(sector, onset)] = (esig, elog, ebnd)
                epref = self._code_of(sector, esig)
                self._epref[(sector, onset)] = epref
                shifted = CODE ^ epref
                self._frame_col[(sector, onset, 1)] = np.array(
                    [ft.get(int(c), 0) for c in shifted], dtype=np.uint8)
            self._frame_col[(sector, 0)] = np.array(
                [ft.get(int(c), 0) for c in CODE], dtype=np.uint8)
