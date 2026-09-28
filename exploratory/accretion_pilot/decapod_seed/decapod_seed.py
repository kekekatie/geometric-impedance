#!/usr/bin/env python3
"""
decapod_seed.py -- does a decapod seed grow with no guesses? (PREREGISTRATION.md, frozen before this file.)
1. Enumerate rings of 10 half-tiles around a forbidden unit decagon (legal, every vertex completable), up to rotation.
2. Classify each ring: FILLABLE (a legal filling of the decagon exists) or DECAPOD (none).
3. Grow each ring with the patient scheduler (decagon boundary never grown), 800 tiles, 3 runs: count guesses, jams.
`python3 decapod_seed.py` runs everything; results/ holds seeds.json, runs.jsonl and the report.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gromit_check"))
import gromit_check as G
L, S = G.L, G.S
PHI = (1 + 5 ** 0.5) / 2
R_DEC = PHI * S
APO = R_DEC * math.cos(math.pi / 10)
V = [R_DEC * cmath.exp(1j * math.radians(18 + 36 * k)) for k in range(10)]
EDGES = [(V[k], V[(k + 1) % 10]) for k in range(10)]
AREA_DEC = 10 * 0.5 * R_DEC ** 2 * math.sin(math.radians(36))
N_ADD, RUNS, SEED0, STALL = 800, 3, 20261050, 20000
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3
area = lambda t: abs(L.orient(*t[1:])) / 2
dkey = lambda t: (t[0], L.key(t[1]), L.key(t[2]), L.key(t[3]))      # decoration-aware tile identity


def candidates(P, p, q, r):
    """Patch.candidates, but keeping BOTH decorations of a tile position. laying_the_tiling's version keys its output
    by canon(), which ignores the A/B/C roles, so the two mirror decorations of an isosceles half-tile at the same place
    collapse to one (see PREREGISTRATION.md, changes before the first run)."""
    out = {}
    for (c, o), (tc, A, B, C) in L.TEMPL.items():
        Pp = {"A": A, "B": B, "C": C}
        for X, Y, Z in (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"), ("B", "A", "C"), ("C", "B", "A"), ("A", "C", "B")):
            x, y, z = Pp[X], Pp[Y], Pp[Z]
            if abs(abs(y - x) - abs(q - p)) > 1e-6:
                continue
            a = (q - p) / (y - x); zz = p + a * (z - x)
            if L.orient(p, q, zz) * L.orient(p, q, r) >= 0:
                continue
            img = {X: p, Y: q, Z: zz}; nt = (tc, img["A"], img["B"], img["C"])
            if P.legal(nt):
                out[dkey(nt)] = nt
    return list(out.values())


def edge_sig(t, p, q):
    return (t[0],) + tuple((round(((z - p) / (q - p)).real, 3), round(((z - p) / (q - p)).imag, 3)) for z in t[1:])


def enumerate_rings():
    rings = []

    def dfs(i, chosen):
        if i == 10:
            rings.append(list(chosen)); return
        P = L.Patch(chosen)
        p, q = EDGES[i]
        for t in candidates(P, p, q, 0j):
            if abs(cen(t)) <= APO or not P.legal(t) or not G.strong(P, t):
                continue
            dfs(i + 1, chosen + [t])
    dfs(0, [])
    seen, uniq = set(), []
    for ring in rings:
        sig = tuple(edge_sig(t, *EDGES[i]) for i, t in enumerate(ring))
        canon = min(sig[j:] + sig[:j] for j in range(10))
        if canon not in seen:
            seen.add(canon); uniq.append(ring)
    return len(rings), uniq


def fillings(ring, limit=50):
    """exhaustive DFS over fillings of the decagon interior; returns the number found (capped at limit)"""
    found = [0]

    def dfs(tiles, got):
        if found[0] >= limit:
            return
        if got >= AREA_DEC - 1e-9:
            Q = L.Patch(tiles)
            if all(L.star(l) in L.STARS for l in Q.V.values() if abs(sum(d for _, d, _ in l) - 2 * math.pi) < 1e-6):
                found[0] += 1
            return
        Q = L.Patch(tiles)
        best = None
        for e in Q.frontier():
            if abs((e[0] + e[1]) / 2) > APO + 1e-6:
                continue
            cs = [t for t in candidates(Q, *e[:3]) if abs(cen(t)) < APO and Q.legal(t)]
            if best is None or len(cs) < len(best):
                best = cs
            if not cs:
                return                                    # an inside edge nothing fits: dead end
        if best is None:
            return
        for t in best:
            dfs(tiles + [t], got + area(t))
    dfs(list(ring), 0.0)
    return found[0]


def grow(ring, rs):
    rng = random.Random(rs)
    P = L.Patch(ring); n0 = len(P.tris); r = 0; guesses = []; status = "ok"; jam = None
    while len(P.tris) - n0 < N_ADD:
        r += 1
        if r > STALL:
            status = "STALL"; break
        fr = [e for e in P.frontier() if abs((e[0] + e[1]) / 2) > APO + 1e-6]
        forced = {}
        for e in fr:
            cs = candidates(P, *e[:3])
            if not cs:
                status = "JAM"; jam = (e[0] + e[1]) / 2; break
            if len(cs) == 1:
                forced.setdefault(dkey(cs[0]), cs[0])
        if status == "JAM":
            break
        legal = [t for t in forced.values() if P.legal(t)]
        if forced and not legal:
            status = "STUCK"; break
        placed = 0
        for t in legal:
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed == 0:
            if forced:
                continue
            cs = sorted(candidates(P, *fr[0][:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
            t = rng.choice(cs); P.add(t)
            m = (fr[0][0] + fr[0][1]) / 2
            guesses.append(dict(round=r, x=round(m.real / S, 3), y=round(m.imag / S, 3), n_cands=len(cs)))
    return dict(status=status, rounds=r, guesses=guesses, tiles=len(P.tris) - n0,
                jam=[round(jam.real / S, 3), round(jam.imag / S, 3)] if jam is not None else None)


def classify(args):
    s, ring = args
    return s, fillings(ring)


def grow_task(args):
    s, k, ring, kind = args; t0 = time.time()
    out = grow(ring, SEED0 + 100 * s + k)
    out.update(seed=s, run=k, kind=kind, seconds=round(time.time() - t0))
    return out


def genuine_ring():
    """a decagon found in the reference tiling, with its ring of 10 outside half-tiles, moved to the origin"""
    verts = {L.key(z): z for t in L.REF for z in t[1:] if abs(z) < 6 * S}
    for c in verts.values():
        ins = [t for t in L.REF if abs(cen(t) - c) < APO]
        vk = {L.key(z) for t in ins for z in t[1:]}
        if abs(sum(area(t) for t in ins) - AREA_DEC) < 1e-9 and all(L.key(c + v) in vk for v in V):
            ring = []
            for p, q in EDGES:
                for t in L.REF:
                    ks = {L.key(z) for z in t[1:]}
                    if L.key(c + p) in ks and L.key(c + q) in ks and abs(cen(t) - c) > APO:
                        ring.append(tuple([t[0]] + [z - c for z in t[1:]]))
            return ring
    return None


def main():
    os.makedirs(RES, exist_ok=True)
    t0 = time.time()
    n_all, rings = enumerate_rings()
    g = genuine_ring()
    sig = lambda r: tuple(edge_sig(t, *EDGES[i]) for i, t in enumerate(r))
    allrot = {sig(r)[j:] + sig(r)[:j] for r in rings for j in range(10)}
    q0b = g is not None and sig(g) in allrot and fillings(g) >= 1
    print(f"Q0b (genuine reference decagon ring is enumerated and fillable): {'PASS' if q0b else 'FAIL'}", flush=True)
    assert q0b
    print(f"rings: {n_all} (with rotations), {len(rings)} up to rotation; {time.time() - t0:.0f} s", flush=True)
    with Pool(4) as p:
        fill = dict(p.map(classify, list(enumerate(rings))))
    kinds = {s: ("FILLABLE" if fill[s] > 0 else "DECAPOD") for s in range(len(rings))}
    json.dump([dict(seed=s, kind=kinds[s], n_fillings=fill[s], tiles=[[t[0]] + [[z.real, z.imag] for z in t[1:]] for t in ring])
               for s, ring in enumerate(rings)], open(os.path.join(RES, "seeds.json"), "w"))
    print(f"fillable {sum(k == 'FILLABLE' for k in kinds.values())}, decapod {sum(k == 'DECAPOD' for k in kinds.values())}; "
          f"fillings per fillable seed {[fill[s] for s in kinds if kinds[s] == 'FILLABLE']}", flush=True)
    tasks = [(s, k, rings[s], kinds[s]) for s in range(len(rings)) for k in range(RUNS)]
    out = []
    with Pool(4, maxtasksperchild=4) as p:
        for res in p.imap_unordered(grow_task, tasks):
            out.append(res)
            print(f"seed {res['seed']} ({res['kind']}) run {res['run']}: {res['status']}, {res['tiles']} tiles, "
                  f"{len(res['guesses'])} guesses, {res['seconds']} s", flush=True)
    with open(os.path.join(RES, "runs.jsonl"), "w") as f:
        for r in sorted(out, key=lambda r: (r["seed"], r["run"])):
            f.write(json.dumps(r) + "\n")
    report(kinds, fill)


def report(kinds=None, fill=None):
    seeds = json.load(open(os.path.join(RES, "seeds.json")))
    kinds = {x["seed"]: x["kind"] for x in seeds}; fill = {x["seed"]: x["n_fillings"] for x in seeds}
    R = [json.loads(l) for l in open(os.path.join(RES, "runs.jsonl"))]
    by = {}
    for r in R:
        by.setdefault(r["seed"], []).append(r)
    dec = [s for s in kinds if kinds[s] == "DECAPOD"]; fil = [s for s in kinds if kinds[s] == "FILLABLE"]
    dec_ok = [s for s in dec if all(r["status"] == "ok" for r in by[s])]
    dec_zero = [s for s in dec_ok if all(len(r["guesses"]) == 0 for r in by[s])]
    fil_guess = [s for s in fil if all(len(r["guesses"]) >= 1 for r in by[s])]
    q0 = bool(fil) and bool(dec)
    q1 = bool(dec_ok) and len(dec_zero) >= 0.8 * len(dec_ok)
    q2 = bool(fil) and len(fil_guess) == len(fil)
    lines = [f"seeds (rings up to rotation): {len(kinds)}; FILLABLE {len(fil)}, DECAPOD {len(dec)} "
             f"(Conway's decagon fillings/decapods: 62)",
             f"  fillings per FILLABLE seed: {[fill[s] for s in fil]}"]
    for kind, ss in (("FILLABLE", fil), ("DECAPOD", dec)):
        rs = [r for s in ss for r in by[s]]
        lines.append(f"  {kind}: runs {len(rs)}, jammed {sum(r['status'] == 'JAM' for r in rs)}, other failures "
                     f"{sum(r['status'] not in ('ok', 'JAM') for r in rs)}; guesses per run "
                     f"{sorted(len(r['guesses']) for r in rs)}")
        for s in ss:
            lines.append(f"      seed {s}: " + "; ".join(f"{r['status']} {r['tiles']} tiles {len(r['guesses'])} guesses"
                                                        + (f" jam at {r['jam']}" if r['jam'] else "") for r in by[s]))
    lines += [f"  Q0: {'PASS' if q0 else 'FAIL'}  at least one FILLABLE and one DECAPOD seed",
              f"  Q1: {'HELD  ' if q1 else 'FAILED'}  DECAPOD seeds (none of whose runs jam) needing zero guesses: "
              f"{len(dec_zero)}/{len(dec_ok)} (need >= 80%)",
              f"  Q2: {'HELD  ' if q2 else 'FAILED'}  FILLABLE seeds needing >= 1 guess in every run: {len(fil_guess)}/{len(fil)}"]
    print("\n".join(lines))
    open(os.path.join(RES, "decapod_seed_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if "--report" in sys.argv:
        report(); sys.exit(0)
    main()
