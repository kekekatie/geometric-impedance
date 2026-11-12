"""Stage 1.5 diagnostic: live-vs-live scoring and the onset-lip hypothesis.

Built on Stage 1 (commit bfa9446). Reuses stage1's exact machinery; changes
nothing frozen there. Two questions, from Argon:

(1) LIVE-vs-LIVE. At the Round-4 deadline, round 5 and the readout have not
    happened. Judging a live restorer against the omniscient end-of-film
    reference mixes pruning loss with ~5% future-noise. So score every decoder
    DIRECTLY against the deadline-reference (the unpruned full-history decoder's
    prediction AT the deadline), for both flag orders, alongside full-reference
    and ground truth.

(2) THE ONSET-LIP HYPOTHESIS. Under FREE_BOTH, rounds 1 and 2 are one frictionless
    hole whose floor is round 0, so the two t0 corners (c0,t0),(c1,t0) suffice.
    Under ONSET_AVG the stone drops at round 1 OR round 2; if it waits for round 2,
    round 1 is still solid ground, so the lip sits at t1 (c0,t1),(c1,t1) -- and the
    round-1 detectors are also what tell the posterior WHEN it dropped. Keeping only
    t0 should therefore leave a gap under ONSET_AVG that t1 (or the full t0+t1
    bracket) closes.

Compares restorer variants keeping different pieces of the pruned core (always on
top of the retained frame + m2 + d3):
    0bit        : serialized state only
    t0          : + (c0,t0),(c1,t0)
    t1          : + (c0,t1),(c1,t1)
    lip_parity  : + (c0, t0^t1),(c1, t0^t1)      -- the "when did it drop" parity
    3bit        : + (c0,t0),(c1,t0),(c0,t1)       -- bracket minus one corner
    bracket4    : + (c0,t0),(c1,t0),(c0,t1),(c1,t1) -- the full onset bracket

Scored on the bounded witness set and the 6930 fresh weight-4 histories, under
ONSET_AVG and FREE_BOTH, against deadline-reference and full-reference and truth.

================================ FROZEN PREDICTIONS ============================
Written before running this script (git: this file is committed before its output).

L1. LIVE-vs-LIVE. Every decoder's agreement vs the deadline-reference exceeds its
    agreement vs the full-reference (removing the ~5% future-noise). Conf ~80%.
L2. ONSET-LIP. Under ONSET_AVG, vs the deadline-reference, t1 > t0 on the witness
    set (the lip and the onset-timing bit live at round 1). Conf ~60%.
L3. Under FREE_BOTH, t0 alone is near-complete (t0 ~ bracket4 vs deadline-ref),
    while t1 is weaker -- the mirror of L2. Conf ~60%.
L4. bracket4 == deadline-reference exactly (agreement 1.000 vs deadline-ref, both
    models, both sets): the full pruned core + m2 reconstructs the whole core, so a
    4-bit restorer IS the deadline-optimal. Conf ~85%.
L5. lip_parity (2 bits) beats t0 under ONSET_AVG but does not reach bracket4: the
    timing parity helps but is not the whole story. Conf ~45%.
L6. REDUNDANCY. bracket4 + m2 already pins the core to a single syndrome (|S_core|
    = 1), so frame is redundant there. For 3bit, frame does NOT in general pin the
    last free core bit (frame is a non-invertible threshold), so 3bit < bracket4 and
    all four bracket bits are needed. Conf ~55%.
===============================================================================
"""

import itertools
import json
from functools import lru_cache

import repcode as rc
import decoders as dec
import stage1 as s1

CHK = range(len(rc.CHECKS))
CORE_POS = s1.CORE_POS                      # [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
IDX = {p: i for i, p in enumerate(CORE_POS)}
_TWO = s1._TWO


def _obs(detset, variant):
    """Observed values of the kept detectors, as a hashable tuple, per variant."""
    c0t0 = 1 if (0, 0) in detset else 0
    c1t0 = 1 if (1, 0) in detset else 0
    c0t1 = 1 if (0, 1) in detset else 0
    c1t1 = 1 if (1, 1) in detset else 0
    if variant == '0bit':
        return ()
    if variant == 't0':
        return (c0t0, c1t0)
    if variant == 't1':
        return (c0t1, c1t1)
    if variant == 'lip_parity':
        return (c0t0 ^ c0t1, c1t0 ^ c1t1)
    if variant == '3bit':
        return (c0t0, c1t0, c0t1)
    if variant == 'bracket4':
        return (c0t0, c1t0, c0t1, c1t1)
    raise ValueError(variant)


def _core_ok(core6, variant, obs):
    g = lambda c, t: core6[IDX[(c, t)]]
    if variant == '0bit':
        return True
    if variant == 't0':
        return (g(0, 0), g(1, 0)) == obs
    if variant == 't1':
        return (g(0, 1), g(1, 1)) == obs
    if variant == 'lip_parity':
        return (g(0, 0) ^ g(0, 1), g(1, 0) ^ g(1, 1)) == obs
    if variant == '3bit':
        return (g(0, 0), g(1, 0), g(0, 1)) == obs
    if variant == 'bracket4':
        return (g(0, 0), g(1, 0), g(0, 1), g(1, 1)) == obs
    raise ValueError(variant)


@lru_cache(maxsize=None)
def _variant_core(frame, m2, d3, det4, variant, obs, flag_after, onset_model, use_frame):
    s_core = [b for b in s1.FRAME_OF_CORE
              if s1.M2_OF_CORE[b] == m2
              and (not use_frame or s1.FRAME_OF_CORE[b] == frame)
              and _core_ok(b, variant, obs)]
    det4_choices = [det4] if flag_after else _TWO
    P0 = P1 = 0.0
    for core6 in s_core:
        for d4 in det4_choices:
            for d5 in _TWO:
                for cl in _TWO:
                    full = s1._full_detset(core6, d3, d4, d5, cl)
                    p0, p1 = s1._ref_marginal_ds(full, True, onset_model)
                    P0 += p0
                    P1 += p1
    tot = P0 + P1
    if tot == 0.0:
        return None, 0
    pred = 0 if P0 >= P1 else 1
    return pred, len(s_core)


def variant_predict(detset, variant, flag_after, onset_model, use_frame=True):
    frame = dec.streaming_commit(detset)
    m2 = dec.m2_boundary(detset)
    d3 = tuple(1 if (c, rc.COMMIT_C) in detset else 0 for c in CHK)
    det4 = tuple(1 if (c, 4) in detset else 0 for c in CHK) if flag_after else None
    return _variant_core(frame, m2, d3, det4, variant, _obs(detset, variant),
                         flag_after, onset_model, use_frame)


# ---- scoring ----------------------------------------------------------------
def score(histories, predict, flag_after, onset_model):
    """Agreement of `predict(ds)->pred` vs deadline-ref, full-ref, and truth."""
    a_dead = a_full = a_true = 0
    score_count = 0
    scmax = 0
    for h in histories:
        ds = h['detset']
        full = s1._ref_predict_ds(ds, True, onset_model)
        if not full[3]:
            continue
        pred, sc = predict(ds)
        if pred is None:
            continue
        scmax = max(scmax, sc)
        score_count += 1
        dref = s1.deadline_reference(ds, flag_after, onset_model)
        truth = rc.logical_of(h['faults'], dec.L)
        a_dead += (pred == dref)
        a_full += (pred == full[0])
        a_true += (pred == truth)
    n = score_count
    return {'n': n,
            'vs_deadline_ref': round(a_dead / n, 4) if n else None,
            'vs_full_ref': round(a_full / n, 4) if n else None,
            'vs_truth': round(a_true / n, 4) if n else None,
            'max_Score_candidates': scmax}


def streaming_hard_pred(flag_after):
    return lambda ds: (s1.streaming_hard(ds, flag_after), 1)


def main():
    witness = [h for pr in s1.witness_indist() for h in pr]
    fresh = [{'faults': f, 'detset': rc.detectors_of(f, dec.H)}
             for f in s1.fresh_histories()]
    sets = {'witness': witness, 'fresh_weight4': fresh}

    out = {'built_on': 'bfa9446', 'predictions': 'see module docstring (frozen)'}

    # (1) live-vs-live: baseline decoders vs deadline-ref, full-ref, truth, both orders
    live = {}
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        live[onset] = {}
        for flag_after in (True, False):
            order = 'flag_after' if flag_after else 'flag_before'
            live[onset][order] = {}
            decs = {
                'streaming_hard': streaming_hard_pred(flag_after),
                '0bit': (lambda fa, om: lambda ds: variant_predict(ds, '0bit', fa, om))(flag_after, onset),
                't0_restorer': (lambda fa, om: lambda ds: variant_predict(ds, 't0', fa, om))(flag_after, onset),
            }
            for setname, hists in sets.items():
                live[onset][order][setname] = {
                    name: score(hists, fn, flag_after, onset) for name, fn in decs.items()}
    out['live_vs_live'] = live

    # (2) onset-lip variants (flag_after), vs deadline-ref, full-ref, truth
    variants = ['0bit', 't0', 't1', 'lip_parity', '3bit', 'bracket4']
    lip = {}
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        lip[onset] = {}
        for setname, hists in sets.items():
            lip[onset][setname] = {}
            for v in variants:
                fn = (lambda vv, om: lambda ds: variant_predict(ds, vv, True, om))(v, onset)
                lip[onset][setname][v] = score(hists, fn, True, onset)
    out['onset_lip_variants'] = lip

    # (3) redundancy: |S_core| for bracket4 and 3bit (with frame); does frame make
    #     a 4th bit redundant? and bracket4 with vs without frame.
    red = {}
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        # on the union of both sets
        allh = witness + fresh
        b4_sc = []
        b3_sc = []
        b4_vs_b4nf = 0           # bracket4 with frame vs without frame (should match)
        b3_vs_b4 = 0             # 3bit vs bracket4 (do they agree?)
        tot = 0
        for h in allh:
            ds = h['detset']
            full = s1._ref_predict_ds(ds, True, onset)
            if not full[3]:
                continue
            tot += 1
            p_b4, sc_b4 = variant_predict(ds, 'bracket4', True, onset, use_frame=True)
            p_b4nf, _ = variant_predict(ds, 'bracket4', True, onset, use_frame=False)
            p_b3, sc_b3 = variant_predict(ds, '3bit', True, onset, use_frame=True)
            b4_sc.append(sc_b4)
            b3_sc.append(sc_b3)
            b4_vs_b4nf += (p_b4 == p_b4nf)
            b3_vs_b4 += (p_b3 == p_b4)
        red[onset] = {
            'decisions': tot,
            'bracket4_Score_candidates_max': max(b4_sc), 'bracket4_Score_candidates_mean': round(sum(b4_sc)/len(b4_sc), 3),
            '3bit_Score_candidates_max': max(b3_sc), '3bit_Score_candidates_mean': round(sum(b3_sc)/len(b3_sc), 3),
            'bracket4_frame_redundant (with==without frame)': f"{b4_vs_b4nf}/{tot}",
            '3bit_agrees_with_bracket4': f"{b3_vs_b4}/{tot}"}
    out['redundancy'] = red

    with open('stage1_5_handback.json', 'w') as fh:
        json.dump(out, fh, indent=2, default=str)
    _print(out)
    return out


def _print(out):
    print("=" * 78)
    print("STAGE 1.5: live-vs-live and the onset-lip hypothesis")
    print("=" * 78)
    print("\n### (1) LIVE-vs-LIVE  (agreement vs deadline-ref | full-ref | truth)")
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        for order in ('flag_after', 'flag_before'):
            print(f"\n-- {onset} / {order} --")
            for setname in ('witness', 'fresh_weight4'):
                print(f"   [{setname}]")
                for name, s in out['live_vs_live'][onset][order][setname].items():
                    print(f"     {name:<16} dead={s['vs_deadline_ref']}  full={s['vs_full_ref']}  truth={s['vs_truth']}")
    print("\n### (2) ONSET-LIP VARIANTS  (flag_after; vs deadline-ref | full-ref | truth)")
    for onset in (dec.ONSET_AVG, dec.FREE_BOTH):
        for setname in ('witness', 'fresh_weight4'):
            print(f"\n-- {onset} / {setname} --")
            print(f"     {'variant':<12}{'vs_dead':>9}{'vs_full':>9}{'vs_truth':>9}")
            for v in ['0bit', 't0', 't1', 'lip_parity', '3bit', 'bracket4']:
                s = out['onset_lip_variants'][onset][setname][v]
                print(f"     {v:<12}{s['vs_deadline_ref']:>9}{s['vs_full_ref']:>9}{s['vs_truth']:>9}")
    print("\n### (3) REDUNDANCY")
    for onset, r in out['redundancy'].items():
        print(f"-- {onset} --")
        for k, v in r.items():
            print(f"     {k}: {v}")


if __name__ == '__main__':
    main()
