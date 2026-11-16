"""Pass 2 execution (frozen by PROTOCOL_PASS2.md). Subcommands: primary, stress, caps.

Decodes the frozen k=3 sample and the stress panel, and runs the cap-sensitivity
comparison. All design choices are frozen in PROTOCOL_PASS2.md; this only runs them.
"""
import sys, json, time
import numpy as np
from pathlib import Path
import nd_infer, nd_run, pass2_sample

SITE = (2, 2); P = 1e-3
ODDS = P / (1 - P)
ARMS = nd_infer.ARMS
BOOT_SEED = 20261117
B_BOOT = 10000
PI = [0.691003, 0.255927, 0.047266, 0.005804]     # model weights within k<=3 (frozen)
P_GE4 = 0.000574                                    # Binomial(370,1e-3), frozen
CRED = {0.0: 0, 0.5: 1, 1.0: 2}
R = Path(__file__).resolve().parents[1] / 'results'


def make_decoder(w_frame=3, w_dec=3):
    return nd_infer.Decoder(5, SITE, w_frame=w_frame, w_dec=w_dec, p=P)


def credits(r, truth):
    hard = 1.0 if r['label'] == truth else 0.0
    tie = 0.5 if r['tie'] else hard
    return hard, tie


def loss_contribs(onset, vx, vz):
    return (([('X', SITE, onset)] if vx else []) + ([('Z', SITE, onset)] if vz else []))


def variants():
    for onset in (1, 2):
        for vx in (0, 1):
            for vz in (0, 1):
                yield onset, vx, vz


def decode_histories(D, extra_lists, label='', collect_records=False):
    """extra_lists: iterable of (tag, tuple-of-extra-primitive-contribs). For each,
    run the 8 variants. Returns per-group arrays and global accumulators. With
    collect_records, also groups histories by committed record (what thick sees) to
    find same-record opposite-truth ambiguities empirically."""
    s = D.s
    arms = ARMS
    # per-group (triple/config) summed paired diffs, for cluster bootstrap
    g_tt_tie, g_tt_hard, g_dt_tie, g_dt_hard = [], [], [], []
    glob = {a: dict(tie=0.0, hard=0.0, tie_count=0) for a in arms}
    grid = {'thick_vs_thin': np.zeros((3, 3)), 'diamond_vs_thin': np.zeros((3, 3))}
    whole_label_ne = 0; whole_post_ne = 0
    records = {}            # rec_hash -> {'truths': set, 'n': int, 'thick_tie': int}
    nhist = 0; start = time.time(); ng = 0
    for extra in extra_lists:
        ng += 1
        s_tt_tie = s_tt_hard = s_dt_tie = s_dt_hard = 0.0
        for onset, vx, vz in variants():
            fts = tuple(extra) + tuple(loss_contribs(onset, vx, vz))
            DZ, DX, truth, _ = s.simulate(*nd_run.compose(fts))
            cr = {}
            rr = {}
            for arm in arms:
                r = D.direct(DZ, DX, arm)
                rr[arm] = r
                h, t = credits(r, truth)
                cr[arm] = (h, t)
                g = glob[arm]; g['hard'] += h; g['tie'] += t; g['tie_count'] += int(r['tie'])
            if collect_records:
                rh = hash(tuple(sorted((k, int(v)) for k, v in {**DZ, **DX}.items())))
                rec = records.get(rh)
                if rec is None:
                    rec = records[rh] = dict(truths=set(), n=0, thick_tie=0)
                rec['truths'].add(int(truth)); rec['n'] += 1; rec['thick_tie'] += int(rr['thick']['tie'])
            s_tt_tie += cr['thick'][1] - cr['thin'][1]
            s_tt_hard += cr['thick'][0] - cr['thin'][0]
            s_dt_tie += cr['diamond'][1] - cr['thin'][1]
            s_dt_hard += cr['diamond'][0] - cr['thin'][0]
            grid['thick_vs_thin'][CRED[cr['thick'][1]]][CRED[cr['thin'][1]]] += 1
            grid['diamond_vs_thin'][CRED[cr['diamond'][1]]][CRED[cr['thin'][1]]] += 1
            if rr['whole']['label'] != rr['thick']['label']:
                whole_label_ne += 1
            if abs(rr['whole']['p0'] - rr['thick']['p0']) > nd_infer.EPS:
                whole_post_ne += 1
            nhist += 1
        g_tt_tie.append(s_tt_tie / 8); g_tt_hard.append(s_tt_hard / 8)
        g_dt_tie.append(s_dt_tie / 8); g_dt_hard.append(s_dt_hard / 8)
        if label and ng % 5000 == 0:
            print(label, ng, 'groups', nhist, 'hist', round(time.time() - start, 1), 's', flush=True)
    return dict(
        g_tt_tie=np.array(g_tt_tie), g_tt_hard=np.array(g_tt_hard),
        g_dt_tie=np.array(g_dt_tie), g_dt_hard=np.array(g_dt_hard),
        glob=glob, grid=grid, whole_label_ne=whole_label_ne, whole_post_ne=whole_post_ne,
        records=records, nhist=nhist, ngroup=ng, elapsed=round(time.time() - start, 1))


def cluster_ci(per_group, B=B_BOOT, seed=BOOT_SEED):
    d = np.asarray(per_group); n = len(d); rng = np.random.default_rng(seed)
    mean = float(d.mean())
    means = np.empty(B)
    step = 500
    for i in range(0, B, step):
        m = min(step, B - i)
        idx = rng.integers(0, n, size=(m, n))
        means[i:i + m] = d[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    se = float(d.std(ddof=1) / np.sqrt(n))
    return dict(mean=mean, ci_lo=float(lo), ci_hi=float(hi), boot_se=float(means.std(ddof=1)),
                cluster_se=se, normal_lo=mean - 1.96 * se, normal_hi=mean + 1.96 * se)


def grid_decomp(g):
    cells = {(i, j): float(g[i][j]) for i in range(3) for j in range(3)}
    tot = sum(cells.values()) or 1.0
    A_ahead = sum(w for (i, j), w in cells.items() if i > j)
    B_ahead = sum(w for (i, j), w in cells.items() if j > i)
    tie_inv = sum(w for (i, j), w in cells.items() if i == 1 or j == 1)
    return dict(A_only=cells[(2, 0)] / tot, B_only=cells[(0, 2)] / tot,
                both_right=cells[(2, 2)] / tot, both_wrong=cells[(0, 0)] / tot,
                A_ahead=A_ahead / tot, B_ahead=B_ahead / tot, net=(A_ahead - B_ahead) / tot,
                tie_involved=tie_inv / tot)


def primary(limit=None):
    D = make_decoder()
    prims = pass2_sample.primitives()
    triples, h = pass2_sample.draw()
    if limit:
        triples = triples[:limit]
    extra_lists = ([prims[a], prims[b], prims[c]] for a, b, c in triples)
    res = decode_histories(D, extra_lists, label='primary')
    n = res['nhist']
    out = dict(kind='primary', d=5, site=list(SITE), seed=pass2_sample.SEED, sample_sha256=h,
               n_triples=len(triples), nhist=n, w_frame=3, w_dec=3,
               arms={a: dict(tie_truth=round(res['glob'][a]['tie'] / n, 6),
                             hard_truth=round(res['glob'][a]['hard'] / n, 6),
                             tie_count=res['glob'][a]['tie_count'],
                             tie_wfrac=round(res['glob'][a]['tie_count'] / n, 6)) for a in ARMS},
               pairs={pr: grid_decomp(res['grid'][pr]) for pr in res['grid']},
               whole_vs_thick=dict(label_ne=res['whole_label_ne'], post_ne=res['whole_post_ne']),
               within_k3=dict(
                   thick_minus_thin=dict(tie=cluster_ci(res['g_tt_tie']), hard=cluster_ci(res['g_tt_hard'])),
                   diamond_minus_thin=dict(tie=cluster_ci(res['g_dt_tie']), hard=cluster_ci(res['g_dt_hard']))),
               elapsed=res['elapsed'])
    # combine with Pass 1 exact k=0,1,2 margins (tie-aware)
    try:
        p1 = json.load(open(R / 'pass1_report.json'))
        wk = p1['within_stratum_margin_thick_thin']['d5']
        m_k = [wk['0']['tie'], wk['1']['tie'], wk['2']['tie'], out['within_k3']['thick_minus_thin']['tie']['mean']]
        combined = sum(PI[k] * m_k[k] for k in range(4))
        ci = out['within_k3']['thick_minus_thin']['tie']
        comb_lo = sum(PI[k] * m_k[k] for k in range(3)) + PI[3] * ci['ci_lo']
        comb_hi = sum(PI[k] * m_k[k] for k in range(3)) + PI[3] * ci['ci_hi']
        out['combined_thick_minus_thin_k_le_3'] = dict(
            pi=PI, k_margins_tie=m_k, combined=round(combined, 8),
            combined_ci=[round(comb_lo, 8), round(comb_hi, 8)],
            benchmark_0p4pp_combined=round(PI[3] * 0.004, 8), p_ge4=P_GE4)
    except FileNotFoundError:
        pass
    tag = 'pass2_primary' + (f'_lim{limit}' if limit else '')
    (R / f'{tag}.json').write_text(json.dumps(out, indent=2) + '\n')
    tt = out['within_k3']['thick_minus_thin']['tie']; dt = out['within_k3']['diamond_minus_thin']['tie']
    print(f"thick-thin(k3) tie mean {tt['mean']:.6f} CI [{tt['ci_lo']:.6f},{tt['ci_hi']:.6f}]")
    print(f"diamond-thin(k3) tie mean {dt['mean']:.6f} CI [{dt['ci_lo']:.6f},{dt['ci_hi']:.6f}]")
    if 'combined_thick_minus_thin_k_le_3' in out:
        c = out['combined_thick_minus_thin_k_le_3']
        print(f"combined k<=3 thick-thin {c['combined']:.8f} CI {c['combined_ci']} benchmark {c['benchmark_0p4pp_combined']}")
    print('elapsed', out['elapsed'])


# ---------------- stress panel ----------------
import itertools


def p_loc(s):
    """Local primitive set: X/Z on the 9 neighbourhood data qubits + MZ/MX on the
    four star stabs, rounds 0-4. (110 primitives.)"""
    star = sorted(s.STAR[SITE])
    Ndata = set()
    for k in star:
        for q in s.STABS[k]['support']:
            Ndata.add(q)
    prims = []
    for q in sorted(Ndata):
        for t in range(5):
            for tag in ('X', 'Z'):
                prims.append((tag, q, t))
    for k in star:
        tag = 'MZ' if k in s.ZSTABS else 'MX'
        for t in range(5):
            prims.append((tag, k, t))
    return prims, sorted(Ndata)


def crossing_reps(s, sector):
    """Minimum-weight representatives of the sector logical whose support includes
    data (2,2). Z_L (X-sector) -> X-faults; X_L (Z-sector) -> Z-faults. Search the
    logical's coset over all stabilizer subsets of that sector."""
    nd = s.NDATA; j0 = s.DIDX[SITE]
    base = list(s.LZ) if sector == 'X' else list(s.XL)
    stab_ids = s.ZSTABS if sector == 'X' else s.XSTABS
    rows = []
    for k in stab_ids:
        row = [0] * nd
        for q in s.STABS[k]['support']:
            row[s.DIDX[q]] = 1
        rows.append(row)
    best_w = None; reps = []
    for m in range(1 << len(rows)):
        v = base[:]
        mm = m; i = 0
        while mm:
            if mm & 1:
                v = [a ^ b for a, b in zip(v, rows[i])]
            mm >>= 1; i += 1
        if not v[j0]:
            continue
        w = sum(v)
        if best_w is None or w < best_w:
            best_w = w; reps = [v]
        elif w == best_w:
            reps.append(v)
    faulttag = 'X' if sector == 'X' else 'Z'
    out = []
    for v in reps:
        qs = [s.DATA[i] for i in range(nd) if v[i]]
        out.append((faulttag, qs))                 # support including (2,2)
    return best_w, out


def _decode_safe(D, DZ, DX, arm):
    try:
        return D.direct(DZ, DX, arm)
    except ValueError:
        return dict(label=None, p0=None, p1=None, tie=None, undecodable=True)


def seam_pairs(D, max_reps=6):
    """Rigorous balanced ambiguous pairs. For each min-weight (2,2)-crossing logical
    rep L (weight 5 -> four non-(2,2) qubits), split those four into 2+2 as H_A,H_B
    (both weight 2, so decodable at w_dec=3). H_A and H_B differ by L\\{(2,2)}, whose
    syndrome is exactly the (2,2)-erasure-freed star detectors, so they differ ONLY
    there; the decoder marginalizes the erasure, so it must treat them symmetrically.
    Their simulated truths are opposite (one side completes the logical). Placement
    round t in {1,3}; onset=t; matching erasure value freed."""
    s = D.s; out = []
    for sector in ('X', 'Z'):
        w, reps = crossing_reps(s, sector)
        faulttag = 'X' if sector == 'X' else 'Z'
        for (tag, qs) in reps[:max_reps]:
            others = [q for q in qs if q != SITE]
            if len(others) % 2 != 0:
                continue
            half = len(others) // 2
            splits = set()
            for comb in itertools.combinations(range(len(others)), half):
                a = frozenset(comb); b = frozenset(range(len(others))) - a
                splits.add(frozenset((a, b)))
            for sp in splits:
                a, b = tuple(sp)
                HA = [others[i] for i in a]; HB = [others[i] for i in b]
                for t in (1, 3):
                    vx, vz = (1, 0) if sector == 'X' else (0, 1)
                    pair = []
                    for H in (HA, HB):
                        extra = [(faulttag, q, t) for q in H]
                        fts = tuple(extra) + tuple(loss_contribs(t, vx, vz))
                        DZ, DX, truth, _ = s.simulate(*nd_run.compose(fts))
                        dec = {aa: _decode_safe(D, DZ, DX, aa) for aa in ARMS}
                        pair.append(dict(extra_weight=len(extra), truth=truth,
                                         labels={aa: dec[aa]['label'] for aa in ARMS},
                                         p0={aa: (round(dec[aa]['p0'], 6) if dec[aa]['p0'] is not None else None) for aa in ARMS},
                                         tie={aa: dec[aa]['tie'] for aa in ARMS}))
                    out.append(dict(sector=sector, logical_weight=w, round=t,
                                    HA=[list(q) for q in HA], HB=[list(q) for q in HB],
                                    opposite_truth=(pair[0]['truth'] != pair[1]['truth']),
                                    thick_symmetric=(pair[0]['p0']['thick'] == pair[1]['p0']['thick']),
                                    thick_both_tie=(bool(pair[0]['tie']['thick']) and bool(pair[1]['tie']['thick'])),
                                    members=pair))
    return out


def near_loss_configs(prims):
    for w in (1, 2):
        for combo in itertools.combinations(prims, w):
            yield [list(c) for c in combo]


def stress():
    D = make_decoder(); s = D.s
    prims, Ndata = p_loc(s)
    extra_lists = near_loss_configs(prims)
    res = decode_histories(D, extra_lists, label='stress-nearloss', collect_records=True)
    n = res['nhist']
    nl = dict(n_prims=len(prims), neighbourhood=[list(q) for q in Ndata], nhist=n,
              arms={a: dict(tie_truth=round(res['glob'][a]['tie'] / n, 6),
                            hard_truth=round(res['glob'][a]['hard'] / n, 6),
                            tie_count=res['glob'][a]['tie_count'],
                            tie_wfrac=round(res['glob'][a]['tie_count'] / n, 6)) for a in ARMS},
              pairs={pr: grid_decomp(res['grid'][pr]) for pr in res['grid']},
              whole_vs_thick=dict(label_ne=res['whole_label_ne'], post_ne=res['whole_post_ne']))
    # empirical seam detection: committed-record groups with BOTH truths present
    ambiguous = [v for v in res['records'].values() if len(v['truths']) > 1]
    seam = dict(record_groups=len(res['records']),
                ambiguous_record_groups=len(ambiguous),
                ambiguous_histories=sum(v['n'] for v in ambiguous),
                thick_ties_total=res['glob']['thick']['tie_count'])
    # geometry of the minimum (2,2)-crossing logicals, for context
    geom = {}
    for sector in ('X', 'Z'):
        w, reps = crossing_reps(s, sector)
        geom[sector] = dict(min_crossing_logical_weight=w, n_min_reps=len(reps))
    out = dict(kind='stress', d=5, site=list(SITE), near_loss=nl,
               empirical_seam=seam, crossing_geometry=geom, elapsed=res['elapsed'])
    (R / 'pass2_stress.json').write_text(json.dumps(out, indent=2) + '\n')
    print('near-loss histories', n, 'arms tie_truth',
          {a: nl['arms'][a]['tie_truth'] for a in ARMS})
    print('thick tie_wfrac', nl['arms']['thick']['tie_wfrac'],
          'thin tie_wfrac', nl['arms']['thin']['tie_wfrac'])
    print('empirical seam:', seam)
    print('crossing geometry:', geom)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'primary'
    if cmd == 'primary':
        lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
        primary(lim)
    elif cmd == 'stress':
        stress()
    else:
        print('unknown or not-yet-implemented subcommand:', cmd)
