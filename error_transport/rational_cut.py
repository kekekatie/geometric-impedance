#!/usr/bin/env python3
"""
Investigation (sec.4, GPT task #3): a DEFECT-FREE rational-cut periodic
approximant torus.

Motivation. The phason-shear torus (seamless_torus.py) keeps IDEAL positions but
forces periodicity by shearing acceptance -- and carries ~5% distributed phason
defects (VALIDATION_NOTES Finding 2). We showed the defect cannot be removed by a
window tweak on ideal positions: the ideal window UNDERSHOOTS (mean degree 3.84)
and the canonical *sheared* window OVERSHOOTS (mean degree 4.08). They bracket the
required mean-4 but neither lands, because ideal-par + sheared-perp are not a
complementary canonical pair.

The genuine defect-free route is a real cut-and-project onto a RATIONAL plane:
  * E_par' := span_R{M_a, M_b}  (rational, since M_a,M_b are integer period vectors)
  * E_perp' := its orthogonal complement in R^N (dim N-2); perp'(M_a)=perp'(M_b)=0
    EXACTLY, so acceptance is exactly periodic under {M_a,M_b} -- no shear, no wall.
  * window := perp'([-1/2,1/2]^N) = the projected unit cube (the CANONICAL window).
By the canonical-projection theorem this is a perfect rhombus tiling (mean degree
exactly 4, zero missing edges) and it is periodic. Positions move off the ideal QC
by O(1/q^2) and edge lengths take a few discrete rhombus values (no longer exactly
1), but winding stays exact. Origin K=0 is always an accepted seed (perp'=0, the
window centre).

Construction + validation only. No walkers, no transport.
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))
import numpy as np
from collections import deque, Counter
from scipy.linalg import null_space
from scipy.spatial import ConvexHull
from geometry import star_vectors, SUBSTRATES

REG = json.load(open(Path(__file__).parent.parent /
                     "defect_holonomy_test" / "phase0_registration.json"))
HERE = Path(__file__).parent
EPS = 1e-6


class RationalCutTorus:
    def __init__(self, substrate, order_index, win_scale=1.0):
        cfg = SUBSTRATES[substrate]
        self.substrate = substrate
        self.N = N = cfg["N"]
        self.par_star, self.perp_star = star_vectors(
            N, cfg["par_step"], cfg["perp_step"])
        o = REG[substrate]["orders"][order_index]
        self.order = o["order"]; self.convergent = o["convergent"]
        self.M_a = np.array(o["M_a"], float); self.M_b = np.array(o["M_b"], float)
        self.P_a = self.M_a @ self.par_star
        self.P_b = self.M_b @ self.par_star
        self.Mcell = np.array([self.P_a, self.P_b]).T
        self.Minv = np.linalg.inv(self.Mcell)
        # rational split: E_par' = span{M_a,M_b}; E_perp' = orthogonal complement
        U = np.array([self.M_a, self.M_b])           # (2,N)
        self.G = U @ U.T
        self.Ginv = np.linalg.inv(self.G)
        self.U = U
        F = null_space(U)                            # (N, N-2) orthonormal
        self.F = F
        # canonical window = projected unit cube in perp' (N-2 dims)
        gens = F.T * win_scale                        # (N-2, N): columns g_j=F[j]
        signs = np.array(np.meshgrid(*[[-0.5, 0.5]] * N)).reshape(N, -1).T
        cube_pts = signs @ gens.T                     # (2^N, N-2)
        self._win_pts = cube_pts
        if F.shape[1] == 2:
            self._hull = ConvexHull(cube_pts)
        else:
            self._hull = ConvexHull(cube_pts)
        self._eq = self._hull.equations               # (faces, N-2+1)
        self._build()

    def _perp(self, K):
        return self.F.T @ K

    def _accept(self, K):
        p = self.F.T @ K
        return bool(np.all(self._eq[:, :-1] @ p + self._eq[:, -1] <= 1e-9))

    def _parcoords(self, K):
        return self.Ginv @ (self.U @ K)               # (a,b): proj onto E_par'

    def _pos(self, K):
        a, b = self.Ginv @ (self.U @ K)
        return a * self.P_a + b * self.P_b

    def _fold(self, par):
        frac = self.Minv @ par
        ci = np.floor(frac + EPS).astype(int)
        return ci, tuple(np.round(frac - ci, 5).tolist())

    def _incell(self, K, ci):
        return K - ci[0] * self.M_a - ci[1] * self.M_b

    def _build(self):
        N = self.N
        eye = np.eye(N)
        seed = np.zeros(N)                             # origin is accepted
        ci0, _ = self._fold(self._pos(seed))
        seed = self._incell(seed, ci0)
        _, fk0 = self._fold(self._pos(seed))
        nodes = {fk0: 0}; nodeK = [seed]
        nodePos = [self._pos(seed)]
        directed = []
        dq = deque([0])
        edge_lengths = []
        while dq:
            u = dq.popleft(); K = nodeK[u]; xu = nodePos[u]
            for k in range(N):
                for s in (1.0, -1.0):
                    K2 = K + s * eye[k]
                    if not self._accept(K2):
                        continue
                    x2 = self._pos(K2)
                    ci2, fk2 = self._fold(x2)
                    v = nodes.get(fk2)
                    if v is None:
                        v = len(nodeK); nodes[fk2] = v
                        Kin = self._incell(K2, ci2)
                        nodeK.append(Kin); nodePos.append(self._pos(Kin))
                        dq.append(v)
                    directed.append((u, v, tuple(int(c) for c in ci2)))
                    edge_lengths.append(float(np.linalg.norm(x2 - xu)))
        self.nodes = nodes
        self.node_K = np.array(nodeK)
        self.node_par = np.array(nodePos)
        self.n = len(nodeK)
        self.directed = directed
        self.edge_lengths = np.array(edge_lengths)


def validate(substrate, order_index, verbose=True):
    T = RationalCutTorus(substrate, order_index)
    N = T.N
    res = dict(substrate=substrate, order=T.order, convergent=T.convergent,
               construction="rational_cut", n_nodes=T.n)
    # antisymmetry / self-loops / dupes
    dset = {}; self_loops = 0; dup = 0
    for u, v, w in T.directed:
        if u == v:
            self_loops += 1
        key = (u, v, tuple(w))
        if key in dset:
            dup += 1
        dset[key] = True
    antisym = sum((v, u, tuple((-np.array(w)).tolist())) not in dset
                  for (u, v, w) in dset)
    res["reverse_winding_antisymmetry"] = bool(antisym == 0)
    res["self_loops"] = self_loops
    res["duplicate_directed_edges"] = dup
    # degree
    deg = Counter(); seen = set()
    for u, v, w in T.directed:
        k = (min(u, v), max(u, v),
             tuple(sorted((tuple(w), tuple((-np.array(w)).tolist())))))
        if k in seen:
            continue
        seen.add(k); deg[u] += 1; deg[v] += 1
    degv = np.array([deg[i] for i in range(T.n)])
    res["mean_degree"] = round(float(degv.mean()), 6)
    res["degree_hist"] = dict(sorted(Counter(degv.tolist()).items()))
    res["max_coordination"] = int(degv.max())
    res["min_coordination"] = int(degv.min())
    res["max_coordination_expected"] = 7 if substrate == "penrose" else 8
    # connectivity
    adj = [[] for _ in range(T.n)]
    for u, v, w in T.directed:
        adj[u].append(v)
    vis = np.zeros(T.n, bool); dq = deque([0]); vis[0] = True; c = 1
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if not vis[v]:
                vis[v] = True; c += 1; dq.append(v)
    res["connected"] = bool(c == T.n)
    # winding closure
    lift = {0: np.zeros(2, int)}; dq = deque([0]); dmap = {}
    for u, v, w in T.directed:
        dmap.setdefault(u, []).append((v, np.array(w)))
    while dq:
        u = dq.popleft()
        for v, w in dmap.get(u, []):
            if v not in lift:
                lift[v] = lift[u] + w; dq.append(v)
    cyc = set()
    for u, v, w in T.directed:
        if u in lift and v in lift:
            h = tuple((lift[u] + np.array(w) - lift[v]).tolist())
            if h != (0, 0):
                cyc.add(h)
    res["closure_both_generators"] = bool(
        any(a != 0 for a, b in cyc) and any(b != 0 for a, b in cyc))
    # edge-length spectrum (rhombus edges -> few discrete values)
    L = T.edge_lengths
    res["edge_length_mean"] = round(float(L.mean()), 4)
    res["edge_length_min"] = round(float(L.min()), 4)
    res["edge_length_max"] = round(float(L.max()), 4)
    res["distinct_edge_lengths"] = int(len(np.unique(np.round(L, 3))))
    # DEFECT-FREE test: mean degree exactly 4 (Euler) and no missing edges
    n_edges = len(seen)
    res["undirected_edges"] = n_edges
    res["expected_edges_defect_free"] = 2 * T.n
    res["missing_edges"] = 2 * T.n - n_edges
    res["mean_degree_deficit"] = round(4.0 - float(degv.mean()), 6)
    res["DEFECT_FREE"] = bool(res["missing_edges"] == 0 and
                              abs(res["mean_degree"] - 4.0) < 1e-9)
    res["faithful_coordination"] = bool(
        degv.max() <= res["max_coordination_expected"])
    res["GATE_PASS"] = bool(res["reverse_winding_antisymmetry"] and
                            self_loops == 0 and dup == 0 and res["connected"] and
                            res["closure_both_generators"])
    if verbose:
        print(f"\n=== rational-cut  {substrate} order {T.order} "
              f"({T.convergent}) ===  nodes={T.n}")
        print(f"  antisym {res['reverse_winding_antisymmetry']} | "
              f"self-loops {self_loops} | dupes {dup} | "
              f"connected {res['connected']} | winding-closure "
              f"{res['closure_both_generators']}  -> GATE "
              f"{'PASS' if res['GATE_PASS'] else 'FAIL'}")
        print(f"  DEFECT-FREE: {res['DEFECT_FREE']}  (mean degree "
              f"{res['mean_degree']} vs 4, missing edges {res['missing_edges']})")
        print(f"  coordination {res['min_coordination']}..{res['max_coordination']} "
              f"(faithful <= {res['max_coordination_expected']}: "
              f"{res['faithful_coordination']})")
        print(f"  degree hist: {res['degree_hist']}")
        print(f"  edge lengths: {res['distinct_edge_lengths']} distinct in "
              f"[{res['edge_length_min']}, {res['edge_length_max']}], "
              f"mean {res['edge_length_mean']}")
    return res


if __name__ == "__main__":
    out = {}
    for sub, oi in [("ammann_beenker", 2), ("ammann_beenker", 3),
                    ("penrose", 2), ("penrose", 3)]:
        out.setdefault(sub, []).append(validate(sub, oi))
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "rational_cut_validation.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n-> results/rational_cut_validation.json")
