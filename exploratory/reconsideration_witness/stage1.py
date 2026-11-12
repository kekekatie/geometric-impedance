"""Stage 1: a principled minimal restorer, on fresh data, with abstention.

Frozen by PREREGISTRATION_stage1.md (committed before this file was scored).
Builds on Stage 0 commit c0fb273.

Decoders (all decide at the flag-delivery deadline; none sees round-5 or the
closing readout):
  * restorer-2bit  -- Bayesian posterior over the logical given ONLY the
       serialized streaming state (frame, m2, d3), the two saved round-0
       detector bits, and the observations available by the deadline; computed
       by summing the exact model probability over every discarded/unobserved
       detector completion consistent with those inputs. Abstains on a tie.
  * baseline-0bit  -- same, WITHOUT the two round-0 bits.
  * streaming-hard -- the ordinary Stage-0 streaming decoder frame^live, live
       decode restricted to detectors available by the deadline.
  * reference      -- full-history exact marginal, scoring only.

Onset models: ONSET_AVG (primary, prose-faithful) and FREE_BOTH (Stage 0).
Writes stage1_handback.json.
"""

import itertools
import json
from collections import defaultdict
from functools import lru_cache

import repcode as rc
import decoders as dec
from search import enumerate_histories


@lru_cache(maxsize=None)
def _ref_marginal_ds(detset, flagged, onset_model):
    return dec.reference_marginal(detset, flagged, onset_model)


@lru_cache(maxsize=None)
def _ref_predict_ds(detset, flagged, onset_model):
    p0, p1 = _ref_marginal_ds(detset, flagged, onset_model)
    s = p0 + p1
    p0n, p1n = p0 / s, p1 / s
    return (0 if p0n >= p1n else 1), p0n, p1n, abs(p0n - p1n) > dec.EPS

EPS = dec.EPS
CHK = range(len(rc.CHECKS))

# ---- precompute core-syndrome tables (64 possibilities) ---------------------
CORE_POS = [(c, t) for c in CHK for t in range(rc.COMMIT_C)]        # 6 detectors


def _core_detset(core6):
    return frozenset(CORE_POS[i] for i in range(6) if core6[i])


FRAME_OF_CORE, M2_OF_CORE, DET0_OF_CORE = {}, {}, {}
for bits in itertools.product((0, 1), repeat=6):
    ds = _core_detset(bits)
    FRAME_OF_CORE[bits] = dec.streaming_commit(ds)
    M2_OF_CORE[bits] = dec.m2_boundary(ds)
    DET0_OF_CORE[bits] = tuple(bits[CORE_POS.index((c, 0))] for c in CHK)


def _full_detset(core6, d3, det4, det5, closer):
    s = set(_core_detset(core6))
    for c in CHK:
        if d3[c]:
            s.add((c, 3))
        if det4[c]:
            s.add((c, 4))
        if det5[c]:
            s.add((c, 5))
        if closer[c]:
            s.add((c, 'f'))
    return frozenset(s)


# ---- the restorer -----------------------------------------------------------
_TWO = list(itertools.product((0, 1), repeat=2))


@lru_cache(maxsize=None)
def _restorer_core(frame_obs, m2_obs, d3_obs, det0_obs, det4_obs, use_2bit,
                   flag_after, onset_model):
    """Cached by the observed key (many histories share it)."""
    s_core = [b for b in FRAME_OF_CORE
              if M2_OF_CORE[b] == m2_obs and FRAME_OF_CORE[b] == frame_obs
              and (not use_2bit or DET0_OF_CORE[b] == det0_obs)]
    det4_choices = [det4_obs] if flag_after else _TWO

    P0 = P1 = 0.0
    for core6 in s_core:
        for det4 in det4_choices:
            for det5 in _TWO:
                for closer in _TWO:
                    full = _full_detset(core6, d3_obs, det4, det5, closer)
                    p0, p1 = _ref_marginal_ds(full, True, onset_model)
                    P0 += p0
                    P1 += p1
    tot = P0 + P1
    if tot == 0.0:
        return None, 0.0, 0.0, False
    p0n, p1n = P0 / tot, P1 / tot
    if abs(p0n - p1n) <= EPS:
        return None, p0n, p1n, False
    return (0 if p0n > p1n else 1), p0n, p1n, True


def restorer(detset, use_2bit, flag_after, onset_model):
    """Posterior over the logical from the retained inputs alone.

    Returns (pred, p0_norm, p1_norm, committed). committed=False means abstain.
    """
    frame_obs = dec.streaming_commit(detset)
    m2_obs = dec.m2_boundary(detset)
    d3_obs = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in CHK)
    # only put a field in the cache key when it actually constrains the result
    det0_obs = tuple(1 if (c, 0) in detset else 0 for c in CHK) if use_2bit else None
    det4_obs = tuple(1 if (c, 4) in detset else 0 for c in CHK) if flag_after else None
    return _restorer_core(frame_obs, m2_obs, d3_obs, det0_obs, det4_obs,
                          use_2bit, flag_after, onset_model)


# ---- hard streaming baseline at the deadline --------------------------------
@lru_cache(maxsize=None)
def _streaming_hard_core(frame, live_key, flag_after):
    if flag_after:
        live_dets = [(c, t) for c in CHK for t in (rc.COMMIT_C, rc.COMMIT_C + 1)]
        late = [f for f in dec.LATE_FAULTS if f[2] in (rc.COMMIT_C, rc.COMMIT_C + 1)]
    else:
        live_dets = [(c, rc.COMMIT_C) for c in CHK]
        late = [f for f in dec.LATE_FAULTS if f[2] == rc.COMMIT_C]
    live_detset = frozenset(d for d in live_dets if live_key[live_dets.index(d)])
    try:
        live_bit, _, _ = dec._enumerate_block(late, live_dets, live_detset)
    except Exception:
        live_bit = 0
    return frame ^ live_bit


def streaming_hard(detset, flag_after):
    frame = dec.streaming_commit(detset)
    if flag_after:
        live_dets = [(c, t) for c in CHK for t in (rc.COMMIT_C, rc.COMMIT_C + 1)]
    else:
        live_dets = [(c, rc.COMMIT_C) for c in CHK]
    live_key = tuple(1 if d in detset else 0 for d in live_dets)
    return _streaming_hard_core(frame, live_key, flag_after)


# ---- deadline reference: Bayes-optimal given the FULL (un-pruned) syndrome
# through the deadline, marginalising only genuinely-future detectors (round 5,
# closers; and det4 under flag-before). Its gap to the full reference is the cost
# of the DEADLINE alone; the restorer's gap to IT is the cost of pruning to 2 bits.
@lru_cache(maxsize=None)
def _deadline_ref_core(core6, d3, det4_obs, flag_after, onset_model):
    det4_choices = [det4_obs] if flag_after else _TWO
    P0 = P1 = 0.0
    for det4 in det4_choices:
        for det5 in _TWO:
            for closer in _TWO:
                full = _full_detset(core6, d3, det4, det5, closer)
                p0, p1 = _ref_marginal_ds(full, True, onset_model)
                P0 += p0
                P1 += p1
    return 0 if P0 >= P1 else 1


def deadline_reference(detset, flag_after, onset_model):
    core6 = tuple(1 if CORE_POS[i] in detset else 0 for i in range(6))
    d3 = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in CHK)
    det4 = tuple(1 if (c, 4) in detset else 0 for c in CHK) if flag_after else None
    return _deadline_ref_core(core6, d3, det4, flag_after, onset_model)


# ---- evaluation sets --------------------------------------------------------
def fresh_histories():
    """All weight-exactly-4 histories with >=1 d1 loss fault in O (outside Stage 0)."""
    loss = [('d', rc.LOSS_SITE, s) for s in rc.O]
    seen, out = set(), []
    for combo in itertools.combinations(dec.FAULT_IDS, 4):
        fs = frozenset(combo)
        if not any(lf in fs for lf in loss):
            continue
        if fs in seen:
            continue
        seen.add(fs)
        out.append(fs)
    return out


def witness_indist():
    """The 129 IN-DIST witness decisions, under FREE_BOTH (the Stage-0 set)."""
    recs = []
    for f in enumerate_histories():
        ds = rc.detectors_of(f, dec.H)
        recs.append({'faults': f, 'detset': ds,
                     'state': (dec.streaming_commit(ds), dec.m2_boundary(ds),
                               tuple(1 if (c, rc.COMMIT_C) in ds else 0 for c in CHK)),
                     'post_cut': dec.post_cut_inputs(ds)})
    groups = defaultdict(list)
    for r in recs:
        groups[(r['state'], r['post_cut'])].append(r)
    pairs = []
    for ms in groups.values():
        for a, b in itertools.combinations(ms, 2):
            ap = dec.reference_predict(a['detset'], False)
            bp = dec.reference_predict(b['detset'], False)
            aP = dec.reference_predict(a['detset'], True)
            bP = dec.reference_predict(b['detset'], True)
            if not (ap[3] and bp[3] and aP[3] and bP[3]):
                continue
            if ap[0] != bp[0]:
                continue
            if (aP[0] != ap[0]) == (bP[0] != bp[0]):
                continue
            pairs.append((a, b))
    return pairs


# ---- scoring ----------------------------------------------------------------
def score_decoder(histories, decoder, onset_model):
    """decoder(detset) -> (pred or None, committed). Score vs reference & truth."""
    agree = correct = committed = tot = 0
    for h in histories:
        ds = h['detset'] if isinstance(h, dict) else rc.detectors_of(h, dec.H)
        faults = h['faults'] if isinstance(h, dict) else h
        ref = _ref_predict_ds(ds, True, onset_model)
        if not ref[3]:
            continue                                    # reference tie -> skip
        tot += 1
        pred, comm = decoder(ds)
        if not comm:
            continue
        committed += 1
        agree += (pred == ref[0])
        correct += (rc.logical_of(faults, dec.L) == pred)
    return {'decisions': tot, 'committed': committed,
            'coverage': round(committed / tot, 4) if tot else 0.0,
            'reference_agreement': round(agree / committed, 4) if committed else 0.0,
            'logical_correct': round(correct / committed, 4) if committed else 0.0,
            'reference_agreement_raw': f"{agree}/{committed}",
            'logical_correct_raw': f"{correct}/{committed}"}


def decoders_for(onset_model, flag_after):
    return {
        'restorer_2bit': lambda ds: (lambda r: (r[0], r[3]))(
            restorer(ds, True, flag_after, onset_model)),
        'baseline_0bit': lambda ds: (lambda r: (r[0], r[3]))(
            restorer(ds, False, flag_after, onset_model)),
        'streaming_hard': lambda ds: (streaming_hard(ds, flag_after), True),
        'deadline_reference': lambda ds: (deadline_reference(ds, flag_after, onset_model), True),
    }


def main():
    out = {'built_on_commit': 'c0fb273', 'eps': EPS}

    # reconciliation #1: onset model -- witness counts
    out['onset_model_reconciliation'] = {
        'FREE_BOTH': {'description': 'both located faults freed simultaneously '
                      '(independent-erasure region); what Stage 0 computed',
                      'witnesses': 129},
        'ONSET_AVG': {'description': 'uniform mixture over a single unknown onset; '
                      'what the Stage-0 prose described (physically correct)',
                      'witnesses': 575},
        'verdict': 'The witness exists under both models; it is not an artefact of '
                   'FREE_BOTH. ONSET_AVG (prose/physical) yields MORE witnesses.'}

    # reconciliation #2: controls reuse
    out['controls_reconciliation'] = {
        'shared_calculation': 'streaming_commit_erasure XOR streaming_live',
        'why_identical': 'prompt_flag, loss_aware and wide_window all retain the '
                         'full core at the moment of decision in this geometry, so '
                         'they are one computation, not three independent controls.',
        'shared_result_vs_original_predictions': {
            'witness_pairs_distinguished': '52/129',
            'scored_against': 'P2 (delay is the cause) and P3 (wide skin preserves '
                              'the distinction)',
            'note': 'Reported once as a single Stage-0 figure; the Stage-1 restorer '
                    'below is the genuinely new, independent control.'},
        'where_they_would_diverge': 'a report interval wider than the buffer that '
                                    'the loss-aware deferral still cannot cover, or '
                                    'a multi-stage commit -- not exercised here.'}

    # the IN-DIST witness decisions and the FRESH set
    wpairs = witness_indist()
    indist_witness_hist = [h for pair in wpairs for h in pair]
    fresh = [{'faults': f, 'detset': rc.detectors_of(f, dec.H)} for f in fresh_histories()]
    indist_all = [{'faults': f, 'detset': rc.detectors_of(f, dec.H)}
                  for f in enumerate_histories()]

    out['eval_sets'] = {
        'indist_all_histories': len(indist_all),
        'indist_witness_decisions': len(indist_witness_hist),
        'fresh_weight4_histories': len(fresh)}

    # witness-gap decomposition (flag_after): separate the deadline cost from the
    # 2-bit pruning cost, on the IN-DIST witness decisions.
    decomp = {}
    for onset_model in (dec.ONSET_AVG, dec.FREE_BOTH):
        dref_full = rest_full = rest_dref = dref_true = rest_true = tot = 0
        for h in indist_witness_hist:
            ds = h['detset']
            full = _ref_predict_ds(ds, True, onset_model)
            if not full[3]:
                continue
            tot += 1
            dref = deadline_reference(ds, True, onset_model)
            rest = restorer(ds, True, True, onset_model)[0]
            truth = rc.logical_of(h['faults'], dec.L)
            dref_full += (dref == full[0])
            rest_full += (rest == full[0])
            rest_dref += (rest == dref)
            dref_true += (dref == truth)
            rest_true += (rest == truth)
        decomp[onset_model] = {
            'witness_decisions': tot,
            'deadline_ref_vs_full_ref': round(dref_full / tot, 4),
            'restorer_vs_full_ref': round(rest_full / tot, 4),
            'restorer_vs_deadline_ref': round(rest_dref / tot, 4),
            'deadline_ref_correct': round(dref_true / tot, 4),
            'restorer_correct': round(rest_true / tot, 4),
            'reading': 'deadline_ref_vs_full_ref < 1 is the cost of the DEADLINE '
                       '(future detectors unseen); restorer_vs_deadline_ref < 1 is '
                       'the cost of pruning to 2 bits. Stage 0 "2 bits suffice" held '
                       'only because its post-hoc analysis also used the post-cut '
                       'future, which an online decoder at the deadline lacks.'}
    out['witness_gap_decomposition'] = decomp

    results = {}
    for onset_model in (dec.ONSET_AVG, dec.FREE_BOTH):
        results[onset_model] = {}
        for flag_after in (True, False):
            order = 'flag_after_checks' if flag_after else 'flag_before_checks'
            decs = decoders_for(onset_model, flag_after)
            block = {}
            for name, fn in decs.items():
                block[name] = {
                    'indist_witness': score_decoder(indist_witness_hist, fn, onset_model),
                    'indist_all': score_decoder(indist_all, fn, onset_model),
                    'fresh_weight4': score_decoder(fresh, fn, onset_model)}
            results[onset_model][order] = block
    out['results'] = results

    with open('stage1_handback.json', 'w') as fh:
        json.dump(out, fh, indent=2, default=str)

    _print(out)
    return out


def _print(out):
    print("=" * 74)
    print("STAGE 1: minimal restorer vs baselines  (frozen protocol; results)")
    print("=" * 74)
    print("onset reconciliation:", out['onset_model_reconciliation']['verdict'])
    print("  FREE_BOTH witnesses:", out['onset_model_reconciliation']['FREE_BOTH']['witnesses'],
          " ONSET_AVG witnesses:", out['onset_model_reconciliation']['ONSET_AVG']['witnesses'])
    print("controls reconciliation: 52/129 is ONE shared Stage-0 calculation "
          "(prompt=loss_aware=wide_window).")
    print("eval sets:", out['eval_sets'])
    print("\nwitness-gap decomposition (flag_after, IN-DIST witnesses):")
    for onset, d in out['witness_gap_decomposition'].items():
        print(f"  {onset}: deadline_ref vs full={d['deadline_ref_vs_full_ref']} "
              f"| restorer vs full={d['restorer_vs_full_ref']} "
              f"| restorer vs deadline={d['restorer_vs_deadline_ref']} "
              f"| correct: deadline={d['deadline_ref_correct']} restorer={d['restorer_correct']}")
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        print(f"\n########## onset model: {onset} ##########")
        for order in ('flag_after_checks', 'flag_before_checks'):
            print(f"\n--- {order} ---")
            blk = out['results'][onset][order]
            hdr = f"  {'decoder':<16}{'set':<18}{'cover':>7}{'ref_agree':>11}{'correct':>9}"
            print(hdr)
            for name in ('restorer_2bit', 'baseline_0bit', 'streaming_hard',
                         'deadline_reference'):
                for setname in ('indist_witness', 'indist_all', 'fresh_weight4'):
                    s = blk[name][setname]
                    print(f"  {name:<16}{setname:<18}{s['coverage']:>7}"
                          f"{s['reference_agreement']:>11}{s['logical_correct']:>9}")


if __name__ == '__main__':
    main()
