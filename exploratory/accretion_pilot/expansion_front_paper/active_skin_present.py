"""Observer-only render and report; never imported by the growth worker."""
from pathlib import Path
import pickle,json,io,base64
import figures as F
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
H=Path(__file__).resolve().parent; O=H/'active-skin'

def main():
    report=json.loads((O/'results.json').read_text()); assert all(r['verified'] for r in report)
    runs=pickle.loads((O/'observer-frames.pkl').read_bytes()); images=[]
    for run in runs:
        encoded=[]
        for fr in run['frames']:
            fig,axs=plt.subplots(1,2,figsize=(11,5.7)); origin=F.CD.cen(fr['archive'][0])
            F.draw(axs[0],fr['archive'],origin,'#eceff1',edge='#d1d6d9')
            for ax in axs:
                F.draw(ax,fr['skin'],origin,F.A,edge='#a0c4ce')
                lines=[[((z-origin).real/F.S,(z-origin).imag/F.S) for z in e[:2]] for e in fr['frontier']]
                ax.add_collection(LineCollection(lines,colors='#af3881',linewidths=1))
                F.setup(ax,run['frames'][-1]['archive'],origin)
            axs[0].set_title('Verifier view: archive + current skin')
            axs[1].set_title('Growth engine: retained skin only')
            fig.suptitle(f'{run["case"]} | slice {fr["slice"]}',fontsize=17)
            fig.text(.05,.07,f'Engine retains {len(fr["skin"])} of {len(fr["archive"])} constructed half-tiles. Pink: true frontier.\nThe blank interior on the right is not a growth edge. The verifier never returns its archive to the engine.',fontsize=10)
            fig.tight_layout(rect=(0,.16,1,.93)); b=io.BytesIO(); fig.savefig(b,format='png',dpi=130); plt.close(fig)
            encoded.append('data:image/png;base64,'+base64.b64encode(b.getvalue()).decode())
            if fr['slice']==120: (O/(run['case']+'-final.png')).write_bytes(b.getvalue())
        images.append(dict(name=run['case'],slices=[f['slice'] for f in run['frames']],frames=encoded))
    page='''<!doctype html><meta charset="utf-8"><title>The active skin</title><style>body{font:18px system-ui;max-width:1200px;margin:24px auto;line-height:1.5;background:#f5f6f7}img{width:100%}input{width:48%}button,select{font:inherit}</style><h1>A growing boundary that drops its interior</h1><p>The left panel belongs to the verifier. The right shows the growth engine's retained geometry. Only selected checkpoints are shown; every intervening step was checked.</p><select id="case" aria-label="History"></select> <button id="play">Play</button> <input id="time" type="range" min="0" value="0" aria-label="Checkpoint"><span id="label"></span><img id="image" alt="Archive and active skin compared"><p>The scheduler still coordinates the entire frontier. This is a finite test of retained state, not a physical width measurement or proof of fully local growth.</p><script>const runs=DATA;const c=document.getElementById('case'),s=document.getElementById('time'),p=document.getElementById('play');let timer=null;runs.forEach((r,i)=>{let o=document.createElement('option');o.value=i;o.textContent=r.name;c.appendChild(o)});function show(){const r=runs[+c.value];s.max=r.frames.length-1;document.getElementById('image').src=r.frames[+s.value];document.getElementById('label').textContent='Slice '+r.slices[+s.value]}c.onchange=show;s.oninput=show;p.onclick=()=>{if(timer){clearInterval(timer);timer=null;p.textContent='Play'}else{timer=setInterval(()=>{s.value=(+s.value+1)%runs[+c.value].frames.length;show()},1100);p.textContent='Pause'}};show()</script>'''.replace('DATA',json.dumps(images))
    page=page.replace('<select id="case"', '<p><strong>Outcome:</strong> continuation 1 jams at slice 70 in BOTH engines (last illustrated checkpoint: 60). The other two histories reach 120. All checked decisions agree; this does not mean every history can continue forever.</p><select id="case"')
    (O/'WATCH-ACTIVE-SKIN.html').write_text(page,encoding='utf-8')
    total=sum(sum(r['edge_queries'] for r in run['rows']) for run in report)
    table='\n'.join(f'| {run["case"]} | {len(run["rows"])} | {run["rows"][-1]["retained"]} | {run["rows"][-1]["archive"]} | {100*run["rows"][-1]["retained"]/run["rows"][-1]["archive"]:.1f}% |' for run in report)
    text=f'''# Active skin: a self-maintaining retained-state engine

Open WATCH-ACTIVE-SKIN.html. Choose a history and scrub the checkpoints. The verifier's archived interior is pale grey on the left; the engine's actual retained tiles are blue on both panels. Pink marks the true frontier. The engine has no stored discarded interior geometry in its maintained state.

## Result

All {sum(len(r['rows']) for r in report)} steps passed: {total} pre-step frontier-edge candidate-set comparisons, all step outcomes and ordered placements, and every post-step frontier. Retained tiles were also checked against the verifier's archive. Both original histories reproduce the earlier cached states through slice 20. See results.json for jams/status and per-step counts.

| History | Steps checked | Final retained half-tiles | Full archive | Retained fraction |
|---|---:|---:|---:|---:|
{table}

The radius was fixed at 2*S before the run. No mismatch was repaired from the archive and no radius adjustment was made. This is a finite replay test on three related histories, not a universal guarantee.

**Continuation 1 jams at step 70 in both engines.** The other histories reach 120 without a jam. Agreement includes reproducing this failure, not solving it. The continuation-1 viewer's last illustrated checkpoint is 60, before the jam; its table records the actual stopping state at 70. A locally legal guess need not permit indefinite consistent growth.

## What the engine keeps

- Whole tiles with at least one vertex within 2*S of a true-frontier vertex, recomputed from retained state after each step. Whole tiles extend beyond the retention radius.
- An explicit true-frontier map, updated by the edges of newly placed tiles. It is never reconstructed from a cropped patch's exposed edges.
- Vertex/overlap indexes rebuilt from retained tiles, fixed matching-rule templates, a random generator and the step number.

The initial seed is supplied once. The growing engine runs in a separate process and accepts only STEP or STOP after initialization. It sends its decisions out, but receives no verifier results, geometric corrections or replacement tiles. This is an inspected program architecture, not an operating-system security sandbox. Fixed template tables are part of the rules, not a record of this history.

## What the verifier does

In the controller process, the full patch evolves independently using the historical candidate rules and patient scheduler. It compares candidate identities, step status/kind/count, exact ordered tile additions and frontier identities. Comparisons stop the experiment on mismatch; they cannot repair the worker. The checker shares the historical legality implementation, so it tests retained-state equivalence, not independent mathematical correctness of those rules.

## What this does and does not establish

In these runs, the retained representation maintained its frontier and matched full-history decisions throughout growth. This goes beyond extracting a local neighbourhood from a full archive at every query. Discarding happened in the worker; only the verifier kept the history.

The engine still coordinates across the whole frontier: forced growth anywhere has priority before a guess, and origin-distance ordering selects the guessed edge. Thus it is not yet an autonomous local scheduler. The skin's thickness is an engineering choice, not a measured physical present. Total memory can grow with frontier length; it is not fixed-size memory. Unexpected future geometries may expose failures, so a universal bound is not claimed.

No particles, physical time, or a physical expanding universe are identified by this experiment. Historical interpretation may use the archive, but the growth worker's decisions cannot.

## Reproduction and next step

ACTIVE_SKIN_PLAN.md records the protocol. active_skin_engine.py contains the state and worker; active_skin_verify.py runs comparisons; active_skin_present.py creates observer visuals. Run inside expansion_front_paper with its earlier figures.py and results/geometry.pkl, using the established Python environment. Packaged scripts are records, not a standalone installation. Original case 180fb0b920bb845b, continuations 1 and 3, plus the altered slice-29 history; horizon 120.

Next, test restart from a serialized skin-only state and broaden seeds/shapes before reducing the radius. Investigate scheduling locality as a separately labelled experiment; do not silently change scheduling to support an interpretation.
'''
    (O/'READ-ME-FIRST.md').write_text(text,encoding='utf-8')
    print(table); print('Candidate comparisons:',total)
if __name__=='__main__': main()
