#!/usr/bin/env python3
"""EXPLORATORY figure + corrected binning for cut_direction (after the registered run).
The registered binning rounded cut-line angles to multiples of 36 deg; the real angles sit at 18 + 36k, so 126 and 162
both landed in '144'. Here: (1) the true cut angle against the decided family and the strip's physical direction, for all
45 distinct situations; (2) settled vs built: when strip tiles were built against their distance from the choice point.
Writes results/corrected_EXPLORATORY.txt and figures/cut_direction.png."""
import os, json, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
BG, INK, MUTED, GOLD, BLUE, RED = "#07080d", "#ece8dc", "#8f8b80", "#f2b84b", "#5b8fe0", "#ff5a4d"
COL = ["#f2b84b", "#5b8fe0", "#7ccf8a", "#e07bb5", "#b9a2f0"]

W = json.load(open(os.path.join(HERE, "results", "worlds.json")))
first = {}
for w in W:
    for c in w["choices"]:
        first.setdefault(c["key"], c)
U = [c for c in first.values() if c.get("shares")]
fam = lambda c: int(np.argmax(c["shares"]))
true_dir = lambda c: int(round((c["line_angle"] - 18) / 36)) * 36 % 180 + 18
by = collections.defaultdict(collections.Counter)
for c in U:
    by[true_dir(c)][fam(c)] += 1
law = lambda a: (108 - 2 * a) % 180
dev = [min(abs(c["axis"] - law(c["line_angle"])) % 180, 180 - abs(c["axis"] - law(c["line_angle"])) % 180) for c in U]
lines = ["EXPLORATORY corrected binning (true cut angles 18 + 36k):"] + [f"  cut line at {d:3d} deg -> decided family {dict(v)}" for d, v in sorted(by.items())]
lines.append(f"  one family per direction: {all(len(v) == 1 for v in by.values())}; directions seen {len(by)}, families {len({next(iter(v)) for v in by.values()})}")
el = [d for d, c in zip(dev, U) if c["ratio"] >= 3]
lines.append(f"  rule: family j <-> cut angle 90 - 36 j (mod 180); strip direction = 108 - 2 x cut angle (mod 180): max deviation {max(el):.1f} deg over "
             f"{len(el)} elongated strips (ratio >= 3); the {len(U) - len(el)} rounder strips deviate by {sorted(round(d) for d, c in zip(dev, U) if c['ratio'] < 3)}")
pairs = [(d, s) for c in U for d, s in c["built"]]
dd = np.array([p[0] for p in pairs]); ss = np.array([p[1] for p in pairs])
slope = np.polyfit(dd, ss, 1)
lines.append(f"  settled vs built: least-squares slice = {slope[1]:.2f} + {slope[0]:.2f} x distance (edges): about {1 / slope[0]:.2f} edges built per slice along the strip")
print("\n".join(lines))
open(os.path.join(HERE, "results", "corrected_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")

fig, axes = plt.subplots(1, 2, figsize=(15, 6.4), facecolor=BG)
for ax in axes:
    ax.set_facecolor(BG); ax.tick_params(colors=MUTED)
    for sp in ax.spines.values():
        sp.set_color(MUTED)
ax = axes[0]
xs = np.linspace(0, 180, 400)
for k in range(-2, 3):
    ax.plot(xs, 108 - 2 * xs + 180 * k, color=MUTED, lw=0.8, ls=":")
rng = np.random.default_rng(1)
for c in U:
    ax.scatter(c["line_angle"] + rng.uniform(-2, 2), c["axis"], s=40, color=COL[fam(c)], edgecolors="none", alpha=0.85)
for j in range(5):
    ax.scatter([], [], color=COL[j], label=f"ribbon family {j}")
ax.set_xlim(0, 180); ax.set_ylim(0, 180)
ax.set_xlabel("direction of the cut in the wiggle room (degrees)", color=INK)
ax.set_ylabel("direction of the decided strip in the world (degrees)", color=INK)
ax.legend(frameon=False, labelcolor=INK, fontsize=9, loc="upper right")
ax.set_title("settled in the window -> named in the world\n(every point on the dotted rule: strip = 108 - 2 x cut)", color=INK, fontsize=11)
ax = axes[1]
ax.scatter(dd + rng.uniform(-0.15, 0.15, len(dd)), ss + rng.uniform(-0.3, 0.3, len(ss)), s=3, color=GOLD, alpha=0.25, edgecolors="none")
ax.axhline(1, color=RED, lw=1.2); ax.text(14, 0.2, "settled: the cut is made here (slice 1)", color=RED, fontsize=9)
xx = np.linspace(0, 20, 50); ax.plot(xx, slope[1] + slope[0] * xx, color=INK, lw=1.2)
ax.text(1, 19.5, f"built: about {1 / slope[0]:.1f} edge per slice", color=INK, fontsize=9)
ax.set_xlim(0, 20); ax.set_ylim(-0.5, 20.5); ax.invert_yaxis()
ax.set_xlabel("distance of a strip tile from the choice point (edges)", color=INK)
ax.set_ylabel("slice at which it was built", color=INK)
ax.set_title("the window knows at once; the world builds it one click at a time", color=INK, fontsize=11)
fig.suptitle("settled vs built: the direction of a cut in the wiggle room names the ribbon the world will lay",
             color=INK, fontsize=13.5, family="serif", style="italic")
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
plt.savefig(os.path.join(HERE, "figures", "cut_direction.png"), dpi=105, facecolor=BG, bbox_inches="tight")
