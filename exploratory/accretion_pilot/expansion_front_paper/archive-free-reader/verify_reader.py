"""Post-review verification; reproduce only the previously scored closure continuations."""
from pathlib import Path
import sys, json, subprocess, tempfile, hashlib, argparse, copy, time
HERE=Path(__file__).resolve().parent
SOURCE_COMMIT="a96c88b83a1d80f915dc29e0ffa193a6164f6e77"
COMPARE_TOL=1e-10
OUT=HERE/"results"
CASES=OUT/"cases"

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2),encoding="utf-8")

def cm_rows(cm): return [[int(r),int(i),float(v)] for (r,i),v in sorted(cm.items())]
def cm_dict(rows): return {(r,i):v for r,i,v in rows}
def sha(data): return hashlib.sha256(data).hexdigest()

def reader(payload):
    # Isolated interpreter: no site packages, PYTHONPATH or repository imports.
    with tempfile.TemporaryDirectory(prefix="reader-") as cwd:
        p=subprocess.run([sys.executable,"-I","-S",str(HERE/"skin_reader.py")],
                         input=json.dumps(payload),text=True,capture_output=True,cwd=cwd,timeout=90)
    if p.returncode: raise RuntimeError("reader process failed: "+p.stderr)
    return json.loads(p.stdout)

def distance(poly,other):
    if not poly or not other: return 0. if not poly and not other else float("inf")
    def point_segment(p,a,b):
        dx,dy=b[0]-a[0],b[1]-a[1]; den=dx*dx+dy*dy
        t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0.
        return ((p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2)**.5
    def directed(a,b):
        return max(min(point_segment(p,b[i],b[(i+1)%len(b)]) for i in range(len(b))) for p in a)
    return max(directed(poly,other),directed(other,poly))

def compare(payload,ref,out):
    if out["status"]!="reconstructed":
        return dict(outcome="unreconstructible",reason=out.get("reason"),agreement=False)
    a,b=cm_dict(out["constraints"]),cm_dict(ref["constraints"])
    same_keys=set(a)==set(b)
    delta=max((abs(a[k]-b[k]) for k in set(a)&set(b)),default=0.)
    areas=[abs(out["area"]-ref["area"])]+[abs(x-y) for x,y in zip(out["intersections"],ref["intersections"])]
    lifts={tuple(v):k for v,k in out["lift"]}; expected={tuple(v):k for v,k in ref["lift"]}
    mismatches=sum(lifts.get(v)!=k for v,k in expected.items())
    outcome="ambiguous" if out["selected"] is None else ("correct" if out["selected"]==ref["true_index"] else "wrong")
    region_delta=distance(out["polygon"],ref["polygon"])
    return dict(outcome=outcome,agreement=same_keys and delta<=COMPARE_TOL and max(areas)<=COMPARE_TOL
                and region_delta<=COMPARE_TOL and mismatches==0,
                constraint_keys_equal=same_keys,max_constraint_residual=delta,area_residuals=areas,
                polygon_boundary_residual=region_delta,lift_mismatches=mismatches,
                vertices=out["vertices"],components=len(out["components"]),omitted=len(out["omitted_vertices"]),
                max_projection_residual=out["max_projection_residual"])

def transformations(payload,out):
    swapped=copy.deepcopy(payload); swapped["hypotheses"].reverse()
    rs=reader(swapped)
    swap_ok=rs["status"]=="reconstructed" and rs["selected"]==(None if out["selected"] is None else 1-out["selected"])
    swap_ok=swap_ok and max(abs(x-y) for x,y in zip(rs["intersections"],reversed(out["intersections"])))<=COMPARE_TOL
    # Lift-coordinate gauge k' = k+(1,0,0,0,0). Physical coordinates unchanged.
    # origin' = origin-S*physical(e0); rank layer keys +1; perp offset/regions +1.
    import math
    gauge=copy.deepcopy(payload); S=gauge["edge_length"]
    gauge["origin"][0]-=S*math.cos(math.radians(18)); gauge["origin"][1]-=S*math.sin(math.radians(18))
    gauge["rank"]={str(int(k)+1):v for k,v in gauge["rank"].items()}
    for hyp in gauge["hypotheses"]:
        for row in hyp: row[2]+=gauge["windows"][row[0]]["normals"][row[1]][0]
    rg=reader(gauge)
    gauge_res=None; gauge_ok=False
    if rg["status"]=="reconstructed":
        original=cm_dict(out["constraints"]); moved=cm_dict(rg["constraints"])
        gauge_res=max(abs(moved[k]-v-payload["windows"][k[0]]["normals"][k[1]][0]) for k,v in original.items())
        gauge_ok=(rg["selected"]==out["selected"] and gauge_res<=COMPARE_TOL
                  and abs(rg["area"]-out["area"])<=COMPARE_TOL
                  and max(abs(x-y) for x,y in zip(rg["intersections"],out["intersections"]))<=COMPARE_TOL)
    return dict(candidate_swap_pass=swap_ok,gauge_shift_pass=gauge_ok,gauge_constraint_residual=gauge_res)

def prepare(saved,selected):
    sys.path.insert(0,str(HERE.parent/"paired-front"))
    import window_retrodiction as W
    from collections import defaultdict
    grouped=defaultdict(list)
    for row,a in selected: grouped[row["world"]].append((row,a))
    for world,pairs in grouped.items():
        todo=[(r,a) for r,a in pairs if not (CASES/f"w{world}-{a['opt']}-s{a['stream']}.json").exists()]
        if not todo: continue
        print("Reconstructing existing world",world,flush=True)
        common=W.P.common_state(world,W.P.centres(80)[world])
        if common is None: raise RuntimeError("original common state unavailable")
        s,edge,mid,cs,meta=common
        assert meta["patch"]==pairs[0][0]["patch"]
        rank=W.Sl.rank_of(s)
        # Origin is determined before commitment, from the shared original convention.
        origin=next(p for t in s for p,q in ((t[1],t[2]),(t[2],t[3]),(t[3],t[1])) if abs(abs(q-p)-W.S)<1e-4*W.S)
        hypotheses=[W.CD.after_first(s,c,rank) for c in cs]
        windows=[dict(normals=n.tolist(),h=float(h)) for n,h in W.WIN]
        for row,old in todo:
            index=0 if old["opt"]=="A" else 1
            stream=W.P.SEED0*1000+world*7919+101*old["stream"]
            arm=W.P.grow_arm(s,cs[index],stream,44)
            assert len(arm["snaps"])==old["nsnaps"] and arm["stop"]==old["stop"] and arm["guesses"]==old["guesses"]
            full=arm["snaps"][44]; skin,front=W.P.skin_of(full)
            assert W.dk(cs[index]) not in {W.dk(t) for t in skin}
            # Verify supplied departure snapshot as well, without redoing every sampled score.
            dep=old["dep"]
            assert W.dk(cs[index]) not in {W.dk(t) for t in W.P.skin_of(arm["snaps"][dep])[0]}
            assert W.dk(cs[index]) in {W.dk(t) for t in W.P.skin_of(arm["snaps"][dep-1])[0]}
            keys={W.L.key(z) for t in skin for z in t[1:]}
            cm=W.F_in_gauge(full,rank,restrict_vkeys=keys)
            ints=[W.Sl.area(W.Sl.region(cm,h)) for h in hypotheses]
            f0=W.Sl.area(W.Sl.region(cm))
            residuals=[abs(f0-old["f0"]),abs(ints[index]-old["aTrue"]),abs(ints[1-index]-old["aOther"])]
            assert max(residuals)<=COMPARE_TOL,residuals
            K,_,conf=W.M.lift(full)
            assert not conf
            payload=dict(schema=1,tiles=[[t[0]]+[[z.real,z.imag] for z in t[1:]] for t in skin],
                         edge_length=float(W.S),origin=[origin.real,origin.imag],
                         rank={str(k):int(v) for k,v in rank.items()},windows=windows,
                         hypotheses=[cm_rows(c) for c in hypotheses])
            ref=dict(true_index=index,constraints=cm_rows(cm),area=f0,intersections=ints,
                     polygon=W.Sl.region(cm),lift=[[list(v),[int(x) for x in K[v]]] for v in sorted(keys)],
                     omitted_vertices=[list(v) for v in sorted(keys) if int(K[v].sum()) not in rank],
                     source_area_residuals=residuals,source_record=old,
                     archive_tiles=len(full),skin_tiles=len(skin),step=44,world=world,
                     initial_choice_absent=True)
            name=f"w{world}-{old['opt']}-s{old['stream']}"
            dump(CASES/(name+".json"),dict(payload=payload,reference=ref))
            print("Prepared",name,len(skin),"skin tiles",flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pilot",action="store_true")
    ap.add_argument("--verify-only",action="store_true")
    args=ap.parse_args()
    saved_path=HERE.parent/"paired-front/results/closure_measurements.json"
    saved=json.loads(saved_path.read_text())
    selected=[(r,a) for r in saved for a in r["arms"] if not a["censored"]]
    assert len(saved)==22 and sum(len(r["arms"]) for r in saved)==88 and len(selected)==49
    assert len({r["world"] for r,a in selected})==20 and {a["last_step"] for r,a in selected}=={44}
    positives=[(r,a) for r,a in selected if a["aOther"]>0]
    if args.pilot:
        picks=[selected[0],next((r,a) for r,a in selected if a["opt"]=="B"),positives[0]]
        unique={}
        for r,a in picks: unique[(r["world"],a["opt"],a["stream"])]=(r,a)
        selected=list(unique.values())
    if not args.verify_only: prepare(saved,selected)
    results=[]
    for row,a in selected:
        name=f"w{row['world']}-{a['opt']}-s{a['stream']}"
        case=json.loads((CASES/(name+".json")).read_text())
        payload,ref=case["payload"],case["reference"]
        result=reader(payload)
        checks=compare(payload,ref,result)
        if result["status"]=="reconstructed": checks.update(transformations(payload,result))
        checks.update(case=name,world=row["world"],original_other_area=a["aOther"],
                      payload_bytes=len(json.dumps(payload).encode()),payload_sha256=sha(json.dumps(payload,sort_keys=True).encode()),
                      source_residuals=ref["source_area_residuals"])
        results.append(checks)
        dump(OUT/"reader-output"/(name+".json"),result)
        dump(OUT/("pilot_comparisons.json" if args.pilot else "comparisons.json"),results)
        print(name,checks["outcome"],"agreement",checks["agreement"],flush=True)
    summary=dict(source_commit=SOURCE_COMMIT,closure_sha256=sha(saved_path.read_bytes()),
                 source_forks=22,source_continuations=88,source_scored=49,source_scored_forks=20,source_censored=39,
                 original_positive_other_count=len(positives),original_max_other=max(a["aOther"] for r,a in positives),
                 checked=len(results),checked_forks=len({r["world"] for r in results}),
                 outcomes={k:sum(r["outcome"]==k for r in results) for k in ("correct","wrong","ambiguous","unreconstructible")},
                 all_comparisons_agree=all(r["agreement"] for r in results),
                 all_swaps_pass=all(r.get("candidate_swap_pass",False) for r in results),
                 all_gauges_pass=all(r.get("gauge_shift_pass",False) for r in results),
                 compare_tolerance=COMPARE_TOL,
                 max_constraint_residual=max((r.get("max_constraint_residual",0) for r in results),default=0),
                 max_area_residual=max((max(r.get("area_residuals",[0])) for r in results),default=0),
                 max_projection_residual=max((r.get("max_projection_residual",0) for r in results),default=0))
    dump(OUT/("pilot_summary.json" if args.pilot else "summary.json"),summary)
    print(json.dumps(summary,indent=2))
    if not (summary["all_comparisons_agree"] and summary["all_swaps_pass"] and summary["all_gauges_pass"] and summary["outcomes"]["correct"]==len(results)):
        raise SystemExit("Verification failed; inspect comparison results")
if __name__=="__main__": main()
