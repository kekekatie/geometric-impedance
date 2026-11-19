"""Run the FROZEN deterministic fresh-cut selection and export the selected patches.

Frozen selection rule (geometry only; no scores consulted):
  Families AB and Penrose, two cuts each.
  Candidate cut = n=21, distance (3,3), >=2 eligible edges, from the frozen disk-cut
    enumeration (24 centres x aspects {1,1.25,.8} x angles {0,pi/8,pi/4,3pi/8} x m in
    [6,25)); corner enumeration as the pilot; DISJOINT (face ids) from that family's
    discovery cut; and hosting >=1 on-route AND >=1 off-route eligible edge
    (on-route = qubit in >=1 weight-3 X-logical support).
  Pair within a cut = (on,off) minimizing, in order: (a) endpoint-degree mismatch
    (0 if sorted degrees equal else 1); (b) |dRough_on-dRough_off|+|dSmooth_on-dSmooth_off|;
    (c) -(on-route #supports); (d) (on_edge_id, off_edge_id) ascending.
  Cut ranking = (pair.a, pair.b, -on_supports, spec, corners). Greedily take the top cut,
    then the next whose face ids are disjoint from already-picked cuts and whose (HX,HZ)
    geometry is not a duplicate, until two are chosen.
  If a family yields fewer than two, report and proceed with what qualifies.
The predicted (circled) edge is the on-route edge of each pair; prediction: G(on)-G(off) > 0.
"""
import json
from pathlib import Path

import geom_select as g

RESULTS = Path(__file__).resolve().parents[1] / 'results'
FAMILIES = ('AB', 'Penrose')


def best_pair(on, off):
    best = None
    for o in on:
        for f in off:
            a = 0 if o['endpoint_degrees'] == f['endpoint_degrees'] else 1
            b = abs((o['d_rough'] or 0) - (f['d_rough'] or 0)) + abs((o['d_smooth'] or 0) - (f['d_smooth'] or 0))
            key = (a, b, -o['n_supports'], o['edge'], f['edge'])
            if best is None or key < best[0]:
                best = (key, o, f)
    (a, b, _, _, _), o, f = best
    return dict(on=o, off=f, degree_mismatch=a, dist_mismatch=b)


def select(family):
    p = g.pilot.parent(family)
    disc = g.discovery_ids(p)
    cands = []
    for cand in g.enumerate_cuts(p):
        if set(cand['ids']) & disc:
            continue
        obj, w3, on, off = g.analyse(p, cand)
        if not (on and off):
            continue
        pair = best_pair(on, off)
        rank = (pair['degree_mismatch'], pair['dist_mismatch'], -pair['on']['n_supports'],
                cand['spec']['spec'], cand['spec']['corners'])
        cands.append(dict(rank=rank, cand=cand, obj=obj, pair=pair, n_w3=len(w3),
                          on_all=on, off_all=off))
    cands.sort(key=lambda r: r['rank'])
    chosen = []
    used_faces = set()
    seen_geom = set()
    for r in cands:
        ids = set(r['cand']['ids'])
        if ids & used_faces:
            continue
        geomkey = (tuple(map(tuple, r['obj']['HX'])), tuple(map(tuple, r['obj']['HZ'])))
        if geomkey in seen_geom:
            continue
        chosen.append(r); used_faces |= ids; seen_geom.add(geomkey)
        if len(chosen) == 2:
            break
    return p, disc, chosen, len(cands)


def main():
    manifest = dict(rule='frozen (see module docstring)', families={})
    for fam in FAMILIES:
        p, disc, chosen, ncand = select(fam)
        print(f'{fam}: {ncand} qualifying fresh cuts; selected {len(chosen)}', flush=True)
        entries = []
        for k, r in enumerate(chosen, 1):
            obj = r['obj']
            # annotate the exported patch with route tags + the chosen pair
            onset = {e['edge']: e['n_supports'] for e in r['on_all']}
            tags = {e['edge']: ('on_route' if e['edge'] in onset else 'off_route')
                    for e in r['on_all'] + r['off_all']}
            obj['route'] = dict(
                n_weight3_x_supports=r['n_w3'],
                eligible_tags=tags,
                on_route_eligible=[e for e in r['on_all']],
                off_route_eligible=[e for e in r['off_all']],
                predicted_pair=dict(on_route_edge=r['pair']['on']['edge'],
                                    off_route_edge=r['pair']['off']['edge'],
                                    on=r['pair']['on'], off=r['pair']['off'],
                                    degree_mismatch=r['pair']['degree_mismatch'],
                                    dist_mismatch=r['pair']['dist_mismatch']),
                discovery_face_overlap=0)
            name = f'{fam}_{k}'
            (RESULTS / f'{name}.json').write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
            pr = r['pair']
            print(f'  {name}: ON e{pr["on"]["edge"]} q{pr["on"]["qubit"]} deg{pr["on"]["endpoint_degrees"]} '
                  f'(#sup {pr["on"]["n_supports"]}, dR{pr["on"]["d_rough"]} dS{pr["on"]["d_smooth"]})  '
                  f'vs OFF e{pr["off"]["edge"]} q{pr["off"]["qubit"]} deg{pr["off"]["endpoint_degrees"]} '
                  f'(dR{pr["off"]["d_rough"]} dS{pr["off"]["d_smooth"]})  '
                  f'match[deg={pr["degree_mismatch"]},dist={pr["dist_mismatch"]}]  nW3={r["n_w3"]}', flush=True)
            entries.append(dict(name=name, predicted_pair=obj['route']['predicted_pair'],
                                n_weight3_x_supports=r['n_w3'],
                                selection_spec=obj['selection']))
        manifest['families'][fam] = dict(n_candidates=ncand, selected=entries,
                                         discovery_excluded=True)
    (RESULTS / 'selection.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('WROTE selection.json + patch JSONs', flush=True)


if __name__ == '__main__':
    main()
