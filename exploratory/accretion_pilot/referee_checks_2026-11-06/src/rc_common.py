#!/usr/bin/env python3
"""
rc_common.py -- shared, read-only wiring for the referee checks (2026-11-06).

Everything frozen is imported, never modified: the growth engine and lattice
(engine_bridge -> L, D, S), the perp-space lift (perp_map -> lift, perp,
edge_dir), the replay helpers (pilot_common -> grow, skin_of, dead_sites), the
reader adapter (phase4_readout -> build_payload, classify, load_forks, B_JAMS),
and the frozen standalone reader (archive-free-reader/skin_reader -> read).

This module adds NO scientific policy. It only provides:
  * the two physical/perp direction bases (matching the reader exactly);
  * a forced-only closure built from the frozen scheduler primitives;
  * the band / recovery-case loaders;
  * a Chebyshev-centre LP on a reader F-region;
  * small lift/loop utilities.
It reuses the archive-free experiment's `af_common` purely for its frozen path
wiring (it sets EFP_SNAPSHOT paths and imports the frozen modules).
"""
from __future__ import annotations
import sys, json, math, cmath, collections
from pathlib import Path

# --- frozen wiring: reuse af_common's path setup (read-only) ---
AF_SRC = (Path(__file__).resolve().parents[2]
          / "scar_continuation_pilot" / "archive_free_2026-11-04" / "src")
if str(AF_SRC) not in sys.path:
    sys.path.insert(0, str(AF_SRC))
import af_common as AF                      # noqa: E402  wires EB, PC, RD, E, F
from af_common import L, D, S, PC, RD, dk   # noqa: E402
EB = AF.EB
M = EB.M                                     # perp_map: lift, perp, edge_dir

# frozen standalone reader (direct read(), identical to the isolated subprocess)
_RD_DIR = str(EB.EFP / "archive-free-reader")
if _RD_DIR not in sys.path:
    sys.path.insert(0, _RD_DIR)
import skin_reader as SR                     # noqa: E402

# --- direction bases, identical to skin_reader.py ---
PHYS = [cmath.exp(1j * math.radians(18 + 72 * j)) for j in range(5)]   # physical (parallel) space
PERP = [cmath.exp(4j * math.pi * j / 5) for j in range(5)]             # internal (perp) space
# The five worm / non-expansive directions are the five physical edge directions PHYS[j]
# (equivalently their opposite); a Conway worm runs along one of them.
WORM_DIRS = [cmath.exp(1j * math.radians(18 + 72 * j)) for j in range(5)]

HERE = Path(__file__).resolve().parents[1]           # referee_checks_2026-11-06
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
AF_INPUT = AF_SRC.parent / "input" / "worker_band_exports.json"
RECOVERY_CASES = EB.EFP / "archive-free-reader" / "results" / "cases"

B_JAMS = list(RD.B_JAMS)


# ---------------------------------------------------------------------------
# tiles / keys
# ---------------------------------------------------------------------------
def dtile(rec):
    """Deserialize a [c,[x,y],[x,y],[x,y]] record to a decorated half-tile."""
    return (int(rec[0]),) + tuple(complex(x, y) for x, y in rec[1:])


def tile_centroid(t):
    return sum(t[1:]) / 3.0


def centroid(tiles):
    zs = [z for t in tiles for z in t[1:]]
    return sum(zs) / len(zs)


# ---------------------------------------------------------------------------
# forced-only closure, built from the frozen scheduler primitives
# ---------------------------------------------------------------------------
def forced_closure(tiles, max_rounds=20000):
    """Apply ONLY forced moves (frontier edges with exactly one legal candidate)
    until none remain. No free choices. Returns (closed_tiles, status, n_added,
    n_zero_candidate_edges_at_end). Uses frozen D.candidates / Patch.legal / add."""
    P = L.Patch(list(tiles))
    n0 = len(P.tris)
    rounds = 0
    while True:
        rounds += 1
        if rounds > max_rounds:
            status = "STALL"
            break
        forced = {}
        zero = 0
        for e in P.frontier():
            cs = D.candidates(P, *e[:3])
            if len(cs) == 0:
                zero += 1
            elif len(cs) == 1:
                forced.setdefault(dk(cs[0]), cs[0])
        if not forced:
            status = "closed"
            break
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if placed == 0:
            status = "blocked"
            break
    # final zero-candidate count
    zero = sum(1 for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0)
    return list(P.tris), status, len(P.tris) - n0, zero


# ---------------------------------------------------------------------------
# lift / loop utilities (perp_map conventions)
# ---------------------------------------------------------------------------
def lift_tiles(tiles):
    """Frozen perp_map BFS lift. Returns (K: {vkey: np.int5}, pos, conflicts)."""
    return M.lift(list(tiles))


def phys_of(k):
    return sum(int(k[j]) * PHYS[j] for j in range(5))


def perp_of(k):
    return sum(int(k[j]) * PERP[j] for j in range(5))


def boundary_edges(tiles):
    """Edges (as frozenset of two vertex keys) that belong to exactly one tile:
    the band's boundary. Returns {edgekey: (p, q)} with representative coords."""
    count = collections.Counter()
    rep = {}
    for t in tiles:
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if abs(abs(q - p) - S) < 1e-4 * S:          # rhombus legs only (length S)
                ek = frozenset((L.key(p), L.key(q)))
                count[ek] += 1
                rep[ek] = (p, q)
    return {ek: rep[ek] for ek, n in count.items() if n == 1}


def boundary_loops(tiles):
    """Chain the boundary legs into closed vertex loops. Returns a list of loops,
    each a list of vertex keys in order (first != last; the loop is cyclic)."""
    bedges = boundary_edges(tiles)
    adj = collections.defaultdict(list)
    pos = {}
    for ek, (p, q) in bedges.items():
        kp, kq = L.key(p), L.key(q)
        adj[kp].append(kq); adj[kq].append(kp)
        pos[kp] = p; pos[kq] = q
    unused = set(bedges)
    loops = []
    while unused:
        ek0 = next(iter(unused))
        a, b = tuple(ek0)
        loop = [a, b]
        unused.discard(ek0)
        cur, prev = b, a
        while True:
            nxts = [w for w in adj[cur] if w != prev and frozenset((cur, w)) in unused]
            if not nxts:
                break
            nxt = nxts[0]
            unused.discard(frozenset((cur, nxt)))
            if nxt == loop[0]:
                break
            loop.append(nxt)
            prev, cur = cur, nxt
        loops.append((loop, pos))
    return loops


# ---------------------------------------------------------------------------
# reader F-region + Chebyshev centre
# ---------------------------------------------------------------------------
def read_tiles(Sstar, cs, tiles):
    """Frozen reader on a tile subset. Returns the raw reader dict (or status)."""
    payload = RD.build_payload(Sstar, cs, tiles)
    raw = SR.read(payload)
    return raw, payload


def chebyshev_centre(constraints, windows):
    """Centre of the largest inscribed circle of F = {x : n_{r,i}.x >= c},
    computed by LP (SciPy highs). Returns (centre[2], radius, status)."""
    import numpy as np
    from scipy.optimize import linprog
    A = []; b = []
    for r, i, c in constraints:
        nx, ny = windows[r]["normals"][i]
        nrm = math.hypot(nx, ny)
        if nrm < 1e-15:
            continue
        # n.x >= c  ->  -n.x <= -c ; with inscribed radius: -n.x + r*1 <= -c
        A.append([-nx / nrm, -ny / nrm, 1.0]); b.append(-c / nrm)
    if not A:
        return None, None, "no_constraints"
    A = np.array(A); b = np.array(b)
    # maximise r (x free, r >= 0); bound x to the reader's own [-50,50] clip box
    res = linprog([0, 0, -1], A_ub=A, b_ub=b,
                  bounds=[(-50, 50), (-50, 50), (0, None)], method="highs")
    if res.status != 0:
        return None, None, f"lp_status_{res.status}"
    x1, x2, r = res.x
    return [float(x1), float(x2)], float(r), "ok"


# ---------------------------------------------------------------------------
# dataset loaders
# ---------------------------------------------------------------------------
def load_jammed_bands():
    """The 11 jammed worker bands (jam checkpoint) + their fork data.
    Returns list of dicts: case, world, si, Sstar, cs, jam_band, final_band, scars, jam_step."""
    exports = json.loads(AF_INPUT.read_text())
    out = []
    for (w, si) in B_JAMS:
        jp = AF.jam_prep(w, si)
        ex = exports[f"w{w}-s{si}"]
        out.append(dict(case=f"w{w}-s{si}", world=w, si=si,
                        Sstar=jp["Sstar"], cs=jp["cs"], B=jp["B"], dead=jp["dead"],
                        jam_band=[dtile(t) for t in ex["jam"]],
                        final_band=[dtile(t) for t in ex["final"]],
                        scars=ex["scars"], jam_step=ex["jam_step"]))
    return out


def load_recovery_cases():
    """The 49 archive-free-reader recovery case payloads (surviving skins) +
    their analyst reference (true_index). Reader EVIDENCE is the payload tiles
    only; the reference is used only to label true A/B for reporting."""
    out = []
    for f in sorted(RECOVERY_CASES.glob("*.json")):
        env = json.loads(f.read_text())
        p = env["payload"]; ref = env.get("reference", {})
        tiles = [(int(t[0]),) + tuple(complex(x, y) for x, y in t[1:]) for t in p["tiles"]]
        out.append(dict(name=f.stem, payload=p, tiles=tiles,
                        true_index=ref.get("true_index"),
                        world=ref.get("world"), step=ref.get("step")))
    return out
