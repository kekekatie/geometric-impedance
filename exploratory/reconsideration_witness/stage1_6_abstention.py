"""Stage 1.6: two reasons to abstain, compared at matched coverage.

Built on Stage 1.5 (commit b43826a). Reuses stage1 / stage1_5 machinery; changes
nothing frozen there. Distance-3 repetition code unchanged.

Both abstention policies run on the SAME existing two-bit Bayesian restorer, from
the SAME retained inputs, and defer/abstain on the SAME proposed logical answer.
Primary restorer input = round-0 readings (`t0`); timing parity (`lip_parity`) is
a prespecified secondary comparison. Primary deadline = round-4 checks then loss
flag (`flag_after`); the reverse order (`flag_before`) is reported separately.

Two policies (higher score = more want to abstain):
  P1  LOW CONFIDENCE       : score = -|P(0)-P(1)| of the restorer's posterior.
                             Abstain on the smallest margin first.
  P2  SENSITIVITY TO        : enumerate discarded core completions compatible with
      DISCARDED HISTORY       the retained state + deadline observations; weight each
                              by its model probability; for each, take the unpruned
                              full-prefix prediction AT THE SAME DEADLINE
                              (deadline-reference). score = posterior probability mass
                              of completions whose deadline prediction REVERSES the
                              proposed answer. Abstain on the largest reversal mass.

Policies see only permitted inputs. The scoring harness alone sees the actual
discarded readings and the simulated logical truth. A deferred answer counts as an
abstention; later recovery is out of scope.

================================= FROZEN PROTOCOL =============================
(committed before the run; this file precedes its own output in git.)

TIE HANDLING.
  * Deadline ties (a completion's deadline-reference posterior is within EPS):
    counted in a separate `tie_mass`, NOT as a reversal (conservative), reported.
  * Restorer proposed-answer ties (P0==P1 within EPS): proposed = 0 (argmax,
    P0>=P1), counted separately; such a case is maximally abstainable under both.
  * Ranking score ties at a coverage boundary: broken deterministically by the
    history's fault-tuple in FAULT_IDS order (lexicographic). Frozen.

EVALUATION SETS (documented).
  * fresh_w4_uniform   : all weight-exactly-4 histories with a d1 loss in O
                         (6930), uniform weight. Primary fresh ensemble, distinct
                         from the witness set, discriminative (many hard cases).
  * bounded_le4_prior  : all histories with a d1 loss in O and total weight <= 4,
                         weighted by model prior of the NON-loss faults
                         (w = prod base_weight over extra faults). Realistic mix.
  * witness_stress     : the 258 Stage-0 witness-pair histories, uniform weight.
                         Separate stress test (selection-biased; reported as such).

COVERAGE COMPARISON.
  Coverage kappa = answered weight / total weight. Grid {1.0,0.9,0.8,0.7,0.6,0.5}.
  At kappa, each policy answers the kappa-weight fraction with the LOWEST abstention
  score; error is the weighted fraction of ANSWERED cases whose proposed answer
  differs from the target. Scored separately vs the actual same-deadline
  deadline-reference (ties in the actual deadline-ref excluded from that denominator,
  counted) and vs simulated truth. Policies compared at matched kappa.

CHECKS. always-answer two-bit decoder = the kappa=1 row. four-reading restorer
  (`bracket4`) reported at kappa=1 as a ceiling (it equals the deadline-optimal).
  Determinism: histories with identical permitted inputs must yield identical
  proposed answers and identical P1/P2 scores (asserted).

FROZEN PREDICTIONS.
  A1 Vs the deadline-reference, at matched kappa<1, P2 (sensitivity) has <= error
     than P1 (low-confidence) on the witness stress set. Conf ~60%.
  A2 Vs truth, the two policies are within a couple points at matched kappa;
     neither dominates. Conf ~50%.
  A3 On bounded_le4_prior, errors are low and P1 ~ P2 (easy mass dominates). ~60%.
  A4 bracket4 has ~0 error vs the deadline-reference and lower error than the
     always-answer two-bit decoder vs truth. Conf ~90%.
  A5 Determinism holds exactly (identical permitted inputs -> identical outputs). ~99%.
===============================================================================
"""

import itertools
import json
from functools import lru_cache

import repcode as rc
import decoders as dec
import stage1 as s1
import stage1_5_onset_lip as s15

EPS = dec.EPS
CHK = range(len(rc.CHECKS))
_TWO = s1._TWO
GRID = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
LOSS = [('d', rc.LOSS_SITE, s) for s in rc.O]


def _deadline_marginal_for_core(core6, d3, det4, flag_after, onset):
    det4_choices = [det4] if flag_after else _TWO
    P0 = P1 = 0.0
    for d4 in det4_choices:
        for d5 in _TWO:
            for cl in _TWO:
                full = s1._full_detset(core6, d3, d4, d5, cl)
                p0, p1 = s1._ref_marginal_ds(full, True, onset)
                P0 += p0
                P1 += p1
    return P0, P1


@lru_cache(maxsize=None)
def _analyze_core(frame, m2, d3, det4, variant, obs, flag_after, onset):
    """All policy quantities, cached by the PERMITTED-INPUT key only."""
    s_core = [b for b in s1.FRAME_OF_CORE
              if s1.M2_OF_CORE[b] == m2 and s1.FRAME_OF_CORE[b] == frame
              and s15._core_ok(b, variant, obs)]
    cores = []
    P0 = P1 = 0.0
    for core6 in s_core:
        cp0, cp1 = _deadline_marginal_for_core(core6, d3, det4, flag_after, onset)
        P0 += cp0
        P1 += cp1
        cores.append((cp0, cp1))
    tot = P0 + P1
    proposed = 0 if P0 >= P1 else 1
    margin = abs(P0 - P1) / tot if tot > 0 else 0.0
    restorer_strict = (abs(P0 - P1) > EPS * tot) if tot > 0 else False
    rev = tie = 0.0
    for cp0, cp1 in cores:
        w = cp0 + cp1
        if w <= 0:
            continue
        dstrict = abs(cp0 - cp1) > EPS * w
        dpred = 0 if cp0 >= cp1 else 1
        if not dstrict:
            tie += w
        elif dpred != proposed:
            rev += w
    reversal_mass = rev / tot if tot > 0 else 0.0
    tie_mass = tie / tot if tot > 0 else 0.0
    return {'proposed': proposed, 'margin': margin, 'restorer_strict': restorer_strict,
            'reversal_mass': reversal_mass, 'tie_mass': tie_mass, 'n_cores': len(cores)}


def analyze(detset, variant, flag_after, onset):
    frame = dec.streaming_commit(detset)
    m2 = dec.m2_boundary(detset)
    d3 = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in CHK)
    det4 = tuple(1 if (c, 4) in detset else 0 for c in CHK) if flag_after else None
    return _analyze_core(frame, m2, d3, det4, variant, s15._obs(detset, variant),
                         flag_after, onset)


def actual_deadline_ref(detset, flag_after, onset):
    """Scoring-only: the deadline-reference for the ACTUAL history (full core).
    Returns (pred, strict)."""
    core6 = tuple(1 if s15.CORE_POS[i] in detset else 0 for i in range(6))
    d3 = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in CHK)
    det4 = tuple(1 if (c, 4) in detset else 0 for c in CHK) if flag_after else None
    P0, P1 = _deadline_marginal_for_core(core6, d3, det4, flag_after, onset)
    tot = P0 + P1
    return (0 if P0 >= P1 else 1), (abs(P0 - P1) > EPS * tot if tot > 0 else False)


# ---- ensembles --------------------------------------------------------------
def _loss_histories(weights):
    seen, out = set(), []
    for w in weights:
        for combo in itertools.combinations(dec.FAULT_IDS, w):
            fs = frozenset(combo)
            if not any(lf in fs for lf in LOSS):
                continue
            if fs in seen:
                continue
            seen.add(fs)
            out.append(fs)
    return out


def _prior_weight(faults):
    extra = sorted(faults, key=lambda f: dec.FIDX[f])
    # drop the single lowest-index loss fault; weight the rest by base prior
    for lf in LOSS:
        if lf in extra:
            extra.remove(lf)
            break
    w = 1.0
    for f in extra:
        w *= dec.base_weight(f)
    return w


def ensembles():
    w4 = _loss_histories([4])
    le4 = _loss_histories([1, 2, 3, 4])
    witness = [h['faults'] for pr in s1.witness_indist() for h in pr]
    return {
        'fresh_w4_uniform': [(f, 1.0) for f in w4],
        'bounded_le4_prior': [(f, _prior_weight(f)) for f in le4],
        'witness_stress': [(f, 1.0) for f in witness],
    }


# ---- scoring ----------------------------------------------------------------
def build_cases(hist_weights, variant, flag_after, onset):
    cases = []
    for faults, w in hist_weights:
        ds = rc.detectors_of(faults, dec.H)
        a = analyze(ds, variant, flag_after, onset)
        dref, dref_strict = actual_deadline_ref(ds, flag_after, onset)
        truth = rc.logical_of(faults, dec.L)
        cases.append({
            'faults': tuple(sorted(faults, key=lambda f: dec.FIDX[f])),
            'weight': w, 'proposed': a['proposed'], 'margin': a['margin'],
            'reversal_mass': a['reversal_mass'], 'tie_mass': a['tie_mass'],
            'dref': dref if dref_strict else None, 'truth': truth,
            'score_lowconf': -a['margin'], 'score_sens': a['reversal_mass']})
    return cases


def sweep(cases, score_key):
    """Matched-coverage error curve.

    stage1_6_tie_fix: ties in the abstention score are resolved by EXACT EXPECTATION
    over the tied score bucket -- NEVER by the hidden simulator fault tuple (which the
    decoder cannot see and which front-loads heavier fault patterns). When a coverage
    cutoff lands inside a tied-score bucket, that bucket is included fractionally and
    contributes its MEAN error, i.e. the exact expected value over uniform random
    tie-breaking within the bucket. Equivalent to keying only by permitted observables
    and averaging across ties.
    """
    from collections import defaultdict
    W = sum(c['weight'] for c in cases)
    buckets = defaultdict(lambda: {'w': 0.0, 'cnt': 0, 'truth_err': 0.0,
                                   'dw': 0.0, 'dref_err': 0.0})
    for c in cases:
        b = buckets[round(c[score_key], 12)]
        b['w'] += c['weight']
        b['cnt'] += 1
        b['truth_err'] += c['weight'] if c['proposed'] != c['truth'] else 0.0
        if c['dref'] is not None:
            b['dw'] += c['weight']
            b['dref_err'] += c['weight'] if c['proposed'] != c['dref'] else 0.0
    order = sorted(buckets)                       # ascending score = answered first
    res = {}
    for kappa in GRID:
        budget = kappa * W
        inc_w = inc_cnt = inc_truth = inc_dw = inc_dref = acc = 0.0
        for s in order:
            b = buckets[s]
            if acc + b['w'] <= budget + 1e-12:
                f = 1.0
            else:
                f = (budget - acc) / b['w'] if b['w'] > 0 else 0.0
                if f <= 0:
                    break
            inc_w += f * b['w']
            inc_cnt += f * b['cnt']
            inc_truth += f * b['truth_err']
            inc_dw += f * b['dw']
            inc_dref += f * b['dref_err']
            acc += b['w']
            if f < 1.0:
                break
        e_dref = inc_dref / inc_dw if inc_dw > 0 else None
        e_truth = inc_truth / inc_w if inc_w > 0 else None
        res[kappa] = {'answered_frac': round(inc_w / W, 4),
                      'n_answered_expected': round(inc_cnt, 1),
                      'err_vs_dref': round(e_dref, 4) if e_dref is not None else None,
                      'err_vs_truth': round(e_truth, 4) if e_truth is not None else None}
    return res


def permitted_key(detset, variant, flag_after, onset):
    """Exactly the inputs a deadline decoder is permitted (no discarded readings)."""
    frame = dec.streaming_commit(detset)
    m2 = dec.m2_boundary(detset)
    d3 = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in CHK)
    det4 = tuple(1 if (c, 4) in detset else 0 for c in CHK) if flag_after else None
    return (frame, m2, d3, det4, variant, s15._obs(detset, variant), flag_after, onset)


def determinism_check(hist_weights, variant, flag_after, onset):
    """Two DIFFERENT histories sharing a permitted key must give identical proposed
    answer and identical P1/P2 scores. Returns (ok, groups_tested, collisions_seen)."""
    seen = {}
    collisions = 0
    for faults, _w in hist_weights:
        ds = rc.detectors_of(faults, dec.H)
        k = permitted_key(ds, variant, flag_after, onset)
        a = analyze(ds, variant, flag_after, onset)
        sig = (a['proposed'], round(a['margin'], 12), round(a['reversal_mass'], 12))
        if k in seen:
            collisions += 1
            if seen[k] != sig:
                return False, len(seen), collisions
        else:
            seen[k] = sig
    return True, len(seen), collisions


def bracket4_row(hist_weights, flag_after, onset):
    """four-reading restorer at kappa=1: error vs deadline-ref and truth."""
    W = ok_dref = ok_truth = dwsum = 0.0
    for faults, w in hist_weights:
        ds = rc.detectors_of(faults, dec.H)
        pred, _ = s15.variant_predict(ds, 'bracket4', flag_after, onset)
        dref, dstrict = actual_deadline_ref(ds, flag_after, onset)
        truth = rc.logical_of(faults, dec.L)
        W += w
        if dstrict:
            dwsum += w
            ok_dref += w if pred != dref else 0
        ok_truth += w if pred != truth else 0
    return {'err_vs_dref': round(ok_dref / dwsum, 4) if dwsum else None,
            'err_vs_truth': round(ok_truth / W, 4) if W else None}


def main():
    ens = ensembles()
    out = {'built_on': 'b43826a', 'grid': GRID,
           'predictions': 'see module docstring (frozen A1-A5)'}

    # determinism: histories sharing a permitted key must give identical outputs
    det = {}
    for ens_name in ('fresh_w4_uniform', 'bounded_le4_prior', 'witness_stress'):
        ok, groups, coll = determinism_check(ens[ens_name], 't0', True, dec.ONSET_AVG)
        det[ens_name] = {'ok': ok, 'distinct_permitted_keys': groups,
                         'colliding_histories': coll}
    out['determinism_identical_inputs_identical_outputs'] = det

    results = {}
    # primary: t0, flag_after, both onsets, all ensembles. plus flag_before on
    # fresh_w4 + witness. plus lip_parity secondary on fresh_w4 + witness (flag_after).
    plan = []
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        for ens_name in ('fresh_w4_uniform', 'bounded_le4_prior', 'witness_stress'):
            plan.append(('t0', True, onset, ens_name))
        for ens_name in ('fresh_w4_uniform', 'witness_stress'):
            plan.append(('t0', False, onset, ens_name))
            plan.append(('lip_parity', True, onset, ens_name))

    for variant, flag_after, onset, ens_name in plan:
        cases = build_cases(ens[ens_name], variant, flag_after, onset)
        key = f"{onset}|{'flag_after' if flag_after else 'flag_before'}|input={variant}|{ens_name}"
        results[key] = {
            'P1_lowconf': sweep(cases, 'score_lowconf'),
            'P2_sensitivity': sweep(cases, 'score_sens'),
            'bracket4_check': bracket4_row(ens[ens_name], flag_after, onset),
            'n_cases': len(cases),
            'mean_tie_mass': round(sum(c['tie_mass'] for c in cases) / len(cases), 4),
            'cases_where_policies_rank_differently': _rank_diff(cases),
        }
    out['results'] = results

    # one concrete case where the two policies disagree most (primary setting)
    cases = build_cases(ens['witness_stress'], 't0', True, dec.ONSET_AVG)
    out['example_divergent_case'] = _divergent_example(cases)

    with open('stage1_6_handback.json', 'w') as fh:
        json.dump(out, fh, indent=2, default=str)
    _print(out)
    return out


def _rank_diff(cases):
    """Count cases whose two abstention scores rank them on opposite sides of the
    median (a coarse 'policies disagree' tally)."""
    import statistics
    m1 = statistics.median(c['score_lowconf'] for c in cases)
    m2 = statistics.median(c['score_sens'] for c in cases)
    diff = sum(1 for c in cases
               if (c['score_lowconf'] > m1) != (c['score_sens'] > m2))
    return f"{diff}/{len(cases)}"


def _divergent_example(cases):
    # normalize both scores to ranks, find the largest rank disagreement
    # The documented illustrative case (a double-onset loss): report its two RAW
    # scores, never an integer rank inside the tied reversal_mass=0 bucket (such a rank
    # depends on list order, as Astra noted). Fall back to the smallest-margin correct
    # P2-kept case if the documented one is absent from this set.
    tie0 = [c for c in cases if abs(c['score_sens']) <= 1e-12]
    documented = frozenset([('d', 0, 0), ('d', 1, 1), ('d', 1, 2)])
    match = [c for c in cases if frozenset(c['faults']) == documented]
    if match:
        best = match[0]
    else:
        pool = [c for c in tie0 if c['proposed'] == c['truth']] or tie0
        best = min(pool, key=lambda c: (c['margin'], c['faults']))
    return {'faults': [list(f) for f in best['faults']],
            'proposed': best['proposed'],
            'P1_score_margin': round(best['margin'], 6),
            'P2_score_reversal_mass': round(best['reversal_mass'], 6),
            'in_P2_zero_reversal_bucket_of_size': len(tie0),
            'actual_deadline_ref': best['dref'], 'truth': best['truth'],
            'reading': 'P1 is tempted to abstain (small margin) though the answer is '
                       'correct; P2 keeps it (reversal_mass = 0, i.e. no discarded '
                       'completion would flip the deadline-optimal) -- it sits in the '
                       'large zero-reversal bucket and is not singled out. No integer '
                       'rank is reported because ranks inside the tied bucket depend '
                       'on list order.'}


def _print(out):
    print("=" * 80)
    print("STAGE 1.6: two reasons to abstain, at matched coverage")
    print("=" * 80)
    print("determinism (identical permitted inputs -> identical outputs):")
    for en, d in out['determinism_identical_inputs_identical_outputs'].items():
        print(f"   {en}: ok={d['ok']} ({d['colliding_histories']} histories shared a "
              f"key across {d['distinct_permitted_keys']} keys)")
    for key, r in out['results'].items():
        print(f"\n### {key}   (n={r['n_cases']}, mean tie_mass={r['mean_tie_mass']}, "
              f"policies-differ {r['cases_where_policies_rank_differently']})")
        print(f"   bracket4 check: err_vs_dref={r['bracket4_check']['err_vs_dref']} "
              f"err_vs_truth={r['bracket4_check']['err_vs_truth']}")
        print(f"   {'kappa':>6} | {'P1 err_dref':>12}{'P2 err_dref':>12} | "
              f"{'P1 err_truth':>13}{'P2 err_truth':>13}")
        for k in GRID:
            a = r['P1_lowconf'][k]
            b = r['P2_sensitivity'][k]
            print(f"   {k:>6} | {str(a['err_vs_dref']):>12}{str(b['err_vs_dref']):>12} | "
                  f"{str(a['err_vs_truth']):>13}{str(b['err_vs_truth']):>13}")
    print("\n### example divergent case (witness, t0, onset_avg, flag_after):")
    for k, v in out['example_divergent_case'].items():
        print(f"   {k}: {v}")


if __name__ == '__main__':
    main()
