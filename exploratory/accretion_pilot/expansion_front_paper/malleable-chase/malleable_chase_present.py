#!/usr/bin/env python3
"""
malleable_chase_present.py -- figures + viewer for Experiment C.
Reads results/summary.json and results/worlds.json. Produces:
  true-stiffness.png   malleable fps' burst-settle fraction (how much wobble was just timing)
  interior-wall.png    wall-nearness of settled vs stayed-open ties (the interior ruler)
  OPEN-MALLEABLE-CHASE.html  self-contained viewer
Run after malleable_chase.py.
"""
from pathlib import Path
import json, base64, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
A, B, CORE, GRAY = "#167c9b", "#d66a34", "#713c91", "#dce1e4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 13})


def png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=150, facecolor="white", bbox_inches="tight"); plt.close(fig)
    return b.getvalue()


def stiffness_figure(stiff):
    vals = list(stiff.values())
    fig, ax = plt.subplots(figsize=(8, 4.3))
    bins = [i / 10 for i in range(12)]
    secret = [v for v in vals if v >= 0.999]
    gen = [v for v in vals if v < 0.999]
    ax.hist([gen, secret], bins=bins, stacked=True, color=[CORE, GRAY], edgecolor="white",
            label=[f"genuinely contingent  n={len(gen)}", f"secretly rigid (timing)  n={len(secret)}"])
    ax.set(xlabel="burst-settle fraction  (0 = always needs a guess  →  1 = always forced by the board)",
           ylabel="number of malleable moves", xlim=(-0.02, 1.08),
           title="The true stiffness, once the scheduler's stopwatch is removed")
    ax.legend(frameon=False, fontsize=10, loc="upper center")
    ax.spines[["top", "right"]].set_visible(False)
    return png(fig)


def wall_figure(settled, opened):
    fig, ax = plt.subplots(figsize=(8, 4.3))
    bins = np.linspace(0, 0.5, 26)
    ax.hist(settled, bins=bins, color=A, alpha=.75, density=True, label=f"settled ties (n={len(settled)})")
    ax.hist(opened, bins=bins, color=B, alpha=.6, density=True, label=f"stayed-open ties (n={len(opened)})")
    ax.axvline(np.median(settled), color=A, ls="--", lw=1.2)
    ax.axvline(np.median(opened), color=B, ls="--", lw=1.2)
    ax.set(xlabel="wall-nearness  min(pA,pB)/F_area   (0 = right on the interior wall)",
           ylabel="density", title="The interior-wall ruler: settled ties are born on the wall")
    ax.legend(frameon=False, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    return png(fig)


def shot(h):
    return "✅ HELD" if h else ("— did not hold" if h is False else "n/a")


def main():
    s = json.loads((RES / "summary.json").read_text())
    worlds = json.loads((RES / "worlds.json").read_text())
    ties = [t for w in worlds for t in w["ties"]]
    settled = [t["wall"] for t in ties if t["wall"] is not None and t["drawer"] in ("single_keystone", "committee")]
    opened = [t["wall"] for t in ties if t["wall"] is not None and t["drawer"] == "stayed_open"]
    enc = {}
    for name, data in [("true-stiffness.png", stiffness_figure(s["true_stiffness"])),
                       ("interior-wall.png", wall_figure(settled, opened) if settled and opened else None)]:
        if data:
            (HERE / name).write_bytes(data); enc[name] = "data:image/png;base64," + base64.b64encode(data).decode()
    c1, c2, c3, c4 = s["C1"], s["C2"], s["C3"], s["C4"]
    rows = [
        ("C1", "much of the wobble was just timing", shot(c1["held"]),
         f"secretly-rigid malleable moves {c1['secret']}/{c1['malleable']} = {c1['frac']:.1%} (pledged ≥ 50%)"),
        ("C2", "but a genuine core survives", shot(c2["held"]),
         f"genuinely contingent moves {c2['genuine']}/{c1['malleable']} = {c2['frac']:.1%} (pledged ≥ 15%)"),
        ("C3", "the interior ruler beats the outer", shot(c3["held"]),
         f"settled ties wall-nearness {c3['settled_wall']:.3f} vs stayed-open {c3['open_wall']:.3f} "
         f"(outer-depth in B was ~flat 0.39 vs 0.45)"),
        ("C4", "and the wall tips the survivors", shot(c4["held"]),
         (f"genuine-(a) settlers {c4['settler_wall']:.3f} vs stayers {c4['stayer_wall']:.3f}"
          if c4.get("settler_wall") is not None else "too few genuine-(a) settlers/stayers to score")),
    ]
    tr = "".join(f"<tr><td class=c>{c}</td><td><b>{t}</b></td><td>{v}</td><td class=d>{d}</td></tr>" for c, t, v, d in rows)
    caps = {"true-stiffness.png": "Each malleable move from Experiment A, by how often the bare board forces it with no guess. A bar at 1.0 is secretly rigid — its wobble was only the scheduler's waiting line.",
            "interior-wall.png": "Settled ties are born with one option already on the verge of vanishing (wall-nearness near 0); open ties straddle the wall."}
    imgs = "".join(f'<figure><img src="{enc[n]}"><figcaption>{caps[n]}</figcaption></figure>' for n in ["true-stiffness.png", "interior-wall.png"] if n in enc)
    mc = s.get("method_control_rigid_settle")
    html = f"""<!doctype html><meta charset="utf-8"><title>The malleable chase</title>
<style>
 body{{max-width:900px;margin:28px auto;padding:0 16px;font:17px/1.55 system-ui,sans-serif;color:#1b2b33;background:#f6f7f8}}
 h1{{font-size:26px;margin:.2em 0}} h2{{font-size:20px;margin:1.3em 0 .4em;color:#294049}} .sub{{color:#5a6b73;font-size:16px}}
 table{{border-collapse:collapse;width:100%;margin:.6em 0;background:#fff;border-radius:8px;overflow:hidden}}
 td{{padding:9px 12px;border-bottom:1px solid #e7eaec;vertical-align:top}} .c{{font-weight:700;color:#167c9b;width:44px}} .d{{color:#55656d;font-size:13.5px}}
 figure{{margin:1.1em 0;background:#fff;padding:12px;border-radius:8px}} img{{width:100%}} figcaption{{color:#55656d;font-size:13.5px;margin-top:6px}}
 .note{{background:#fff;border-left:3px solid #d66a34;padding:10px 14px;border-radius:0 8px 8px 0;font-size:14.5px;color:#3a4a52}}
</style>
<h1>What actually tips the wobble</h1>
<p class=sub>Experiment C, the malleable chase. {s['bursted']} recurring-fingerprint ties forced-burst and measured against the interior wall.</p>
<h2>The called shots</h2>
<table>{tr}</table>
{imgs}
<p class=note>Method note: "secretly rigid" means the bare board forces the tie with no guess at all (forced-only burst). The rigid-fingerprint control burst-settled at a mean of {mc:.2f}. The interior-wall ruler is the compatibility region's geometry (how near one option is to vanishing), not a literal per-vertex partition depth — that literal measure is a deeper build, flagged for later. No claim about physical space or time.</p>
"""
    (HERE / "OPEN-MALLEABLE-CHASE.html").write_text(html, encoding="utf-8")
    print("Wrote figures and OPEN-MALLEABLE-CHASE.html")


if __name__ == "__main__":
    main()
