#!/usr/bin/env python3
"""
v10_build.py -- construct & validate pentagrid patches, histories, and the reader.

Deliverables (no production dynamics): validated patches, labelled images,
diagnostics tables, reader sanity, and ONE tiny smoke fixture proving the
substrate-general engine runs and the reader returns numbers. Stops there.

Reproduce:
    python v10_build.py
"""
from __future__ import annotations

import json
import os

import numpy as np

import substrate_lib as sl

_HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_HERE, "results")
FIG = os.path.join(_HERE, "figures")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

RADIUS = 6.0
# 3 regular Penrose patches: distinct generic offset vectors, each sum 0.
REG_OFFSETS = [
    np.array([0.30, 0.10, -0.25, -0.25, 0.10]),   # mirror-symmetric (x-axis)
    np.array([0.12, 0.31, -0.08, -0.20, -0.15]),  # generic sum 0
    np.array([-0.05, 0.22, 0.17, -0.29, -0.05]),  # generic sum 0
]
# 3 perturbed patches: same base offset, jitter seeds 0,1,2, amplitude 0.30.
PERT_SEEDS = [0, 1, 2]
PERT_AMP = 0.30


def build_all():
    patches = {}
    for i, off in enumerate(REG_OFFSETS):
        patches[("regular", i)] = sl.make_regular(RADIUS, offsets=off, seed=0)
    for i, sd in enumerate(PERT_SEEDS):
        patches[("perturbed", i)] = sl.make_perturbed(RADIUS, jitter_amp=PERT_AMP,
                                                       seed=sd)
    return patches


def diagnostics(patches):
    rows = ["arm,patch,V,E,F,thick,thin,thick_over_thin,degree_hist,"
            "n_boundary_vertices,median_interior_boundary_dist,validate"]
    val_lines = []
    for (arm, i), sub in patches.items():
        ok, checks = sl.validate(sub)
        sc = sub.shape_counts()
        th, tn = sc.get("thick", 0), sc.get("thin", 0)
        bd = sub.boundary_distance()
        interior = [d for d in bd.values() if d > 0]
        med_bd = float(np.median(interior)) if interior else 0.0
        rows.append(f"{arm},{i},{sub.V},{sub.Ecount},{sub.F},{th},{tn},"
                    f"{th / max(1, tn):.4f},{sub.degree_hist()},"
                    f"{len(sub.boundary_vertices())},{med_bd:.1f},"
                    f"{'PASS' if ok else 'FAIL'}")
        val_lines.append(f"[{arm} #{i}] validate = {'PASS' if ok else 'FAIL'}")
        for k, (p, v) in checks.items():
            val_lines.append(f"    [{'ok' if p else 'XX'}] {k}: {v}")
    with open(os.path.join(RES, "patch_diagnostics.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    with open(os.path.join(RES, "validation_full.txt"), "w") as f:
        f.write("\n".join(val_lines) + "\n")
    return all("FAIL" not in r for r in rows)


def reader_sanity(patches):
    rows = ["arm,patch,hist_index,hist_len,edge_overlap,n_candidates,"
            "n_pos,n_neg,n_zero,swap_flips_sign,saturated_reader_value"]
    pairs_found = {}
    for (arm, i), sub in patches.items():
        pairs = sl.make_history_pairs(sub, k=3)
        pairs_found[(arm, i)] = len(pairs)
        for hidx, h in enumerate(pairs):
            rd = sl.reader_diagnostics(sub, h)
            rows.append(f"{arm},{i},{hidx},{h['len']},{h['edge_overlap']},"
                        f"{rd['n_candidates']},{rd['n_pos']},{rd['n_neg']},"
                        f"{rd['n_zero']},{rd['swap_flips_sign']},"
                        f"{rd['saturated_reader_value']:.1f}")
    with open(os.path.join(RES, "reader_sanity.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    return pairs_found


def smoke_fixture(patches):
    """Tiny: 60 steps, 2 seeds, one small patch, Growing rules. NOT the experiment.
    Confirms the substrate-general engine runs and the reader returns numbers."""
    sub = patches[("regular", 0)]
    h = sl.make_history_pairs(sub, k=1)[0]
    coeff = sl.reader_coefficients(sub, h)
    out = ["# TINY SMOKE FIXTURE (not a production run): regular patch #0,",
           "# impose history A vs B (3 passes), reset walker to S, 60 steps, 2 seeds.",
           "seed,history,S_high_after_history,S_high_after_60,n_active_after_60"]
    for seed in range(2):
        for hk, path in (("A", h["pathA"]), ("B", h["pathB"])):
            w = sl.SubstrateWorld(sub)
            for _ in range(3):                      # 3 history passes
                for a, b in zip(path[:-1], path[1:]):
                    w.reinforce(a, b); w.grow_from_edge(a, b)
            s0 = w.s_high(coeff)
            rng = np.random.default_rng(1000 + seed)
            v = h["S"]
            for _ in range(60):
                nxt = w.weighted_step(v, rng)
                w.reinforce(v, nxt); w.grow_from_edge(v, nxt); v = nxt
            out.append(f"{seed},{hk},{s0:.1f},{w.s_high(coeff):.1f},{w.n_activations}")
    with open(os.path.join(RES, "smoke_fixture.txt"), "w") as f:
        f.write("\n".join(out) + "\n")
    return out


def draw_patch(ax, sub, title):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    thick, thin = [], []
    for f in sub.faces:
        poly = Polygon([sub.pos[v] for v in f["verts"]], closed=True)
        (thick if f["shape"] == "thick" else thin).append(poly)
    ax.add_collection(PatchCollection(thick, facecolor="#cfe3f2",
                                      edgecolor="#5a5a5a", linewidths=0.5))
    ax.add_collection(PatchCollection(thin, facecolor="#f2dfcf",
                                      edgecolor="#5a5a5a", linewidths=0.5))
    for e in sub.boundary_edges():                 # boundary in bold
        p0, p1 = sub.pos[e[0]], sub.pos[e[1]]
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], "-", color="#b30000", lw=1.6)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=10)


def make_patch_images(patches):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    sr, sp = patches[("regular", 0)], patches[("perturbed", 0)]
    draw_patch(axes[0], sr, f"Regular pentagrid (Penrose)  V={sr.V} E={sr.Ecount} "
                            f"F={sr.F}\nthick={sr.shape_counts().get('thick',0)} "
                            f"thin={sr.shape_counts().get('thin',0)}")
    draw_patch(axes[1], sp, f"Perturbed pentagrid (amp={PERT_AMP})  V={sp.V} "
                            f"E={sp.Ecount} F={sp.F}\nthick="
                            f"{sp.shape_counts().get('thick',0)} "
                            f"thin={sp.shape_counts().get('thin',0)}")
    fig.suptitle("v10 construction: thick (blue) vs thin (tan) unit rhombi; "
                 "boundary in red. Same tile set, different arrangement.",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(FIG, "patches_v10.png"), dpi=150)
    plt.close(fig)


def make_reader_image(patches):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sub = patches[("regular", 0)]
    h = sl.make_history_pairs(sub, k=1)[0]
    coeff = sl.reader_coefficients(sub, h)
    fig, ax = plt.subplots(figsize=(8, 8))
    for e in sub.base_edges:                        # faint substrate
        p0, p1 = sub.pos[e[0]], sub.pos[e[1]]
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], "-", color="#dddddd", lw=0.5, zorder=1)
    # candidate diagonals colored by frozen reader sign
    for f in sub.faces:
        for d in f["diagonals"]:
            c = coeff.get(d, 0.0)
            col = "#d62728" if c > 0 else ("#1f77b4" if c < 0 else "#cccccc")
            p0, p1 = sub.pos[d[0]], sub.pos[d[1]]
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], "-", color=col, lw=0.8,
                    alpha=0.8, zorder=2)
    for path, col, lab in ((h["pathA"], "#000000", "A (left)"),
                           (h["pathB"], "#7f7f7f", "B (right)")):
        xs = [sub.pos[v][0] for v in path]; ys = [sub.pos[v][1] for v in path]
        ax.plot(xs, ys, "-o", color=col, lw=2.5, ms=4, zorder=4, label=lab)
    ax.plot(*sub.pos[h["S"]], "s", color="green", ms=11, zorder=5, label="S (start)")
    ax.plot(*sub.pos[h["E"]], "^", color="purple", ms=11, zorder=5, label="E (end)")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Frozen reader on regular patch: candidate diagonals coloured by\n"
                 "proximity sign (red = nearer A, blue = nearer B); paths A/B in "
                 "black/grey", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "reader_v10.png"), dpi=150)
    plt.close(fig)


def main():
    patches = build_all()
    all_valid = diagnostics(patches)
    print("All patches validate:", "PASS" if all_valid else "FAIL")
    pairs = reader_sanity(patches)
    print("History pairs found per patch:", {f"{a}#{i}": n for (a, i), n in pairs.items()})
    smoke = smoke_fixture(patches)
    print("Smoke fixture (tiny, not the experiment):")
    for line in smoke:
        if not line.startswith("#"):
            print("   ", line)
    make_patch_images(patches)
    make_reader_image(patches)

    cfg = {"radius": RADIUS, "regular_offsets": [o.tolist() for o in REG_OFFSETS],
           "perturbed_seeds": PERT_SEEDS, "perturbed_amp": PERT_AMP,
           "params": {"w0": 1.0, "alpha": 0.5, "w_max": 6.0, "theta": 4.0,
                      "w_init": 1.0, "reader_thresh": 5.5},
           "note": "construction & feasibility only; no production dynamics run",
           "env": {"numpy": np.__version__}}
    with open(os.path.join(RES, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"Wrote results/ and figures/ under {_HERE}")


if __name__ == "__main__":
    main()
