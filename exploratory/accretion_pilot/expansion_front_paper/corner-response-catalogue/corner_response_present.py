#!/usr/bin/env python3
"""
corner_response_present.py -- figures + a self-contained viewer for the catalogue.
Reads results/summary.json (written by corner_response.py) and produces:
  stiffness-line.png   the distribution of settle-fractions across recurring moves
  drawers.png          how every caught tie broke
  OPEN-CORNER-RESPONSE.html   a self-contained read-only viewer (embeds the figures)
Run after corner_response.py.
"""
from pathlib import Path
import json, base64, io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
A, B, CORE, GRAY, EDGE = "#167c9b", "#d66a34", "#713c91", "#dce1e4", "#929da3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 13})


def png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=150, facecolor="white", bbox_inches="tight"); plt.close(fig)
    return b.getvalue()


def stiffness_figure(stiffness, rigid_cut=0.9):
    vals = list(stiffness.values())
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    bins = [i / 10 for i in range(11)]
    rigid = [v for v in vals if v >= rigid_cut]
    mall = [v for v in vals if v < rigid_cut]
    ax.hist([mall, rigid], bins=bins, stacked=True, color=[B, A], edgecolor="white",
            label=[f"malleable (<{rigid_cut:.0%})  n={len(mall)}", f"rigid (≥{rigid_cut:.0%})  n={len(rigid)}"])
    ax.axvline(rigid_cut, color="#36464d", ls="--", lw=1)
    ax.set(xlabel="settle-fraction  (0 = always stays open  →  1 = always settles)",
           ylabel="number of recurring moves", xlim=(-0.02, 1.02),
           title="The stiffness line: how often does the same move settle its tie?")
    ax.legend(frameon=False, fontsize=10, loc="upper center")
    ax.spines[["top", "right"]].set_visible(False)
    return png(fig)


def drawers_figure(drawers):
    order = ["single_keystone", "committee", "stayed_open", "directly_chosen", "gone"]
    labels = {"single_keystone": "single keystone\n(one corner)", "committee": "committee\n(a bloc)",
              "stayed_open": "stayed open", "directly_chosen": "scheduler chose it", "gone": "built over"}
    cols = {"single_keystone": A, "committee": CORE, "stayed_open": GRAY,
            "directly_chosen": "#b7c0c6", "gone": "#e7eaec"}
    items = [(k, drawers.get(k, 0)) for k in order if drawers.get(k, 0)]
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    bars = ax.bar([labels[k] for k, _ in items], [v for _, v in items],
                  color=[cols[k] for k, _ in items], edgecolor=EDGE)
    for bar, (_, v) in zip(bars, items):
        ax.text(bar.get_x() + bar.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=10)
    ax.set(ylabel="number of ties", title="How every caught tie broke")
    ax.spines[["top", "right"]].set_visible(False)
    return png(fig)


def shot(held):
    return ("✅ HELD" if held else "❌ did not hold")


def main():
    s = json.loads((RES / "summary.json").read_text())
    stiff = s.get("stiffness", {})
    figs = {"stiffness-line.png": stiffness_figure(stiff) if stiff else None,
            "drawers.png": drawers_figure(s["drawers"])}
    enc = {}
    for name, data in figs.items():
        if data:
            (HERE / name).write_bytes(data)
            enc[name] = "data:image/png;base64," + base64.b64encode(data).decode()

    a1, a2a, a2b, a3 = s["A1"], s["A2a"], s["A2b"], s["A3"]
    rows = [
        ("A1", "one corner usually does it", shot(a1["held"]),
         f"single keystones settle {a1['keystone']}/{a1['settled']} = {a1['frac']:.1%} of settled ties (pledged ≥ 60%)"),
        ("A2a", "and it really is the corner", shot(a2a["held"]),
         f"the deciding touch is a corner (vertex rule) in {a2a['corner']}/{a2a['keystone']} = {a2a['frac']:.1%} (pledged ≥ 80%)"),
        ("A2b", "not just any neighbour", shot(a2b["held"]),
         f"mean {a2b['mean_placebo']:.1%} of nearby tiles settle alone vs the keystone's 100% (pledged < 50%)"),
        ("A3", "reality has give", shot(a3["held"]),
         f"{a3['malleable']}/{a3['recurring']} = {a3['frac']:.1%} of recurring moves are malleable (pledged ≥ 15%)"),
    ]
    tr = "".join(f"<tr><td class=c>{c}</td><td><b>{t}</b></td><td>{v}</td><td class=d>{d}</td></tr>" for c, t, v, d in rows)
    imgs = "".join(f'<figure><img src="{enc[n]}"><figcaption>{cap}</figcaption></figure>'
                   for n, cap in [("drawers.png", "Every two-way tie across 24 fresh worlds, filed by how it broke."),
                                  ("stiffness-line.png", "Each recurring move placed by how often it settles. A clump at 1.0 is rigid; the scatter below is malleable — reality with give.")]
                   if n in enc)
    html = f"""<!doctype html><meta charset="utf-8"><title>The corner-response catalogue</title>
<style>
 body{{max-width:900px;margin:28px auto;padding:0 16px;font:17px/1.55 system-ui,-apple-system,sans-serif;color:#1b2b33;background:#f6f7f8}}
 h1{{font-size:27px;margin:.2em 0}} h2{{font-size:20px;margin:1.4em 0 .4em;color:#294049}}
 .sub{{color:#5a6b73;font-size:16px}}
 table{{border-collapse:collapse;width:100%;margin:.6em 0;background:#fff;border-radius:8px;overflow:hidden}}
 td{{padding:9px 12px;border-bottom:1px solid #e7eaec;vertical-align:top}}
 .c{{font-weight:700;color:#167c9b;width:48px}} .d{{color:#55656d;font-size:14px}}
 figure{{margin:1.2em 0;background:#fff;padding:12px;border-radius:8px}} img{{width:100%}}
 figcaption{{color:#55656d;font-size:14px;margin-top:6px}}
 .note{{background:#fff;border-left:3px solid #d66a34;padding:10px 14px;border-radius:0 8px 8px 0;font-size:15px;color:#3a4a52}}
</style>
<h1>One corner, one decision</h1>
<p class=sub>The corner-response catalogue &mdash; Experiment A. {s['total_ties']} two-way ties caught across 24 fresh, unseen worlds. Shots called before any world was grown.</p>
<h2>The called shots</h2>
<table>{tr}</table>
{imgs}
<h2>What this says, in plain words</h2>
<p>When the growing edge faces a tie, it mostly makes up its mind through a <b>single tile meeting at a single corner</b> &mdash; a keystone handshake &mdash; and it really is the corner doing it, not just any neighbour crowding in. But the same move does <i>not</i> always do the same thing: a good share of recurring moves settle only some of the time. Reality here has give.</p>
<p class=note>This is a study of how a growing Penrose tiling settles its own open choices. It makes no claim about matter, time, or physical space. Whether the corner-handshake is the acceptance-window truncation of the directional-balance paper is Experiment B; whether stiffness predicts how long structures last is the bridge to the endurance work. Both are later rungs.</p>
"""
    (HERE / "OPEN-CORNER-RESPONSE.html").write_text(html, encoding="utf-8")
    print("Wrote figures and OPEN-CORNER-RESPONSE.html")


if __name__ == "__main__":
    main()
