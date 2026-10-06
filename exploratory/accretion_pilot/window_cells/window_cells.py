#!/usr/bin/env python3
"""
window_cells.py -- does the local clock live in the window after all? (PREREGISTRATION.md, frozen before this file.)
A: settling time vs the level-r window cell (= translation class of the decorated tiles in the r-disc), with shuffled-
label nulls, cross-world prediction, depth within cells, and cell size (frequency). B: perp_map M1 and decision_radius R1
redone within 1-edge cells. C: M2 against the true Penrose window (four pentagons), whole worlds vs 36-degree wedges.
`python3 window_cells.py [A|B|C ...]` runs the named parts (default all) and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, hashlib, collections
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "structure_clock"))
import structure_clock as SC
M, D, L, S = SC.M, SC.D, SC.L, SC.S
RES = os.path.join(HERE, "results")
TAU = (1 + 5 ** 0.5) / 2
SCALES = [0.6, 0.8, 1.0, 1.25, 1.5, 2.0]
N_WORLDS, NULL, MIN_TRAIN, TOL, NPART = 20, 200, 3, 0.01, 100
cen = SC.cen


def ring_of(x):
    return [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]


def seeds_and_ok():
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
    return seeds, ok0


def cell_key(tiles, idx, z):
    """translation class of the decorated tiles idx, relative to point z (hashed)."""
    rk = lambda w: (round((w - z).real / S, 3), round((w - z).imag / S, 3))
    items = sorted((tiles[i][0], rk(tiles[i][1]), rk(tiles[i][2]), rk(tiles[i][3])) for i in idx)
    return hashlib.md5(repr(items).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- Part A
def a_world(args):
    s, ring = args
    P, rnd, rounds, guesses, status = SC.grow(ring, SC.N_TILES, D.SEED0 + 100 * s)
    tiles = list(P.tris)
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    tc = np.array([cen(t) for t in tiles]); tr = np.array([rnd[D.dkey(t)] for t in tiles])
    rows = []
    for v in sorted(K):
        z = pos[v]
        if abs(z) < SC.R_IN * S or v not in dep or np.min(np.abs(mids - z)) < SC.FRONT_GAP * S:
            continue
        d = np.abs(tc - z); row = dict(rad=abs(z) / S, depth=dep[v], T={}, cell={})
        for r in SCALES:
            idx = np.where(d <= r * S)[0]
            if len(idx) == 0:
                break
            row["T"][str(r)] = int(tr[idx].max() - tr[idx].min()); row["cell"][str(r)] = cell_key(tiles, idx, z)
        else:
            rows.append(row)
    return dict(seed=s, status=status, guesses=guesses, rows=rows)


def resid(rad, y):
    y = np.asarray(y, float); b = np.array([int(x) for x in rad]); out = y.copy()
    for k in set(b):
        m = b == k; out[m] = y[m] - y[m].mean()
    return out


def eta2(y, lab):
    y = np.asarray(y, float); tot = ((y - y.mean()) ** 2).sum()
    if tot == 0:
        return float("nan")
    g = collections.defaultdict(list)
    for yi, li in zip(y, lab):
        g[li].append(yi)
    return float(sum(len(v) * (np.mean(v) - y.mean()) ** 2 for v in g.values()) / tot)


def shuffle_within(lab, rad, rng):
    lab = list(lab); b = collections.defaultdict(list)
    for i, x in enumerate(rad):
        b[int(x)].append(i)
    out = list(lab)
    for idx in b.values():
        vals = [lab[i] for i in idx]; rng.shuffle(vals)
        for i, v in zip(idx, vals):
            out[i] = v
    return out


def loo_r2(worlds, labs_train, labs_test):
    """pooled leave-one-world-out R2: predict y by the mean y of the same cell in the other worlds (>= MIN_TRAIN)."""
    tot_s = collections.Counter(); tot_n = collections.Counter(); own = []
    for (y, _), lt in zip(worlds, labs_train):
        s_ = collections.Counter(); n_ = collections.Counter()
        for yi, li in zip(y, lt):
            s_[li] += yi; n_[li] += 1
        own.append((s_, n_)); tot_s.update(s_); tot_n.update(n_)
    ys, ps = [], []
    for (y, _), le, (s_, n_) in zip(worlds, labs_test, own):
        for yi, li in zip(y, le):
            n = tot_n[li] - n_[li]
            if n >= MIN_TRAIN:
                ys.append(yi); ps.append((tot_s[li] - s_[li]) / n)
    ys, ps = np.array(ys), np.array(ps)
    n_all = sum(len(y) for y, _ in worlds)
    if len(ys) < 2:
        return float("nan"), 0.0
    return float(1 - ((ys - ps) ** 2).sum() / ((ys - ys.mean()) ** 2).sum()), len(ys) / n_all


def part_a(lines):
    seeds, ok0 = seeds_and_ok()
    dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])][:N_WORLDS]
    with Pool(4, maxtasksperchild=2) as p:
        W = p.map(a_world, [(x["seed"], ring_of(x)) for x in dec])
    json.dump(W, open(os.path.join(RES, "a_worlds.json"), "w"))
    lines.append(f"PART A: {len(W)} decapod worlds, statuses {sorted({w['status'] for w in W})}, guesses {sorted({w['guesses'] for w in W})}, "
                 f"probes per world {min(len(w['rows']) for w in W)}-{max(len(w['rows']) for w in W)}")
    rng = random.Random(2070); summary = {}
    for r in map(str, SCALES):
        per = []; worlds = []
        freq = collections.Counter(row["cell"][r] for w in W for row in w["rows"]); ntot = sum(freq.values())
        for w in W:
            rad = [row["rad"] for row in w["rows"]]; lab = [row["cell"][r] for row in w["rows"]]
            y = resid(rad, [row["T"][r] for row in w["rows"]]); worlds.append((y, rad))
            e = eta2(y, lab); nulls = [eta2(y, shuffle_within(lab, rad, rng)) for _ in range(NULL)]
            nm = float(np.mean(nulls)); adj = (e - nm) / (1 - nm) if nm < 1 else float("nan")
            # A4: depth vs T within cells (centred on cell means), cells with >= 2 probes
            g = collections.defaultdict(list)
            for i, l in enumerate(lab):
                g[l].append(i)
            dc, yc = [], []
            for idx in g.values():
                if len(idx) >= 2:
                    dd = np.array([w["rows"][i]["depth"] for i in idx]); yy = y[idx]
                    dc += list(dd - dd.mean()); yc += list(yy - yy.mean())
            a4 = spearmanr(dc, yc).correlation if len(dc) > 10 and np.ptp(dc) > 0 and np.ptp(yc) > 0 else float("nan")
            a5, _ = SC.strat_spearman(rad, [math.log(freq[l] / ntot) for l in lab], y)
            per.append(dict(eta2=e, null_mean=nm, null95=float(np.quantile(nulls, 0.95)), adj=adj, a4=float(a4), a5=float(a5),
                            n_cells=len(set(lab)), singletons=sum(1 for v in g.values() if len(v) == 1)))
        labs = [[row["cell"][r] for row in w["rows"]] for w in W]
        r2, cov = loo_r2(worlds, labs, labs)
        nr2 = [loo_r2(worlds, [shuffle_within(l, rad, rng) for l, (_, rad) in zip(labs, worlds)], labs)[0] for _ in range(NULL)]
        summary[r] = dict(per=per, r2=r2, coverage=cov, null_r2_95=float(np.nanquantile(nr2, 0.95)), null_r2_mean=float(np.nanmean(nr2)),
                          cells_total=len(freq))
        a1 = sum(q["adj"] >= 0.5 for q in per); a2 = sum(q["eta2"] > q["null95"] for q in per); a5n = sum(q["a5"] < 0 for q in per)
        lines.append(f"  disc {r}: cells {len(freq)} (singletons/world median {np.median([q['singletons'] for q in per]):.0f}, cells/world "
                     f"median {np.median([q['n_cells'] for q in per]):.0f}); eta2 median {np.median([q['eta2'] for q in per]):.3f} vs null "
                     f"{np.median([q['null_mean'] for q in per]):.3f}; adjusted eta2 median {np.median([q['adj'] for q in per]):+.3f} "
                     f"[{min(q['adj'] for q in per):+.3f}, {max(q['adj'] for q in per):+.3f}]; A1 adj>=0.5 in {a1}/20; A2 eta2>null95 in {a2}/20")
        lines.append(f"      cross-world R2 {r2:+.3f} (coverage {cov:.2f}; null mean {summary[r]['null_r2_mean']:+.3f}, null95 "
                     f"{summary[r]['null_r2_95']:+.3f}); A4 within-cell rho(depth,T) median {np.nanmedian([q['a4'] for q in per]):+.3f}; "
                     f"A5 rho(log freq,T) <0 in {a5n}/20, median {np.nanmedian([q['a5'] for q in per]):+.3f}")
    json.dump(summary, open(os.path.join(RES, "a_summary.json"), "w"))
    A1 = all(sum(q["adj"] >= 0.5 for q in summary[r]["per"]) >= 15 for r in summary)
    A2 = all(sum(q["eta2"] > q["null95"] for q in summary[r]["per"]) >= 15 for r in summary)
    A3 = all(summary[r]["r2"] > 0 and summary[r]["r2"] > summary[r]["null_r2_95"] for r in summary)
    A3s = all(summary[r]["r2"] >= 0.5 for r in summary)
    A4 = all(abs(np.nanmedian([q["a4"] for q in summary[r]["per"]])) < 0.1 for r in summary)
    A5 = sum(sum(q["a5"] < 0 for q in summary[r]["per"]) >= 15 for r in summary) >= 5
    lines += [f"  A1: {'HELD  ' if A1 else 'FAILED'}  (Fable strong) adjusted eta2 >= 0.5 in >= 15/20 worlds at every scale",
              f"  A2: {'HELD  ' if A2 else 'FAILED'}  eta2 above null 95th pct in >= 15/20 worlds at every scale",
              f"  A3: {'HELD  ' if A3 else 'FAILED'}  cross-world R2 > 0 and > null95 at every scale; strong form R2 >= 0.5 everywhere: {'yes' if A3s else 'no'}",
              f"  A4: {'HELD  ' if A4 else 'FAILED'}  |median within-cell rho(depth, T)| < 0.1 at every scale",
              f"  A5: {'HELD  ' if A5 else 'FAILED'}  rho(log cell frequency, T) < 0 in >= 15/20 worlds at >= 5/6 scales"]


# ---------------------------------------------------------------- Part B
def cells_at(tiles, pts, r=1.0):
    tc = np.array([cen(t) for t in tiles])
    return [cell_key(tiles, np.where(np.abs(tc - z) <= r * S)[0], z) for z in pts]


def b1_task(k):
    tiles, events, guesses, status = M.grow(L.seed_patch(0j, 3 * S), M.N_M1, M.SEED0 + k, record=True)
    K, pos, conf = M.lift(tiles); dep, areas, layers = M.depths(K)
    d = lambda a, b: (dep[a] + dep[b]) / 2 if a in dep and b in dep else None
    ev = [(a, b, n, d(a, b)) for a, b, n in events if n >= 1 and d(a, b) is not None]
    edges = sorted({(a, b) for a, b, _, _ in ev})
    cl = dict(zip(edges, cells_at(tiles, [(complex(*a) + complex(*b)) / 2 for a, b in edges])))
    op = [x for _, _, n, x in ev if n >= 2]; fo = [x for _, _, n, x in ev if n == 1]
    g = collections.defaultdict(lambda: ([], []))
    for a, b, n, x in ev:
        g[cl[(a, b)]][0 if n >= 2 else 1].append(x)
    num = den = 0.0
    for o, f in g.values():
        if o and f:
            w = len(o) + len(f); num += w * (np.mean(o) - np.mean(f)); den += w
    return dict(run=k, med_open=float(np.median(op)), med_forced=float(np.median(fo)), raw_gap=float(np.mean(op) - np.mean(fo)),
                within_gap=num / den if den else float("nan"), share_in_mixed=den / len(ev), n_cells=len(g))


def b2_world(s):
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in seeds if v["seed"] == s)
    P, rnd, rounds, guesses, status = SC.grow(ring_of(x), SC.N_TILES, D.SEED0 + 100 * s)
    tiles = list(P.tris)
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    cands = sorted(v for v in K if v in dep and 4 * S <= abs(pos[v]) <= 10 * S and np.min(np.abs(mids - pos[v])) >= 4.5 * S)
    random.Random(2050 + s).shuffle(cands)
    vs = cands[:100]
    return s, [dep[v] for v in vs], cells_at(tiles, [pos[v] for v in vs])


def part_b(lines):
    saved = {r["run"]: r for r in json.load(open(os.path.join(HERE, "..", "perp_map", "results", "m1_runs.json")))}
    with Pool(4, maxtasksperchild=2) as p:
        B1 = p.map(b1_task, range(M.SEEDS_M1))
        B2 = p.map(b2_world, [2, 3, 4, 5])
    rep = all(abs(b["med_open"] - saved[b["run"]]["med_open"]) < 1e-9 and abs(b["med_forced"] - saved[b["run"]]["med_forced"]) < 1e-9 for b in B1)
    lines.append(f"PART B1 (M1 within 1-edge cells): regrown runs reproduce saved medians: {rep}")
    for b in B1:
        lines.append(f"    run {b['run']}: raw gap (open - forced mean depth) {b['raw_gap']:+.4f}; within-cell gap {b['within_gap']:+.4f} "
                     f"(ratio {b['within_gap'] / b['raw_gap']:+.2f}); events in cells with both kinds {b['share_in_mixed']:.2f}; cells {b['n_cells']}")
    b1 = sum(abs(b["within_gap"]) < abs(b["raw_gap"]) / 3 for b in B1)
    lines.append(f"  B1: {'HELD  ' if b1 >= 9 and rep else 'FAILED'}  within-cell gap < 1/3 of raw gap in {b1}/12 (need >= 9)")
    W = {w["seed"]: w for w in json.load(open(os.path.join(HERE, "..", "decision_radius", "results", "worlds.json")))}
    dp, dr, lab, match = [], [], [], True
    for s, deps, cells in B2:
        rows = W[s]["rows"]
        match &= all(abs(a - r["depth"]) < 1e-9 for a, r in zip(deps, rows)) and len(rows) == len(deps)
        dp += deps; dr += [r["decision_radius"] for r in rows]; lab += cells
    raw = spearmanr(dp, dr).correlation
    g = collections.defaultdict(list)
    for i, l in enumerate(lab):
        g[l].append(i)
    dc, rc = [], []
    for idx in g.values():
        if len(idx) >= 2:
            a = np.array([dp[i] for i in idx]); b = np.array([dr[i] for i in idx])
            dc += list(a - a.mean()); rc += list(b - b.mean())
    within = spearmanr(dc, rc).correlation
    lines += [f"PART B2 (R1 within 1-edge cells): regrown probes match saved depths: {match}; cells {len(g)}, probes in cells with >= 2: {len(dc)}",
              f"    raw pooled rho(depth, decision radius) {raw:+.3f}; within-cell {within:+.3f}; eta2 of decision radius by cell "
              f"{eta2(dr, lab):.3f}",
              f"  B2: {'HELD  ' if abs(within) < 0.1 and match else 'FAILED'}  |within-cell rho| < 0.1"]
    json.dump(dict(B1=B1, B2=dict(raw=raw, within=within, n=len(dc), cells=len(g))), open(os.path.join(RES, "b_summary.json"), "w"))


# ---------------------------------------------------------------- Part C
def pentagon(R, sign):
    """facet normals and apothem of a regular pentagon with vertices at sign * R * zeta^(2j) (angles multiples of 72)."""
    vert_angles = [cmath.phase(sign * cmath.exp(2j * math.pi * 2 * j / 5)) for j in range(5)]
    normals = np.array([[math.cos(a + math.pi / 5), math.sin(a + math.pi / 5)] for a in vert_angles])
    return normals, R * math.cos(math.pi / 5)


def points_by_rank(K):
    lays = sorted({int(k.sum()) for k in K.values()})
    assert len(lays) == 4, lays
    rank = {l: i for i, l in enumerate(lays)}
    return {v: (rank[int(k.sum())], M.perp(k)) for v, k in K.items()}


def window(signs):
    return [pentagon(1.0 if i in (0, 3) else TAU, signs[i]) for i in range(4)]


def fit(pts, win):
    """min s such that one translation t puts every point inside its layer's pentagon pushed out by s. returns (s, t)."""
    A, b = [], []
    for rk, z in pts:
        n, h = win[rk]
        for nx, ny in n:
            A.append([-nx, -ny, -1.0]); b.append(h - (nx * z.real + ny * z.imag))
    res = linprog([0, 0, 1], A_ub=A, b_ub=b, bounds=[(None, None)] * 3, method="highs")
    return float(res.x[2]), complex(res.x[0], res.x[1])


def violation(rk, z, t, win):
    n, h = win[rk]
    return float(max(nx * (z - t).real + ny * (z - t).imag for nx, ny in n) - h)


def union_area(ts, win, res=0.01):
    tot = 0.0
    for rk in range(4):
        n, h = win[rk]; R = h / math.cos(math.pi / 5)
        xs = [t.real for t in ts]; ys = [t.imag for t in ts]
        gx = np.arange(min(xs) - R, max(xs) + R, res); gy = np.arange(min(ys) - R, max(ys) + R, res)
        X, Y = np.meshgrid(gx, gy); inside = np.zeros(X.shape, bool)
        for t in ts:
            inside |= np.all([nx * (X - t.real) + ny * (Y - t.imag) <= h for nx, ny in n], axis=0)
        tot += inside.sum() * res * res
    return tot


def c_world(args):
    s, kind, ring, win = args
    tiles, _, guesses, status = M.grow(ring, 800, D.SEED0 + 100 * s, wall=True)
    K, pos, conf = M.lift(tiles); dep, areas, layers = M.depths(K)
    pr = points_by_rank(K); vs = sorted(pr)
    s_all, t_all = fit([pr[v] for v in vs], win)
    out_pts = [(abs(pos[v]) / S, math.degrees(cmath.phase(pos[v])) % 360) for v in vs if violation(*pr[v], t_all, win) > TOL]
    best = None
    for phase in (0.0, 18.0):
        wedge = {v: int(((math.degrees(cmath.phase(pos[v])) - phase) % 360) // 36) for v in vs}
        fits = [fit([pr[v] for v in vs if wedge[v] == w], win) for w in range(10)]
        worst = max(f[0] for f in fits)
        if best is None or worst < best[0]:
            best = (worst, phase, fits, [sum(1 for v in vs if wedge[v] == w) for w in range(10)])
    worst, phase, fits, sizes = best
    rng = random.Random(2071 + s); all_fit = 0
    for _ in range(NPART):
        order = list(vs); rng.shuffle(order); i = 0; ok = True
        for n in sizes:
            grp = order[i:i + n]; i += n
            if fit([pr[v] for v in grp], win)[0] > TOL:
                ok = False; break
        all_fit += ok
    return dict(seed=s, kind=kind, status=status, guesses=len(guesses), hull_area=float(sum(areas.values())), n=len(vs),
                s_all=s_all, n_out=len(out_pts), out_pts=out_pts, wedge_phase=phase, wedge_s=[f[0] for f in fits], wedge_sizes=sizes,
                worst_wedge=worst, random_all_fit=all_fit, union_area=union_area([f[1] for f in fits], win),
                wedge_shifts=[[f[1].real - t_all.real, f[1].imag - t_all.imag] for f in fits])


def part_c(lines):
    ref = [t for t in L.REF if max(abs(z) for z in t[1:]) < 10 * S]
    K, pos, conf = M.lift(ref); pr = points_by_rank(K); pts = list(pr.values())
    combos = [(a, b, c, d) for a in (1, -1) for b in (1, -1) for c in (1, -1) for d in (1, -1)]
    scored = sorted((fit(pts, window(sg))[0], sg) for sg in combos)
    s_ref, signs = scored[0]; win = window(signs)
    lines.append(f"PART C: window orientation from the reference tiling: signs {signs}, s* {s_ref:+.4f} (next best {scored[1][0]:+.4f}); "
                 f"true window area {sum(2.5 * (1.0 if i in (0, 3) else TAU) ** 2 * math.sin(2 * math.pi / 5) for i in range(4)):.3f}")
    seeds, _ = seeds_and_ok(); by = {x["seed"]: x for x in seeds}
    saved = {x["seed"]: x for x in json.load(open(os.path.join(HERE, "..", "perp_map", "results", "m2_worlds.json")))}
    tasks = [(s, saved[s]["kind"], ring_of(by[s]), win) for s in saved]
    with Pool(4, maxtasksperchild=1) as p:
        C = p.map(c_world, tasks)
    json.dump(C, open(os.path.join(RES, "c_worlds.json"), "w"))
    rep = all(abs(c["hull_area"] - saved[c["seed"]]["total_area"]) < 1e-6 for c in C)
    for c in C:
        rr = [round(a, 1) for a, _ in sorted(c["out_pts"])]
        lines.append(f"    {c['kind']:8s} seed {c['seed']:3d}: hull {c['hull_area']:.2f}; whole-world s* {c['s_all']:+.4f}; vertices outside "
                     f"{c['n_out']}/{c['n']} at radii {rr[:12]}{'...' if len(rr) > 12 else ''}; wedges (phase {c['wedge_phase']:.0f}) worst s* "
                     f"{c['worst_wedge']:+.4f}; random partitions all-fit {c['random_all_fit']}/{NPART}; wedge-union area {c['union_area']:.2f}")
    fil = [c for c in C if c["kind"] == "FILLABLE"]; dec = [c for c in C if c["kind"] == "DECAPOD"]
    c0 = s_ref <= TOL and all(c["s_all"] <= TOL for c in fil) and rep
    c1 = sum(c["s_all"] > TOL for c in dec)
    c2 = sum(c["s_all"] > TOL and c["worst_wedge"] <= TOL and c["random_all_fit"] < 50 for c in dec)
    lines += [f"  C0: {'PASS' if c0 else 'FAIL'}  reference and fillable worlds fit the true window (s* <= {TOL}); M2 areas reproduced: {rep}",
              f"  C1: {'HELD  ' if c1 >= 6 else 'FAILED'}  decapod worlds exceed the true window in {c1}/8 (need >= 6)",
              f"  C2: {'HELD  ' if c2 >= 6 else 'FAILED'}  every wedge fits while the whole does not, and beats random partitions, in {c2}/8 (need >= 6)"]


def main():
    os.makedirs(RES, exist_ok=True)
    parts = sys.argv[1:] or ["A", "B", "C"]
    for part in parts:
        lines = []
        {"A": part_a, "B": part_b, "C": part_c}[part](lines)
        print("\n".join(lines), flush=True)
        open(os.path.join(RES, f"report_{part}.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
