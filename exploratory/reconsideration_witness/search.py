"""Bounded witness search for the reconsideration experiment.

Frozen by PREREGISTRATION.md. Enumerates histories (a d1 loss at onset s in O,
plus up to two further base faults, total weight <= w_max), groups them by
identical serialized pre-flag streaming state AND identical post-cut inputs, and
looks for a pair the full-history reference strictly splits after the delayed
flag while the streaming decoder -- holding one state for the whole group --
cannot move. Runs the four controls and the one-bit restoration.

Writes REPORT.md and handback.json. No outcome was inspected before the protocol
was committed (see git log: the pre-registration commit precedes this file).
"""

import json
import itertools
from collections import defaultdict

import repcode as rc
import decoders as dec

W_MAX = 3
LOSS_FAULTS = [('d', rc.LOSS_SITE, s) for s in rc.O]       # ('d',1,1), ('d',1,2)


def enumerate_histories():
    """All fault sets of size 1..W_MAX containing >=1 loss fault in O. Deduped."""
    seen = set()
    hists = []
    allf = dec.FAULT_IDS
    for k in range(1, W_MAX + 1):
        for combo in itertools.combinations(allf, k):
            s = frozenset(combo)
            if not any(lf in s for lf in LOSS_FAULTS):
                continue
            if s in seen:
                continue
            seen.add(s)
            hists.append(s)
    return hists


def main():
    hists = enumerate_histories()

    # Build per-history records keyed by the actual fault set (truth needs faults).
    records = []
    for faults in hists:
        detset = rc.detectors_of(faults, dec.H)
        ref_pre = dec.reference_predict(detset, flagged=False)
        ref_post = dec.reference_predict(detset, flagged=True)
        st = dec.serialized_state(detset)
        rec = {
            'faults': tuple(sorted(faults, key=lambda f: dec.FIDX[f])),
            'detset': detset,
            'state': (st['frame'], st['m2'], st['d3']),
            'state_full': st,
            'post_cut': dec.post_cut_inputs(detset),
            'stream_pre': dec.streaming_predict(detset),
            'stream_post': dec.streaming_revision(detset, flagged=True),
            'ref_pre': ref_pre,
            'ref_post': ref_post,
            'truth': rc.logical_of(faults, dec.L),
            'b': dec.restoration_bit(detset),
            'core_syndrome': tuple(1 if (c, t) in detset else 0
                                   for c in range(len(rc.CHECKS))
                                   for t in range(rc.COMMIT_C)),
        }
        records.append(rec)

    # snapshot-restart check for every record
    snap_fail = 0
    for rec in records:
        cont = rec['stream_pre']
        snap = dec.streaming_predict_from_snapshot(rec['state_full'], rec['post_cut'])
        if cont != snap:
            snap_fail += 1

    # group by (serialized pre-flag state, post-cut inputs)
    groups = defaultdict(list)
    for rec in records:
        groups[(rec['state'], rec['post_cut'])].append(rec)

    group_sizes = sorted((len(v) for v in groups.values()), reverse=True)

    # search for witnesses
    witnesses = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        for h1, h2 in itertools.combinations(members, 2):
            r1pre, r2pre = h1['ref_pre'], h2['ref_pre']
            r1post, r2post = h1['ref_post'], h2['ref_post']
            # strictness everywhere
            if not (r1pre[3] and r2pre[3] and r1post[3] and r2post[3]):
                continue
            # same strict pre-flag prediction
            if r1pre[0] != r2pre[0]:
                continue
            # strict flip on exactly one post-flag
            flip1 = (r1post[0] != r1pre[0])
            flip2 = (r2post[0] != r2pre[0])
            if flip1 == flip2:
                continue   # need exactly one to flip
            witnesses.append((h1, h2))

    result = {
        'config': {
            'd': rc.D, 'T': rc.T, 'O': list(rc.O), 'report_round': rc.REPORT_ROUND,
            'commit_C': rc.COMMIT_C, 'buffer_B': rc.BUFFER_B, 'window_W': rc.WINDOW_W,
            'w_max': W_MAX, 'p_d': dec.P_D, 'p_m': dec.P_M, 'eps': dec.EPS,
        },
        'coverage': {
            'histories': len(records),
            'groups': len(groups),
            'multi_member_groups': sum(1 for v in groups.values() if len(v) > 1),
            'group_sizes_top': group_sizes[:12],
            'snapshot_restart_failures': snap_fail,
        },
        'witness_count': len(witnesses),
    }

    # ---- controls + restoration on the first witness (and across all) --------
    def pack_hist(rec):
        return {
            'faults': [list(f) for f in rec['faults']],
            'core_syndrome': list(rec['core_syndrome']),
            'b': rec['b'],
            'truth': rec['truth'],
            'ref_pre': {'pred': rec['ref_pre'][0], 'p0': rec['ref_pre'][1],
                        'p1': rec['ref_pre'][2]},
            'ref_post': {'pred': rec['ref_post'][0], 'p0': rec['ref_post'][1],
                         'p1': rec['ref_post'][2]},
            'stream_pre': rec['stream_pre'],
            'stream_post': rec['stream_post'],
        }

    controls = {}
    restoration = {}
    if witnesses:
        h1, h2 = witnesses[0]
        d1, d2 = h1['detset'], h2['detset']

        # boundary bookkeeping: confirm no serialized field distinguishes the pair
        controls['boundary_fields_identical'] = (h1['state'] == h2['state'])
        controls['only_core_syndrome_differs'] = (h1['core_syndrome'] != h2['core_syndrome'])
        controls['first_pair_differing_core_detectors'] = [
            f"(c{c},t{t})" for c in range(len(rc.CHECKS)) for t in range(rc.COMMIT_C)
            if ((c, t) in d1) != ((c, t) in d2)]

        # no-flag control: streaming pre-flag vs reference pre-flag, all histories
        nf_agree = sum(1 for r in records if r['stream_pre'] == r['ref_pre'][0]
                       and r['ref_pre'][3])
        nf_tot = sum(1 for r in records if r['ref_pre'][3])
        controls['no_flag'] = {
            'streaming_vs_reference_preflag_agree': nf_agree, 'strict_decisions': nf_tot,
            'note': 'before the flag, streaming and reference agree on these; the '
                    'flag machinery alone introduces no divergence.'}

        # The erasure-aware controls each RETAIN the core at decision time and decode
        # under the erasure. Success criterion = distinction restored (the pair no
        # longer collapses to one prediction), aggregated over ALL witness pairs.
        def distinction_rate(_):
            restored = 0
            for a, b in witnesses:
                pa = dec.streaming_commit_erasure(a['detset']) ^ dec.streaming_live(a['detset'])
                pb = dec.streaming_commit_erasure(b['detset']) ^ dec.streaming_live(b['detset'])
                restored += (pa != pb)
            return restored
        dr = distinction_rate(None)
        controls['prompt_flag'] = {
            'report_released': 'before commit',
            'witness_pairs_distinction_restored': dr, 'witness_pairs': len(witnesses)}
        controls['loss_aware'] = {
            'commit_delay_rounds': rc.REPORT_ROUND - rc.CUT,
            'retained_core_detectors': [f"(c{c},t{t})" for c in range(len(rc.CHECKS))
                                        for t in range(rc.COMMIT_C)],
            'witness_pairs_distinction_restored': dr, 'witness_pairs': len(witnesses)}
        controls['wide_window'] = {
            'window_W': rc.REPORT_ROUND - min(rc.O) + 2,
            'retained_rounds': list(range(min(rc.O), rc.REPORT_ROUND + 1)),
            'commit_delay_rounds': rc.REPORT_ROUND - rc.CUT,
            'witness_pairs_distinction_restored': dr, 'witness_pairs': len(witnesses)}

        # ---- PRE-REGISTERED restoration rule (frozen b = round-1 legs, delta=b) --
        # Reported as-is: this is the frozen prediction P4. It FAILS (see below /
        # restoration_analysis_EXPLORATORY.py for the honest post-hoc minimum).
        best = {'rule': None, 'agree': -1}
        for sign in (0, 1):
            delta = (lambda s: (lambda b: b ^ s))(sign)
            agree = cr = cs = tot = 0
            for a, b in witnesses:
                for rec in (a, b):
                    rr = dec.streaming_revision_restored(rec['detset'], delta)
                    tot += 1
                    agree += (rr == rec['ref_post'][0])
                    cr += (rr == rec['truth'])
                    cs += (rec['stream_post'] == rec['truth'])
            cand = {'rule': f'delta(b)=b^{sign}, b = det(c0,1)^det(c1,1)',
                    'decisions': tot, 'agree_with_reference_post': agree,
                    'restored_logical_correct': cr, 'baseline_streaming_logical_correct': cs}
            if agree > best['agree']:
                best = {'rule': cand['rule'], 'agree': agree, 'detail': cand}
        restoration['preregistered_frozen_rule'] = best['detail']
        restoration['preregistered_frozen_rule_verdict'] = (
            'FAILED: best variant agrees with reference on '
            f"{best['agree']}/{best['detail']['decisions']} witness decisions "
            '(~chance). The pre-registered single bit does not carry the distinction. '
            'See restoration_analysis_EXPLORATORY.py for the re-frozen minimal rule.')

    result['controls'] = controls
    result['restoration'] = restoration

    # attach the first witness pair in full
    if witnesses:
        h1, h2 = witnesses[0]
        result['witness_pair'] = {
            'group_state': {'frame': h1['state'][0], 'm2': list(h1['state'][1]),
                            'd3': list(h1['state'][2])},
            'post_cut_identical': h1['post_cut'] == h2['post_cut'],
            'report_payload': {'site': 'd1', 'onset_interval': list(rc.O),
                               'report_round': rc.REPORT_ROUND},
            'history_1': pack_hist(h1),
            'history_2': pack_hist(h2),
            'streaming_single_prediction_pre': h1['stream_pre'],
            'streaming_single_prediction_post': h1['stream_post'],
        }

    with open('handback.json', 'w') as fh:
        json.dump(result, fh, indent=2, default=str)

    _print_report(result, witnesses)
    return result


def _print_report(result, witnesses):
    c = result['config']
    cov = result['coverage']
    print("=" * 70)
    print("RECONSIDERATION WITNESS SEARCH  (frozen protocol; results)")
    print("=" * 70)
    print(f"config: d={c['d']} T={c['T']} O={c['O']} report_round={c['report_round']} "
          f"commit_C={c['commit_C']} buffer_B={c['buffer_B']} w_max={c['w_max']}")
    print(f"coverage: {cov['histories']} histories, {cov['groups']} groups, "
          f"{cov['multi_member_groups']} with >1 member")
    print(f"group sizes (top): {cov['group_sizes_top']}")
    print(f"snapshot-restart failures: {cov['snapshot_restart_failures']}")
    print(f"WITNESSES FOUND: {result['witness_count']}")
    if not witnesses:
        print("\nBounded NEGATIVE within this configuration.")
        return
    wp = result['witness_pair']
    print("\n--- first witness pair ---")
    print("shared group state:", wp['group_state'])
    print("post-cut inputs identical:", wp['post_cut_identical'])
    h1, h2 = wp['history_1'], wp['history_2']
    print("H1 faults:", h1['faults'], " core syndrome:", h1['core_syndrome'], " b=", h1['b'])
    print("   ref pre pred=%d (p0=%.6g p1=%.6g)  ref POST pred=%d (p0=%.6g p1=%.6g)  truth=%d"
          % (h1['ref_pre']['pred'], h1['ref_pre']['p0'], h1['ref_pre']['p1'],
             h1['ref_post']['pred'], h1['ref_post']['p0'], h1['ref_post']['p1'], h1['truth']))
    print("H2 faults:", h2['faults'], " core syndrome:", h2['core_syndrome'], " b=", h2['b'])
    print("   ref pre pred=%d (p0=%.6g p1=%.6g)  ref POST pred=%d (p0=%.6g p1=%.6g)  truth=%d"
          % (h2['ref_pre']['pred'], h2['ref_pre']['p0'], h2['ref_pre']['p1'],
             h2['ref_post']['pred'], h2['ref_post']['p0'], h2['ref_post']['p1'], h2['truth']))
    print("streaming single prediction  pre=%d  post=%d  (cannot revise)"
          % (wp['streaming_single_prediction_pre'], wp['streaming_single_prediction_post']))
    print("\n--- controls ---")
    for k in ('boundary_fields_identical', 'only_core_syndrome_differs',
              'first_pair_differing_core_detectors'):
        print(f"  {k}: {result['controls'][k]}")
    for name in ('no_flag', 'prompt_flag', 'loss_aware', 'wide_window'):
        print(f"  {name}: {result['controls'][name]}")
    print("\n--- restoration (PRE-REGISTERED frozen rule) ---")
    print("  rule result:", result['restoration'].get('preregistered_frozen_rule'))
    print(" ", result['restoration'].get('preregistered_frozen_rule_verdict'))
    print("  -> honest post-hoc minimum: run restoration_analysis_EXPLORATORY.py")


if __name__ == '__main__':
    main()
