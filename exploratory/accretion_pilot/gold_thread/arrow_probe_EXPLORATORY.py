import sys, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ribbons_EXPLORATORY as R
M, D, L, S = R.M, R.D, R.L, R.S
ref = [t for t in L.REF if abs(R.F.cen(t)) < 0.8]
rib, be = R.ribbons(ref)
# marking of a j-edge, oriented along +eps_j, from each side: (tile type, role at tail, role at head)
def roles(t):
    return {L.key(t[1]): "A", L.key(t[2]): "B", L.key(t[3]): "C"}
marks = collections.defaultdict(set)   # (j, ribbon root) -> set of markings
per_edge = {}
for e, ks in be.items():
    if len(ks) != 2: continue
    idx = {D.dkey(t): t for t in ref} if 'idx' not in globals() else idx
    t0 = idx[ks[0]]; pts = {L.key(z): z for z in t0[1:]}
    p, q = [pts[k] for k in e]
    if not R.is_leg(p, q): continue
    j, sg = M.edge_dir(p, q)
    if sg < 0: p, q = q, p
    m = []
    for k in ks:
        t = idx[k]; rl = roles(t)
        side = 'L' if ((R.F.cen(t) - p) * (q - p).conjugate()).imag > 0 else 'R'
        m.append((side, t[0], rl[L.key(p)], rl[L.key(q)]))
    m = tuple(sorted(m)); per_edge[e] = (j, m)
    marks[(j, rib[j][ks[0]])].add(m)
cnt = collections.Counter(len(v) for v in marks.values())
print("ribbons:", len(marks), "distinct markings per ribbon:", dict(cnt))
allm = collections.Counter(m for j, m in per_edge.values())
print("distinct edge markings overall:", len(allm)); print(allm.most_common(6))

def arrow(m):
    # left tile's (type, unordered roles) = edge kind; direction = whether roles run in sorted order along +eps_j
    side, c, a, b = [x for x in m if x[0] == 'L'][0]
    return (c, tuple(sorted((a, b)))), (1 if a < b else -1)
arr = collections.defaultdict(set)
for e, (j, m) in per_edge.items():
    ks = be[e]; arr[(j, rib[j][ks[0]])].add(arrow(m))
print("distinct (kind, direction) per ribbon:", dict(collections.Counter(len(v) for v in arr.values())))
print("distinct directions per ribbon:", dict(collections.Counter(len({d for _, d in v}) for v in arr.values())))
print("examples:", list(arr.values())[:5])

# arrow classes from the tiling itself: the two sides of a shared edge carry the same arrow (same orientation)
par = {}
def fd(a):
    par.setdefault(a, a)
    while par[a] != a: a = par[a]
    return a
for e, (j, m) in per_edge.items():
    (s1, c1, a1, b1), (s2, c2, a2, b2) = m
    par[fd((c1, a1, b1))] = fd((c2, a2, b2)); par[fd((c1, b1, a1))] = fd((c2, b2, a2))
cls = sorted({fd(x) for x in list(par)})
print("arrow classes (oriented):", cls)
arr2 = collections.defaultdict(set)
for e, (j, m) in per_edge.items():
    s, c, a, b = m[0]; arr2[(j, rib[j][be[e][0]])].add(fd((c, a, b)))
print("distinct oriented arrows per ribbon:", dict(collections.Counter(len(v) for v in arr2.values())))
kinds = lambda v: len({frozenset({x, fd((x[0], x[2], x[1]))}) for x in v})
print("distinct arrow KINDS per ribbon (ignoring direction):", dict(collections.Counter(kinds(v) for v in arr2.values())))
