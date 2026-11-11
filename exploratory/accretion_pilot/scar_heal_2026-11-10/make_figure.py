"""figures/heal_w7_s0.png -- the scar site before (step 35) and after (horizon, HEAL arm):
the open scar edge e, the tile c that fills it, and the healed neighbourhood. Amber env."""
import sys, math
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scar_heal as H
from scar_heal import C, L, dk, IW, AF, S


def tiles_near(tiles, centre, radius):
    return [t for t in tiles if abs(sum(t[1:]) / 3 - centre) <= radius]


def draw(ax, tiles, e, c, title, span):
    emid = (e[0] + e[1]) / 2
    for t in tiles:
        xs = [z.real for z in t[1:]] + [t[1].real]; ys = [z.imag for z in t[1:]] + [t[1].imag]
        is_c = (dk(t) == dk(c))
        ax.fill(xs, ys, facecolor=('#e15759' if is_c else '#d9d9d9'),
                edgecolor='white', lw=0.5, alpha=(0.95 if is_c else 0.6), zorder=(3 if is_c else 1))
    # the scar edge e
    ax.plot([e[0].real, e[1].real], [e[0].imag, e[1].imag], color='#1b3a5c', lw=3, zorder=5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(emid.real - span, emid.real + span); ax.set_ylim(emid.imag - span, emid.imag + span)
    ax.set_title(title, fontsize=11)


def main():
    cp = H.checkpoint(7, 0, 2)
    e, c = cp['e'], cp['c']
    before = [IW.dtile(IW.etile(t)) for t in cp['hist_tris']]  # full history at step 35 (context)
    before_skin = L.Patch(IW.rebuild_skin(cp['state']).tris if False else [])  # not used
    # before = the live-only band at step 35 (reconstruct)
    P = IW.rebuild_skin(cp['state']); band35 = list(P.tris)
    heal = H.run_skinarm('HEAL', cp, H.HORIZON)
    after = [IW.dtile(t) for t in heal['final_band']]
    span = 7 * S
    emid = (e[0] + e[1]) / 2
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 6.4))
    draw(ax1, tiles_near(band35, emid, span * 1.4), e, c,
         'Before (step 35): the dormant scar edge e is open (blue);\nthe reduced skin admits c but keeps the skip label', span)
    draw(ax2, tiles_near(after, emid, span * 1.4), e, c,
         f"After (step {H.HORIZON}, HEAL): c placed (red), labelled edge e closes;\n"
         f"but c's long-side base never settles (pruned in 2S/3S, re-pins in 1S)  -> not a strict heal", span)
    fig.suptitle("w7-s0 r2: forgetting the witness closes edge e, but relocates the misfit to c's base", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    (HERE / 'figures').mkdir(exist_ok=True)
    fig.savefig(HERE / 'figures' / 'heal_w7_s0.png', dpi=130)
    print('wrote figures/heal_w7_s0.png')


if __name__ == '__main__':
    main()
