#!/usr/bin/env python3
"""
monte_carlo.py -- independent sanity check of Task 2 on the FULL labelled graph (no reduction,
no pruning, no truncation): simulate the pair-collision toy to frozen N times and compare the
one-pair frequency with the certified interval from pair_collision.py.

A gate, not a result: asserts the estimate lies within 4 standard errors of the certified value,
and that the collision frequency lies within 4 SE of 1/3. Nonzero exit on failure.

    python3 monte_carlo.py            # N = 200000, seed 20260923
    python3 monte_carlo.py 50000 7    # N, seed
"""
from __future__ import annotations
import os, sys, random, math
import pair_collision as PC

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "monte_carlo_report.txt")
CERT_LO, CERT_HI = 0.123896379462952, 0.123896379462967     # from pair_collision.py (K=12)


def run_once(rng):
    G = PC.start_full(); collided = False
    while True:
        evs = PC.events_full(G)
        if not any(e[0] == "C" for e in evs) and PC.is_matching_full(G):
            return collided, len(PC.active_edges(G))
        e = evs[rng.randrange(len(evs))]
        collided |= (e[0] == "C" and e[2] == PC.Q_)
        G = PC.apply_full(G, e)


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260923
    rng = random.Random(seed)
    one = col = 0; ends = {}
    for _ in range(N):
        c, B = run_once(rng)
        col += c; one += (B == 1); ends[B] = ends.get(B, 0) + 1
    p1, pc = one / N, col / N
    se1 = math.sqrt(p1 * (1 - p1) / N); sec = math.sqrt(pc * (1 - pc) / N)
    mid = (CERT_LO + CERT_HI) / 2
    lines = [f"Monte Carlo, full labelled graph, N={N}, seed={seed}",
             f"  end states by active-edge count B: {dict(sorted(ends.items()))}",
             f"  P(CONTACT(a,q,c) fired) ~ {pc:.5f} +- {sec:.5f}   (exact 1/3 = {1/3:.5f}; "
             f"z = {(pc - 1/3) / sec:+.2f})",
             f"  P(one pair + two loners) ~ {p1:.5f} +- {se1:.5f}   (certified {mid:.9f}; "
             f"z = {(p1 - mid) / se1:+.2f};  1/8 would be z = {(p1 - 0.125) / se1:+.2f})"]
    ok = (set(ends) <= {1, 2} and abs(pc - 1 / 3) < 4 * sec and abs(p1 - mid) < 4 * se1)
    lines.append("MONTE CARLO CONSISTENT WITH EXACT RESULTS." if ok else "MONTE CARLO CHECK FAILED.")
    print("\n".join(lines))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(lines) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
