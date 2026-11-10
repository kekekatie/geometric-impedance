"""
address_gapfill.py -- what does the hidden address put in the gap at a dormant scar?

For each hidden offset t the nearby reduced skin allows (t in F(W)), the perfect Penrose
tiling with that offset places exactly one tile across the scar edge e. We read it off:
g(t). The reading uses the frozen reader's OWN cut-and-project window -- proven identical
to the de Bruijn pentagrid window of penrose_address.py by the exact convention bridge
    pos = origin + S * exp(i*18deg) * sum_j K_j * EV[j],   perp(K) = reader PERP(K)
(a vertex K in Z^5 is in the ideal tiling at offset t iff perp(K) - t lies in its layer's
window pentagon, which is exactly the reader's F constraint). penrose_address is used as an
independent structural cross-check.

Frozen engine/lift/reader 84130b9 unchanged; the reader is reached only through tile lists;
nothing feeds back into any constructor; the scar stays skipped.

Run with the amber env (EFP_SNAPSHOT, AMBER_BASE_CACHE, AMBER_CACHE, AMBER_FORK_CACHE).
Modes:  python3 address_gapfill.py gates     # Gate 0 + Gate 1 + non-scar sanity (pre-protocol)
        python3 address_gapfill.py run out.json   # full sampling + controls (post-protocol)
"""
from __future__ import annotations
import sys, os, math, cmath, json, ast, hashlib, itertools, collections, functools
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
AMBER = HERE.parent / 'amber_lobe_ablation_2026-11-06'
sys.path.insert(0, str(AMBER / 'src'))
import common as C
from common import AF, L, D, S, dk, IW
import readout as GRID
sys.path.insert(0, str(C.PILOT / 'penrose_address_environment'))
import penrose_address as PA
sys.path.insert(0, str(AF.EB.EFP / 'archive-free-reader'))
import skin_reader as SR
SR.inverse = functools.lru_cache(maxsize=None)(SR.inverse)

ROT = cmath.exp(1j * math.radians(18))
EV = [complex(*PA.EV[j]) for j in range(5)]
PERP = [cmath.exp(4j * math.pi * j / 5) for j in range(5)]
B1 = json.loads((HERE.parent / 'address_requery_2026-11-10' / 'address_requery.json').read_text())
PROTO = json.loads((HERE.parent / 'address_requery_2026-11-10' / 'protocol_windows.json').read_text())
QDIAG = json.loads((AMBER / 'results' / 'query_diagnostics.json').read_text())
TOL_R = 1e-9; BOX = 50.0
CASES = {(7, 0, 2): 35, (7, 1, 2): 35, (7, 0, 1): 26, (7, 0, 3): 37, (15, 0, 1): 42, (19, 0, 1): 42, (28, 0, 1): 42}


def gen_par(k):  # generator physical (pre-rotation)
    return sum(int(k[j]) * EV[j] for j in range(5))
def perp(k):     # hidden address == reader PERP(K)
    return sum(int(k[j]) * PERP[j] for j in range(5))


# ---------- reduced band + scar edge + committed window ----------
def first_disagreement(w, si, r):
    states = C.load(f'w{w}-s{si}-r{r}-c0-states.pkl')
    rec, _ = C.old(f'verify-{w}-{si}.pkl'); jam = rec['jam_step']
    baseline = [row for row in C.old(f'trace-{w}-{si}.pkl')['calls'] if not row['skin']]
    hist = L.Patch(baseline[jam - 1]['pre'])
    for step, m in enumerate(states['actual'], jam):
        for t in m['placed']:
            hist.add(t)
        band = L.Patch(m['tiles'])
        pinned = {frozenset(tuple(v) for v in ek) for ek in m['scars']}
        for e in hist.frontier():
            if AF.edge_id(*e[:2]) not in pinned:
                continue
            got = D.candidates(band, *e[:3]); want = D.candidates(hist, *e[:3])
            if C.keys(got) != C.keys(want):
                return dict(step=step, m=m, band=band, hist=hist, edge=e, got=list(got),
                            want=list(want), baseline=baseline, jam=jam)
    raise RuntimeError('no disagreement')


def committed_window(band, e, hw):
    cen = GRID.centroid(band.tris); mid = (e[0] + e[1]) / 2
    ang = math.atan2((mid - cen).imag, (mid - cen).real)
    comps = GRID.edge_components(GRID.window(band.tris, cen, ang, hw))
    ek = {L.key(e[0]), L.key(e[1])}
    withe = [cp for cp in comps if ek & {L.key(z) for t in cp for z in t[1:]}]
    return sorted((withe[0] if withe else comps[0]), key=dk), ang


# ---------- reader payload / lift / F ----------
_BASE = {}
def base_payload(w, si):
    if (w, si) not in _BASE:
        jp = C.old(f'jam-{w}-{si}.pkl')
        _BASE[(w, si)] = AF.RD.build_payload(jp['Sstar'], jp['cs'], [])
    return _BASE[(w, si)]

def read_tiles(w, si, tiles):
    payload = dict(base_payload(w, si), tiles=[IW.etile(t) for t in tiles])
    try:
        raw = SR.read(payload)
    except Exception as ex:
        return None, payload, f'{type(ex).__name__}: {ex}'
    if raw.get('status') != 'reconstructed':
        return None, payload, raw.get('status')
    return raw, payload, 'ok'

def windows_and_rank(payload):
    wins = payload['windows']; rank = {int(k): v for k, v in payload['rank'].items()}
    return wins, rank

def accept(K, t, wins, rank):
    """vertex K accepted at offset t iff perp(K) - t in its layer's window pentagon."""
    lay = int(sum(K))
    if lay not in rank:
        return False
    rk = rank[lay]; z = perp(K) - t
    for (nx, ny), h in [((n[0], n[1]), wins[rk]['h']) for n in wins[rk]['normals']]:
        if nx * z.real + ny * z.imag > h + 1e-12:
            return False
    return True

def chebyshev(constraints, wins):
    A, b = [], []
    for rk, i, c in constraints:
        nx, ny = wins[rk]['normals'][i]; nrm = math.hypot(nx, ny)
        if nrm < 1e-15:
            continue
        A.append([-nx / nrm, -ny / nrm, 1.0]); b.append(-c / nrm)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        A.append([float(sx), float(sy), 1.0]); b.append(BOX)
    res = linprog([0, 0, -1], A_ub=np.asarray(A), b_ub=np.asarray(b), bounds=[(None, None)] * 3, method='highs')
    return (res.x[0], res.x[1]), float(res.x[2]) if res.status == 0 else (None, None)


# ---------- geometric candidates across e (frozen template rule, no legality) ----------
def geometric_candidates(p, q, r):
    out = {}
    for (cc, o), (tc, A, B, Cc) in L.TEMPL.items():
        Pp = {"A": A, "B": B, "C": Cc}
        for X, Y, Z in (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"),
                        ("B", "A", "C"), ("C", "B", "A"), ("A", "C", "B")):
            x, y, z = Pp[X], Pp[Y], Pp[Z]
            if abs(abs(y - x) - abs(q - p)) > 1e-6:
                continue
            a = (q - p) / (y - x); zz = p + a * (z - x)
            if L.orient(p, q, zz) * L.orient(p, q, r) >= 0:
                continue
            img = {X: p, Y: q, Z: zz}; nt = (tc, img["A"], img["B"], img["C"])
            out[dk(nt)] = nt
    return list(out.values())

def third_vertex(cand, p, q):
    """the candidate's vertex that is not an endpoint of edge (p,q)."""
    pk, qk = L.key(p), L.key(q)
    for z in cand[1:]:
        if L.key(z) not in (pk, qk):
            return z
    return None


# ---------- g(t): ideal tile across e at offset t ----------
def gap_reader(w, si, W, e):
    """Return (candidates, Kz_of_candidate dict, wins, rank, lift_ok)."""
    p, q, r = e[0], e[1], e[2]
    cands = geometric_candidates(p, q, r)
    wins, rank = windows_and_rank(base_payload(w, si))
    Kz = {}
    for cand in cands:
        raw, payload, st = read_tiles(w, si, list(W) + [cand])
        if st != 'ok':
            Kz[dk(cand)] = None; continue
        tv = third_vertex(cand, p, q); tvk = (round(tv.real, 6), round(tv.imag, 6))
        lift = {tuple(v): k for v, k in raw['lift']}
        Kz[dk(cand)] = lift.get(tvk)
    return cands, Kz, wins, rank

def third_key(cand, Kz):
    kz = Kz[dk(cand)]
    return None if kz is None else tuple(int(x) for x in kz)

def g_of_t(cands, Kz, t, wins, rank):
    """Return (accepted_third_vertex_Kz, [decorated tiles with that vertex]). The reader is
    vertex-only, so the gap SHAPE (third vertex) is unambiguous; mirror decorations that share
    the vertex are returned together and resolved separately."""
    acc = collections.defaultdict(list)
    for cand in cands:
        kz = Kz[dk(cand)]
        if kz is not None and accept(kz, t, wins, rank):
            acc[tuple(int(x) for x in kz)].append(cand)
    if len(acc) == 1:
        kz, tiles = next(iter(acc.items()))
        return dict(third_Kz=list(kz), tiles=[dk(x) for x in tiles])
    if not acc:
        return dict(third_Kz=None, tiles=[])       # none accepted (on/over a facet)
    return dict(third_Kz='MULTI', tiles=[dk(x) for ts in acc.values() for x in ts])  # genuine tie


# ---------- F(W) sampling grid (fixed rule) ----------
def sample_offsets(polygon, n_min=400, seed=20261110, facet_tol=1e-6, constraints=None, wins=None):
    xs = [v[0] for v in polygon]; ys = [v[1] for v in polygon]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    import random
    rng = random.Random(seed)
    poly = [complex(v[0], v[1]) for v in polygon]
    def inside(px, py):
        # ray cast + facet margin via constraints
        if constraints is not None:
            for rk, i, c in constraints:
                nx, ny = wins[rk]['normals'][i]; nrm = math.hypot(nx, ny)
                if (nx * px + ny * py - c) / nrm < facet_tol:
                    return False
            return True
        return False
    # deterministic grid: sqrt(n) x sqrt(n) lattice over bbox, keep inside, top up with seeded jitter
    g = max(2, int(math.ceil(math.sqrt(n_min * (x1 - x0) * (y1 - y0) / max(1e-9, _poly_area(polygon)))) ) + 1)
    pts, dropped = [], 0
    for ix in range(g):
        for iy in range(g):
            px = x0 + (ix + 0.5) * (x1 - x0) / g; py = y0 + (iy + 0.5) * (y1 - y0) / g
            if inside(px, py):
                pts.append((px, py))
            else:
                dropped += 1
    return pts, dropped

def _poly_area(poly):
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly))))


# ---------- the committed candidate c, witness tile ----------
def candidate_c(dd):
    wantk = set(C.keys(dd['want'])); wrong = [t for t in dd['got'] if dk(t) not in wantk]
    return wrong[0] if wrong else dd['got'][0]

def witness_tile(w, si, r):
    wit = next((x for x in QDIAG if x['case'] == f'w{w}-B-s{si}' and x['radius'] == r), None)
    if not wit or not wit.get('witness', {}).get('minimal'):
        return None
    tiles = [IW.dtile(t) for t in wit['witness']['minimal']['tiles']]
    return tiles[0] if tiles else None


# ---------- GATES (pre-protocol; do not read the scar gap) ----------
def gates():
    w, si, r = 7, 0, 2
    dd = first_disagreement(w, si, r); e = dd['edge']; band = dd['band']
    hw = math.pi / 8
    W, ang = committed_window(band, e, hw)
    sha = hashlib.sha256('\n'.join(sorted(C.keys(W))).encode()).hexdigest()
    pw = PROTO['w7-s0-r2']['windows']; plabel = [x for x in pw if 'hw0.3927' in x][0]
    print(f'[gate0] window |W|={len(W)} sha={sha[:12]} committed={pw[plabel]["sha256"][:12]} match={sha==pw[plabel]["sha256"]}')
    raw, payload, st = read_tiles(w, si, W)
    b1prim = next(x for x in B1['cases'][0]['windows'] if x['label'].startswith('ladder_hw0.3927'))
    print(f'[gate0] F(W) area={raw["area"]:.6e} (brief1 {b1prim["F_W"]["area"]:.6e})  '
          f'match={abs(raw["area"]-b1prim["F_W"]["area"])<1e-12}')
    wins, rank = windows_and_rank(payload)
    # Gate 1: ideal patch contains every tile of W as decorated triangle at >=21 offsets.
    # A W-vertex is accepted at t iff perp(K)-t in pentagon; a W TILE is in the ideal patch
    # iff all three of its vertices are accepted. We test this at the Chebyshev centre + 20 offsets.
    liftraw = raw; lift = {tuple(v): k for v, k in liftraw['lift']}
    (cx, cy), rr = chebyshev(raw['constraints'], wins)
    poly = raw['polygon']
    pts, dropped = sample_offsets(poly, 60, constraints=raw['constraints'], wins=wins)
    offs = [(cx, cy)] + pts[:25]
    g1 = []
    for (tx, ty) in offs:
        t = complex(tx, ty)
        ok = all(accept(lift[(round(z.real, 6), round(z.imag, 6))], t, wins, rank)
                 for tile in W for z in tile[1:])
        g1.append(ok)
    print(f'[gate1] offsets tested={len(offs)}  all-W-vertices-accepted={sum(g1)}/{len(offs)}  '
          f'(every W tile in the ideal patch)  cheb_centre=({cx:.4f},{cy:.4f}) r={rr:.4f}')
    # non-scar sanity: g(t) machinery on a TRUE-tile live site (not the scar edge)
    true_tiles = dd['baseline'][dd['step']]['added']
    bvk = {tuple(L.key(z)) for tile in band.tris for z in tile[1:]}
    site = None
    for t in true_tiles:
        for (pp, qq) in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if tuple(L.key(pp)) in bvk and tuple(L.key(qq)) in bvk:
                site = (pp, qq, GRID.centroid(band.tris), t); break
        if site:
            break
    pp, qq, rr_ref, ttrue = site
    Wn, _ = committed_window(band, (pp, qq, rr_ref), hw)
    cands, Kz, wins2, rank2 = gap_reader(w, si, Wn, (pp, qq, rr_ref))
    rawn, payn, stn = read_tiles(w, si, Wn)
    (c2x, c2y), _ = chebyshev(rawn['constraints'], wins2)
    g = g_of_t(cands, Kz, complex(c2x, c2y), wins2, rank2)
    # engine's true tile third vertex Kz (lift W+true)
    rawt, _, _ = read_tiles(w, si, list(Wn) + [ttrue])
    tv = third_vertex(ttrue, pp, qq); tvk = (round(tv.real, 6), round(tv.imag, 6))
    trueKz = {tuple(v): k for v, k in rawt['lift']}.get(tvk)
    same = (g['third_Kz'] is not None and g['third_Kz'] != 'MULTI'
            and tuple(g['third_Kz']) == tuple(int(x) for x in trueKz))
    print(f"[sanity] non-scar site: {len(cands)} geom candidates; g(cheb) third_Kz={g['third_Kz']} "
          f"tiles={len(g['tiles'])}; true third_Kz={list(trueKz)}; g_shape==true? {same}")


# ---------- measurement over an offset set ----------
def tile_vertices_Kz(w, si, W, tile):
    """lift W + tile, return {vkey: Kz} for the tile's vertices (consistent gauge)."""
    raw, _, st = read_tiles(w, si, list(W) + [tile])
    if st != 'ok':
        return None
    lift = {tuple(v): k for v, k in raw['lift']}
    out = {}
    for z in tile[1:]:
        out[(round(z.real, 6), round(z.imag, 6))] = lift.get((round(z.real, 6), round(z.imag, 6)))
    return out

def present(tileKz, t, wins, rank):
    if tileKz is None or any(k is None for k in tileKz.values()):
        return None
    return all(accept(k, t, wins, rank) for k in tileKz.values())

def f_polygon(w, si, W):
    raw, payload, st = read_tiles(w, si, W)
    if st != 'ok':
        return None, None, None, st
    wins, rank = windows_and_rank(payload)
    return raw, wins, rank, 'ok'

def measure(w, si, W, edge, cobj, wit, label, offsets=None):
    raw, wins, rank, st = f_polygon(w, si, W)
    if st != 'ok':
        return dict(label=label, status=st)
    area = raw['area']
    if area <= 1e-12:
        return dict(label=label, status='F_empty', area=area)
    if offsets is None:
        offsets, dropped = sample_offsets(raw['polygon'], 400, constraints=raw['constraints'], wins=wins)
    else:
        dropped = 0
    cands, Kz, _, _ = gap_reader(w, si, W, edge)
    cthird = tuple(int(x) for x in Kz[dk(cobj)]) if Kz.get(dk(cobj)) is not None else None
    witKz = tile_vertices_Kz(w, si, W, wit) if wit is not None else None
    shape_count = collections.Counter(); n_c = 0; n_w = 0; n_both = 0; n_multi = 0; n_none = 0
    g_by_offset = []
    for (tx, ty) in offsets:
        t = complex(tx, ty)
        g = g_of_t(cands, Kz, t, wins, rank)
        key = g['third_Kz']
        if key is None:
            n_none += 1; continue
        if key == 'MULTI':
            n_multi += 1; continue
        shape_count[tuple(key)] += 1
        is_c = (cthird is not None and tuple(key) == cthird)
        if is_c:
            n_c += 1
        w_present = present(witKz, t, wins, rank) if witKz is not None else None
        if w_present:
            n_w += 1
            if is_c:
                n_both += 1
        g_by_offset.append((tx, ty, list(key), bool(is_c), bool(w_present) if w_present is not None else None))
    nacc = sum(shape_count.values())
    distinct = []
    for kz, cnt in shape_count.most_common():
        tiles = [dk(x) for x in cands if Kz.get(dk(x)) is not None and tuple(int(v) for v in Kz[dk(x)]) == kz]
        distinct.append(dict(third_Kz=list(kz), fraction=round(cnt / nacc, 4), n=cnt,
                             is_c=(cthird is not None and kz == cthird), tiles=tiles))
    return dict(label=label, status='ok', area=area, n_offsets=len(offsets), n_accepted=nacc,
                n_dropped_grid=dropped, n_none=n_none, n_multi=n_multi,
                p_c=round(n_c / nacc, 4) if nacc else None,
                p_w=round(n_w / nacc, 4) if (nacc and witKz is not None) else None,
                p_both=round(n_both / nacc, 4) if nacc else None,
                c_third_Kz=list(cthird) if cthird else None,
                distinct_shapes=distinct, _offsets=offsets, _wins=wins, _rank=rank,
                _cands=cands, _Kz=Kz)

# ---------- controls (primary window + its offsets) ----------
def live_sites(dd, W):
    band = dd['band']; baseline = dd['baseline']; step = dd['step']
    wv = {tuple(L.key(z)) for t in W for z in t[1:]}
    sites = []
    for t in baseline[step]['added']:
        for (p, q) in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if tuple(L.key(p)) in wv and tuple(L.key(q)) in wv:
                sites.append((p, q, GRID.centroid(band.tris), t)); break
    return sites

def control_true_wrong(w, si, dd, W, offsets, wins, rank):
    sites = live_sites(dd, W); true_rows = []; wrong_rows = []
    for idx, (p, q, rref, ttrue) in enumerate(sites):
        edge = (p, q, rref)
        cands, Kz, _, _ = gap_reader(w, si, W, edge)
        # true tile shape
        tv = third_vertex(ttrue, p, q); traw, _, tst = read_tiles(w, si, list(W) + [ttrue])
        if tst != 'ok':
            continue
        tKz = {tuple(v): k for v, k in traw['lift']}.get((round(tv.real, 6), round(tv.imag, 6)))
        tKz = tuple(int(x) for x in tKz) if tKz is not None else None
        # wrong tile: first excluded decorated key
        legal = {dk(x) for x in D.candidates(dd['band'], p, q, rref)}
        geo = geometric_candidates(p, q, rref)
        excl = [geo_t for geo_t in sorted(geo, key=lambda x: repr(dk(x))) if dk(geo_t) not in legal]
        wtile = excl[0] if excl else None
        wthird = None
        if wtile is not None:
            wv = third_vertex(wtile, p, q); wr, _, wst = read_tiles(w, si, list(W) + [wtile])
            if wst == 'ok':
                wk = {tuple(v): k for v, k in wr['lift']}.get((round(wv.real, 6), round(wv.imag, 6)))
                wthird = tuple(int(x) for x in wk) if wk is not None else None
        dis = 0; nd = 0; wrong_hit = 0; nw = 0
        for (tx, ty) in offsets:
            g = g_of_t(cands, Kz, complex(tx, ty), wins, rank)
            k = g['third_Kz']
            if k is None or k == 'MULTI':
                continue
            nd += 1
            if tKz is not None and tuple(k) != tKz:
                dis += 1
            if wthird is not None:
                nw += 1
                if tuple(k) == wthird:
                    wrong_hit += 1
        true_rows.append(dict(site=idx, n_defined=nd, disagreements=dis))
        if wthird is not None:
            wrong_rows.append(dict(site=idx, n_defined=nw, wrong_is_ideal=wrong_hit))
    tot_dis = sum(r['disagreements'] for r in true_rows)
    return dict(true_tile=dict(total_disagreements=tot_dis, n_sites=len(true_rows), rows=true_rows),
                wrong_tile=dict(rows=wrong_rows,
                                wrong_is_ideal_total=sum(r['wrong_is_ideal'] for r in wrong_rows),
                                n_defined_total=sum(r['n_defined'] for r in wrong_rows)))

def control_two_sides(w, si, dd, W, edge, offsets):
    p, q = edge[0], edge[1]
    def side(tile):
        c = sum(tile[1:]) / 3
        return 1 if ((c - p) * (q - p).conjugate()).imag > 0 else -1
    A = [t for t in W if side(t) > 0]; Bside = [t for t in W if side(t) < 0]
    out = {}
    for name, half in (('sideA', A), ('sideB', Bside)):
        if len(half) < 3:
            out[name] = dict(n=len(half), status='too_small'); continue
        raw, wins, rank, st = f_polygon(w, si, half)
        out[name] = dict(n=len(half), status=st, area=(raw['area'] if st == 'ok' else None))
    return dict(n_sideA=len(A), n_sideB=len(Bside), halves=out)

def ordinary_scars(w, si, dd, W, offsets, wins, rank):
    """pinned scars where reduced AND full-history menus are both empty: g(t) there."""
    hist = dd['hist']; band = dd['band']; pinned = {frozenset(tuple(v) for v in ek) for ek in dd['m']['scars']}
    wv = {tuple(L.key(z)) for t in W for z in t[1:]}
    rows = []
    for e in hist.frontier():
        if AF.edge_id(*e[:2]) not in pinned:
            continue
        if not ({tuple(L.key(e[0])), tuple(L.key(e[1]))} <= wv):
            continue
        if C.keys(D.candidates(band, *e[:3])) or C.keys(D.candidates(hist, *e[:3])):
            continue  # want BOTH empty
        cands, Kz, _, _ = gap_reader(w, si, W, e)
        if not cands:
            rows.append(dict(edge=AF.frontier_id(e), n_candidates=0)); continue
        sc = collections.Counter()
        for (tx, ty) in offsets:
            g = g_of_t(cands, Kz, complex(tx, ty), wins, rank)
            if g['third_Kz'] not in (None, 'MULTI'):
                sc[tuple(g['third_Kz'])] += 1
        rows.append(dict(edge=AF.frontier_id(e), n_candidates=len(cands),
                         distinct_gap_shapes=len(sc), top=[[list(k), v] for k, v in sc.most_common(3)]))
    return rows

def run(outpath):
    cases_out = []; co_presence_any = []
    for (w, si, r), expect in CASES.items():
        dd = first_disagreement(w, si, r); e = dd['edge']; band = dd['band']
        assert dd['step'] == expect
        cobj = candidate_c(dd); wit = witness_tile(w, si, r)
        proto = PROTO[f'w{w}-s{si}-r{r}']
        # windows with F(W) non-empty, by committed rule
        windows = []
        for hw in GRID.HALFWIDTHS:
            W, _ = committed_window(band, e, hw)
            label = ('primary' if hw == GRID.HALFWIDTHS[0] else 'ladder') + f'_hw{round(hw,4)}'
            windows.append((label, hw, W))
        results = []; primary = None; prim_offsets = None
        for label, hw, W in windows:
            res = measure(w, si, W, e, cobj, wit, label)
            if res.get('status') == 'ok' and label.startswith('primary'):
                primary = res; prim_offsets = res['_offsets']
            results.append(res)
            if res.get('status') == 'ok' and (res.get('p_both') or 0) > 0:
                co_presence_any.append(f"w{w}-s{si}-r{r}/{label}")
        # controls on the primary window + its offsets
        controls = None
        if primary is not None:
            W = next(W for (lab, hw, W) in windows if lab.startswith('primary'))
            wins, rank = primary['_wins'], primary['_rank']
            controls = dict(
                true_wrong=control_true_wrong(w, si, dd, W, prim_offsets, wins, rank),
                two_sides=control_two_sides(w, si, dd, W, e, prim_offsets),
                ordinary_scars=ordinary_scars(w, si, dd, W, prim_offsets, wins, rank))
        # strip helper fields from results for JSON
        for res in results:
            for k in ('_offsets', '_wins', '_rank', '_cands', '_Kz'):
                res.pop(k, None)
        cases_out.append(dict(case=f'w{w}-s{si}-r{r}', world=w, si=si, radius=r, step=dd['step'],
                              edge=AF.frontier_id(e), candidate_c=repr(dk(cobj)),
                              witness=repr(dk(wit)) if wit is not None else None,
                              windows=results, controls=controls))
        p = next((x for x in results if x['label'].startswith('primary')), {})
        print(f"[gapfill] w{w}-s{si}-r{r}: primary p_c={p.get('p_c')} p_w={p.get('p_w')} p_both={p.get('p_both')} "
              f"shapes={len(p.get('distinct_shapes',[]))} true_dis="
              f"{(controls or {}).get('true_wrong',{}).get('true_tile',{}).get('total_disagreements')}", flush=True)
    prim = cases_out[0]
    pp = next(x for x in prim['windows'] if x['label'].startswith('primary'))
    gate_clean = (prim['controls']['true_wrong']['true_tile']['total_disagreements'] == 0)
    p_c = pp.get('p_c')
    if not gate_clean:
        cls = 'NO_HEADLINE (true-tile control disagreements; see table)'
    elif co_presence_any:
        cls = 'OVERRIDE: c and witness co-present in an ideal patch (see list) -- rejection is not a perfect-tiling fact'
    elif p_c == 0:
        cls = 'A. Address forbids (p_c = 0)'
    elif p_c == 1:
        cls = 'B. Address predicts (p_c = 1)'
    elif p_c is None:
        cls = 'D. Not readable (F(W) empty at primary)'
    else:
        cls = 'C. Address undecided (0 < p_c < 1)'
    summary = dict(primary_case='w7-s0-r2', primary_p_c=p_c, primary_p_w=pp.get('p_w'),
                   primary_p_both=pp.get('p_both'), true_tile_gate_clean=gate_clean,
                   co_presence_windows=co_presence_any, declared_outcome_class=cls)
    Path(outpath).write_text(json.dumps(dict(summary=summary, cases=cases_out), indent=2, default=repr) + '\n')
    print('\nDECLARED OUTCOME:', cls)
    print('wrote', outpath)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'gates'
    if mode == 'gates':
        gates()
    elif mode == 'run':
        run(sys.argv[2] if len(sys.argv) > 2 else str(HERE / 'address_gapfill.json'))
