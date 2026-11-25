"""Phase 2 runner for experiment/dynamic-growth-scar-2026-11-25.

Reuses the exact untouched (3,3) decoder, CorrectedPatchCode address mapping,
Indexed necessary-evidence prefilter, shared-onset inference, XOR simulator, and
exhaustive k<=2 ordinary-fault ensemble from exploratory/aperiodic_predict_2026-11-20/src/.

Usage:
    python3 exploratory/dynamic_growth_scar_2026-11-25/run_growth.py --export-only
    python3 exploratory/dynamic_growth_scar_2026-11-25/run_growth.py --step A1
"""

import argparse
import collections as C
import hashlib
import itertools as I
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PRED_SRC = REPO / "exploratory" / "aperiodic_predict_2026-11-20" / "src"
AB1_PATH = REPO / "exploratory" / "aperiodic_predict_2026-11-20" / "results" / "AB_1.json"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PRED_SRC))
import geom_select as gs  # noqa: E402
import paired_run as prior  # noqa: E402
import patch_decoder as pd  # noqa: E402
from nd_infer import Decoder as Original  # noqa: E402


# Frozen step definitions matching PROTOCOL.md (commit c510bf5)
STEPS = {
    "A1":   dict(family="AB",      base="AB_1",        add_tiles=[762],      label="Half-swallow Ear (+762)"),
    "A2":   dict(family="AB",      base="AB_1",        add_tiles=[762, 764], label="Full-bury Ear (+762,+764)"),
    "A1-H": dict(family="AB",      base="AB_1",        add_tiles=[755],      label="Bury Hallway (+755)"),
    "B1":   dict(family="Penrose", base="Penrose_ear", add_tiles=[158],      label="Half-swallow Ear (+158)"),
    "B2":   dict(family="Penrose", base="Penrose_ear", add_tiles=[158, 156], label="Extend outer ring (+158,+156)"),
    "B1-H": dict(family="Penrose", base="Penrose_ear", add_tiles=[289],      label="Bury Hallway (+289)"),
}

BASE_SPEC = {
    "AB_1":        dict(family="AB",      spec=(22, 2, 2, 9),  corners=(4, 7, 13, 15), edge=14, hall_pface=757, ear_pface=760),
    "Penrose_ear": dict(family="Penrose", spec=(7, 1, 3, 10),  corners=(0, 4, 9, 13),  edge=13, hall_pface=221, ear_pface=220),
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
    """Exact necessary-evidence prefilter; retains original marginal and row order."""

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


def recover_base(base_name: str):
    bs = BASE_SPEC[base_name]
    p = gs.pilot.parent(bs["family"])
    for cand in gs.enumerate_cuts(p):
        if cand["spec"]["spec"] == bs["spec"] and cand["spec"]["corners"] == bs["corners"]:
            obj, _, _, _ = gs.analyse(p, cand)
            verts = {v["id"]: tuple(v["lift"]) for v in obj["vertices"]}
            ce = next(e for e in obj["edges"] if e["id"] == bs["edge"])
            tpe = tuple(sorted((verts[ce["vertices"][0]], verts[ce["vertices"][1]])))
            return p, tuple(sorted(cand["ids"])), tpe, bs["hall_pface"], bs["ear_pface"]
    raise RuntimeError(f"Base {base_name} not found!")


def best_valid_cut(p, disk_obj, target_phys_edge):
    L = len(disk_obj["cycle"])
    E = len(disk_obj["edges"])
    valid = []
    seen = set()
    for s in range(L):
        for shifts in I.product((-1, 0, 1), repeat=3):
            corners = (s,) + tuple(s + j * L // 4 + t for j, t in zip((1, 2, 3), shifts))
            if not all(a < b for a, b in zip(corners, corners[1:] + (s + L,))):
                continue
            roughkey = tuple(
                sorted((i % L) for a, b in ((s, corners[1]), (corners[2], corners[3])) for i in range(a, b))
            )
            if roughkey in seen:
                continue
            seen.add(roughkey)
            c = gs.pilot.cut(p, disk_obj, corners)
            if target_phys_edge not in c["eligible"]:
                continue
            x, z = gs.pilot.distances(disk_obj, c)
            if x is None or z is None or len(x) < 3 or len(z) < 3:
                continue
            dx, dz = len(x), len(z)
            n_qubits = E - len(roughkey)
            valid.append((abs(dx - 3) + abs(dz - 3), n_qubits, dx, dz, corners, c, x, z))
    valid.sort(key=lambda t: (t[0], t[1], t[4]))
    assert valid, "No valid d>=3 cut found!"
    return valid[0]


def export_step(step_name: str):
    dest = OUT_DIR / f"{step_name}.json"
    meta_dest = OUT_DIR / f"{step_name}_meta.json"
    if dest.exists() and meta_dest.exists():
        return dest, json.loads(meta_dest.read_text())

    cfg = STEPS[step_name]
    p, base_ids, tpe, hall_pf, ear_pf = recover_base(cfg["base"])
    new_ids = tuple(sorted(set(base_ids) | set(cfg["add_tiles"])))
    dsk = gs.pilot.disk(p, new_ids)
    assert dsk is not None, f"{step_name} does not form a valid disk!"
    _, n_q, dx, dz, corners, c, x, z = best_valid_cut(p, dsk, tpe)
    specd = dict(centre=None, aspect=None, angle=None, spec=(step_name, len(new_ids)), corners=corners)
    obj = gs.pilot.export(p, (None, dsk, c, specd, x, z), {})

    verts = {v["id"]: tuple(v["lift"]) for v in obj["vertices"]}
    face_map = {tuple(sorted(vs)): idx for idx, vs in enumerate(p["faces"])}
    te = next(
        e for e in obj["edges"]
        if tuple(sorted((verts[e["vertices"][0]], verts[e["vertices"][1]]))) == tpe
    )
    hall_z = ear_z = None
    for fid in te["incident_faces"]:
        fobj = next(f for f in obj["faces"] if f["id"] == fid)
        pf = face_map[tuple(sorted(verts[v] for v in fobj["vertices"]))]
        if pf == hall_pf:
            hall_z = fobj["zcheck"]
        elif pf == ear_pf:
            ear_z = fobj["zcheck"]
    assert hall_z is not None and ear_z is not None

    w3 = gs.weight3_xlogicals(obj["HX"], obj["HZ"], obj["n"]) if dx == 3 else []
    n_w3_on = sum(1 for s in w3 if te["qubit"] in s)

    meta = dict(
        step=step_name, label=cfg["label"], family=cfg["family"], base=cfg["base"],
        add_tiles=cfg["add_tiles"], n_tiles=len(new_ids), n_qubits=n_q,
        nx=len(obj["HX"]), nz=len(obj["HZ"]), d=[dx, dz], corners=list(corners),
        edge=te["id"], qubit=te["qubit"], n_w3_on=n_w3_on,
        hallway_zcheck=hall_z, ear_zcheck=ear_z, scored_logical_Z=obj["logical_Z"],
    )
    dest.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    meta_dest.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {step_name}: n={n_q}, {meta['nx']}X/{meta['nz']}Z, d={meta['d']}, n_w3_on={n_w3_on}, hall={hall_z}, ear={ear_z}", flush=True)
    return dest, meta


def run_step(step_name: str):
    start = time.time()
    patch_path, meta = export_step(step_name)
    code = CorrectedPatchCode(patch_path)
    d = code.json
    eid = meta["edge"]
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
        phys_role = (
            "endpoint" if c[0] == "X"
            else "hallway" if c == meta["hallway_zcheck"]
            else "ear"
        )
        arms.append(
            dict(
                omitted=c, index=ci, type=c[0],
                role="endpoint" if c[0] == "X" else "face",
                physical_role=phys_role,
                weight=len(code.STABS[ci]["support"]),
                retained_indices=ret,
            )
        )

    D = Indexed(code, e["qubit"])
    assert D.star == code.STAR[e["qubit"]]
    endpoint_indices = [a["index"] for a in arms if a["role"] == "endpoint"]
    names = ["thin", "intact", "thick", "neither_face"] + [a["omitted"] for a in arms]
    credits = {a: [0.0, 0.0, 0.0] for a in names}
    ties = {a: [0, 0, 0] for a in names}
    counts = [0, 0, 0]
    movements = {
        a["omitted"]: {m: [0.0, 0.0, 0.0] for m in ("gained", "lost", "labels", "ties")}
        for a in arms
    }
    checks = dict(direct_fullscan_checks=0, direct_fullscan_mismatches=0, max_posterior_difference=0.0)

    pool = prior.ordinary_pool(code)
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
                neither_face=query(D, stored, endpoint_indices),
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
                        elif a == "neither_face":
                            rr = D.decide(*direct_evidence(D, dz, dx, endpoint_indices))
                        else:
                            arm = next((x for x in arms if x["omitted"] == a), None)
                            indices = [] if a == "thin" else D.star if a == "intact" else arm["retained_indices"]
                            rr = D.decide(*direct_evidence(D, dz, dx, indices))
                        checks["direct_fullscan_checks"] += 1
                        checks["direct_fullscan_mismatches"] += not same(rr, dec[a])
                        checks["max_posterior_difference"] = max(
                            checks["max_posterior_difference"], abs(rr["p0"] - dec[a]["p0"])
                        )
                finally:
                    D._marginal_compute, D._mcache = method, cache

        if len(D._mcache) > 500000:
            D._mcache.clear()
        if cid % 10000 == 0:
            print(step_name, "cid=", cid, "n=", n, "sec=", round(time.time() - start, 1), flush=True)

    assert checks["direct_fullscan_mismatches"] == 0
    weights = [prior.ODDS**k for k in range(3)]
    mass = sum(c * w for c, w in zip(counts, weights))
    mean = lambda arr: sum(c * w for c, w in zip(arr, weights)) / mass

    scores = {a: mean(credits[a]) for a in names}
    full_gain = 100.0 * (scores["thick"] - scores["thin"])
    intact_gain = 100.0 * (scores["intact"] - scores["thin"])
    neither_gain = 100.0 * (scores["neither_face"] - scores["thin"])

    table = []
    for arm in arms:
        a = arm["omitted"]
        mm = movements[a]
        cost = 100.0 * (scores["intact"] - scores[a])
        gain_over_thin = 100.0 * (scores[a] - scores["thin"])
        table.append(
            dict(
                **arm,
                cost_pp=cost,
                gain_over_thin_pp=gain_over_thin,
                surviving_pct_of_full=100.0 * gain_over_thin / full_gain if abs(full_gain) > 1e-12 else None,
                truth_gained_pp=100.0 * mean(mm["gained"]),
                truth_lost_pp=100.0 * mean(mm["lost"]),
                label_changes=int(sum(mm["labels"])),
                tie_status_changes=int(sum(mm["ties"])),
            )
        )

    hall_row = next(r for r in table if r["physical_role"] == "hallway")
    ear_row = next(r for r in table if r["physical_role"] == "ear")
    # Keeping Hallway only = omitting Ear; keeping Ear only = omitting Hallway
    g_hall_only = ear_row["gain_over_thin_pp"]
    g_ear_only = hall_row["gain_over_thin_pp"]
    I_pp = (g_hall_only - neither_gain) - (intact_gain - g_ear_only)

    out = dict(
        step=step_name, meta=meta, pool_size=len(pool), histories=n,
        histories_by_weight=counts, config_stream_sha256=h.hexdigest(),
        full_archive_gain_pp=full_gain, intact_gain_pp=intact_gain,
        intact_pct_of_full=100.0 * intact_gain / full_gain if abs(full_gain) > 1e-12 else None,
        neither_face_gain_pp=neither_gain,
        neither_face_pct_of_full=100.0 * neither_gain / full_gain if abs(full_gain) > 1e-12 else None,
        interaction_I_pp=I_pp,
        interaction_I_pct_of_full=100.0 * I_pp / full_gain if abs(full_gain) > 1e-12 else None,
        omissions=table, validation=checks, elapsed_seconds=round(time.time() - start, 2),
    )
    out_path = OUT_DIR / f"{step_name}_result.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"COMPLETE {step_name} in {out['elapsed_seconds']}s | n={meta['n_qubits']} | hist={n} | "
        f"full={full_gain:.6f} pp | intact={out['intact_pct_of_full']:.2f}% | "
        f"neither={out['neither_face_pct_of_full']:.4f}% | I={I_pp:+.6f} pp ({out['interaction_I_pct_of_full']:.1f}%)",
        flush=True,
    )
    for r in table:
        print(
            f"  omit {r['omitted']} ({r['physical_role']}/w{r['weight']}): "
            f"cost={r['cost_pp']:+.6f} pp | surviving={r['surviving_pct_of_full']:.2f}% | flips={r['label_changes']}",
            flush=True,
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-only", action="store_true")
    ap.add_argument("--step", choices=list(STEPS))
    args = ap.parse_args()
    if args.export_only:
        for s in STEPS:
            export_step(s)
    elif args.step:
        run_step(args.step)
    else:
        for s in STEPS:
            run_step(s)
