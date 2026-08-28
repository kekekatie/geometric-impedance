#!/usr/bin/env python3
"""
JUST FOR THE JOY OF IT (exploratory, not a metric) — drop a wavepacket in the middle of
the Penrose tiling and watch it spread. The confirmatory dynamical experiment needs its
sealed pre-reg; this is only us looking at the thing move.

Tight-binding H = adjacency; psi(t) = exp(-iHt) psi(0) via the eigenbasis. We start from a
single central site and watch |psi(v,t)|^2 crawl outward, and measure the mean-square
displacement MSD(t) ~ t^(2/dw): crystals spread ballistically (slope 2), disorder localizes
(slope 0), quasicrystals sit in a strange critical in-between.
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def system(N, extent):
    lifts, par, perp, ustar = generate(N, extent)
    E = build_edges(lifts, N, ustar)
    n = len(par)
    A = np.zeros((n, n))
    for i, j in E:
        A[i, j] = A[j, i] = 1.0
    ev, evec = np.linalg.eigh(A)
    v0 = int(np.argmin(np.hypot(par[:, 0], par[:, 1])))     # central site
    c = evec[v0, :]                                          # overlap of start with each mode
    return dict(par=par, ev=ev, evec=evec, v0=v0, n=n, E=E)


def amp(sysd, t):
    psi = sysd["evec"] @ (sysd["evec"][sysd["v0"], :] * np.exp(-1j * sysd["ev"] * t))
    return np.abs(psi) ** 2


def msd(sysd, t):
    p = amp(sysd, t)
    d2 = np.sum((sysd["par"] - sysd["par"][sysd["v0"]]) ** 2, axis=1)
    return float((p * d2).sum())


def snapshots(N=10, extent=14):
    s = system(N, extent)
    par = s["par"]
    ts = [0.0, 1.5, 3.5, 7.0, 14.0, 28.0]
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 9))
    for ax, t in zip(axes.ravel(), ts):
        w = amp(s, t)
        w = w / (w.max() + 1e-12)
        ax.scatter(par[:, 0], par[:, 1], c="0.9", s=5, linewidths=0)
        ax.scatter(par[:, 0], par[:, 1], c=w, s=8 + 60 * w, cmap="magma",
                   vmin=0, vmax=1, linewidths=0)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"t = {t:g}", fontsize=11)
    fig.suptitle(f"A wave let loose on {NAME[N]} — |ψ(t)|² spreading from one site "
                 f"(exploratory, for the joy of it)", fontsize=13)
    out = __file__.rsplit("/", 1)[0] + f"/wave_motion_{NAME[N]}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print("wrote", out)


def spreading_curve():
    fig, ax = plt.subplots(figsize=(8.5, 6))
    t = np.linspace(0.3, 40, 80)
    for N, col in ((10, "#e45756"), (8, "#4c78a8"), (12, "#54a24b")):
        s = system(N, 14)
        m = np.array([msd(s, tt) for tt in t])
        ax.loglog(t, np.sqrt(m), color=col, lw=2, label=NAME[N])
    # reference slopes: ballistic (crystal) and diffusive
    ax.loglog(t, 0.9 * t, "k--", lw=1, alpha=.6, label="ballistic (crystal)  slope 1")
    ax.loglog(t, 1.4 * np.sqrt(t), "k:", lw=1, alpha=.6, label="diffusive  slope ½")
    ax.set_xlabel("time"); ax.set_ylabel("spread  √⟨r²⟩ from the start site")
    ax.set_title("How fast does the wave crawl outward?\n"
                 "quasiperiodic spreading sits between ballistic and diffusive (exploratory)")
    ax.legend(frameon=False, fontsize=9)
    out = __file__.rsplit("/", 1)[0] + "/wave_spreading.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print("wrote", out)


def animate(N=10, extent=14, nframes=48, tmax=26.0):
    s = system(N, extent)
    par = s["par"]
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("#0e0e12"); ax.set_facecolor("#0e0e12")
    ax.scatter(par[:, 0], par[:, 1], c="#26262e", s=5, linewidths=0)
    sc = ax.scatter(par[:, 0], par[:, 1], c=np.zeros(s["n"]), s=10, cmap="magma",
                    vmin=0, vmax=1, linewidths=0)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ttl = ax.set_title("", color="#e8e8ee", fontsize=12)
    ax.set_xlim(par[:, 0].min()*1.02, par[:, 0].max()*1.02)
    ax.set_ylim(par[:, 1].min()*1.02, par[:, 1].max()*1.02)
    times = np.linspace(0, tmax, nframes)

    def frame(i):
        w = amp(s, times[i])
        w = w / (w.max() + 1e-12)
        sc.set_array(w)
        sc.set_sizes(8 + 90 * w)
        ttl.set_text(f"a wave on {NAME[N]}   ·   t = {times[i]:4.1f}")
        return sc, ttl

    an = FuncAnimation(fig, frame, frames=nframes, blit=False)
    out = __file__.rsplit("/", 1)[0] + f"/wave_motion_{NAME[N]}.gif"
    an.save(out, writer=PillowWriter(fps=12))
    print("wrote", out)


if __name__ == "__main__":
    snapshots(10)
    spreading_curve()
    animate(10)
