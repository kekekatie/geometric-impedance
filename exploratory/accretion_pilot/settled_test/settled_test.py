#!/usr/bin/env python3
"""
settled_test.py -- predicted, or settled? (PREREGISTRATION.md, frozen before this file.)
24 fresh ordinary worlds. At every live two-way choice with a cut line: (1) the two options' INITIAL BURSTS (forced only,
stopped before the first guess) and their changed region's dominant family vs the family the cut predicts; (2) the core:
the largest connected chain of predicted-family tiles in each side's changed region; (3) 5 continuations per option
(patient scheduler, 20 slices, different streams): does the family survive, and are core tiles built after the first
guess identical across continuations of the same option?
`python3 settled_test.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, itertools, collections
from multiprocessing import Pool
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cut_direction"))
import cut_direction as CD
SN, SH, M, Sl, L, D, S = CD.SN, CD.SH, CD.M, CD.Sl, CD.L, CD.D, CD.S
SEED0, N_ADD, N_WORLDS, BURST_CAP, AHEAD, N_CONT, MIN_CHANGED = 20261190, 1500, 24, 40, 20, 5, 6
RES = os.path.join(HERE, "results")
cen = CD.cen
ek = lambda p, q: frozenset((L.key(p), L.key(q)))


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[168:168 + N_WORLDS]


def line_angle(n):
    return (math.degrees(math.atan2(n[1], n[0])) + 90) % 180


def predicted_family(angle):
    return int(round((90 - angle) / 36)) % 5


def dominant(tiles):
    if not tiles:
        return None
    sh = [sum(j in CD.families(t) for t in tiles) / len(tiles) for j in range(5)]
    return int(np.argmax(sh))


def burst(base, c):
    Q = L.Patch(list(base)); Q.add(c); status = "stalled"
    for _ in range(BURST_CAP):
        forced = {}; jam = False
        for e in Q.frontier():
            cs = D.candidates(Q, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam:
            status = "JAM"; break
        if not forced:
            break
        placed = [t for t in forced.values() if Q.legal(t)]
        for t in placed:
            Q.add(t)
        if not placed:
            break
    else:
        status = "cap"
    return Q.tris[len(base):], status


def continuation(base, c, stream):
    Q = L.Patch(list(base)); Q.add(c); rng = random.Random(stream); after = set(); guesses = 0; guessed = False; status = "ok"
    for s in range(1, AHEAD + 1):
        n0 = len(Q.tris); st, n, kind = SN.patient(Q, rng)
        if st == "JAM":
            status = "JAM"; break
        if kind == "guess":
            guesses += 1; guessed = True
        if guessed:
            after |= {D.dkey(t) for t in Q.tris[n0:]}
    return Q.tris[len(base):], after, guesses, status


def core(tiles, j):
    """largest chain: tiles joined through a shared family-j leg or a shared base (same rhombus)."""
    idx = {D.dkey(t): t for t in tiles}; by = collections.defaultdict(list)
    for k, t in idx.items():
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if CD.is_leg(p, q):
                if M.edge_dir(p, q)[0] == j:
                    by[("leg", ek(p, q))].append(k)
            else:
                by[("base", ek(p, q))].append(k)
    par = {k: k for k in idx}

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for ks in by.values():
        for a, b in zip(ks, ks[1:]):
            par[find(a)] = find(b)
    comp = collections.Counter(find(k) for k in idx)
    if not comp:
        return set()
    root = comp.most_common(1)[0][0]
    return {k for k in idx if find(k) == root}


def agreement(test_tiles, other):
    """among test tiles whose place `other` has built: share that are the identical tile. returns (identical, covered)."""
    if not test_tiles or not other:
        return 0, 0
    tree = cKDTree([[cen(t).real / S, cen(t).imag / S] for t in other]); okeys = {D.dkey(t) for t in other}
    ident = cov = 0
    for t in test_tiles:
        z = cen(t)
        if D.dkey(t) in okeys:
            ident += 1; cov += 1; continue
        near = tree.query_ball_point([z.real / S, z.imag / S], 1.2)
        if any(L.inside(z, *other[i][1:]) for i in near):
            cov += 1
    return ident, cov


def world(k):
    rng = random.Random(SEED0 + k); c0 = centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0; rank = Sl.rank_of(P.tris); out = []; status = "ok"
    skipped = collections.Counter()
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
            base = list(P.tris); cm0 = Sl.constraints(base, rank); aF = Sl.area(Sl.region(cm0))
            cA, cB = CD.after_first(base, cs[0], rank), CD.after_first(base, cs[1], rank)
            line = SH.cut_line(cm0, cA, cB)
            if aF <= 0 or Sl.area(Sl.region(cA)) <= 0 or Sl.area(Sl.region(cB)) <= 0:
                skipped["not live"] += 1
            elif line is None:
                skipped["no cut line"] += 1
            else:
                line0 = SH.cut_line(cm0, Sl.constraints(base + [cs[0]], rank), Sl.constraints(base + [cs[1]], rank))
                z = (fr[0][0] + fr[0][1]) / 2
                out.append(dict(world=k, slice=r, key=CD.whole_key(base, z), base=base, cs=cs, angle=line_angle(line[0]),
                                angle_tile_only=None if line0 is None else line_angle(line0[0])))
        P.add(rng.choice(cs))
    return dict(world=k, status=status, skipped=dict(skipped), choices=out)


def situation(job):
    key, base, cs, angle = job
    j = predicted_family(angle)
    (bA, sA), (bB, sB) = burst(base, cs[0]), burst(base, cs[1])
    uA, uB = CD.strip(bA, bB)
    res = dict(key=key, j=j, burst_status=[sA, sB], n_changed=len(uA) + len(uB), dom_burst=dominant(uA + uB),
               core_share=[len(core(u, j)) / len(u) if u else None for u in (uA, uB)])
    streams = [SEED0 * 1000 + int(key, 16) % (2 ** 31) + 7919 * i for i in range(N_CONT)]
    cont = {"A": [continuation(base, cs[0], s) for s in streams], "B": [continuation(base, cs[1], s) for s in streams]}
    res["guesses"] = {o: [g for _, _, g, _ in cont[o]] for o in "AB"}
    doms = []; cores = {"A": [], "B": []}; noncore = {"A": [], "B": []}; slice20 = []
    for i in range(N_CONT):
        nA, nB = cont["A"][i][0], cont["B"][i][0]
        vA, vB = CD.strip(nA, nB)
        doms.append(dominant(vA + vB))
        for o, v, after in (("A", vA, cont["A"][i][1]), ("B", vB, cont["B"][i][1])):
            ck = core(v, j)
            cores[o].append([t for t in v if D.dkey(t) in ck and D.dkey(t) in after])
            noncore[o].append([t for t in v if D.dkey(t) not in ck and D.dkey(t) in after])
            slice20.append(dict(core=len(ck) / len(v) if v else None, fams=[sum(f in CD.families(t) for t in v if D.dkey(t) not in ck) for f in range(5)]))
    res["dom_cont"] = doms; res["slice20"] = slice20
    for lab, group in (("core", cores), ("noncore", noncore)):
        worst = None; tot_i = tot_c = 0
        for o in "AB":
            for a, b in itertools.permutations(range(N_CONT), 2):
                i_, c_ = agreement(group[o][a], cont[o][b][0])
                tot_i += i_; tot_c += c_
                if c_:
                    worst = i_ / c_ if worst is None else min(worst, i_ / c_)
        res[lab] = dict(worst=worst, identical=tot_i, covered=tot_c)
    return res


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(N_WORLDS))
    first = {}
    for w in W:
        for c in w["choices"]:
            first.setdefault(c["key"], c)
    jobs = [(c["key"], c["base"], c["cs"], c["angle"]) for c in first.values()]
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(situation, jobs, chunksize=1)
    meta = {k: dict(world=c["world"], slice=c["slice"], angle=c["angle"], angle_tile_only=c["angle_tile_only"]) for k, c in first.items()}
    json.dump(dict(situations=R, meta=meta, skipped=[w["skipped"] for w in W], statuses=[w["status"] for w in W]),
              open(os.path.join(RES, "results.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    T = [r for r in R if r["n_changed"] >= MIN_CHANGED]
    lines = [f"worlds: statuses {dict(collections.Counter(w['status'] for w in W))}; skipped {dict(sum((collections.Counter(w['skipped']) for w in W), collections.Counter()))}; "
             f"choices used {sum(len(w['choices']) for w in W)}; distinct situations {len(R)}; tested (>= {MIN_CHANGED} changed tiles in the initial bursts) {len(T)}",
             f"  initial burst statuses {dict(collections.Counter(s for r in R for s in r['burst_status']))}"]
    p1 = sum(r["dom_burst"] == r["j"] for r in T)
    lines.append(f"  P1: {'HELD  ' if T and p1 >= 0.9 * len(T) else 'FAILED'}  initial-burst dominant family = predicted family in {p1}/{len(T)} (need >= 90%)")
    cs_ = [x for r in T for x in r["core_share"] if x is not None]
    p2 = sum(x >= 0.5 for x in cs_)
    lines.append(f"  P2: {'HELD  ' if cs_ and p2 >= 0.6 * len(cs_) else 'FAILED'}  core chain covers >= 50% of a side's changed tiles in {p2}/{len(cs_)} situation-sides "
                 f"(need >= 60%); core shares median {np.median(cs_):.2f} (IQR {np.quantile(cs_, .25):.2f}-{np.quantile(cs_, .75):.2f})")
    p3 = sum(len(set(r["dom_cont"])) == 1 for r in T)
    lines.append(f"  P3: {'HELD  ' if T and p3 >= 0.9 * len(T) else 'FAILED'}  slice-20 dominant family identical across all {N_CONT} continuation pairs in {p3}/{len(T)} (need >= 90%); "
                 f"and equal to the predicted family in all {N_CONT}: {sum(set(r['dom_cont']) == {r['j']} for r in T)}/{len(T)}")
    has = [r for r in T if r["core"]["worst"] is not None]
    p4 = sum(r["core"]["worst"] >= 0.99 for r in has)
    lines.append(f"  P4: {'HELD  ' if has and p4 >= 0.8 * len(has) else 'FAILED'}  core tiles built after the first guess identical across continuations of the same option "
                 f"(worst pair >= 99%) in {p4}/{len(has)} situations with such tiles (need >= 80%); pooled {sum(r['core']['identical'] for r in has)}/"
                 f"{sum(r['core']['covered'] for r in has)}; situations without such tiles: {len(T) - len(has)}")
    hc = [r for r in T if r["noncore"]["worst"] is not None]
    lines.append(f"  control (non-core changed tiles built after the first guess): worst pair >= 99% in {sum(r['noncore']['worst'] >= 0.99 for r in hc)}/{len(hc)}; "
                 f"pooled {sum(r['noncore']['identical'] for r in hc)}/{sum(r['noncore']['covered'] for r in hc)}")
    g = [x for r in R for o in "AB" for x in r["guesses"][o]]
    lines.append(f"  reported: guesses per continuation in {AHEAD} slices: {dict(sorted(collections.Counter(g).items()))} (mean {np.mean(g):.2f})")
    same = [m for m in meta.values() if m["angle_tile_only"] is not None]
    lines.append(f"  reported: cut read from the choice tile alone found in {len(same)}/{len(meta)}; same direction as after the first slice in "
                 f"{sum(abs(((m['angle'] - m['angle_tile_only']) + 90) % 180 - 90) < 1 for m in same)}/{len(same)}")
    c20 = [x["core"] for r in T for x in r["slice20"] if x["core"] is not None]
    nf = np.sum([x["fams"] for r in T for x in r["slice20"]], axis=0)
    lines.append(f"  reported: slice-20 core share median {np.median(c20):.2f}; non-core changed tiles by family (counts, a tile can have two) {nf.tolist()}")
    lines.append(f"  reported: P1 among all situations incl. small ones {sum(r['dom_burst'] == r['j'] for r in R if r['dom_burst'] is not None)}/{sum(r['dom_burst'] is not None for r in R)}")
    print("\n".join(lines))
    open(os.path.join(RES, "settled_test_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
