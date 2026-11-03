import copy,types,itertools
from audit_common import *
import phase1_arc_readout as P1

def same(a,b,atol=1e-11):
    return a['status']==b['status'] and a.get('selected')==b.get('selected') and abs(a.get('area',0)-b.get('area',0))<=atol and all(abs(x-y)<=atol for x,y in zip(a.get('intersections',[]),b.get('intersections',[])))

def controls(reader,st,tiles,label):
    rec,comp,raw,payload=reader.score(st,tiles);out=dict(label=label,original=rec,reference_vertex_present=S.L.key(complex(*payload['origin'])) in {S.L.key(z) for t in comp for z in t[1:]})
    reversed_payload=copy.deepcopy(payload);reversed_payload['tiles']=list(reversed(reversed_payload['tiles']))
    reverse=S.SR.read(reversed_payload);assert same(raw,reverse)
    code=(S.READER_DIR/'skin_reader.py').read_text();assert code.count('for root in sorted(pos):')==1
    module=types.ModuleType('audit_reversed_roots');exec(compile(code.replace('for root in sorted(pos):','for root in sorted(pos, reverse=True):'),'<audit root-order control>','exec'),module.__dict__)
    module.inverse=S.SR.inverse
    root_reverse=module.read(reversed_payload);assert same(raw,root_reverse)
    translated=copy.deepcopy(payload);delta=.125+.0625j
    translated['origin']=[payload['origin'][0]+delta.real,payload['origin'][1]+delta.imag]
    translated['tiles']=[[t[0]]+[[x+delta.real,y+delta.imag] for x,y in t[1:]] for t in payload['tiles']]
    tr=S.SR.read(translated);assert same(raw,tr)
    # k' = k+e0; physical origin' = origin-S*PHYS[0]; rank layers +1;
    # perpendicular offsets and every hypothesis RHS translate by PERP[0].
    gauge=copy.deepcopy(payload);o=complex(*payload['origin'])-payload['edge_length']*S.SR.PHYS[0]
    gauge['origin']=[o.real,o.imag];gauge['rank']={str(int(k)+1):v for k,v in payload['rank'].items()}
    z=S.SR.PERP[0]
    gauge['hypotheses']=[[[r,i,c+payload['windows'][r]['normals'][i][0]*z.real+payload['windows'][r]['normals'][i][1]*z.imag] for r,i,c in hyp] for hyp in payload['hypotheses']]
    gr=S.SR.read(gauge);assert same(raw,gr)
    oldlift={tuple(v):k for v,k in raw['lift']};assert all(k==[oldlift[tuple(v)][j]+(j==0) for j in range(5)] for v,k in gr['lift'])
    swapped=copy.deepcopy(payload);swapped['hypotheses'].reverse();sw=S.SR.read(swapped)
    assert sw['selected']==(1-raw['selected'] if raw['selected'] is not None else None)
    assert np.allclose(sw['intersections'],list(reversed(raw['intersections'])),atol=1e-11,rtol=0)
    isolated=S.RD.run_reader(payload);assert same(raw,isolated)
    out.update(reverse_tile_order=True,reverse_root_and_traversal=True,consistent_translation=True,nontrivial_lift_gauge=True,gauge_lifts_shift_exactly=True,swapped_hypotheses=True,direct_vs_isolated_exact=raw==isolated,direct_vs_isolated_numerical=True,max_area_change=max(abs(x['area']-raw['area']) for x in [reverse,root_reverse,tr,gr,isolated]),reader_projection_residual=raw['max_projection_residual'],birth_areas=[S.SR.area(S.SR.region(payload['windows'],{(r,i):c for r,i,c in h})) for h in payload['hypotheses']])
    return out

def scan(reader,st,center,n,tag):
    c=A.centroid(st['band']);rows=[];best=None;besttiles=[]
    for i in range(1,n+1):
        hw=math.pi*i/n;win=A.angular_window(st['band'],c,center,hw)
        rec,comp,_,_=reader.score(st,win);rec.update(index=i,half_width=hw,center=center,scan=tag);rows.append(rec)
        if (rec['area'] or 0)>1e-9 and (best is None or rec['n_tiles']>best['n_tiles']):best=rec;besttiles=comp
    return rows,best,besttiles

def main():
    reader=Reader();originals=[];grid=[];design=[];control_results=[];selected_cache={};allstates={}
    for w,si in S.B_JAMS:
        jam=load(f'jam-{w}-{si}.pkl');final=load(f'growth-{w}-{si}.pkl');tag=f'w{w}-B-s{si}';jamtheta,_=A.notch_theta0(jam);finaltheta=P3.scar_centroid_angle(final,A.centroid(final['band']))
        allstates[(w,si,'jam')]=jam;allstates[(w,si,'final')]=final
        case=dict(case=tag,checkpoints={})
        for checkpoint,st,n,theta in [('jam',jam,48,jamtheta),('final',final,32,finaltheta)]:
            glob,_,_,_=reader.score(st,st['band'])
            rows,best,besttiles=scan(reader,st,theta+math.pi,n,'original_'+checkpoint)
            selected_cache[(w,si,checkpoint)]=besttiles
            side=[]
            if checkpoint=='jam':
                for label,center,halfwidth in [('sector_pi/2',theta+math.pi,math.pi/4),('sector_pi',theta+math.pi,math.pi/2),('sector_3pi/2',theta+math.pi,3*math.pi/4),('cw_half',theta+math.pi/2,math.pi/2),('ccw_half',theta-math.pi/2,math.pi/2)]:
                    rec,_,_,_=reader.score(st,A.angular_window(st['band'],A.centroid(st['band']),center,halfwidth));rec['label']=label;side.append(rec)
            case['checkpoints'][checkpoint]=dict(global_readout=glob,original_scan=rows,largest_found=best,other_original_windows=side)
            requested=[];gridbest=None
            for ci in range(6):
                center=jamtheta+ci*math.pi/3
                for wi,hw in enumerate([math.pi/8,math.pi/4,math.pi/2,3*math.pi/4]):
                    rec,_,_,_=reader.score(st,A.angular_window(st['band'],A.centroid(st['band']),center,hw));rec.update(case=tag,checkpoint=checkpoint,centre_index=ci,width_index=wi,center=center,half_width=hw)
                    requested.append(rec)
                    if (rec['area'] or 0)>1e-9 and (gridbest is None or rec['n_tiles']>gridbest['n_tiles']):gridbest=rec
            grid.append(dict(case=tag,checkpoint=checkpoint,windows=requested,counts=dict(collections.Counter(r['outcome'] for r in requested)),largest_compatible_found=gridbest))
            print(tag,checkpoint,'original',best['n_tiles'] if best else None,'grid',dict(collections.Counter(r['outcome'] for r in requested)),flush=True)
            if (w,si)==(7,0):
                for cname,ctheta in [('jam_notch_opposite',jamtheta+math.pi),('final_scar_opposite',finaltheta+math.pi)]:
                    for resolution in [32,48]:
                        dr,db,_=scan(reader,st,ctheta,resolution,cname)
                        design.append(dict(checkpoint=checkpoint,center_kind=cname,resolution=resolution,windows=dr,largest_found=db))
            if (w,si) in [(7,0),(5,0)]:
                control_results.append(controls(reader,st,st['band'],tag+' '+checkpoint+' whole'))
                control_results.append(controls(reader,st,besttiles,tag+' '+checkpoint+' selected'))
        originals.append(case)
        dump('readout_verification.json',dict(complete=False,cases=originals,controls=control_results))
        dump('sensitivity.json',dict(complete=False,main_grid=grid,resolution_centre_diagnostic=design))
    assert sum(len(x['windows']) for x in grid)==528 and sum(len(x['windows']) for x in design)==320
    summary=dict(main_counts=dict(collections.Counter(r['outcome'] for x in grid for r in x['windows'])),diagnostic_counts=dict(collections.Counter(r['outcome'] for x in design for r in x['windows'])),requested_windows=848,unique_main_subsets=len({(x['case'],r['subset_hash']) for x in grid for r in x['windows']}),absolute_alignment_checks=reader.align_checks,exact_payloads_cached=len(reader.cache))
    dump('readout_verification.json',dict(complete=True,cases=originals,controls=control_results,absolute_alignment_checks=reader.align_checks))
    dump('sensitivity.json',dict(complete=True,protocol_commit='f1b893b',main_grid=grid,resolution_centre_diagnostic=design,summary=summary))
    (CACHE/'selected-audit.pkl').write_bytes(pickle.dumps(selected_cache))
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
