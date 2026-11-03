"""Distinguish reader area rejection from infeasibility of the same closed constraints."""
from audit_common import *
def main():
    reader=Reader();selected=load('selected-audit.pkl');rows=[]
    for w,si in S.B_JAMS:
        for checkpoint in ['jam','final']:
            st=load(f'{"jam" if checkpoint=="jam" else "growth"}-{w}-{si}.pkl')
            rec,_,raw,p=reader.score(st,selected[(w,si,checkpoint)])
            cm={(r,i):c for r,i,c in raw['constraints']}
            for r,i,c in p['hypotheses'][0]:cm[(r,i)]=max(cm.get((r,i),-math.inf),c)
            a=[];b=[]
            for (r,i),c in sorted(cm.items()):
                nx,ny=p['windows'][r]['normals'][i];norm=math.hypot(nx,ny);a.append([-nx/norm,-ny/norm]);b.append(-c/norm)
            a=np.array(a);b=np.array(b);rr=linprog([0,0],A_ub=a,b_ub=b,bounds=[(None,None)]*2,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
            spans=[]
            if rr.status==0:
                for objective in [[1,0],[0,1]]:
                    lo=linprog(objective,A_ub=a,b_ub=b,bounds=[(None,None)]*2,method='highs');hi=linprog([-x for x in objective],A_ub=a,b_ub=b,bounds=[(None,None)]*2,method='highs')
                    spans.append(float(-hi.fun-lo.fun) if lo.status==hi.status==0 else None)
            rows.append(dict(case=f'w{w}-B-s{si}',checkpoint=checkpoint,reader_selected=raw['selected'],reader_intersection_A_area=raw['intersections'][0],A_box_free_feasibility_status=int(rr.status),A_feasible_witness=rr.x.tolist() if rr.status==0 else None,max_constraint_violation=float(max(a@rr.x-b)) if rr.status==0 else None,axis_spans=spans,numerical_dimension=('segment' if max(spans)>1e-7 else 'point') if spans else 'infeasible' if rr.status==2 else 'unresolved',note='Floating-point closed-halfplane check; no symbolic certification.'))
    dump('boundary_intersections.json',rows);print(json.dumps(rows,indent=2),flush=True)
if __name__=='__main__':main()
