"""Fresh-cut selector for the prospective route prediction.

Reuses the frozen geometry generator (aperiodic_qec_geometry_2026-11-19/pilot.py) unchanged:
parent/disk/cut/distances/export. For AB and Penrose it enumerates every n=21, distance-(3,3)
cut from the frozen disk-cut set, enumerates ALL weight-3 X-logical supports from the saved
matrices, tags each eligible edge on-route (in >=1 support) / off-route (in none), keeps only
cuts that host both an on-route and an off-route eligible edge, and picks the best-matched
on/off pair per cut. It then excludes the discovery cut (and overlapping/duplicate geometry)
and selects two mutually non-overlapping fresh cuts per family under a frozen ranking.

Geometry only; no decoder scores are consulted.
"""
import collections as C
import importlib.util
import itertools as I
import json
import math
from pathlib import Path

import numpy as np

GEOM = Path(__file__).resolve().parents[2] / 'aperiodic_qec_geometry_2026-11-19'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pilot = _load('pilot', GEOM / 'pilot.py')

ASPECTS = (1., 1.25, .8)
ANGLES = (0., math.pi / 8, math.pi / 4, 3 * math.pi / 8)
N_TARGET = 21


# ---- weight-3 X-logical supports from saved matrices ----
def _basis(ints):
    bs = []
    for v in ints:
        x = v
        for b in bs:
            x = min(x, x ^ b)
        if x:
            bs.append(x); bs.sort(reverse=True)
    return bs


def _in_span(x, bs):
    for b in bs:
        x = min(x, x ^ b)
    return x == 0


def weight3_xlogicals(HX, HZ, n):
    """All weight-3 supports in ker(HZ) \\ row(HX)."""
    def to_int(r):
        return sum((1 << i) for i, b in enumerate(r) if b)
    rowHX = _basis([to_int(r) for r in HX])
    HZi = [to_int(r) for r in HZ]
    out = []
    for combo in I.combinations(range(n), 3):
        v = 0
        for q in combo:
            v |= 1 << q
        if all(bin(h & v).count('1') % 2 == 0 for h in HZi) and not _in_span(v, rowHX):
            out.append(set(combo))
    return out


# ---- boundary graph distances (same convention as the pilot run) ----
def _boundary(obj):
    adj = C.defaultdict(set)
    for e in obj['edges']:
        u, v = e['vertices']; adj[u].add(v); adj[v].add(u)
    eid = {e['id']: e for e in obj['edges']}
    rough = set(); smooth = set()
    for arc in obj['arcs']:
        tgt = rough if arc['label'] == 'rough' else smooth
        for e in arc['edges']:
            tgt.update(eid[e]['vertices'])
    return adj, rough, smooth


def _bfs(adj, starts, targets):
    if not targets:
        return None
    seen = {s: 0 for s in starts}; q = C.deque(starts)
    while q:
        x = q.popleft()
        if x in targets:
            return seen[x]
        for y in adj[x]:
            if y not in seen:
                seen[y] = seen[x] + 1; q.append(y)
    return None


def edge_descriptor(obj, edge_id):
    e = next(ed for ed in obj['edges'] if ed['id'] == edge_id)
    adj, rough, smooth = _boundary(obj)
    ends = e['vertices']
    return dict(d_rough=_bfs(adj, ends, rough), d_smooth=_bfs(adj, ends, smooth),
                endpoint_vertices=ends)


# ---- enumerate n=21 distance-(3,3) cuts (frozen disk-cut set) ----
def _disk_cuts(p):
    centres = sorted((v for v in p['pos'] if sum(t * t for t in p['pos'][v]) <= 16),
                     key=lambda v: (round(sum(t * t for t in p['pos'][v]), 10), v))[:24]
    facec = {i: np.mean([p['pos'][v] for v in vs], axis=0) for i, vs in enumerate(p['faces'])}
    patches = {}
    for ci, v in enumerate(centres):
        for ai, aspect in enumerate(ASPECTS):
            for oi, angle in enumerate(ANGLES):
                def score(f, angle=angle, aspect=aspect, v=v):
                    dx, dy = facec[f] - p['pos'][v]
                    x = dx * math.cos(angle) + dy * math.sin(angle)
                    y = -dx * math.sin(angle) + dy * math.cos(angle)
                    return (round((x / aspect) ** 2 + (y * aspect) ** 2, 10),
                            tuple(sorted(p['faces'][f])))
                order = sorted(facec, key=score)
                for m in range(6, 25):
                    ids = tuple(sorted(order[:m])); spec = (ci, ai, oi, m)
                    if ids not in patches:
                        dsk = pilot.disk(p, ids)
                        if dsk:
                            patches[ids] = (spec, dsk, v, aspect, angle)
    return patches


def enumerate_cuts(p):
    """Yield distinct n=21, distance-(3,3) cuts with >=2 eligible edges."""
    patches = _disk_cuts(p)
    seen = set()
    for spec, d, centre, aspect, angle in patches.values():
        L = len(d['cycle']); E = len(d['edges'])
        for s in range(L):
            for shifts in I.product((-1, 0, 1), repeat=3):
                corners = (s,) + tuple(s + j * L // 4 + t for j, t in zip((1, 2, 3), shifts))
                if not all(a < b for a, b in zip(corners, corners[1:] + (s + L,))):
                    continue
                n = E - ((corners[1] - s) + (corners[3] - corners[2]))
                if n != N_TARGET:
                    continue
                roughkey = tuple(sorted((i % L) for a, b in ((s, corners[1]), (corners[2], corners[3]))
                                        for i in range(a, b)))
                key = (d['ids'], roughkey)
                if key in seen:
                    continue
                seen.add(key)
                c = pilot.cut(p, d, corners)
                if len(c['eligible']) < 2:
                    continue
                x, z = pilot.distances(d, c)
                if x is None or z is None or len(x) != 3 or len(z) != 3:
                    continue
                specd = dict(centre=centre, aspect=aspect, angle=angle, spec=spec, corners=corners)
                yield dict(ids=d['ids'], d=d, c=c, spec=specd, x=x, z=z)


def discovery_ids(p):
    best, stats = pilot.search(p)
    return set(best[1]['ids'])


def analyse(p, cand):
    """Export a candidate to the patch JSON and tag its eligible edges on/off-route."""
    obj = pilot.export(p, (None, cand['d'], cand['c'], cand['spec'], cand['x'], cand['z']), {})
    w3 = weight3_xlogicals(obj['HX'], obj['HZ'], obj['n'])
    on, off = [], []
    for e in obj['eligible']:
        q = e['qubit']
        cnt = sum(1 for s in w3 if q in s)
        desc = edge_descriptor(obj, e['edge'])
        rec = dict(edge=e['edge'], qubit=q, n_supports=cnt,
                   endpoint_degrees=sorted(e['endpoint_degrees']),
                   d_rough=desc['d_rough'], d_smooth=desc['d_smooth'])
        (on if cnt > 0 else off).append(rec)
    return obj, w3, on, off
