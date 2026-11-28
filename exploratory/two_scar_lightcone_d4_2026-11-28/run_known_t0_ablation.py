"""Known-onset (t0) ablation runner for experiment/two-scar-lightcone-d4-2026-11-28.

Replays the exact same exhaustive k<=2 ensembles and Indexed / Indexed2 decoders
from run_two_scar.py, but reveals the true onset time t0 in {1, 2} to the decoder
(conditioning both thin and archived arms on known t0) to separate shared-clock
timing coupling from spatial / logical-bridge coupling.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "results"
sys.path.insert(0, str(ROOT))

import run_two_scar as base  # noqa: E402
from run_two_scar import (  # noqa: E402
    CorrectedPatchCode,
    Indexed,
    Indexed2,
    VARIANTS_2,
    build_rings_for_qubits,
    ensure_patch,
    prior,
    same,
)
import patch_decoder as pd  # noqa: E402

ABLATION_PAIRS = {
    "Pen_sep":   base.PAIRS["Pen_sep"],
    "Pen_touch": base.PAIRS["Pen_touch"],
    "AB_sep":    base.PAIRS["AB_sep"],
    "AB_touch":  base.PAIRS["AB_touch"],
}

ABLATION_SINGLES = {
    "Pen_d4_mid": [3, 9, 11],
    "AB_2scar":   [5, 12, 18],
}


def decide_known_t0(D, az, ax, bz, bx, frames, onset: int, verify_z: bool = False):
    """Exact bounded posterior conditioned on known onset t0.
    Because onset is fixed, the Z-sector marginal r > 0 cancels identically from
    p0/(p0+p1); verify_z=True explicitly computes r and multiplies (for full-scan checks).
    """
    q0, q1 = D._marginal("X", tuple(sorted(az.items())), tuple(sorted(bz.items())), frames[0], onset, True)
    if verify_z:
        r = D._marginal("Z", tuple(sorted(ax.items())), tuple(sorted(bx.items())), frames[1], onset, False)
        p0, p1 = r * q0, r * q1
    else:
        p0, p1 = q0, q1
    tot = p0 + p1
    if tot <= 0:
        raise ValueError("zero evidence")
    p0n, p1n = p0 / tot, p1 / tot
    tie = abs(p0n - p1n) <= pd.EPS
    label = 0 if (tie or p0n >= p1n) else 1
    return dict(label=label, p0=p0n, p1=p1n, tie=bool(tie))


def decide_subset_known_t0(D, dz, dx, bz, bx, frames, indices, onset: int, thick: bool = False, verify_z: bool = False):
    if thick:
        return decide_known_t0(D, dz, dx, {}, {}, frames, onset, verify_z=verify_z)
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
    return decide_known_t0(D, az, ax, bz, bx, frames, onset, verify_z=verify_z)


def run_single_known_t0(patch_name: str, q: int):
    start = time.time()
    out_path = OUT_DIR / f"{patch_name}_single_q{q}_known_t0.json"
    if out_path.exists():
        print(f"SKIP existing {out_path.name}", flush=True)
        return
    patch_path = ensure_patch(patch_name)
    code = CorrectedPatchCode(patch_path)
    subsets, rinfo = build_rings_for_qubits(code, [q])
    D = Indexed(code, q)
    names = ["thin", "ring1", "ring2_z", "thick"]
    credits = {a: [0.0, 0.0, 0.0] for a in names}
    counts = [0, 0, 0]
    checks = dict(direct_fullscan_checks=0, direct_fullscan_mismatches=0, max_posterior_difference=0.0)
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
            dec = {
                a: decide_subset_known_t0(D, dz, dx, bz, bx, frames, subsets.get(a, []), onset, thick=(a == "thick"))
                for a in names
            }
            for a in names:
                credits[a][k] += prior.cred(dec[a], truth)
            counts[k] += 1
            n += 1
            if n % 4001 == 0:
                method, cache = D._marginal_compute, D._mcache
                D._marginal_compute = D._marginal_fullscan
                D._mcache = {}
                try:
                    for a in names:
                        rr = decide_subset_known_t0(
                            D, dz, dx, bz, bx, frames, subsets.get(a, []), onset, thick=(a == "thick"), verify_z=True
                        )
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(checks["max_posterior_difference"], abs(rr["p0"] - dec[a]["p0"]))
                finally:
                    D._marginal_compute, D._mcache = method, cache
        if len(D._mcache) > 500000:
            D._mcache.clear()
        if cid % 25000 == 0:
            print(f"{patch_name}_q{q}_t0 cid={cid} n={n} sec={round(time.time()-start,1)}", flush=True)

    assert checks["direct_fullscan_mismatches"] == 0, checks
    weights = [prior.ODDS ** k for k in range(3)]
    mass = sum(c * w for c, w in zip(counts, weights))
    mean = lambda arr: sum(c * w for c, w in zip(arr, weights)) / mass
    scores = {a: mean(credits[a]) for a in names}
    gain_by_k = {
        a: [100.0 * (credits[a][k] - credits["thin"][k]) * weights[k] / mass for k in range(3)]
        for a in ("ring1", "ring2_z", "thick")
    }
    full = 100.0 * (scores["thick"] - scores["thin"])
    r1 = 100.0 * (scores["ring1"] - scores["thin"])
    r2 = 100.0 * (scores["ring2_z"] - scores["thin"])
    out = dict(
        mode="single_known_t0", patch=patch_name, qubit=q, n_qubits=code.NDATA,
        histories=n, histories_by_weight=counts, config_stream_sha256=h.hexdigest(),
        ring_info=rinfo,
        full_gain_pp=full, ring1_gain_pp=r1, ring2_z_gain_pp=r2,
        ring1_pct_of_full=100.0 * r1 / full if abs(full) > 1e-12 else None,
        ring2_z_pct_of_full=100.0 * r2 / full if abs(full) > 1e-12 else None,
        gain_by_k_pp=gain_by_k,
        validation=checks, elapsed_seconds=round(time.time() - start, 2),
    )
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"COMPLETE SINGLE_T0 {patch_name}_q{q} in {out['elapsed_seconds']}s | full={full:.6f} pp | "
        f"R1={out['ring1_pct_of_full']:.2f}% -> R2={out['ring2_z_pct_of_full']:.2f}% | "
        f"full_by_k={[round(x,6) for x in gain_by_k['thick']]}",
        flush=True,
    )


def run_pair_known_t0(pair_name: str, max_configs: int = 0):
    start = time.time()
    cfg = ABLATION_PAIRS[pair_name]
    patch_name = cfg["patch"]
    qA, qB = cfg["qubits"]
    patch_path = ensure_patch(patch_name)
    code = CorrectedPatchCode(patch_path)
    subsets, rinfo = build_rings_for_qubits(code, [qA, qB])
    D = Indexed2(code, qA, qB)
    names = ["thin", "ring1", "ring2_z", "thick"]
    credits = {a: [0.0, 0.0, 0.0] for a in names}
    counts = [0, 0, 0]
    checks = dict(direct_fullscan_checks=0, direct_fullscan_mismatches=0, max_posterior_difference=0.0)
    pool = prior.ordinary_pool(code)
    h = hashlib.sha256()
    n = 0
    check_mod = 50 if max_configs else 16001

    for cid, k, extra in prior.config_stream(pool):
        if max_configs and cid >= max_configs:
            break
        h.update((json.dumps([cid, k, extra], separators=(",", ":")) + "\n").encode())
        for onset, vxA, vzA, vxB, vzB in VARIANTS_2:
            loss = (
                ([("X", qA, onset)] if vxA else [])
                + ([("Z", qA, onset)] if vzA else [])
                + ([("X", qB, onset)] if vxB else [])
                + ([("Z", qB, onset)] if vzB else [])
            )
            dz, dx, truth, _ = code.simulate(*prior.nd_run.compose(extra + tuple(loss)))
            bz = {kk: dz[kk, 0] ^ dz[kk, 1] ^ dz[kk, 2] for kk in D.s.ZSTABS}
            bx = {kk: dx[kk, 0] ^ dx[kk, 1] ^ dx[kk, 2] for kk in D.s.XSTABS}
            frames = D.observed_frames(dz, dx)
            dec = {
                a: decide_subset_known_t0(D, dz, dx, bz, bx, frames, subsets.get(a, []), onset, thick=(a == "thick"))
                for a in names
            }
            for a in names:
                credits[a][k] += prior.cred(dec[a], truth)
            counts[k] += 1
            n += 1
            if n % check_mod == 0:
                method, cache = D._marginal_compute, D._mcache
                D._marginal_compute = D._marginal_fullscan
                D._mcache = {}
                try:
                    for a in names:
                        rr = decide_subset_known_t0(
                            D, dz, dx, bz, bx, frames, subsets.get(a, []), onset, thick=(a == "thick"), verify_z=True
                        )
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(checks["max_posterior_difference"], abs(rr["p0"] - dec[a]["p0"]))
                finally:
                    D._marginal_compute, D._mcache = method, cache
        if len(D._mcache) > 600000:
            D._mcache.clear()
        if cid % 20000 == 0:
            print(f"{pair_name}_t0 cid={cid} n={n} sec={round(time.time()-start,1)}", flush=True)

    assert checks["direct_fullscan_mismatches"] == 0, checks
    weights = [prior.ODDS ** k for k in range(3)]
    mass = sum(c * w for c, w in zip(counts, weights))
    mean = lambda arr: sum(c * w for c, w in zip(arr, weights)) / mass
    scores = {a: mean(credits[a]) for a in names}
    gain_by_k = {
        a: [100.0 * (credits[a][k] - credits["thin"][k]) * weights[k] / mass for k in range(3)]
        for a in ("ring1", "ring2_z", "thick")
    }
    full = 100.0 * (scores["thick"] - scores["thin"])
    r1 = 100.0 * (scores["ring1"] - scores["thin"])
    r2 = 100.0 * (scores["ring2_z"] - scores["thin"])
    out = dict(
        mode="pair_known_t0", pair=pair_name, patch=patch_name, regime=cfg["regime"],
        qubits=list(cfg["qubits"]), n_qubits=code.NDATA,
        histories=n, histories_by_weight=counts, config_stream_sha256=h.hexdigest(),
        ring_info=rinfo,
        full_gain_pp=full, ring1_gain_pp=r1, ring2_z_gain_pp=r2,
        ring1_pct_of_full=100.0 * r1 / full if abs(full) > 1e-12 else None,
        ring2_z_pct_of_full=100.0 * r2 / full if abs(full) > 1e-12 else None,
        gain_by_k_pp=gain_by_k,
        validation=checks, elapsed_seconds=round(time.time() - start, 2),
    )
    if not max_configs:
        out_path = OUT_DIR / f"{pair_name}_known_t0_result.json"
        out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"COMPLETE PAIR_T0 {pair_name} ({'SELFTEST' if max_configs else 'FULL'}) in {out['elapsed_seconds']}s | "
        f"hist={n} | full={full:.6f} pp | R1={out['ring1_pct_of_full']}% -> R2={out['ring2_z_pct_of_full']}% | "
        f"full_by_k={[round(x,6) for x in gain_by_k['thick']]} | checks={checks}",
        flush=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--pair", choices=list(ABLATION_PAIRS))
    ap.add_argument("--singles", choices=list(ABLATION_SINGLES))
    args = ap.parse_args()
    if args.selftest:
        run_pair_known_t0("Pen_sep", max_configs=15)
    elif args.pair:
        run_pair_known_t0(args.pair)
    elif args.singles:
        for q in ABLATION_SINGLES[args.singles]:
            run_single_known_t0(args.singles, q)
