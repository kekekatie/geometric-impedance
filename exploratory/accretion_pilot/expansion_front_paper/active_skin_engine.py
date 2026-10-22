"""State-retaining growth worker. No trajectory/cache reads or archive feedback.

Fixed rule catalogue is imported through figures, as in earlier experiments.
The protocol/controller lives separately in active_skin_verify.py.
"""
import random
import figures as F
L,D,S=F.L,F.D,F.S

def edge_id(p,q): return frozenset((L.key(p),L.key(q)))
def tile_id(t): return repr(D.dkey(t))
def frontier_id(e): return repr(sorted(edge_id(e[0],e[1])))

class ActiveSkin(L.Patch):
    def __init__(self, seed, radius=2):
        self.boundary={}; self.radius=radius; self.additions=[]
        super().__init__(list(seed))
        self.prune(); self.additions=[]

    def add(self,t):
        # Only newly attached tile geometry updates the true frontier.
        for p,q in ((t[1],t[2]),(t[2],t[3]),(t[3],t[1])):
            k=edge_id(p,q)
            if k in self.boundary: del self.boundary[k]
            else:
                pts=[z for z in t[1:] if L.key(z) in k]
                r=next(z for z in t[1:] if L.key(z) not in k)
                self.boundary[k]=(pts[0],pts[1],r,t)
        super().add(t); self.additions.append(t)

    def frontier(self):
        return sorted(self.boundary.values(),key=lambda e:(abs((e[0]+e[1])/2),L.key((e[0]+e[1])/2)))

    def prune(self):
        points={L.key(z):z for e in self.boundary.values() for z in e[:2]}
        reach=self.radius*S+1e-12
        keep=[t for t in self.tris if any(abs(z-v)<=reach for z in t[1:] for v in points.values())]
        dropped=len(self.tris)-len(keep)
        # The temporary local index has artificial edges. It is used for legal()
        # only; frontier() above always consults the explicit true boundary.
        index=L.Patch(keep)
        self.tris,self.edges,self.V=index.tris,index.edges,index.V
        return dropped

def inventory(P):
    return [(frontier_id(e),sorted(tile_id(t) for t in D.candidates(P,*e[:3]))) for e in P.frontier()]

def step(P,rng,s,swap29=False):
    if swap29 and s==29:
        fr=P.frontier()
        assert all(len(D.candidates(P,*e[:3]))>1 for e in fr)
        cs=F.SN.ordered(D.candidates(P,*fr[0][:3])); assert len(cs)==2
        drawn=rng.choice(cs); other=next(t for t in cs if D.dkey(t)!=D.dkey(drawn))
        P.add(other); return 'ok',1,'guess'
    return F.SN.patient(P,rng)

def worker(conn,seed,stream,radius,swap29):
    # Retain no second copy of the starting patch after construction.
    P=ActiveSkin(seed,radius); del seed
    rng=random.Random(stream)
    conn.send(dict(kind='ready',tiles=P.tris,frontier=[frontier_id(e) for e in P.frontier()]))
    s=0
    try:
        while True:
            command=conn.recv()
            if command=='STOP': break
            if command!='STEP': raise ValueError('Only STEP/STOP are accepted')
            s+=1; before=inventory(P); P.additions=[]
            status,n,kind=step(P,rng,s,swap29)
            placed=P.additions; P.additions=[]; dropped=P.prune()
            conn.send(dict(kind='step',slice=s,status=status,mode=kind,n=n,before=before,placed=placed,dropped=dropped,tiles=P.tris,frontier=[frontier_id(e) for e in P.frontier()]))
    except Exception:
        import traceback
        conn.send(dict(kind='error',traceback=traceback.format_exc()))
    finally: conn.close()
