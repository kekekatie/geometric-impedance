#!/usr/bin/env python3
"""
Partition granularity: how far can a perpendicular coordinate move before the
local environment it encodes changes?

In cut-and-project the perpendicular coordinate determines a vertex's local
environment exactly, so the acceptance window partitions into regions of constant
environment. If those regions are large, a vertex can be jittered a long way
without its relational meaning changing; if small, meaning changes almost
immediately. That quantity is a code distance, not an analogy to one.

Measured per vertex as the perpendicular-space distance to the nearest vertex of
a different environment class, normalised by the window's characteristic radius
so substrates with different window sizes remain comparable.
"""
import numpy as np
from scipy.spatial import cKDTree


def environment_classes(n_vertices, edges, mode="degree_signature"):
    """Local environment class per vertex."""
    adj = [[] for _ in range(n_vertices)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    deg = np.array([len(a) for a in adj])
    if mode == "degree":
        return deg
    sig = [(deg[i], tuple(sorted(deg[j] for j in adj[i]))) for i in range(n_vertices)]
    lookup = {s: k for k, s in enumerate(sorted(set(sig)))}
    return np.array([lookup[s] for s in sig])


def margins(perp, classes, interior_mask=None):
    """Perp-space distance from each vertex to the nearest differently-classed one."""
    tree = cKDTree(perp)
    idx = np.arange(len(perp)) if interior_mask is None else np.where(interior_mask)[0]
    out = np.full(len(idx), np.nan)
    k = 2
    todo = np.arange(len(idx))
    while len(todo) and k <= min(len(perp), 512):
        d, j = tree.query(perp[idx[todo]], k=k)
        for row, t in enumerate(todo):
            diff = np.where(classes[j[row]] != classes[idx[t]])[0]
            if len(diff):
                out[t] = d[row, diff[0]]
        todo = todo[np.isnan(out[todo])]
        k *= 4
    return out


def granularity(perp, edges, par=None, interior=0.5, mode="degree_signature"):
    """Return normalised granularity statistics for one substrate."""
    n = len(perp)
    classes = environment_classes(n, edges, mode)
    mask = np.ones(n, bool)
    if par is not None and interior < 1.0:
        r = np.linalg.norm(par - par.mean(0), axis=1)
        mask = r <= np.quantile(r, interior)
    m = margins(perp, classes, mask)
    m = m[~np.isnan(m)]

    # Perp-space sampling density differs between substrates, and the raw margin
    # scales with it. Normalise by the typical nearest-neighbour spacing so the
    # measure reads "how many neighbours away is the nearest different class",
    # which is density-free. Normalising by window radius alone does not fix this.
    tree = cKDTree(perp)
    nn = tree.query(perp[mask], k=2)[0][:, 1]
    spacing = float(np.median(nn))
    scale = float(np.mean(np.linalg.norm(perp - perp.mean(0), axis=1)))
    return {"n_classes": int(classes.max() + 1),
            "margin_median": float(np.median(m)),
            "nn_spacing": spacing,
            "granularity": float(np.median(m) / spacing),   # headline: density-free
            "by_window_radius": float(np.median(m) / scale),
            "window_radius": scale,
            "n_measured": int(len(m))}


def purity(perp, edges, par=None, interior=0.5, mode="degree", ks=(4, 8, 16, 32)):
    """Fraction of a vertex's k nearest perpendicular neighbours sharing its class.

    The distance-to-nearest-different-class measure saturates: with a fine class
    definition every nearest perpendicular neighbour already differs, so every
    substrate returns 1.0 and nothing is resolved. Purity degrades smoothly with
    k instead, and its decay rate is the granularity: a coarse partition keeps
    neighbours on-class out to large k, a fine one loses them immediately.
    """
    n = len(perp)
    classes = environment_classes(n, edges, mode)
    mask = np.ones(n, bool)
    if par is not None and interior < 1.0:
        r = np.linalg.norm(par - par.mean(0), axis=1)
        mask = r <= np.quantile(r, interior)
    tree = cKDTree(perp)
    idx = np.where(mask)[0]
    out = {}
    for k in ks:
        _, j = tree.query(perp[idx], k=k + 1)
        same = (classes[j[:, 1:]] == classes[idx][:, None]).mean()
        out[f"purity_k{k}"] = float(same)
    base = float(np.bincount(classes[idx]).max() / len(idx))   # chance level
    out["chance"] = base
    out["n_classes"] = int(classes.max() + 1)
    out["purity_excess_k8"] = out["purity_k8"] - base
    return out
