import common as C
from common import IW
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection

def main():
    trace=C.old('trace-7-0.pkl');full=[r for r in trace['calls'] if not r['skin']][-1]['post']
    baseline=[IW.dtile(t) for t in trace['final_state']['tiles']]
    states=C.load('w7-s0-r2-c0-states.pkl');live=states['snapshots']['44'];livekeys=set(C.keys(live))
    lost=[t for t in baseline if repr(C.dk(t)) not in livekeys]
    fig,axes=plt.subplots(1,2,figsize=(11,5.4))
    for ax in axes:
        ax.add_collection(PolyCollection([[(z.real,z.imag) for z in t[1:]] for t in full],facecolors='#f0f1f2',edgecolors='#d9dde1',linewidths=.3))
        ax.add_collection(PolyCollection([[(z.real,z.imag) for z in t[1:]] for t in live],facecolors='#5b9fbe',edgecolors='white',linewidths=.25))
        ax.autoscale();ax.set_aspect('equal');ax.axis('off')
    axes[0].add_collection(PolyCollection([[(z.real,z.imag) for z in t[1:]] for t in lost],facecolors='#e7b15b',edgecolors='white',linewidths=.25))
    lines=[[(float(x),float(y)) for x,y in e] for e in states['actual'][-1]['scars']]
    for ax in axes:ax.add_collection(LineCollection(lines,colors='#b52946',linewidths=2))
    axes[0].set_title(f'Original full-boundary band: {len(baseline)} / {len(full)} tiles\nAmber = tiles removed by live-only pruning',fontsize=11)
    axes[1].set_title(f'Live-only 2S band: {len(live)} / {len(full)} tiles\nSame ordered continuation through step 44',fontsize=11)
    fig.suptitle('World 7 / B / stream 0 — step 44',fontsize=15)
    fig.text(.5,.045,'Blue: retained live-only tiles. Red: persistent scar edge tags.\nGrey background is evaluator history for illustration; the constructor does not retain those tiles.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.10,1,.94));out=C.HERE/'figures';out.mkdir(exist_ok=True)
    fig.savefig(out/'w7_retention.png',dpi=180);plt.close(fig)
if __name__=='__main__':main()
