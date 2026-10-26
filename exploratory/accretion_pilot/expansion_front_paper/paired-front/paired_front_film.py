#!/usr/bin/env python3
"""
paired_front_film.py -- the Phase-1 deliverable: two fronts side by side, over time.

Astra's spec: identical colours for identical geometry; an analyst-only difference overlay; markers for
the choice-tile's departure from the retained skin, and for censoring. Renders one fork (a coupled A/B
stream pair) as an animated GIF plus a static multi-step strip.

Colours (same meaning in both panels, every frame):
  grey        tiles common to A and B (same decorated tile, same place) -- shared, identical
  blue/orange tiles that DIFFER on shared coverage (A-only / B-only where the other also covers) -- the trace
  pale        tiles only this arm covers (front displacement; the other front is elsewhere)
  bold outline the original choice-tile, while it is still in the retained skin

Run:  python3 paired_front_film.py --world 0 --steps 44
"""
from __future__ import annotations
from pathlib import Path
import sys, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import paired_front as PF
L, D, S, CD = PF.L, PF.D, PF.S, PF.CD
cen, dk = PF.cen, PF.dk
RES = HERE / "results"; RES.mkdir(exist_ok=True)
GREY, ABLUE, BORANGE, PALE = "#c9d1d6", "#167c9b", "#d66a34", "#eef1f3"


def polys(ts, origin):
    return [[((z - origin).real / S, (z - origin).imag / S) for z in t[1:]] for t in ts]


def classify(skinSelf, skinOther, color):
    """Return (common, differ, displaced) tile lists for one arm vs the other."""
    kO = {dk(t) for t in skinOther}
    cov = lambda p: any(L.inside(p, *u[1:]) for u in skinOther)
    common, differ, displaced = [], [], []
    for t in skinSelf:
        if dk(t) in kO:
            common.append(t)
        elif cov(cen(t)):
            differ.append(t)
        else:
            displaced.append(t)
    return common, differ, displaced


def draw_panel(ax, skin, other, choice_key, origin, color, title, lim):
    common, differ, displaced = classify(skin, other, color)
    ax.add_collection(PolyCollection(polys(common, origin), facecolors=GREY, edgecolors="white", linewidths=.2))
    ax.add_collection(PolyCollection(polys(displaced, origin), facecolors=PALE, edgecolors="#dde3e7", linewidths=.2))
    ax.add_collection(PolyCollection(polys(differ, origin), facecolors=color, edgecolors="white", linewidths=.25))
    ch = [t for t in skin if dk(t) == choice_key]
    if ch:
        ax.add_collection(PolyCollection(polys(ch, origin), facecolors="none", edgecolors="#111", linewidths=2.4))
    ax.set(xlim=lim[:2], ylim=lim[2:], aspect="equal"); ax.axis("off")
    ax.set_title(title, fontsize=9)
    return len(differ), len(ch) > 0


def frame(fig, armsA, armsB, mid, s, lim, departA, departB):
    fig.clf()
    axA, axB = fig.subplots(1, 2)
    skinA, _ = PF.skin_of(armsA["snaps"][min(s, len(armsA["snaps"]) - 1)])
    skinB, _ = PF.skin_of(armsB["snaps"][min(s, len(armsB["snaps"]) - 1)])
    dA, inA = draw_panel(axA, skinA, skinB, armsA["choice"], mid, ABLUE, "Option A", lim)
    dB, inB = draw_panel(axB, skinB, skinA, armsB["choice"], mid, BORANGE, "Option B", lim)
    gone = []
    if departA is not None and s >= departA:
        gone.append(f"A choice-tile pruned @ {departA}")
    if departB is not None and s >= departB:
        gone.append(f"B choice-tile pruned @ {departB}")
    tag = ("  |  " + "; ".join(gone)) if gone else "  |  choice-tiles still in skin"
    fig.suptitle(f"Paired fronts, step {s}   (differing-on-shared-ground: A {dA}, B {dB}){tag}\n"
                 f"grey = identical · blue/orange = differs on shared ground (the trace) · pale = front is elsewhere · black outline = the original choice-tile",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.92))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", type=int, default=0)
    ap.add_argument("--steps", type=int, default=44)
    args = ap.parse_args()
    centre = PF.centres(args.world + 1)[args.world]
    cs0 = PF.common_state(args.world, centre)
    if cs0 is None:
        print(f"world {args.world}: no qualifying fork"); return
    Sstar, edge, mid, cs, meta = cs0
    stream = PF.SEED0 * 1000 + args.world * 7919
    armsA = PF.grow_arm(Sstar, cs[0], stream, args.steps)
    armsB = PF.grow_arm(Sstar, cs[1], stream, args.steps)
    rows, departA, departB = PF.compare(armsA, armsB, args.steps)
    # a common viewing window: the union of both arms' final skins, around the fork
    finalA, _ = PF.skin_of(armsA["snaps"][-1]); finalB, _ = PF.skin_of(armsB["snaps"][-1])
    p = np.array([q for t in polys(finalA + finalB, mid) for q in t])
    lo, hi = p.min(0) - 1, p.max(0) + 1; m = max(hi - lo)
    lim = (lo[0], lo[0] + m, lo[1], lo[1] + m)

    nmax = min(len(armsA["snaps"]), len(armsB["snaps"]))
    fig = plt.figure(figsize=(11, 6.2))
    frames = []
    try:
        from PIL import Image
        for s in range(nmax):
            frame(fig, armsA, armsB, mid, s, lim, departA, departB)
            fig.canvas.draw()
            w, h = fig.canvas.get_width_height()
            buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)
            frames.append(Image.fromarray(buf[..., :3].copy()))
        gif = RES / f"paired_front_world{args.world}.gif"
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=320, loop=0)
        print(f"wrote {gif} ({len(frames)} frames)")
    except Exception as e:
        print(f"GIF assembly skipped ({type(e).__name__}: {e})")

    # static strip at a few key steps (including around departure)
    keys = sorted(set([1, (departA or 6), (departB or 10), nmax // 2, nmax - 1]))
    keys = [k for k in keys if 0 <= k < nmax][:5]
    figS, axs = plt.subplots(2, len(keys), figsize=(3.1 * len(keys), 6.4))
    for col, s in enumerate(keys):
        skinA, _ = PF.skin_of(armsA["snaps"][s]); skinB, _ = PF.skin_of(armsB["snaps"][s])
        draw_panel(axs[0, col], skinA, skinB, armsA["choice"], mid, ABLUE, f"A · step {s}", lim)
        draw_panel(axs[1, col], skinB, skinA, armsB["choice"], mid, BORANGE, f"B · step {s}", lim)
    figS.suptitle(f"World {args.world}: two fronts from one fork (choice-tiles pruned at A={departA}, B={departB})\n"
                  "grey identical · blue/orange differs on shared ground · pale front-elsewhere · outline = choice-tile",
                  fontsize=11)
    figS.tight_layout(rect=(0, 0, 1, 0.93))
    strip = RES / f"paired_front_world{args.world}_strip.png"
    figS.savefig(strip, dpi=150, facecolor="white", bbox_inches="tight"); plt.close(figS)
    print(f"wrote {strip}")


if __name__ == "__main__":
    main()
