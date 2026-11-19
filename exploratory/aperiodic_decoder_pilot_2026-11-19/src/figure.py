"""One figure Katie can read by eye: three rows (square / AB / Penrose), each drawing the
actual patch twice. Left column colours the six eligible edges by thick - thin; right by
diamond - thin. Shared diverging scale centred at zero; untested edges neutral grey; each
tested edge labelled with its short id. An all-zero map is a result worth showing."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import TwoSlopeNorm, Normalize

RESULTS = Path(__file__).resolve().parents[1] / 'results'
GEOM = Path(__file__).resolve().parents[2] / 'aperiodic_qec_geometry_2026-11-19' / 'results'
PATCHES = ('square', 'AB', 'Penrose')
CMAP = plt.get_cmap('RdBu_r')
NEUTRAL = '#d9d9d9'


def patch_geom(fam):
    d = json.loads((GEOM / f'{fam}.json').read_text())
    xy = {v['id']: v['xy'] for v in d['vertices']}
    edges = [(e['vertices'][0], e['vertices'][1], e['id']) for e in d['edges']]
    elig = {e['edge']: e for e in d['eligible']}
    return xy, edges, elig, d


def draw(ax, fam, metric_by_edge, short_by_edge, norm):
    xy, edges, elig, _ = patch_geom(fam)
    ends = {eid: (u, v) for (u, v, eid) in edges}
    for (u, v, eid) in edges:                       # all edges: light grey skeleton
        x = [xy[u][0], xy[v][0]]; y = [xy[u][1], xy[v][1]]
        ax.plot(x, y, color=NEUTRAL, lw=1.4, zorder=1, solid_capstyle='round')
    for eid in elig:                                # eligible edges: coloured
        u, v = ends[eid]
        val = metric_by_edge.get(eid)
        col = CMAP(norm(val)) if val is not None else NEUTRAL
        x = [xy[u][0], xy[v][0]]; y = [xy[u][1], xy[v][1]]
        ax.plot(x, y, color=col, lw=5.2, zorder=3, solid_capstyle='round')
        mx, my = (xy[u][0] + xy[v][0]) / 2, (xy[u][1] + xy[v][1]) / 2
        ax.annotate(short_by_edge.get(eid, ''), (mx, my), fontsize=7, ha='center',
                    va='center', zorder=4,
                    bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.75))
    ax.set_aspect('equal'); ax.axis('off')


def main():
    flat = json.loads((RESULTS / 'edges.json').read_text())['rows']
    by_fam = {}
    for r in flat:
        by_fam.setdefault(r['family'], {})[r['edge_id']] = r
    vmax = max(abs(r['thick_minus_thin_pp']) for r in flat)
    vmax = max(vmax, max(abs(r['diamond_minus_thin_pp']) for r in flat), 1e-6)
    norm = (TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax) if vmax > 0
            else Normalize(-1, 1))
    cols = [('thick_minus_thin_pp', 'cost of forgetting   (thick − thin, pp)'),
            ('diamond_minus_thin_pp', 'what 8 old readings recover   (diamond − thin, pp)')]
    fig, axes = plt.subplots(3, 2, figsize=(10.5, 13.2))
    for i, fam in enumerate(PATCHES):
        rows = by_fam.get(fam, {})
        short = {eid: r['short_id'] for eid, r in rows.items()}
        for j, (key, _) in enumerate(cols):
            ax = axes[i][j]
            metric = {eid: r[key] for eid, r in rows.items()}
            draw(ax, fam, metric, short, norm)
            if j == 0:
                ax.set_title(fam, fontsize=13, loc='left', fontweight='bold', x=-0.02)
    for j, (_, lab) in enumerate(cols):
        axes[0][j].annotate(lab, (0.5, 1.06), xycoords='axes fraction', ha='center',
                            fontsize=11, fontweight='bold')
    sm = ScalarMappable(norm=norm, cmap=CMAP); sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, orientation='horizontal', fraction=0.035, pad=0.03,
                        aspect=46)
    cbar.set_label('percentage points  (blue = archive/skin helps · red = hurts · white = 0)',
                   fontsize=10)
    fig.suptitle('Delayed-erasure re-judgment across 18 certified loss edges\n'
                 'square (degree-fixed control) · Ammann–Beenker · Penrose',
                 fontsize=13.5, y=0.97)
    fig.savefig(RESULTS / 'heatmap.png', dpi=140, bbox_inches='tight')
    fig.savefig(RESULTS / 'heatmap.svg', bbox_inches='tight')
    print('WROTE results/heatmap.png, results/heatmap.svg   vmax=%.4g pp' % vmax)


if __name__ == '__main__':
    main()
