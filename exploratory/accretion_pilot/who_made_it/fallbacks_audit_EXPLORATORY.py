#!/usr/bin/env python3
"""EXPLORATORY audit (Astra's check, after the registered run): in heldout.py, a REVEAL world picks the option whose
piece of F contains its hidden point; if neither or both contain it, the code falls back to a coin. heldout.py never
counted how often that happened. This replays the 96 REVEAL worlds (training and held out) exactly, with the same code
path and random stream, and counts: two-option choices, fallbacks with 0 or 2 pieces containing the point, and choices
with other than two options. It also checks the replay reproduces the stored worlds. Writes
results/fallbacks_audit_EXPLORATORY.txt."""
import os, json, random, collections
from multiprocessing import Pool
import heldout as H
W, Sl, F_, L, D, S = H.W, H.Sl, H.F_, H.L, H.D, H.S


def replay(args):
    mode, centre, stream = args
    rng = random.Random(stream)
    P = L.Patch(L.seed_patch(centre, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris)
    t0 = W.sample_in(Sl.region(Sl.constraints(P.tris, rank)), rng)
    c = collections.Counter(); status = "ok"
    while len(P.tris) - n0 < W.N_ADD:
        st, placed, anyf = F_.step(P)
        if st == "JAM":
            status = "JAM"; break
        if placed or anyf:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) != 2:
            c[f"options_{len(cs)}"] += 1; P.add(rng.choice(cs)); continue
        c["two"] += 1
        base = list(P.tris)
        cms = [Sl.constraints(list(F_.sibling(base, x)[0].tris), rank) for x in cs]
        inside = [W.contains(cm, t0) for cm in cms]
        if sum(inside) == 1:
            k = inside.index(True)
        else:
            c[f"fallback_{sum(inside)}_inside"] += 1; k = rng.randrange(2)
        P.add(cs[k])
    return dict(stream=stream, status=status, counts=dict(c))


if __name__ == "__main__":
    C = H.centres96()
    jobs = [("REVEAL", C[k], 20261700 + k) for k in range(48)] + [("REVEAL", C[48 + k], 20261900 + k) for k in range(48)]
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(replay, jobs)
    stored = json.load(open(os.path.join(H.RES, "heldout_worlds.json")))
    ref = {w["stream"]: w for w in stored["train"] + stored["test"] if w["mode"] == "REVEAL"}
    match = sum(r["counts"].get("two", 0) == ref[r["stream"]]["choices"] and r["status"] == ref[r["stream"]]["status"] for r in R)
    tot = collections.Counter()
    for r in R:
        tot.update(r["counts"])
    hit = [r["stream"] for r in R if any(k.startswith("fallback") for k in r["counts"])]
    lines = [f"EXPLORATORY audit of REVEAL fallbacks in heldout.py: {len(R)} REVEAL worlds replayed "
             f"(replay matches stored choice count and status in {match}/{len(R)})",
             f"  totals: {dict(tot)}",
             f"  worlds with any fallback: {len(hit)} {hit}"]
    print("\n".join(lines))
    open(os.path.join(H.RES, "fallbacks_audit_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
