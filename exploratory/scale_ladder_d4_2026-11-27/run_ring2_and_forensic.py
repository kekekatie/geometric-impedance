"""Follow-up runner for experiment/scale-ladder-d4-2026-11-27:
  1) Radial Ring-1 -> Ring-2 -> Ring-3 -> All-Z -> Full-Thick lightcone closure
     across all four d=(4,4) Bulk-vs.-Boundary sites.
  2) Exact k=2 forensic decomposition of paired-face interaction I on the two
     Corner-Ear sites (Pen_d4_ear, I=-14.6%, contrasted with AB_d4_ear, I=-0.3%).

Reuses the exact untouched (3,3) decoder, CorrectedPatchCode, 128-bit Indexed
prefilter, and exhaustive k<=2 ordinary-fault ensemble from run_d4_ladder.py.
"""

import argparse
import collections as C
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "results"
sys.path.insert(0, str(ROOT))

import run_d4_ladder as base  # noqa: E402
from run_d4_ladder import CorrectedPatchCode, Indexed, SITES, check_index, same  # noqa: E402
import paired_run as prior  # noqa: E402


def build_rings(code: CorrectedPatchCode, qubit: int):
    d = code.json
    nx, nz = len(d["HX"]), len(d["HZ"])
    hz = [{j for j, v in enumerate(r) if v} for r in d["HZ"]]
    hx = [{j for j, v in enumerate(r) if v} for r in d["HX"]]

    r1_z = {i for i, s in enumerate(hz) if qubit in s}
    r1_x = {i for i, s in enumerate(hx) if qubit in s}
    assert len(r1_z) == 2 and len(r1_x) == 2

    # Dual-graph BFS from Ring-1 Z-faces (sharing a data edge)
    z_ring = {i: 1 for i in r1_z}
    frontier = set(r1_z)
    rad = 1
    while frontier:
        qs = set().union(*(hz[i] for i in frontier))
        nxt = {i for i, s in enumerate(hz) if i not in z_ring and (s & qs)}
        rad += 1
        for i in nxt:
            z_ring[i] = rad
        frontier = nxt

    r2_z = {i for i, r in z_ring.items() if r == 2}
    r3_z = {i for i, r in z_ring.items() if r == 3}
    r1_z_qubits = set().union(*(hz[i] for i in r1_z))
    r2_x = {i for i, s in enumerate(hx) if i not in r1_x and (s & r1_z_qubits)}

    def z_idx(zset):
        return [nx + i for i in sorted(zset)]

    def x_idx(xset):
        return sorted(xset)

    star = sorted(x_idx(r1_x) + z_idx(r1_z))
    assert star == code.STAR[qubit]

    subsets = {
        "thin": [],
        "ring1": star,
        "ring2_z": sorted(star + z_idx(r2_z)),
        "ring2_xz": sorted(star + z_idx(r2_z) + x_idx(r2_x)),
        "ring3_z": sorted(star + z_idx(r2_z | r3_z)),
        "all_z": sorted(star + z_idx(set(range(nz)) - r1_z)),
    }
    ring_info = {
        "nx": nx,
        "nz": nz,
        "r1_z": [f"Z{i}" for i in sorted(r1_z)],
        "r1_x": [f"X{i}" for i in sorted(r1_x)],
        "r2_z": [f"Z{i}" for i in sorted(r2_z)],
        "r2_x": [f"X{i}" for i in sorted(r2_x)],
        "r3_z": [f"Z{i}" for i in sorted(r3_z)],
        "z_rings_by_dist": {
            str(r): [f"Z{i}" for i in sorted(i for i, dr in z_ring.items() if dr == r)]
            for r in sorted(set(z_ring.values()))
        },
        "subset_check_counts": {k: len(v) for k, v in subsets.items()},
    }
    return subsets, ring_info, z_ring, hz


def decide_subset(D, dz, dx, bz, bx, frames, indices):
    if not indices:
        selected_z = {(k, t) for k in D.s.ZSTABS for t in (3, 4)}
        selected_x = {(k, t) for k in D.s.XSTABS for t in (3, 4)}
    else:
        idx_set = set(indices)
        selected_z = {(k, t) for k in D.s.ZSTABS for t in (3, 4)} | {
            (k, t) for k in idx_set if k in D.s.ZSTABS for t in (1, 2)
        }
        selected_x = {(k, t) for k in D.s.XSTABS for t in (3, 4)} | {
            (k, t) for k in idx_set if k in D.s.XSTABS for t in (1, 2)
        }
    az = {d: v for d, v in dz.items() if d in selected_z}
    ax = {d: v for d, v in dx.items() if d in selected_x}
    return D.decide(az, ax, bz, bx, frames)


def run_site(name: str, forensic: bool):
    start = time.time()
    patch_path = OUT_DIR / f"{name}.json"
    meta = json.loads((OUT_DIR / f"{name}_meta.json").read_text(encoding="utf-8"))
    code = CorrectedPatchCode(patch_path)
    d = code.json
    q = meta["qubit"]
    nx, nz = len(d["HX"]), len(d["HZ"])

    subsets, ring_info, z_ring, hz = build_rings(code, q)
    D = Indexed(code, q)
    assert D.star == code.STAR[q]

    names = ["thin", "ring1", "ring2_z", "ring2_xz", "ring3_z", "all_z", "thick"]
    if forensic:
        bulk_ci = check_index(meta["bulk_zcheck"], nx, nz)
        bnd_ci = check_index(meta["boundary_zcheck"], nx, nz)
        x_star = [i for i in D.star if i < nx]
        subsets["bulk_only"] = sorted(x_star + [bulk_ci])
        subsets["bnd_only"] = sorted(x_star + [bnd_ci])
        subsets["neither_face"] = sorted(x_star)
        names.extend(["bulk_only", "bnd_only", "neither_face"])

    credits = {a: [0.0, 0.0, 0.0] for a in names}
    counts = [0, 0, 0]
    checks = dict(direct_fullscan_checks=0, direct_fullscan_mismatches=0, max_posterior_difference=0.0)

    # Forensic accumulators
    mode_counts = C.Counter()
    mode_dI = C.defaultdict(float)
    config_dI = C.defaultdict(lambda: [0.0, 0, C.Counter()])  # key -> [sum_dI, nhist, mode_counter]
    qubit_ring = {}
    for qid in range(d["n"]):
        inc_rings = [z_ring[zi] for zi, s in enumerate(hz) if qid in s]
        qubit_ring[qid] = min(inc_rings) if inc_rings else -1

    pool = prior.ordinary_pool(code)
    h = hashlib.sha256()
    n = 0

    for cid, k, extra in prior.config_stream(pool):
        h.update((json.dumps([cid, k, extra], separators=(",", ":")) + "\n").encode())
        for onset, vx, vz in prior.VARIANTS:
            loss = ([("X", q, onset)] if vx else []) + ([("Z", q, onset)] if vz else [])
            dz, dx, truth, _ = code.simulate(*prior.nd_run.compose(extra + tuple(loss)))
            bz = {kk: dz[kk, 0] ^ dz[kk, 1] ^ dz[kk, 2] for kk in D.s.ZSTABS}
            bx = {kk: dx[kk, 0] ^ dx[kk, 1] ^ dx[kk, 2] for kk in D.s.XSTABS}
            frames = D.observed_frames(dz, dx)

            dec = {}
            for a in names:
                if a == "thick":
                    dec[a] = D.direct(dz, dx, "thick")
                else:
                    dec[a] = decide_subset(D, dz, dx, bz, bx, frames, subsets[a])
            c = {a: prior.cred(dec[a], truth) for a in names}
            for a in names:
                credits[a][k] += c[a]

            if forensic:
                dI = (c["bulk_only"] + c["bnd_only"]) - (c["ring1"] + c["neither_face"])
                if abs(dI) > 1e-12:
                    pat = (c["ring1"], c["bulk_only"], c["bnd_only"], c["neither_face"])
                    mode_counts[(k, pat)] += 1
                    mode_dI[(k, pat)] += dI
                    cfg_key = (k, tuple(extra))
                    rec = config_dI[cfg_key]
                    rec[0] += dI
                    rec[1] += 1
                    rec[2][pat] += 1

            counts[k] += 1
            n += 1

            if n % 3001 == 0:
                method, cache = D._marginal_compute, D._mcache
                D._marginal_compute = D._marginal_fullscan
                D._mcache = {}
                try:
                    for a in names:
                        if a == "thick":
                            rr = D.direct(dz, dx, "thick")
                        else:
                            rr = decide_subset(D, dz, dx, bz, bx, frames, subsets[a])
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(
                            checks["max_posterior_difference"], abs(rr["p0"] - dec[a]["p0"])
                        )
                finally:
                    D._marginal_compute, D._mcache = method, cache

        if len(D._mcache) > 500000:
            D._mcache.clear()
        if cid % 15000 == 0:
            print(name, "cid=", cid, "n=", n, "sec=", round(time.time() - start, 1), flush=True)

    assert checks["direct_fullscan_mismatches"] == 0
    weights = [prior.ODDS**k for k in range(3)]
    mass = sum(c * w for c, w in zip(counts, weights))
    mean = lambda arr: sum(c * w for c, w in zip(arr, weights)) / mass

    scores = {a: mean(credits[a]) for a in names}
    full_gain = 100.0 * (scores["thick"] - scores["thin"])
    ladder = {}
    for a in ["ring1", "ring2_z", "ring2_xz", "ring3_z", "all_z", "thick"]:
        g = 100.0 * (scores[a] - scores["thin"])
        ladder[a] = dict(
            gain_pp=g,
            pct_of_full=100.0 * g / full_gain if abs(full_gain) > 1e-12 else None,
            n_checks=len(subsets[a]) if a in subsets else (nx + nz),
        )

    out = dict(
        site=name,
        meta=meta,
        ring_info=ring_info,
        histories=n,
        histories_by_weight=counts,
        config_stream_sha256=h.hexdigest(),
        full_archive_gain_pp=full_gain,
        radial_ladder=ladder,
        validation=checks,
        elapsed_seconds=round(time.time() - start, 2),
    )

    if forensic:
        lz_set = set(meta["scored_logical_Z"])
        bulk_zi = int(meta["bulk_zcheck"][1:])
        bnd_zi = int(meta["boundary_zcheck"][1:])
        bulk_qs = hz[bulk_zi]
        bnd_qs = hz[bnd_zi]

        modes_summary = []
        for (kk, pat), cnt in sorted(mode_counts.items(), key=lambda x: -abs(mode_dI[x[0]])):
            dI_pp = 100.0 * mode_dI[(kk, pat)] * weights[kk] / mass
            modes_summary.append(
                dict(
                    k=kk,
                    pattern_intact_bulk_bnd_neither=list(pat),
                    count=cnt,
                    raw_dI_sum=mode_dI[(kk, pat)],
                    weighted_dI_pp=dI_pp,
                    pct_of_full=100.0 * dI_pp / full_gain,
                )
            )

        def annotate_extra(extra_tuple):
            ann = []
            for ptype, qid, t in extra_tuple:
                zfaces = [f"Z{zi}" for zi, s in enumerate(hz) if qid in s]
                ann.append(
                    dict(
                        pauli=ptype,
                        qubit=qid,
                        round=t,
                        on_scored_LZ=(qid in lz_set),
                        on_bulk_face=(qid in bulk_qs),
                        on_bnd_face=(qid in bnd_qs),
                        ring=qubit_ring[qid],
                        zfaces=zfaces,
                    )
                )
            return ann

        sorted_cfgs = sorted(config_dI.items(), key=lambda x: x[1][0])
        top_synergy = []
        for (kk, ext), (sdI, nh, mc) in sorted_cfgs[:15]:
            if sdI >= 0:
                break
            dI_pp = 100.0 * sdI * weights[kk] / mass
            top_synergy.append(
                dict(
                    k=kk,
                    faults=annotate_extra(ext),
                    n_nonzero_variants=nh,
                    raw_dI_sum=sdI,
                    weighted_dI_pp=dI_pp,
                    pct_of_full=100.0 * dI_pp / full_gain,
                    modes={str(list(p)): cnt for p, cnt in mc.items()},
                )
            )
        top_redundancy = []
        for (kk, ext), (sdI, nh, mc) in reversed(sorted_cfgs[-15:]):
            if sdI <= 0:
                break
            dI_pp = 100.0 * sdI * weights[kk] / mass
            top_redundancy.append(
                dict(
                    k=kk,
                    faults=annotate_extra(ext),
                    n_nonzero_variants=nh,
                    raw_dI_sum=sdI,
                    weighted_dI_pp=dI_pp,
                    pct_of_full=100.0 * dI_pp / full_gain,
                    modes={str(list(p)): cnt for p, cnt in mc.items()},
                )
            )

        g_intact = 100.0 * (scores["ring1"] - scores["thin"])
        g_bulk = 100.0 * (scores["bulk_only"] - scores["thin"])
        g_bnd = 100.0 * (scores["bnd_only"] - scores["thin"])
        g_neither = 100.0 * (scores["neither_face"] - scores["thin"])
        I_pp = (g_bulk + g_bnd) - (g_intact + g_neither)

        out["forensic"] = dict(
            four_terms_gain_pp=dict(
                both_kept=g_intact,
                bulk_only=g_bulk,
                bnd_only=g_bnd,
                neither_face=g_neither,
            ),
            I_pp=I_pp,
            I_pct_of_full=100.0 * I_pp / full_gain,
            total_nonzero_dI_histories=sum(mode_counts.values()),
            modes=modes_summary,
            top_synergy_configs=top_synergy,
            top_redundancy_configs=top_redundancy,
        )

    out_path = OUT_DIR / f"{name}_ring2_forensic.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"COMPLETE {name} in {out['elapsed_seconds']}s | full={full_gain:.6f} pp | "
        f"R1={ladder['ring1']['pct_of_full']:.2f}% -> R2_Z={ladder['ring2_z']['pct_of_full']:.2f}% -> "
        f"R2_XZ={ladder['ring2_xz']['pct_of_full']:.2f}% -> R3_Z={ladder['ring3_z']['pct_of_full']:.2f}% -> "
        f"All_Z={ladder['all_z']['pct_of_full']:.2f}%",
        flush=True,
    )
    if forensic:
        f = out["forensic"]
        print(
            f"  FORENSIC {name}: I={f['I_pp']:+.6f} pp ({f['I_pct_of_full']:+.1f}%) | "
            f"nonzero_hist={f['total_nonzero_dI_histories']} | top_modes={[(m['k'], m['pattern_intact_bulk_bnd_neither'], m['count'], round(m['pct_of_full'], 2)) for m in f['modes'][:5]]}",
            flush=True,
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=list(SITES), required=True)
    ap.add_argument("--forensic", action="store_true")
    args = ap.parse_args()
    run_site(args.site, args.forensic)
