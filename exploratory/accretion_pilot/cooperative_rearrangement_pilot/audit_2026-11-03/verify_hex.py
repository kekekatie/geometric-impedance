"""Bounded hexagon audit and regression checks; no new repair regions."""
import sys,json,itertools,collections,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
import coop_common as C
import part4_search as P
import hexflip as H
import audit_tools as A

def independent_fillings(region):
    """Uncapped open-edge search with independent area-intersection overlap.
    Shares frozen template placement atlas, but no historical search/inside test.
    Deduplicates geometries before branching; all decorations then enumerated.
    """
    target=sum(A.area(list(t[1:])) for t in region);boundary=A.boundary(region)
    points={C.L.key(z):z for t in region for z in t[1:]};solutions={};nodes=0;maxdepth=0
    def rec(placed,used,remaining):
        nonlocal nodes,maxdepth
        nodes+=1;maxdepth=max(maxdepth,len(placed))
        if abs(remaining)<1e-12:
            if A.boundary(placed)==boundary:
                signature=tuple(sorted(tuple(sorted(C.L.key(z) for z in t[1:])) for t in placed))
                solutions[signature]=placed
            return
        oe=(boundary-set(used))|{e for e,n in used.items() if e not in boundary and n==1}
        if not oe:return
        edge=min(oe,key=lambda e:sorted(e));p,q=[points[v] for v in sorted(edge)]
        candidates={}
        for t in H._template_placements(p,q):
            key=tuple(sorted(C.L.key(z) for z in t[1:]));candidates.setdefault(key,t)
        for t in candidates.values():
            ar=A.area(list(t[1:]))
            if ar>remaining+1e-12:continue
            if abs(sum(A.area(A.intersection(list(t[1:]),list(u[1:]))) for u in region)-ar)>1e-12:continue
            if any(A.overlap(t,u) for u in placed):continue
            ue=used.copy()
            for a,b in itertools.combinations(t[1:],2):ue[C.ekey(a,b)]+=1
            if any(n>2 or (e in boundary and n>1) for e,n in ue.items()):continue
            for z in t[1:]:points[C.L.key(z)]=z
            rec(placed+[t],ue,remaining-ar)
    rec([],collections.Counter(),target)
    decorated={}
    for geometry in solutions.values():
        variants=[]
        for t in geometry:
            vv={}
            for perm in itertools.permutations(t[1:]):
                for c in (0,1):
                    nt=(c,)+perm
                    if A.template_ok(nt):vv[C.dk(nt)]=nt
            variants.append(list(vv.values()))
        for fill in itertools.product(*variants):decorated[tuple(sorted(C.dk(t) for t in fill))]=list(fill)
    return decorated,dict(nodes=nodes,max_depth=maxdepth,geometric_dissections=len(solutions),decorated_fillings=len(decorated),caps=None)

def main():
    st,band,rank,dead=P.load_state();hexes=P.flip_hexagons_near_dead(band,dead);records=[]
    controls={};star_comparisons=0
    for number,h in enumerate(hexes):
        region=h['tiles'];rkeys={C.dk(t) for t in region};exterior=[t for t in band if C.dk(t) not in rkeys]
        surr=P.local_exterior(band,region)
        generated,info=independent_fillings(region)
        original,lookup=H.enumerate_hexagon_fillings(region,surr,legality='geom',max_solutions=256)
        assert set(generated)==set(original),(number,len(generated),len(original))
        legal=[];historical=[];affected=set()
        for sol in original:
            fill=[lookup[k] for k in sol]
            old=C.completed_replacement_legal(surr,region,fill)
            new=A.completed_replacement_legal(exterior,region,fill)
            assert old==new
            if new:legal.append(sol)
            patch=C.L.Patch(exterior+fill)
            touched={C.L.key(z) for t in region+fill for z in t[1:]}
            for v in touched:
                if patch.V.get(v):
                    assert C.vertex_star_ok(patch.V[v])==patch.vertex_ok(v,[])
                    star_comparisons+=1
            affected|=touched
        assert len(legal)==1 and legal[0]==tuple(sorted(rkeys))
        missing_local=[C.dk(t) for t in exterior if any(C.L.key(z) in affected for z in t[1:]) and C.dk(t) not in {C.dk(t) for t in surr}]
        assert not missing_local
        records.append(dict(region=sorted(rkeys),independent_search=info,exact_candidate_set_agreement=True,legal_completed=1,only_identity=True,all_affected_exterior_stars_in_local_neighbourhood=True))
        print(f'hex {number+1}/15: {info}, only identity',flush=True)
        if number==0:
            controls['empty_historical_accepts']=C.completed_replacement_legal(surr,region,[])
            controls['empty_corrected_rejects']=not A.completed_replacement_legal(exterior,region,[])
            controls['incomplete_corrected_rejects']=not A.completed_replacement_legal(exterior,region,region[:-1])
            controls['duplicate_corrected_rejects']=not A.completed_replacement_legal(exterior,region,region+[region[0]])
            moved=[(t[0],)+tuple(z+0.001 for z in t[1:]) for t in region]
            controls['shifted_footprint_rejected']=not A.completed_replacement_legal(exterior,region,moved)
            bad=list(region);c,a,b,d=bad[0];bad[0]=(c,a+0.13+0.07j,b,d)
            controls['malformed_template_rejected']=not A.completed_replacement_legal(exterior,region,bad)
            controls['identity_passes']=A.completed_replacement_legal(exterior,region,region)
            # Two crossings with no containment is a generic overlap-unit control.
            t1=(0,complex(-2,-.3),complex(2,-.3),complex(0,.3))
            t2=(0,complex(-.3,-2),complex(-.3,2),complex(.3,0))
            controls['crossing_overlap_detected']=A.overlap(t1,t2)
    assert all(controls.values()),controls
    result=dict(regions=records,controls=controls,star_comparisons=star_comparisons,
      nonidentity_legal_positive_control='Unavailable under the exact sampled exterior/rules; no relaxed-rule repair example substituted.',
      corrected_true_frontier=A.true_frontier_counts(st,band))
    (HERE/'results').mkdir(exist_ok=True)
    (HERE/'results'/'hex_verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='regions'},indent=2))

if __name__=='__main__':main()
