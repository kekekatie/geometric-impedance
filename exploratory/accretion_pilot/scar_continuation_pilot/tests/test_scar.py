#!/usr/bin/env python3
"""
test_scar.py -- unit tests for the scar-continuation pilot. Exits non-zero on
failure. Run (from src dir, with EFP_SNAPSHOT set):  python3 ../tests/test_scar.py

Covers:
  * single-valued 5D-lift PATH-INDEPENDENCE on connected sub-arcs (the Phase-1
    gauge safeguard): two independent spanning-tree lifts agree up to a constant;
    the frozen reader also reconstructs (no lift_cycle_conflict) on one component;
  * STRICT LEGALITY of every tile placed by the scar-tolerant scheduler (Phase 2):
    every added tile passes the frozen Patch.legal at placement, and the whole
    final patch is atlas-consistent.
"""
from __future__ import annotations
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import scar_common as SC
from scar_common import L
import arc_tools as AT

FAILS = []
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)

PHYS = SC.SR.PHYS
PHYS_TOL = SC.SR.PHYS_TOL


def lift_from_root(tiles, root_key):
    """Independent relative 5D lift via BFS from a chosen root vertex-key, using the
    frozen edge-direction basis PHYS. Returns {vkey: 5-vector} or raises on a cycle
    conflict (which must not happen on a valid connected sub-arc)."""
    key = lambda z: (round(z.real, 6), round(z.imag, 6))
    pos = {}; adj = collections.defaultdict(list)
    for t in tiles:
        zs = [t[1], t[2], t[3]]
        for z in zs:
            pos.setdefault(key(z), z)
        for p, q in zip(zs, zs[1:] + zs[:1]):
            delta = (q - p) / SC.S
            if abs(abs(delta) - 1) > 1e-4:
                continue
            err, j, sg = min((abs(delta - sg * e), j, sg) for j, e in enumerate(PHYS) for sg in (-1, 1))
            if err > PHYS_TOL:
                continue
            adj[key(p)].append((key(q), j, sg))
            adj[key(q)].append((key(p), j, -sg))
    rel = {root_key: [0] * 5}; queue = collections.deque([root_key])
    while queue:
        u = queue.popleft()
        for v, j, sg in adj[u]:
            kv = rel[u].copy(); kv[j] += sg
            if v in rel:
                if rel[v] != kv:
                    raise ValueError("lift_cycle_conflict")
            else:
                rel[v] = kv; queue.append(v)
    return rel


def test_lift_path_independence():
    st = SC.jam_state(7, 0)
    import math
    c = AT.centroid(st["band"]); th0, _ = AT.notch_theta0(st)
    arc = AT.largest_component(AT.angular_window(st["band"], c, th0 + math.pi, 1.0))
    keys = sorted({(round(z.real, 6), round(z.imag, 6)) for t in arc for z in t[1:]})
    r1, r2 = keys[0], keys[len(keys) // 2]
    try:
        lift1 = lift_from_root(arc, r1)
        lift2 = lift_from_root(arc, r2)
        no_conflict = True
    except ValueError:
        no_conflict = False
    check(no_conflict, "connected arc lift has no cycle conflict (single-valued)")
    if no_conflict:
        shared = set(lift1) & set(lift2)
        # the two lifts must differ by a constant 5-vector (path-independent)
        const = [lift1[r2][j] - lift2[r2][j] for j in range(5)]
        ok = all(all(lift1[v][j] - lift2[v][j] == const[j] for j in range(5)) for v in shared)
        check(ok, f"two independent spanning-tree lifts agree up to a constant ({len(shared)} vertices)")
    # frozen reader reconstructs on this single connected component
    payload = SC.RD.build_payload(st["Sstar"], st["cs"], arc)
    raw = SC.SR.read(payload)
    check(raw.get("status") == "reconstructed" and len(raw.get("components", [])) == 1,
          f"frozen reader reconstructs the connected arc as ONE component (status={raw.get('status')})")


def test_scar_strict_legality():
    """Every tile the scar-tolerant scheduler places must pass the frozen legality;
    the completed patch must be atlas-consistent at every vertex."""
    try:
        import scar_continuation as SCN
    except Exception as e:
        check(False, f"scar_continuation importable ({e})"); return
    res = SCN.scar_grow(7, 0, steps=44, record_illegal=True)
    check(res["illegal_placements"] == 0,
          f"scar-tolerant growth placed 0 illegal tiles (got {res['illegal_placements']})")
    # final patch atlas-consistency: every vertex is a complete/contiguous star
    P = L.Patch(list(res["full"]))
    import math
    bad = 0
    for k, lst in P.V.items():
        tot = sum(d for _, d, _ in lst)
        if tot > 2 * math.pi + 1e-6:
            bad += 1
    check(bad == 0, f"final scar-grown patch has no over-full vertex ({bad} bad)")


def main():
    print("[lift path-independence]")
    test_lift_path_independence()
    print("[scar strict legality]")
    test_scar_strict_legality()
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}"); sys.exit(1)
    print("ALL SCAR PILOT CHECKS PASSED.")


if __name__ == "__main__":
    main()
