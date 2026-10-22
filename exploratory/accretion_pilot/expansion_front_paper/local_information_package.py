from pathlib import Path
import json,pickle,base64,html
import figures as F
import choice_tracking as C
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
H=Path(__file__).resolve().parent; O=H/'local-information'
ts=pickle.loads((H/'choice-tracking/replay.pkl').read_bytes())[0][42]['tiles']
inv=json.loads((H/'choice-tracking/inventory.json').read_text())[0]
site=next(x for x in inv['events'] if x['slice']==44)['site']
P=F.L.Patch(ts); ed=next(ed for ed in P.frontier() if C.ek(ed)==site); z=(ed[0]+ed[1])/2
local=[t for t in ts if min(abs(v-z) for v in t[1:])<=F.S+1e-12]
assert C.keys(F.D.candidates(P,*ed[:3]))==C.keys(F.D.candidates(F.L.Patch(local),*ed[:3]))
fig,axs=plt.subplots(1,2,figsize=(10,5))
F.draw(axs[0],ts,z,F.GRAY); F.draw(axs[0],local,z,F.A); F.setup(axs[0],ts,z)
F.draw(axs[1],local,z,F.A); axs[1].add_patch(Circle((0,0),1,fill=False,ec='#af3881',ls='--')); axs[1].set(xlim=(-2.5,2.5),ylim=(-2.5,2.5),aspect='equal'); axs[1].axis('off')
axs[0].set_title(f'Whole patch: {len(ts)} half-tiles'); axs[1].set_title(f'Local query: {len(local)} retained half-tiles\nSame two alternatives at the target edge')
for ax in axs:
    ax.plot([(v-z).real/F.S for v in ed[:2]],[(v-z).imag/F.S for v in ed[:2]],c='#af3881',lw=3)
fig.suptitle('What does this one frontier site need to see?',fontsize=16)
fig.text(.04,.03,'Pink line: original target edge. Dashed circle: radius S. Entire tiles touching the circle by a vertex are retained.\nThe local view extends beyond the circle; this is an information probe, not a new growth simulation.',fontsize=9)
fig.tight_layout(rect=(0,.12,1,.91)); fig.savefig(O/'local-view.png',dpi=160); plt.close(fig)
text='''# Local information and the proposed present

We keep two roles separate: an observer may retain a history for analysis, while the simulated rule must be audited for the information it actually uses. These tests concern the latter, at fixed sites in saved states.

## Result

All 841 frontier-edge observations matched the full patch's exact decorated candidate sets at every tested radius: 1, 2, 3, 4 and 6 in the engine's S length units (4,205 comparisons total). At radius 1, the neighbourhood retained an average 8.64 half-tiles, averaging 2.71% of the corresponding complete patch. There were no extra or missing candidate tiles at any tested radius.

## What was tested

Fifteen saved states: continuations 1 and 3 after slices 11, 19, 28, 42, 44 and 59, plus the changed-slice-29 history after slices 43, 44 and 45. Every original frontier edge in each state was queried. These are repeated observations in related histories, not 841 independent worlds. The list of states and radii was fixed in the script before inspecting results.

A neighbourhood retains each whole tile with any vertex within R*S of the queried edge's midpoint. Retained tiles can extend beyond that circle. This is a lateral spatial neighbourhood around a site, not a layer count measured backwards from the front. Smaller radii were not tested, so no minimum width is established.

Only original frontier edges are queried, with their original orientation/support information. Artificial edges exposed by cutting away tiles are never queried or grown. This prevents the earlier hole-refill problem, but means we have not demonstrated that a truncated patch can autonomously maintain its own frontier. Membership in the neighbourhood is selected using the recorded full geometry.

## Interpretation boundary

Supported here: the full engine's local candidate decisions at these sites can be reproduced from nearby retained geometry. A whole archive was unnecessary for these particular queries.

Not established: a physical thickness of now; globally extendible choices; a theorem for all patches; evolution using only a bounded moving band; or a scheduler that operates without global coordination. The original scheduler still waits until no forced site remains anywhere before making a guess, and prioritises by distance from a global origin. This test does not change that rule.

Future ancestry and propagation reports should identify whether a finding concerns local admissibility, scheduler selection, or an observer's reconstruction. The recent waiting times belong partly to scheduler selection and should not be interpreted as local physical lifetimes.

## Next useful test

Before changing scheduling, maintain an explicit active boundary with enough incident-tile information, keeping the archive available only to an independent verifier. Compare candidates and updates against the reference throughout growth. This would test whether the neighbourhood result can be turned into a working present-state representation. Scheduling locality remains a separate experiment.

## Reproduction

local_information_test.py and local_information_package.py run in expansion_front_paper with figures.py and the existing replay caches. Included scripts are records, not a standalone installation. measurements.json records all comparisons including retained sizes and candidate-set discrepancies. Original case 180fb0b920bb845b; baseline d4e00c5d4396c38bd69b265907b5f3d6c5bc030a. Exploratory finite-state audit.
'''
(O/'READ-ME-FIRST.md').write_text(text,encoding='utf-8')
page='<meta charset="utf-8"><title>What does the present need to see?</title><style>body{font:18px system-ui;max-width:1200px;margin:24px auto;line-height:1.5}img{width:100%}pre{white-space:pre-wrap;font:inherit}</style><h1>Small local views, matching alternatives</h1><p>Every tested local candidate set matched the full patch. This is evidence about information needed at a site, not a measurement of the physical width of now.</p>'
for name in ['local-view.png','local-information.png']: page+='<img alt="'+name+'" src="data:image/png;base64,'+base64.b64encode((O/name).read_bytes()).decode()+'">'
page+='<pre>'+html.escape(text)+'</pre>'
(O/'OPEN-LOCAL-NOW-CHECK.html').write_text(page,encoding='utf-8')
print('Report and illustrated local example saved.')
