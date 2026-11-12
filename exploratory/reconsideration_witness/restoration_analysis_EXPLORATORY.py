"""POST-HOC (exploratory) restoration analysis.

The pre-registered one-bit rule FAILED (see REPORT.md / CHANGES.md). Sol's
protocol allows discovering a rule by examining the result, RE-FREEZING it, and
testing on fresh histories with full counts. This quantifies, faithfully against
the full-history reference, how much of the pruned "reason" the streaming
decoder must restore to reproduce the reference's post-flag revision -- the
paper's "one tile, or one corner", measured.

Everything here is labelled exploratory; it changes nothing frozen. Writes
restoration_posthoc.json.
"""

import itertools
import json
from collections import defaultdict

import repcode as rc
import decoders as dec
from search import enumerate_histories

CORE = [(c, t) for c in range(len(rc.CHECKS)) for t in range(rc.COMMIT_C)]


def records():
    out = []
    for f in enumerate_histories():
        ds = rc.detectors_of(f, dec.H)
        rpre = dec.reference_predict(ds, False)
        rpost = dec.reference_predict(ds, True)
        out.append({
            'faults': f, 'detset': ds,
            'core': tuple(1 if p in ds else 0 for p in CORE),
            'frame': dec.streaming_commit(ds), 'm2': dec.m2_boundary(ds),
            'live': dec.streaming_live(ds),
            'ref_pre': rpre[0], 'pre_strict': rpre[3],
            'ref_post': rpost[0], 'post_strict': rpost[3],
            'truth': rc.logical_of(f, dec.L),
            'group': (dec.streaming_commit(ds), dec.m2_boundary(ds),
                      tuple(1 if (c, rc.COMMIT_C) in ds else 0
                            for c in range(len(rc.CHECKS))),
                      dec.post_cut_inputs(ds)),
        })
    return out


def minimal_subset_for_reference(recs, groups_filter=None):
    """Smallest set of core-detector positions whose values determine the
    reference's strict post-flag prediction WITHIN every group."""
    for k in range(0, len(CORE) + 1):
        for S in itertools.combinations(range(len(CORE)), k):
            table = {}
            ok = True
            for r in recs:
                if not r['post_strict']:
                    continue
                if groups_filter is not None and r['group'] not in groups_filter:
                    continue
                key = (r['group'], tuple(r['core'][i] for i in S))
                if key in table and table[key] != r['ref_post']:
                    ok = False
                    break
                table[key] = r['ref_post']
            if ok:
                return list(S), table
    return None, None


def witness_pairs(recs):
    """Strict pairs within a group that share pre-flag prediction and split
    post-flag (the reference-splitting witnesses)."""
    groups = defaultdict(list)
    for r in recs:
        groups[r['group']].append(r)
    pairs = []
    for ms in groups.values():
        for a, b in itertools.combinations(ms, 2):
            if not (a['pre_strict'] and b['pre_strict'] and a['post_strict'] and b['post_strict']):
                continue
            if a['ref_pre'] != b['ref_pre']:
                continue
            if (a['ref_post'] != a['ref_pre']) == (b['ref_post'] != b['ref_pre']):
                continue
            pairs.append((a, b))
    return pairs, groups


def main():
    recs = records()
    pairs, groups = witness_pairs(recs)
    out = {'histories': len(recs), 'reference_splitting_witness_pairs': len(pairs)}

    # minimal restoration against the reference, global
    S, table = minimal_subset_for_reference(recs)
    S_names = [f"(c{CORE[i][0]},t{CORE[i][1]})" for i in S]
    out['minimal_global_restoration'] = {
        'n_detectors': len(S), 'detectors': S_names,
        'claim': 'with (frame, m2) and these pruned detectors, the full-history '
                 'reference post-flag revision is determined in every group.'}

    # single-detector (one "corner") pair-specific coverage
    cov = []
    for i in range(len(CORE)):
        sep = sum(1 for a, b in pairs if a['core'][i] != b['core'][i])
        cov.append({'detector': f"(c{CORE[i][0]},t{CORE[i][1]})", 'pairs_separated': sep})
    cov.sort(key=lambda x: -x['pairs_separated'])
    out['single_detector_pair_specific'] = {
        'total_pairs': len(pairs), 'best': cov[0], 'all': cov,
        'note': 'no single fixed detector separates all pairs; one bit is a '
                'pair-specific restoration only.'}

    # held-out: discover minimal positions on even groups, confirm the SAME
    # positions determine the reference on odd (held-out) groups.
    gkeys = sorted(groups.keys(), key=repr)
    even = set(gkeys[::2])
    odd = set(gkeys[1::2])
    S_tr, _ = minimal_subset_for_reference(recs, groups_filter=even)
    # do the training positions still determine the reference on held-out groups?
    tbl = {}
    held_ok = True
    for r in recs:
        if not r['post_strict'] or r['group'] not in odd:
            continue
        key = (r['group'], tuple(r['core'][i] for i in S_tr))
        if key in tbl and tbl[key] != r['ref_post']:
            held_ok = False
            break
        tbl[key] = r['ref_post']
    out['held_out'] = {
        'train_minimal_detectors': [f"(c{CORE[i][0]},t{CORE[i][1]})" for i in S_tr],
        'same_positions_determine_reference_on_held_out_groups': held_ok}

    # reference-agreement vs logical-correctness on witness decisions, with the
    # 2-detector restoration (by construction agrees 100% with reference).
    decisions = [r for pair in pairs for r in pair]
    n = len(decisions)
    ref_correct = sum(1 for r in decisions if r['ref_post'] == r['truth'])
    stream_correct = sum(1 for r in decisions
                         if (r['frame'] ^ r['live']) == r['truth'])
    # restored == reference by construction on these groups:
    restored_agrees_reference = n
    out['correctness'] = {
        'witness_decisions': n,
        'restored_agrees_with_reference': restored_agrees_reference,
        'restored_agrees_with_reference_frac': 1.0,
        'reference_logical_correct': ref_correct,
        'reference_logical_correct_frac': round(ref_correct / n, 3),
        'unrestored_streaming_logical_correct': stream_correct,
        'unrestored_streaming_logical_correct_frac': round(stream_correct / n, 3),
        'note': 'Restoration recovers AGREEMENT WITH FULL HISTORY (the retention '
                'claim). It does not make the logical always correct: witness '
                'decisions sit on the logical boundary where the reference itself '
                'is far from certain.'}

    with open('restoration_posthoc.json', 'w') as fh:
        json.dump(out, fh, indent=2, default=str)

    print(json.dumps(out, indent=2, default=str))


if __name__ == '__main__':
    main()
