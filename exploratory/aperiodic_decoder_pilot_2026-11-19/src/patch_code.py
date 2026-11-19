"""Geometry adapter: expose a certified aperiodic/square patch through the SAME
attribute/method contract as nd_surface.Surface, so the audited bounded decoder
(nd_infer.Decoder) runs on it unchanged.

We subclass nd_surface.Surface and override only the geometry construction: instead of
geo.build_code(d) we load DATA / STABS / STAR / LZ / XL from the saved patch JSON
(exploratory/aperiodic_qec_geometry_2026-11-19/results/{square,AB,Penrose}.json). Every
generic method (simulate, unit_sig, sector_faults, build_tables, positions, stabs) is
inherited verbatim.

Check-ID convention: 'X{i}' -> stab index i (0..9), 'Z{i}' -> stab index 10+i (10..19).
Data qubits are indices 0..n-1. STAR[lost_qubit] = the four incident check indices of
that eligible edge (two endpoint X-checks + two adjacent face Z-checks).
"""
import json
import sys
from pathlib import Path

import numpy as np

# distance5 src carries nd_surface / nd_infer (and sets its own path for `geo`).
_D5_SRC = (Path(__file__).resolve().parents[2]
           / 'reconsideration_witness' / 'distance5_2026-11-16' / 'src')
sys.path.insert(0, str(_D5_SRC))
import nd_surface  # noqa: E402

_GEOM_DIR = (Path(__file__).resolve().parents[2]
             / 'aperiodic_qec_geometry_2026-11-19' / 'results')


def check_index(cid):
    """'X3' -> 3, 'Z7' -> 17 (X-checks 0..9, Z-checks 10..19)."""
    return int(cid[1:]) + (0 if cid[0] == 'X' else 10)


class PatchCode(nd_surface.Surface):
    def __init__(self, family, p=1e-3, T=5):
        data = json.loads((_GEOM_DIR / f'{family}.json').read_text())
        self.family = family
        self.json = data
        self.d = 3                       # nominal distance label (dX = dZ = 3)
        self.T = T
        self.P = p
        n = data['n']
        self.DATA = list(range(n))
        self.NDATA = n
        self.DIDX = {q: q for q in self.DATA}
        # STABS: indices 0..9 = X-checks (HX rows), 10..19 = Z-checks (HZ rows)
        HX = data['HX']
        HZ = data['HZ']
        self.STABS = []
        for row in HX:
            self.STABS.append({'type': 'X', 'support': tuple(q for q in range(n) if row[q])})
        for row in HZ:
            self.STABS.append({'type': 'Z', 'support': tuple(q for q in range(n) if row[q])})
        self.XSTABS = [k for k, s in enumerate(self.STABS) if s['type'] == 'X']
        self.ZSTABS = [k for k, s in enumerate(self.STABS) if s['type'] == 'Z']
        self.NSTAB = len(self.STABS)
        self.ZDETS = [(k, t) for k in self.ZSTABS for t in range(T)]   # X-sector detectors
        self.XDETS = [(k, t) for k in self.XSTABS for t in range(T)]   # Z-sector detectors
        # logical supports as indicator vectors over data qubits
        self.LZ = [1 if q in set(data['logical_Z']) else 0 for q in range(n)]
        self.XL = [1 if q in set(data['logical_X']) else 0 for q in range(n)]
        assert self._dot(self.LZ, self.XL) == 1, 'logical supports must anticommute'
        # STAR[lost_qubit] = the four incident check indices of that eligible edge
        self.STAR = {}
        self.eligible = {}            # lost_qubit -> full eligible record
        for e in data['eligible']:
            idxs = sorted(check_index(c) for c in e['checks'])
            self.STAR[e['qubit']] = idxs
            self.eligible[e['qubit']] = e
        # cache for per-patch frame tables (shared across the 6 edges)
        self._frame_cache = {}

    # --- adapter self-checks (geometry only, no decoder scores) ---
    def hx(self):
        return np.array([[1 if q in s['support'] else 0 for q in range(self.NDATA)]
                         for s in self.STABS if s['type'] == 'X'], dtype=np.int64)

    def hz(self):
        return np.array([[1 if q in s['support'] else 0 for q in range(self.NDATA)]
                         for s in self.STABS if s['type'] == 'Z'], dtype=np.int64)


def gf2_rank(M):
    M = (np.array(M) % 2).astype(np.uint8).copy()
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i, c]:
                piv = i
                break
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        r += 1
        if r == rows:
            break
    return r
