#!/usr/bin/env python3
"""
front_activation.py -- more of the zip, or a faster zip? (PREREGISTRATION.md, frozen before this file.)
24 fresh ordinary worlds grown with the patient scheduler. At every live, unequal two-way choice, both options are grown
in lockstep until both first bursts have ended plus 20 slices (cap 100). Every slice records the active boundary (frontier
length that received a tile), tiles placed, total frontier length, and the median distance of new tiles from the base
patch. Distinct situations (whole base patch identical relative to the choice point) are grown once.
`python3 front_activation.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, hashlib, collections
from multiprocessing import Pool
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "speed_of_now"))
import speed_of_now as SN
Sl, L, D, S = SN.Sl, SN.L, SN.D, SN.S
SEED0, N_ADD, N_WORLDS, CAP, RELAX, EQ_TOL, MIN_M = 20261170, 1500, 24, 100, 20, 0.01, 3
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[120:120 + N_WORLDS]


def whole_key(tiles, z):
    rk = lambda w: (round((w - z).real / S, 3), round((w - z).imag / S, 3))
    return hashlib.md5(repr(sorted((t[0], rk(t[1]), rk(t[2]), rk(t[3])) for t in tiles)).encode()).hexdigest()[:16]


def edge_len(ek):
    a, b = list(ek)
    return abs(complex(*a) - complex(*b)) / S


def world(k):
    """grow the main world; return the live, unequal two-way choices with their base patches."""
    rng = random.Random(SEED0 + k)
    P = L.Patch(L.seed_patch(centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    rank = Sl.rank_of(P.tris); out = []; status = "ok"; n_two = 0; skipped = collections.Counter()
    while len(P.tris) - n0 < N_ADD:
        r += 1
        fr = P.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam:
            status = "JAM"; break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3]))
        if len(cs) == 2:
            n_two += 1
            base = list(P.tris); cm0 = Sl.constraints(base, rank); aF = Sl.area(Sl.region(cm0))
            if aF > 0:
                # piece kept by each option, measured after its first forced slice (F settles there, cf. golden_digits G4)
                pcs = []
                for c in cs:
                    Q = L.Patch(list(base)); Q.add(c); st, n, kind = SN.patient(Q, random.Random(0))
                    tiles = list(Q.tris) if kind == "forced" else base + [c]      # never let a guess shrink the piece
                    pcs.append(Sl.area(Sl.region(Sl.constraints(tiles, rank))) / aF)
                if min(pcs) <= 0:
                    skipped["dead"] += 1
                elif abs(pcs[0] - pcs[1]) < EQ_TOL:
                    skipped["equal"] += 1
                else:
                    z = (fr[0][0] + fr[0][1]) / 2
                    out.append(dict(world=k, slice=r, base=base, cs=cs, pieces=pcs, aF=aF, rank=rank, key=whole_key(base, z)))
            else:
                skipped["F_zero"] += 1
        P.add(rng.choice(cs))
    return dict(world=k, status=status, n_two=n_two, skipped=dict(skipped), choices=out)


def pair(job):
    """grow both options in lockstep. Per sibling and slice: placed, active length, front length, kind, median distance."""
    key, base, cs, rank = job
    stream = SEED0 * 1000 + int(key, 16) % (2 ** 31)
    tree = cKDTree([[cen(t).real / S, cen(t).imag / S] for t in base])
    dist = lambda ts: float(np.median(tree.query([[cen(t).real / S, cen(t).imag / S] for t in ts])[0])) if ts else None
    sib = []
    for c in cs:
        Q = L.Patch(list(base)); Q.add(c)
        sib.append(dict(Q=Q, rng=random.Random(stream), rows=[dict(placed=1, active=None, front=None, kind="choice", med=dist([c]))],
                        burst_end=None, status="ok"))
    end = None
    for s in range(1, CAP + 1):
        for x in sib:
            if x["status"] == "JAM":
                continue
            Q = x["Q"]; n_before = len(Q.tris)
            fr_keys = [ek for ek, ts in Q.edges.items() if len(ts) == 1]
            st, n, kind = SN.patient(Q, x["rng"])
            if st == "JAM":
                x["status"] = "JAM"; x["rows"].append(dict(placed=0, active=0.0, front=sum(map(edge_len, fr_keys)), kind="jam", med=None)); continue
            act = sum(edge_len(ek) for ek in fr_keys if len(Q.edges[ek]) == 2)
            x["rows"].append(dict(placed=n, active=act, front=sum(map(edge_len, fr_keys)), kind=kind, med=dist(Q.tris[n_before:])))
            if kind == "guess" and x["burst_end"] is None:
                x["burst_end"] = s - 1
        if end is None and all(x["burst_end"] is not None or x["status"] == "JAM" for x in sib):
            end = max((x["burst_end"] if x["burst_end"] is not None else len(x["rows"]) - 1) for x in sib)
        if end is not None and s >= end + RELAX:
            break
    res = []
    for x in sib:
        Q = x["Q"]
        if x["burst_end"] is not None:
            n_burst = len(base) + sum(r["placed"] for r in x["rows"][:x["burst_end"] + 1])
            tiles_at_burst = Q.tris[:n_burst]
        else:
            tiles_at_burst = list(Q.tris)
        res.append(dict(rows=x["rows"], burst_end=x["burst_end"], status=x["status"],
                        burst=sum(r["placed"] for r in x["rows"][:(x["burst_end"] if x["burst_end"] is not None else len(x["rows"]) - 1) + 1]),
                        piece_at_burst=Sl.area(Sl.region(Sl.constraints(tiles_at_burst, rank)))))
    return dict(key=key, sibs=res, relax_end=end)


def ratio_ok(a, b):
    return b is not None and a is not None and b > 0 and a > 0 and 0.8 <= a / b <= 1.25


def analyse(W, R):
    by_key = {r["key"]: r for r in R}
    first = {}
    for w in W:
        for c in w["choices"]:
            first.setdefault(c["key"], c)
    lines = [f"worlds: statuses {dict(collections.Counter(w['status'] for w in W))}; two-way choices {sum(w['n_two'] for w in W)}; "
             f"skipped {dict(sum((collections.Counter(w['skipped']) for w in W), collections.Counter()))}; live unequal "
             f"{sum(len(w['choices']) for w in W)}; distinct situations {len(first)}"]
    P = []
    for key, c in first.items():
        r = by_key[key]
        i_sm = 0 if c["pieces"][0] < c["pieces"][1] else 1
        sm, lg = r["sibs"][i_sm], r["sibs"][1 - i_sm]
        P.append(dict(key=key, c=c, sm=sm, lg=lg, piece_sm=c["pieces"][i_sm], relax_end=r["relax_end"]))
    blen = lambda x: x["burst_end"] if x["burst_end"] is not None else len(x["rows"]) - 1
    M = [p for p in P if min(blen(p["sm"]), blen(p["lg"])) >= MIN_M]
    a1 = a2 = a3 = 0; rows = []
    for p in M:
        m = min(blen(p["sm"]), blen(p["lg"]))
        f = {}
        for nm in ("sm", "lg"):
            rr = p[nm]["rows"][1:m + 1]
            f[nm] = dict(active=np.mean([x["active"] for x in rr]),
                         dens=np.mean([x["placed"] / x["active"] for x in rr if x["active"] and x["active"] > 0]),
                         adv=(p[nm]["rows"][m]["med"] - p[nm]["rows"][0]["med"]) / m if p[nm]["rows"][m]["med"] is not None else None,
                         share=np.mean([x["active"] / x["front"] for x in rr if x["front"]]))
        a1 += f["sm"]["active"] > f["lg"]["active"]; a2 += ratio_ok(f["sm"]["dens"], f["lg"]["dens"]); a3 += ratio_ok(f["sm"]["adv"], f["lg"]["adv"])
        rows.append((p, m, f))
    n = len(M)
    lines.append(f"  pairs with >= {MIN_M} matched slices: {n} of {len(P)}")
    lines.append(f"  A1: {'HELD  ' if n and a1 >= 0.7 * n else 'FAILED'}  smaller piece has the larger mean active boundary in {a1}/{n} (need >= 70%)")
    lines.append(f"  A2: {'HELD  ' if n and a2 >= 0.7 * n else 'FAILED'}  activity per active length ratio within 0.8-1.25 in {a2}/{n} (need >= 70%)")
    lines.append(f"  A3: {'HELD  ' if n and a3 >= 0.6 * n else 'FAILED'}  outward advance ratio within 0.8-1.25 in {a3}/{n} (need >= 60%)")
    full = [p for p in P if p["relax_end"] is not None and p["relax_end"] + RELAX <= CAP
            and all(len(p[nm]["rows"]) - 1 >= p["relax_end"] + RELAX for nm in ("sm", "lg"))]
    a4 = 0; rel = []
    for p in full:
        e = p["relax_end"]; sh = {}
        for nm in ("sm", "lg"):
            rr = p[nm]["rows"][e + 1:e + RELAX + 1]
            sh[nm] = np.mean([x["active"] / x["front"] for x in rr if x["front"]])
        a4 += ratio_ok(sh["sm"], sh["lg"]); rel.append(sh["sm"] / sh["lg"] if sh["lg"] > 0 else float("nan"))
    lines.append(f"  A4: {'HELD  ' if full and a4 >= 0.6 * len(full) else 'FAILED'}  relaxation active-share ratio within 0.8-1.25 in {a4}/{len(full)} "
                 f"(need >= 60%); pairs not reaching a full window: {len(P) - len(full)} "
                 f"(jams {sum(any(p[nm]['status'] == 'JAM' for nm in ('sm', 'lg')) for p in P)}); ratios {sorted(round(x, 2) for x in rel)}")
    lines.append("  reported per pair (piece kept by smaller; matched slices m; active sm/lg; density sm/lg; outward advance sm/lg; active share sm/lg):")
    for p, m, f in sorted(rows, key=lambda x: x[0]["piece_sm"]):
        g = lambda v: "None" if v is None else f"{v:.2f}"
        lines.append(f"    {p['piece_sm']:.3f}  m {m:3d}  active {f['sm']['active']:.1f}/{f['lg']['active']:.1f}  dens {g(f['sm']['dens'])}/{g(f['lg']['dens'])}  "
                     f"adv {g(f['sm']['adv'])}/{g(f['lg']['adv'])}  share {f['sm']['share']:.3f}/{f['lg']['share']:.3f}")
    bs = [(p["sm"]["burst"], p["lg"]["burst"], p["sm"]["burst_end"], p["lg"]["burst_end"]) for p in P]
    lines.append(f"  reported: bursts (smaller/larger piece; None = never ended by slice {CAP}): " + "; ".join(f"{a}/{b} ({c}/{d})" for a, b, c, d in bs))
    agree = sum((p["sm"]["piece_at_burst"] < p["lg"]["piece_at_burst"]) for p in P)
    lines.append(f"  check: the smaller piece measured after the first slice is also smaller at burst end in {agree}/{len(P)} situations")
    lines.append(f"  reported: S1 replication (smaller piece has the larger burst): {sum(a > b for a, b, _, _ in bs)}/{len(bs)}")
    allc = [c for w in W for c in w["choices"]]
    pk = {p["key"]: p for p in P}
    lines.append(f"  reported per choice (not per situation): A1 holds in {sum(next((f['sm']['active'] > f['lg']['active'] for p, m, f in rows if p['key'] == c['key']), False) for c in allc)}"
                 f"/{sum(any(p['key'] == c['key'] for p, m, f in rows) for c in allc)} choices with matched slices")
    return lines


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(N_WORLDS))
    jobs = {}
    for w in W:
        for c in w["choices"]:
            jobs.setdefault(c["key"], (c["key"], c["base"], c["cs"], c["rank"]))
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(pair, list(jobs.values()), chunksize=1)
    slim = [dict(world=w["world"], status=w["status"], n_two=w["n_two"], skipped=w["skipped"],
                 choices=[{k: v for k, v in c.items() if k not in ("base", "cs", "rank")} for c in w["choices"]]) for w in W]
    json.dump(dict(worlds=slim, pairs=R), open(os.path.join(RES, "results.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    lines = analyse(W, R)
    print("\n".join(lines))
    open(os.path.join(RES, "front_activation_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
