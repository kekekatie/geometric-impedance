#!/usr/bin/env python3
"""
endurance_bridge_present.py -- figures + viewer for Experiment D (a clean null),
plus Argon's partition-line visual bonus.
Reads results/summary.json; re-grows one world for the partition overlay.
"""
from pathlib import Path
import sys, json, base64, io, collections, hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))
sys.path.insert(0, str(HERE.parent / "depth-direction-lenses"))
sys.path.insert(0, str(HERE.parent.parent / "perp_map"))
import figures as F
import perp_map as PM
import endurance_observer as T
import depth_direction as DD

L, S = F.L, F.S
RES = HERE / "results"
A, B2, CORE = "#167c9b", "#d66a34", "#111111"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 12})


def png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=150, facecolor="white", bbox_inches="tight"); plt.close(fig)
    return b.getvalue()


def null_figure(reach, stiff):
    reach = np.asarray(reach); stiff = np.asarray(stiff)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12, 4.4))
    axL.hist(reach, bins=np.linspace(0, np.percentile(reach, 98), 40), color=A, edgecolor="white")
    axL.set(xlabel="forced-support reach (tiles)", ylabel="settlements",
            title="Reach distribution: one smooth spread, no ribs/hinges split (D2 ✗)")
    axL.spines[["top", "right"]].set_visible(False)
    # reach by stiffness band
    bands = [(0.0, 0.3), (0.3, 0.6), (0.6, 0.9), (0.9, 1.01)]
    meds = [np.median(reach[(stiff >= lo) & (stiff < hi)]) for lo, hi in bands]
    labels = ["0–0.3", "0.3–0.6", "0.6–0.9", "rigid\n0.9–1.0"]
    axR.bar(labels, meds, color=[B2, B2, B2, A], edgecolor="#929da3")
    axR.set(xlabel="fingerprint stiffness (how often it settles)", ylabel="median reach",
            title="Wobbly moves anchor BIGGER cascades than rigid (D1 ✗, and inverted)")
    axR.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return png(fig)


def partition_figure(world=3):
    w = DD.grow_world_b(world)
    tiles = [tuple([t[0]] + [complex(z) for z in t[1:]]) for t in w["tiles"]]
    K, pos, conf = PM.lift(tiles)
    kverts = set()
    for tie in w["ties"]:
        if tie["drawer"] == "single_keystone":
            for v in tie.get("keystone_vertices", []):
                kverts.add(tuple(v))
    # vertex type = reflection-folded canonical class of its completed star
    vtiles = collections.defaultdict(list)
    for t in tiles:
        for z in t[1:]:
            vtiles[L.key(z)].append(t)
    bylayer = collections.defaultdict(list)
    for v, k in K.items():
        bylayer[int(k.sum())].append(v)
    lay = max(bylayer, key=lambda l: len(bylayer[l])); verts = bylayer[lay]
    types = {}
    for v in verts:
        zc = pos.get(v)
        if zc is None:
            continue
        star = vtiles[v]
        import math
        ang = 0.0
        for t in star:
            o = [p for p in t[1:] if L.key(p) != v]
            if len(o) == 2 and abs(o[0] - zc) > 1e-9 and abs(o[1] - zc) > 1e-9:
                u, ww = o[0] - zc, o[1] - zc
                ang += math.acos(max(-1, min(1, (u.conjugate() * ww).real / (abs(u) * abs(ww)))))
        if abs(ang - 2 * math.pi) > 1e-6:          # only complete vertices have a well-defined type
            continue
        a = T.canonical(star, [], zc, False); b = T.canonical(star, [], zc, True)
        types[v] = hashlib.sha256(repr(min(a, b)).encode()).hexdigest()[:8]
    uniq = sorted(set(types.values()))
    cmap = plt.cm.tab20
    cidx = {u: cmap(i % 20) for i, u in enumerate(uniq)}
    fig, ax = plt.subplots(figsize=(7.4, 6.6))
    xs = [PM.perp(K[v]).real for v in types]; ys = [PM.perp(K[v]).imag for v in types]
    ax.scatter(xs, ys, c=[cidx[types[v]] for v in types], s=26, edgecolors="none", alpha=.9)
    kin = [v for v in kverts if v in K and v in types]
    ax.scatter([PM.perp(K[v]).real for v in kin], [PM.perp(K[v]).imag for v in kin],
               s=46, facecolors="none", edgecolors=CORE, linewidths=1.2, label="keystone corner")
    ax.set(aspect="equal", xlabel="perp coordinate 1", ylabel="perp coordinate 2",
           title=f"The acceptance window by vertex TYPE (world {world})\nkeystone corners cluster in the inner type-regions, not the outer rim")
    ax.legend(loc="lower right", fontsize=9, framealpha=.9)
    return png(fig), len(uniq)


def main():
    s = json.loads((RES / "summary.json").read_text())
    enc = {}
    enc["reach-null.png"] = null_figure(s["reach_values"], s["stiffness_values"])
    pf, ntypes = partition_figure()
    enc["partition-overlay.png"] = pf
    for name, data in enc.items():
        (HERE / name).write_bytes(data)
    encb = {n: "data:image/png;base64," + base64.b64encode(d).decode() for n, d in enc.items()}
    d1, d2, d3 = s["D1"], s["D2"], s["D3"]
    html = f"""<!doctype html><meta charset="utf-8"><title>The endurance bridge (a null)</title>
<style>
 body{{max-width:900px;margin:28px auto;padding:0 16px;font:17px/1.55 system-ui,sans-serif;color:#1b2b33;background:#f6f7f8}}
 h1{{font-size:25px;margin:.2em 0}} h2{{font-size:19px;margin:1.3em 0 .4em;color:#294049}} .sub{{color:#5a6b73;font-size:16px}}
 table{{border-collapse:collapse;width:100%;margin:.6em 0;background:#fff;border-radius:8px;overflow:hidden}}
 td{{padding:9px 12px;border-bottom:1px solid #e7eaec;vertical-align:top}} .c{{font-weight:700;color:#167c9b;width:44px}} .d{{color:#55656d;font-size:13.5px}}
 figure{{margin:1.1em 0;background:#fff;padding:12px;border-radius:8px}} img{{width:100%}} figcaption{{color:#55656d;font-size:13.5px;margin-top:6px}}
 .note{{background:#fff;border-left:3px solid #d66a34;padding:10px 14px;border-radius:0 8px 8px 0;font-size:14.5px;color:#3a4a52}}
</style>
<h1>The endurance bridge — a clean null</h1>
<p class=sub>Experiment D (structural version), {s['settlements']} settlements. The forced-support-reach proxy did not deliver; all three shots missed. Reported honestly, with the lesson.</p>
<h2>The called shots (all missed)</h2>
<table>
<tr><td class=c>D1</td><td><b>decisive births breed ribs</b></td><td>— did not hold</td><td class=d>Spearman(stiffness, reach) {d1['spearman']:.3f} (pledged &gt; 0.2), and <i>inverted</i>: rigid reach {d1['rigid_median']:.0f} vs malleable {d1['mall_median']:.0f}</td></tr>
<tr><td class=c>D2</td><td><b>two modes</b></td><td>— did not hold</td><td class=d>bimodality {d2['dip']:.3f} (pledged &gt; 0.5): one smooth spread</td></tr>
<tr><td class=c>D3</td><td><b>not the stopwatch</b></td><td>— did not hold</td><td class=d>Spearman(reach, frontier-speed) {d3['spearman']:.3f} (pledged |ρ|&lt;0.2): the proxy is partly timing-confounded</td></tr>
</table>
<figure><img src="{encb['reach-null.png']}"><figcaption>Left: reach is one smooth distribution, not two modes. Right: wobbly (malleable) settlements anchor larger cascades than rigid ones — the opposite of the hypothesis (and confounded, per D3).</figcaption></figure>
<h2>Visual bonus — Argon's partition overlay</h2>
<figure><img src="{encb['partition-overlay.png']}"><figcaption>The acceptance window coloured by vertex type ({ntypes} types this world). The window partitions into clear type-regions (green outer rim, a red mid-band, a varied centre); the keystone corners (black rings) live in the inner regions, not the outer rim — consistent with Argon's reading that choices occupy specific internal sub-windows. Showing them precisely on the partition <i>lines</i> would need the literal de Bruijn boundaries drawn, a deeper build.</figcaption></figure>
<p class=note>What D taught us: forced-support reach is the wrong proxy for endurance — it is partly a timing artifact (D3) and shows no rib/hinge split (D2). The faithful measure is same-class motif renewal in the hollow active-skin growth (Astra's finding-#9 machinery), which gets its own pre-registration. The suggestive inversion (wobbly sites cascade wider) is real in the data but untrustworthy while D3 fails. No claim about physical space or time.</p>
"""
    (HERE / "OPEN-ENDURANCE-BRIDGE.html").write_text(html, encoding="utf-8")
    print("Wrote figures and OPEN-ENDURANCE-BRIDGE.html")


if __name__ == "__main__":
    main()
