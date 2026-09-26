#!/usr/bin/env python3
"""
healing.py -- can the writing walker's knots be healed by LOCAL hexagon flips?
(PREREGISTRATION_HEALING.md, frozen before this file existed.)

Local move: a hexagon flip at a vertex where exactly three rhombi meet. A knot heals if flips, all
at vertices within 3 tile edges of the knot, leave every knot vertex legal and create no new illegal
vertex. Exhaustive breadth-first search to depth 4 (states deduplicated).
H0 (sanity, asserted): single-flip defects in the pristine tiling heal at depth 1.
H1/H2 (predictions): < 25% of mid-wake knots heal within depth 4, at push 0.2 and 0.05.
"""
from __future__ import annotations
import os, sys, math, random, collections, json
import writing_walker as W

PA, par = W.PA, W.par
RADIUS, DEPTH, LINK = 3.0, 4, 2.5
LINES, FAILS, VERDICTS = [], [], []


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    log(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def dist(a, b):
    pa, pb = par(a), par(b)
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1])


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


class Tiling:
    """a set of rhombi (each a 4-cycle of Z^5 corners) with vertex -> faces index."""

    def __init__(self, faces):
        self.faces = {frozenset(cs): cs for cs in faces}
        self.vf = collections.defaultdict(set)
        for k, cs in self.faces.items():
            for K in cs:
                self.vf[K].add(k)

    def copy(self):
        t = Tiling.__new__(Tiling)
        t.faces = dict(self.faces); t.vf = collections.defaultdict(set, {k: set(v) for k, v in self.vf.items()})
        return t

    def neighbours(self, K):
        out = set()
        for k in self.vf.get(K, ()):
            cs = self.faces[k]; i = cs.index(K)
            out.add(cs[(i + 1) % 4]); out.add(cs[(i - 1) % 4])
        return out

    def star(self, K):
        return PA.star_type(K, {K: self.neighbours(K)})

    def flip_plan(self, v):
        """if v is a degree-3 vertex inside a hexagon, return (old face keys, new corner tuples, new centre)."""
        fs = self.vf.get(v, set())
        nb = self.neighbours(v)
        if len(fs) != 3 or len(nb) != 3:
            return None
        a, b, c = (sub(n, v) for n in nb)
        want = {frozenset((v, add(v, x), add(add(v, x), y), add(v, y))) for x, y in ((a, b), (b, c), (c, a))}
        if want != set(fs):
            return None
        w = add(add(add(v, a), b), c)
        new = [(w, sub(w, x), sub(sub(w, x), y), sub(w, y)) for x, y in ((a, b), (b, c), (c, a))]
        return list(fs), new, w

    def apply(self, plan):
        old, new, _ = plan
        for k in old:
            for K in self.faces[k]:
                self.vf[K].discard(k)
                if not self.vf[K]:
                    del self.vf[K]
            del self.faces[k]
        for cs in new:
            k = frozenset(cs); self.faces[k] = cs
            for K in cs:
                self.vf[K].add(k)


def affected(plan):
    old, new, w = plan
    vs = set()
    for cs in new:
        vs.update(cs)
    return vs


def heal_search(T, knot, atlas, illegal_before):
    """BFS over flip sequences at vertices within RADIUS of the knot; returns depth of first heal or None."""
    centre_pts = list(knot)
    near = lambda K: min(dist(K, q) for q in centre_pts) <= RADIUS
    knot_set = set(knot)
    others_illegal = illegal_before - knot_set
    start = T.copy()
    seen = {frozenset(start.faces)}
    frontier = [(start, set())]                     # (tiling, vertices whose star changed so far)
    for depth in range(1, DEPTH + 1):
        nxt = []
        for tl, changed in frontier:
            cands = [K for K in list(tl.vf) if near(K)]
            for v in cands:
                plan = tl.flip_plan(v)
                if plan is None:
                    continue
                t2 = tl.copy(); t2.apply(plan)
                key = frozenset(t2.faces)
                if key in seen:
                    continue
                seen.add(key)
                ch = changed | affected(plan) | set(plan[0] and [K for k in plan[0] for K in tl.faces[k]])
                check = {K for K in (ch | knot_set) if K in t2.vf}
                bad = {K for K in check if t2.star(K) not in atlas}
                if not (bad - others_illegal) and not (bad & knot_set):
                    return depth
                nxt.append((t2, ch))
        frontier = nxt
        if len(seen) > 400_000:
            log(f"    (search capped at {len(seen)} states)"); return None
    return None


def knots_of(F, atlas):
    T = Tiling([cs for cs, *_ in F.values()])
    types = W.star_types(F)
    illegal = {K for K, tp in types.items() if tp not in atlas}
    mid = [K for K in illegal if abs(W.dot(W.EJP, par(K))) <= 25]
    groups, left = [], set(mid)
    while left:
        g, st = [], [left.pop()]
        while st:
            u = st.pop(); g.append(u)
            for q in list(left):
                if dist(u, q) <= LINK:
                    left.discard(q); st.append(q)
        groups.append(g)
    return T, illegal, groups


def main():
    os.makedirs(W.RES, exist_ok=True)
    log("=" * 92)
    log("HEALING TEST -- can the writing walker's knots be removed by local hexagon flips?")
    log("=" * 92)
    base = W.build(0.0, 0.0)
    atlas = set(W.star_types(base).values())
    # ---- H0: single-flip defects in the pristine tiling ----
    T0 = Tiling([cs for cs, *_ in base.values()])
    rng = random.Random(7)
    cands = [K for K in T0.vf if math.hypot(*par(K)) < 20 and T0.flip_plan(K)]
    rng.shuffle(cands)
    tested, healed1, made_defect = 0, 0, 0
    for v in cands:
        if tested >= 40:
            break
        t = T0.copy(); plan = t.flip_plan(v); t.apply(plan)
        ch = affected(plan) | {K for k in plan[0] for K in T0.faces[k]}
        bad = {K for K in ch if K in t.vf and t.star(K) not in atlas}
        if not bad:
            continue
        made_defect += 1; tested += 1
        d = heal_search(t, sorted(bad), atlas, bad)
        healed1 += (d == 1)
    log(f"  pristine tiling: {len(cands)} flippable vertices within radius 20; tested {tested} single flips that "
        f"create shape-illegal vertices")
    if tested:
        require(healed1 == tested, f"H0: every single-flip defect heals at depth 1 ({healed1}/{tested})")
    else:
        log("  H0 vacuous: no single flip in the pristine tiling creates a shape-illegal vertex")
    # ---- H1, H2 ----
    out = {}
    for tag, delta in (("H1", 0.2), ("H2", 0.05)):
        F = W.build(delta, 30.0)
        T, illegal, groups = knots_of(F, atlas)
        depths = []
        for g in groups:
            d = heal_search(T, g, atlas, illegal)
            depths.append(d)
            log(f"    push {delta}: knot of {len(g)} illegal vertices at t = "
                f"{sum(W.dot(W.EJP, par(K)) for K in g) / len(g):+.1f} -> "
                + (f"HEALED at depth {d}" if d else f"not healed within depth {DEPTH}"))
        frac = sum(1 for d in depths if d) / len(depths) if depths else float("nan")
        out[delta] = dict(knots=len(groups), healed=sum(1 for d in depths if d), depths=depths)
        VERDICTS.append((tag, frac < 0.25, f"push {delta}: {out[delta]['healed']}/{len(groups)} mid-wake knots heal "
                                           f"within depth {DEPTH} ({frac:.0%}; need < 25%)"))
    # ---- reference: undoing all the walker's flips restores the pristine tiling ----
    require(W.build(0.2, 30.0) != base and W.build(0.0, 30.0) == base,
            "reference: the walker's wake differs from the pristine tiling, and undoing the push restores it exactly")
    log("-" * 92)
    for tag, held, msg in VERDICTS:
        log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")
    log("STRUCTURAL CHECKS: " + ("ALL PASSED" if not FAILS else "FAILED: " + "; ".join(FAILS)))
    open(os.path.join(W.RES, "healing_report.txt"), "w").write("\n".join(LINES) + "\n")
    json.dump({str(k): v for k, v in out.items()}, open(os.path.join(W.RES, "healing.json"), "w"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
