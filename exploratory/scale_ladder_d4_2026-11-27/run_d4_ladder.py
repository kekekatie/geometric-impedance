"""Standalone runner for experiment/scale-ladder-d4-2026-11-27 (frozen protocol 5665179).

Exports and scores the four 13-tile d=(4,4) Bulk-vs.-Boundary cuts:
  - AB_d4_mid  (n=26): Bulk(0,4) vs. Middle Yard(1,3)
  - AB_d4_ear  (n=28): Bulk(0,4) vs. Corner Ear(2,2)
  - Pen_d4_mid (n=26): Bulk(0,4) vs. Middle Yard(1,3)
  - Pen_d4_ear (n=26): Bulk(0,4) vs. Corner Ear(2,2)

Reuses the exact untouched (3,3) decoder, CorrectedPatchCode, Indexed prefilter,
shared-onset inference, XOR simulator, and exhaustive k<=2 ordinary-fault ensemble.
"""

import argparse
import collections as C
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PRED_SRC = REPO / "exploratory" / "aperiodic_predict_2026-11-20" / "src"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PRED_SRC))
import geom_select as gs  # noqa: E402
import paired_run as prior  # noqa: E402
import patch_decoder as pd  # noqa: E402
from nd_infer import Decoder as Original  # noqa: E402


SITES = {
    "AB_d4_mid":  dict(family="AB",      ci=2, aspect=1.25, m=13, corners=(4, 8, 12, 16),  target_bndS=(0, 1)),
    "AB_d4_ear":  dict(family="AB",      ci=4, aspect=1.25, m=13, corners=(16, 20, 26, 29), target_bndS=(0, 2)),
    "Pen_d4_mid": dict(family="Penrose", ci=3, aspect=1.25, m=13, corners=(6, 10, 14, 18), target_bndS=(0, 1)),
    "Pen_d4_ear": dict(family="Penrose", ci=4, aspect=1.25, m=13, corners=(4, 9, 14, 19),  target_bndS=(0, 2)),
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
    """128-bit safe (SIGP_LO/SIGP_HI) necessary-evidence prefilter for >12 checks/sector.
    Leaves nd_infer.py completely untouched while avoiding uint64 overflow at ndet > 64.
    """

    def __init__(self, code, site):
        super().__init__(code, site, w_dec=3, w_frame=3)
        self.index = {}
        self.rowcache = {}
        self._sig_lo = {}
        self._sig_hi = {}
        for sec in ("X", "Z"):
            t = self._tab[sec]
            SIG = t["SIG"]
            ndet = SIG.shape[1]
            assert ndet <= 128, f"ndet={ndet} exceeds 128-bit split"
            lo_n = min(64, ndet)
            self._sig_lo[sec] = (SIG[:, :lo_n].astype(np.uint64) << np.arange(lo_n, dtype=np.uint64)).sum(1)
            if ndet > 64:
                hi_n = ndet - 64
                self._sig_hi[sec] = (SIG[:, 64:].astype(np.uint64) << np.arange(hi_n, dtype=np.uint64)).sum(1)
            else:
                self._sig_hi[sec] = np.zeros(SIG.shape[0], dtype=np.uint64)
            key = t["BNDP"].copy()
            n = len(self.s.stabs(sec))
            for j, i in enumerate(
                i for i, (_, r) in enumerate(self.s.positions(sec)) if r in (3, 4)
            ):
                key |= SIG[:, i].astype(np.uint64) << np.uint64(n + j)
            order = np.argsort(key, kind="stable")
            self.index[sec] = (key[order], order)

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
        esig, elog, ebnd = self._erasure[(sector, onset)]
        dmask_lo = dval_lo = dmask_hi = dval_hi = np.uint64(0)
        espack_lo = espack_hi = np.uint64(0)
        for dd, v in cond_dets:
            c = didx[dd]
            if c < 64:
                bit = np.uint64(1) << np.uint64(c)
                dmask_lo |= bit
                if v:
                    dval_lo |= bit
                if esig[c]:
                    espack_lo |= bit
            else:
                bit = np.uint64(1) << np.uint64(c - 64)
                dmask_hi |= bit
                if v:
                    dval_hi |= bit
                if esig[c]:
                    espack_hi |= bit
        bmask = bval = ebpack = np.uint64(0)
        for k, v in cond_bnd:
            c = sidx[k]
            bit = np.uint64(1) << np.uint64(c)
            bmask |= bit
            if v:
                bval |= bit
            if ebnd[c]:
                ebpack |= bit
        w0 = w1 = 0.0
        for e in (0, 1):
            tv_lo = dval_lo ^ (espack_lo if e else np.uint64(0))
            tv_hi = dval_hi ^ (espack_hi if e else np.uint64(0))
            bt = bval ^ (ebpack if e else np.uint64(0))
            mask = (SL & dmask_lo) == tv_lo
            if dmask_hi:
                mask &= (SH & dmask_hi) == tv_hi
            if bmask:
                mask &= (BNDP & bmask) == bt
            if frame is not None:
                fcol_full = self._frame_col[(sector, onset, 1)] if e else self._frame_col[(sector, 0)]
                fcol = fcol_full[rows] if rows is not None else fcol_full
                mask &= fcol == frame
            pr = ODDS[mask]
            lg = LOG[mask] ^ (int(elog) if e else 0)
            w0 += float(pr[lg == 0].sum()) * 0.5
            w1 += float(pr[lg == 1].sum()) * 0.5
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
        return self._marginal_exact_rows(sector, self.rowcache[ck], cond_dets, cond_bnd, frame, onset, split)


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


def dual_bfs_dists(d, c, start_node):
    da = C.defaultdict(list)
    sm = {e: -(j + 1) for j, arc in enumerate((c["arcs"][1], c["arcs"][3])) for e in arc}
    for e in c["data"]:
        fs = d["edges"][e]
        a, b = fs if len(fs) == 2 else (fs[0], sm[e])
        da[a].append((b, e))
        da[b].append((a, e))
    dist = {start_node: 0}
    q = C.deque([start_node])
    while q:
        u = q.popleft()
        for v, _ in da[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def export_site(name: str):
    dest = OUT_DIR / f"{name}.json"
    meta_dest = OUT_DIR / f"{name}_meta.json"
    if dest.exists() and meta_dest.exists():
        return dest, json.loads(meta_dest.read_text())

    cfg = SITES[name]
    p = gs.pilot.parent(cfg["family"], large=True)
    facec = {i: np.mean([p["pos"][v] for v in vs], axis=0) for i, vs in enumerate(p["faces"])}
    centres = sorted(
        (v for v in p["pos"] if sum(t * t for t in p["pos"][v]) <= 9),
        key=lambda v: (round(sum(t * t for t in p["pos"][v]), 10), v),
    )[:8]
    v = centres[cfg["ci"]]
    aspect = cfg["aspect"]
    order = sorted(
        facec,
        key=lambda f: (
            round(((facec[f][0] - p["pos"][v][0]) / aspect) ** 2 + ((facec[f][1] - p["pos"][v][1]) * aspect) ** 2, 10),
            tuple(sorted(p["faces"][f])),
        ),
    )
    ids = tuple(sorted(order[: cfg["m"]]))
    dsk = gs.pilot.disk(p, ids)
    assert dsk is not None
    c = gs.pilot.cut(p, dsk, cfg["corners"])
    x, z = gs.pilot.distances(dsk, c)
    assert len(x) == 4 and len(z) == 4

    specd = dict(centre=v, aspect=aspect, angle=0.0, spec=(name, cfg["m"]), corners=cfg["corners"])
    obj = gs.pilot.export(p, (None, dsk, c, specd, x, z), {})

    # Identify the target on-route eligible edge matching target_bndS
    d1 = dual_bfs_dists(dsk, c, -1)
    d2 = dual_bfs_dists(dsk, c, -2)
    smooth_set = set(c["arcs"][1]) | set(c["arcs"][3])
    verts_lift = {vt["id"]: tuple(vt["lift"]) for vt in obj["vertices"]}
    edge_by_lift = {
        tuple(sorted((verts_lift[e["vertices"][0]], verts_lift[e["vertices"][1]]))): e
        for e in obj["edges"]
    }
    chosen = None
    zset = set(z)
    for e_phys in c["eligible"]:
        f1, f2 = dsk["edges"][e_phys]
        cands = []
        if f1 in d1 and f2 in d2:
            cands.append(d1[f1] + 1 + d2[f2])
        if f2 in d1 and f1 in d2:
            cands.append(d1[f2] + 1 + d2[f1])
        if not cands or min(cands) != 4:
            continue
        bs_pair = []
        for fid in (f1, f2):
            vs = p["faces"][fid]
            fedges = [gs.pilot.edge(a, b) for a, b in zip(vs, vs[1:] + vs[:1])]
            bs_pair.append(sum(1 for ed in fedges if ed in smooth_set))
        if tuple(sorted(bs_pair)) == cfg["target_bndS"]:
            lz_hit = e_phys in zset
            if chosen is None or (lz_hit and not chosen[0]):
                chosen = (lz_hit, e_phys, f1, f2, bs_pair)
    assert chosen is not None, f"Target edge not found for {name}"
    lz_hit, e_phys, f1, f2, bs_pair = chosen
    te = edge_by_lift[e_phys]

    # Map bulk vs boundary Z-check names in exported obj
    ebnd = {eid: arc["label"] for arc in obj["arcs"] for eid in arc["edges"]}
    fedges_obj = C.defaultdict(list)
    for e in obj["edges"]:
        for fid in e["incident_faces"]:
            fedges_obj[fid].append(e)
    bulk_z = bnd_z = None
    for fid in te["incident_faces"]:
        bs = sum(1 for e in fedges_obj[fid] if len(e["incident_faces"]) == 1 and ebnd.get(e["id"]) == "smooth")
        fobj = next(f for f in obj["faces"] if f["id"] == fid)
        if bs == 0:
            bulk_z = fobj["zcheck"]
        else:
            bnd_z = fobj["zcheck"]
    assert bulk_z is not None and bnd_z is not None

    meta = dict(
        site=name, family=cfg["family"], n_tiles=cfg["m"], n_qubits=obj["n"],
        nx=len(obj["HX"]), nz=len(obj["HZ"]), d=[4, 4], corners=list(cfg["corners"]),
        edge=te["id"], qubit=te["qubit"], lz_hit=lz_hit,
        target_bndS=list(cfg["target_bndS"]),
        bulk_zcheck=bulk_z, boundary_zcheck=bnd_z,
        scored_logical_Z=obj["logical_Z"],
    )
    dest.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    meta_dest.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {name}: n={obj['n']}, {meta['nx']}X/{meta['nz']}Z, d=(4,4), e{te['id']}(q{te['qubit']}), lz_hit={lz_hit}, bulk={bulk_z}, bnd={bnd_z}", flush=True)
    return dest, meta


def run_site(name: str):
    start = time.time()
    patch_path, meta = export_site(name)
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
            else "bulk" if c == meta["bulk_zcheck"]
            else "boundary"
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
    bulk_name = meta["bulk_zcheck"]
    bnd_name = meta["boundary_zcheck"]
    names = ["thin", "intact", "thick", "neither_face"] + [a["omitted"] for a in arms]
    credits = {a: [0.0, 0.0, 0.0] for a in names}
    ties = {a: [0, 0, 0] for a in names}
    counts = [0, 0, 0]
    sum_dI_by_k = [0.0, 0.0, 0.0]
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
            # Exact per-history I = (c_bulk_only + c_bnd_only) - (c_intact + c_neither)
            # bulk_only = omitting bnd_name; bnd_only = omitting bulk_name
            sum_dI_by_k[k] += (c[bnd_name] + c[bulk_name]) - (c["intact"] + c["neither_face"])
            for arm in arms:
                a = arm["omitted"]
                delta = c[a] - c["intact"]
                movements[a]["gained"][k] += max(delta, 0.0)
                movements[a]["lost"][k] += max(-delta, 0.0)
                movements[a]["labels"][k] += int(dec[a]["label"] != dec["intact"]["label"])
                movements[a]["ties"][k] += int(dec[a]["tie"] != dec["intact"]["tie"])
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
        if cid % 15000 == 0:
            print(name, "cid=", cid, "n=", n, "sec=", round(time.time() - start, 1), flush=True)

    assert checks["direct_fullscan_mismatches"] == 0
    weights = [prior.ODDS**k for k in range(3)]
    mass = sum(c * w for c, w in zip(counts, weights))
    mean = lambda arr: sum(c * w for c, w in zip(arr, weights)) / mass

    scores = {a: mean(credits[a]) for a in names}
    full_gain = 100.0 * (scores["thick"] - scores["thin"])
    intact_gain = 100.0 * (scores["intact"] - scores["thin"])
    neither_gain = 100.0 * (scores["neither_face"] - scores["thin"])
    I_by_k_pp = [100.0 * sum_dI_by_k[k] * weights[k] / mass for k in range(3)]
    I_pp = sum(I_by_k_pp)

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

    out = dict(
        site=name, meta=meta, pool_size=len(pool), histories=n,
        histories_by_weight=counts, config_stream_sha256=h.hexdigest(),
        full_archive_gain_pp=full_gain, intact_gain_pp=intact_gain,
        intact_pct_of_full=100.0 * intact_gain / full_gain if abs(full_gain) > 1e-12 else None,
        neither_face_gain_pp=neither_gain,
        neither_face_pct_of_full=100.0 * neither_gain / full_gain if abs(full_gain) > 1e-12 else None,
        interaction_I_pp=I_pp,
        interaction_I_pct_of_full=100.0 * I_pp / full_gain if abs(full_gain) > 1e-12 else None,
        I_by_k_pp=I_by_k_pp,
        omissions=table, validation=checks, elapsed_seconds=round(time.time() - start, 2),
    )
    out_path = OUT_DIR / f"{name}_result.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"COMPLETE {name} in {out['elapsed_seconds']}s | n={meta['n_qubits']} | hist={n} | "
        f"full={full_gain:.6f} pp | intact={out['intact_pct_of_full']:.2f}% | "
        f"neither={out['neither_face_pct_of_full']:.4f}% | I={I_pp:+.6f} pp ({out['interaction_I_pct_of_full']:.1f}%) | "
        f"I_by_k={[round(x,6) for x in I_by_k_pp]}",
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
    ap.add_argument("--site", choices=list(SITES))
    args = ap.parse_args()
    if args.export_only:
        for s in SITES:
            export_site(s)
    elif args.site:
        run_site(args.site)
    else:
        for s in SITES:
            run_site(s)
