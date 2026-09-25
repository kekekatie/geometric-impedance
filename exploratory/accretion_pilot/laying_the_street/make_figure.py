#!/usr/bin/env python3
"""make_figure.py -- figures/barcodes.png: the first 150 letters each rule lays (L dark, S light)."""
import os, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import laying_the_street as L

HERE = os.path.dirname(os.path.abspath(__file__))
SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
DARK, LIGHT, MARK = "#0d3a73", "#bcd6f5", "#eb6834"
NSHOW = 150
L.N = 400
rows = [("the Fibonacci street (reference)", L.FIB[:NSHOW]),
        ("LOCAL, window 13 (dice at choices)", L.lay("LOCAL", "LSLLS", random.Random(1), k=13)[0]),
        ("COPY: same-scale twin -> repetition", L.lay("COPY", "LSLLS", random.Random(1))[0]),
        ("ANTI: opposite of twin -> noise", L.lay("ANTI", "LSLLS", random.Random(1))[0]),
        ("DICE -> noise", L.lay("DICE", "LSLLS", random.Random(1))[0]),
        ("SCALE, seed LSLLS -> perfect", L.lay("SCALE", "LSLLS", None)[0]),
        ("SCALE, seed LLSLS -> a scar at the start", L.lay("SCALE", "LLSLS", None)[0]),
        ("SCALE, seed LLLLL -> a mistake that inflates", L.lay("SCALE", "LLLLL", None)[0]),
        ("WRONGSCALE -> a different, wrong street", L.lay("WRONGSCALE", "LSLLS", None)[0])]
fig, ax = plt.subplots(figsize=(12, 5.8), dpi=150)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
for i, (lab, w) in enumerate(rows):
    y = len(rows) - 1 - i
    for x, c in enumerate(w[:NSHOW]):
        ax.add_patch(Rectangle((x, y + 0.1), 1, 0.62, color=DARK if c == "L" else LIGHT, lw=0))
    d = L.defects(w[:NSHOW])
    if d and i > 0:
        ax.plot([d[0] - 0.5], [y + 0.86], marker="v", ms=7, color=MARK)
    ax.text(-2, y + 0.41, lab, ha="right", va="center", fontsize=9, color=INK)
ax.set_xlim(-2, NSHOW); ax.set_ylim(-0.1, len(rows) + 0.1)
ax.set_xticks([0, 50, 100, 150]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(colors=INK2, labelsize=8.5)
ax.set_xlabel("letters laid, one at a time, using only the letters already laid", color=INK2, fontsize=9)
fig.suptitle("Laying the street with no map: only the street's own zoomed-out self keeps it right",
             color=INK, fontsize=12.5, fontweight="bold", x=0.01, ha="left", y=0.985)
fig.text(0.01, 0.925, "Dark = long tile (L), light = short tile (S). Orange arrow = the first defect "
         "(a pattern the Fibonacci street never contains).", color=INK2, fontsize=9, ha="left")
fig.subplots_adjust(left=0.27, right=0.99, top=0.88, bottom=0.11)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.savefig(os.path.join(HERE, "figures", "barcodes.png"), facecolor=SURF)
print("wrote figures/barcodes.png")
