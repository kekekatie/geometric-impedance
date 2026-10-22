#!/usr/bin/env python3
"""
corner_response.py -- the corner-response catalogue (Experiment A).
(PREREGISTRATION.md, frozen before this file.)

Across fresh ordinary worlds, every live two-way tie on the growing frontier is
caught, fingerprinted, and watched. When a tie is settled by neighbouring
construction (not by the scheduler choosing it), we ask -- with local_response's
machinery -- whether a single tile is enough (a keystone) and why the rejected
option dies (the vertex / corner rule). We then group ties by "sameness" and ask
what fraction of each recurring move settles: the stiffness line.

Three called shots (see PREREGISTRATION.md):
  A1  single keystones settle >= 60% of settled ties (not committees).
  A2  the deciding touch is a corner (vertex rule) >= 80%, and the real keystone
      beats the random-neighbour placebo by more than 2x.
  A3  reality has give: >= 15% of recurring moves are malleable (settle < 90%).

Run:  python3 corner_response.py            # full study, 24 worlds, parallel
      python3 corner_response.py --worlds 2 --nadd 300 --serial   # quick test
"""
from __future__ import annotations
from pathlib import Path
import sys, os, json, math, cmath, random, hashlib, collections, argparse
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # find the engine (../)
import figures as F                 # wires the engine: F.L F.D F.Sl F.SN F.S F.CD
import local_response as LR         # LR.reasons(P,t) -> overlaps / duplicate / failing_vertices
import endurance_observer as T      # T.canonical(tiles, edges, centre, reflect): sames fingerprint

L, D, Sl, SN, S = F.L, F.D, F.Sl, F.SN, F.S
CD = F.CD

HERE = Path(__file__).resolve().parent
RES = HERE / "results"; RES.mkdir(exist_ok=True)

# --- fixed in the pre-registration ---------------------------------------
SEED0   = 20261200      # random seed base (per world: SEED0 + world index)
N_ADD   = 1500          # tiles added per world
N_WORLDS = 24           # worlds 0..23  ->  wedge entries 192..215
WEDGE0  = 192           # first wedge entry (144-167 and 168-191 already used)
K       = 20            # watching window, in slices
RADII   = (1, 2, 3, 4)  # fingerprint radii (edge lengths); 2 is primary
RPRIMARY = 2
MIN_RECUR = 5           # a fingerprint must recur >= this to enter the stiffness line
RIGID_CUT = 0.9         # settle-fraction >= this is "rigid", below is "malleable"
TESTWIN = 6             # local window (edge lengths) used for the necessary/sufficient test
EPS = 1e-9

key = lambda t: repr(D.dkey(t))
ek  = lambda e: repr(sorted([L.key(e[0]), L.key(e[1])]))


def centres():
    """Seed centres at wedge entries WEDGE0 .. WEDGE0+N_WORLDS (fresh, unseen)."""
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[WEDGE0:WEDGE0 + N_WORLDS]


def near(tiles, mid, radius):
    """Tiles with any vertex within radius*S of the point mid."""
    r = radius * S + EPS
    return [t for t in tiles if any(abs(z - mid) <= r for z in t[1:])]


def fingerprint(before, mid, radius):
    """Reflection-folded canonical key of the local situation facing the tie."""
    local = near(before, mid, radius)
    if not local:
        return None
    a = T.canonical(local, [], mid, False)
    b = T.canonical(local, [], mid, True)
    return hashlib.sha256(repr(min(a, b)).encode()).hexdigest()[:16]


def response_test(before, added_local, edge):
    """Generalise local_response: of the locally added tiles, which single tile is
    SUFFICIENT alone (settles the tie) and NECESSARY (its omission reopens it)?
    Returns the drawer and, for a keystone, why the rejected option dies.
    """
    base = near(before, (edge[0] + edge[1]) / 2, TESTWIN)   # small exact window for speed
    opts = lambda ts: sorted(key(t) for t in D.candidates(L.Patch(ts), *edge[:3]))
    a = opts(base)
    if len(a) != 2:
        return dict(drawer="unresolved", note=f"base options={len(a)}")
    b = opts(base + added_local)
    if len(b) != 1:
        # settled, but not by anything inside the local window -> non-local committee
        return dict(drawer="committee", nonlocal_=True, n_local=len(added_local))
    rejected = next(t for t in D.candidates(L.Patch(base), *edge[:3]) if key(t) not in b)
    sufficient, necessary, reasons_for = [], [], {}
    for i, t in enumerate(added_local):
        alone   = opts(base + [t])
        without = opts(base + added_local[:i] + added_local[i + 1:])
        if alone == b:
            sufficient.append(i)
            reasons_for[i] = LR.reasons(L.Patch(base + [t]), rejected)
        if without != b:
            necessary.append(i)
    n_local = len(added_local)
    placebo_rate = len(sufficient) / n_local if n_local else 0.0   # fraction of neighbours that settle alone
    if sufficient:
        keystones = []
        for i in sufficient:
            r = reasons_for[i]
            corner = bool(r["failing_vertices"]) and not r["overlaps"] and not r["duplicate"]
            # does the keystone tile actually carry the failing vertex? (its corner does the work)
            tverts = {repr(list(k)) for k in L.corners([added_local[i]])}
            shares_vertex = any(repr(v) in tverts for v in r["failing_vertices"])
            keystones.append(dict(index=i + 1, necessary=i in necessary, corner=corner,
                                  shares_vertex=shares_vertex, failing_vertices=r["failing_vertices"],
                                  overlaps=bool(r["overlaps"]), duplicate=r["duplicate"]))
        return dict(drawer="single_keystone", keystones=keystones, n_local=n_local,
                    n_sufficient=len(sufficient), n_necessary=len(necessary), placebo_rate=placebo_rate)
    # no single tile is sufficient: a committee settled it
    return dict(drawer="committee", n_local=n_local, placebo_rate=placebo_rate)


def grow_world(k):
    """Grow one fresh world, catching and watching every two-way tie."""
    rng = random.Random(SEED0 + k)
    c0 = centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0
    active = {}            # site -> dict(before, edge, first_slice, mid, fps)
    done = set()           # resolved site keys (never re-register)
    ties = []              # resolved tie records
    status = "ok"

    def resolve(sk, rec):
        tie = active.pop(sk); done.add(sk)
        rec.update(world=k, site=sk, first_slice=tie["first_slice"], resolved_slice=r,
                   fps=tie["fps"], xy=[tie["mid"].real / S, tie["mid"].imag / S])
        ties.append(rec)

    while len(P.tris) - n0 < N_ADD:
        r += 1
        fr = P.frontier()
        cand = {}; fmap = {}
        jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            sk = ek(e); cand[sk] = len(cs); fmap[sk] = e
        if jam:
            status = "JAM"; break

        # 1. update / resolve tracked ties from current candidate counts
        for sk in list(active):
            tie = active[sk]
            if sk not in cand:
                resolve(sk, dict(drawer="gone"))                       # built over / left frontier
            elif cand[sk] == 1:
                added = P.tris[len(tie["before"]):]
                added_local = near(added, tie["mid"], RPRIMARY)
                rec = response_test(tie["before"], added_local, tie["edge"])
                rec["response_settled"] = True
                resolve(sk, rec)
            elif r - tie["first_slice"] >= K:
                resolve(sk, dict(drawer="stayed_open"))
            # else cand[sk]==2 and within window: keep watching

        # 2. register new two-way ties
        for sk, n in cand.items():
            if n == 2 and sk not in active and sk not in done:
                mid = (fmap[sk][0] + fmap[sk][1]) / 2
                before = list(P.tris)
                fps = {R: fingerprint(before, mid, R) for R in RADII}
                active[sk] = dict(before=before, edge=fmap[sk], first_slice=r, mid=mid, fps=fps)

        # 3. the growth step (forced-first, else one guess) -- mirrors cut_direction.world
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3]))
        gk = ek(fr[0])
        if gk in active:                                               # scheduler chose this tie directly
            resolve(gk, dict(drawer="directly_chosen", options=len(cs)))
        P.add(rng.choice(cs))

    # flush ties still open at end of growth
    for sk in list(active):
        resolve(sk, dict(drawer="stayed_open", at_end=True))
    return dict(world=k, status=status, slices=r, added=len(P.tris) - n0, ties=ties)


# --- aggregation and scoring ---------------------------------------------
def score(worlds):
    ties = [t for w in worlds for t in w["ties"]]
    drawers = collections.Counter(t["drawer"] for t in ties)
    kstone = [t for t in ties if t["drawer"] == "single_keystone"]
    commit = [t for t in ties if t["drawer"] == "committee"]
    opened = [t for t in ties if t["drawer"] == "stayed_open"]
    settled = kstone + commit

    lines = []
    lines.append(f"worlds: {len(worlds)}; statuses {dict(collections.Counter(w['status'] for w in worlds))}; "
                 f"total ties caught {len(ties)}")
    lines.append(f"drawers: {dict(drawers)}")

    # A1 -- single keystones are the usual settle
    a1_frac = len(kstone) / len(settled) if settled else 0.0
    lines.append(f"A1: {'HELD  ' if a1_frac >= 0.60 else 'FAILED'}  single keystones settle "
                 f"{len(kstone)}/{len(settled)} = {a1_frac:.2%} of settled ties (need >= 60%)")

    # A2a -- corner, not edge
    corner_k = [t for t in kstone if any(ksd["corner"] for ksd in t["keystones"])]
    a2a_frac = len(corner_k) / len(kstone) if kstone else 0.0
    shares_v = sum(any(ksd["corner"] and ksd["shares_vertex"] for ksd in t["keystones"]) for t in kstone)
    lines.append(f"A2a: {'HELD  ' if a2a_frac >= 0.80 else 'FAILED'}  deciding touch is a corner "
                 f"(vertex rule, no overlap) in {len(corner_k)}/{len(kstone)} = {a2a_frac:.2%} (need >= 80%); "
                 f"keystone carries the failing vertex in {shares_v}/{len(kstone)}")

    # A2b -- beats the random-neighbour placebo
    placebo = [t["placebo_rate"] for t in kstone if "placebo_rate" in t]
    mean_placebo = sum(placebo) / len(placebo) if placebo else 0.0
    lines.append(f"A2b: {'HELD  ' if mean_placebo < 0.5 else 'FAILED'}  mean fraction of neighbours that "
                 f"settle alone = {mean_placebo:.2%} (need < 50%; keystone itself always settles = 100%)")

    # A3 -- reality has give (stiffness line at the primary radius)
    groups = collections.defaultdict(list)
    for t in ties:
        if t["drawer"] in ("single_keystone", "committee", "stayed_open"):   # observable (not directly chosen)
            fp = t["fps"].get(str(RPRIMARY)) or t["fps"].get(RPRIMARY)
            if fp:
                groups[fp].append(1 if t["drawer"] in ("single_keystone", "committee") else 0)
    recurring = {fp: v for fp, v in groups.items() if len(v) >= MIN_RECUR}
    fracs = {fp: sum(v) / len(v) for fp, v in recurring.items()}
    malleable = [fp for fp, f in fracs.items() if f < RIGID_CUT]
    a3_frac = len(malleable) / len(recurring) if recurring else 0.0
    lines.append(f"A3: {'HELD  ' if a3_frac >= 0.15 else 'FAILED'}  recurring moves (>= {MIN_RECUR}x): "
                 f"{len(recurring)}; malleable (<{RIGID_CUT:.0%}): {len(malleable)} = {a3_frac:.2%} (need >= 15%)")
    if recurring:
        dist = collections.Counter(round(f, 1) for f in fracs.values())
        lines.append("    stiffness line (settle-fraction -> #moves): " +
                     "; ".join(f"{b:.1f}:{dist[b]}" for b in sorted(dist)))

    # reported: stiffness vs radius
    lines.append("  reported (stiffness vs window radius):")
    for R in RADII:
        g = collections.defaultdict(list)
        for t in ties:
            if t["drawer"] in ("single_keystone", "committee", "stayed_open"):
                fp = t["fps"].get(str(R)) or t["fps"].get(R)
                if fp:
                    g[fp].append(1 if t["drawer"] != "stayed_open" else 0)
        rec = {fp: v for fp, v in g.items() if len(v) >= MIN_RECUR}
        if rec:
            fr2 = [sum(v) / len(v) for v in rec.values()]
            mal = sum(f < RIGID_CUT for f in fr2) / len(fr2)
            lines.append(f"    radius {R}*S: {len(rec)} recurring moves; "
                         f"malleable {mal:.2%}; mean settle-fraction {sum(fr2)/len(fr2):.2%}")

    summary = dict(total_ties=len(ties), drawers=dict(drawers),
                   A1=dict(held=a1_frac >= 0.60, frac=a1_frac, keystone=len(kstone), settled=len(settled)),
                   A2a=dict(held=a2a_frac >= 0.80, frac=a2a_frac, corner=len(corner_k), keystone=len(kstone)),
                   A2b=dict(held=mean_placebo < 0.5, mean_placebo=mean_placebo),
                   A3=dict(held=a3_frac >= 0.15, frac=a3_frac, recurring=len(recurring), malleable=len(malleable)),
                   stiffness={fp: round(f, 4) for fp, f in sorted(fracs.items(), key=lambda kv: kv[1])})
    return "\n".join(lines), summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=N_WORLDS)
    ap.add_argument("--nadd", type=int, default=None)
    ap.add_argument("--serial", action="store_true")
    args = ap.parse_args()
    global N_ADD
    if args.nadd:
        N_ADD = args.nadd
    ids = list(range(args.worlds))
    if args.serial or args.worlds == 1:
        worlds = [grow_world(k) for k in ids]
    else:
        with Pool(min(4, args.worlds), maxtasksperchild=1) as p:
            worlds = p.map(grow_world, ids)
    report, summary = score(worlds)
    print(report)
    (RES / "worlds.json").write_text(json.dumps(worlds, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (RES / "summary.json").write_text(json.dumps(summary, indent=2))
    (RES / "corner_response_report.txt").write_text(report + "\n")


if __name__ == "__main__":
    main()
