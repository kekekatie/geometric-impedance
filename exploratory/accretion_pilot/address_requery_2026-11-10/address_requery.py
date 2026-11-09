"""
address_requery.py -- can the reduced live skin's hidden (perp-space) address reject,
through the frozen window reader, the tile its local rule wrongly admits at a dormant scar?

Runs Gate 0, the primary F(W) vs F(W+c) test, the window ladder, the four controls, both
reader conventions, both w7 streams, and the correlated 1S/3S/group-3 secondary instances.
Frozen engine/lift/reader (84130b9) are imported unchanged; the reader is reached only by
passing a tile list (append c = tiles+[c], no wrapper). Nothing feeds back into a constructor.

Env (as in the amber ablation):
  EFP_SNAPSHOT, AMBER_BASE_CACHE, AMBER_CACHE, AMBER_FORK_CACHE, MPLBACKEND=Agg, PYTHONUTF8=1
Writes results next to this file (pass an output path as argv[1]; default address_requery.json).
"""
import sys, os, math, json, hashlib, itertools, collections
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
AMBER = HERE.parent / 'amber_lobe_ablation_2026-11-06'
sys.path.insert(0, str(AMBER / 'src'))
import common as C
from common import AF, IW, L, D, S, dk
import readout as GRID
sys.path.insert(0, str(C.PILOT / 'referee_checks_2026-11-06' / 'src'))
import rc_common as RC
import functools
SR = RC.SR
SR.inverse = functools.lru_cache(maxsize=None)(SR.inverse)   # memoize coord inversion (as the amber readout does)
PERP = RC.PERP

TOL_R = 1e-9
BOX = 50.0
AREA_EMPTY = 1e-12
PRIMARY_HW = GRID.HALFWIDTHS[-1]
PROTO = json.loads((HERE / 'protocol_windows.json').read_text())
QDIAG = json.loads((AMBER / 'results' / 'query_diagnostics.json').read_text())
CASES = [(7, 0, 2, 35), (7, 1, 2, 35), (7, 0, 1, 26), (7, 0, 3, 37),
         (15, 0, 1, 42), (19, 0, 1, 42), (28, 0, 1, 42)]

# ---------- reader region + Chebyshev margin (feas.py formulation, replicated) ----------
_BASE = {}
def base_payload(w, si):
    if (w, si) not in _BASE:
        jp = C.old(f'jam-{w}-{si}.pkl')
        _BASE[(w, si)] = AF.RD.build_payload(jp['Sstar'], jp['cs'], [])
    return _BASE[(w, si)]

def chebyshev(constraints, windows):
    A, b = [], []
    for rk, i, c in constraints:
        nx, ny = windows[rk]['normals'][i]; nrm = math.hypot(nx, ny)
        if nrm < 1e-15:
            continue
        A.append([-nx / nrm, -ny / nrm, 1.0]); b.append(-c / nrm)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        A.append([float(sx), float(sy), 1.0]); b.append(BOX)
    if not A:
        return BOX, 'positive_area'
    res = linprog([0, 0, -1], A_ub=np.asarray(A), b_ub=np.asarray(b),
                  bounds=[(None, None)] * 3, method='highs')
    if res.status != 0 or res.x is None:
        return None, 'unresolved'
    r = float(res.x[2])
    cls = 'positive_area' if r > TOL_R else ('infeasible' if r < -TOL_R else 'lower_dimensional')
    return r, cls

def region(w, si, tiles):
    payload = dict(base_payload(w, si), tiles=[IW.etile(t) for t in tiles])
    try:
        raw = SR.read(payload)   # read() RAISES ReconstructionError; only its subprocess wrapper converts to a status
    except Exception as ex:
        return dict(status='unreconstructible', raw_status=f'{type(ex).__name__}: {ex}')
    if raw.get('status') != 'reconstructed':
        return dict(status='unreconstructible', raw_status=raw.get('status'))
    r, cls = chebyshev(raw['constraints'], payload['windows'])
    return dict(status='ok', area=float(raw['area']), cheb_r=r, cheb_cls=cls,
                constraints=raw['constraints'], lift=raw.get('lift'),
                windows=payload['windows'], rank=payload['rank'])

def nonempty(reg, conv):
    if reg['status'] != 'ok':
        return None
    return reg['area'] > AREA_EMPTY if conv == 'open' else (reg['cheb_r'] is not None and reg['cheb_r'] >= -TOL_R)

def classify(regW, regWc, conv):
    if regW['status'] != 'ok':
        return 'UNRECONSTRUCTIBLE'
    if not nonempty(regW, conv):
        return 'UNDEFINED'
    if regWc['status'] != 'ok':
        return 'UNRECONSTRUCTIBLE'
    return 'ADMIT' if nonempty(regWc, conv) else 'REJECT'

# ---------- Helly witness on an empty F(W+c) ----------
def witness(regWc, tiles_Wc):
    cons = regWc['constraints']; wins = regWc['windows']; rankmap = {int(k): v for k, v in regWc['rank'].items()}
    def feas(sub):
        r, _ = chebyshev(sub, wins); return r is not None and r >= -TOL_R
    minimal = None
    for k in (1, 2, 3):
        for sub in itertools.combinations(cons, k):
            if not feas(list(sub)):
                minimal = list(sub); break
        if minimal:
            break
    if minimal is None:
        return dict(found=False, note='no infeasible subset of size <=3 (open-empty but closed-feasible, or numerical)')
    # map each witness constraint to the retained tile(s) whose lifted vertex is binding
    vtiles = collections.defaultdict(list)
    for t in tiles_Wc:
        for z in t[1:]:
            vtiles[tuple(L.key(z))].append(repr(dk(t)))
    lift = {tuple(v): k for v, k in regWc['lift']}
    supply = []
    for rk, i, cval in minimal:
        nx, ny = wins[rk]['normals'][i]; h = wins[rk]['h']
        binders = []
        for vk, k in lift.items():
            if rankmap.get(int(sum(k))) != rk:
                continue
            z = sum(k[j] * PERP[j] for j in range(5))
            val = nx * z.real + ny * z.imag - h
            if abs(val - cval) <= 1e-7:
                binders.append(dict(vertex=list(vk), tiles=sorted(set(vtiles.get(vk, [])))))
        supply.append(dict(constraint=[rk, i, cval], binding_vertices=binders))
    return dict(found=True, n_constraints=len(minimal), constraints=minimal, supply=supply)

# ---------- reduced band + first disagreement + window rebuild ----------
def jam_of(w, si):
    rec, _ = C.old(f'verify-{w}-{si}.pkl'); return rec['jam_step']

def first_disagreement(w, si, r):
    states = C.load(f'w{w}-s{si}-r{r}-c0-states.pkl'); jam = jam_of(w, si)
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
                return dict(step=step, m=m, band=band, hist=hist, edge=e,
                            got=list(got), want=list(want), baseline=baseline, jam=jam)
    raise RuntimeError(f'no disagreement w{w}-s{si}-r{r}')

def comp_with(band_tiles, cen, ang, hw, anchor_keys):
    comps = GRID.edge_components(GRID.window(band_tiles, cen, ang, hw))
    withk = [cp for cp in comps if anchor_keys & {L.key(z) for t in cp for z in t[1:]}]
    return sorted((withk[0] if withk else comps[0]), key=dk) if comps else []

def sha(tiles):
    return hashlib.sha256(('\n'.join(sorted(C.keys(tiles)))).encode()).hexdigest()

# ---------- geometric candidates WITHOUT the legality filter (frozen template rule) ----------
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
    return out

# ---------- the test for one window ----------
def test_window(w, si, W, c, label):
    regW = region(w, si, W)
    regWc = region(w, si, list(W) + [c])
    rec = dict(label=label, n=len(W),
               F_W=dict(status=regW['status'], area=regW.get('area'), cheb_r=regW.get('cheb_r'), cls=regW.get('cheb_cls')),
               F_Wc=dict(status=regWc['status'], area=regWc.get('area'), cheb_r=regWc.get('cheb_r'), cls=regWc.get('cheb_cls')))
    for conv in ('open', 'closed'):
        rec[conv] = classify(regW, regWc, conv)
    if regWc['status'] == 'ok' and (not nonempty(regWc, 'closed')):
        rec['witness'] = witness(regWc, list(W) + [c])
    return rec

# ---------- controls ----------
def true_wrong_controls(w, si, d, cenpt):
    band = d['band']; baseline = d['baseline']; step = d['step']
    band_vkeys = {tuple(L.key(z)) for t in band.tris for z in t[1:]}
    true_tiles = baseline[step]['added']    # placements at the NEXT step (step+1, 1-indexed)
    sites = []
    for t in true_tiles:
        for (p, q) in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if tuple(L.key(p)) in band_vkeys and tuple(L.key(q)) in band_vkeys:
                sites.append((p, q, t)); break
    true_rows, wrong_rows = [], []
    anchor_all = set()
    for idx, (p, q, t_true) in enumerate(sites):
        mid = (p + q) / 2; ang = math.atan2((mid - cenpt).imag, (mid - cenpt).real)
        ek = {L.key(p), L.key(q)}
        W = comp_with(band.tris, cenpt, ang, PRIMARY_HW, ek)
        if not W:
            continue
        # true-tile
        tr = test_window(w, si, W, t_true, f'true-site{idx}')
        tr['edge'] = AF.frontier_id((p, q, 0j)); true_rows.append(tr)
        # wrong-tile: first excluded decorated candidate on this edge (reference = band centroid)
        legal_keys = {dk(x) for x in D.candidates(band, p, q, cenpt)}
        geo = geometric_candidates(p, q, cenpt)
        excl = [geo[k] for k in sorted(geo, key=lambda kk: repr(kk)) if k not in legal_keys]
        if excl:
            wr = test_window(w, si, W, excl[0], f'wrong-site{idx}')
            wr['edge'] = AF.frontier_id((p, q, 0j)); wr['wrong_tile'] = repr(dk(excl[0])); wrong_rows.append(wr)
    def false_rejects(rows):
        return {conv: sum(1 for r in rows if r['F_W']['status'] == 'ok'
                          and nonempty(dict(status='ok', area=r['F_W']['area'], cheb_r=r['F_W']['cheb_r']), conv)
                          and r[conv] == 'REJECT') for conv in ('open', 'closed')}
    def reject_rate(rows):
        out = {}
        for conv in ('open', 'closed'):
            defined = [r for r in rows if r[conv] in ('ADMIT', 'REJECT')]
            out[conv] = dict(n_defined=len(defined), n_reject=sum(1 for r in defined if r[conv] == 'REJECT'))
        return out
    return dict(n_sites=len(sites),
                true_tile=dict(false_rejects=false_rejects(true_rows), rows=true_rows),
                wrong_tile=dict(reject_rate=reject_rate(wrong_rows), rows=wrong_rows))

def restored_control(w, si, r, d, c):
    tag = f'w{w}-B-s{si}'
    wit = next((x for x in QDIAG if x['case'] == tag and x['radius'] == r), None)
    if not wit or not wit.get('witness', {}).get('minimal'):
        return dict(available=False, note='no recorded witness for this case/radius')
    extra = [IW.dtile(t) for t in wit['witness']['minimal']['tiles']]
    # primary window + witness restored
    proto = PROTO[f'w{w}-s{si}-r{r}']
    plabel = next(k for k in proto['windows'] if k.startswith('primary'))
    Wkeys = set(proto['windows'][plabel]['tile_keys'])
    W = [t for t in d['band'].tris if repr(dk(t)) in Wkeys]
    Wr = sorted({dk(t): t for t in (W + extra)}.values(), key=dk)
    rec = test_window(w, si, Wr, c, 'restored-primary')
    rec['n_witness_added'] = len(extra); rec['witness_keys'] = C.keys(extra)
    return dict(available=True, result=rec)

def displaced_control(w, si, d, c, ang0, cenpt):
    rows = []
    for frac, off in (('quarter', math.pi / 2), ('half', math.pi), ('three_quarter', 3 * math.pi / 2)):
        ang = ang0 + off
        W = comp_with(d['band'].tris, cenpt, ang, PRIMARY_HW, set())  # largest comp, far from scar
        if not W:
            rows.append(dict(offset=frac, note='empty window')); continue
        rec = test_window(w, si, W, c, f'displaced-{frac}')
        rows.append(rec)
    return rows

# ---------- lift of c anchored to the band ----------
def lift_candidate(band_tiles, c):
    try:
        K, pos, conf = RC.M.lift(list(band_tiles) + [c])
        addr = {str(tuple(L.key(z))): [int(x) for x in K[L.key(z)]] for z in c[1:] if L.key(z) in K}
        return dict(consistent=(len(conf) == 0), conflicts=len(conf), n_c_vertices_lifted=len(addr), addresses=addr)
    except Exception as ex:
        return dict(consistent=False, error=f'{type(ex).__name__}: {ex}')

# ---------- per-case driver ----------
def run_case(w, si, r, expect):
    d = first_disagreement(w, si, r)
    assert d['step'] == expect, (w, si, r, d['step'], expect)
    e = d['edge']; wantk = set(C.keys(d['want']))
    wrong = [t for t in d['got'] if dk(t) not in wantk]
    c = wrong[0] if wrong else d['got'][0]
    band = d['band']; cen = GRID.centroid(band.tris)
    mid = (e[0] + e[1]) / 2; ang = math.atan2((mid - cen).imag, (mid - cen).real)
    proto = PROTO[f'w{w}-s{si}-r{r}']
    # windows: rebuild by rule, ASSERT committed SHA
    windows = {}
    for hw in GRID.HALFWIDTHS:
        W = comp_with(band.tris, cen, ang, hw, {L.key(e[0]), L.key(e[1])})
        label = ('primary' if hw == PRIMARY_HW else 'ladder') + f'_hw{round(hw,4)}'
        assert sha(W) == proto['windows'][label]['sha256'], f'{label} SHA mismatch {w}-{si}-{r}'
        windows[label] = W
    whole = sorted(band.tris, key=dk)
    assert sha(whole) == proto['windows']['whole_live_skin']['sha256'], 'whole-skin SHA mismatch'
    windows['whole_live_skin'] = whole
    # lift c
    liftc = lift_candidate(band.tris, c)
    # primary test + ladder + whole
    win_results = [test_window(w, si, W, c, label) for label, W in windows.items()]
    # controls
    ctrl = dict(true_wrong=true_wrong_controls(w, si, d, cen),
                restored=restored_control(w, si, r, d, c),
                displaced=displaced_control(w, si, d, c, ang, cen))
    primary_label = next(k for k in windows if k.startswith('primary'))
    primary = next(x for x in win_results if x['label'] == primary_label)
    out = dict(case=f'w{w}-s{si}-r{r}', world=w, si=si, radius=r, step=d['step'],
               edge=AF.frontier_id(e), candidate_c=repr(dk(c)), full_menu_empty=(d['want'] == []),
               lift_c=liftc, windows=win_results,
               primary_open=primary['open'], primary_closed=primary['closed'], controls=ctrl)
    gate = ctrl['true_wrong']['true_tile']['false_rejects']
    print(f"[req] w{w}-s{si}-r{r} step{d['step']} primary open={primary['open']} closed={primary['closed']} "
          f"| true-tile false_rejects={gate} wrong-reject={ctrl['true_wrong']['wrong_tile']['reject_rate']}", flush=True)
    return out

def main():
    outpath = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / 'address_requery.json')
    results = [run_case(*args) for args in CASES]
    # headline: primary w7-s0, true-tile control clean
    prim = results[0]
    gate = prim['controls']['true_wrong']['true_tile']['false_rejects']
    clean = (gate['open'] == 0 and gate['closed'] == 0)
    po, pc = prim['primary_open'], prim['primary_closed']

    # cross-scale invariants, over every window of every case
    def same_F(wd):
        a, b = wd['F_W'], wd['F_Wc']
        if a['status'] != b['status']:
            return False
        if a['status'] != 'ok':
            return True
        return abs((a['area'] or 0) - (b['area'] or 0)) <= 1e-15 and abs((a['cheb_r'] or 0) - (b['cheb_r'] or 0)) <= 1e-12
    all_windows = [wd for cs in results for wd in cs['windows']]
    c_never_changes_F = all(same_F(wd) for wd in all_windows)
    reject_at_scar = [f"{cs['case']}/{wd['label']}/{conv}" for cs in results for wd in cs['windows']
                      for conv in ('open', 'closed') if wd[conv] == 'REJECT']
    # per-case ladder class span (did the class change with scale?)
    def span(cs):
        classes = {wd[conv] for wd in cs['windows'] for conv in ('open', 'closed')}
        return sorted(classes)
    primary_class_changes = len(set(span(prim))) > 1

    if not clean:
        outcome = 'NO_HEADLINE (true-tile control false-rejected; see table)'
    elif reject_at_scar:
        outcome = 'A/partial. Address rejects in some scar window (see list)'
    elif primary_class_changes:
        outcome = ('D. Split -- the class changes along the ladder (narrow half-widths ADMIT, '
                   'wide/undefined), and c never changes F at the scar, so there is no REJECT at any scale')
    elif po == 'UNDEFINED' and pc == 'UNDEFINED':
        outcome = 'C. Address undefined at the primary window'
    elif po == 'ADMIT' and pc == 'ADMIT':
        outcome = 'B. Address admits'
    else:
        outcome = 'D. Split'
    displaced_reject = [f"{cs['case']}/{x.get('label')}/{conv}" for cs in results
                        for x in cs['controls']['displaced'] if 'open' in x
                        for conv in ('open', 'closed') if x[conv] == 'REJECT']
    summary = dict(question='can the reduced skin hidden address reject c, the tile the local rule wrongly admits?',
                   primary_case='w7-s0-r2', primary_open=po, primary_closed=pc,
                   true_tile_control_clean=clean, true_tile_false_rejects=gate,
                   c_never_changes_F_at_scar=c_never_changes_F,
                   reject_at_scar_windows=reject_at_scar,
                   displaced_far_from_scar_rejects=displaced_reject,
                   primary_window_class_changes_with_scale=primary_class_changes,
                   declared_outcome_class=outcome,
                   plain='The window reader never rejects c at the scar (F(W+c) = F(W) at every scale and both '
                         'conventions); narrow windows ADMIT, wide windows are UNDEFINED; restoring the witness tile '
                         'does not change this; the only rejections of c occur in windows far from the scar. The shed '
                         'reason is not recoverable by this window reader.')
    (outpath).write_text(json.dumps(dict(summary=summary, cases=results), indent=2, default=repr) + '\n')
    print('\nDECLARED OUTCOME:', outcome)
    print('wrote', outpath)

if __name__ == '__main__':
    main()
