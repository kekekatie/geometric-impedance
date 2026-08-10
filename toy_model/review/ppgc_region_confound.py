#!/usr/bin/env python3
"""Region-shape confound checks for Pattern Persistence and Geometric Channelling.

Three checks, run in sequence:
  1. WR under uniform activation for each pipeline (the shape-only floor)
  2. Table I renormalised by each substrate own diffusion baseline
  3. Sensitivity of that renormalisation to the Penrose patch footprint
"""

import csv, numpy as np
rows=list(csv.DictReader(open("/home/user/geometric-impedance/substrates/real_penrose_lift.csv",encoding="utf-8-sig")))
P0=np.array([[float(r["x"]),float(r["y"])] for r in rows]); P0-=P0.mean(0)
rad=np.linalg.norm(P0,axis=1); P0=P0[np.argsort(rad)]

def pen_disc(n):                       # innermost n points, normalised to [-1,1]^2
    P=P0[:n].copy(); return P/np.abs(P).max()
def square(k):
    g=np.linspace(-1,1,k); return np.array([[x,y] for x in g for y in g])
def rand_square(n,seed):
    return np.random.default_rng(seed).uniform(-1,1,(n,2))

rng=np.random.default_rng(1)
# their protocol: mean over 15 starting positions
centres=rng.uniform(-0.5,0.5,(15,2))
def WRu(pts):                          # WR under UNIFORM activation: no dynamics
    return np.mean([np.linalg.norm(pts-c,axis=1).mean() for c in centres])

print("WR with NO dynamics at all - uniform activation, 15 starting positions")
print("(measures only the shape/extent of each point set)\n")
print(f"{'pipeline':<28} {'Pen':>7} {'Sq':>7} {'Rnd':>7} {'Pen/Sq':>8} {'Pen/Rnd':>8}")
cfg=[("A  ~600 pts",      611,  25,  625),
     ("B  ~3000 pts",    3000,  55, 3000),
     ("C  ~3877 pts",    3877,  55, 3877),
     ("D  625 subsampled", 625, 25,  625)]
for name,np_,k,nr in cfg:
    p,s,r = WRu(pen_disc(np_)), WRu(square(k)), WRu(rand_square(nr,7))
    print(f"{name:<28} {p:7.3f} {s:7.3f} {r:7.3f} {p/s:8.2f} {p/r:8.2f}")

print("\nPaper's Table I (after full dynamics):")
print(f"{'A  ~600 pts':<28} {0.515:7.3f} {0.823:7.3f} {0.803:7.3f} {0.63:8.2f} {0.64:8.2f}")
print(f"{'B  ~3000 pts':<28} {0.646:7.3f} {0.685:7.3f} {0.677:7.3f} {0.94:8.2f} {0.95:8.2f}")
print(f"{'C  ~3877 pts':<28} {0.646:7.3f} {0.685:7.3f} {0.674:7.3f} {0.94:8.2f} {0.96:8.2f}")
print(f"{'D  625 subsampled':<28} {0.638:7.3f} {0.698:7.3f} {0.690:7.3f} {0.91:8.2f} {0.93:8.2f}")

# density / connection-radius check for pipeline A (count+degree matched, NOT density matched)
pa=pen_disc(611); sa=square(25)
da = len(pa)/ (np.pi*1.0**2); ds = len(sa)/4.0
print(f"\nPipeline A densities:  penrose disc {da:.0f} pts/unit^2   square {ds:.0f} pts/unit^2"
      f"   ratio {da/ds:.2f}")
print(f"radius needed for ~18 neighbours: penrose {np.sqrt(18/(np.pi*da)):.3f}   square {np.sqrt(18/(np.pi*ds)):.3f}"
      f"   -> square steps {np.sqrt(18/(np.pi*ds))/np.sqrt(18/(np.pi*da)):.2f}x further per update")
import csv, numpy as np
rows=list(csv.DictReader(open("/home/user/geometric-impedance/substrates/real_penrose_lift.csv",encoding="utf-8-sig")))
P0=np.array([[float(r["x"]),float(r["y"])] for r in rows]); P0-=P0.mean(0)
P0=P0[np.argsort(np.linalg.norm(P0,axis=1))]
pen=lambda n:(lambda P:P/np.abs(P).max())(P0[:n].copy())
sq =lambda k:np.array([[x,y] for x in np.linspace(-1,1,k) for y in np.linspace(-1,1,k)])
rnd=lambda n,s:np.random.default_rng(s).uniform(-1,1,(n,2))
C=np.random.default_rng(1).uniform(-0.5,0.5,(15,2))
U=lambda pts:np.mean([np.linalg.norm(pts-c,axis=1).mean() for c in C])   # fully-diffused WR

TAB={"A":(0.515,0.823,0.803),"B":(0.646,0.685,0.677),
     "C":(0.646,0.685,0.674),"D":(0.638,0.698,0.690)}
CFG={"A":(611,25,625),"B":(3000,55,3000),"C":(3877,55,3877),"D":(625,25,625)}

print("Each substrate's WR normalised by its OWN fully-diffused baseline.")
print("Value = fraction of the way to full diffusion. LOWER = better retention.\n")
print(f"{'pipeline':<10} {'Penrose':>9} {'Square':>9} {'Random':>9}   {'winner':>10}")
for k in "ABCD":
    (pw,sw,rw)=TAB[k]; (n,g,nr)=CFG[k]
    up,us,ur = U(pen(n)), U(sq(g)), U(rnd(nr,7))
    a,b,c = pw/up, sw/us, rw/ur
    win = ["Penrose","Square","Random"][int(np.argmin([a,b,c]))]
    print(f"{k:<10} {a:9.3f} {b:9.3f} {c:9.3f}   {win:>10}")

print("\n--- consistency check: is the square lattice disc-cropped or a full square? ---")
print("Diffusion from a blob approaches the uniform WR from BELOW; it cannot exceed it.")
for k in "AD":
    (pw,sw,rw)=TAB[k]; (n,g,nr)=CFG[k]
    print(f"  pipeline {k}: reported Sq WR {sw:.3f} | full-square uniform {U(sq(g)):.3f}"
          f" (ok) | disc-cropped-square uniform {U(pen(n)):.3f}"
          f" ({'IMPOSSIBLE' if sw>U(pen(n)) else 'ok'})")
print("\n=> the square and random substrates fill the square domain; only Penrose is a disc.")
import csv, numpy as np
rows=list(csv.DictReader(open("/home/user/geometric-impedance/substrates/real_penrose_lift.csv",encoding="utf-8-sig")))
P0=np.array([[float(r["x"]),float(r["y"])] for r in rows]); P0-=P0.mean(0)
P0=P0[np.argsort(np.linalg.norm(P0,axis=1))]
C=np.random.default_rng(1).uniform(-0.5,0.5,(15,2))
U=lambda p:np.mean([np.linalg.norm(p-c,axis=1).mean() for c in C])
sq=lambda k:np.array([[x,y] for x in np.linspace(-1,1,k) for y in np.linspace(-1,1,k)])

# How disc-like is the patch? Sweep from a pure disc to a square-cropped patch.
def patch(n, squareness):
    """squareness=0 -> disc of n points; 1 -> n points cropped to a square box."""
    P=P0.copy()
    if squareness>0:
        keep=np.max(np.abs(P),axis=1) <= np.quantile(np.max(np.abs(P),axis=1), 1.0)
        P=P[keep]
        P=P[np.argsort(np.max(np.abs(P),axis=1)*squareness + np.linalg.norm(P,axis=1)*(1-squareness))]
    P=P[:n].copy()
    return P/np.abs(P).max()

print("Penrose uniform-WR baseline vs how the patch is cropped:\n")
print(f"{'crop':<26} {'uniform WR':>11}")
for s,lab in [(0.0,"pure disc (inner-fraction)"),(0.5,"intermediate"),(1.0,"square-cropped")]:
    print(f"{lab:<26} {U(patch(3000,s)):11.3f}")
print(f"{'25x25 square lattice':<26} {U(sq(25)):11.3f}")
print(f"{'55x55 square lattice':<26} {U(sq(55)):11.3f}")

print("\nWhat Penrose baseline would be needed for the paper's DIRECTION to survive")
print("normalisation in each pipeline (i.e. Penrose to still beat Square)?\n")
TAB={"A":(0.515,0.823,25),"B":(0.646,0.685,55),"C":(0.646,0.685,55),"D":(0.638,0.698,25)}
for k,(pw,sw,g) in TAB.items():
    need = pw / (sw/U(sq(g)))
    print(f"  pipeline {k}: needs Penrose uniform WR >= {need:.3f}"
          f"   (disc gives {U(patch(3000,0.0)):.3f}, square-cropped gives {U(patch(3000,1.0)):.3f})"
          f"  -> {'survives' if need <= U(patch(3000,1.0)) else 'does NOT survive even square-cropped'}")
