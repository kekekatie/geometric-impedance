import numpy as np
# The paper's falsification test runs native-vs-rewired on PENROSE ONLY.
# The square lattice is never given the same test. So: does a periodic
# substrate ALSO lose its memory benefit when its edges are scrambled?
# If yes, the 20:1 ratio is about spatial locality, not aperiodicity.

rng_global = np.random.default_rng(0)

def square_lattice(k=25):
    g = np.linspace(-1, 1, k)
    return np.array([[x, y] for x in g for y in g])

def ball_edges(pts, target_deg=5.7):
    from scipy.spatial import cKDTree
    t = cKDTree(pts)
    lo, hi = 0.01, 1.0
    for _ in range(60):                       # bisect radius to hit mean degree
        r = (lo + hi) / 2
        d = np.array([len(t.query_ball_point(p, r)) - 1 for p in pts]).mean()
        lo, hi = (r, hi) if d < target_deg else (lo, r)
    pairs = t.query_pairs(r)
    return sorted(pairs), r

def rewire(edges, n_swaps, seed):
    rr = np.random.default_rng(seed)
    E = [tuple(e) for e in edges]; S = set(E)
    for _ in range(n_swaps):
        i, j = rr.integers(0, len(E), 2)
        if i == j: continue
        a, b = E[i]; c, d = E[j]
        if len({a,b,c,d}) < 4: continue
        e1, e2 = (min(a,c),max(a,c)), (min(b,d),max(b,d))
        if e1 in S or e2 in S or e1[0]==e1[1] or e2[0]==e2[1]: continue
        S.discard(E[i]); S.discard(E[j]); S.add(e1); S.add(e2)
        E[i], E[j] = e1, e2
    return sorted(S)

def W_matrix(n, edges):
    W = np.zeros((n, n))
    for u, v in edges: W[u, v] = 1; W[v, u] = 1
    rs = W.sum(1, keepdims=True); rs[rs == 0] = 1
    return W / rs

def run(pts, W, centre, mem_mix, mem_decay, steps=80, seed=0):
    rng = np.random.default_rng(seed)
    n = len(pts)
    s = np.exp(-((pts - centre) ** 2).sum(1) / (2 * 0.15 ** 2)); s /= s.sum()
    m = np.zeros(n)
    carry = 0.35 if mem_mix > 0 else 0.55
    for _ in range(steps):
        s_new = carry*s + 0.30*(W @ s) + mem_mix*m - 0.08*s + 0.005*rng.standard_normal(n)
        m = mem_decay*m + 0.35*s
        s = np.clip(s_new, 0, None)
        m = np.clip(m, 0, None)
    w = s / s.sum() if s.sum() > 0 else np.ones(n)/n
    return float((w * np.linalg.norm(pts - centre, axis=1)).sum())

pts = square_lattice()
edges, r = ball_edges(pts)
deg = np.zeros(len(pts)); 
for u,v in edges: deg[u]+=1; deg[v]+=1
print(f"square lattice: {len(pts)} pts, {len(edges)} edges, mean degree {deg.mean():.2f}, radius {r:.3f}")

Wn = W_matrix(len(pts), edges)
Wr = [W_matrix(len(pts), rewire(edges, 8000, 42+k)) for k in range(3)]

centres = [np.array(c) for c in [(0,0), (0.3,0.3), (-0.4,0.2)]]
def sweep(W_list, mem_mix, mem_decay):
    vals=[run(pts, W, c, mem_mix, mem_decay, seed=si)
          for W in (W_list if isinstance(W_list,list) else [W_list])
          for c in centres for si in range(3)]
    return float(np.mean(vals))

nat0 = sweep(Wn, 0.0, 0.0);   natM = sweep(Wn, 0.50, 0.92)
rew0 = sweep(Wr, 0.0, 0.0);   rewM = sweep(Wr, 0.50, 0.92)

print("\nSQUARE LATTICE — the arm the paper never ran")
print(f"  native  ball : WR {nat0:.4f} (no memory) -> {natM:.4f} (max memory)   gain {nat0-natM:+.4f}")
print(f"  rewired      : WR {rew0:.4f} (no memory) -> {rewM:.4f} (max memory)   gain {rew0-rewM:+.4f}")
g_n, g_r = nat0-natM, rew0-rewM
print(f"  memory benefit ratio native:rewired = {g_n/g_r:.1f}:1" if abs(g_r)>1e-6 else "  rewired gain ~0")
print("\npaper's Penrose figures: native gain 0.23, rewired gain 0.01, ratio 20:1")
