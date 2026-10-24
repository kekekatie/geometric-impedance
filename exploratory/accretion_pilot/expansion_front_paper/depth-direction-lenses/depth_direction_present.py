#!/usr/bin/env python3
"""
depth_direction_present.py -- figures + viewer for Experiment B.
Reads results/summary.json and re-grows one world for the map. Produces:
  depth-map.png          the physical skin coloured by hull depth, keystones marked,
                         beside the hidden window (perp space) with inward arrows
  b3-depth-vs-settle.png settle-fraction vs choice-vertex depth, per recurring move
  OPEN-DEPTH-LENSES.html self-contained viewer (scorecard + figures)
Run after depth_direction.py.
"""
from pathlib import Path
import sys, json, base64, io, math, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))
sys.path.insert(0, str(HERE.parent.parent / "perp_map"))
import figures as F
import perp_map as PM
import depth_direction as DD

L, S, ZETA = F.L, F.S, PM.ZETA
RES = HERE / "results"
A, CORE = "#167c9b", "#111111"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 13})


def png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=150, facecolor="white", bbox_inches="tight"); plt.close(fig)
    return b.getvalue()


def map_figure(world=3):
    w = DD.grow_world_b(world)
    tiles = [tuple([t[0]] + [complex(z) for z in t[1:]]) for t in w["tiles"]]
    K, pos, conf = PM.lift(tiles)
    dep, _, _ = PM.depths(K)
    # keystone failing-vertices (the deciding corners)
    kverts = set()
    for tie in w["ties"]:
        if tie["drawer"] == "single_keystone":
            for v in tie.get("keystone_vertices", []):
                kverts.add(tuple(v))
    cmap = plt.cm.viridis; norm = plt.Normalize(0, 1)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 6.2))

    # LEFT: physical skin, tiles coloured by mean vertex depth
    polys, cols = [], []
    for t in tiles:
        ds = [dep[L.key(z)] for z in t[1:] if L.key(z) in dep]
        if not ds:
            continue
        polys.append([(z.real / S, z.imag / S) for z in t[1:]])
        cols.append(cmap(norm(np.mean(ds))))
    axL.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="#ffffff", linewidths=0.15))
    kx = [pos[v].real / S for v in kverts if v in pos]; ky = [pos[v].imag / S for v in kverts if v in pos]
    axL.scatter(kx, ky, s=14, facecolors="none", edgecolors=CORE, linewidths=0.8, label="keystone corner")
    p = np.array([q for poly in polys for q in poly]); lo = p.min(0) - 1; hi = p.max(0) + 1
    axL.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), aspect="equal"); axL.axis("off")
    axL.set_title("The skin, coloured by hidden depth\n(dark = shallow / window edge; bright = deep)")
    axL.legend(loc="lower right", fontsize=9, framealpha=.9)

    # RIGHT: the hidden window (one layer), perp coords, inward arrows, keystones
    bylayer = collections.defaultdict(list)
    for v, k in K.items():
        bylayer[int(k.sum())].append(v)
    lay = max(bylayer, key=lambda l: len(bylayer[l])); verts = bylayer[lay]
    adj = collections.defaultdict(list)
    for t in tiles:
        for a, b in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if abs(abs(b - a) - S) < 1e-4 * S:
                j, sg = PM.edge_dir(a, b); adj[L.key(a)].append((j, sg))
    P = {v: PM.perp(K[v]) for v in verts}
    xs = [P[v].real for v in verts if v in dep]; ys = [P[v].imag for v in verts if v in dep]
    cs = [dep[v] for v in verts if v in dep]
    sc = axR.scatter(xs, ys, c=cs, cmap=cmap, norm=norm, s=16, edgecolors="none", alpha=.85)
    # the deciding corners, and short arrows showing their inward pull
    kin = [v for v in kverts if v in P and v in dep and len(adj[v]) >= 4]
    axR.scatter([P[v].real for v in kin], [P[v].imag for v in kin], s=34, facecolors="none",
                edgecolors=CORE, linewidths=1.0, label="keystone corner")
    for v in kin[::3]:
        R = sum(sg * ZETA ** (2 * j) for j, sg in adj[v]) / len(adj[v])
        axR.arrow(P[v].real, P[v].imag, R.real * 0.45, R.imag * 0.45, head_width=0.045,
                  lw=0.6, color="#d66a34", alpha=.85, length_includes_head=True)
    axR.legend(loc="lower right", fontsize=9, framealpha=.9)
    axR.set(aspect="equal"); axR.set_title("The hidden window (one layer)\nshallow vertices at the rim, arrows pulling inward")
    axR.set_xlabel("perp coordinate 1"); axR.set_ylabel("perp coordinate 2")
    fig.colorbar(sc, ax=axR, fraction=0.046, pad=0.04, label="hull depth")
    fig.suptitle(f"The same gesture, front and back  (world {world})", fontsize=16)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return png(fig)


def b3_figure(scatter):
    if not scatter:
        return None
    md = [x for x, _ in scatter]; sf = [y for _, y in scatter]
    fig, ax = plt.subplots(figsize=(7.2, 5))
    ax.scatter(md, sf, s=28, color=A, alpha=.75, edgecolors="white")
    if len(md) > 2:
        b, a = np.polyfit(md, sf, 1)
        xs = np.linspace(min(md), max(md), 50); ax.plot(xs, b * xs + a, "--", color="#d66a34", lw=1.4)
    ax.set(xlabel="choice-vertex depth  (0 = window edge / shallow → 1 = deep)",
           ylabel="settle-fraction of the move", title="B3: does depth tip the wobble?")
    ax.spines[["top", "right"]].set_visible(False)
    return png(fig)


def shot(h):
    return "✅ HELD" if h else "— did not hold"


def main():
    s = json.loads((RES / "summary.json").read_text())
    enc = {}
    for name, data in [("depth-map.png", map_figure()), ("b3-depth-vs-settle.png", b3_figure(s.get("b3_scatter")))]:
        if data:
            (HERE / name).write_bytes(data); enc[name] = "data:image/png;base64," + base64.b64encode(data).decode()
    b1, b2, b3 = s["B1"], s["B2"], s["B3"]
    rows = [
        ("B1", "the deciding corner is shallow", shot(b1["held"]),
         f"keystone depth median {b1['keystone_median']:.3f} vs world median {b1['world_median']:.3f}; "
         f"below-world in {b1['wins']}/{b1['worlds']} worlds (pledged ≥ 20/24). "
         f"[shuffled control: {s['shuffled_B1_wins']}]"),
        ("B2", "and it pulls inward", shot(b2["held"]),
         f"inward alignment {b2['inward']:.3f} (pledged > 0.5), tangential {b2['tangential']:.3f} (~0), over {b2['n']} corners"),
        ("B3", "depth on trial for the wobble", shot(b3["held"]),
         f"depth↔settle Spearman {b3['spearman']:.3f} across {b3['moves']} moves (pledged ≤ −0.2); "
         f"settled corners depth {b3['settled_depth']:.3f} vs stayed-open {b3['open_depth']:.3f}"),
    ]
    tr = "".join(f"<tr><td class=c>{c}</td><td><b>{t}</b></td><td>{v}</td><td class=d>{d}</td></tr>" for c, t, v, d in rows)
    caps = {"depth-map.png": "Left: the physical skin, each tile coloured by its hidden-space depth, deciding corners ringed. Right: the same vertices in the hidden window — shallow ones at the rim, arrows pulling inward.",
            "b3-depth-vs-settle.png": "Each recurring move: how shallow its choice-corner sits (x) against how often it settles (y)."}
    imgs = "".join(f'<figure><img src="{enc[n]}"><figcaption>{caps[n]}</figcaption></figure>' for n in ["depth-map.png", "b3-depth-vs-settle.png"] if n in enc)
    html = f"""<!doctype html><meta charset="utf-8"><title>The depth-and-direction lenses</title>
<style>
 body{{max-width:980px;margin:28px auto;padding:0 16px;font:17px/1.55 system-ui,sans-serif;color:#1b2b33;background:#f6f7f8}}
 h1{{font-size:26px;margin:.2em 0}} h2{{font-size:20px;margin:1.3em 0 .4em;color:#294049}} .sub{{color:#5a6b73;font-size:16px}}
 table{{border-collapse:collapse;width:100%;margin:.6em 0;background:#fff;border-radius:8px;overflow:hidden}}
 td{{padding:9px 12px;border-bottom:1px solid #e7eaec;vertical-align:top}} .c{{font-weight:700;color:#167c9b;width:44px}} .d{{color:#55656d;font-size:13.5px}}
 figure{{margin:1.1em 0;background:#fff;padding:12px;border-radius:8px}} img{{width:100%}} figcaption{{color:#55656d;font-size:13.5px;margin-top:6px}}
 .note{{background:#fff;border-left:3px solid #d66a34;padding:10px 14px;border-radius:0 8px 8px 0;font-size:14.5px;color:#3a4a52}}
</style>
<h1>The same gesture, seen from the back</h1>
<p class=sub>Experiment B: the depth-and-direction lenses. A's {s['keystone_ties']} keystone corners, joined onto the hidden-space map of {s['ties']} ties across 24 worlds.</p>
<h2>The called shots</h2>
<table>{tr}</table>
{imgs}
<p class=note>Honest note on B1: the pledged yardstick compared keystone corners to the <i>whole world's</i> average depth, which is dragged shallow by the raw growing frontier — so it can read "failed" even when the corners are genuinely shallow. The fairer comparison, settled vs stayed-open corners (shown under B3), is the one to read for "shallower settles more." We report the pledged shot as-is regardless. This study marries A's events to a perpendicular-space structure; it makes no claim about physical space or literal holonomy.</p>
"""
    (HERE / "OPEN-DEPTH-LENSES.html").write_text(html, encoding="utf-8")
    print("Wrote figures and OPEN-DEPTH-LENSES.html")


if __name__ == "__main__":
    main()
