import sys, json, collections
sys.path.insert(0,'../reverse_loop_test')
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from geometry import star_vectors, SUBSTRATES
from torus_holonomy import build_torus

reg=json.load(open('phase0_registration.json'))
o=reg['ammann_beenker']['orders'][1]      # order 2, quantum 0.17157
M_a=np.array(o['M_a']); M_b=np.array(o['M_b'])
cfg=SUBSTRATES['ammann_beenker']; par_star,perp_star=star_vectors(cfg['N'],cfg['par_step'],cfg['perp_step'])
P_a=M_a@par_star; P_b=M_b@par_star
tor=build_torus('ammann_beenker',M_a,M_b,radius=12.0)
cell=tor['cell']; adj=tor['adj']
# positions of cell vertices
from geometry import Patch
pt=Patch('ammann_beenker',radius=12.0); pos={int(i):pt.par[int(i)] for i in cell}

# find a real fundamental a-cycle (holonomy ~ pi_perp(M_a)) via BFS tree
root=int(cell[0]); acc={root:np.zeros(2)}; par_v={root:None}; order=[root]; dq=collections.deque([root])
while dq:
    u=dq.popleft()
    for v,dp in adj.get(u,[]):
        if v not in acc: acc[v]=acc[u]+dp; par_v[v]=u; order.append(v); dq.append(v)
target=np.linalg.norm(M_a@perp_star)
loop=None
for u in order:
    for v,dp in adj.get(u,[]):
        h=acc[u]+dp-acc[v]
        if abs(np.linalg.norm(h)-target)<1e-3:
            # reconstruct u->root and v->root paths
            def up(x):
                p=[x]
                while par_v[p[-1]] is not None: p.append(par_v[p[-1]])
                return p
            pu=up(u); pv=up(v)
            loop=(pu, pv); break
    if loop: break

fig=plt.figure(figsize=(11,6.2))
ax=fig.add_axes([0.02,0.06,0.60,0.9])
# tile the unit cell 2x2 for context
segs=[]; 
shifts=[np.zeros(2),P_a,P_b,P_a+P_b]
seen=set()
for sh in shifts:
    for u in cell:
        for v,dp in adj.get(int(u),[]):
            # only draw physically-short (non-wrap) edges for clarity
            d=pos[int(v)]-pos[int(u)]
            if np.linalg.norm(d)<1.4:
                segs.append([pos[int(u)]+sh,pos[int(v)]+sh])
lc=LineCollection(segs,colors='#c9d6e5',linewidths=0.8,zorder=1); ax.add_collection(lc)
allp=np.array([pos[int(i)] for i in cell])
for sh in shifts:
    ax.scatter(allp[:,0]+sh[0],allp[:,1]+sh[1],s=6,color='#5b7aa5',zorder=2)
# unit cell outline
cellpoly=np.array([[0,0],P_a,P_a+P_b,P_b,[0,0]])+allp.min(0)*0
# shift outline to enclose the base tile
base=allp.min(0)
poly=np.array([base,base+P_a,base+P_a+P_b,base+P_b,base])
ax.plot(poly[:,0],poly[:,1],color='#b2182b',lw=1.4,ls='--',zorder=3,alpha=0.7)
# draw the winding loop
if loop:
    pu,pv=loop
    path=pu[::-1]+pv    # root..u then v..root
    P=np.array([pos[int(x)] for x in path])
    ax.plot(P[:,0],P[:,1],color='#1b7837',lw=2.6,zorder=4)
    ax.scatter([P[0,0]],[P[0,1]],s=60,color='#1b7837',zorder=5)
ax.set_aspect('equal'); ax.axis('off')
ax.set_title("Ammann–Beenker order-2 approximant\na loop that winds the period carries a quantum of address memory",
             fontsize=11)
ax.text(0.5,-0.02,r"$\oint d\perp \;=\; \pi_\perp(M_a) \;=\; 0.1716$",
        transform=ax.transAxes,ha='center',fontsize=13,color='#1b7837')

# price-list inset
ax2=fig.add_axes([0.68,0.16,0.30,0.66])
pl=json.load(open('results/v3_torus_pricelist.json'))['substrates']
for sub,c,lab,rr in [('ammann_beenker','#b2182b','Ammann–Beenker',np.sqrt(2)-1),
                     ('penrose','#2166ac','Penrose',2/(1+np.sqrt(5)))]:
    rows=pl[sub]['price_list']
    ks=[r['order'] for r in rows]; qs=[r['measured_quantum'] for r in rows]
    ax2.semilogy(ks,qs,'o-',color=c,label=lab,lw=2,ms=6)
ax2.set_xlabel('approximant order  k'); ax2.set_ylabel('holonomy quantum  |π⊥(M)|  (log)')
ax2.set_title('the price list:\nmemory bought with imperfection',fontsize=9.5)
ax2.legend(fontsize=8,frameon=False); ax2.set_xticks([1,2,3,4])
ax2.grid(True,which='both',alpha=0.15)
ax2.text(0.5,0.06,'ratio √2−1 (AB) · 1/φ (Penrose)\n→ 0 in the ideal limit',
         transform=ax2.transAxes,ha='center',fontsize=7.5,color='#444')
fig.savefig('figures/v3_approximant_winding_memory.png',dpi=150,bbox_inches='tight',facecolor='white')
print("saved figures/v3_approximant_winding_memory.png ; loop found:",loop is not None)
