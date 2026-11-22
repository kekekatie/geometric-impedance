"""Standalone replay script for the 2x2 role-reversal witness-omission test.

Tests two fresh n=21, d=(3,3) cuts from the frozen disk-cut pool:
  1. AB_bal:      AB spec=(22, 2, 2, 10), corners=(2, 5, 11, 15), e14 (q9)
                  (AB_1 plus one extra tile filling in Z6's corner ear -> Mirror Middle Yards)
  2. Penrose_ear: Penrose spec=(7, 1, 3, 10), corners=(0, 4, 9, 13), e13 (q9)
                  (Hallway Z7 vs. protruding deg-2 Corner Ear Z6)

Reuses the untouched (3,3) decoder, CorrectedPatchCode address mapping,
necessary-evidence prefilter, shared-onset inference, XOR simulator, and
exhaustive k<=2 ordinary-fault ensemble (385,648 histories/site) from
exploratory/aperiodic_predict_2026-11-20/src/.

Usage:
    python3 exploratory/role_reversal_omission_2026-11-22/run_role_reversal.py
    python3 exploratory/role_reversal_omission_2026-11-22/run_role_reversal.py --site AB_bal
    python3 exploratory/role_reversal_omission_2026-11-22/run_role_reversal.py --site Penrose_ear
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
PRED_SRC = ROOT.parent / "aperiodic_predict_2026-11-20" / "src"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PRED_SRC))
import geom_select as gs  # noqa: E402
import paired_run as prior  # noqa: E402
import patch_decoder as pd  # noqa: E402
from nd_infer import Decoder as Original  # noqa: E402


TARGETS = {
    "AB_bal": dict(family="AB", spec=(22, 2, 2, 10), corners=(2, 5, 11, 15), edge=14),
    "Penrose_ear": dict(family="Penrose", spec=(7, 1, 3, 10), corners=(0, 4, 9, 13), edge=13),
}


def check_index(cid: str, nx: int, nz: int) -> int:
    assert cid[0] in ("X", "Z") and cid[1:].isdigit(), cid
    i = int(cid[1:])
    assert 0 <= i < (nx if cid[0] == "X" else nz), cid
    return i if cid[0] == "X" else nx + i


class CorrectedPatchCode(prior.FreshPatchCode):
    def __init__(self, path: Path):
        super().__init__(path)
        nx, nz = len(self.json["HX"]), len(self.json["HZ"])
        for e in self.json["eligible"]:
            self.STAR[e["qubit"]] = sorted(check_index(c, nx, nz) for c in e["checks"])
            actual = [i for i, s in enumerate(self.STABS) if e["qubit"] in s["support"]]
            assert self.STAR[e["qubit"]] == actual


class Indexed(pd.PatchDecoder):
    """Necessary-evidence prefilter; retains exact original marginal and row order."""

    def __init__(self, code, site):
        super().__init__(code, site, w_dec=3, w_frame=3)
        self.index = {}
        self.rowcache = {}
        for sec in ("X", "Z"):
            t = self._tab[sec]
            key = t["BNDP"].copy()
            n = len(self.s.stabs(sec))
            for j, i in enumerate(
                i for i, (_, r) in enumerate(self.s.positions(sec)) if r in (3, 4)
            ):
                key |= ((t["SIGP"] >> np.uint64(i)) & np.uint64(1)) << np.uint64(n + j)
            order = np.argsort(key, kind="stable")
            self.index[sec] = (key[order], order)

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
        esig, _, ebnd = self._erasure[sector, onset]
        ep = sum(int(ebnd[j]) << j for j in range(len(stabs))) | sum(
            int(esig[pos.index(d)]) << (len(stabs) + j) for j, d in enumerate(live)
        )
        ck = (sector, tuple(sorted({key, key ^ ep})))
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
        rows = self.rowcache[ck]
        tab = self._tab[sector]
        cols = {k: self._frame_col[k] for k in ((sector, 0), (sector, onset, 1))}
        try:
            self._tab[sector] = {
                **tab,
                **{k: tab[k][rows] for k in ("SIGP", "BNDP", "LOG", "ODDS")},
            }
            for k, v in cols.items():
                self._frame_col[k] = v[rows]
            return Original._marginal_compute(
                self, sector, cond_dets, cond_bnd, frame, onset, split
            )
        finally:
            self._tab[sector] = tab
            self._frame_col.update(cols)


def unpack(D, state):
    live = {tuple(map(int, k.split(","))): v for k, v in state["live"].items()}
    boundary = {int(k): v for k, v in state["boundary"].items()}
    archive = {tuple(x) for x in state["archive"]}
    return live, boundary, archive, state["frame"]


def query(D, stored, checks):
    live, boundary, archive, frames = stored
    rec = dict(live)
    for k in checks:
        for t in (1, 2):
            rec[k, t] = int((k, t) in archive)
    az = {d: v for d, v in rec.items() if d[0] in D.s.ZSTABS}
    ax = {d: v for d, v in rec.items() if d[0] in D.s.XSTABS}
    bz = {k: v for k, v in boundary.items() if k in D.s.ZSTABS}
    bx = {k: v for k, v in boundary.items() if k in D.s.XSTABS}
    return D.decide(az, ax, bz, bx, frames)


def direct_evidence(D, dz, dx, indices):
    selected = {(k, t) for k in range(D.NST) for t in (3, 4)} | {
        (k, t) for k in indices for t in (1, 2)
    }
    az = {d: v for d, v in dz.items() if d in selected}
    ax = {d: v for d, v in dx.items() if d in selected}
    bz = {k: dz[k, 0] ^ dz[k, 1] ^ dz[k, 2] for k in D.s.ZSTABS}
    bx = {k: dx[k, 0] ^ dx[k, 1] ^ dx[k, 2] for k in D.s.XSTABS}
    assert set(az) | set(ax) == selected
    return az, ax, bz, bx, D.observed_frames(dz, dx)


def same(a, b):
    return (
        a["label"] == b["label"]
        and a["tie"] == b["tie"]
        and abs(a["p0"] - b["p0"]) <= pd.EPS
        and abs(a["p1"] - b["p1"]) <= pd.EPS
    )


def export_target_patch(name: str) -> Path:
    dest = OUT_DIR / f"{name}.json"
    if dest.exists():
        return dest
    cfg = TARGETS[name]
    p = gs.pilot.parent(cfg["family"])
    for cand in gs.enumerate_cuts(p):
        if cand["spec"]["spec"] == cfg["spec"] and cand["spec"]["corners"] == cfg["corners"]:
            obj, w3, on, off = gs.analyse(p, cand)
            dest.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
            return dest
    raise RuntimeError(f"Target {name} not found in frozen pool!")


def run_site(name: str):
    start = time.time()
    cfg = TARGETS[name]
    patch_path = export_target_patch(name)
    code = CorrectedPatchCode(patch_path)
    d = code.json
    eid = cfg["edge"]
    e = next(x for x in d["eligible"] if x["edge"] == eid)
    edge = next(x for x in d["edges"] if x["id"] == eid)
    verts = {v["id"]: v for v in d["vertices"]}
    faces = {f["id"]: f for f in d["faces"]}
    geometric = [verts[v]["xcheck"] for v in edge["vertices"]] + [
        faces[f]["zcheck"] for f in edge["incident_faces"]
    ]
    assert set(geometric) == set(e["checks"]) and len(geometric) == 4
    nx, nz = len(d["HX"]), len(d["HZ"])
    idx = lambda c: check_index(c, nx, nz)
    assert sorted(map(idx, geometric)) == code.STAR[e["qubit"]]

    arms = []
    for c in sorted(geometric, key=idx):
        ci = idx(c)
        ret = sorted(i for i in code.STAR[e["qubit"]] if i != ci)
        arms.append(
            dict(
                omitted=c,
                index=ci,
                type=c[0],
                role="endpoint" if c[0] == "X" else "face",
                weight=len(code.STABS[ci]["support"]),
                retained_indices=ret,
            )
        )

    D = Indexed(code, e["qubit"])
    assert D.star == code.STAR[e["qubit"]]

    names = ["thin", "intact", "thick"] + [a["omitted"] for a in arms]
    credits = {a: [0.0, 0.0, 0.0] for a in names}
    ties = {a: [0, 0, 0] for a in names}
    counts = [0, 0, 0]
    movements = {
        a["omitted"]: {m: [0.0, 0.0, 0.0] for m in ("gained", "lost", "labels", "ties")}
        for a in arms
    }
    checks = dict(
        direct_fullscan_checks=0,
        direct_fullscan_mismatches=0,
        max_posterior_difference=0.0,
    )

    pool = prior.ordinary_pool(code)
    assert len(pool) == 310
    h = hashlib.sha256()
    n = 0

    for cid, k, extra in prior.config_stream(pool):
        h.update((json.dumps([cid, k, extra], separators=(",", ":")) + "\n").encode())
        for onset, vx, vz in prior.VARIANTS:
            loss = ([("X", e["qubit"], onset)] if vx else []) + (
                [("Z", e["qubit"], onset)] if vz else []
            )
            dz, dx, truth, _ = code.simulate(*prior.nd_run.compose(extra + tuple(loss)))
            state = D.serialize(dz, dx, "diamond")
            stored = unpack(D, state)
            dec = dict(
                thin=query(D, stored, []),
                intact=query(D, stored, D.star),
                thick=D.direct(dz, dx, "thick"),
            )
            for a in arms:
                dec[a["omitted"]] = query(D, stored, a["retained_indices"])
            c = {a: prior.cred(dec[a], truth) for a in names}
            for a in names:
                credits[a][k] += c[a]
                ties[a][k] += dec[a]["tie"]
            for arm in arms:
                a = arm["omitted"]
                delta = c[a] - c["intact"]
                movements[a]["gained"][k] += max(delta, 0.0)
                movements[a]["lost"][k] += max(-delta, 0.0)
                movements[a]["labels"][k] += int(dec[a]["label"] != dec["intact"]["label"])
                movements[a]["ties"][k] += int(dec[a]["tie"] != dec["intact"]["tie"])
            counts[k] += 1
            n += 1

            if n % 2003 == 0:
                method, cache = D._marginal_compute, D._mcache
                D._marginal_compute = Original._marginal_compute.__get__(D)
                D._mcache = {}
                try:
                    for a in names:
                        if a == "thick":
                            rr = D.direct(dz, dx, "thick")
                        else:
                            arm = next((x for x in arms if x["omitted"] == a), None)
                            indices = (
                                []
                                if a == "thin"
                                else D.star
                                if a == "intact"
                                else arm["retained_indices"]
                            )
                            rr = D.decide(*direct_evidence(D, dz, dx, indices))
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(
                            checks["max_posterior_difference"],
                            abs(rr["p0"] - dec[a]["p0"]),
                        )
                finally:
                    D._marginal_compute, D._mcache = method, cache

        if len(D._mcache) > 500000:
            D._mcache.clear()

    assert n == 385648 and counts == [8, 2480, 383160]
    assert checks["direct_fullscan_mismatches"] == 0

    weights = [prior.ODDS**k for k in range(3)]
    mass = sum(c * w for c, w in zip(counts, weights))
    mean = lambda arr: sum(c * w for c, w in zip(arr, weights)) / mass

    scores = {
        a: dict(truth_credit=mean(credits[a]), credits_by_weight=credits[a], ties_by_weight=ties[a])
        for a in names
    }
    full_gain = 100.0 * (scores["thick"]["truth_credit"] - scores["thin"]["truth_credit"])
    intact_gain = 100.0 * (scores["intact"]["truth_credit"] - scores["thin"]["truth_credit"])
    table = []
    for arm in arms:
        a = arm["omitted"]
        mm = movements[a]
        cost = 100.0 * (scores["intact"]["truth_credit"] - scores[a]["truth_credit"])
        gained, lost = 100.0 * mean(mm["gained"]), 100.0 * mean(mm["lost"])
        assert abs(cost - (lost - gained)) < 1e-11
        gain_over_thin = 100.0 * (scores[a]["truth_credit"] - scores["thin"]["truth_credit"])
        table.append(
            dict(
                **arm,
                cost_pp=cost,
                gain_over_thin_pp=gain_over_thin,
                surviving_pct_of_full=100.0 * gain_over_thin / full_gain if full_gain else None,
                full_archive_gain_pp=full_gain,
                intact_gain_pp=intact_gain,
                intact_pct_of_full=100.0 * intact_gain / full_gain if full_gain else None,
                truth_gained_pp=gained,
                truth_lost_pp=lost,
                label_changes=int(sum(mm["labels"])),
                tie_status_changes=int(sum(mm["ties"])),
            )
        )

    out = dict(
        name=name,
        config=cfg,
        qubit=e["qubit"],
        scored_logical_Z=d["logical_Z"],
        histories=n,
        config_stream_sha256=h.hexdigest(),
        full_archive_gain_pp=full_gain,
        intact_gain_pp=intact_gain,
        intact_pct_of_full=100.0 * intact_gain / full_gain if full_gain else None,
        omissions=table,
        validation=checks,
        elapsed_seconds=round(time.time() - start, 2),
    )
    out_path = OUT_DIR / f"{name}_omission.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"COMPLETE {name} in {out['elapsed_seconds']}s -> {out_path}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=list(TARGETS))
    args = ap.parse_args()
    for s in ([args.site] if args.site else list(TARGETS)):
        run_site(s)
