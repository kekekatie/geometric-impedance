#!/usr/bin/env python3
"""
CONFIRMATORY run for the SEALED PREREG_transport_hierarchy.md.

Per-vertex observable (coherent LDOS in a fixed window; incoherent return-prob null)
regressed on nested feature sets M0..M4, held-out-offset CV. Decisive quantity: the
M4-over-M3 increment, and whether the STRATIFIED address shuffle (within M3 bins,
M4 recomputed) kills it. Same regressor for every rung and both engines.

Nothing here is tuned to the outcome: features, windows (|E| in [0.8,2.5] primary,
|E|<=0.2 secondary), incoherent times {5,10,20}, bulk mask r<0.8 r_max, and the
regressor are all fixed by the sealed pre-reg / this harness before the run.
"""

import sys
from collections import deque, Counter

import numpy as np
from scipy.spatial import ConvexHull, cKDTree
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure, frame
from rank4_headline import EXTENT

NAME = {8: "silver", 10: "golden", 12: "platinum"}
OFFSETS = [(0.31, 0.19), (0.07, 0.41), (0.23, 0.05), (0.44, 0.28), (0.16, 0.33)]
WIN_PRIMARY = (0.8, 2.5)
WIN_SECONDARY = (0.0, 0.2)
RW_TIMES = (5, 10, 20)
GBT = dict(max_depth=3, max_iter=250, learning_rate=0.06, l2_regularization=1.0,
           random_state=0)


# --------------------------------------------------------------------------- #
def adjacency_list(n, E):
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    return adj


def ball_shells(adj, src, rmax):
    """Graph-distance ball memberships: dist[v] for v within rmax of src (BFS)."""
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        if dist[u] == rmax:
            continue
        for w in adj[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                q.append(w)
    return dist


def hull_depth(perp):
    """Signed distance of each perp point to the boundary of the address point cloud."""
    h = ConvexHull(perp)
    A, b = h.equations[:, :-1], h.equations[:, -1]          # A x + b <= 0 inside
    return -(perp @ A.T + b).max(axis=1)                    # >0 inside = depth


def build_features(N, offset):
    st = structure(N)
    star, par4 = st["star"], st["par4"]
    lifts, par, perp, ustar = generate(N, EXTENT[N], offset=np.array(offset))
    n = len(par)
    E = build_edges(lifts, N, ustar)
    adj = adjacency_list(n, E)
    deg = np.array([len(adj[i]) for i in range(n)], float)
    tree = cKDTree(par)

    # incident edge geometry
    star_par = star @ par4
    ang_of = {}                                            # (i,j) undirected -> not needed
    edge_len_mean = np.zeros(n); edge_len_var = np.zeros(n)
    psi = {nn: np.zeros(n) for nn in (N, N // 2, 2 * N)}
    for i in range(n):
        if not adj[i]:
            continue
        d = par[adj[i]] - par[i]
        L = np.linalg.norm(d, axis=1)
        edge_len_mean[i] = L.mean(); edge_len_var[i] = L.var()
        th = np.arctan2(d[:, 1], d[:, 0])
        for nn in psi:
            psi[nn][i] = np.abs(np.exp(1j * nn * th).mean())

    # local vertex density and radial counts g(r)
    def gcount(r):
        return np.array(tree.query_ball_point(par, r, return_length=True), float)
    dens = gcount(2.0)
    g_small = [gcount(1.6), gcount(2.6)]
    g_med = [gcount(4.0), gcount(6.0)]

    # motif type: canonical multiset of incident star (line, sign) -> KEY (global
    # codebook is built later so one-hot width is consistent across offsets)
    idx = {tuple(r): k for k, r in enumerate(lifts)}
    motif_keys = []
    for i in range(n):
        sig = []
        for k, s in enumerate(star):
            for sign in (1, -1):
                if tuple(lifts[i] + sign * s) in idx:
                    sig.append((k, sign))
        motif_keys.append(tuple(sorted(sig)))

    shell_r = (2, 4, 8)

    # coherent LDOS (primary + secondary window) and incoherent return prob
    A = np.zeros((n, n))
    for i, j in E:
        A[i, j] = A[j, i] = 1.0
    evals, evecs = np.linalg.eigh(A)
    w2 = evecs**2
    def ldos(lo, hi):
        m = (np.abs(evals) >= lo) & (np.abs(evals) <= hi)
        return w2[:, m].sum(1)
    ld_primary = ldos(*WIN_PRIMARY)
    ld_secondary = ldos(*WIN_SECONDARY)
    P = A / deg[:, None]
    ret = {}
    want = set(RW_TIMES)
    Pcur = np.eye(n)
    for t in range(1, max(RW_TIMES) + 1):
        Pcur = Pcur @ P
        if t in want:
            ret[t] = np.diag(Pcur).copy()

    R = np.hypot(par[:, 0], par[:, 1])
    bulk = R < 0.8 * R.max()
    return dict(N=N, n=n, bulk=bulk, perp=perp, adj=adj, par=par, tree=tree,
                shell_r=shell_r, deg=deg, dens=dens, edge_len_mean=edge_len_mean,
                edge_len_var=edge_len_var, g_small=g_small, g_med=g_med,
                psi=psi, motif_keys=motif_keys,
                ld_primary=ld_primary, ld_secondary=ld_secondary, ret=ret)


def _m4_cols(f, perp_field):
    """Raw M4 columns: shell-averaged perp, perp variance, gradient, hull depth."""
    n, adj, tree, par, shell_r = f["n"], f["adj"], f["tree"], f["par"], f["shell_r"]
    sm = {r: np.zeros((n, 2)) for r in shell_r}
    sv = {r: np.zeros(n) for r in shell_r}
    gr = np.zeros(n)
    for i in range(n):
        dist = ball_shells(adj, i, max(shell_r))
        members = np.array(sorted(dist)); dd = np.array([dist[v] for v in members])
        for r in shell_r:
            sel = members[dd <= r]
            sm[r][i] = perp_field[sel].mean(0); sv[r][i] = perp_field[sel].var(0).sum()
        nb = tree.query_ball_point(par[i], 3.0)
        if len(nb) >= 4:
            X = np.column_stack([par[nb] - par[i], np.ones(len(nb))])
            coef, *_ = np.linalg.lstsq(X, perp_field[nb], rcond=None)
            gr[i] = np.linalg.norm(coef[:2])
    dpt = hull_depth(perp_field)
    cols = []
    for r in shell_r:
        cols.append(sm[r]); cols.append(sv[r][:, None])
    cols.append(gr[:, None]); cols.append(dpt[:, None])
    return np.column_stack(cols)


def assemble(f, codebook, rng=None):
    """Build M0..M4 (sealed) + M4shuf (stratified-shuffle kill) + M3pos/M4pos
    (EXPLORATORY physical-position control: is M4 still additive over M3 plus
    physical coordinates (x, y, r)? guards a smooth-position confound)."""
    n = f["n"]
    M0 = np.column_stack([f["dens"]])
    M1 = np.column_stack([M0, f["deg"], f["edge_len_mean"], f["edge_len_var"]])
    oh = np.zeros((n, len(codebook)))
    for i, k in enumerate(f["motif_keys"]):
        oh[i, codebook[k]] = 1.0
    motif_code = np.array([codebook[k] for k in f["motif_keys"]])
    M2 = np.column_stack([M1, oh, f["g_small"][0], f["g_small"][1]])
    N = f["N"]
    M3 = np.column_stack([M2, f["psi"][N], f["psi"][N // 2], f["psi"][2 * N],
                          f["g_med"][0], f["g_med"][1]])
    m4 = _m4_cols(f, f["perp"])
    M4 = np.column_stack([M3, m4])
    # stratified shuffle: motif_code x degree-decile, perp permuted within bins
    deg = f["deg"]
    dec = np.clip((deg.argsort().argsort() * 10 // n), 0, 9)
    m3bin = motif_code * 10 + dec
    sp = f["perp"].copy()
    order = np.argsort(m3bin)
    for grp in np.split(order, np.unique(m3bin[order], return_index=True)[1][1:]):
        if len(grp) > 1:
            sp[grp] = f["perp"][grp][rng.permutation(len(grp))]
    M4shuf = np.column_stack([M3, _m4_cols(f, sp)])
    # exploratory physical-position control
    par = f["par"]
    posc = np.column_stack([par, np.hypot(par[:, 0], par[:, 1])])
    M3pos = np.column_stack([M3, posc])
    M4pos = np.column_stack([M3pos, m4])
    return dict(M0=M0, M1=M1, M2=M2, M3=M3, M4=M4, M4shuf=M4shuf,
                M3pos=M3pos, M4pos=M4pos)


def held_out_r2(blocks, y, bulk_list, rung):
    """Leave-one-offset-out CV R^2 for a given feature rung across offsets."""
    scores = []
    K = len(blocks)
    for test in range(K):
        Xtr = np.vstack([blocks[o][rung][bulk_list[o]] for o in range(K) if o != test])
        ytr = np.concatenate([y[o][bulk_list[o]] for o in range(K) if o != test])
        Xte = blocks[test][rung][bulk_list[test]]
        yte = y[test][bulk_list[test]]
        mdl = HistGradientBoostingRegressor(**GBT)
        mdl.fit(Xtr, ytr)
        scores.append(r2_score(yte, mdl.predict(Xte)))
    return np.mean(scores), np.std(scores)


def run_family(N):
    feats = [build_features(N, off) for off in OFFSETS]
    bulk_list = [f["bulk"] for f in feats]
    rng = np.random.default_rng(0)
    # shared motif codebook across offsets so one-hot width is consistent
    codebook = {}
    for f in feats:
        for k in f["motif_keys"]:
            codebook.setdefault(k, len(codebook))
    B = [assemble(f, codebook, rng) for f in feats]

    out = {}
    for label, key in (("coherent-primary", "ld_primary"),
                       ("coherent-secondary", "ld_secondary"),
                       ("incoherent-t10", None)):
        y = ([f["ret"][10] for f in feats] if key is None
             else [f[key] for f in feats])
        rungs = {}
        for r in ("M0", "M1", "M2", "M3", "M4", "M4shuf", "M3pos", "M4pos"):
            rungs[r] = held_out_r2(B, y, bulk_list, r)
        out[label] = rungs
    return out, feats


def main(families=(8, 10, 12)):
    for N in families:
        out, feats = run_family(N)
        nb = sum(int(f["bulk"].sum()) for f in feats)
        print(f"\n{'='*72}\n{NAME[N]} (N={N})  {len(OFFSETS)} offsets  "
              f"{nb} bulk vertices total\n{'='*72}")
        for label, rungs in out.items():
            print(f"  {label}:")
            for r in ("M0", "M1", "M2", "M3", "M4", "M4shuf", "M3pos", "M4pos"):
                mu, sd = rungs[r]
                print(f"     {r:7s} R2 = {mu:+.4f} ± {sd:.4f}")
            dm = rungs["M4"][0] - rungs["M3"][0]
            ds = rungs["M4shuf"][0] - rungs["M3"][0]
            dp = rungs["M4pos"][0] - rungs["M3pos"][0]
            print(f"     --> M4-over-M3 increment = {dm:+.4f}   "
                  f"(stratified-shuffle = {ds:+.4f};  M4-over-M3+position = {dp:+.4f})")


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (8, 10, 12)
    main(fams)
