#!/usr/bin/env python3
"""
substrate_lib.py -- de Bruijn pentagrid rhombus tilings + validation + reader.

Construction & feasibility support for the v9/v10 substrate comparison. NO
production dynamics here; a tiny smoke fixture lives in v10_build.py.

Mathematical basis
------------------
N.G. de Bruijn, "Algebraic theory of Penrose's non-periodic tilings of the plane"
(Nederl. Akad. Wetensch. Indag. Math. 43 (1981) 39-66). The *pentagrid*: five
families j=0..4 of equally spaced parallel lines, family j normal to the unit
vector e_j = (cos 2*pi*j/5, sin 2*pi*j/5), line n of family j at
    e_j . x = n + gamma_j                         (regular spacing)
The dual of the line arrangement is a rhombus tiling. Each intersection of a line
of family r with a line of family s (r != s) maps to a rhombus whose edges are the
unit vectors e_r, e_s, hence all sides length 1; the rhombus is 'thick' (72 deg)
when |r-s| in {1,4} (mod 5) and 'thin' (36 deg) when |r-s| in {2,3}. A tiling
vertex is  V = sum_j K_j(x) e_j  with integer strip indices K_j.

de Bruijn's regularity/Penrose conditions (used here):
  * REGULAR pentagrid: no point lies on >=3 lines simultaneously (generic offsets).
  * PENROSE: the offsets satisfy sum_j gamma_j in Z (de Bruijn Sec. 5). We use an
    offset vector with sum 0 that is symmetric under j -> -j (mod 5), giving a
    Penrose tiling with an exact mirror line (the x-axis).

PERTURBED arm: we replace the regular line positions n + gamma_j by
    P_{j,n} = n + gamma_j + delta_{j,n},   delta ~ Uniform(-A, A), A < 0.5
(fixed seed), keeping each family's positions strictly increasing in n. Because the
rhombus *shapes* depend only on the fixed inter-family angles, every face is still
one of the same two unit rhombi; only the *arrangement* changes. We call this a
"perturbed pentagrid" and DO NOT claim it is disordered / lacks long-range order:
bounded jitter is not established to destroy quasiperiodic order (that would need a
diffraction / structure-factor argument, deferred).
"""
from __future__ import annotations

import math
from collections import defaultdict, deque

import numpy as np

PHI = (1.0 + 5.0 ** 0.5) / 2.0
E = np.array([[math.cos(2 * math.pi * j / 5), math.sin(2 * math.pi * j / 5)]
              for j in range(5)])          # unit normals e_0..e_4
# offsets: sum 0, symmetric under j->-j (mod5): gamma = (g0, g1, g2, g2, g1)
DEFAULT_OFFSETS = np.array([0.30, 0.10, -0.25, -0.25, 0.10])   # sum = 0.0
ROUND = 6                                    # vertex coordinate rounding for dedup


def _rhombus_shape(r, s):
    d = min((r - s) % 5, (s - r) % 5)
    return "thick" if d == 1 else "thin"     # d in {1,2}


class Substrate:
    """A finite rhombus-tiling patch as a graph with faces."""

    def __init__(self, mode, radius, offsets, jitter_amp, seed):
        self.mode = mode
        self.radius = radius
        self.offsets = np.asarray(offsets, float)
        self.jitter_amp = jitter_amp
        self.seed = seed
        self.pos = {}                        # vid -> (x, y)
        self.vid = {}                        # rounded coord -> vid
        self.base_edges = set()              # frozenset{u, v}
        self.faces = []                      # list of dict
        self.adj = defaultdict(set)          # original-graph adjacency
        self.edge_faces = defaultdict(list)  # edge (u<v) -> [face idx]
        self._build()

    # ---- construction -----------------------------------------------------
    def _line_positions(self, rng):
        M = int(math.ceil(self.radius)) + 3
        ns = np.arange(-M, M + 1)
        P = {}
        for j in range(5):
            p = ns + self.offsets[j]
            if self.jitter_amp > 0:
                p = p + rng.uniform(-self.jitter_amp, self.jitter_amp, size=p.shape)
                assert np.all(np.diff(p) > 0), "perturbation broke line ordering"
            P[j] = p
        return P

    def _get_vid(self, point):
        key = (round(point[0], ROUND), round(point[1], ROUND))
        if key not in self.vid:
            vid = len(self.pos)
            self.vid[key] = vid
            self.pos[vid] = np.array(key)
        return self.vid[key]

    def _build(self):
        rng = np.random.default_rng(self.seed)
        P = self._line_positions(rng)
        eps = 1e-4
        seen_faces = set()
        for r in range(5):
            for s in range(r + 1, 5):
                A = np.array([E[r], E[s]])
                Ainv = np.linalg.inv(A)
                for Pr in P[r]:
                    for Ps in P[s]:
                        x = Ainv @ np.array([Pr, Ps])
                        if x[0] * x[0] + x[1] * x[1] > (self.radius + 2.0) ** 2:
                            continue
                        corners = []
                        for sr in (-1, 1):
                            for ss in (-1, 1):
                                y = Ainv @ np.array([Pr + sr * eps, Ps + ss * eps])
                                K = np.array([np.searchsorted(P[j], E[j] @ y,
                                                              side="right")
                                              for j in range(5)])
                                v = (K[:, None] * E).sum(axis=0)
                                corners.append(v)
                        # order (-,-),(+,-),(+,+),(-,+) -> proper rhombus cycle
                        order = [corners[0], corners[2], corners[3], corners[1]]
                        if any(np.hypot(*c) > self.radius for c in order):
                            continue
                        vids = tuple(self._get_vid(c) for c in order)
                        if len(set(vids)) != 4:
                            continue
                        if _poly_area(order) < 0:        # normalise to CCW
                            order = order[::-1]
                            vids = vids[::-1]
                        fkey = frozenset(vids)
                        if fkey in seen_faces:
                            continue
                        seen_faces.add(fkey)
                        fedges = [tuple(sorted((vids[i], vids[(i + 1) % 4])))
                                  for i in range(4)]
                        diags = [tuple(sorted((vids[0], vids[2]))),
                                 tuple(sorted((vids[1], vids[3])))]
                        fidx = len(self.faces)
                        self.faces.append({"verts": vids, "edges": fedges,
                                           "diagonals": diags,
                                           "shape": _rhombus_shape(r, s),
                                           "families": (r, s)})
                        for e in fedges:
                            self.base_edges.add(e)
                            self.edge_faces[e].append(fidx)
                            self.adj[e[0]].add(e[1])
                            self.adj[e[1]].add(e[0])
        self._keep_main_component()

    def _keep_main_component(self):
        if not self.pos:
            return
        start = min(self.pos, key=lambda v: np.hypot(*self.pos[v]))
        seen = {start}
        q = deque([start])
        while q:
            x = q.popleft()
            for y in self.adj[x]:
                if y not in seen:
                    seen.add(y); q.append(y)
        if len(seen) == len(self.pos):
            return
        # rebuild keeping only the main component
        keep = seen
        old_faces = [f for f in self.faces if all(v in keep for v in f["verts"])]
        remap = {}
        newpos = {}
        for v in sorted(keep):
            remap[v] = len(newpos); newpos[len(newpos)] = self.pos[v]
        self.pos = newpos
        self.vid = {(round(p[0], ROUND), round(p[1], ROUND)): i
                    for i, p in self.pos.items()}
        self.base_edges = set(); self.adj = defaultdict(set)
        self.edge_faces = defaultdict(list); self.faces = []
        for f in old_faces:
            vids = tuple(remap[v] for v in f["verts"])
            fedges = [tuple(sorted((vids[i], vids[(i + 1) % 4]))) for i in range(4)]
            diags = [tuple(sorted((vids[0], vids[2]))),
                     tuple(sorted((vids[1], vids[3])))]
            fidx = len(self.faces)
            self.faces.append({"verts": vids, "edges": fedges, "diagonals": diags,
                               "shape": f["shape"], "families": f["families"]})
            for e in fedges:
                self.base_edges.add(e); self.edge_faces[e].append(fidx)
                self.adj[e[0]].add(e[1]); self.adj[e[1]].add(e[0])

    # ---- summaries --------------------------------------------------------
    @property
    def V(self):
        return len(self.pos)

    @property
    def Ecount(self):
        return len(self.base_edges)

    @property
    def F(self):
        return len(self.faces)

    def boundary_edges(self):
        return [e for e, fs in self.edge_faces.items() if len(fs) == 1]

    def boundary_vertices(self):
        bv = set()
        for e in self.boundary_edges():
            bv.add(e[0]); bv.add(e[1])
        return bv

    def degree_hist(self):
        h = defaultdict(int)
        for v in self.pos:
            h[len(self.adj[v])] += 1
        return dict(sorted(h.items()))

    def shape_counts(self):
        c = defaultdict(int)
        for f in self.faces:
            c[f["shape"]] += 1
        return dict(c)

    def graph_bfs_dist(self, source):
        dist = {source: 0}
        q = deque([source])
        while q:
            x = q.popleft()
            for y in self.adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1; q.append(y)
        return dist

    def boundary_distance(self):
        """graph distance from every vertex to the nearest boundary vertex."""
        bv = self.boundary_vertices()
        dist = {v: 0 for v in bv}
        q = deque(bv)
        while q:
            x = q.popleft()
            for y in self.adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1; q.append(y)
        return dist


# ---------------------------------------------------------------------------
# Construction convenience
# ---------------------------------------------------------------------------
def make_regular(radius=6.0, offsets=DEFAULT_OFFSETS, seed=0):
    return Substrate("regular", radius, offsets, 0.0, seed)


def make_perturbed(radius=6.0, offsets=DEFAULT_OFFSETS, jitter_amp=0.30, seed=0):
    return Substrate("perturbed", radius, offsets, jitter_amp, seed)


# ---------------------------------------------------------------------------
# Validation (geometry AND topology)
# ---------------------------------------------------------------------------
def _poly_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def validate(sub, tol=1e-6):
    checks = {}
    # 1. unit sides
    max_side_err = 0.0
    for e in sub.base_edges:
        d = np.hypot(*(sub.pos[e[0]] - sub.pos[e[1]]))
        max_side_err = max(max_side_err, abs(d - 1.0))
    checks["unit_sides (max|len-1|)"] = (max_side_err < 1e-6, max_side_err)
    # 2. permitted rhombus shapes: edges are two directions from +-E, area matches
    exp_area = {"thick": math.sin(2 * math.pi / 5), "thin": math.sin(math.pi / 5)}
    bad_shape = 0; max_area_err = 0.0; oriented = 0
    for f in sub.faces:
        pts = [sub.pos[v] for v in f["verts"]]
        ar = _poly_area(pts)
        oriented += (ar > 0)
        max_area_err = max(max_area_err, abs(abs(ar) - exp_area[f["shape"]]))
        # edge direction check: 4 edges use exactly 2 distinct axis directions
        dirs = set()
        for i in range(4):
            d = sub.pos[f["verts"][(i + 1) % 4]] - sub.pos[f["verts"][i]]
            k = int(np.argmin([min(np.hypot(*(d - E[j])), np.hypot(*(d + E[j])))
                               for j in range(5)]))
            dirs.add(k)
        if len(dirs) != 2:
            bad_shape += 1
    checks["rhombus_shapes_ok"] = (bad_shape == 0, bad_shape)
    checks["face_areas (max err)"] = (max_area_err < 1e-6, max_area_err)
    checks["faces_CCW_oriented"] = (oriented == sub.F, f"{oriented}/{sub.F}")
    # 3. incidence: interior edge in 2 faces, boundary in 1
    bad_inc = sum(1 for e, fs in sub.edge_faces.items() if len(fs) not in (1, 2))
    checks["edge_incidence (<=2 faces)"] = (bad_inc == 0, bad_inc)
    # 4. connectedness
    comp = len(sub.graph_bfs_dist(next(iter(sub.pos))))
    checks["connected"] = (comp == sub.V, f"{comp}/{sub.V}")
    # 5. boundary loops: every boundary vertex has exactly 2 boundary edges
    bdeg = defaultdict(int)
    for e in sub.boundary_edges():
        bdeg[e[0]] += 1; bdeg[e[1]] += 1
    bad_loop = sum(1 for v, d in bdeg.items() if d != 2)
    checks["boundary_is_loops"] = (bad_loop == 0, bad_loop)
    # 6. Euler: V - E + F = 1 (disk; F = interior rhombi, outer face excluded)
    euler = sub.V - sub.Ecount + sub.F
    checks["euler V-E+F==1"] = (euler == 1, euler)
    # 7. no overlaps/gaps: sum of face areas == area enclosed by boundary polygon
    total_face_area = sum(exp_area[f["shape"]] for f in sub.faces)
    checks["area_sum (thick*%d thin*%d)" %
           (sub.shape_counts().get("thick", 0),
            sub.shape_counts().get("thin", 0))] = (True, round(total_face_area, 4))
    # 8. no duplicate faces
    fset = set(frozenset(f["verts"]) for f in sub.faces)
    checks["no_duplicate_faces"] = (len(fset) == sub.F, f"{len(fset)}/{sub.F}")
    all_pass = all(v[0] for v in checks.values())
    return all_pass, checks


# ---------------------------------------------------------------------------
# Histories (deterministic, geometry-only) and the frozen reader
# ---------------------------------------------------------------------------
def _turn_path(sub, S, target_dist, prefer):
    """Greedy shortest-path toward vertices at graph-distance target_dist from S,
    breaking ties by turning 'left' (ccw) or 'right' (cw). Geometry only."""
    distS = sub.graph_bfs_dist(S)
    # choose end E deterministically: farthest-in-a-fixed-direction vertex at
    # exactly target_dist (fixed direction = +x); handled by caller via candidates
    return distS


def _shortest_path_extreme(sub, S, E, prefer):
    """A shortest S->E path; among shortest paths pick the one that at each step
    turns maximally ccw (prefer='left') or cw (prefer='right'). Deterministic."""
    distE = sub.graph_bfs_dist(E)
    if S not in distE:
        return None
    L = distE[S]
    path = [S]
    cur = S
    prev_dir = np.array([1.0, 0.0])          # reference heading
    for _ in range(L):
        nxts = [y for y in sub.adj[cur] if distE.get(y, 1e9) == distE[cur] - 1]
        if not nxts:
            return None
        # signed angle of each candidate step relative to prev_dir
        def signed_angle(y):
            d = sub.pos[y] - sub.pos[cur]
            ang = math.atan2(d[1], d[0]) - math.atan2(prev_dir[1], prev_dir[0])
            return (ang + math.pi) % (2 * math.pi) - math.pi
        nxts.sort(key=signed_angle, reverse=(prefer == "left"))
        nxt = nxts[0]
        prev_dir = sub.pos[nxt] - sub.pos[cur]
        path.append(nxt); cur = nxt
    return path


def make_history_pair(sub, min_len=6, max_len=14):
    """Deterministic geometry-only equal-length common-endpoint pair (A,B).

    S = vertex nearest centroid. Scan candidate ends E by increasing distance then
    fixed angular order; A = leftmost shortest path, B = rightmost. Eligible iff
    both exist, equal length in [min_len,max_len], and edge-disjoint except at
    endpoints. Returns (S, E, pathA, pathB) or None (failure)."""
    S = min(sub.pos, key=lambda v: np.hypot(*sub.pos[v]))
    distS = sub.graph_bfs_dist(S)
    cands = [v for v, d in distS.items() if min_len <= d <= max_len]
    # deterministic order: by (distance, angle from +x, vid)
    cands.sort(key=lambda v: (distS[v],
                              math.atan2(*(sub.pos[v] - sub.pos[S])[::-1]), v))
    for E in cands:
        A = _shortest_path_extreme(sub, S, E, "left")
        B = _shortest_path_extreme(sub, S, E, "right")
        if A is None or B is None:
            continue
        if len(A) != len(B):
            continue
        esA = set(tuple(sorted((A[i], A[i + 1]))) for i in range(len(A) - 1))
        esB = set(tuple(sorted((B[i], B[i + 1]))) for i in range(len(B) - 1))
        if esA == esB:
            continue                          # identical path; not a usable pair
        overlap = len(esA & esB)
        return {"S": S, "E": E, "pathA": A, "pathB": B,
                "len": len(A) - 1, "edge_overlap": overlap,
                "edgesA": esA, "edgesB": esB}
    return None


def make_history_pairs(sub, k=3, min_len=6, max_len=14):
    """Up to k deterministic eligible (A,B) pairs with DISTINCT end vertices,
    scanned in the same deterministic order as make_history_pair."""
    S = min(sub.pos, key=lambda v: np.hypot(*sub.pos[v]))
    distS = sub.graph_bfs_dist(S)
    cands = [v for v, d in distS.items() if min_len <= d <= max_len]
    cands.sort(key=lambda v: (distS[v],
                              math.atan2(*(sub.pos[v] - sub.pos[S])[::-1]), v))
    out = []
    for E in cands:
        A = _shortest_path_extreme(sub, S, E, "left")
        B = _shortest_path_extreme(sub, S, E, "right")
        if A is None or B is None or len(A) != len(B):
            continue
        esA = set(tuple(sorted((A[i], A[i + 1]))) for i in range(len(A) - 1))
        esB = set(tuple(sorted((B[i], B[i + 1]))) for i in range(len(B) - 1))
        if esA == esB:
            continue
        out.append({"S": S, "E": E, "pathA": A, "pathB": B, "len": len(A) - 1,
                    "edge_overlap": len(esA & esB), "edgesA": esA, "edgesB": esB})
        if len(out) >= k:
            break
    return out


def _dist_vertex_to_pathset(sub, pathverts):
    """graph distance (original graph) from every vertex to nearest path vertex."""
    dist = {v: 0 for v in pathverts}
    q = deque(pathverts)
    while q:
        x = q.popleft()
        for y in sub.adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1; q.append(y)
    return dist


def reader_coefficients(sub, hist):
    """Frozen per-candidate-diagonal sign from proximity to A vs B paths, on the
    FROZEN ORIGINAL graph. c(d) = sign( d(d,B) - d(d,A) ): +1 nearer A, -1 nearer B.
    Distance of diagonal d=(u,w) to a path = min(d_G(u,path), d_G(w,path))."""
    dA = _dist_vertex_to_pathset(sub, set(hist["pathA"]))
    dB = _dist_vertex_to_pathset(sub, set(hist["pathB"]))
    coeff = {}
    for f in sub.faces:
        for d in f["diagonals"]:
            u, w = d
            da = min(dA.get(u, 1e9), dA.get(w, 1e9))
            db = min(dB.get(u, 1e9), dB.get(w, 1e9))
            coeff[d] = float(np.sign(db - da))     # +1 nearer A
    return coeff


class SubstrateWorld:
    """Minimal substrate-general engine (same rules/params as v2). For the tiny
    smoke fixture only in v10 -- NOT a production run."""
    W0 = 1.0; ALPHA = 0.5; WMAX = 6.0; THETA = 4.0; WINIT = 1.0; THRESH = 5.5

    def __init__(self, sub):
        self.sub = sub
        self.weight = {e: self.W0 for e in sub.base_edges}
        self.adj = defaultdict(list)
        for e in sub.base_edges:
            self.adj[e[0]].append(e[1]); self.adj[e[1]].append(e[0])
        self.base_edge_set = set(sub.base_edges)
        self.inactive = set(d for f in sub.faces for d in f["diagonals"])
        self.active = set()
        self.n_activations = 0

    def _key(self, u, v):
        return (u, v) if u < v else (v, u)

    def reinforce(self, u, v):
        e = self._key(u, v)
        self.weight[e] += self.ALPHA * (self.WMAX - self.weight[e])

    def _activate(self, d):
        if d not in self.inactive:
            return
        self.inactive.discard(d); self.active.add(d)
        self.weight[d] = self.WINIT
        self.adj[d[0]].append(d[1]); self.adj[d[1]].append(d[0])
        self.n_activations += 1

    def grow_from_edge(self, u, v):
        e = self._key(u, v)
        if e not in self.base_edge_set:
            return
        for fidx in self.sub.edge_faces[e]:
            f = self.sub.faces[fidx]
            act = sum(self.weight[be] - self.W0 for be in f["edges"])
            if act >= self.THETA:
                for d in f["diagonals"]:
                    if d in self.inactive:
                        self._activate(d)

    def weighted_step(self, v, rng):
        nb = self.adj[v]
        ws = np.array([self.weight[self._key(v, u)] for u in nb], float)
        return nb[rng.choice(len(nb), p=ws / ws.sum())]

    def s_high(self, coeff):
        return sum(coeff.get(d, 0.0) for d in self.active if self.weight[d] >= self.THRESH)


def reader_diagnostics(sub, hist):
    """Sign-swap symmetry, +/-/0 counts, and saturated reader value."""
    c = reader_coefficients(sub, hist)
    hist_swap = dict(hist)
    hist_swap["pathA"], hist_swap["pathB"] = hist["pathB"], hist["pathA"]
    c_swap = reader_coefficients(sub, hist_swap)
    swap_ok = all(abs(c[d] + c_swap[d]) < 1e-9 for d in c)
    npos = sum(1 for v in c.values() if v > 0)
    nneg = sum(1 for v in c.values() if v < 0)
    nzero = sum(1 for v in c.values() if v == 0)
    saturated = sum(c.values())              # all candidates high -> reader value
    return {"n_candidates": len(c), "swap_flips_sign": swap_ok,
            "n_pos": npos, "n_neg": nneg, "n_zero": nzero,
            "saturated_reader_value": saturated, "coeff": c}
