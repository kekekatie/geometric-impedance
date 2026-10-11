#!/usr/bin/env python3
"""
heldout.py -- PREREGISTRATION_heldout.md (frozen before this file). Does one finished world carry evidence of how it
was made? Finished-patch measurements only: M1 log leftover wiggle room, M2 vertex-type frequencies, M3 kind of F
(empty -> SELECT). Logistic classifiers fit on 48 training seeds (both modes), frozen, scored on 48 held-out seeds.
`python3 heldout.py`.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, collections
from multiprocessing import Pool
import numpy as np
from scipy.optimize import minimize
from scipy.stats import binomtest

import who_made_it as W
sys.path.insert(0, os.path.join(W.HERE, "..", "slack"))
import classify_EXPLORATORY as CL
Sl, F_, L, D, S = W.Sl, W.F_, W.L, W.D, W.S
RES = W.RES


def centres96():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[:96]


def world(args):
    mode, centre, stream = args
    rng = random.Random(stream)
    P = L.Patch(L.seed_patch(centre, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris)
    t0 = W.sample_in(Sl.region(Sl.constraints(P.tris, rank)), rng) if mode == "REVEAL" else None
    status = "ok"; n_choices = 0
    while len(P.tris) - n0 < W.N_ADD:
        st, placed, anyf = F_.step(P)
        if st == "JAM":
            status = "JAM"; break
        if placed or anyf:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) != 2:
            P.add(rng.choice(cs)); continue
        n_choices += 1
        if mode == "SELECT":
            k = rng.randrange(2)
        else:
            base = list(P.tris)
            cms = [Sl.constraints(list(F_.sibling(base, c)[0].tris), rank) for c in cs]
            inside = [W.contains(cm, t0) for cm in cms]
            k = inside.index(True) if sum(inside) == 1 else rng.randrange(2)
        P.add(cs[k])
    cm = Sl.constraints(P.tris, rank)
    kind, _ = CL.classify(cm)
    area = Sl.area(Sl.region(cm)) if kind == "polygon" else 0.0
    return dict(mode=mode, stream=stream, status=status, kind=kind, area=area, choices=n_choices, types=W.vertex_types(P))


def fit_logistic(X, y, lam=1e-3):
    mu, sd = X.mean(0), X.std(0) + 1e-12; Z = (X - mu) / sd
    Z1 = np.c_[np.ones(len(Z)), Z]
    def nll(w):
        z = Z1 @ w
        return np.sum(np.logaddexp(0, z) - y * z) + lam * np.sum(w[1:] ** 2)
    w = minimize(nll, np.zeros(Z1.shape[1]), method="BFGS").x
    return lambda Xn: (np.c_[np.ones(len(Xn)), (Xn - mu) / sd] @ w) > 0


def main():
    C = centres96()
    train = [("SELECT", C[k], 20261600 + k) for k in range(48)] + [("REVEAL", C[k], 20261700 + k) for k in range(48)]
    test = [("SELECT", C[48 + k], 20261800 + k) for k in range(48)] + [("REVEAL", C[48 + k], 20261900 + k) for k in range(48)]
    with Pool(4, maxtasksperchild=1) as p:
        TR = p.map(world, train); TE = p.map(world, test)
    json.dump(dict(train=TR, test=TE), open(os.path.join(RES, "heldout_worlds.json"), "w"),
              default=lambda o: o.item() if hasattr(o, "item") else str(o))
    types = sorted({t for w in TR + TE for t in w["types"]})
    m1 = lambda w: [math.log(w["area"])]
    m2 = lambda w: [w["types"].get(t, 0) / max(1, sum(w["types"].values())) for t in types]
    live = lambda ws: [w for w in ws if w["kind"] != "empty" and w["area"] > 0]
    lines = []
    for name, feat in (("A (M1 leftover wiggle room)", m1), ("B (M2 vertex frequencies)", m2), ("C (M1 + M2)", lambda w: m1(w) + m2(w))):
        tr = live(TR)
        Xtr = np.array([feat(w) for w in tr]); ytr = np.array([w["mode"] == "SELECT" for w in tr], float)
        clf = fit_logistic(Xtr, ytr)
        correct = 0
        for w in TE:
            if w["kind"] == "empty" or w["area"] <= 0:
                pred = True                                    # M3 rule: empty F -> SELECT
            else:
                pred = bool(clf(np.array([feat(w)]))[0])
            correct += pred == (w["mode"] == "SELECT")
        pv = binomtest(correct, len(TE), 0.5, alternative="greater").pvalue
        lines.append(f"  classifier {name}: held-out accuracy {correct}/{len(TE)} = {correct / len(TE):.3f} (one-sided binomial p {pv:.4f})")
        if name.startswith("A"):
            accA, pA = correct / len(TE), pv
        if name.startswith("B"):
            accB = correct / len(TE)
    emp = [w for w in TE if w["kind"] == "empty"]
    lines = [f"training: jams SELECT {sum(w['status'] == 'JAM' for w in TR if w['mode'] == 'SELECT')}, REVEAL "
             f"{sum(w['status'] == 'JAM' for w in TR if w['mode'] == 'REVEAL')}; held out: jams SELECT "
             f"{sum(w['status'] == 'JAM' for w in TE if w['mode'] == 'SELECT')}, REVEAL {sum(w['status'] == 'JAM' for w in TE if w['mode'] == 'REVEAL')}",
             f"F kinds (held out): {dict(collections.Counter((w['mode'], w['kind']) for w in TE))}"] + lines
    lines += [f"  H1: {'HELD  ' if pA < 0.05 else 'FAILED'}  classifier A above chance on held-out seeds (p {pA:.4f})",
              f"  H2: {'HELD  ' if accB < 0.60 else 'FAILED'}  classifier B accuracy {accB:.3f} (need < 0.60)",
              f"  H3: {'HELD  ' if all(w['mode'] == 'SELECT' for w in emp) else 'FAILED'}  held-out worlds with empty F: {len(emp)}, all SELECT: "
              f"{all(w['mode'] == 'SELECT' for w in emp)}"]
    for mode in ("SELECT", "REVEAL"):
        a = [math.log(w["area"]) for w in TR + TE if w["mode"] == mode and w["area"] > 0]
        c = [w["choices"] for w in TR + TE if w["mode"] == mode]
        lines.append(f"  reported: {mode} log leftover area median {np.median(a):.2f} (IQR {np.quantile(a, .25):.2f} to {np.quantile(a, .75):.2f}); "
                     f"choices per world median {np.median(c):.0f}")
    print("\n".join(lines))
    open(os.path.join(RES, "heldout_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
