"""Figures for the route prediction. draw_prediction(): the committed, UNCOLOURED pencil
mark -- each patch drawn once with the predicted on-route edge circled and the matched
off-route edge boxed. draw_result(): the side-by-side prediction vs measured map (filled
after decoding), same orientation and edge IDs, shared zero-centred scale, untested edges
grey."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.cm import ScalarMappable
from matplotlib.colors import TwoSlopeNorm

RESULTS = Path(__file__).resolve().parents[1] / 'results'
PATCHES = ('AB_1', 'Penrose_1', 'Penrose_2')
NEUTRAL = '#cfcfcf'
ELIG = '#9ecae1'


def _geom(name):
    d = json.loads((RESULTS / f'{name}.json').read_text())
    xy = {v['id']: v['xy'] for v in d['vertices']}
    ends = {e['id']: tuple(e['vertices']) for e in d['edges']}
    return d, xy, ends


def _skeleton(ax, d, xy, ends):
    for e in d['edges']:
        u, v = e['vertices']
        ax.plot([xy[u][0], xy[v][0]], [xy[u][1], xy[v][1]], color=NEUTRAL, lw=1.3,
                zorder=1, solid_capstyle='round')
    for e in d['eligible']:                      # eligible edges a touch darker
        u, v = ends[e['edge']]
        ax.plot([xy[u][0], xy[v][0]], [xy[u][1], xy[v][1]], color=ELIG, lw=2.6,
                zorder=2, solid_capstyle='round')
    ax.set_aspect('equal'); ax.axis('off')


def _mid(xy, ends, eid):
    u, v = ends[eid]
    return (xy[u][0] + xy[v][0]) / 2, (xy[u][1] + xy[v][1]) / 2


def draw_prediction():
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.2))
    for ax, name in zip(axes, PATCHES):
        d, xy, ends = _geom(name)
        _skeleton(ax, d, xy, ends)
        pp = d['route']['predicted_pair']
        on, off = pp['on_route_edge'], pp['off_route_edge']
        ux, uy = _mid(xy, ends, on)
        fu, fv = ends[on]
        ax.plot([xy[fu][0], xy[fv][0]], [xy[fu][1], xy[fv][1]], color='#d6604d', lw=4.5,
                zorder=4, solid_capstyle='round')
        r = 0.42
        ax.add_patch(Circle((ux, uy), r, fill=False, ec='#b2182b', lw=2.2, zorder=5))
        ax.annotate(f'ON e{on}', (ux, uy + r + 0.18), ha='center', fontsize=9,
                    fontweight='bold', color='#b2182b', zorder=6)
        ox, oy = _mid(xy, ends, off)
        ou, ov = ends[off]
        ax.plot([xy[ou][0], xy[ov][0]], [xy[ou][1], xy[ov][1]], color='#4d4d4d', lw=4.5,
                zorder=4, solid_capstyle='round', ls=(0, (2, 1.4)))
        ax.annotate(f'OFF e{off}', (ox, oy - r - 0.18), ha='center', va='top', fontsize=9,
                    fontweight='bold', color='#4d4d4d', zorder=6)
        nw3 = d['route']['n_weight3_x_supports']
        mm = f"deg {'=' if pp['degree_mismatch'] == 0 else '≠'}, dist Δ{pp['dist_mismatch']}"
        ax.set_title(f'{name}\n{nw3} shortest X-routes · match: {mm}', fontsize=10.5)
    fig.suptitle('Prediction (geometry only): the CIRCLED on-route edge will cost more to '
                 'forget than the matched OFF-route edge   —   G(on) − G(off) > 0',
                 fontsize=12, y=1.02)
    fig.savefig(RESULTS / 'prediction.png', dpi=140, bbox_inches='tight')
    fig.savefig(RESULTS / 'prediction.svg', bbox_inches='tight')
    print('WROTE results/prediction.png, results/prediction.svg')


def draw_result():
    """Pencil-mark prediction (left) beside the measured thick-thin map (right), per patch.
    Same orientation + edge IDs; shared zero-centred scale; untested edges grey."""
    res = json.loads((RESULTS / 'paired_results.json').read_text())
    gmap = {}
    for k, v in res['edges'].items():
        gmap.setdefault(v['patch'], {})[v['edge']] = v['G_thick_thin']
    vmax = max((abs(g) for p in gmap.values() for g in p.values()), default=1e-3) or 1e-3
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    cmap = plt.get_cmap('RdBu_r')
    fig, axes = plt.subplots(3, 2, figsize=(9.5, 13))
    for i, name in enumerate(PATCHES):
        d, xy, ends = _geom(name)
        # left: prediction mark
        axL = axes[i][0]; _skeleton(axL, d, xy, ends)
        pp = d['route']['predicted_pair']; on, off = pp['on_route_edge'], pp['off_route_edge']
        for eid, col, ls, lab in ((on, '#b2182b', '-', 'ON'), (off, '#4d4d4d', (0, (2, 1.4)), 'OFF')):
            u, v = ends[eid]
            axL.plot([xy[u][0], xy[v][0]], [xy[u][1], xy[v][1]], color=col, lw=4.2, ls=ls,
                     zorder=4, solid_capstyle='round')
        ux, uy = _mid(xy, ends, on)
        axL.add_patch(Circle((ux, uy), 0.42, fill=False, ec='#b2182b', lw=2, zorder=5))
        axL.set_title(f'{name} — prediction', fontsize=10, loc='left')
        # right: measured map
        axR = axes[i][1]; _skeleton(axR, d, xy, ends)
        for e in d['eligible']:
            eid = e['edge']; g = gmap.get(name, {}).get(eid)
            if g is None:
                continue
            u, v = ends[eid]
            axR.plot([xy[u][0], xy[v][0]], [xy[u][1], xy[v][1]], color=cmap(norm(g)), lw=5.2,
                     zorder=3, solid_capstyle='round')
            mx, my = _mid(xy, ends, eid)
            mk = '●' if eid == on else ('■' if eid == off else '')
            axR.annotate(f'e{eid}{mk}', (mx, my), fontsize=7.5, ha='center', va='center', zorder=5,
                         bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.75))
        axR.set_title(f'{name} — measured thick−thin', fontsize=10, loc='left')
    sm = ScalarMappable(norm=norm, cmap=cmap); sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, orientation='horizontal', fraction=0.03, pad=0.03, aspect=46)
    cbar.set_label('thick − thin (pp)   red = archive helps · ●=predicted on-route · ■=matched off-route',
                   fontsize=9)
    fig.suptitle('Route prediction vs measured archive benefit', fontsize=13, y=0.95)
    fig.savefig(RESULTS / 'result.png', dpi=140, bbox_inches='tight')
    fig.savefig(RESULTS / 'result.svg', bbox_inches='tight')
    print('WROTE results/result.png, results/result.svg  vmax=%.4g pp' % vmax)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'result':
        draw_result()
    else:
        draw_prediction()
