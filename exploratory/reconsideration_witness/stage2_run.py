"""Stage 2 Component 2: run the d=3 bulk experiment (four arms vs same-deadline ref).

Frozen by PREREGISTRATION_2D.md Amendment A (d22dbe9). Replay: python3 stage2_run.py
-> stage2_handback.json.
"""

import itertools
import json
from collections import defaultdict

import stage2_surface as sc

W_MAX = 2


def base_faults():
    f = []
    for q in sc.DATA:
        for t in range(sc.T):
            f.append(('X', q, t))
            f.append(('Z', q, t))
    for k in sc.ZSTABS:
        for t in range(sc.T):
            f.append(('MZ', k, t))
    for k in sc.XSTABS:
        for t in range(sc.T):
            f.append(('MX', k, t))
    return f


def to_sets(fault_tuples):
    xf, zf, mzf, mxf = set(), set(), set(), set()
    for ft in fault_tuples:
        if ft[0] == 'X':
            xf.add((ft[1], ft[2]))
        elif ft[0] == 'Z':
            zf.add((ft[1], ft[2]))
        elif ft[0] == 'MZ':
            mzf.add((ft[1], ft[2]))
        else:
            mxf.add((ft[1], ft[2]))
    return xf, zf, mzf, mxf


def histories():
    """(weight, fault_tuples including the loss) over all onsets, loss values, extras<=W_MAX."""
    pool = base_faults()
    out = []
    for w in range(0, W_MAX + 1):
        for extra in itertools.combinations(pool, w):
            for s in sc.ONSET:
                for vx in (0, 1):
                    for vz in (0, 1):
                        loss = []
                        if vx:
                            loss.append(('X', sc.LOSS_SITE, s))
                        if vz:
                            loss.append(('Z', sc.LOSS_SITE, s))
                        out.append((sc.P ** w, tuple(extra) + tuple(loss), s))
    return out


def pruned_fired(DZ, DX):
    """Detector readings in the pruned rounds {0,1,2} that fired (the sparse archive)."""
    ev = []
    for k in sc.ZSTABS:
        for t in range(sc.COMMIT_CUT):
            if DZ[(k, t)]:
                ev.append(('Z', k, t))
    for k in sc.XSTABS:
        for t in range(sc.COMMIT_CUT):
            if DX[(k, t)]:
                ev.append(('X', k, t))
    return ev


def diamond_query_count():
    return len(sc.STAR_Z) * len(sc.DIAMOND_ROUNDS) + len(sc.STAR_X) * len(sc.DIAMOND_ROUNDS)


def resolving_readings(state, site):
    """Archive entries OUTSIDE the diamond that, added to the diamond arm, flip its
    decision toward the whole-archive decision. Returns the list of such readings."""
    base = sc.decode_restart(state, 'diamond', site)[0]
    whole = sc.decode_restart(state, 'whole', site)[0]
    star = set(sc.STAR[site])
    out = []
    for (tag, k, t) in state['archive']:
        if k in star:
            continue                              # inside the diamond already
        # add just this one reading to the diamond evidence
        availZ, availX = {}, {}
        for (kk, tt), v in state['live'].items():
            (availZ if kk in sc.ZSTABS else availX)[(kk, tt)] = v
        bndZ = {kk: v for kk, v in state['boundary'].items() if kk in sc.ZSTABS}
        bndX = {kk: v for kk, v in state['boundary'].items() if kk in sc.XSTABS}
        for kk in sc.STAR_Z:
            for tt in sc.DIAMOND_ROUNDS:
                availZ[(kk, tt)] = 1 if ('Z', kk, tt) in state['archive'] else 0
        for kk in sc.STAR_X:
            for tt in sc.DIAMOND_ROUNDS:
                availX[(kk, tt)] = 1 if ('X', kk, tt) in state['archive'] else 0
        (availZ if tag == 'Z' else availX)[(k, t)] = 1
        d = sc.decide(availZ, availX, bndZ, bndX)[0]
        if d != base and d == whole:
            out.append([tag, k, t])
    return out


def main():
    hists = histories()
    out = {'built_on': 'd22dbe9', 'w_max': W_MAX, 'n_histories': len(hists),
           'pipeline': 'archive built BEFORE the flag (site-agnostic fired checks); '
                       'each arm restarts from the serialized state and reads only '
                       'what it kept (diamond/whole QUERY the sparse archive)'}

    Wtot = 0.0
    agree = {a: 0.0 for a in sc.ARMS}
    correct = {a: 0.0 for a in sc.ARMS}
    disagree_ct = {a: 0 for a in sc.ARMS}
    restart_mismatch = 0                          # restart vs direct decode (must be 0)
    whole_ne_thick = 0
    archive_recon_ok = True
    diamond_miss_whole_gets = []
    diamond_gets_whole_miss = []
    # among diamond!=reference cases: who is actually right vs truth?
    dm_diamond_right = dm_ref_right = dm_both_wrong = 0
    peak = {a: 0 for a in sc.ARMS}
    whole_query = []

    for weight, fts, s_true in hists:
        xf, zf, mzf, mxf = to_sets(fts)
        DZ, DX, zl, xl = sc.simulate(xf, zf, mzf, mxf)
        truth = zl
        state = sc.serialize_pre_flag(DZ, DX)
        # thick (reference) reads the full uncommitted window; the rest RESTART
        ref = sc.decode_arm(DZ, DX, 'thick')[0]
        dec = {'thick': ref}
        for a in ('thin', 'diamond', 'whole'):
            dec[a] = sc.decode_restart(state, a, sc.LOSS_SITE)[0]
            if dec[a] != sc.decode_arm(DZ, DX, a)[0]:     # restart == direct check
                restart_mismatch += 1
        if dec['whole'] != dec['thick']:
            whole_ne_thick += 1
        # archive reconstruction (incl. quiet=0) == dense pruned record
        fired = set(pruned_fired(DZ, DX))
        for k in sc.ZSTABS:
            for t in range(sc.COMMIT_CUT):
                if (1 if ('Z', k, t) in fired else 0) != DZ[(k, t)]:
                    archive_recon_ok = False
        for k in sc.XSTABS:
            for t in range(sc.COMMIT_CUT):
                if (1 if ('X', k, t) in fired else 0) != DX[(k, t)]:
                    archive_recon_ok = False

        Wtot += weight
        for a in sc.ARMS:
            agree[a] += weight if dec[a] == ref else 0
            correct[a] += weight if dec[a] == truth else 0
            if dec[a] != ref:
                disagree_ct[a] += 1
            peak[a] = max(peak[a], sc.peak_storage_bits(state, a))
        whole_query.append(sc.query_readings(state, 'whole'))
        if dec['diamond'] != ref:
            if dec['diamond'] == truth:
                dm_diamond_right += 1
            elif ref == truth:
                dm_ref_right += 1
            else:
                dm_both_wrong += 1
        if dec['diamond'] != ref and dec['whole'] == ref:
            diamond_miss_whole_gets.append((weight, fts, s_true, dec, truth, state))
        if dec['whole'] != ref and dec['diamond'] == ref:
            diamond_gets_whole_miss.append((weight, fts, s_true, dec, truth, state))

    out['weighted'] = {
        a: {'agreement_vs_reference': round(agree[a] / Wtot, 6),
            'logical_correct_vs_truth': round(correct[a] / Wtot, 6),
            'raw_disagreements_vs_reference': disagree_ct[a]}
        for a in sc.ARMS}
    out['self_checks'] = {
        'restart_reproduces_direct_decode (must be 0 mismatches)': restart_mismatch,
        'whole_archive_equals_thick (must be 0)': whole_ne_thick,
        'sparse_dense_archive_reconstruct_same': archive_recon_ok}
    out['locality'] = {
        'cases_diamond_misses_whole_recovers': len(diamond_miss_whole_gets),
        'cases_whole_misses_diamond_recovers': len(diamond_gets_whole_miss)}
    out['diamond_vs_reference_disagreements'] = {
        'total': disagree_ct['diamond'],
        'diamond_matches_truth (reference is wrong)': dm_diamond_right,
        'reference_matches_truth (diamond is wrong)': dm_ref_right,
        'both_wrong': dm_both_wrong,
        'note': 'agreement with the reference is not correctness: on some disagreements '
                'the local diamond is right and the same-deadline reference is wrong.'}
    out['storage_bits_peak'] = {
        **{a: peak[a] for a in sc.ARMS},
        'coord_bits_per_archive_event': sc.COORD_BITS,
        'diamond_and_whole_share_one_archive': True,
        'diamond_query_readings (fixed)': sc.query_readings({'archive': set()}, 'diamond'),
        'whole_query_readings_mean': round(sum(whole_query) / len(whole_query), 3),
        'note': 'diamond and whole keep the SAME archive (same peak storage); they '
                'differ only in what they READ -- diamond a fixed <=8 local query, '
                'whole every archived event.'}

    def pack(item):
        weight, fts, s_true, dec, truth, state = item
        res = resolving_readings(state, sc.LOSS_SITE)
        return {'faults': [list(f) for f in fts], 'true_onset': s_true,
                'decisions': dec, 'truth_zl': truth,
                'resolving_readings_outside_star': res,
                'note': 'adding exactly these pruned archived readings (outside the '
                        'loss star) to the diamond flips it to the whole/reference '
                        f'answer; here the reference={dec["thick"]} but truth={truth}'}
    out['example_diamond_miss'] = pack(max(diamond_miss_whole_gets, key=lambda it: it[0])) \
        if diamond_miss_whole_gets else None

    with open('stage2_handback.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)
    _print(out)
    return out


def _print(out):
    print("=" * 78)
    print("STAGE 2 COMPONENT 2: d=3 bulk -- serialize/restart pipeline, four arms")
    print("=" * 78)
    print(f"histories: {out['n_histories']} (w_max={out['w_max']})")
    print("\n  self-checks:")
    for k, v in out['self_checks'].items():
        print(f"    {k}: {v}")
    print("\n  arm             agree_vs_ref  correct_vs_truth  raw_disagree  peak_bits")
    for a in sc.ARMS:
        w = out['weighted'][a]
        print(f"    {a:<14}{w['agreement_vs_reference']:>12}"
              f"{w['logical_correct_vs_truth']:>17}{w['raw_disagreements_vs_reference']:>13}"
              f"{out['storage_bits_peak'][a]:>11}")
    print("\n  locality:", out['locality'])
    print("  diamond-vs-reference disagreements:", out['diamond_vs_reference_disagreements'])
    print("  storage:", {k: v for k, v in out['storage_bits_peak'].items()
                         if 'query' in k or 'coord' in k})
    ex = out['example_diamond_miss']
    if ex:
        print("\n  example diamond-miss:", ex['faults'])
        print("    resolving readings outside star:", ex['resolving_readings_outside_star'])
        print(f"    reference={ex['decisions']['thick']}  truth={ex['truth_zl']}  "
              f"diamond={ex['decisions']['diamond']}")


if __name__ == '__main__':
    main()
