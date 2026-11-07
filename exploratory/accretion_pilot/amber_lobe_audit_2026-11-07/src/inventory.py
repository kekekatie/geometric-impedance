"""Observe original worker frames at send boundaries on one prescribed replay."""
import sys, inspect, json
import run as R
from run import C,HERE
from worker import constructor

def main():
    state=C.load('w7-s0-r2-c0-input.pkl')
    opens=[];recording=[False]
    def hook(event,args):
        if recording[0] and event=='open':opens.append(repr(args[0]))
    sys.addaudithook(hook)
    class Probe:
        def __init__(self):self.step=22;self.frames=[]
        def recv(self):
            if self.step==44:return 'STOP'
            self.step+=1;return 'STEP'
        def close(self):pass
        def send(self,message):
            if message['kind']=='error':raise AssertionError(message)
            if message['kind']=='ready' or self.step not in (35,44):return
            frame=inspect.currentframe().f_back;v=frame.f_locals;P=v['P'];rebuilt=C.L.Patch(P.tris)
            assert dict(P.edges)==dict(rebuilt.edges) and dict(P.V)==dict(rebuilt.V)
            assert all(e[3] is None for e in P.boundary.values()) and not P.additions
            have=set(C.keys(P.tris));calls=v['calls'];monitor=v['monitors']
            geometry={C.L.key(z) for t in P.tris for z in t[1:]}
            bcoords={C.L.key(z) for e in P.boundary.values() for z in e[:3]}
            row=dict(step=self.step,worker_local_names=sorted(v),patch_attributes=sorted(vars(P)),tiles=len(P.tris),
                edge_index=len(P.edges),vertex_index=len(P.V),boundary_edges=len(P.boundary),boundary_coordinates=len(bcoords),
                boundary_coordinates_outside_tiles=len(bcoords-geometry),all_boundary_owners_none=True,
                rebuilt_indexes_exact=True,scar_labels=len(v['pinned']),input_state_deleted='state' not in v,
                transient_placed_tiles=len(v['placed']),transient_placed_not_retained=sum(k not in have for k in C.keys(v['placed'])),
                transient_candidate_keys=sum(len(ts) for _,ts in calls),
                transient_candidate_keys_not_retained=sum(k not in have for _,ts in calls for k in ts),
                transient_monitor_keys=sum(len(ts) for _,ts in monitor),
                transient_monitor_keys_not_retained=sum(k not in have for _,ts in monitor for k in ts))
            self.frames.append(row)
    probe=Probe();recording[0]=True
    constructor(probe,state,0)
    recording[0]=False
    assert [r['step'] for r in probe.frames]==[35,44]
    assert not opens,opens
    static=[]
    for name,module in list(sys.modules.items()):
        f=getattr(module,'__file__','') or ''
        if 'efp-snapshot' not in f:continue
        if hasattr(module,'STIFF'):static.append(dict(module=name,path=f,type=type(module.STIFF).__name__,size=len(module.STIFF)))
    out=dict(replay='w7-s0 primary2 through44; unchanged constructor with observing pipe stand-in',
        frames=probe.frames,runtime_file_opens=opens,static_reference_tiles=len(C.L.REF),
        historical_stiffness_globals=static,
        limits='In-process observation of the unchanged constructor, not an operating-system access sandbox. Imports precede runtime file-open observation. Transient telemetry persists in worker locals until overwritten; it is not consulted by the next scheduling step.',all_passed=True)
    C.dump(HERE/'worker_inventory.json',out);print(json.dumps(out,indent=2),flush=True)

if __name__=='__main__':main()
