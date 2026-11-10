"""figures/gapfill_w7_s0.png -- F(W) (the offsets the nearby skin allows) drawn inside the
perp-space acceptance cells of the candidate gap tiles. F(W) sits entirely inside c's cell:
the address predicts c. Run with the amber env."""
import sys, math, cmath, json
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import address_gapfill as G
from address_gapfill import (first_disagreement, candidate_c, committed_window, gap_reader,
                             read_tiles, third_vertex, perp, dk, L, D, AF)
import math as _m


def pentagon_vertices(normals, h):
    """vertices of {y : n_i . y <= h} for a regular pentagon given its 5 facet normals."""
    import numpy as np
    V = []
    n = len(normals)
    for i in range(n):
        for j in range(i + 1, n):
            a = np.array([normals[i], normals[j]], float); b = np.array([h, h])
            try:
                y = np.linalg.solve(a, b)
            except np.linalg.LinAlgError:
                continue
            if all(nx * y[0] + ny * y[1] <= h + 1e-9 for nx, ny in normals):
                V.append((y[0], y[1]))
    # order by angle
    cx = sum(p[0] for p in V) / len(V); cy = sum(p[1] for p in V) / len(V)
    V.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    return V


def main():
    w, si, r = 7, 0, 2
    dd = first_disagreement(w, si, r); e = dd['edge']; band = dd['band']; cobj = candidate_c(dd)
    W, _ = committed_window(band, e, math.pi / 8)
    cands, Kz, wins, rank = gap_reader(w, si, W, e)
    raw, pay, st = read_tiles(w, si, W)
    poly = raw['polygon']
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    colors = plt.cm.tab10.colors
    # candidate cells: cell(t) = perp(Kz) - pentagon(layer)
    seen_v = {}
    ci = 0
    for cnd in cands:
        k = Kz[dk(cnd)]
        if k is None:
            continue
        kz = tuple(int(x) for x in k)
        if kz in seen_v:
            continue
        seen_v[kz] = True
        lay = int(sum(kz)); rk = rank[lay]
        pv = pentagon_vertices(wins[rk]['normals'], wins[rk]['h'])
        pz = perp(kz)
        cell = [(pz.real - y[0], pz.imag - y[1]) for y in pv]
        is_c = (Kz[dk(cobj)] is not None and kz == tuple(int(x) for x in Kz[dk(cobj)]))
        col = '#e15759' if is_c else colors[(ci % 8) + 1]
        ax.add_patch(Polygon(cell, closed=True, facecolor=col, alpha=0.25 if not is_c else 0.35,
                             edgecolor=col, lw=1.5,
                             label=('c (the queried tile)' if is_c else f'alt third={kz}')))
        tx = sum(p[0] for p in cell) / len(cell); ty = sum(p[1] for p in cell) / len(cell)
        ax.text(tx, ty, 'c' if is_c else '', ha='center', va='center', color='#b4242a', fontsize=16, fontweight='bold')
        ci += 1
    # F(W)
    ax.add_patch(Polygon([(p[0], p[1]) for p in poly], closed=True, facecolor='#4e79a7',
                         alpha=0.85, edgecolor='#1b3a5c', lw=2.0, label='F(W): offsets the skin allows', zorder=5))
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    mx = (min(xs) + max(xs)) / 2; my = (min(ys) + max(ys)) / 2
    ax.set_xlim(mx - 1.6, mx + 1.6); ax.set_ylim(my - 1.6, my + 1.6)
    ax.set_aspect('equal'); ax.set_xlabel('hidden offset  t  (perp-space, reader frame)')
    ax.set_title('w7-s0 r2 step 35, half-width pi/8\nF(W) lies entirely inside c\'s gap-cell: '
                 'the address predicts c  (p_c = 1)', fontsize=11)
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    fig.tight_layout()
    (HERE / 'figures').mkdir(exist_ok=True)
    fig.savefig(HERE / 'figures' / 'gapfill_w7_s0.png', dpi=130)
    print('wrote figures/gapfill_w7_s0.png')


if __name__ == '__main__':
    main()
