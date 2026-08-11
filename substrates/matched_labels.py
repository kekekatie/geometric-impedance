#!/usr/bin/env python3
"""
Privileged-site labels at a matched positive rate.

The v3 label is the intersection of three top-quartile retention sets. That fixes
the *threshold* per criterion but leaves the resulting positive rate free, and it
comes out wildly different per substrate: on Ammann-Beenker roughly 4% of
interior vertices, on Penrose well under 1%, sometimes too few to score at all.
Any AB-vs-Penrose comparison built on it therefore differs in positive rate as
well as in substrate.

This replaces the intersection with a rank-averaged composite of the same three
retention scores, thresholded at a fixed fraction. Every substrate then yields
the same positive rate by construction, and the three criteria still all
contribute.

The composite is built from graph-topological retention only; address features
are perpendicular-space coordinates and share no term with it, so the v3 leak
class does not apply. A shuffle null is still the right guard and callers should
keep running one.
"""

import numpy as np

from audit_with_nulls import retention, graph_ball_radius2


def _ranks(x):
    """Percentile rank in [0, 1], ties averaged."""
    order = np.argsort(np.argsort(x))
    return order / max(len(x) - 1, 1)


def matched_rate_labels(adj, active, euclid_seeds, fraction=0.03):
    """Top `fraction` of active vertices by rank-averaged retention.

    Returns (y, scores). The three retention criteria are the same ones the v3
    audit uses: a radius-2 graph ball, a Euclidean ball, and the closed
    neighbourhood.
    """
    n = len(adj)
    deg = np.array([len(adj[i]) for i in range(n)], dtype=float)
    active = list(active)

    g = np.array([retention(adj, deg, graph_ball_radius2(adj, i)) for i in active])
    e = np.array([retention(adj, deg, euclid_seeds.get(i, [i])) for i in active])
    p = np.array([retention(adj, deg, {i} | adj[i]) for i in active])

    composite = (_ranks(g) + _ranks(e) + _ranks(p)) / 3.0
    k = max(int(round(fraction * len(active))), 1)
    cutoff = np.partition(composite, -k)[-k]
    y = (composite >= cutoff).astype(int)
    return y, composite


def intersection_labels(adj, active, euclid_seeds):
    """The v3 label, for side-by-side comparison."""
    from audit_with_nulls import shared_core_labels
    y, _, _, _ = shared_core_labels(adj, active, euclid_seeds)
    return y
