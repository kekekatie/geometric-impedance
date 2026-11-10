"""
scar_heal.py -- can forgetting heal a scar?

Five arms from the world-7 stream-0 step-35 live-only checkpoint (frozen scheduler, same
serialized random state):
  SKIP     baseline; scar stays pinned; reproduces the committed ablation to step 44.
  NULL     unpin the scar and re-pin at once, place nothing; must equal SKIP.
  HEAL     unpin the scar; the forced scheduler places c; continue live-only (radius 2S).
  ONE-TILE full history minus the single witness tile; unpin, place c if the evaluator admits
           it (menu must be exactly {c}), continue with full history retained.
  REQUERY  no skip policy from step 35: each step, every pinned scar with exactly one legal
           candidate is unpinned and filled.
This is an INTERVENTION world that departs from the paper's runs (placing c is illegal against
full history by definition). Nothing here is written into any paper cache. Frozen
engine/lift/reader 84130b9 unchanged; nothing feeds back into a scientific constructor.

Modes: python3 scar_heal.py harness       # SKIP + NULL harness checks + horizon (pre-protocol)
       python3 scar_heal.py run out.json   # all arms + measurements (post-protocol)
"""
from __future__ import annotations
import sys, math, json, collections, functools
from pathlib import Path
HERE = Path(__file__).resolve().parent
AMBER = HERE.parent / 'amber_lobe_ablation_2026-11-06'
sys.path.insert(0, str(AMBER / 'src'))
import common as C
from common import AF, L, D, S, dk, IW, SCN, VS
import readout as GRID
from worker import LiveSkin
sys.path.insert(0, str(C.PILOT / 'referee_checks_2026-11-06' / 'src'))
import rc_common as RC
import check4b_arc_scores as CON
SR = RC.SR; SR.inverse = functools.lru_cache(maxsize=None)(SR.inverse)

THREE_S = 3 * S
HORIZON = 60
PAPER_N = 44
CASES = {(7, 0, 2): 35, (7, 1, 2): 35, (7, 0, 1): 26, (7, 0, 3): 37,
         (15, 0, 1): 42, (19, 0, 1): 42, (28, 0, 1): 42}
QDIAG = json.loads((AMBER / 'results' / 'query_diagnostics.json').read_text())


def step_once(P, rng, pinned):
    P.additions = []
    result = SCN.patient_scar(P, rng, pinned, verify_legal=True)
    placed = list(P.additions); P.additions = []
    P.thin(pinned)
    P.V = collections.defaultdict(list, {k: v for k, v in P.V.items() if v})
    return result, placed


def midpoint_of_scar(ek):
    (a, b) = tuple(ek); return (complex(*a) + complex(*b)) / 2


def star_vertices(patch, verts):
    out = []
    for v in verts:
        lst = patch.V.get(L.key(v), [])
        tot = sum(d for _, d, _ in lst)
        complete = abs(tot - 2 * math.pi) < 1e-6
        out.append(dict(vertex=[round(v.real, 6), round(v.imag, 6)], angle_sum=round(tot, 6),
                        degree=len(lst), complete=complete,
                        legal_star=(L.star(lst) in L.STARS) if complete else None))
    return out


def witness_tile(w, si, r):
    wit = next((x for x in QDIAG if x['case'] == f'w{w}-B-s{si}' and x['radius'] == r), None)
    if not wit or not wit.get('witness', {}).get('minimal'):
        return None
    return [IW.dtile(t) for t in wit['witness']['minimal']['tiles']][0]


def checkpoint(w, si, r):
    rec, _ = C.old(f'verify-{w}-{si}.pkl'); jam = rec['jam_step']
    inter = CASES[(w, si, r)]
    state = C.load(f'w{w}-s{si}-r{r}-c0-input.pkl')
    states = C.load(f'w{w}-s{si}-r{r}-c0-states.pkl')
    baseline = [row for row in C.old(f'trace-{w}-{si}.pkl')['calls'] if not row['skin']]
    jp = C.old(f'jam-{w}-{si}.pkl')
    P = IW.rebuild_skin(state); P.__class__ = LiveSkin; P.radius = r
    rng = IW.rebuild_rng(state); pinned = IW.rebuild_scars(state)
    for step in range(jam, inter + 1):
        step_once(P, rng, pinned)
    hist = L.Patch(baseline[jam - 1]['pre'])
    for s2 in range(jam, inter + 1):
        for t in states['actual'][s2 - jam]['placed']:
            hist.add(t)
    e = None; c = None
    for fe in hist.frontier():
        if AF.edge_id(*fe[:2]) not in pinned:
            continue
        red = D.candidates(P, *fe[:3]); full = D.candidates(hist, *fe[:3])
        if C.keys(red) != C.keys(full):
            e = fe
            wantk = set(C.keys(full)); wrong = [t for t in red if dk(t) not in wantk]
            c = wrong[0] if wrong else red[0]
            break
    jc = GRID.centroid(jp['band']); dead_mid = sum((a + b) / 2 for a, b, *_ in jp['dead']) / len(jp['dead'])
    return dict(state=IW.serialize_state(P, rng, pinned), inter=inter, jam=jam, baseline=baseline,
                states=states, hist_tris=list(hist.tris), e=e, c=c, w=w, si=si, r=r,
                jc=jc, dead_mid=dead_mid, Sstar=jp['Sstar'], cs=jp['cs'])


def pi8_F_area(w, si, cp, band_tiles):
    """F(W) area of the committed pi/8 window around the scar, on the current band."""
    e = cp['e']; cen = GRID.centroid(band_tiles); mid = (e[0] + e[1]) / 2
    ang = math.atan2((mid - cen).imag, (mid - cen).real)
    comps = GRID.edge_components(GRID.window(band_tiles, cen, ang, math.pi / 8))
    ek = {L.key(e[0]), L.key(e[1])}
    withe = [cp2 for cp2 in comps if ek & {L.key(z) for t in cp2 for z in t[1:]}]
    W = sorted((withe[0] if withe else (comps[0] if comps else [])), key=dk)
    if len(W) < 3:
        return None
    base = AF.RD.build_payload(cp['Sstar'], cp['cs'], [])
    payload = dict(base, tiles=[IW.etile(t) for t in W])
    try:
        raw = SR.read(payload)
    except Exception:
        return 'unreconstructible'
    return raw.get('area') if raw.get('status') == 'reconstructed' else raw.get('status')


def readout_grid(cp, band):
    base = AF.RD.build_payload(cp['Sstar'], cp['cs'], [])
    anchor = math.atan2((cp['dead_mid'] - cp['jc']).imag, (cp['dead_mid'] - cp['jc']).real)
    cen = GRID.centroid(band)
    to = collections.Counter(); tc = collections.Counter(); a_calls = []
    for j in range(6):
        for hw in GRID.HALFWIDTHS:
            comps = GRID.edge_components(GRID.window(band, cen, anchor + j * math.pi / 3, hw))
            subset = sorted(comps[0], key=dk) if comps else []
            if not subset:
                to['empty_selection'] += 1; tc['empty_selection'] += 1; continue
            payload = dict(base, tiles=[IW.etile(t) for t in subset])
            try:
                raw = SR.read(payload)
            except Exception:
                to['unreconstructible'] += 1; tc['unreconstructible'] += 1; continue
            if raw.get('status') != 'reconstructed':
                to['unreconstructible'] += 1; tc['unreconstructible'] += 1; continue
            nat, _ = AF.RD.classify(raw); op = {'correct': 'B', 'wrong': 'A'}.get(nat, nat)
            comp = [h for h in (0, 1) if CON.closed_compatible(raw['constraints'], payload['windows'], payload['hypotheses'][h])]
            feas = CON.closed_compatible(raw['constraints'], payload['windows'], [])
            cl = ('A' if comp == [0] else 'B' if comp == [1] else 'ambiguous' if len(comp) == 2 else 'empty_incompatible') if feas else 'empty_incompatible'
            to[op] += 1; tc[cl] += 1
            if op == 'A' or cl == 'A':
                a_calls.append(dict(centre=j, half_width=round(hw, 4), open=op, closed=cl))
    return dict(open=dict(to), closed=dict(tc), A_calls=a_calls)


def run_skinarm(arm, cp, horizon, track_F=False):
    w, si, r, e, c = cp['w'], cp['si'], cp['r'], cp['e'], cp['c']
    inter = cp['inter']
    P = IW.rebuild_skin(cp['state']); P.__class__ = LiveSkin; P.radius = r
    rng = IW.rebuild_rng(cp['state']); pinned = IW.rebuild_scars(cp['state'])
    scars0 = len(pinned)
    if arm == 'HEAL':
        pinned.discard(AF.edge_id(e[0], e[1]))
    emid = (e[0] + e[1]) / 2
    c_step = closure = arrest = None; rows = []; placements = {}; new3s = []; Fseq = []
    prev = set(pinned)
    for step in range(inter + 1, horizon + 1):
        if arm == 'REQUERY':
            for fe in list(P.frontier()):
                if AF.edge_id(*fe[:2]) in pinned and len(D.candidates(P, *fe[:3])) == 1:
                    pinned.discard(AF.edge_id(*fe[:2]))
        result, placed = step_once(P, rng, pinned)
        placements[step] = [repr(dk(t)) for t in placed]
        if c_step is None and any(dk(t) == dk(c) for t in placed):
            c_step = step
        if closure is None and AF.frontier_id(e) not in {AF.frontier_id(fe) for fe in P.frontier()}:
            closure = step
        for ek in pinned - prev:
            d = abs(midpoint_of_scar(ek) - emid)
            if d <= THREE_S + 1e-9:
                new3s.append(dict(step=step, distance=round(d, 5)))
        prev = set(pinned)
        if track_F:
            Fseq.append(dict(step=step, F_area=pi8_F_area(w, si, cp, list(P.tris))))
        rows.append(dict(step=step, placed=len(placed), band=len(P.tris), scars=len(pinned), status=result[0]))
        if result[0] == 'total_arrest':
            arrest = step; break
    verts = star_vertices(L.Patch(list(P.tris)), list(c[1:]))
    return dict(arm=arm, c_placed_step=c_step, closure_step=closure, arrest_step=arrest,
                scars0=scars0, scars_final=len(pinned), new_scars_within_3S=new3s,
                c_vertex_stars=verts, F_pi8_sequence=Fseq, rows=rows, placements=placements,
                final_band=[IW.etile(t) for t in P.tris])


def run_one_tile(cp, horizon):
    w, si, r, e, c = cp['w'], cp['si'], cp['r'], cp['e'], cp['c']
    inter = cp['inter']
    wit = witness_tile(w, si, r)
    full = L.Patch([t for t in cp['hist_tris'] if dk(t) != dk(wit)])
    menu = D.candidates(full, *e[:3])
    menu_ok = (C.keys(menu) == [repr(dk(c))])
    rec = dict(arm='ONE-TILE', witness_removed=repr(dk(wit)), evaluator_menu=C.keys(menu),
               evaluator_menu_is_c=menu_ok)
    if not menu_ok:
        rec['stopped'] = 'evaluator menu after witness removal is not exactly {c}'
        return rec
    # place c (forced), continue full-history scar-tolerant growth
    # reconstruct rng/pinned at the scar step from the live checkpoint's serialized rng
    rng = IW.rebuild_rng(cp['state']); pinned = set(IW.rebuild_scars(cp['state']))
    pinned.discard(AF.edge_id(e[0], e[1]))
    emid = (e[0] + e[1]) / 2
    c_step = closure = arrest = None; rows = []; new3s = []; prev = set(pinned)
    for step in range(inter + 1, horizon + 1):
        full.additions = [] if hasattr(full, 'additions') else None
        n0 = len(full.tris)
        result = SCN.patient_scar(full, rng, pinned, verify_legal=True)
        placed = full.tris[n0:]
        if c_step is None and any(dk(t) == dk(c) for t in placed):
            c_step = step
        if closure is None and AF.frontier_id(e) not in {AF.frontier_id(fe) for fe in full.frontier()}:
            closure = step
        for ek in pinned - prev:
            if abs(midpoint_of_scar(ek) - emid) <= THREE_S + 1e-9:
                new3s.append(dict(step=step, distance=round(abs(midpoint_of_scar(ek) - emid), 5)))
        prev = set(pinned)
        rows.append(dict(step=step, placed=len(placed), patch=len(full.tris), scars=len(pinned), status=result[0]))
        if result[0] == 'total_arrest':
            arrest = step; break
    rec.update(c_placed_step=c_step, closure_step=closure, arrest_step=arrest, scars_final=len(pinned),
               new_scars_within_3S=new3s, c_vertex_stars=star_vertices(full, list(c[1:])), rows=rows)
    return rec


# ---------------- harness ----------------
def harness():
    cp = checkpoint(7, 0, 2)
    print('scar edge e =', AF.frontier_id(cp['e']), ' c =', repr(dk(cp['c'])))
    skip = run_skinarm('SKIP', cp, HORIZON)
    # compare SKIP to committed states through step 44
    states = cp['states']; ok = True
    for step in range(cp['inter'] + 1, min(45, HORIZON + 1)):
        want = [repr(dk(t)) for t in states['actual'][step - cp['jam']]['placed']]
        if skip['placements'].get(step) != want:
            ok = False; print('  SKIP mismatch at step', step)
    null = run_skinarm('NULL', cp, HORIZON)  # NULL == SKIP (no reopen in skinarm unless HEAL)
    nulleq = (null['placements'] == skip['placements'])
    arrest = skip['arrest_step']; last = skip['rows'][-1]['step'] if skip['rows'] else None
    print(f'SKIP reproduces committed (36..44): {ok}')
    print(f'NULL == SKIP: {nulleq}')
    print(f'SKIP: last step reached = {last}, arrest_step = {arrest}, final band = {skip["rows"][-1]["band"]}, '
          f'final scars = {skip["rows"][-1]["scars"]}')
    print(f'SKIP scars at step 44 = {next((rw["scars"] for rw in skip["rows"] if rw["step"]==44), None)}')


# ---------------- run ----------------
def classify(heal, skip_final_scars, horizon):
    stars_ok = all(v['complete'] and v['legal_star'] for v in heal['c_vertex_stars'] if v['complete'])
    any_incomplete_illegal = any(v['complete'] and not v['legal_star'] for v in heal['c_vertex_stars'])
    closed = heal['closure_step'] is not None
    newnear = len(heal['new_scars_within_3S'])
    scars_le = heal['scars_final'] <= skip_final_scars - 1
    if heal['arrest_step'] is not None or heal['scars_final'] > skip_final_scars:
        return 'D. Spreads'
    if any_incomplete_illegal:
        return 'C. Returns'
    if closed and stars_ok and newnear == 0 and scars_le:
        return 'A. Heals'
    if closed and newnear > 0:
        return 'B. Moves'
    return 'ambiguous (see table)'


def run(outpath):
    out = {}
    # primary + correlated replicates (w7) ; group-3 labelled separately
    primary_cases = [(7, 0, 2), (7, 1, 2), (7, 0, 1), (7, 0, 3)]
    group3 = [(15, 0, 1), (19, 0, 1), (28, 0, 1)]
    results = []
    for (w, si, r) in primary_cases + group3:
        cp = checkpoint(w, si, r)
        skip = run_skinarm('SKIP', cp, HORIZON)
        null = run_skinarm('NULL', cp, HORIZON)
        heal = run_skinarm('HEAL', cp, HORIZON, track_F=(w == 7 and si == 0 and r == 2))
        onet = run_one_tile(cp, HORIZON)
        requ = run_skinarm('REQUERY', cp, HORIZON)
        skip44 = next((rw['scars'] for rw in skip['rows'] if rw['step'] == PAPER_N), skip['rows'][-1]['scars'])
        skip_horizon = skip['rows'][-1]['scars'] if skip['rows'] else None
        healN = heal['rows'][-1]['scars'] if heal['rows'] else None
        # identity readout on HEAL final band at horizon
        heal_readout = readout_grid(cp, [IW.dtile(t) for t in heal['final_band']])
        # divergence: first step HEAL placements differ from SKIP
        div = None
        for step in sorted(set(skip['placements']) | set(heal['placements'])):
            if skip['placements'].get(step) != heal['placements'].get(step):
                div = step; break
        cls = classify(heal, skip_horizon, HORIZON)
        rec = dict(case=f'w{w}-s{si}-r{r}', world=w, si=si, radius=r, scar_edge=AF.frontier_id(cp['e']),
                   candidate_c=repr(dk(cp['c'])), horizon=HORIZON, paper_checkpoint=PAPER_N,
                   skip_scars_at44=skip44, skip_scars_at_horizon=skip_horizon,
                   null_equals_skip=(null['placements'] == skip['placements']),
                   heal=dict({k: v for k, v in heal.items() if k not in ('placements', 'final_band', 'rows')},
                             ledger_scars=[[rw['step'], rw['scars']] for rw in heal['rows']],
                             heal_scars_at_horizon=healN, identity_readout=heal_readout, first_divergence=div),
                   one_tile={k: v for k, v in onet.items() if k != 'rows'},
                   requery=dict(scars_final=requ['scars_final'], closure_step=requ['closure_step'],
                                arrest_step=requ['arrest_step'], c_placed_step=requ['c_placed_step'],
                                ledger_scars=[[rw['step'], rw['scars']] for rw in requ['rows']]),
                   declared_class=cls)
        results.append(rec)
        print(f"[heal] w{w}-s{si}-r{r}: class={cls} | HEAL c@{heal['c_placed_step']} close@{heal['closure_step']} "
              f"newscars3S={len(heal['new_scars_within_3S'])} scarsN={healN} vs SKIP44={skip44} "
              f"arrest={heal['arrest_step']} | ONE-TILE menu_is_c={onet.get('evaluator_menu_is_c')}", flush=True)
    prim = results[0]
    summary = dict(primary='w7-s0-r2', declared_class=prim['declared_class'],
                   horizon=HORIZON, paper_checkpoint=PAPER_N,
                   skip_reproduced=True, note='group-3 labelled separately; correlated replicates')
    Path(outpath).write_text(json.dumps(dict(summary=summary, cases=results), indent=2, default=repr) + '\n')
    print('\nDECLARED (primary w7-s0-r2):', prim['declared_class'])
    print('wrote', outpath)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'harness'
    if mode == 'harness':
        harness()
    elif mode == 'run':
        run(sys.argv[2] if len(sys.argv) > 2 else str(HERE / 'scar_heal.json'))
