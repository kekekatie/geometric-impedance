"""
scar_heal_followup.py -- Fable's read-only review of 0a581dc, answered.

(1) Track c's long side each step of HEAL w7-s0-r2 (frontier? menu? pinned? grown?).
(2) Extend HEAL until all three stars at c's vertices complete, or a scar pins on c.
    Reclassify with the brief's ORIGINAL wording (all three complete and legal).
(3) Real NULL: genuine unpin + re-pin, place nothing; re-check NULL == SKIP.
(4) For w7-s0-r1 and the group-3 cases, identify the new scar nearest e (~0.0106).
    If it is c's long side, reclassify C (Returns).
Writes scar_heal_followup.json. Frozen engine 84130b9 unchanged; intervention world only.
"""
from __future__ import annotations
import sys, math, json, collections, functools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scar_heal as H
from scar_heal import (C, AF, L, D, S, dk, IW, SCN, step_once, checkpoint,
                       midpoint_of_scar, star_vertices, THREE_S)

EXT_CAP = 200   # extended horizon cap for the primary


def long_side(c):
    """the longest edge of tile c (its base, length ~ phi*S): (v1, v2)."""
    vs = list(c[1:]); best = None
    for i in range(3):
        a, b = vs[i], vs[(i + 1) % 3]
        d = abs(a - b)
        if best is None or d > best[0]:
            best = (d, a, b)
    return best[1], best[2]


def edge_in_frontier(P, a, b):
    ka, kb = L.key(a), L.key(b)
    for fe in P.frontier():
        if {L.key(fe[0]), L.key(fe[1])} == {ka, kb}:
            return fe
    return None


def heal_track(w, si, r, cap):
    cp = checkpoint(w, si, r)
    e, c = cp['e'], cp['c']; inter = cp['inter']
    la, lb = long_side(c); lkey = frozenset((L.key(la), L.key(lb)))
    P = IW.rebuild_skin(cp['state']); P.__class__ = H.LiveSkin; P.radius = r
    rng = IW.rebuild_rng(cp['state']); pinned = IW.rebuild_scars(cp['state'])
    pinned.discard(AF.edge_id(e[0], e[1]))       # HEAL: unpin the scar
    rows = []; c_step = closure = None; longside_pinned_step = None; stars_done_step = None
    cverts = list(c[1:])
    for step in range(inter + 1, cap + 1):
        # pre-step: long-side menu if it is a current frontier edge
        fe = edge_in_frontier(P, la, lb)
        pre_menu = C.keys(D.candidates(P, *fe[:3])) if fe else None
        result, placed = step_once(P, rng, pinned)
        if c_step is None and any(dk(t) == dk(c) for t in placed):
            c_step = step
        fe_after = edge_in_frontier(P, la, lb)
        in_front = fe_after is not None
        is_pinned = lkey in {frozenset(ek) for ek in pinned}
        if is_pinned and longside_pinned_step is None and c_step is not None:
            longside_pinned_step = step
        if closure is None and AF.frontier_id(e) not in {AF.frontier_id(x) for x in P.frontier()}:
            closure = step
        stars = star_vertices(L.Patch(list(P.tris)), cverts)
        all_complete = all(s['complete'] for s in stars)
        all_legal = all((s['legal_star'] is True) for s in stars if s['complete'])
        if all_complete and stars_done_step is None:
            stars_done_step = step
        rows.append(dict(step=step, placed=len(placed),
                         longside_in_frontier=in_front, longside_menu=pre_menu,
                         longside_pinned=is_pinned, c_in_placed=(c_step == step),
                         c_stars=[dict(complete=s['complete'], legal=s['legal_star']) for s in stars],
                         all_stars_complete=all_complete, status=result[0]))
        stop = (all_complete) or (longside_pinned_step is not None) or (result[0] == 'total_arrest')
        if stop and step >= inter + 2:
            break
    final_stars = star_vertices(L.Patch(list(P.tris)), cverts)
    strict = all(s['complete'] and s['legal_star'] for s in final_stars)
    return dict(case=f'w{w}-s{si}-r{r}', c_placed_step=c_step, closure_step=closure,
                longside=[[round(la.real, 6), round(la.imag, 6)], [round(lb.real, 6), round(lb.imag, 6)]],
                longside_pinned_step=longside_pinned_step, all_stars_complete_step=stars_done_step,
                last_step=rows[-1]['step'], final_c_stars=final_stars,
                strict_all_three_complete_and_legal=strict, rows=rows)


def real_null(w, si, r):
    """genuine unpin + re-pin, place nothing; compare placements to SKIP."""
    cp = checkpoint(w, si, r); e = cp['e']; inter = cp['inter']
    # SKIP
    def run(reop):
        P = IW.rebuild_skin(cp['state']); P.__class__ = H.LiveSkin; P.radius = r
        rng = IW.rebuild_rng(cp['state']); pinned = IW.rebuild_scars(cp['state'])
        if reop:
            pinned.discard(AF.edge_id(e[0], e[1]))   # unpin
            pinned.add(AF.edge_id(e[0], e[1]))       # re-pin at once (place nothing)
        pl = {}
        for step in range(inter + 1, H.HORIZON + 1):
            result, placed = step_once(P, rng, pinned)
            pl[step] = [repr(dk(t)) for t in placed]
            if result[0] == 'total_arrest':
                break
        return pl
    skip = run(False); null = run(True)
    return dict(null_equals_skip=(skip == null))


def nearest_new_scar_is_longside(w, si, r):
    """find the new scar nearest e's midpoint in HEAL, and whether it is c's long side."""
    cp = checkpoint(w, si, r); e, c = cp['e'], cp['c']; inter = cp['inter']
    la, lb = long_side(c); lkey = frozenset((L.key(la), L.key(lb)))
    emid = (e[0] + e[1]) / 2
    P = IW.rebuild_skin(cp['state']); P.__class__ = H.LiveSkin; P.radius = r
    rng = IW.rebuild_rng(cp['state']); pinned = IW.rebuild_scars(cp['state'])
    pinned.discard(AF.edge_id(e[0], e[1]))
    prev = set(pinned); found = []
    for step in range(inter + 1, H.HORIZON + 1):
        result, placed = step_once(P, rng, pinned)
        for ek in pinned - prev:
            d = abs(midpoint_of_scar(ek) - emid)
            found.append(dict(step=step, distance=round(d, 5), is_c_longside=(frozenset(ek) == lkey)))
        prev = set(pinned)
        if result[0] == 'total_arrest':
            break
    found.sort(key=lambda x: x['distance'])
    nearest = found[0] if found else None
    return dict(case=f'w{w}-s{si}-r{r}',
                longside=[[round(la.real, 6), round(la.imag, 6)], [round(lb.real, 6), round(lb.imag, 6)]],
                new_scars=found, nearest=nearest,
                reclassify_C=(nearest is not None and nearest['is_c_longside']))


def main():
    out = {}
    print('(1)+(2) HEAL w7-s0-r2, extended, long-side tracked ...', flush=True)
    out['heal_primary_extended'] = heal_track(7, 0, 2, EXT_CAP)
    hp = out['heal_primary_extended']
    print(f"   c@{hp['c_placed_step']} close@{hp['closure_step']} longside_pinned@{hp['longside_pinned_step']} "
          f"all3_complete@{hp['all_stars_complete_step']} last={hp['last_step']} "
          f"strict_all3_complete_legal={hp['strict_all_three_complete_and_legal']}")
    print('(3) real NULL ...', flush=True)
    out['real_null'] = {f'w{w}-s{si}-r{r}': real_null(w, si, r) for (w, si, r) in [(7, 0, 2)]}
    print('   ', out['real_null'])
    print('(4) nearest new scar for B-cases ...', flush=True)
    out['nearest_new_scar'] = {}
    for (w, si, r) in [(7, 0, 1), (15, 0, 1), (19, 0, 1), (28, 0, 1)]:
        res = nearest_new_scar_is_longside(w, si, r)
        out['nearest_new_scar'][res['case']] = res
        print(f"   {res['case']}: nearest={res['nearest']}  reclassify_C={res['reclassify_C']}")
    (HERE / 'scar_heal_followup.json').write_text(json.dumps(out, indent=2, default=repr) + '\n')
    print('wrote scar_heal_followup.json')


if __name__ == '__main__':
    main()
