#!/usr/bin/env python3
"""
Reverse-Loop Test -- experiment runners (Exp 1, Exp 2; Exp 3 is analysis-only).

Each row emitted is one walker. Matched sets share S, T and the direct backbone;
conditions differ only in the spliced loop, so endpoints are identical by
construction.
"""

import numpy as np
import walker as W


TIERS = {"0.5x": 0.5, "1x": 1.0, "2x": 2.0, "4x": 4.0}
CONDITIONS = {"C1": "in_zone", "C2": "crossing", "C3": "deep_dip"}


def _row(patch, substrate, condition, tier, matched_id, start_zone,
         S, T, path, method):
    res, _ = W.residue_stepwise(patch, path)
    ts = W.transit_stats(patch, path)
    return dict(
        substrate=substrate, condition=condition, tier=tier,
        matched_id=matched_id, start_zone=int(start_zone),
        S=int(S), T=int(T),
        path_len=len(path) - 1,
        final_residue=res,
        directional_balance=W.directional_balance(patch, path),
        max_transit_depth=ts["max_transit_depth"],
        min_transit_depth=ts["min_transit_depth"],
        zone_crossings=ts["zone_crossings"],
        deepest_zone=ts["deepest_zone"],
        shallowest_zone=ts["shallowest_zone"],
        S_depth=float(patch.depth[S]), T_depth=float(patch.depth[T]),
        S_zone=int(patch.zone[S]), T_zone=int(patch.zone[T]),
        splice_method=method,
    )


def run_experiment1(patch, substrate, rng, n_sets, L_direct, comp,
                    progress_every=200):
    """Spliced-loop equivalence. Returns list of walker rows."""
    rows = []
    comp_set = set(comp.tolist())
    made = 0
    attempts = 0
    while made < n_sets and attempts < n_sets * 30:
        attempts += 1
        s = W.sample_direct(patch, rng, L_direct, comp)
        if s is None:
            continue
        S, T, path, dist, parent = s
        start_zone = patch.zone[S]

        # choose an interior splice vertex (avoid the endpoints)
        if len(path) < 5:
            continue
        # Build all conditions x tiers; require the whole matched set to succeed
        set_rows = []
        # C0 direct appears once per matched set
        set_rows.append(_row(patch, substrate, "C0", "0x", made, start_zone,
                             S, T, path, "direct"))
        ok = True
        for cond_name, kind in CONDITIONS.items():
            for tier_name, tier_mult in TIERS.items():
                target_len = max(2, int(round(tier_mult * L_direct)))
                # try several splice points
                loop = None
                method = None
                for _ in range(8):
                    xi = int(rng.integers(1, len(path) - 1))
                    X = path[xi]
                    loop, method = W.make_cycle(patch, X, target_len, rng,
                                                kind, comp_set)
                    if loop is not None:
                        break
                if loop is None:
                    ok = False
                    break
                spliced = W.splice(path, loop)
                set_rows.append(_row(patch, substrate, cond_name, tier_name,
                                     made, start_zone, S, T, spliced, method))
            if not ok:
                break
        if not ok:
            continue
        rows.extend(set_rows)
        made += 1
        if progress_every and made % progress_every == 0:
            print(f"    [{substrate}] Exp1 matched sets: {made}/{n_sets}",
                  flush=True)
    return rows, made


def run_experiment2(patch, substrate, rng, n_loops, L_direct, comp,
                    progress_every=200):
    """
    Closed-loop holonomy probe. S = T. For each loop we record pre-loop residue
    (a reference direct walk of length L_direct ending at S) and post-loop
    residue (that same walk continued around the closed loop back to S).

    C4 = retrace control (must cancel). C5 = non-retraced cycles.
    """
    rows = []
    comp_set = set(comp.tolist())
    made = 0
    attempts = 0
    # C5 spans the three depth classes, mirroring C1-C3
    c5_kinds = {"C5_in_zone": "in_zone", "C5_crossing": "crossing",
                "C5_deep_dip": "deep_dip"}
    while made < n_loops and attempts < n_loops * 30:
        attempts += 1
        s = W.sample_direct(patch, rng, L_direct, comp)
        if s is None:
            continue
        S, preT, pre_path, dist, parent = s
        # the loop base vertex is preT (walker's current position)
        base = preT
        pre_res, pre_vec = W.residue_stepwise(patch, pre_path)
        start_zone = patch.zone[S]

        set_rows = []
        for tier_name, tier_mult in TIERS.items():
            target_len = max(2, int(round(tier_mult * L_direct)))
            # C4 retrace
            loop4, m4 = W.make_cycle(patch, base, target_len, rng, "retrace",
                                     comp_set)
            if loop4 is None:
                continue
            full4 = pre_path + loop4[1:]
            post4, _ = W.residue_stepwise(patch, full4)
            r = _row(patch, substrate, "C4", tier_name, made, start_zone,
                     S, base, full4, m4)
            r.update(pre_residue=pre_res, post_residue=post4,
                     loop_residual=abs(post4 - pre_res),
                     loop_holonomy=W.residue_stepwise(patch, loop4)[0],
                     loop_return_phys=float(np.linalg.norm(
                         patch.par[loop4[-1]] - patch.par[loop4[0]])),
                     loop_len=len(loop4) - 1,
                     loop_max_depth=float(patch.depth[loop4].max()),
                     loop_depth_range=float(patch.depth[loop4].max()
                                            - patch.depth[loop4].min()),
                     loop_zone_crossings=int(np.count_nonzero(
                         np.diff(patch.zone[loop4]) != 0)))
            set_rows.append(r)

            # C5 non-retraced, three depth classes
            for c5name, kind in c5_kinds.items():
                loop5, m5 = None, None
                for _ in range(8):
                    loop5, m5 = W.make_cycle(patch, base, target_len, rng,
                                             kind, comp_set)
                    if loop5 is not None and not _is_retrace(loop5):
                        break
                if loop5 is None:
                    continue
                full5 = pre_path + loop5[1:]
                post5, _ = W.residue_stepwise(patch, full5)
                r = _row(patch, substrate, c5name, tier_name, made, start_zone,
                         S, base, full5, m5)
                r.update(pre_residue=pre_res, post_residue=post5,
                         loop_residual=abs(post5 - pre_res),
                         loop_holonomy=W.residue_stepwise(patch, loop5)[0],
                         loop_return_phys=float(np.linalg.norm(
                             patch.par[loop5[-1]] - patch.par[loop5[0]])),
                         loop_len=len(loop5) - 1,
                         loop_max_depth=float(patch.depth[loop5].max()),
                         loop_depth_range=float(patch.depth[loop5].max()
                                                - patch.depth[loop5].min()),
                         loop_zone_crossings=int(np.count_nonzero(
                             np.diff(patch.zone[loop5]) != 0)))
                set_rows.append(r)
        if not set_rows:
            continue
        rows.extend(set_rows)
        made += 1
        if progress_every and made % progress_every == 0:
            print(f"    [{substrate}] Exp2 loops: {made}/{n_loops}", flush=True)
    return rows, made


def _is_retrace(loop):
    """Heuristic: is this closed loop an exact out-and-back?"""
    h = len(loop) // 2
    return loop[:h + 1] == loop[h:][::-1]


def sensitivity_dzone(patch, rng, n, L_direct, comp):
    """
    Mandatory sensitivity control (Sec 4.1): reproduce the known depth-zone
    effect on residue at this N and record its effect size d_zone.

    The linger result established that *movement between depth zones* changes
    residue (the mechanism chain gap->residue, Spearman ~0.30, deeper = better
    address pinning = less perp drift). We operationalise the known positional
    effect as the *maximal* depth-zone contrast: final residue for walks whose
    endpoint lands in the shallowest zone (0) vs the deepest zone (n_zones-1).
    Returns (shallow_res, deep_res, per_zone_means).
    """
    nz = patch.n_zones
    byzone = {z: [] for z in range(nz)}
    tries = 0
    need = n
    while (len(byzone[0]) < need or len(byzone[nz - 1]) < need) and tries < n * 120:
        tries += 1
        s = W.sample_direct(patch, rng, L_direct, comp)
        if s is None:
            continue
        S, T, path, _, _ = s
        tz = int(patch.zone[T])
        if len(byzone[tz]) < need:
            byzone[tz].append(W.residue_stepwise(patch, path)[0])
    per_zone_means = [float(np.mean(byzone[z])) if byzone[z] else float("nan")
                      for z in range(nz)]
    return (np.array(byzone[0]), np.array(byzone[nz - 1]), per_zone_means)
