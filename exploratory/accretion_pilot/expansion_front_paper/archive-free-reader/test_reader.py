"""Meaningful isolation/geometry checks on the first saved pilot payload."""
from pathlib import Path
import json, copy, subprocess, sys, tempfile
import verify_reader as V

def main():
    files=sorted(V.CASES.glob("*.json"))
    if not files: raise RuntimeError("Run --pilot first")
    case=json.loads(files[0].read_text()); p=case["payload"]
    base=V.reader(p)
    assert base["status"]=="reconstructed"
    checks=[]
    def record(name,passed,**kw):
        checks.append(dict(check=name,passed=bool(passed),**kw))
        assert passed,name
    bad=copy.deepcopy(p); bad["true_branch"]="A"
    record("reject_undeclared_branch_label",V.reader(bad)["status"]=="unreconstructible")
    bad=copy.deepcopy(p); del bad["origin"]
    record("reject_missing_common_origin",V.reader(bad)["status"]=="unreconstructible")
    bad=copy.deepcopy(p)
    for t in bad["tiles"]:
        for z in t[1:]: z[0]+=.123456789*p["edge_length"]
    record("reject_off_module_geometry",V.reader(bad)["status"]=="unreconstructible")
    shuffled=copy.deepcopy(p); shuffled["tiles"].reverse()
    rr=V.reader(shuffled)
    a,b=V.cm_dict(base["constraints"]),V.cm_dict(rr["constraints"])
    residual=max(abs(a[k]-b[k]) for k in a)
    record("input_tile_order_invariance",residual<=V.COMPARE_TOL and rr["selected"]==base["selected"],residual=residual)
    # Independently selected separated surviving triangles: no history to connect them.
    key=lambda z:(round(z[0],6),round(z[1],6))
    first=p["tiles"][0]; k0={key(z) for z in first[1:]}
    second=next(t for t in reversed(p["tiles"]) if not k0 & {key(z) for z in t[1:]})
    dis=copy.deepcopy(p); dis["tiles"]=[first,second]
    rd=V.reader(dis)
    expected={tuple(v):k for v,k in case["reference"]["lift"]}
    record("disconnected_components_reconstruct_without_bridges",
           rd["status"]=="reconstructed" and len(rd["components"])==2
           and all(expected[tuple(v)]==k for v,k in rd["lift"]),
           components=len(rd.get("components",[])))
    moved=copy.deepcopy(p); dx,dy=.125,-.25
    for t in moved["tiles"]:
        for z in t[1:]: z[0]+=dx; z[1]+=dy
    moved["origin"][0]+=dx; moved["origin"][1]+=dy
    rm=V.reader(moved)
    residual=max(abs(x-y) for x,y in zip(base["intersections"],rm["intersections"]))
    record("common_physical_translation",rm["selected"]==base["selected"] and residual<=V.COMPARE_TOL,residual=residual)
    # Demonstrate that attempted archive reads are denied after reader initialization.
    code=("import runpy,sys; m=runpy.run_path("+repr(str(V.HERE/"skin_reader.py"))+"); "
          "sys.addaudithook(m['deny_archive_access']); "
          "\ntry:\n open("+repr(str(V.HERE.parent/"paired-front/results/closure_measurements.json"))+")"
          "\nexcept m['ReconstructionError']:\n print('blocked')"
          "\nelse:\n raise AssertionError('archive read allowed')")
    proc=subprocess.run([sys.executable,"-I","-S","-c",code],capture_output=True,text=True)
    record("reader_audit_hook_blocks_archive_open",proc.returncode==0 and proc.stdout.strip()=="blocked")
    # Degenerate hypotheses must not force a label.
    equal=copy.deepcopy(p); equal["hypotheses"]=[p["hypotheses"][base["selected"]]]*2
    re=V.reader(equal)
    record("identical_compatible_hypotheses_report_ambiguous",re["selected"] is None and all(x>1e-9 for x in re["intersections"]))
    V.dump(V.OUT/"checks.json",checks)
    print(json.dumps(checks,indent=2))
if __name__=="__main__": main()
