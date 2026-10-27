"""Archive-free geometry reader. Standard library only; JSON stdin/stdout.
No imports from the growth engine, no file inputs, no branch label.
Coordinates use five unit directions exp(i*(18+72*j) degrees).
"""
import sys, json, math, cmath, collections
B = 128
PHYS_TOL = 1e-7                 # in rhombus-edge units
AREA_TOL = 1e-9
PERP = [cmath.exp(4j*math.pi*j/5) for j in range(5)]
PHYS = [cmath.exp(1j*math.radians(18+72*j)) for j in range(5)]
CELL = PHYS_TOL*2
_PAIR = None

class ReconstructionError(ValueError):
    pass

def inverse(z):
    """Exhaustive unique inverse in |k_j-k_4|<=128, modulo (1,1,1,1,1)."""
    global _PAIR
    if _PAIR is None:
        _PAIR = collections.defaultdict(list)
        for a in range(-B,B+1):
            for b in range(-B,B+1):
                p=a*PHYS[0]+b*PHYS[1]
                _PAIR[(math.floor(p.real/CELL),math.floor(p.imag/CELL))].append((a,b,p))
    found=[]
    for c in range(-B,B+1):
        for d in range(-B,B+1):
            p=c*PHYS[2]+d*PHYS[3]; target=z-p
            u,v=math.floor(target.real/CELL),math.floor(target.imag/CELL)
            for du in (-1,0,1):
                for dv in (-1,0,1):
                    for a,b,q in _PAIR.get((u+du,v+dv),()):
                        residual=abs(p+q-z)
                        if residual<=PHYS_TOL:
                            found.append(([a,b,c,d,0],residual))
    if len(found)!=1:
        raise ReconstructionError("coordinate_inverse_candidates="+str(len(found)))
    return found[0]

def clip(poly,n,c):
    out=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]
        fa=n[0]*a[0]+n[1]*a[1]-c; fb=n[0]*b[0]+n[1]*b[1]-c
        if fa>=0: out.append(a)
        if (fa>=0)!=(fb>=0):
            s=fa/(fa-fb); out.append([a[0]+s*(b[0]-a[0]),a[1]+s*(b[1]-a[1])])
    return out

def region(windows,*cms):
    poly=[[-50.,-50.],[50.,-50.],[50.,50.],[-50.,50.]]
    keys=set().union(*(set(c) for c in cms))
    for rk,i in sorted(keys):
        poly=clip(poly,windows[rk]["normals"][i],max(c.get((rk,i),-1e18) for c in cms))
        if not poly: break
    return poly

def area(p):
    return .5*abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))

def read(payload):
    expected={"schema","tiles","edge_length","origin","rank","windows","hypotheses"}
    if set(payload)!=expected or payload["schema"]!=1:
        raise ReconstructionError("undeclared_input_fields")
    S=payload["edge_length"]; origin=complex(*payload["origin"])
    rank={int(k):v for k,v in payload["rank"].items()}
    if len(rank)!=4 or sorted(rank)!=list(range(min(rank),min(rank)+4)):
        raise ReconstructionError("expected_four_consecutive_layers")
    # Vertex key follows the historical coordinate convention, not historical labels.
    key=lambda z:(round(z.real,6),round(z.imag,6))
    pos={}; adj=collections.defaultdict(list)
    max_merge=0.
    for tile in payload["tiles"]:
        zs=[complex(*p) for p in tile[1:]]
        for z in zs:
            vk=key(z)
            if vk in pos: max_merge=max(max_merge,abs(pos[vk]-z)/S)
            else: pos[vk]=z
        for p,q in zip(zs,zs[1:]+zs[:1]):
            delta=(q-p)/S
            if abs(abs(delta)-1)>1e-4: continue
            err,j,sg=min((abs(delta-sg*e),j,sg) for j,e in enumerate(PHYS) for sg in (-1,1))
            if err>PHYS_TOL: raise ReconstructionError("edge_direction_residual")
            adj[key(p)].append((key(q),j,sg))
            adj[key(q)].append((key(p),j,-sg))
    if max_merge>PHYS_TOL: raise ReconstructionError("vertex_key_collision")
    K={}; components=[]; max_proj=0.
    for root in sorted(pos):
        if root in K: continue
        rel={root:[0]*5}; queue=collections.deque([root])
        while queue:
            u=queue.popleft()
            for v,j,sg in adj[u]:
                kv=rel[u].copy(); kv[j]+=sg
                if v in rel and rel[v]!=kv: raise ReconstructionError("lift_cycle_conflict")
                if v not in rel: rel[v]=kv; queue.append(v)
        h,res=inverse((pos[root]-origin)/S)
        # Fix all-ones kernel by requiring this component to lie in the declared slab.
        sums=[sum(h)+sum(v) for v in rel.values()]
        low=math.ceil((min(rank)-min(sums))/5)
        high=math.floor((max(rank)-max(sums))/5)
        shifts=[q for q in range(low,high+1) if all(s+5*q in rank for s in sums)]
        if len(shifts)!=1: raise ReconstructionError("layer_gauge_candidates="+str(len(shifts)))
        shift=shifts[0]
        for vk,r in rel.items():
            k=[h[j]+r[j]+shift for j in range(5)]
            if max(abs(k[j]-k[4]) for j in range(4))>B:
                raise ReconstructionError("coordinate_domain_exceeded")
            error=abs(sum(k[j]*PHYS[j] for j in range(5))-(pos[vk]-origin)/S)
            max_proj=max(max_proj,error)
            if error>PHYS_TOL: raise ReconstructionError("physical_projection_residual")
            K[vk]=k
        components.append(dict(vertices=len(rel),root=list(root),inverse_residual=res,
                               layer_shift=shift,inverse_candidates=1,layer_candidates=1))
    cm={}; omitted=[]
    for vk,k in K.items():
        layer=sum(k)
        if layer not in rank: omitted.append(list(vk)); continue
        rk=rank[layer]; z=sum(k[j]*PERP[j] for j in range(5)); win=payload["windows"][rk]
        for i,(nx,ny) in enumerate(win["normals"]):
            c=nx*z.real+ny*z.imag-win["h"]
            cm[(rk,i)]=max(cm.get((rk,i),-1e18),c)
    poly=region(payload["windows"],cm)
    ints=[area(region(payload["windows"],cm,{(r,i):v for r,i,v in hyp})) for hyp in payload["hypotheses"]]
    compatible=[i for i,v in enumerate(ints) if v>AREA_TOL]
    selected=compatible[0] if len(compatible)==1 and area(poly)>1e-12 else None
    return dict(status="reconstructed",selected=selected,area=area(poly),intersections=ints,
                constraints=[[r,i,v] for (r,i),v in sorted(cm.items())],polygon=poly,
                components=components,omitted_vertices=omitted,vertices=len(K),
                max_projection_residual=max_proj,max_vertex_merge_residual=max_merge,
                lift=[[list(v),k] for v,k in sorted(K.items())],
                tolerances=dict(physical=PHYS_TOL,area=AREA_TOL,coefficient_bound=B))

def deny_archive_access(event,args):
    if event=="open" or event.startswith(("socket.","subprocess.","os.system")):
        raise ReconstructionError("forbidden_reader_io:"+event)

def main():
    sys.addaudithook(deny_archive_access)
    try: result=read(json.load(sys.stdin))
    except ReconstructionError as e: result=dict(status="unreconstructible",reason=str(e))
    print(json.dumps(result,separators=(",",":")))
if __name__=="__main__": main()
