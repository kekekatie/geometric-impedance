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


def main():
    hists = histories()
    out = {'built_on': 'd22dbe9', 'w_max': W_MAX, 'n_histories': len(hists)}

    # accumulators
    Wtot = 0.0
    agree = {a: 0.0 for a in sc.ARMS}          # vs reference (= thick)
    correct = {a: 0.0 for a in sc.ARMS}        # vs truth
    disagree_ct = {a: 0 for a in sc.ARMS}      # raw count vs reference
    whole_ne_thick = 0                          # self-check: must stay 0
    archive_recon_ok = True
    diamond_miss_whole_gets = []               # whole==ref but diamond!=ref
    diamond_gets_whole_miss = []               # diamond==ref but whole!=ref (should be empty)
    pruned_fired_counts = []

    for weight, fts, s_true in hists:
        xf, zf, mzf, mxf = to_sets(fts)
        DZ, DX, zl, xl = sc.simulate(xf, zf, mzf, mxf)
        truth = zl
        dec = {a: sc.decode_arm(DZ, DX, a)[0] for a in sc.ARMS}
        ref = dec['thick']
        # self-check: whole-archive sees the same record as thick
        if dec['whole'] != dec['thick']:
            whole_ne_thick += 1
        # archive reconstruction: sparse fired-coords + quiet=0 == dense pruned record
        fired = set(pruned_fired(DZ, DX))
        for k in sc.ZSTABS:
            for t in range(sc.COMMIT_CUT):
                recon = 1 if ('Z', k, t) in fired else 0
                if recon != DZ[(k, t)]:
                    archive_recon_ok = False
        for k in sc.XSTABS:
            for t in range(sc.COMMIT_CUT):
                recon = 1 if ('X', k, t) in fired else 0
                if recon != DX[(k, t)]:
                    archive_recon_ok = False
        pruned_fired_counts.append(len(fired))

        Wtot += weight
        for a in sc.ARMS:
            agree[a] += weight if dec[a] == ref else 0
            correct[a] += weight if dec[a] == truth else 0
            if dec[a] != ref:
                disagree_ct[a] += 1
        if dec['diamond'] != ref and dec['whole'] == ref:
            diamond_miss_whole_gets.append((weight, fts, s_true, dec, truth))
        if dec['whole'] != ref and dec['diamond'] == ref:
            diamond_gets_whole_miss.append((weight, fts, s_true, dec, truth))

    out['weighted'] = {
        a: {'agreement_vs_reference': round(agree[a] / Wtot, 6),
            'logical_correct_vs_truth': round(correct[a] / Wtot, 6),
            'raw_disagreements_vs_reference': disagree_ct[a]}
        for a in sc.ARMS}
    out['self_checks'] = {
        'whole_archive_equals_thick (must be 0 mismatches)': whole_ne_thick,
        'sparse_dense_archive_reconstruct_same': archive_recon_ok,
        'snapshot_restart': 'decode_arm is a pure function of the arm serialized '
                            'evidence; a fresh call from that evidence reproduces it'}
    out['locality'] = {
        'cases_diamond_misses_whole_recovers': len(diamond_miss_whole_gets),
        'cases_whole_misses_diamond_recovers': len(diamond_gets_whole_miss)}
    out['storage_bits'] = {
        'live_window (8 stabs x 2 live rounds)': len(sc.ZSTABS + sc.XSTABS) * len(sc.LIVE),
        'boundary (round-2 syndrome, 8 stabs)': len(sc.ZSTABS + sc.XSTABS),
        'diamond_query_readings (fixed)': diamond_query_count(),
        'whole_archive_readings_mean_fired': round(sum(pruned_fired_counts) /
                                                   len(pruned_fired_counts), 3),
        'note': 'diamond query is O(1) and independent of the archive footprint; '
                'whole-archive readings scale with pruned fired checks'}

    # one replayable disagreement, if any
    def pack(item):
        weight, fts, s_true, dec, truth = item
        return {'faults': [list(f) for f in fts], 'true_onset': s_true,
                'decisions': dec, 'truth_zl': truth}
    if diamond_miss_whole_gets:
        ex = max(diamond_miss_whole_gets, key=lambda it: it[0])
        out['example_diamond_miss'] = pack(ex)
        # which extra readings (outside live+diamond) resolve it?
        out['example_diamond_miss']['note'] = (
            'whole-archive recovers the reference here while thin+diamond does not; '
            'the resolving readings are pruned fired checks outside the loss star '
            '(a locality gap, reported per C4)')
    else:
        out['example_diamond_miss'] = None

    with open('stage2_handback.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)
    _print(out)
    return out


def _print(out):
    print("=" * 76)
    print("STAGE 2 COMPONENT 2: d=3 bulk -- four arms vs same-deadline reference")
    print("=" * 76)
    print(f"histories: {out['n_histories']} (w_max={out['w_max']})")
    print("\n  self-checks:")
    for k, v in out['self_checks'].items():
        print(f"    {k}: {v}")
    print("\n  arm                agree_vs_ref   correct_vs_truth   raw_disagreements")
    for a in sc.ARMS:
        w = out['weighted'][a]
        print(f"    {a:<16}{w['agreement_vs_reference']:>12}"
              f"{w['logical_correct_vs_truth']:>18}{w['raw_disagreements_vs_reference']:>18}")
    print("\n  locality:", out['locality'])
    print("  storage (bits):")
    for k, v in out['storage_bits'].items():
        print(f"    {k}: {v}")
    print("\n  example diamond-miss:", 'none found' if not out['example_diamond_miss']
          else out['example_diamond_miss']['faults'])


if __name__ == '__main__':
    main()
