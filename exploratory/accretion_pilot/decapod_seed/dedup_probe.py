#!/usr/bin/env python3
"""dedup_probe.py -- does laying_the_tiling.Patch.candidates (which keys candidates by canon(), ignoring the A/B/C roles)
ever hide a legal decoration during ordinary growth? Patient growth, local_deciders seed 0, 600 tiles."""
import sys, os, random
sys.path.insert(0, "/home/user/geometric-impedance/exploratory/accretion_pilot/local_deciders")
import local_deciders as LD
L, S = LD.L, LD.S
from laying_the_tiling import TEMPL, orient

def all_candidates(P, p, q, r):
    out = {}
    for (c, o), (tc, A, B, C) in TEMPL.items():
        Pp = {"A": A, "B": B, "C": C}
        for X, Y, Z in (("A","B","C"),("B","C","A"),("C","A","B"),("B","A","C"),("C","B","A"),("A","C","B")):
            x, y, z = Pp[X], Pp[Y], Pp[Z]
            if abs(abs(y - x) - abs(q - p)) > 1e-6: continue
            a = (q - p) / (y - x); zz = p + a * (z - x)
            if orient(p, q, zz) * orient(p, q, r) >= 0: continue
            img = {X: p, Y: q, Z: zz}; nt = (tc, img["A"], img["B"], img["C"])
            if P.legal(nt):
                out[(tc, L.key(nt[1]), L.key(nt[2]), L.key(nt[3]))] = nt
    return list(out.values())

# patient growth, seed 0 of local_deciders, check every frontier edge in every round until 1500 tiles
rng = random.Random(LD.SEED0 + 0)
P = L.Patch(L.seed_patch(0j, 3 * S)); n0 = len(P.tris); r = 0
edges = lost = forced_but_two = forced = 0
while len(P.tris) - n0 < 600:
    r += 1
    fr = P.frontier(); fz = {}
    for e in fr:
        cs = P.candidates(*e[:3]); full = all_candidates(P, *e[:3])
        edges += 1; lost += len(full) > len(cs)
        if len(cs) == 1:
            forced += 1; forced_but_two += len(full) > 1
            fz.setdefault(L.canon(cs[0]), cs[0])
    placed = 0
    for t in fz.values():
        if P.legal(t): P.add(t); placed += 1
    if not placed:
        cs = sorted(P.candidates(*fr[0][:3]), key=lambda u: sorted(L.canon(u)[1])); P.add(rng.choice(cs))
print(f"rounds {r}: frontier-edge checks {edges}; edges where dedup hid a legal decoration {lost}; forced edges {forced}, of which really had 2+ decorated options {forced_but_two}")
