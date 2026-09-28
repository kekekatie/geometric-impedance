#!/usr/bin/env python3
"""
free_fall.py -- does anything fall? Maximal-proper-time paths beside quiet / full worldlines (PREREGISTRATION.md,
frozen before this file). Worlds regrown exactly as ../worldline_body. A test body rides the now; proper time per round
= local happening rate h(phi, r) * sqrt(1 - v^2), v = lateral speed in edges/round (c = 1). Exact DP between two events.
`python3 free_fall.py` runs everything; results/ holds cases.jsonl and the report.
"""
from __future__ import annotations
import os, sys, json, math, cmath
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "worldline_body"))
import worldline_body as W
D, L, S = W.D, W.L, W.S
BIN = 0.5; PHI_MAX = 40.0; R_WIN = 2.5; H_RAD = 1.5
NB = int(2 * PHI_MAX / BIN) + 1
PHIS = np.radians(np.linspace(-PHI_MAX, PHI_MAX, NB))
DELTAS, S0 = [8, 12, 16], [-3.0, 3.0]
RES = os.path.join(HERE, "results")


def field(h, th, exclude):
    """front radius R[b, r] and clock rate H[b, r] in the body frame (angle measured from direction th)."""
    rot = cmath.exp(-1j * math.radians(th))
    rows = [(D.cen(t) * rot / S, h["rnd"][q], q in exclude) for q, t in h["geo"].items()]
    z = np.array([c for c, _, _ in rows]); rr = np.array([x for _, x, _ in rows]); ex = np.array([e for _, _, e in rows])
    ang = np.angle(z); rad = np.abs(z); nr = int(rr.max()) + 2
    M = np.zeros((NB, nr))
    win = math.radians(R_WIN)
    for b, ph in enumerate(PHIS):
        sel = (np.abs(ang - ph) <= win) & ~ex
        for x, rd in zip(rr[sel], rad[sel]):
            M[b, x] = max(M[b, x], rd)
    R = np.maximum.accumulate(M, axis=1)
    H = np.zeros((NB, nr))
    for r in range(nr):
        sel = (rr >= r - 1) & (rr <= r + 1)
        zs = z[sel]
        pts = R[:, r] * np.exp(1j * PHIS)
        H[:, r] = (np.abs(zs[None, :] - pts[:, None]) <= H_RAD).sum(axis=1) / 3.0
    return R, H


def free_path(R, H, r1, delta, b0):
    """exact DP: maximise sum over rounds r1..r1+delta-1 of H[b, r] * sqrt(1 - v^2), v = R[b, r] * |phi' - phi| <= 1"""
    NEG = -1e18
    best = np.full(NB, NEG); best[b0] = 0.0
    back = []
    idx = np.arange(NB)
    for r in range(r1, r1 + delta):
        new = np.full(NB, NEG); arg = np.full(NB, -1)
        for b in idx[best > NEG / 2]:
            v = R[b, r] * np.abs(PHIS - PHIS[b])
            ok = v <= 1.0 + 1e-12
            gain = H[b, r] * np.sqrt(np.clip(1 - v ** 2, 0, None)) - 1e-9 * np.abs(idx - b0)
            cand = np.where(ok, best[b] + gain, NEG)
            better = cand > new
            new = np.where(better, cand, new); arg = np.where(better, b, arg)
        back.append(arg); best = new
    path = [b0]
    for arg in reversed(back):
        path.append(int(arg[path[-1]]))
    path = path[::-1]
    return path, best[b0]


def case_rows(args):
    s, ring, bi, th = args
    ctrl = W.grow(ring, W.N_CTRL)
    rk = {D.dkey(t) for t in ring}
    stripe = [t for q, t in ctrl["geo"].items() if q not in rk and W.in_stripe(D.cen(t), th)]
    c2k = W.grow(ring, W.N_ADD)
    quiet = W.grow(ring, W.N_ADD, th=th, quiet=True, rng_seed=W.SEED0 + 10 * s + bi)
    full = W.grow(ring, W.N_ADD, prelaid=stripe)
    pre = {D.dkey(t) for t in stripe}
    fields = {"CONTROL": field(c2k, th, set()), "QUIET": field(quiet, th, set()), "FULL": field(full, th, pre)}
    Rc = fields["CONTROL"][0]
    b_mid = NB // 2
    r1 = next(r for r in range(Rc.shape[1]) if Rc[b_mid, r] >= 5.0)
    out = []
    for s0 in S0:
        phi0 = s0 / Rc[b_mid, r1]
        b0 = int(np.argmin(np.abs(PHIS - phi0)))
        sgn = 1 if s0 > 0 else -1
        for delta in DELTAS:
            ex = {}; info = {}
            for arm, (R, H) in fields.items():
                r_end = r1 + delta
                if r_end >= R.shape[1]:
                    ex[arm] = None; continue
                path, tau = free_path(R, H, r1, delta, b0)
                valid = path[0] == b0 and path[-1] == b0 and all(
                    R[path[i], r1 + i] * abs(PHIS[path[i + 1]] - PHIS[path[i]]) <= 1 + 1e-9 for i in range(delta))
                disp = [sgn * R[b, r1 + i] * (PHIS[b] - PHIS[b0]) for i, b in enumerate(path[:-1])]
                k = int(np.argmax(np.abs(disp))) if disp else 0
                steps = np.sign(np.diff(path)); steps = steps[steps != 0]
                ex[arm] = float(disp[k]) if disp else 0.0
                info[arm] = dict(valid=bool(valid), tau=float(tau), edge=bool(any(b in (0, NB - 1) for b in path)),
                                 turns=int((np.diff(steps) != 0).sum()) if len(steps) > 1 else 0, path=path)
            out.append(dict(seed=s, body=bi, theta=th, side=s0, delta=delta, r1=int(r1), excursion=ex, info=info))
    return out


def main():
    os.makedirs(RES, exist_ok=True)
    tasks = [(s, ring, bi, th) for s, ring in W.pick_seeds() for bi, th in enumerate(W.THETAS)]
    with Pool(4, maxtasksperchild=1) as p:
        rows = [x for r in p.imap_unordered(case_rows, tasks) for x in r]
    with open(os.path.join(RES, "cases.jsonl"), "w") as f:
        for x in sorted(rows, key=lambda x: (x["seed"], x["body"], x["side"], x["delta"])):
            f.write(json.dumps(x) + "\n")
    report()


def report():
    X = [json.loads(l) for l in open(os.path.join(RES, "cases.jsonl"))]
    ok = [x for x in X if all(x["excursion"].get(a) is not None for a in ("CONTROL", "QUIET", "FULL"))]
    f0 = all(x["info"][a]["valid"] for x in ok for a in x["info"])
    lines = [f"cases {len(X)}, usable (all arms reach r1 + delta) {len(ok)}",
             f"  CONTROL mean excursion (signed, + = away from the body line): side -3: "
             f"{np.mean([x['excursion']['CONTROL'] for x in ok if x['side'] < 0]):+.3f}, side +3: "
             f"{np.mean([x['excursion']['CONTROL'] for x in ok if x['side'] > 0]):+.3f} edges"]
    res = {}
    for arm in ("QUIET", "FULL"):
        eff = [x["excursion"][arm] - x["excursion"]["CONTROL"] for x in ok]
        res[arm] = eff
        byd = {d: [x["excursion"][arm] - x["excursion"]["CONTROL"] for x in ok if x["delta"] == d] for d in DELTAS}
        mags = [abs(np.mean(byd[d])) for d in DELTAS]
        expo = float(np.polyfit(np.log(DELTAS), np.log(mags), 1)[0]) if all(m > 0 for m in mags) else float("nan")
        lines.append(f"{arm}: effect > 0 in {sum(e > 0 for e in eff)}/{len(eff)}, < 0 in {sum(e < 0 for e in eff)}, = 0 in "
                     f"{sum(e == 0 for e in eff)}; mean effect {np.mean(eff):+.3f} edges; by delta "
                     + ", ".join(f"{d}: {np.mean(byd[d]):+.3f}" for d in DELTAS) + f"; |mean| vs delta exponent {expo:.2f}")
        lines.append(f"    paths touching the window edge {sum(x['info'][arm]['edge'] for x in ok)}; jagged (> 2 turns) "
                     f"{sum(x['info'][arm]['turns'] > 2 for x in ok)}/{len(ok)}")
    q, f = res["QUIET"], res["FULL"]
    f1 = sum(e > 0 for e in q) >= 0.65 * len(q) and np.mean(q) > 0
    f2 = sum(e < 0 for e in f) >= 0.65 * len(f) and np.mean(f) < 0
    lines += [f"  F0: {'PASS' if f0 else 'FAIL'}  every free path valid (speed <= 1 edge/round, from A to B)",
              f"  F1: {'HELD  ' if f1 else 'FAILED'}  QUIET: path bulges away from the slow worldline (falls toward it): "
              f"{sum(e > 0 for e in q)}/{len(q)} (need >= 65%), mean {np.mean(q):+.3f}",
              f"  F2: {'HELD  ' if f2 else 'FAILED'}  FULL: path bulges toward the fast highway: {sum(e < 0 for e in f)}/{len(f)} "
              f"(need >= 65%), mean {np.mean(f):+.3f}"]
    print("\n".join(lines))
    open(os.path.join(RES, "free_fall_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if "--report" in sys.argv:
        report(); sys.exit(0)
    main()
