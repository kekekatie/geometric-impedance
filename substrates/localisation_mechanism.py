#!/usr/bin/env python3
"""
What property of the address layer resists localisation?

The multiplex result showed a perpendicular-space potential localising transport
far less than the same weights shuffled. But a shuffle null only excludes
"random". It does not distinguish quasiperiodic order from any other kind of
spatial coherence.

So: four potentials carrying an *identical multiset of values*, differing only in
how those values are arranged over the vertices.

  quasiperiodic  true perpendicular radius on its true vertex
  random         the same values permuted (the original shuffle null)
  smooth         the same values rank-matched onto distance from patch centre
  periodic       the same values rank-matched onto a cosine grid

If quasiperiodic, smooth and periodic all behave alike and differ from random,
the effect is spatial coherence and has nothing to do with quasiperiodicity. If
quasiperiodic separates from periodic and smooth, that is a stronger and much
more interesting claim.

Random is replicated over several permutations to get an error bar; the other
three are deterministic given the substrate.
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from audit_with_nulls import read_csv_rows, read_edges
from multiplex_ab import transition, transport_stats


def rank_match(values, target):
    """Arrange `values` over vertices so their ordering follows `target`.

    Produces a field with exactly the same multiset of values as `values` but
    the spatial arrangement of `target`.
    """
    out = np.empty_like(values)
    out[np.argsort(target)] = np.sort(values)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lift", default="real_ab_lift.csv")
    ap.add_argument("--edges", default="real_ab_edges.csv")
    ap.add_argument("--sigmas", default="1.5,1.0,0.7,0.5")
    ap.add_argument("--shuffles", type=int, default=5)
    ap.add_argument("--sources", type=int, default=8)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = read_csv_rows(args.lift)
    E = read_edges(args.edges)
    n = len(rows)
    par = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    perp = np.array([[float(r["perp_x"]), float(r["perp_y"])] for r in rows])
    pr = np.linalg.norm(perp, axis=1)

    rng = np.random.default_rng(args.seed)
    centre = par.mean(0)
    radial = np.linalg.norm(par - centre, axis=1)
    src = rng.choice(np.argsort(radial)[:600], args.sources, replace=False)

    span = float(np.ptp(par[:, 0]))
    k = 2 * np.pi * 10.0 / span                       # ~10 oscillations across the patch
    cosgrid = np.cos(k * par[:, 0]) + np.cos(k * par[:, 1])

    fields = {
        "quasiperiodic": [pr],
        "smooth":        [rank_match(pr, radial)],
        "periodic":      [rank_match(pr, cosgrid)],
        "random":        [pr[rng.permutation(n)] for _ in range(args.shuffles)],
    }

    for name, fs in fields.items():
        for f in fs:
            assert np.allclose(np.sort(f), np.sort(pr)), f"{name} multiset differs"
    print(f"substrate: {n} vertices, {len(E)} edges")
    print(f"all four fields carry an identical multiset of values "
          f"(range {pr.min():.3f}-{pr.max():.3f})\n")

    sigmas = [float(x) for x in args.sigmas.split(",")]
    print(f"{'sigma':>6} {'field':>15} {'spread':>18} {'localisation':>20}")
    print("-" * 62)
    results = {}
    for sg in sigmas:
        for name, fs in fields.items():
            sp, ip = [], []
            for f in fs:
                a, b = transport_stats(transition(n, E, f, sg), par, src, steps=args.steps)
                sp.append(a); ip.append(b)
            m_sp, m_ip = float(np.mean(sp)), float(np.mean(ip))
            e_sp = float(np.std(sp, ddof=1)) if len(sp) > 1 else 0.0
            e_ip = float(np.std(ip, ddof=1)) if len(ip) > 1 else 0.0
            results[(sg, name)] = (m_sp, m_ip)
            print(f"{sg:6.2f} {name:>15} {m_sp:11.4f} +- {e_sp:.4f} "
                  f"{m_ip:13.4e} +- {e_ip:.1e}")
        print("-" * 62)

    print("\nlocalisation relative to random at matched sigma (lower = resists more):")
    print(f"{'sigma':>6} {'quasiperiodic':>15} {'smooth':>12} {'periodic':>12}")
    for sg in sigmas:
        r = results[(sg, "random")][1]
        print(f"{sg:6.2f} "
              f"{results[(sg,'quasiperiodic')][1]/r:15.3f} "
              f"{results[(sg,'smooth')][1]/r:12.3f} "
              f"{results[(sg,'periodic')][1]/r:12.3f}")


if __name__ == "__main__":
    main()
