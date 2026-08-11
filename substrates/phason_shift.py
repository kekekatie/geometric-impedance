import sys, numpy as np
sys.path.insert(0,"/home/user/geometric-impedance/substrates")
from generate_ab import generate, build_edges

def patch(offset, extent=22):
    lifts, par, perp = generate(extent, np.array(offset))
    E = build_edges(lifts)
    keys = {tuple(k) for k in lifts}                    # lift vector = canonical id
    idx  = {tuple(k): i for i, k in enumerate(lifts)}
    Ek   = {(tuple(lifts[u]), tuple(lifts[v])) for u, v in E}
    return keys, Ek, len(lifts)

base_off = (0.1381, 0.0927)
V0, E0, n0 = patch(base_off)
print(f"reference AB patch: {n0} vertices, {len(E0)} edges\n")
print(f"{'phason shift':>13} {'vertices':>9} {'V jaccard':>10} {'E jaccard':>10} {'flipped':>8}")
for d in [0.0, 0.002, 0.01, 0.05, 0.15, 0.40]:
    V1, E1, n1 = patch((base_off[0] + d, base_off[1]))
    vj = len(V0 & V1) / len(V0 | V1)
    ej = len(E0 & E1) / len(E0 | E1)
    print(f"{d:13.3f} {n1:9d} {vj:10.4f} {ej:10.4f} {len(V0 ^ V1):8d}")

print("\nfor comparison, the perturbation used in the v3 audit:")
print(f"{'5E random rewiring':>13} {'':>9} {'1.0000':>10} {'0.0001':>10}   (vertices untouched, graph annihilated)")
