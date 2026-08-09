import csv, numpy as np
# Their WR metric: activation-weighted mean distance from the blob centre.
# Question: how much of the zero-memory "Penrose beats square by ~0.12"
# is just the two point sets having different SHAPES, before any dynamics run?
# Test with UNIFORM activation - i.e. the fully-diffused state, no dynamics at all.

# Square lattice: 25x25 on [-1,1]^2  (their spec)
g = np.linspace(-1, 1, 25)
sq = np.array([[x, y] for x in g for y in g])

# Penrose: their real substrate, innermost points, rescaled to fit [-1,1]^2.
# "cropped to the inner 70%" produces a DISC of points, not a square.
rows = list(csv.DictReader(open("/home/user/geometric-impedance/substrates/real_penrose_lift.csv",
                                encoding="utf-8-sig")))
P = np.array([[float(r["x"]), float(r["y"])] for r in rows])
P -= P.mean(0)
P = P[np.argsort(np.linalg.norm(P, axis=1))[:611]]     # 611 vertices, as in the paper
P = P / np.abs(P).max()                                 # rescale into [-1,1]^2

def WR(pts, centre):
    return np.linalg.norm(pts - centre, axis=1).mean()   # uniform activation

print(f"square lattice : {len(sq)} pts, max |coord| {np.abs(sq).max():.3f}")
print(f"penrose disc   : {len(P)} pts, max |coord| {np.abs(P).max():.3f}")
print()
print("WR under UNIFORM activation (no dynamics, pattern fully diffused):")
print(f"{'blob centre':>16} {'square':>8} {'penrose':>8} {'gap':>8}")
for c in [(0,0), (0.3,0.3), (-0.4,0.2), (0.5,-0.5)]:
    c = np.array(c)
    a, b = WR(sq, c), WR(P, c)
    print(f"{str(tuple(c)):>16} {a:8.4f} {b:8.4f} {a-b:8.4f}")
print()
print("paper's reported zero-memory gap (Penrose vs square): ~0.12")
