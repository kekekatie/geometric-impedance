#!/usr/bin/env python3
"""Smoke test: can we faithfully replay a closure fork and a known B jam?

Reproduces the fork-selection + stream formula from window_retrodiction.main,
grows world 5 option B stream 0 (a recorded B jam), and checks it jams at the
recorded step. Prints, does not write.
"""
from __future__ import annotations
import engine_bridge as EB
P, W, S = EB.P, EB.W, EB.S

MAXWORLDS = 80

def fork_for_world(k):
    """Return (Sstar, edge, mid, cs, meta) for world k, or None (mirrors W.main)."""
    cs0 = P.common_state(k, P.centres(MAXWORLDS)[k])
    return cs0

def streams_for(k, nstreams=2):
    return [P.SEED0 * 1000 + k * 7919 + 101 * i for i in range(nstreams)]

def main():
    print(f"snapshot commit: {EB.SNAPSHOT_COMMIT}")
    print(f"SEED0={P.SEED0} WEDGE0={P.WEDGE0} MINPATCH={P.MINPATCH} RADIUS={P.RADIUS}")

    # Fork 0
    f0 = fork_for_world(0)
    assert f0 is not None, "world 0 should yield a fork"
    Sstar, edge, mid, cs, meta = f0
    print(f"\nworld 0 fork: patch={meta['patch']} ncands={len(cs)} "
          f"A=shape{cs[0][0]} B=shape{cs[1][0]}")

    # Known B jam: world 5, stream index 0, jam recorded at step 42 (nsnaps 43).
    k = 5
    f = fork_for_world(k)
    Sstar, edge, mid, cs, meta = f
    A, B = cs[0], cs[1]
    stream = streams_for(k)[0]
    print(f"\nworld {k}: patch={meta['patch']} stream0={stream}")
    armB = P.grow_arm(Sstar, B, stream, 44)
    print(f"  B arm: stop={armB['stop']} nsnaps={len(armB['snaps'])} guesses={armB['guesses']}")
    assert armB["stop"] == "jam", "world 5 B stream0 should jam"
    assert len(armB["snaps"]) == 43, f"expected nsnaps 43, got {len(armB['snaps'])}"
    # A arm must NOT jam
    armA = P.grow_arm(Sstar, A, stream, 44)
    print(f"  A arm: stop={armA['stop']} nsnaps={len(armA['snaps'])} guesses={armA['guesses']}")
    assert armA["stop"] != "jam", "world 5 A stream0 should not jam"
    print("\nSMOKE TEST PASSED: frozen engine replays fork + recorded B jam faithfully.")

if __name__ == "__main__":
    main()
