#!/usr/bin/env python3
"""
depth_direction.py -- the depth-and-direction lenses (Experiment B).
(PREREGISTRATION.md, frozen before this file.)

Re-grows the same 24 worlds as Experiment A, catches the same ties, then switches
on the hidden-side lenses from perp_map: hull depth and directional balance per
vertex. Marries A's keystone corners onto that map and asks:
  B1  keystone vertices are shallow (near the window edge).
  B2  their directional-balance arrows pull inward.
  B3  depth on trial for A's malleability: do shallower choice vertices settle more?

Run:  python3 depth_direction.py                    # full, 24 worlds, parallel
      python3 depth_direction.py --worlds 2 --nadd 400 --serial   # quick test
"""
from __future__ import annotations
from pathlib import Path
import sys, os, json, math, cmath, random, collections, argparse
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                                   # figures, corner path
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))     # corner_response
sys.path.insert(0, str(HERE.parent.parent / "perp_map"))               # perp_map

import figures as F
import corner_response as CR
import perp_map as PM

L, D, S = F.L, F.D, F.S
ZETA = PM.ZETA
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
INWARD_MIN = 0.5           # B2 threshold
B3_SPEARMAN = -0.2         # B3 threshold


# --- growth that also keeps the vertices each tie lives on, and the final patch ---
def grow_world_b(k):
    rng = random.Random(CR.SEED0 + k)
    P = L.Patch(L.seed_patch(CR.centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    active, done, ties = {}, set(), []
    status = "ok"

    def resolve(sk, rec):
        tie = active.pop(sk); done.add(sk)
        rec.update(world=k, site=sk, first_slice=tie["first_slice"], fps=tie["fps"],
                   choice_vertices=tie["cvk"], xy=[tie["mid"].real / S, tie["mid"].imag / S])
        if rec.get("drawer") == "single_keystone":
            kv = set()
            for ks in rec.get("keystones", []):
                if ks["corner"]:
                    for fv in ks["failing_vertices"]:
                        kv.add(tuple(fv))
            rec["keystone_vertices"] = [list(v) for v in kv]
        ties.append(rec)

    while len(P.tris) - n0 < CR.N_ADD:
        r += 1
        fr = P.frontier(); cand = {}; fmap = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            sk = CR.ek(e); cand[sk] = len(cs); fmap[sk] = e
        if jam:
            status = "JAM"; break
        for sk in list(active):
            tie = active[sk]
            if sk not in cand:
                resolve(sk, dict(drawer="gone"))
            elif cand[sk] == 1:
                added_local = CR.near(P.tris[len(tie["before"]):], tie["mid"], CR.RPRIMARY)
                rec = CR.response_test(tie["before"], added_local, tie["edge"]); rec["response_settled"] = True
                resolve(sk, rec)
            elif r - tie["first_slice"] >= CR.K:
                resolve(sk, dict(drawer="stayed_open"))
        for sk, n in cand.items():
            if n == 2 and sk not in active and sk not in done:
                e = fmap[sk]; mid = (e[0] + e[1]) / 2; before = list(P.tris)
                active[sk] = dict(before=before, edge=e, first_slice=r, mid=mid,
                                  cvk=[list(L.key(e[0])), list(L.key(e[1]))],
                                  fps={R: CR.fingerprint(before, mid, R) for R in CR.RADII})
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= CR.N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        cs = F.SN.ordered(D.candidates(P, *fr[0][:3])); gk = CR.ek(fr[0])
        if gk in active:
            resolve(gk, dict(drawer="directly_chosen"))
        P.add(rng.choice(cs))
    for sk in list(active):
        resolve(sk, dict(drawer="stayed_open", at_end=True))
    return dict(world=k, status=status, ties=ties, tiles=[list(t) for t in P.tris])


# --- the two lenses: depth, directional balance, inward pull, completeness per vertex ---
def lenses(tiles):
    tiles = [tuple([t[0]] + [complex(z) if not isinstance(z, complex) else z for z in t[1:]]) for t in tiles]
    K, pos, conf = PM.lift(tiles)
    dep, areas, layers = PM.depths(K)
    adj = collections.defaultdict(list)
    for t in tiles:
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if abs(abs(q - p) - S) < 1e-4 * S:
                j, sg = PM.edge_dir(p, q)
                adj[L.key(p)].append((j, sg))
    # per-layer perp centroid for the inward/radial test
    bylayer = collections.defaultdict(list)
    for v, kk in K.items():
        bylayer[int(kk.sum())].append(v)
    centroid = {lay: np.mean([[PM.perp(K[v]).real, PM.perp(K[v]).imag] for v in vs], axis=0)
                for lay, vs in bylayer.items() if len(vs) >= 10}
    # completeness: do tiles fill all the way around the vertex (2*pi)?
    vtiles = collections.defaultdict(list)
    for t in tiles:
        for z in t[1:]:
            vtiles[L.key(z)].append(t)
    balance, inward, tangential, complete = {}, {}, {}, {}
    for v, nbrs in adj.items():
        R = sum(sg * ZETA ** (2 * j) for j, sg in nbrs) / len(nbrs)
        balance[v] = abs(R)
        lay = int(K[v].sum())
        if lay in centroid and abs(R) > EPS and v in pos:
            pv = np.array([PM.perp(K[v]).real, PM.perp(K[v]).imag]); rad = centroid[lay] - pv
            if np.linalg.norm(rad) > EPS:
                rhat = rad / np.linalg.norm(rad); that = np.array([-rhat[1], rhat[0]])
                inward[v] = float(np.dot([R.real, R.imag], rhat)) / abs(R)
                tangential[v] = float(np.dot([R.real, R.imag], that)) / abs(R)
        zc = pos.get(v)
        if zc is not None:
            ang = 0.0
            for t in vtiles[v]:
                o = [p for p in t[1:] if L.key(p) != v]
                if len(o) == 2:
                    u, w = o[0] - zc, o[1] - zc
                    if abs(u) > EPS and abs(w) > EPS:
                        ang += math.acos(max(-1, min(1, (u.conjugate() * w).real / (abs(u) * abs(w)))))
            complete[v] = abs(ang - 2 * math.pi) < 1e-6
    return dict(dep=dep, balance=balance, inward=inward, tangential=tangential,
                complete=complete, conflicts=len(conf), n_vertices=len(K))


def world_task(k):
    w = grow_world_b(k)
    g = lenses(w["tiles"])
    dep, complete = g["dep"], g["complete"]
    def d(vk):
        t = tuple(vk)
        return dep.get(t)
    # annotate each tie
    out = []
    for tie in w["ties"]:
        cvd = [d(v) for v in tie["choice_vertices"]]; cvd = [x for x in cvd if x is not None]
        rec = dict(world=k, drawer=tie["drawer"], fps=tie["fps"],
                   choice_depth=float(np.mean(cvd)) if cvd else None)
        if tie["drawer"] == "single_keystone" and tie.get("keystone_vertices"):
            kd = [d(v) for v in tie["keystone_vertices"]]; kd = [x for x in kd if x is not None]
            kb = [g["balance"].get(tuple(v)) for v in tie["keystone_vertices"]]
            ki = [g["inward"].get(tuple(v)) for v in tie["keystone_vertices"] if complete.get(tuple(v))]
            kt = [g["tangential"].get(tuple(v)) for v in tie["keystone_vertices"] if complete.get(tuple(v))]
            rec["keystone_depth"] = float(np.mean(kd)) if kd else None
            rec["keystone_inward"] = float(np.mean([x for x in ki if x is not None])) if any(x is not None for x in ki) else None
            rec["keystone_tangential"] = float(np.mean([x for x in kt if x is not None])) if any(x is not None for x in kt) else None
        out.append(rec)
    world_depths = [v for v in dep.values()]
    # interior subset depth<->balance spearman (lens vs paper)
    iv = [v for v in g["balance"] if complete.get(v) and v in dep]
    lens_rho = float(spearmanr([dep[v] for v in iv], [g["balance"][v] for v in iv])[0]) if len(iv) > 20 else None
    return dict(world=k, status=w["status"], ties=out,
                world_median_depth=float(np.median(world_depths)) if world_depths else None,
                conflicts=g["conflicts"], lens_rho=lens_rho, n_interior=len(iv))


def score(worlds):
    ties = [t for w in worlds for t in w["ties"]]
    ks = [t for t in ties if t["drawer"] == "single_keystone"]
    lines = [f"worlds: {len(worlds)}; statuses {dict(collections.Counter(w['status'] for w in worlds))}; "
             f"lift conflicts {[w['conflicts'] for w in worlds]}; ties {len(ties)}; keystone ties {len(ks)}"]

    # B1 -- keystone vertices shallow (per world: keystone median depth < world median depth)
    wins = 0; worlds_with = 0
    for w in worlds:
        kd = [t["keystone_depth"] for t in w["ties"] if t["drawer"] == "single_keystone" and t.get("keystone_depth") is not None]
        if kd and w["world_median_depth"] is not None:
            worlds_with += 1
            if np.median(kd) < w["world_median_depth"]:
                wins += 1
    allkd = [t["keystone_depth"] for t in ks if t.get("keystone_depth") is not None]
    allwd = [w["world_median_depth"] for w in worlds if w["world_median_depth"] is not None]
    lines.append(f"B1: {'HELD  ' if wins >= 20 else 'FAILED'}  keystone-vertex median depth below world median in "
                 f"{wins}/{worlds_with} worlds (need >= 20/24); pooled keystone depth median "
                 f"{np.median(allkd):.3f} vs world median {np.median(allwd):.3f}")

    # B2 -- keystone arrows pull inward, tangential ~ 0
    ki = [t["keystone_inward"] for t in ks if t.get("keystone_inward") is not None]
    kt = [t["keystone_tangential"] for t in ks if t.get("keystone_tangential") is not None]
    mean_in = float(np.mean(ki)) if ki else 0.0; mean_tan = float(np.mean(kt)) if kt else 0.0
    lines.append(f"B2: {'HELD  ' if mean_in > INWARD_MIN else 'FAILED'}  keystone inward alignment mean {mean_in:.3f} "
                 f"(need > {INWARD_MIN}; +1=inward), over {len(ki)} complete keystone vertices; "
                 f"tangential mean {mean_tan:.3f} (want ~0)")

    # B3 -- depth on trial: shallower choice vertices settle more
    groups = collections.defaultdict(lambda: dict(settled=0, obs=0, depths=[]))
    for t in ties:
        if t["drawer"] in ("single_keystone", "committee", "stayed_open"):
            fp = t["fps"].get(str(CR.RPRIMARY)) or t["fps"].get(CR.RPRIMARY)
            if fp and t["choice_depth"] is not None:
                g = groups[fp]; g["obs"] += 1; g["depths"].append(t["choice_depth"])
                if t["drawer"] != "stayed_open":
                    g["settled"] += 1
    rec = {fp: g for fp, g in groups.items() if g["obs"] >= CR.MIN_RECUR}
    sf = [g["settled"] / g["obs"] for g in rec.values()]
    md = [float(np.mean(g["depths"])) for g in rec.values()]
    rho = float(spearmanr(md, sf)[0]) if len(rec) > 3 else None
    # pooled: settled vs stayed-open choice depth
    sd = [t["choice_depth"] for t in ties if t["drawer"] in ("single_keystone", "committee") and t["choice_depth"] is not None]
    od = [t["choice_depth"] for t in ties if t["drawer"] == "stayed_open" and t["choice_depth"] is not None]
    held_b3 = rho is not None and rho <= B3_SPEARMAN
    lines.append(f"B3: {'HELD  ' if held_b3 else 'did not hold' if rho is not None else 'N/A'}  "
                 f"depth<->settle-fraction Spearman {rho if rho is None else round(rho,3)} across {len(rec)} recurring moves "
                 f"(pledged <= {B3_SPEARMAN}; negative = shallower settles more)")
    lines.append(f"    pooled choice-vertex depth: settled median {np.median(sd):.3f} (n {len(sd)}) vs "
                 f"stayed-open median {np.median(od):.3f} (n {len(od)})")

    # reported: our lens vs the paper
    rhos = [w["lens_rho"] for w in worlds if w["lens_rho"] is not None]
    lines.append(f"  reported (lens vs paper): depth<->balance Spearman on interior subset, per-world median "
                 f"{np.median(rhos):.3f} (June paper: -0.72 to -0.78)")
    # reported: shuffled control for B1
    allv = []
    for w in worlds:
        allv += [t["keystone_depth"] for t in w["ties"] if t["drawer"] == "single_keystone" and t.get("keystone_depth") is not None]
    rng = random.Random(0)
    shuf_wins = 0
    for w in worlds:
        kd = [t["keystone_depth"] for t in w["ties"] if t["drawer"] == "single_keystone" and t.get("keystone_depth") is not None]
        if kd and w["world_median_depth"] is not None:
            fake = [rng.choice(allv) for _ in kd]
            if np.median(fake) < w["world_median_depth"]:
                shuf_wins += 1
    lines.append(f"  reported (shuffled control for B1): keystone-below-world in {shuf_wins}/{worlds_with} worlds "
                 f"when depths are drawn at random (should be ~half; real B1 was {wins})")

    summary = dict(ties=len(ties), keystone_ties=len(ks),
                   B1=dict(held=wins >= 20, wins=wins, worlds=worlds_with,
                           keystone_median=float(np.median(allkd)), world_median=float(np.median(allwd))),
                   B2=dict(held=mean_in > INWARD_MIN, inward=mean_in, tangential=mean_tan, n=len(ki)),
                   B3=dict(held=held_b3, spearman=rho, moves=len(rec),
                           settled_depth=float(np.median(sd)), open_depth=float(np.median(od))),
                   lens_rho_median=float(np.median(rhos)) if rhos else None,
                   shuffled_B1_wins=shuf_wins,
                   b3_scatter=[[round(x, 4), round(y, 4)] for x, y in zip(md, sf)])
    return "\n".join(lines), summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=CR.N_WORLDS)
    ap.add_argument("--nadd", type=int, default=None)
    ap.add_argument("--serial", action="store_true")
    args = ap.parse_args()
    if args.nadd:
        CR.N_ADD = args.nadd
    ids = list(range(args.worlds))
    if args.serial or args.worlds == 1:
        worlds = [world_task(k) for k in ids]
    else:
        with Pool(min(4, args.worlds), maxtasksperchild=1) as p:
            worlds = p.map(world_task, ids)
    report, summary = score(worlds)
    print(report)
    (RES / "worlds.json").write_text(json.dumps(worlds, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (RES / "summary.json").write_text(json.dumps(summary, indent=2))
    (RES / "depth_direction_report.txt").write_text(report + "\n")


if __name__ == "__main__":
    main()
