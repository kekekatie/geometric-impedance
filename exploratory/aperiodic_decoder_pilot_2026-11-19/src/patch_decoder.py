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
