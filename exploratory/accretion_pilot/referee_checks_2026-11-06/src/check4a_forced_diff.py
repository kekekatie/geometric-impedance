#!/usr/bin/env python3
"""
check4a_forced_diff.py -- Check 4a: A/B forced-consequence diff on all 22 forks.

Move class: FORCED ONLY (no free choices). For each fork, forced-close Sstar+A and
Sstar+B, diff the closures tile by tile, and classify the diff as a single strip
along one of the five worm directions, per PROTOCOL.md (one edge-connected
component, principal axis within 12 deg of a worm direction, aspect ratio >= 3).

Writes results/check4a_forced_diff.json and results/worm_lines.json (the per-world
worm line d_w, p_w used by check 4b). Pre-registered; outcomes not inspected before
PROTOCOL commit.
"""
from __future__ import annotations
import json, math, cmath
import rc_common as RC

AXIS_TOL_DEG = 12.0
ASPECT_MIN = 3.0


def classify_strip(diff_tiles):
    if not diff_tiles:
        return dict(single_strip=False, kind="no_difference", n_components=0)
    comps = RC.edge_components(diff_tiles)
    cents = [RC.tile_centroid(t) for t in diff_tiles]
    axis, length, width = RC.pca_axis_extent(cents)
    widx, resid = RC.nearest_worm(axis)
    aspect = (length / width) if width > 1e-9 else float("inf")
    single = (len(comps) == 1 and resid <= AXIS_TOL_DEG and aspect >= ASPECT_MIN)
    return dict(single_strip=bool(single), kind="strip" if single else "not_single_strip",
                n_components=len(comps),
                worm_index=int(widx), axis_residual_deg=round(float(resid), 3),
                axis_angle_deg=round(math.degrees(cmath.phase(axis)) % 180.0, 3),
                length_S=round(length, 3), width_S=round(width, 3),
                aspect_ratio=round(aspect, 3) if aspect != float("inf") else None,
                component_sizes=[len(c) for c in comps[:6]])


def main():
    RC.RESULTS.mkdir(parents=True, exist_ok=True)
    forks = RC.RD.load_forks()
    worlds = sorted(forks)
    out = []; worm_lines = {}; diff_regions = {}
    n_strip = 0
    for w in worlds:
        Sstar = forks[w]["Sstar"]; A = forks[w]["cs"][0]; B = forks[w]["cs"][1]
        cA, sA, addA, zA = RC.forced_closure(list(Sstar) + [A])
        cB, sB, addB, zB = RC.forced_closure(list(Sstar) + [B])
        ka = {RC.dk(t) for t in cA}; kb = {RC.dk(t) for t in cB}
        a_only_keys = ka - kb; b_only_keys = kb - ka
        amap = {RC.dk(t): t for t in cA}; bmap = {RC.dk(t): t for t in cB}
        diff_tiles = [amap[k] for k in a_only_keys] + [bmap[k] for k in b_only_keys]
        cls = classify_strip(diff_tiles)
        # lift-conflict check on the diff geometry (should be 0)
        try:
            _, _, conf = RC.lift_tiles(diff_tiles) if diff_tiles else ([], {}, [])
            n_conf = len(conf)
        except Exception as e:  # noqa
            n_conf = f"lift_error:{type(e).__name__}"
        rec = dict(world=w, closure_status=[sA, sB], n_added=[addA, addB],
                   zero_candidate_edges=[zA, zB],
                   n_A_only=len(a_only_keys), n_B_only=len(b_only_keys),
                   n_diff=len(diff_tiles), diff_lift_conflicts=n_conf, **cls)
        out.append(rec)
        # A/B difference region (used by check 4b's EXPLORATORY overlap split; the
        # pre-registered worm line is only defined for single strips, below).
        if diff_tiles:
            cents = [RC.tile_centroid(t) for t in diff_tiles]
            p_diff = sum(cents) / len(cents)
            axis, _, _ = RC.pca_axis_extent(cents)
            dvkeys = sorted({repr(RC.L.key(z)) for t in diff_tiles for z in t[1:]})
            diff_regions[str(w)] = dict(world=w, worm_index=cls.get("worm_index"),
                                        single_strip=cls["single_strip"],
                                        p_diff=[p_diff.real, p_diff.imag],
                                        d_axis=[axis.real, axis.imag],
                                        diff_vertex_keys=dvkeys)
        if cls["single_strip"]:
            n_strip += 1
            cents = [RC.tile_centroid(t) for t in diff_tiles]
            p_w = sum(cents) / len(cents)
            d_w = RC.WORM_DIRS[cls["worm_index"]]
            worm_lines[str(w)] = dict(world=w, worm_index=cls["worm_index"],
                                      d_w=[d_w.real, d_w.imag], p_w=[p_w.real, p_w.imag],
                                      length_S=cls["length_S"], width_S=cls["width_S"])
        print(f"[4a] w{w:>2}: A+{addA} B+{addB} | diff {len(diff_tiles)} "
              f"(A_only {len(a_only_keys)}, B_only {len(b_only_keys)}) comps={cls['n_components']} "
              f"strip={cls['single_strip']} worm={cls.get('worm_index')} "
              f"resid={cls.get('axis_residual_deg')} asp={cls.get('aspect_ratio')} "
              f"L={cls.get('length_S')} W={cls.get('width_S')}", flush=True)

    summary = dict(n_forks=len(worlds), n_single_strip=n_strip,
                   prediction_P4a_threshold=20, P4a_held=bool(n_strip >= 20))
    (RC.RESULTS / "check4a_forced_diff.json").write_text(
        json.dumps(dict(summary=summary, forks=out), indent=2, default=float))
    (RC.RESULTS / "worm_lines.json").write_text(json.dumps(worm_lines, indent=2, default=float))
    (RC.RESULTS / "diff_regions.json").write_text(json.dumps(diff_regions, default=float))
    print(f"\nP4a: single strip in {n_strip}/{len(worlds)} forks (need >= 20) -> "
          f"{'HELD' if n_strip >= 20 else 'FAILED'}")
    print("wrote results/check4a_forced_diff.json, results/worm_lines.json")


if __name__ == "__main__":
    main()
