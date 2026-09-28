#!/usr/bin/env python3
"""
speed_of_light.py -- how fast does influence travel in a Gromit world? (PREREGISTRATION.md, frozen before this file.)
Twin histories: A grows normally (FAST arm, WAIT scheduler, ../continuation_choices); B replays A up to guess j and
lays an alternative there. Within the forcing epoch (until either history's next guess / B's jam / the size cap)
the difference can travel only through the local rules. Measures reach R(t), sideways width W(t), front speed,
elongation of the difference. Incremental: results/perturbations.jsonl; `--summary` evaluates Z1, Z2, L1-L3.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "continuation_choices"))
import continuation_choices as CC
SZ, L = CC.SZ, CC.L
S = L.SCALE_LEN
N_ADD, RUNS, SEED0 = CC.N_ADD, 12, 20261020
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "perturbations.jsonl")
cen = SZ.centroid


def grow_hist(k, override=None):
    """CC.grow('FAST', ...) re-implemented with an optional override (j, alt): at guess j, lay the alt-th candidate
    that A did not choose (the rng draw is still made, so the stream stays aligned). Returns the full history."""
    rng = random.Random(SEED0 + k)
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris)
    rnd = {L.canon(t): 0 for t in seed}; geo = {L.canon(t): t for t in seed}
    r = 0; guesses = []; status = "ok"; jam = None
    while len(P.tris) - n0 < N_ADD:
        r += 1
        if r > CC.STALL:
            status = "STALL"; break
        fr = P.frontier(); forced = {}; dead = None
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                dead = e; break
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), cs[0])
        if dead is not None:
            status = "JAM"; jam = (dead[0] + dead[1]) / 2; break
        legal = [(q, t) for q, t in forced.items() if P.legal(t)]
        if forced and not legal:
            status = "STUCK"; break
        placed = 0
        for q, t in legal:
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); rnd[q] = r; geo[q] = t; placed += 1
        if placed == 0:
            if forced:
                continue
            cs = sorted(P.candidates(*fr[0][:3]), key=lambda u: sorted(L.canon(u)[1]))
            t = rng.choice(cs); n_alt = len(cs) - 1
            if override is not None and len(guesses) == override[0]:
                t = [u for u in cs if L.canon(u) != L.canon(t)][override[1]]
            mid = (fr[0][0] + fr[0][1]) / 2
            guesses.append(dict(round=r, mid=[mid.real, mid.imag], n_alt=n_alt))
            P.add(t); rnd[L.canon(t)] = r; geo[L.canon(t)] = t
    capped = len(P.tris) - n0 >= N_ADD
    return dict(rnd=rnd, geo=geo, guesses=guesses, status=status, jam=jam, rounds=r, capped=capped, P=P)


def last_complete_round(h):
    """The last round whose placements are complete in this history (a capped or jammed final round is partial)."""
    return h["rounds"] - 1 if (h["capped"] or h["status"] != "ok") else h["rounds"]


def front_mean_radius(hist, r, ang):
    P = L.Patch([hist["geo"][q] for q, x in hist["rnd"].items() if x <= r])
    ms = [(e[0] + e[1]) / 2 for e in P.frontier()]
    ms = [m for m in ms if abs(cmath.phase(m / cmath.exp(1j * ang))) <= math.radians(20)]
    return (sum(abs(m) for m in ms) / len(ms) / S) if ms else float("nan")


def compare(A, B, r0, p0, t_end):
    """R(t), W(t) and D_t (as centroids, in edges) for t = 0 .. t_end - r0; plus the Z2 check."""
    ang = cmath.phase(p0); R, W, z2 = [], [], True; Dlast = []
    keys = set(A["rnd"]) | set(B["rnd"])
    for r in range(r0, t_end + 1):
        D = [q for q in keys if (A["rnd"].get(q, math.inf) <= r) != (B["rnd"].get(q, math.inf) <= r)]
        for q in D:
            first = min(A["rnd"].get(q, math.inf), B["rnd"].get(q, math.inf))
            z2 &= first >= r0
        cs = [cen((A["geo"].get(q) or B["geo"][q])) for q in D]
        R.append(max((abs(c - p0) / S for c in cs), default=0.0))
        W.append(max((abs(c) * abs(cmath.phase(c / cmath.exp(1j * ang))) / S for c in cs), default=0.0))
        Dlast = [(c.real / S, c.imag / S) for c in cs]
    return R, W, z2, Dlast


def task(args):
    k, j, alt = args; t0 = time.time()
    A = grow_hist(k)
    B = grow_hist(k, override=(j, alt))
    g = A["guesses"][j]; r0 = g["round"]; p0 = complex(*g["mid"])
    a_next = A["guesses"][j + 1]["round"] - 1 if j + 1 < len(A["guesses"]) else last_complete_round(A)
    b_next = B["guesses"][j + 1]["round"] - 1 if j + 1 < len(B["guesses"]) else last_complete_round(B)
    end = min(a_next, b_next)
    reason = ("B jam" if (end == b_next and B["status"] == "JAM" and j + 1 >= len(B["guesses"])) else
              "cap" if end == last_complete_round(A) or end == last_complete_round(B) else "next guess")
    R, W, z2, Dlast = compare(A, B, r0, p0, end)
    T = end - r0
    dmax = max(max(abs(t[1] - t[2]), abs(t[2] - t[3]), abs(t[3] - t[1])) for t in A["geo"].values()) / S
    steps = [R[0]] + [R[i] - R[i - 1] for i in range(1, len(R))]
    z1 = all(s <= 2 * dmax + 1e-9 for s in steps)
    v_f = ((front_mean_radius(A, end, cmath.phase(p0)) - front_mean_radius(A, r0 - 1, cmath.phase(p0))) / T) if T > 0 else float("nan")
    # after the window (exploratory): the scheduler's non-local channel
    after_end = min(last_complete_round(A), last_complete_round(B))
    Ra, _, _, _ = compare(A, B, r0, p0, after_end) if after_end > end else (R, W, z2, Dlast)
    after_steps = [Ra[i] - Ra[i - 1] for i in range(len(R), len(Ra))]
    return dict(run=k, guess=j, alt=alt, r0=r0, p0=[p0.real / S, p0.imag / S], T=T, end_reason=reason,
                B_status=B["status"], B_jam=[B["jam"].real / S, B["jam"].imag / S] if B["jam"] is not None else None,
                B_jam_round=B["rounds"] if B["status"] == "JAM" else None,
                R=[round(x, 4) for x in R], W=[round(x, 4) for x in W], D_T=[[round(a, 3), round(b, 3)] for a, b in Dlast],
                d_max=dmax, z1=z1, z2=z2, max_step=max(steps) if steps else 0.0, v_f=v_f,
                after_rounds=len(after_steps), after_max_step=max(after_steps, default=0.0),
                after_final_R=Ra[-1] if Ra else 0.0, seconds=round(time.time() - t0))


def summary():
    import numpy as np
    X = [json.loads(l) for l in open(OUT)]
    lines = [f"perturbations: {len(X)} over {len({x['run'] for x in X})} runs; window end reasons "
             f"{ {r: sum(x['end_reason'] == r for x in X) for r in ('next guess', 'B jam', 'cap')} }"]
    jams = [x for x in X if x["end_reason"] == "B jam"]
    lines.append(f"  B jammed inside the window: {len(jams)} "
                 + str([(x['run'], x['guess'], x['B_jam_round'] - x['r0'], [round(v, 2) for v in x['B_jam']]) for x in jams]))
    z1 = all(x["z1"] for x in X); z2 = all(x["z2"] for x in X)
    dmax = X[0]["d_max"]
    lines.append(f"  d_max (tile diameter) = {dmax:.3f} edges; largest per-round reach step inside windows "
                 f"{max(x['max_step'] for x in X):.3f} edges ({max(x['max_step'] for x in X) / dmax:.2f} x d_max)")
    el = [x for x in X if x["T"] >= 6 and len(x["D_T"]) >= 5]
    alphas = []
    for x in el:
        ts = [t for t in range(1, x["T"] + 1) if x["W"][t] > 0]
        if len(ts) >= 3:
            alphas.append(float(np.polyfit(np.log(ts), np.log([x["W"][t] for t in ts]), 1)[0]))
    news = [x["W"][x["T"]] / x["T"] for x in el]
    vf = [x["v_f"] for x in el if not math.isnan(x["v_f"])]
    L1 = bool(alphas) and np.median(alphas) >= 0.8
    L2 = bool(news) and bool(vf) and np.median(news) >= 3 * np.median(vf)
    big = [x for x in X if len(x["D_T"]) >= 10]
    elong = []
    for x in big:
        pts = np.array(x["D_T"]); ev = np.sort(np.linalg.eigvalsh(np.cov(pts.T)))
        elong.append(float(np.sqrt(ev[1] / ev[0])) if ev[0] > 1e-12 else float("inf"))
    L3 = bool(elong) and np.mean([e >= 3 for e in elong]) >= 0.5
    lines += [f"  Z1: {'PASS' if z1 else 'FAIL'}  influence never jumps more than 2 x d_max per round inside the window",
              f"  Z2: {'PASS' if z2 else 'FAIL'}  no tile laid before the perturbation ever differs",
              f"  L1: {'HELD  ' if L1 else 'FAILED'}  light-like spread: median alpha {np.median(alphas) if alphas else float('nan'):.2f} "
              f"(need >= 0.8); n = {len(alphas)}; alphas {sorted(round(a, 2) for a in alphas)}",
              f"  L2: {'HELD  ' if L2 else 'FAILED'}  sideways news speed median {np.median(news) if news else float('nan'):.3f} vs local front speed "
              f"median {np.median(vf) if vf else float('nan'):.3f} edges/round (need >= 3x; ratio "
              f"{(np.median(news) / np.median(vf)) if news and vf and np.median(vf) != 0 else float('nan'):.1f}); n = {len(el)}",
              f"  L3: {'HELD  ' if L3 else 'FAILED'}  rays: elongation >= 3 in {np.mean([e >= 3 for e in elong]) if elong else float('nan'):.2f} "
              f"(need >= 0.5); n = {len(elong)}; elongations {sorted(round(e, 1) for e in elong)}",
              f"  window lengths T: {sorted(x['T'] for x in X)}; |D_T|: {sorted(len(x['D_T']) for x in X)}",
              f"  (after the window, exploratory) largest per-round reach step {max((x['after_max_step'] for x in X), default=0):.2f} edges; "
              f"perturbations with a step > 2 x d_max after the window: {sum(x['after_max_step'] > 2 * dmax + 1e-9 for x in X)}/{len(X)}"]
    print("\n".join(lines))
    open(os.path.join(RES, "speed_of_light_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {(json.loads(l)["run"], json.loads(l)["guess"], json.loads(l)["alt"]) for l in open(OUT)} if os.path.exists(OUT) else set()
    with Pool(4, maxtasksperchild=1) as p:                 # list every perturbation from each run's history A
        hists = p.map(grow_hist, range(RUNS))
    todo = [(k, j, a) for k, h in enumerate(hists) for j, g in enumerate(h["guesses"]) for a in range(g["n_alt"])
            if (k, j, a) not in done]
    del hists
    with Pool(4, maxtasksperchild=1) as p:
        for res in p.imap_unordered(task, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"run {res['run']} guess {res['guess']} alt {res['alt']}: T {res['T']} ({res['end_reason']}), "
                  f"|D_T| {len(res['D_T'])}, reach {res['R'][-1]:.2f}, {res['seconds']} s", flush=True)
    summary()
