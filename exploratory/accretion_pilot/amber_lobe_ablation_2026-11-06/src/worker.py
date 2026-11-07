"""Constructor receives retained state only; evaluator/caches never consulted here."""
import common as C
from common import L,D,S,E,IW,AF,SCN,dk

class LiveSkin(E.ActiveSkin):
    def thin(self,pinned,collar=0):
        live=[e for e in self.frontier() if AF.edge_id(*e[:2]) not in pinned and D.candidates(self,*e[:3])]
        centres={L.key(z):z for e in live for z in e[:2]}
        scar_points={L.key(z):z for e in self.frontier() if AF.edge_id(*e[:2]) in pinned for z in e[:2]}
        reach=self.radius*S+1e-12
        keep=[t for t in self.tris if any(abs(z-v)<=reach for z in t[1:] for v in centres.values()) or
              (collar>0 and any(abs(z-v)<=collar*S+1e-12 for z in t[1:] for v in scar_points.values()))]
        n=len(self.tris)-len(keep);index=L.Patch(keep)
        self.tris,self.edges,self.V=index.tris,index.edges,index.V
        self.boundary={k:(p,q,r,None) for k,(p,q,r,o) in self.boundary.items()}
        self.additions=[]
        return dict(dropped=n,live_centres_edges=len(live),retained=len(keep),
                    metadata_edges=len(self.boundary),metadata_coordinates=len({L.key(z) for e in self.boundary.values() for z in e[:3]}),
                    metadata_coordinates_outside_tiles=len({L.key(z) for e in self.boundary.values() for z in e[:3]}-set(self.V)))

def constructor(conn,state,collar):
    try:
        P=IW.rebuild_skin(state);P.__class__=LiveSkin
        rng=IW.rebuild_rng(state);pinned=IW.rebuild_scars(state);del state
        conn.send(dict(kind='ready',tiles=list(P.tris),frontier=C.front(P),scars=C.scars(pinned)))
        while True:
            cmd=conn.recv()
            if cmd=='STOP':break
            assert cmd=='STEP'
            before=C.front(P);rb=rng.getstate();calls=[];original=D.candidates
            def capture(Q,*e):
                cs=original(Q,*e)
                if Q is P:calls.append((AF.frontier_id(e),C.keys(cs)))
                return cs
            D.candidates=capture;P.additions=[]
            try:result=SCN.patient_scar(P,rng,pinned,verify_legal=True)
            finally:D.candidates=original
            placed=list(P.additions);P.additions=[];meta=P.thin(pinned,collar)
            monitors=[(AF.frontier_id(e),C.keys(D.candidates(P,*e[:3]))) for e in P.frontier() if AF.edge_id(*e[:2]) in pinned]
            # Candidate monitoring can create empty defaultdict entries; remove them
            # without retaining any historical occupancy or altering real corner data.
            P.V={k:v for k,v in P.V.items() if v}
            import collections
            P.V=collections.defaultdict(list,P.V)
            conn.send(dict(kind='step',result=result,placed=placed,tiles=list(P.tris),
                           frontier_before=before,frontier_after=C.front(P),rng_before=rb,rng_after=rng.getstate(),
                           candidates=calls,scars=C.scars(pinned),monitors=monitors,retention=meta))
    except Exception:
        import traceback
        conn.send(dict(kind='error',traceback=traceback.format_exc()))
    finally:conn.close()
