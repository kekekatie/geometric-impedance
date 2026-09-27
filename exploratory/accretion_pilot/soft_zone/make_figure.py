#!/usr/bin/env python3
"""make_figure.py -- the soft zone: freedom to re-lay a hole, by distance behind the front and by age."""
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
H = [h for l in open("results/holes.jsonl") for h in json.loads(l)["holes"]]
bins = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6)]
F = [np.mean([h["soft"] for h in H if h["bin"] == [lo, hi]]) for lo, hi in bins]
N = [sum(1 for h in H if h["bin"] == [lo, hi]) for lo, hi in bins]
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.2))
ax[0].bar(range(5), F, color=["#e67e22", "#f0b27a", "#aab7b8", "#aab7b8", "#aab7b8"], edgecolor="#555")
for i, (f, n) in enumerate(zip(F, N)):
    ax[0].text(i, f + 0.015, f"{f:.2f}\n(n={n})", ha="center", fontsize=8)
ax[0].set_xticks(range(5)); ax[0].set_xticklabels([f"{lo}-{hi}" for lo, hi in bins])
ax[0].set_xlabel("distance behind the growing front (tile edges)")
ax[0].set_ylabel("freedom: share of holes that can be re-laid differently")
ax[0].set_title("The soft zone: the present is open only near the front", fontsize=10); ax[0].set_ylim(0, 0.55)
edges = [0, 10, 20, 30, 40, 70]
fa = [np.mean([h["soft"] for h in H if a <= h["age"] < b]) for a, b in zip(edges, edges[1:])]
na = [sum(1 for h in H if a <= h["age"] < b) for a, b in zip(edges, edges[1:])]
ax[1].bar(range(len(fa)), fa, color="#8fb3e0", edgecolor="#555")
for i, (f, n) in enumerate(zip(fa, na)):
    ax[1].text(i, f + 0.015, f"{f:.2f}\n(n={n})", ha="center", fontsize=8)
ax[1].set_xticks(range(len(fa))); ax[1].set_xticklabels([f"{a}-{b}" for a, b in zip(edges, edges[1:])])
ax[1].set_xlabel("age of the hole's tiles (rounds since laid)")
ax[1].set_title("By age, there is no clean cut-off", fontsize=10); ax[1].set_ylim(0, 0.55)
for a in ax:
    a.grid(alpha=0.2, axis="y"); [a.spines[k].set_visible(False) for k in ("top", "right")]
fig.tight_layout(); fig.savefig("figures/soft_zone.png", dpi=160); print("wrote figures/soft_zone.png")
