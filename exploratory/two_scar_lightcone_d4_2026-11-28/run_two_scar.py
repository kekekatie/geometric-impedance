"""Phase 2 runner for experiment/two-scar-lightcone-d4-2026-11-28 (frozen protocol cd555f5).

Implements an exact simultaneous two-erasure extension (Indexed2) of the untouched
(3,3) bounded decoder (nd_infer.py) with 128-bit safe SIGP_LO/SIGP_HI packing,
plus matching single-scar baselines on the exact same d=(4,4) patches:
  - Pen_d4_mid (n=26, 12X/13Z):
      Pen_sep   : (q9, q11)  — Separated Control (ovR12=0, d_er=(3,3))
      Pen_touch : (q3, q9)   — Lightcone-Touching (ovR1=0, ovR12=3, d_er=(3,3))
      Pen_coll  : (q4, q5)   — Same-Route Collision (ovR1=1, ovR12=6, d_er=(2,4))
  - AB_2scar (n=31, 15X/15Z):
      AB_sep    : (q12, q18) — Separated Control (ovR12=0, d_er=(3,3))
      AB_touch  : (q5, q12)  — Lightcone-Touching (ovR1=0, ovR12=3, d_er=(3,3))
      AB_coll   : (q10, q20) — Same-Route Collision (ovR1=1, ovR12=5, d_er=(2,3))
"""

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PRED_SRC = REPO / "exploratory" / "aperiodic_predict_2026-11-20" / "src"
D4_DIR = REPO / "exploratory" / "scale_ladder_d4_2026-11-27"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PRED_SRC))
sys.path.insert(0, str(D4_DIR))
import geom_select as gs  # noqa: E402
import paired_run as prior  # noqa: E402
import patch_decoder as pd  # noqa: E402
from run_d4_ladder import CorrectedPatchCode, Indexed, same  # noqa: E402

PAIRS = {
    "Pen_sep":   dict(patch="Pen_d4_mid", regime="Separated Control",    qubits=(9, 11)),
    "Pen_touch": dict(patch="Pen_d4_mid", regime="Lightcone-Touching",   qubits=(3, 9)),
    "Pen_coll":  dict(patch="Pen_d4_mid", regime="Same-Route Collision", qubits=(4, 5)),
    "AB_sep":    dict(patch="AB_2scar",   regime="Separated Control",    qubits=(12, 18)),
    "AB_touch":  dict(patch="AB_2scar",   regime="Lightcone-Touching",   qubits=(5, 12)),
    "AB_coll":   dict(patch="AB_2scar",   regime="Same-Route Collision", qubits=(10, 20)),
}

SINGLES = {
    "Pen_d4_mid": [3, 4, 5, 9, 11],
    "AB_2scar":   [5, 10, 12, 18, 20],
}

VARIANTS_2 = [
    (o, vxA, vzA, vxB, vzB)
    for o in (1, 2)
    for vxA in (0, 1)
    for vzA in (0, 1)
    for vxB in (0, 1)
    for vzB in (0, 1)
]


def ensure_patch(patch_name: str) -> Path:
    dest = OUT_DIR / f"{patch_name}.json"
    if dest.exists():
        return dest
    if patch_name == "Pen_d4_mid":
        src = D4_DIR / "results" / "Pen_d4_mid.json"
        shutil.copy2(src, dest)
        print(f"Copied existing Pen_d4_mid.json -> {dest}", flush=True)
        return dest
    if patch_name == "AB_2scar":
        p = gs.pilot.parent("AB", large=True)
        facec = {i: np.mean([p["pos"][v] for v in vs], axis=0) for i, vs in enumerate(p["faces"])}
        centres = sorted(
            (v for v in p["pos"] if sum(t * t for t in p["pos"][v]) <= 9),
            key=lambda v: (round(sum(t * t for t in p["pos"][v]), 10), v),
        )[:8]
        v = centres[2]
        aspect = 1.5
        order = sorted(
            facec,
            key=lambda f: (
                round(((facec[f][0] - p["pos"][v][0]) / aspect) ** 2 + ((facec[f][1] - p["pos"][v][1]) * aspect) ** 2, 10),
                tuple(sorted(p["faces"][f])),
            ),
        )
        dsk = gs.pilot.disk(p, tuple(sorted(order[:15])))
        assert dsk is not None
        corners = (0, 3, 8, 15)
        c = gs.pilot.cut(p, dsk, corners)
        x, z = gs.pilot.distances(dsk, c)
        assert len(x) == 4 and len(z) == 4
        specd = dict(centre=v, aspect=aspect, angle=0.0, spec=("AB", 15), corners=corners)
        obj = gs.pilot.export(p, (None, dsk, c, specd, x, z), {})
        assert obj["n"] == 31 and len(obj["HX"]) == 15 and len(obj["HZ"]) == 15
        dest.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        print(f"Exported AB_2scar: n={obj['n']}, 15X/15Z, d=(4,4)", flush=True)
        return dest
    raise ValueError(patch_name)


def build_rings_for_qubits(code: CorrectedPatchCode, qubits):
    d = code.json
    nx, nz = len(d["HX"]), len(d["HZ"])
    hz = [{j for j, v in enumerate(r) if v} for r in d["HZ"]]
    hx = [{j for j, v in enumerate(r) if v} for r in d["HX"]]

    r1_z_all, r1_x_all, r2_z_all = set(), set(), set()
    per_q = {}
    for q in qubits:
        r1_z = {i for i, s in enumerate(hz) if q in s}
        r1_x = {i for i, s in enumerate(hx) if q in s}
        r1_z_qs = set().union(*(hz[i] for i in r1_z))
        r2_z = {i for i, s in enumerate(hz) if i not in r1_z and (s & r1_z_qs)}
        r1_z_all |= r1_z
        r1_x_all |= r1_x
        r2_z_all |= r2_z
        per_q[str(q)] = dict(
            r1_z=[f"Z{i}" for i in sorted(r1_z)],
            r2_z=[f"Z{i}" for i in sorted(r2_z)],
            r1_x=[f"X{i}" for i in sorted(r1_x)],
        )

    def z_idx(zset):
        return [nx + i for i in sorted(zset)]

    def x_idx(xset):
        return sorted(xset)

    ring1_union = sorted(x_idx(r1_x_all) + z_idx(r1_z_all))
    ring2_union = sorted(x_idx(r1_x_all) + z_idx(r1_z_all | r2_z_all))
    subsets = {
        "thin": [],
        "ring1": ring1_union,
        "ring2_z": ring2_union,
    }
    info = dict(
        per_qubit=per_q,
        ring1_n_checks=len(ring1_union),
        ring2_z_n_checks=len(ring2_union),
        union_r1_z=[f"Z{i}" for i in sorted(r1_z_all)],
        union_r12_z=[f"Z{i}" for i in sorted(r1_z_all | r2_z_all)],
    )
    return subsets, info


class Indexed2(pd.PatchDecoder):
    """Exact 128-bit safe simultaneous two-erasure decoder (leaves nd_infer.py untouched)."""

    def __init__(self, code, site_a: int, site_b: int, w_dec=3, w_frame=3, onsets=(1, 2), p=1e-3):
        self.s = code
        self.site_a = site_a
        self.site_b = site_b
        self.sites = (site_a, site_b)
        self.onsets = tuple(onsets)
        self.w_dec = w_dec
        self.w_frame = w_frame
        self.odds = p / (1 - p)
        self.NST = self.s.NSTAB
        self.star = sorted(set(self.s.STAR[site_a]) | set(self.s.STAR[site_b]))
        self._prep2()

    def _prep2(self):
        self._pidx = {sec: self._prefix_idx(sec) for sec in ("X", "Z")}
        self._tab = {}
        self._frame_table = {}
        self._erasure2 = {}
        self._frame_col2 = {}
        self._mcache = {}
        self.index = {}
        self.rowcache = {}
        self._sig_lo = {}
        self._sig_hi = {}

        for sector in ("X", "Z"):
            t = self.s.build_tables(sector, self.w_dec)
            SIG, BND, LOG, W = t["SIG"], t["BND"], t["LOG"], t["W"]
            ODDS = self.odds ** W
            idx = self._pidx[sector]
            powers = 1 << np.arange(len(idx), dtype=np.int64)
            CODE = SIG[:, idx].astype(np.int64) @ powers
            ndet = SIG.shape[1]
            nst = BND.shape[1]
            assert ndet <= 128, f"ndet={ndet} exceeds 128-bit split"
            lo_n = min(64, ndet)
            self._sig_lo[sector] = (SIG[:, :lo_n].astype(np.uint64) << np.arange(lo_n, dtype=np.uint64)).sum(1)
            if ndet > 64:
                hi_n = ndet - 64
                self._sig_hi[sector] = (SIG[:, 64:].astype(np.uint64) << np.arange(hi_n, dtype=np.uint64)).sum(1)
            else:
                self._sig_hi[sector] = np.zeros(SIG.shape[0], dtype=np.uint64)
            BNDP = (BND.astype(np.uint64) << np.arange(nst, dtype=np.uint64)).sum(1)
            t.update(SIG=SIG, BND=BND, LOG=LOG, ODDS=ODDS, CODE=CODE, BNDP=BNDP)
            self._tab[sector] = t
            ftab = self._build_frame_table(sector)
            self._frame_table[sector] = ftab

            # Necessary-evidence index key: BNDP | live(rounds 3,4)
            key = BNDP.copy()
            for j, i in enumerate(i for i, (_, r) in enumerate(self.s.positions(sector)) if r in (3, 4)):
                key |= SIG[:, i].astype(np.uint64) << np.uint64(nst + j)
            order = np.argsort(key, kind="stable")
            self.index[sector] = (key[order], order)

            faulttag = "X" if sector == "X" else "Z"
            fcol0 = np.array([ftab.get(int(c), 0) for c in CODE], dtype=np.uint8)
            for onset in self.onsets:
                esA, elA, ebA = self.s.unit_sig(sector, (faulttag, self.site_a, onset))
                esB, elB, ebB = self.s.unit_sig(sector, (faulttag, self.site_b, onset))
                z_sig = np.zeros_like(esA)
                z_bnd = np.zeros_like(ebA)
                for eA in (0, 1):
                    for eB in (0, 1):
                        es = (esA if eA else z_sig) ^ (esB if eB else z_sig)
                        el = (int(elA) if eA else 0) ^ (int(elB) if eB else 0)
                        eb = (ebA if eA else z_bnd) ^ (ebB if eB else z_bnd)
                        self._erasure2[(sector, onset, eA, eB)] = (es, el, eb)
                        if eA == 0 and eB == 0:
                            self._frame_col2[(sector, onset, 0, 0)] = fcol0
                        else:
                            epref = self._code_of(sector, es)
                            shifted = CODE ^ epref
                            self._frame_col2[(sector, onset, eA, eB)] = np.array(
                                [ftab.get(int(c), 0) for c in shifted], dtype=np.uint8
                            )

    def _marginal_exact_rows(self, sector, rows, cond_dets, cond_bnd, frame, onset, split):
        t = self._tab[sector]
        SL = self._sig_lo[sector][rows] if rows is not None else self._sig_lo[sector]
        SH = self._sig_hi[sector][rows] if rows is not None else self._sig_hi[sector]
        BNDP = t["BNDP"][rows] if rows is not None else t["BNDP"]
        LOG = t["LOG"][rows] if rows is not None else t["LOG"]
        ODDS = t["ODDS"][rows] if rows is not None else t["ODDS"]
        pos = self.s.positions(sector)
        stabs = self.s.stabs(sector)
        didx = {dd: i for i, dd in enumerate(pos)}
        sidx = {k: i for i, k in enumerate(stabs)}

        dmask_lo = dval_lo = dmask_hi = dval_hi = np.uint64(0)
        cd_lo, cd_hi = [], []
        for dd, v in cond_dets:
            c = didx[dd]
            if c < 64:
                bit = np.uint64(1) << np.uint64(c)
                dmask_lo |= bit
                if v:
                    dval_lo |= bit
                cd_lo.append((c, bit))
            else:
                bit = np.uint64(1) << np.uint64(c - 64)
                dmask_hi |= bit
                if v:
                    dval_hi |= bit
                cd_hi.append((c, bit))
        bmask = bval = np.uint64(0)
        cb_list = []
        for k, v in cond_bnd:
            c = sidx[k]
            bit = np.uint64(1) << np.uint64(c)
            bmask |= bit
            if v:
                bval |= bit
            cb_list.append((c, bit))

        w0 = w1 = 0.0
        for eA in (0, 1):
            for eB in (0, 1):
                esig, elog, ebnd = self._erasure2[(sector, onset, eA, eB)]
                es_lo = es_hi = eb_pk = np.uint64(0)
                if eA or eB:
                    for c, bit in cd_lo:
                        if esig[c]:
                            es_lo |= bit
                    for c, bit in cd_hi:
                        if esig[c]:
                            es_hi |= bit
                    for c, bit in cb_list:
                        if ebnd[c]:
                            eb_pk |= bit
                tv_lo = dval_lo ^ es_lo
                tv_hi = dval_hi ^ es_hi
                bt = bval ^ eb_pk
                mask = (SL & dmask_lo) == tv_lo
                if dmask_hi:
                    mask &= (SH & dmask_hi) == tv_hi
                if bmask:
                    mask &= (BNDP & bmask) == bt
                if frame is not None:
                    fcol_full = self._frame_col2[(sector, onset, eA, eB)]
                    fcol = fcol_full[rows] if rows is not None else fcol_full
                    mask &= fcol == frame
                pr = ODDS[mask]
                lg = LOG[mask] ^ elog
                w0 += float(pr[lg == 0].sum()) * 0.25
                w1 += float(pr[lg == 1].sum()) * 0.25
        return (w0, w1) if split else (w0 + w1)

    def _marginal_fullscan(self, sector, cond_dets, cond_bnd, frame, onset, split):
        return self._marginal_exact_rows(sector, None, cond_dets, cond_bnd, frame, onset, split)

    def _marginal_compute(self, sector, cond_dets, cond_bnd, frame, onset, split):
        det = dict(cond_dets)
        bnd = dict(cond_bnd)
        stabs = self.s.stabs(sector)
        pos = self.s.positions(sector)
        if not bnd:
            bnd = {k: det[k, 0] ^ det[k, 1] ^ det[k, 2] for k in stabs}
        live = [d for d in pos if d[1] in (3, 4)]
        key = sum(int(bnd[k]) << j for j, k in enumerate(stabs)) | sum(
            int(det[d]) << (len(stabs) + j) for j, d in enumerate(live)
        )
        ep_keys = set()
        for eA in (0, 1):
            for eB in (0, 1):
                esig, _, ebnd = self._erasure2[(sector, onset, eA, eB)]
                ep = sum(int(ebnd[j]) << j for j in range(len(stabs))) | sum(
                    int(esig[pos.index(d)]) << (len(stabs) + j) for j, d in enumerate(live)
                )
                ep_keys.add(key ^ ep)
        ck = (sector, tuple(sorted(ep_keys)))
        if ck not in self.rowcache:
            keys, order = self.index[sector]
            chunks = [
                order[
                    np.searchsorted(keys, np.uint64(k), "left") : np.searchsorted(
                        keys, np.uint64(k), "right"
                    )
                ]
                for k in ck[1]
            ]
            self.rowcache[ck] = np.sort(np.concatenate(chunks))
        return self._marginal_exact_rows(sector, self.rowcache[ck], cond_dets, cond_bnd, frame, onset, split)


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


def run_single(patch_name: str, q: int):
    start = time.time()
    out_path = OUT_DIR / f"{patch_name}_single_q{q}.json"
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
                a: (D.direct(dz, dx, "thick") if a == "thick" else decide_subset(D, dz, dx, bz, bx, frames, subsets[a]))
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
                        rr = D.direct(dz, dx, "thick") if a == "thick" else decide_subset(D, dz, dx, bz, bx, frames, subsets[a])
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(checks["max_posterior_difference"], abs(rr["p0"] - dec[a]["p0"]))
                finally:
                    D._marginal_compute, D._mcache = method, cache
        if len(D._mcache) > 500000:
            D._mcache.clear()
        if cid % 20000 == 0:
            print(f"{patch_name}_q{q} cid={cid} n={n} sec={round(time.time()-start,1)}", flush=True)

    assert checks["direct_fullscan_mismatches"] == 0
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
        mode="single", patch=patch_name, qubit=q, n_qubits=code.NDATA,
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
        f"COMPLETE SINGLE {patch_name}_q{q} in {out['elapsed_seconds']}s | full={full:.6f} pp | "
        f"R1={out['ring1_pct_of_full']:.2f}% -> R2={out['ring2_z_pct_of_full']:.2f}% | "
        f"full_by_k={[round(x,6) for x in gain_by_k['thick']]}",
        flush=True,
    )


def run_pair(pair_name: str, max_configs: int = 0):
    start = time.time()
    cfg = PAIRS[pair_name]
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
                a: (D.direct(dz, dx, "thick") if a == "thick" else decide_subset(D, dz, dx, bz, bx, frames, subsets[a]))
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
                        rr = D.direct(dz, dx, "thick") if a == "thick" else decide_subset(D, dz, dx, bz, bx, frames, subsets[a])
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(checks["max_posterior_difference"], abs(rr["p0"] - dec[a]["p0"]))
                finally:
                    D._marginal_compute, D._mcache = method, cache
        if len(D._mcache) > 600000:
            D._mcache.clear()
        if cid % 15000 == 0:
            print(f"{pair_name} cid={cid} n={n} sec={round(time.time()-start,1)}", flush=True)

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
        mode="pair", pair=pair_name, patch=patch_name, regime=cfg["regime"],
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
        out_path = OUT_DIR / f"{pair_name}_result.json"
        out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"COMPLETE PAIR {pair_name} ({'SELFTEST' if max_configs else 'FULL'}) in {out['elapsed_seconds']}s | "
        f"hist={n} | full={full:.6f} pp | R1={out['ring1_pct_of_full']}% -> R2={out['ring2_z_pct_of_full']}% | "
        f"full_by_k={[round(x,6) for x in gain_by_k['thick']]} | checks={checks}",
        flush=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--pair", choices=list(PAIRS))
    ap.add_argument("--singles", choices=list(SINGLES))
    ap.add_argument("--single-q", type=int)
    args = ap.parse_args()
    if args.selftest:
        ensure_patch("Pen_d4_mid")
        ensure_patch("AB_2scar")
        run_pair("Pen_coll", max_configs=15)
    elif args.pair:
        run_pair(args.pair)
    elif args.singles:
        qs = [args.single_q] if args.single_q is not None else SINGLES[args.singles]
        for q in qs:
            run_single(args.singles, q)
