#!/usr/bin/env python3
"""
Reverse-Loop Test -- walker, address-residue metric, splice/cycle construction.

ADDRESS RESIDUE (reconstructed metric -- see geometry.py provenance note)
-------------------------------------------------------------------------
The walker accumulates, step by step along its *actual* traversed path, the
perpendicular-space (address) displacement of each edge:

    residue_vec = sum_i ( perp[v_{i+1}] - perp[v_i] )
    residue     = || residue_vec ||

This is the geometry's native address transport. It is computed by literal
stepwise accumulation (not from the endpoints) so that any failure of the
connection to be exact would show up as a route-dependent residue. Because the
perp coordinate is a single-valued function of the vertex in a defect-free
cut-and-project patch, this accumulation telescopes to perp[end]-perp[start];
the experiment measures whether that holds across topologically different routes
and around closed loops, rather than assuming it.

Transit covariates (for Experiment 3) are recorded from the same traversal:
maximum/minimum depth reached, number of depth-zone-boundary crossings, and
steps spent per zone.
"""

import numpy as np
from collections import deque


# --------------------------------------------------------------------------- #
# Graph primitives
# --------------------------------------------------------------------------- #

def bfs(patch, source):
    """Breadth-first search from source. Returns (dist, parent)."""
    n = patch.n
    dist = np.full(n, -1, dtype=np.int64)
    parent = np.full(n, -1, dtype=np.int64)
    dist[source] = 0
    q = deque([source])
    while q:
        u = q.popleft()
        for v in patch.adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    return dist, parent


def bfs_restricted(patch, source, allowed):
    """BFS from source traversing only vertices in `allowed` (a boolean mask).
    Returns (dist, parent)."""
    n = patch.n
    dist = np.full(n, -1, dtype=np.int64)
    parent = np.full(n, -1, dtype=np.int64)
    if not allowed[source]:
        return dist, parent
    dist[source] = 0
    q = deque([source])
    while q:
        u = q.popleft()
        for v in patch.adj[u]:
            if allowed[v] and dist[v] < 0:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    return dist, parent


def reconstruct_path(parent, source, target):
    """Path source..target from a BFS parent array, or None if unreachable."""
    if target != source and parent[target] < 0:
        return None
    path = [target]
    while path[-1] != source:
        path.append(int(parent[path[-1]]))
    path.reverse()
    return path


# --------------------------------------------------------------------------- #
# Address residue + transit covariates
# --------------------------------------------------------------------------- #

def residue_stepwise(patch, path):
    """Accumulate address (perp) displacement step by step along `path`."""
    if len(path) < 2:
        return 0.0, np.zeros(2)
    acc = np.zeros(2)
    perp = patch.perp
    for a, b in zip(path[:-1], path[1:]):
        acc += perp[b] - perp[a]
    return float(np.linalg.norm(acc)), acc


def transit_stats(patch, path):
    """Depth / zone covariates over a traversed path."""
    d = patch.depth[path]
    z = patch.zone[path]
    crossings = int(np.count_nonzero(np.diff(z) != 0))
    steps_per_zone = np.bincount(z, minlength=patch.n_zones).tolist()
    return dict(
        max_transit_depth=float(d.max()),
        min_transit_depth=float(d.min()),
        zone_crossings=crossings,
        steps_per_zone=steps_per_zone,
        deepest_zone=int(z.max()),
        shallowest_zone=int(z.min()),
    )


def directional_balance(patch, path):
    """Net parallel displacement magnitude -- a 'final position' descriptor
    orthogonal to depth (echoes the protocol's 'depth + directional balance')."""
    par = patch.par
    net = par[path[-1]] - par[path[0]]
    return float(np.linalg.norm(net))


# --------------------------------------------------------------------------- #
# Direct path S -> T (Experiment 1 backbone)
# --------------------------------------------------------------------------- #

def sample_direct(patch, rng, L_direct, comp, tol=2):
    """Sample S in `comp`, find T at BFS distance ~ L_direct, return path."""
    for _ in range(200):
        S = int(rng.choice(comp))
        dist, parent = bfs(patch, S)
        cand = np.where((dist >= L_direct - tol) & (dist <= L_direct + tol))[0]
        if len(cand) == 0:
            continue
        T = int(rng.choice(cand))
        path = reconstruct_path(parent, S, T)
        if path is not None and len(path) >= 2:
            return S, T, path, dist, parent
    return None


# --------------------------------------------------------------------------- #
# Cycle construction (splice loops, closed loops)
# --------------------------------------------------------------------------- #

def _random_out_walk(patch, x, steps, rng, step_filter=None):
    """Non-backtracking-ish random walk of `steps` edges from x."""
    path = [x]
    prev = -1
    for _ in range(steps):
        nbrs = patch.adj[path[-1]]
        if step_filter is not None:
            allowed = [v for v in nbrs if step_filter(v)]
            if not allowed:
                allowed = list(nbrs)
        else:
            allowed = list(nbrs)
        # discourage immediate backtrack when alternatives exist
        forward = [v for v in allowed if v != prev]
        pool = forward if forward else allowed
        nxt = int(rng.choice(pool))
        prev = path[-1]
        path.append(nxt)
    return path


def make_cycle(patch, x, target_len, rng, kind, comp_set, max_tries=40):
    """
    Build a closed loop x -> ... -> x of total length ~ target_len that returns
    to x, satisfying a depth-class constraint. Method: random out-walk of
    ~target_len/2 steps (bidirectional stitching, per protocol note 7), then a
    shortest path back to x. Depth class enforced by rejection on the assembled
    loop.

      kind='in_zone'   : every vertex stays in zone(x)
      kind='crossing'  : crosses >=1 zone boundary and returns
      kind='deep_dip'  : reaches the deepest zone reachable from x
      kind='retrace'   : exact out-and-back (positive control, Exp 2)

    Returns (loop_path, method_str) or (None, None).
    """
    zx = patch.zone[x]
    deepest = patch.n_zones - 1
    half = max(1, target_len // 2)

    for attempt in range(max_tries):
        if kind == "in_zone":
            sf = lambda v: patch.zone[v] == zx
            out = _random_out_walk(patch, x, half, rng, step_filter=sf)
            end = out[-1]
            allowed = patch.zone == zx
            dist, parent = bfs_restricted(patch, end, allowed)
            back = reconstruct_path(parent, end, x)
            if back is None:
                continue
            loop = out + back[1:]
            z = patch.zone[loop]
            if len(loop) < 3 or loop[0] != loop[-1] or not np.all(z == zx):
                continue
            return loop, "stitch_in_zone"
        elif kind == "deep_dip":
            # bias toward greater depth
            def sf_deep(v):
                return True
            out = _random_out_walk(patch, x, half, rng)
            # greedy deep segment: from the far end push toward max depth
        elif kind == "crossing":
            out = _random_out_walk(patch, x, half, rng)
        elif kind == "retrace":
            out = _random_out_walk(patch, x, half, rng)
            loop = out + out[-2::-1]
            return loop, "retrace_exact"
        else:
            raise ValueError(kind)

        end = out[-1]
        dist, parent = bfs(patch, end)
        back = reconstruct_path(parent, end, x)
        if back is None:
            continue
        loop = out + back[1:]
        if len(loop) < 3 or loop[0] != loop[-1]:
            continue

        z = patch.zone[loop]
        if kind == "in_zone":
            if not np.all(z == zx):
                continue
        elif kind == "crossing":
            if z.max() == z.min():
                continue
        elif kind == "deep_dip":
            # accept if it reaches the deepest zone available in this patch
            # region; try to steer deeper if not yet there
            if z.max() < deepest:
                # attempt a deeper stitch: walk from x toward deepest vertex
                target_deep = _deepest_near(patch, x, dist_cap=target_len)
                if target_deep is None:
                    continue
                d2, p2 = bfs(patch, x)
                seg1 = reconstruct_path(p2, x, target_deep)
                d3, p3 = bfs(patch, target_deep)
                seg2 = reconstruct_path(p3, target_deep, x)
                if seg1 is None or seg2 is None:
                    continue
                loop = seg1 + seg2[1:]
                z = patch.zone[loop]
                if z.max() < deepest:
                    continue
        return loop, "stitch_bidirectional"
    return None, None


def _deepest_near(patch, x, dist_cap):
    """Vertex of maximum depth within graph distance dist_cap of x."""
    dist, _ = bfs(patch, x)
    within = np.where((dist >= 0) & (dist <= dist_cap))[0]
    if len(within) == 0:
        return None
    return int(within[np.argmax(patch.depth[within])])


def splice(direct_path, cycle):
    """Insert `cycle` (closed loop at vertex X) into `direct_path` at X.
    The cycle's start/end vertex X must appear in direct_path."""
    X = cycle[0]
    idx = direct_path.index(X)
    return direct_path[:idx] + cycle + direct_path[idx + 1:]
