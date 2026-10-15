#!/usr/bin/env python3
"""EXPLORATORY (Astra's step 1, 2026-10-15; no predictions): can we follow one thing on the active front without
replacing it with a lookalike?

Rules, fixed before running:
  * World: fresh ordinary seed (wedge entry 192, seed 20261200), patient scheduler, grown to 600 added tiles.
  * The pattern: at that moment, the frontier vertex whose direction from the seed centre is closest to 0 degrees
    (ties: nearest); the pattern is every tile meeting at that vertex. Chosen by geometry, not by its future.
  * Forcing dependencies: a tile's legality is checked at its three corners against the tiles already there, so its
    PARENTS are all tiles sharing a corner with it at the moment it is placed (a joint set, no single parent).
  * Lineage: a new tile is a DESCENDANT if any parent is the pattern or a descendant. Its STRENGTH is the share of its
    parents that are in the lineage (1 = built only from the lineage; small = jointly built with outsiders).
  * Lookalikes: other frontier vertices with the same partial shape as the pattern's vertex (same multiset of corner
    labels and the same total angle), descended or not.
  * Followed for 40 slices. Per slice: new descendants, their mean strength, their spread (rms distance from their own
    centre), how far their centre sits from the pattern, and the lookalikes (inside vs outside the lineage).
  * Labels per slice: ACTIVE (new descendants), PAUSED (none this slice, but growth elsewhere), ENDED (run over).
Writes results/follow_EXPLORATORY.txt, figures/follow.gif and figures/follow_frames.png.

VARIANT B (added after run A picked a single protruding tile that then sat idle for 37 slices; rule fixed before
running B): set VARIANT=B. The pattern vertex must have >= 3 tiles meeting at it (a compact cluster), still the one
closest to the 0-degree ray; followed for 120 slices. Outputs get the suffix _B."""
import os, sys, math, cmath, random, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.animation import FuncAnimation, PillowWriter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "speed_of_now"))
import speed_of_now as SN
L, D, S = SN.L, SN.D, SN.S
WEDGE, SEED, PRE = 192, 20261200, 600
VARIANT = os.environ.get("VARIANT", "A")
SLICES, MIN_TILES, SUF = (120, 3, "_B") if VARIANT == "B" else (40, 1, "")
BG, INK, MUTED, GOLD, STRONG, WEAK, OTHER, OLD = "#07080d", "#ece8dc", "#8f8b80", "#f2b84b", "#ff7a45", "#7fb3ff", "#3a3f55", "#1b1d27"
cen = lambda t: sum(t[1:]) / 3


def centre():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[WEDGE]


class Tracker:
    """a Patch plus, for every vertex, the tiles meeting there (to read parents at placement)."""
    def __init__(s, tiles):
        s.P = L.Patch([]); s.vt = collections.defaultdict(list)
        for t in tiles:
            s.add(t)

    def add(s, t):
        parents = {D.dkey(u) for z in t[1:] for u in s.vt[L.key(z)]}
        s.P.add(t)
        for z in t[1:]:
            s.vt[L.key(z)].append(t)
        return parents


def shape(V, k):
    lst = V[k]
    return (tuple(sorted(l for _, _, l in lst)), round(sum(d for _, d, _ in lst), 6))


def step(T, rng):
    """one patient slice; returns [(tile, parents)] and kind."""
    P = T.P; fr = P.frontier(); forced = {}
    for e in fr:
        cs = D.candidates(P, *e[:3])
        if not cs:
            return None, "JAM"
        if len(cs) == 1:
            forced.setdefault(D.dkey(cs[0]), cs[0])
    if forced:
        out = []
        for t in forced.values():
            if P.legal(t):
                out.append((t, T.add(t)))
        return out, "forced"
    t = rng.choice(SN.ordered(D.candidates(P, *fr[0][:3])))
    return [(t, T.add(t))], "guess"


def main():
    c0 = centre(); rng = random.Random(SEED)
    T = Tracker(L.seed_patch(c0, 3 * S)); n0 = len(T.P.tris)
    while len(T.P.tris) - n0 < PRE:
        out, kind = step(T, rng)
        assert out is not None, "jam before the pattern was chosen"
    # pick the pattern
    fverts = {L.key(z) for e in T.P.frontier() for z in e[:2]}
    ang = lambda k: abs(((math.degrees(cmath.phase(complex(*k) - c0)) + 180) % 360) - 180)
    kp = min((k for k in fverts if len(T.vt[k]) >= MIN_TILES), key=lambda k: (round(ang(k), 6), abs(complex(*k) - c0)))
    pattern = {D.dkey(t) for t in T.vt[kp]}; pshape = shape(T.P.V, kp); zp = complex(*kp)
    settled = list(T.P.tris); lineage = set(pattern); strength = {k: 1.0 for k in pattern}
    frames = []; lines = [f"EXPLORATORY follow-a-pattern (variant {VARIANT}): world wedge {WEDGE}, seed {SEED}; pattern chosen after {PRE} added tiles at frontier vertex "
                          f"{zp / S:.2f} edges from origin ({ang(kp):.1f} deg from the 0-degree ray of the seed centre); {len(pattern)} tiles; vertex shape {pshape}"]
    for s in range(1, SLICES + 1):
        out, kind = step(T, rng)
        if out is None:
            lines.append(f"  slice {s:2d}: JAM"); break
        new_desc = []
        for t, par in out:
            k = D.dkey(t); inl = par & lineage
            if inl:
                lineage.add(k); strength[k] = len(inl) / len(par); new_desc.append(t)
        fverts = {L.key(z) for e in T.P.frontier() for z in e[:2]}
        lk = [k for k in fverts if k != kp and shape(T.P.V, k) == pshape]
        lk_in = [k for k in lk if any(D.dkey(u) in lineage for u in T.vt[k])]
        if new_desc:
            zs = np.array([cen(t) for t in new_desc]) / S; zc = zs.mean()
            spread = float(np.sqrt(np.mean(np.abs(zs - zc) ** 2))); dist = abs(zc - zp / S)
            st = np.mean([strength[D.dkey(t)] for t in new_desc])
            lab = "ACTIVE"
            lines.append(f"  slice {s:2d} ({kind:6s}): {lab:6s} new descendants {len(new_desc):3d} of {len(out):3d} placed; mean strength {st:.2f}; "
                         f"spread {spread:5.2f} edges; centre {dist:5.2f} edges from the pattern; lookalikes {len(lk_in)} in lineage / {len(lk) - len(lk_in)} outside")
        else:
            lines.append(f"  slice {s:2d} ({kind:6s}): PAUSED no new descendants ({len(out)} placed elsewhere); lookalikes {len(lk_in)} in / {len(lk) - len(lk_in)} outside")
        frames.append(dict(tiles=list(T.P.tris), lineage=set(lineage), strength=dict(strength), new={D.dkey(t) for t, _ in out},
                           lk_in=[complex(*k) for k in lk_in], lk_out=[complex(*k) for k in lk if k not in lk_in], s=s, kind=kind))
    allw = [strength[k] for k in lineage if k not in pattern]
    lines.append(f"  ENDED after {SLICES} slices: lineage {len(lineage) - len(pattern)} descendants; strength median {np.median(allw):.2f}; "
                 f"share with strength 1 (built only from the lineage) {np.mean([w == 1 for w in allw]):.2f}")
    print("\n".join(lines))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
    open(os.path.join(HERE, "results", f"follow_EXPLORATORY{SUF}.txt"), "w").write("\n".join(lines) + "\n")

    sk = {D.dkey(t) for t in settled}
    last = frames[-1]["tiles"]
    xs = [z.real / S for t in last for z in t[1:]]; ys = [z.imag / S for t in last for z in t[1:]]
    lim = (zp.real / S - 16, zp.real / S + 16, zp.imag / S - 16, zp.imag / S + 16)

    def draw(ax, f):
        ax.clear(); ax.set_facecolor(BG); ax.axis("off")
        poly, fc = [], []
        for t in f["tiles"]:
            k = D.dkey(t)
            pts = [(z.real / S, z.imag / S) for z in t[1:]]
            if not any(lim[0] - 2 < x < lim[1] + 2 and lim[2] - 2 < y < lim[3] + 2 for x, y in pts):
                continue
            poly.append(pts)
            if k in pattern:
                fc.append(GOLD)
            elif k in f["lineage"]:
                w = f["strength"][k]; fc.append(STRONG if w >= 0.5 else WEAK)
            elif k in sk:
                fc.append(OLD)
            else:
                fc.append(OTHER)
        ax.add_collection(PolyCollection(poly, facecolors=fc, edgecolors="#0b0c12", linewidths=0.25))
        for z in f["lk_out"]:
            ax.plot([z.real / S], [z.imag / S], "o", mfc="none", mec=INK, ms=7, mew=1)
        for z in f["lk_in"]:
            ax.plot([z.real / S], [z.imag / S], "o", mfc="none", mec=GOLD, ms=7, mew=1)
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal")
        ax.set_title(f"slice {f['s']} ({f['kind']})   gold = the pattern; orange = descendants built mostly from it;\n"
                     f"blue = built jointly with outsiders; dark = settled before; grey = new, unrelated; rings = lookalikes "
                     f"(white outside the lineage, gold inside)", color=INK, fontsize=8.5)

    fig, ax = plt.subplots(figsize=(8, 8.4), facecolor=BG)
    anim = FuncAnimation(fig, lambda i: draw(ax, frames[i]), frames=len(frames))
    anim.save(os.path.join(HERE, "figures", f"follow{SUF}.gif"), writer=PillowWriter(fps=4), dpi=80)
    plt.close(fig)
    pick = sorted({0, len(frames) // 4, len(frames) // 2, 3 * len(frames) // 4, len(frames) - 1})
    fig, axes = plt.subplots(1, len(pick), figsize=(4.2 * len(pick), 4.8), facecolor=BG)
    for ax, i in zip(axes, pick):
        draw(ax, frames[i]); ax.set_title(f"slice {frames[i]['s']}", color=INK, fontsize=11)
    fig.suptitle("following one pattern: gold = pattern, orange = mostly-its descendants, blue = joint descendants, rings = lookalikes",
                 color=INK, fontsize=12, family="serif", style="italic")
    plt.savefig(os.path.join(HERE, "figures", f"follow_frames{SUF}.png"), dpi=95, facecolor=BG, bbox_inches="tight")


if __name__ == "__main__":
    main()
