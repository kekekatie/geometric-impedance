#!/usr/bin/env python3
"""
substrate_lib.py (v11) -- de Bruijn pentagrid tilings, REPAIRED construction &
validation, histories, frozen reader, and a substrate-general engine.

Repairs over v10 (see DESIGN_NOTE_v11.md / v10 correction):
  R1. validate() now genuinely tests overlaps/gaps: traces boundary loops, compares
      net enclosed (signed shoelace) area with the summed face area to an explicit
      tolerance, tests non-incident ORIGINAL-edge crossings, and checks each face
      centroid lies in exactly one face. (v10's area check was a no-op.)
  R2. Robust strip-index construction via searchsorted (no eps sampling), with a
      clearance test to non-incident lines; near-degenerate intersections are
      COUNTED and reported, not silently used.
  R3. Cropping now reports discarded components; candidate diagonals are checked
      unique and distinct from original edges.
Neighbour and candidate orderings are canonicalised (sorted) for reproducibility.

Source: N.G. de Bruijn, Indag. Math. 43 (1981) 39-66 (pentagrid; Penrose iff the
offsets sum to an integer and the pentagrid is regular).
"""
from __future__ import annotations

import math
from collections import defaultdict, deque

import numpy as np

PHI = (1.0 + 5.0 ** 0.5) / 2.0
E = np.array([[math.cos(2 * math.pi * j / 5), math.sin(2 * math.pi * j / 5)]
              for j in range(5)])
ROUND = 6
CLEAR_TOL = 1e-7          # min clearance of an intersection to non-incident lines
DEFAULT_OFFSETS = np.array([0.30, 0.10, -0.25, -0.25, 0.10])   # sum 0 (x-mirror)
EXP_AREA = {"thick": math.sin(2 * math.pi / 5), "thin": math.sin(math.pi / 5)}


def _rhombus_shape(r, s):
    d = min((r - s) % 5, (s - r) % 5)
    return "thick" if d == 1 else "thin"


def _poly_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def _seg_proper_intersect(p1, p2, p3, p4):
    """True if open segments p1p2 and p3p4 cross in their interiors."""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1 = cross(p3, p4, p1); d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3); d4 = cross(p1, p2, p4)
    if ((d1 > 1e-12 and d2 < -1e-12) or (d1 < -1e-12 and d2 > 1e-12)) and \
       ((d3 > 1e-12 and d4 < -1e-12) or (d3 < -1e-12 and d4 > 1e-12)):
        return True
    return False


def _point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)):
            xint = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xint:
                inside = not inside
    return inside


class Substrate:
    def __init__(self):
        self.mode = None; self.pos = {}; self.vid = {}
        self.base_edges = set(); self.faces = []
        self.adj = defaultdict(list); self.edge_faces = defaultdict(list)
        self.degeneracies = 0; self.discarded_components = 0
        self.discarded_vertices = 0

    # ---- builders ---------------------------------------------------------
    @classmethod
    def pentagrid(cls, radius, offsets, jitter_amp=0.0, seed=0):
        self = cls()
        self.mode = "perturbed" if jitter_amp > 0 else "regular"
        self.radius = radius; self.offsets = np.asarray(offsets, float)
        self.jitter_amp = jitter_amp; self.seed = seed
        rng = np.random.default_rng(seed)
        M = int(math.ceil(radius)) + 3
        ns = np.arange(-M, M + 1)
        P = {}
        for j in range(5):
            p = ns + self.offsets[j]
            if jitter_amp > 0:
                p = p + rng.uniform(-jitter_amp, jitter_amp, size=p.shape)
                assert np.all(np.diff(p) > 0), "perturbation broke line ordering"
            P[j] = p
        raw_faces = []
        for r in range(5):
            for s in range(r + 1, 5):
                Ainv = np.linalg.inv(np.array([E[r], E[s]]))
                for Pr in P[r]:
                    for Ps in P[s]:
                        x = Ainv @ np.array([Pr, Ps])
                        if x @ x > (radius + 2.0) ** 2:
                            continue
                        # clearance to non-incident lines (robustness gate)
                        clear = math.inf
                        for j in range(5):
                            if j in (r, s):
                                continue
                            proj = E[j] @ x
                            k = np.searchsorted(P[j], proj)
                            for kk in (k - 1, k):
                                if 0 <= kk < len(P[j]):
                                    clear = min(clear, abs(proj - P[j][kk]))
                        if clear < CLEAR_TOL:
                            self.degeneracies += 1
                            continue
                        K = np.array([np.searchsorted(P[j], E[j] @ x, side="right")
                                      for j in range(5)])
                        ir = np.searchsorted(P[r], Pr, side="left")
                        isd = np.searchsorted(P[s], Ps, side="left")
                        corners = []
                        for a in (0, 1):
                            for b in (0, 1):
                                Kc = K.copy(); Kc[r] = ir + a; Kc[s] = isd + b
                                corners.append((Kc[:, None] * E).sum(axis=0))
                        loop = [corners[0], corners[2], corners[3], corners[1]]
                        if any(np.hypot(*c) > radius for c in loop):
                            continue
                        raw_faces.append((loop, _rhombus_shape(r, s)))
        # dedupe vertices
        for loop, shape in raw_faces:
            for c in loop:
                self._get_vid(c)
        loops = []
        for loop, shape in raw_faces:
            vids = tuple(self._get_vid(c) for c in loop)
            if len(set(vids)) == 4:
                loops.append((vids, shape))
        self._finalize(loops)
        self._keep_main_component()
        return self

    @classmethod
    def from_faces(cls, positions, loops_shapes):
        """positions: list of (x,y); loops_shapes: list of (vid_loop, shape)."""
        self = cls()
        self.mode = "explicit"
        for p in positions:
            self._get_vid(np.asarray(p, float))
        self._finalize(loops_shapes)
        return self

    def _get_vid(self, point):
        key = (round(float(point[0]), ROUND), round(float(point[1]), ROUND))
        if key not in self.vid:
            vid = len(self.pos); self.vid[key] = vid
            self.pos[vid] = np.array(key)
        return self.vid[key]

    def _finalize(self, loops):
        self.base_edges = set(); self.faces = []
        self.adj = defaultdict(list); self.edge_faces = defaultdict(list)
        seen = set()
        adjset = defaultdict(set)
        for vids, shape in loops:
            pts = [self.pos[v] for v in vids]
            if _poly_area(pts) < 0:
                vids = tuple(reversed(vids))
            fkey = frozenset(vids)
            if fkey in seen:
                continue
            seen.add(fkey)
            fedges = [tuple(sorted((vids[i], vids[(i + 1) % 4]))) for i in range(4)]
            diags = [tuple(sorted((vids[0], vids[2]))),
                     tuple(sorted((vids[1], vids[3])))]
            fidx = len(self.faces)
            self.faces.append({"verts": vids, "edges": fedges, "diagonals": diags,
                               "shape": shape})
            for e in fedges:
                self.base_edges.add(e); self.edge_faces[e].append(fidx)
                adjset[e[0]].add(e[1]); adjset[e[1]].add(e[0])
        # canonical (sorted) adjacency for reproducibility
        self.adj = {v: sorted(adjset[v]) for v in self.pos}

    def _keep_main_component(self):
        if not self.pos:
            return
        start = min(self.pos, key=lambda v: np.hypot(*self.pos[v]))
        seen = {start}; q = deque([start])
        while q:
            x = q.popleft()
            for y in self.adj.get(x, []):
                if y not in seen:
                    seen.add(y); q.append(y)
        if len(seen) == len(self.pos):
            return
        # count discarded, rebuild
        comps = self._count_components()
        self.discarded_components = comps - 1
        self.discarded_vertices = len(self.pos) - len(seen)
        keep = seen
        old_faces = [f for f in self.faces if all(v in keep for v in f["verts"])]
        remap = {}; newpos = {}
        for v in sorted(keep):
            remap[v] = len(newpos); newpos[len(newpos)] = self.pos[v]
        self.pos = newpos
        self.vid = {(round(p[0], ROUND), round(p[1], ROUND)): i
                    for i, p in self.pos.items()}
        loops = [(tuple(remap[v] for v in f["verts"]), f["shape"]) for f in old_faces]
        self._finalize(loops)

    def _count_components(self):
        seen = set(); comps = 0
        for v in self.pos:
            if v in seen:
                continue
            comps += 1; q = deque([v]); seen.add(v)
            while q:
                x = q.popleft()
                for y in self.adj.get(x, []):
                    if y not in seen:
                        seen.add(y); q.append(y)
        return comps

    # ---- summaries --------------------------------------------------------
    @property
    def V(self): return len(self.pos)
    @property
    def Ecount(self): return len(self.base_edges)
    @property
    def F(self): return len(self.faces)

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
            h[len(self.adj.get(v, []))] += 1
        return dict(sorted(h.items()))

    def shape_counts(self):
        c = defaultdict(int)
        for f in self.faces:
            c[f["shape"]] += 1
        return dict(c)

    def all_diagonals(self):
        ds = []
        for f in self.faces:
            ds.extend(f["diagonals"])
        return ds

    def graph_bfs_dist(self, source):
        dist = {source: 0}; q = deque([source])
        while q:
            x = q.popleft()
            for y in self.adj.get(x, []):
                if y not in dist:
                    dist[y] = dist[x] + 1; q.append(y)
        return dist

    def boundary_distance(self):
        bv = self.boundary_vertices()
        dist = {v: 0 for v in bv}; q = deque(bv)
        while q:
            x = q.popleft()
            for y in self.adj.get(x, []):
                if y not in dist:
                    dist[y] = dist[x] + 1; q.append(y)
        return dist


# ---------------------------------------------------------------------------
# Validation (geometry AND topology; overlaps/gaps genuinely tested -- R1)
# ---------------------------------------------------------------------------
def _trace_boundary_loops(sub):
    badj = defaultdict(list)
    for e in sub.boundary_edges():
        badj[e[0]].append(e[1]); badj[e[1]].append(e[0])
    unused = set(tuple(sorted(e)) for e in sub.boundary_edges())
    loops = []
    while unused:
        e0 = next(iter(unused)); unused.discard(e0)
        loop = [e0[0], e0[1]]; unused_ok = True
        while loop[-1] != loop[0]:
            cur = loop[-1]; nxt = None
            for y in badj[cur]:
                ek = tuple(sorted((cur, y)))
                if ek in unused:
                    nxt = y; unused.discard(ek); break
            if nxt is None:
                unused_ok = False; break
            loop.append(nxt)
        loops.append(loop[:-1] if loop[-1] == loop[0] else loop)
        if not unused_ok:
            break
    return loops


def validate(sub, tol=1e-6, check_overlaps=True):
    checks = {}

    def rec(name, ok, val):
        checks[name] = (bool(ok), val)

    # unit sides
    mse = max((abs(np.hypot(*(sub.pos[e[0]] - sub.pos[e[1]])) - 1.0)
               for e in sub.base_edges), default=0.0)
    rec("unit_sides", mse < 1e-6, mse)
    # rhombus shapes + areas + CCW
    bad_shape = 0; max_area_err = 0.0; ccw = 0
    for f in sub.faces:
        pts = [sub.pos[v] for v in f["verts"]]
        ar = _poly_area(pts); ccw += (ar > 0)
        max_area_err = max(max_area_err, abs(abs(ar) - EXP_AREA[f["shape"]]))
        dirs = set()
        for i in range(4):
            d = sub.pos[f["verts"][(i + 1) % 4]] - sub.pos[f["verts"][i]]
            k = int(np.argmin([min(np.hypot(*(d - E[j]), ), np.hypot(*(d + E[j])))
                               for j in range(5)]))
            dirs.add(k)
        if len(dirs) != 2:
            bad_shape += 1
    rec("rhombus_shapes_ok", bad_shape == 0, bad_shape)
    rec("face_areas", max_area_err < 1e-6, max_area_err)
    rec("faces_CCW", ccw == sub.F, f"{ccw}/{sub.F}")
    # incidence
    bad_inc = sum(1 for e, fs in sub.edge_faces.items() if len(fs) not in (1, 2))
    rec("edge_incidence_1or2", bad_inc == 0, bad_inc)
    # connected
    comp = len(sub.graph_bfs_dist(next(iter(sub.pos)))) if sub.pos else 0
    rec("connected", comp == sub.V, f"{comp}/{sub.V}")
    # boundary loops
    bdeg = defaultdict(int)
    for e in sub.boundary_edges():
        bdeg[e[0]] += 1; bdeg[e[1]] += 1
    bad_loop = sum(1 for d in bdeg.values() if d != 2)
    loops = _trace_boundary_loops(sub)
    rec("boundary_is_loops", bad_loop == 0, bad_loop)
    rec("n_boundary_loops", len(loops) >= 1, len(loops))
    # euler (disk with h holes: V-E+F = 1 - (n_loops-1) = 2 - n_loops)
    euler = sub.V - sub.Ecount + sub.F
    rec("euler_V-E+F==2-loops", euler == 2 - len(loops), (euler, 2 - len(loops)))
    # --- R1: genuine overlaps/gaps ---
    face_area = sum(EXP_AREA[f["shape"]] for f in sub.faces)
    net_boundary_area = sum(abs(_poly_area([sub.pos[v] for v in lp])) for lp in loops)
    # outer loop positive, holes negative -> use largest as outer
    areas = sorted((abs(_poly_area([sub.pos[v] for v in lp])) for lp in loops),
                   reverse=True)
    enclosed = areas[0] - sum(areas[1:]) if areas else 0.0
    rec("area_faces==enclosed", abs(face_area - enclosed) < 1e-4 * max(1, face_area),
        (round(face_area, 4), round(enclosed, 4)))
    # non-incident original-edge crossings
    crossings = 0
    if check_overlaps:
        edges = [(e, sub.pos[e[0]], sub.pos[e[1]]) for e in sub.base_edges]
        for i in range(len(edges)):
            ei, a1, a2 = edges[i]
            for k in range(i + 1, len(edges)):
                ek, b1, b2 = edges[k]
                if set(ei) & set(ek):
                    continue
                if _seg_proper_intersect(a1, a2, b1, b2):
                    crossings += 1
        rec("no_edge_crossings", crossings == 0, crossings)
        # face-centroid in exactly one face
        polys = [([sub.pos[v] for v in f["verts"]],
                  np.mean([sub.pos[v] for v in f["verts"]], axis=0)) for f in sub.faces]
        bad_cent = 0
        for _, cen in polys:
            cnt = 0
            for poly, _c in polys:
                xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
                if min(xs) - 1e-9 <= cen[0] <= max(xs) + 1e-9 and \
                   min(ys) - 1e-9 <= cen[1] <= max(ys) + 1e-9:
                    if _point_in_poly(cen, poly):
                        cnt += 1
            if cnt != 1:
                bad_cent += 1
        rec("centroid_in_one_face", bad_cent == 0, bad_cent)
    # candidate diagonals unique + distinct from originals (R3)
    diags = sub.all_diagonals()
    rec("diagonals_unique", len(diags) == len(set(diags)),
        f"{len(set(diags))}/{len(diags)}")
    rec("diagonals_not_original", len(set(diags) & sub.base_edges) == 0,
        len(set(diags) & sub.base_edges))
    rec("degeneracies_reported", True, sub.degeneracies)
    rec("discarded_components", True, sub.discarded_components)
    all_pass = all(v[0] for v in checks.values())
    return all_pass, checks


# ---------------------------------------------------------------------------
# Square substrate (for engine equivalence fixture)
# ---------------------------------------------------------------------------
def square_substrate(n):
    pos = []
    idx = {}
    for r in range(n):
        for c in range(n):
            idx[(r, c)] = len(pos); pos.append((float(c), float(-r)))
    loops = []
    for r in range(n - 1):
        for c in range(n - 1):
            a = idx[(r, c)]; b = idx[(r, c + 1)]
            cc = idx[(r + 1, c + 1)]; d = idx[(r + 1, c)]
            loops.append(((a, b, cc, d), "thick"))    # square; shape label unused
    return Substrate.from_faces(pos, loops)


# ---------------------------------------------------------------------------
# Histories (deterministic, geometry-only) and frozen reader
# ---------------------------------------------------------------------------
def _shortest_path_extreme(sub, S, E, prefer):
    distE = sub.graph_bfs_dist(E)
    if S not in distE:
        return None
    path = [S]; cur = S; prev_dir = np.array([1.0, 0.0])
    for _ in range(distE[S]):
        nxts = [y for y in sub.adj[cur] if distE.get(y, 1e9) == distE[cur] - 1]
        if not nxts:
            return None

        def signed_angle(y):
            d = sub.pos[y] - sub.pos[cur]
            ang = math.atan2(d[1], d[0]) - math.atan2(prev_dir[1], prev_dir[0])
            return (ang + math.pi) % (2 * math.pi) - math.pi
        nxts.sort(key=lambda y: (signed_angle(y), y), reverse=(prefer == "left"))
        nxt = nxts[0]; prev_dir = sub.pos[nxt] - sub.pos[cur]
        path.append(nxt); cur = nxt
    return path


def make_history_pairs(sub, k=3, length=6):
    """Up to k deterministic eligible (A,B) pairs, DISTINCT end vertices, FIXED
    length (edges). A = leftmost shortest path, B = rightmost. Eligible iff both
    exist, both equal `length`, and are NOT identical (they may share edges/
    vertices; shared counts are reported)."""
    S = min(sub.pos, key=lambda v: np.hypot(*sub.pos[v]))
    distS = sub.graph_bfs_dist(S)
    cands = [v for v, d in distS.items() if d == length]
    cands.sort(key=lambda v: (math.atan2(*(sub.pos[v] - sub.pos[S])[::-1]), v))
    out = []
    for E in cands:
        A = _shortest_path_extreme(sub, S, E, "left")
        B = _shortest_path_extreme(sub, S, E, "right")
        if A is None or B is None or len(A) != length + 1 or len(B) != length + 1:
            continue
        esA = set(tuple(sorted((A[i], A[i + 1]))) for i in range(length))
        esB = set(tuple(sorted((B[i], B[i + 1]))) for i in range(length))
        if esA == esB:
            continue
        vsh = len(set(A) & set(B)) - 2      # shared internal vertices
        out.append({"S": S, "E": E, "pathA": A, "pathB": B, "len": length,
                    "shared_edges": len(esA & esB), "shared_internal_vertices": vsh,
                    "edgesA": esA, "edgesB": esB})
        if len(out) >= k:
            break
    return out


def _dist_to_pathset(sub, pathverts):
    dist = {v: 0 for v in pathverts}; q = deque(pathverts)
    while q:
        x = q.popleft()
        for y in sub.adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1; q.append(y)
    return dist


def reader_coefficients(sub, hist):
    dA = _dist_to_pathset(sub, set(hist["pathA"]))
    dB = _dist_to_pathset(sub, set(hist["pathB"]))
    coeff = {}
    for f in sub.faces:
        for d in f["diagonals"]:
            u, w = d
            da = min(dA.get(u, 1e9), dA.get(w, 1e9))
            db = min(dB.get(u, 1e9), dB.get(w, 1e9))
            coeff[d] = float(np.sign(db - da))
    return coeff


def reader_diagnostics(sub, hist):
    c = reader_coefficients(sub, hist)
    hs = dict(hist); hs["pathA"], hs["pathB"] = hist["pathB"], hist["pathA"]
    cs = reader_coefficients(sub, hs)
    swap_ok = all(abs(c[d] + cs[d]) < 1e-9 for d in c)
    return {"n_candidates": len(c), "swap_flips_sign": swap_ok,
            "n_pos": sum(1 for v in c.values() if v > 0),
            "n_neg": sum(1 for v in c.values() if v < 0),
            "n_zero": sum(1 for v in c.values() if v == 0),
            "saturated_reader_value": sum(c.values()), "coeff": c}


# ---------------------------------------------------------------------------
# Substrate-general engine (canonical neighbour order; matches v2 rules)
# ---------------------------------------------------------------------------
class SubstrateWorld:
    W0 = 1.0; ALPHA = 0.5; WMAX = 6.0; THETA = 4.0; WINIT = 1.0; THRESH = 5.5

    def __init__(self, sub):
        self.sub = sub
        self.weight = {e: self.W0 for e in sub.base_edges}
        self.adj = {v: list(sub.adj[v]) for v in sub.pos}    # canonical (sorted)
        self.base_edge_set = set(sub.base_edges)
        self.inactive = set(sub.all_diagonals())
        self.active = set()
        self.n_activations = 0
        self.boundary_set = sub.boundary_vertices()
        self.boundary_visits = 0
        self.total_steps = 0

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
        # keep adjacency canonical
        self.adj[d[0]] = sorted(self.adj[d[0]] + [d[1]])
        self.adj[d[1]] = sorted(self.adj[d[1]] + [d[0]])
        self.n_activations += 1

    def grow_from_edge(self, u, v):
        e = self._key(u, v)
        if e not in self.base_edge_set:
            return
        for fidx in self.sub.edge_faces[e]:
            f = self.sub.faces[fidx]
            if sum(self.weight[be] - self.W0 for be in f["edges"]) >= self.THETA:
                for d in f["diagonals"]:
                    if d in self.inactive:
                        self._activate(d)

    def weighted_step(self, v, rng):
        nb = self.adj[v]
        ws = np.array([self.weight[self._key(v, u)] for u in nb], float)
        nxt = nb[rng.choice(len(nb), p=ws / ws.sum())]
        self.total_steps += 1
        if nxt in self.boundary_set:
            self.boundary_visits += 1
        return nxt

    # ---- readouts ---------------------------------------------------------
    def s_high(self, coeff):
        return float(sum(coeff.get(d, 0.0) for d in self.active
                         if self.weight[d] >= self.THRESH))

    def n_high(self):
        return int(sum(1 for d in self.active if self.weight[d] >= self.THRESH))

    def total_weight(self):
        return float(sum(self.weight.values()))

    def headroom(self):
        return float(np.mean([self.WMAX - w for w in self.weight.values()]))

    def frac_active(self):
        tot = len(self.active) + len(self.inactive)
        return len(self.active) / tot if tot else 0.0

    def structural_access(self, source, hops=4):
        seen = {source: 0}; q = deque([source]); cnt = 0
        while q:
            x = q.popleft()
            if seen[x] == hops:
                continue
            for y in self.adj[x]:
                if y not in seen:
                    seen[y] = seen[x] + 1; cnt += 1; q.append(y)
        return cnt

    def effective_alternatives(self, source, L=4):
        hent = {}; trans = {}
        for v in self.adj:
            nb = self.adj[v]
            ws = np.array([self.weight[self._key(v, u)] for u in nb], float)
            s = ws.sum()
            p = ws / s
            hent[v] = float(-(p * np.log(p)).sum())
            trans[v] = list(zip(nb, p))
        pi = defaultdict(float); pi[source] = 1.0; H = 0.0
        for _ in range(L):
            H += sum(pr * hent[v] for v, pr in pi.items())
            nxt = defaultdict(float)
            for v, pr in pi.items():
                for u, pvu in trans[v]:
                    nxt[u] += pr * pvu
            pi = nxt
        return math.exp(H)
