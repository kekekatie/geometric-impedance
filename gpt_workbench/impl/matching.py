"""
Ratified local conditional-permutation matching law (conditional-null v4.1 §3/§9).

Distance-weighted additive stochastic minimum-cost assignment within each exact-motif group:
  candidate graph = k=32 nearest same-motif standardised-feature neighbours (self excluded);
  cost = feature_distance + lambda*U(0,1), lambda=1.0 (NOT distance*U);
  Policy A: deterministic escalation 32 -> 64 -> full same-motif group (no silent dropping);
  stable keyed seeds; singletons are fixed points; q_ref is the constrained-reference tail.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from . import constants as C

BIG = 1e6


def exact_motif_groups(motif_keys):
    """Groups of size >= 2 (as arrays of vertex indices) and the singleton fraction."""
    g = {}
    for loc, key in enumerate(motif_keys):
        g.setdefault(key, []).append(loc)
    groups = [np.array(v, int) for v in g.values() if len(v) >= 2]
    n_singleton = sum(1 for v in g.values() if len(v) == 1)
    frac = n_singleton / max(len(motif_keys), 1)
    return groups, n_singleton, frac


def cell_permutation_feasible(motif_keys):
    """A patch supports the local permutation null iff singleton fraction <= 5% (physical v7 §7)."""
    _, _, frac = exact_motif_groups(motif_keys)
    return frac <= C.SINGLETON_MAX, frac


def candidate_graph(Xg, k):
    """k nearest same-group standardised-feature neighbours (self excluded); k='full' => complete."""
    from scipy.spatial import cKDTree
    m = len(Xg)
    if k == "full":
        E = [[b for b in range(m) if b != a] for a in range(m)]
        D = [[float(np.linalg.norm(Xg[a] - Xg[b])) for b in range(m) if b != a] for a in range(m)]
        return E, D
    kk = min(k, m - 1)
    dist, nbr = cKDTree(Xg).query(Xg, k=kk + 1)
    E = [[] for _ in range(m)]; D = [[] for _ in range(m)]
    for a in range(m):
        for c in range(kk + 1):
            b = int(nbr[a][c])
            if b != a:
                E[a].append(b); D[a].append(float(dist[a][c]))
    return E, D


def feasible_at(E):
    """Structural feasibility: does a perfect derangement exist in candidate graph E? (rng-free)."""
    m = len(E)
    Cst = np.full((m, m), BIG)
    for a in range(m):
        for b in E[a]:
            Cst[a, b] = 1.0
    r, c = linear_sum_assignment(Cst)
    return Cst[r, c].max() < BIG


def policy_A_k(Xg):
    """Frozen Policy A: smallest escalation k in {32,64,full} at which a derangement exists."""
    for k in C.MATCH_ESCALATION:
        E, _ = candidate_graph(Xg, k)
        if feasible_at(E):
            return k, E
    # 'full' always feasible for group size >= 2
    E, _ = candidate_graph(Xg, "full")
    return "full", E


def assign(E, D, rng, lam=C.MATCH_LAMBDA):
    """Minimum-cost perfect derangement; cost = feature_distance + lam*U(0,1). None if none exists."""
    m = len(E)
    Cst = np.full((m, m), BIG)
    for a in range(m):
        for b, dd in zip(E[a], D[a]):
            Cst[a, b] = dd + lam * rng.random()
    r, c = linear_sum_assignment(Cst)
    if Cst[r, c].max() >= BIG:
        return None
    p = np.empty(m, int); p[r] = c
    return p


def build_permutation(Xstd, motif_keys, key_prefix, b, lam=C.MATCH_LAMBDA):
    """Full-vertex permutation for replicate b under Policy A. Singletons/fixed points map to self.
    key_prefix should carry stable identifiers (family, tier, offset) so seeds are order-stable."""
    from .seeds import address_perm_rng
    n = len(motif_keys)
    perm = np.arange(n)
    groups, _, _ = exact_motif_groups(motif_keys)
    for gi in groups:
        Xg = Xstd[gi]
        k_used, E = policy_A_k(Xg)
        D = candidate_graph(Xg, k_used)[1]
        r = address_perm_rng(*key_prefix, tuple(sorted(map(str, np.atleast_1d(motif_keys[gi[0]]).ravel()))), b)
        p = assign(E, D, r, lam)
        if p is None:                       # cannot happen under Policy A, but never drop silently
            raise RuntimeError("Policy A escalation failed to find a derangement")
        perm[gi] = gi[p]
    return perm


def escalation_fraction(Xstd, motif_keys):
    """Fraction of movable vertices whose group needed k>32 under Policy A (diagnostic; no dropping)."""
    groups, _, _ = exact_motif_groups(motif_keys)
    movable = sum(len(g) for g in groups)
    escalated = 0
    for gi in groups:
        E32, _ = candidate_graph(Xstd[gi], C.MATCH_K)
        if not feasible_at(E32):
            escalated += len(gi)
    return escalated / max(movable, 1)
