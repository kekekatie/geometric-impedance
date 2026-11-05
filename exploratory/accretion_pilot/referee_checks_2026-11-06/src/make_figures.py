#!/usr/bin/env python3
"""
make_figures.py -- one figure per check, from the saved results JSONs.

  figures/check4a_forced_diff.png   A/B forced-closure diff: a representative diff map
                                     (w0) + aspect-ratio bar across 22 forks vs the
                                     single-strip threshold (none qualify).
  figures/check4b_arc_scores.png     arc reader-outcome distributions (open vs closed),
                                     recovery skins and jammed bands; A-selecting count.
  figures/check3a_loop_closure.png   max |b_perp| per band (all zero) vs tolerance.
  figures/check3b_offset_profile.png Chebyshev-centre offset profiles (ramp vs step).
"""
from __future__ import annotations
import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rc_common as RC

R = RC.RESULTS
F = RC.FIGURES
F.mkdir(parents=True, exist_ok=True)


def fig_4a():
    data = json.loads((R / "check4a_forced_diff.json").read_text())
    forks = data["forks"]
    # representative diff map: recompute small world w0 (fast)
    fk = RC.RD.load_forks()
    w = 0; Sstar = fk[w]["Sstar"]; A = fk[w]["cs"][0]; B = fk[w]["cs"][1]
    cA, *_ = RC.forced_closure(list(Sstar) + [A])
    cB, *_ = RC.forced_closure(list(Sstar) + [B])
    ka = {RC.dk(t): t for t in cA}; kb = {RC.dk(t): t for t in cB}
    a_only = [ka[k] for k in (set(ka) - set(kb))]
    b_only = [kb[k] for k in (set(kb) - set(ka))]
    shared = [ka[k] for k in (set(ka) & set(kb))]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))

    def poly(ax, t, color, a=0.9):
        xs = [z.real for z in t[1:]] + [t[1].real]
        ys = [z.imag for z in t[1:]] + [t[1].imag]
        ax.fill(xs, ys, color=color, alpha=a, lw=0.2, ec="white")
    for t in shared:
        poly(ax1, t, "#d9d9d9", 0.5)
    for t in a_only:
        poly(ax1, t, "#4e79a7")
    for t in b_only:
        poly(ax1, t, "#e15759")
    ax1.set_aspect("equal"); ax1.axis("off")
    ax1.set_title(f"w0 A/B forced-closure diff\nA-only (blue) {len(a_only)}  B-only (red) {len(b_only)}  "
                  f"— a 2-D region, not a worm strip", fontsize=10)

    worlds = [f["world"] for f in forks]
    aspects = [f.get("aspect_ratio") or 0 for f in forks]
    ax2.bar(range(len(worlds)), aspects, color="#59a14f")
    ax2.axhline(3.0, color="#e15759", ls="--", label="single-strip threshold (aspect ≥ 3)")
    ax2.set_xticks(range(len(worlds))); ax2.set_xticklabels([str(w) for w in worlds], rotation=90, fontsize=7)
    ax2.set_ylabel("diff aspect ratio (length / width)"); ax2.set_xlabel("world")
    ax2.set_title(f"P4a: single strip in {data['summary']['n_single_strip']}/22 forks — FAILED", fontsize=10)
    ax2.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(F / "check4a_forced_diff.png", dpi=130); plt.close(fig)
    print("wrote figures/check4a_forced_diff.png")


def fig_3a():
    data = json.loads((R / "check3a_loop_closure.json").read_text())
    bands = data["bands"]
    cases = [b["case"] for b in bands]
    mperp = [b["max_b_perp_abs"] for b in bands]
    mpar = [b["max_b_par_abs"] for b in bands]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = range(len(cases))
    ax.bar([i - 0.2 for i in x], mperp, width=0.4, label="max |b⊥| (perp holonomy)", color="#4e79a7")
    ax.bar([i + 0.2 for i in x], mpar, width=0.4, label="max |b∥| (physical closure)", color="#bab0ac")
    ax.axhline(data["summary"]["tolerance"], color="#e15759", ls="--", label="tolerance 1e-6")
    ax.set_xticks(list(x)); ax.set_xticklabels(cases, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("max over band's boundary loops")
    ax.set_title(f"P3a HELD: b⊥ = 0 on all {data['summary']['total_loops']} loops "
                 f"(0 lift conflicts); b∥ = 0 confirms closure", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(F / "check3a_loop_closure.png", dpi=130); plt.close(fig)
    print("wrote figures/check3a_loop_closure.png")


def fig_3b():
    data = json.loads((R / "check3b_offset_profile.json").read_text())
    bands = data["bands"]
    n = len(bands); cols = 3; rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(13, 2.6 * rows))
    axes = axes.flatten()
    for k, b in enumerate(bands):
        ax = axes[k]
        prof = [p for p in b["profile"] if p.get("centre") and p.get("defined")]
        ang = [p["angle"] for p in prof]
        c0 = [p["centre"][0] for p in prof]
        c1 = [p["centre"][1] for p in prof]
        ax.plot(ang, c0, ".", ms=2, color="#4e79a7", label="offset x")
        ax.plot(ang, c1, ".", ms=2, color="#e15759", label="offset y")
        ax.set_title(f"{b['case']}  {b['classification']} "
                     f"(conc {b['concentration_frac']:.2f}, {b['n_steps']} steps)", fontsize=8)
        ax.set_xlabel("angle around band (deg)", fontsize=7)
        ax.tick_params(labelsize=6)
        if k == 0:
            ax.legend(fontsize=6)
    for k in range(n, len(axes)):
        axes[k].axis("off")
    fig.suptitle(f"Check 3b: local best-fit offset (Chebyshev centre of F) vs angle — "
                 f"tally {data['summary']['classification_tally']}", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(F / "check3b_offset_profile.png", dpi=130); plt.close(fig)
    print("wrote figures/check3b_offset_profile.png")


def fig_4b():
    data = json.loads((R / "check4b_arc_scores.json").read_text())
    cats = ["B", "ambiguous", "empty_incompatible", "A", "unreconstructible"]
    colors = {"B": "#59a14f", "ambiguous": "#edc948", "empty_incompatible": "#bab0ac",
              "A": "#e15759", "unreconstructible": "#9c755f"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, dkey, title in [(axes[0], "recovery", "49 recovery skins"),
                            (axes[1], "jammed", "11 jammed bands")]:
        d = data[dkey]
        for conv, xoff in [("open_tally", 0), ("closed_tally", 1)]:
            tally = d[conv]; bottom = 0
            for cat in cats:
                v = tally.get(cat, 0)
                ax.bar(xoff, v, bottom=bottom, color=colors[cat], width=0.6,
                       label=cat if xoff == 0 else None)
                bottom += v
        ax.set_xticks([0, 1]); ax.set_xticklabels(["open", "closed"])
        ax.set_title(f"{title}\n{d['n_arcs']} arcs (K=32)", fontsize=10)
        ax.set_ylabel("arcs")
    axes[0].legend(fontsize=8, loc="upper right")
    na = data["summary"]["falsifier_A_on_B_case_total"]
    nc = data["summary"]["correct_A_on_A_case_total"]
    fig.suptitle(f"Check 4b: arc reader outcomes (crossing/parallel not evaluable — no worm line). "
                 f"never-A falsifiers (A on a B-case): {na}; correct A on A-true cases: {nc}", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(F / "check4b_arc_scores.png", dpi=130); plt.close(fig)
    print("wrote figures/check4b_arc_scores.png")


def main():
    import sys
    which = sys.argv[1:] or ["4a", "3a", "3b", "4b"]
    if "4a" in which: fig_4a()
    if "3a" in which: fig_3a()
    if "3b" in which: fig_3b()
    if "4b" in which: fig_4b()


if __name__ == "__main__":
    main()
