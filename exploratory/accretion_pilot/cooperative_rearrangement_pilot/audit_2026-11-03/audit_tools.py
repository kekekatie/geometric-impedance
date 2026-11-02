"""Audit-only hardening; frozen engine and historical pilot remain untouched."""
import itertools, math, collections, json
import coop_common as C

def classify_region(band_constraints, region, full_verdict):
    """Reuse the proven full verdict; never assume infeasibility after LP failure."""
    cmax, engulfed = band_constraints.exterior_cmax(region)
    if cmax == band_constraints.full_cmax:
        return dict(full_verdict)
    return C.classify_exterior(cmax)

def area(poly):
    return abs(sum((a.conjugate()*b).imag for a,b in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>2 else 0.

def intersection(a,b):
    """Convex polygon clipping; triangles are convex. No engine inside() test."""
    out=list(a)
    signed=sum((p.conjugate()*q).imag for p,q in zip(b,b[1:]+b[:1]))
    sign=1 if signed>0 else -1
    for p,q in zip(b,b[1:]+b[:1]):
        old=out;out=[]
        if not old:break
        f=lambda z:sign*((q-p).conjugate()*(z-p)).imag
        for u,v in zip(old,old[1:]+old[:1]):
            fu,fv=f(u),f(v)
            if fu>=-1e-15:out.append(u)
            if (fu>=-1e-15)!=(fv>=-1e-15):out.append(u+(v-u)*fu/(fu-fv))
    return out

def overlap(a,b):return area(intersection(list(a[1:]),list(b[1:])))>1e-12

def boundary(tiles):
    counts=collections.Counter(C.ekey(a,b) for t in tiles for a,b in itertools.combinations(t[1:],2))
    return {k for k,n in counts.items() if n==1}

def template_ok(t):
    for template in C.L.TEMPL.values():
        if t[0]!=template[0]:continue
        factor=(t[2]-t[1])/(template[2]-template[1])
        if abs(abs(factor)-1)<1e-8 and abs(t[1]+factor*(template[3]-template[1])-t[3])<1e-9:return True
    return False

def completed_replacement_legal(exterior,region,fill):
    """Explicit footprint, template, overlap and final affected-star checks."""
    if not region or not fill or not all(template_ok(t) for t in fill):return False
    if boundary(fill)!=boundary(region):return False
    if abs(sum(area(list(t[1:])) for t in fill)-sum(area(list(t[1:])) for t in region))>1e-12:return False
    for i,t in enumerate(fill):
        if abs(sum(area(intersection(list(t[1:]),list(u[1:]))) for u in region)-area(list(t[1:])))>1e-12:return False
        if any(overlap(t,u) for u in fill[:i]):return False
        near=[u for u in exterior if abs(sum(t[1:])/3-sum(u[1:])/3)<4*C.S]
        if any(overlap(t,u) for u in near):return False
    patch=C.L.Patch(list(exterior)+list(fill))
    touched={C.L.key(z) for t in list(region)+list(fill) for z in t[1:]}
    return all(not patch.V.get(v) or patch.vertex_ok(v,[]) for v in touched)

def true_frontier_counts(state,band):
    patch=C.L.Patch(band);fr={C.ekey(e[0],e[1]):e for e in patch.frontier()}
    counts=[]
    for rec in state['true_frontier']:
        key=C.ekey(complex(*rec['p']),complex(*rec['q']))
        if key not in fr:raise ValueError('saved true frontier missing')
        e=fr[key]
        if json.loads(json.dumps(C.dk(e[3])))!=rec['owner']:raise ValueError('true frontier owner changed')
        counts.append(len(C.D.candidates(patch,*e[:3])))
    return dict(n_frontier=len(counts),n_dead_sites=counts.count(0),n_growable=sum(c>0 for c in counts),candidate_count_histogram=dict(sorted(collections.Counter(counts).items())))
