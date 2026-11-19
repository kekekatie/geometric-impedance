"""Drive the 18-site primary run under the frozen sampled ensemble (N=8000 k=2, seed
20261119, shared across sites). Per-edge checkpoints so a kill resumes. Adds per-edge
geometry descriptors (sorted endpoint degrees, graph distance to rough/smooth boundary,
endpoint lift/layer). Writes results/edges_raw.json."""
import collections
import json
import sys
import time
from pathlib import Path

import patch_code as pc
import patch_run as pr

PATCHES = ('square', 'AB', 'Penrose')
N_K2 = 8000
RESULTS = Path(__file__).resolve().parents[1] / 'results'
CKPT = RESULTS / '_ckpt'


def boundary_graph(data):
    """Undirected vertex graph; sets of vertices on rough/smooth arcs."""
    adj = collections.defaultdict(set)
    for e in data['edges']:
        u, v = e['vertices']
        adj[u].add(v); adj[v].add(u)
    rough = set(); smooth = set()
    eid = {e['id']: e for e in data['edges']}
    for arc in data['arcs']:
        tgt = rough if arc['label'] == 'rough' else smooth
        for e in arc['edges']:
            tgt.update(eid[e]['vertices'])
    return adj, rough, smooth


def bfs_dist(adj, starts, targets):
    if not targets:
        return None
    seen = {s: 0 for s in starts}
    q = collections.deque(starts)
    best = None
    while q:
        x = q.popleft()
        if x in targets:
            best = seen[x]; break
        for y in adj[x]:
            if y not in seen:
                seen[y] = seen[x] + 1; q.append(y)
    return best


def edge_geometry(data, edge_id):
    edge = next(e for e in data['edges'] if e['id'] == edge_id)
    adj, rough, smooth = boundary_graph(data)
    ends = edge['vertices']
    vby = {v['id']: v for v in data['vertices']}
    d_rough = bfs_dist(adj, ends, rough)
    d_smooth = bfs_dist(adj, ends, smooth)
    lifts = [vby[v]['lift'] for v in ends]
    layers = [vby[v].get('layer') for v in ends]
    intsum = [vby[v].get('integer_sum') for v in ends]
    mod5 = [vby[v].get('source_mod5') for v in ends]
    return dict(endpoint_vertices=ends, d_rough=d_rough, d_smooth=d_smooth,
                endpoint_lift=lifts, endpoint_layer=layers,
                endpoint_integer_sum=intsum, endpoint_source_mod5=mod5)


def main():
    CKPT.mkdir(parents=True, exist_ok=True)
    pairs, total, sampled, shah = pr.k2_sample(310, N_K2)
    rows = []
    t_all = time.time()
    for fam in PATCHES:
        code = pc.PatchCode(fam)
        data = code.json
        for elig in data['eligible']:
            edge_id = elig['edge']; qubit = elig['qubit']
            tag = f'{fam}_e{edge_id}'
            ck = CKPT / f'{tag}.json'
            if ck.exists():
                rows.append(json.loads(ck.read_text()))
                print(f'{tag}: loaded checkpoint', flush=True)
                continue
            res = pr.run_edge(code, qubit, pairs, total)
            geo = edge_geometry(data, edge_id)
            row = dict(family=fam, edge_id=edge_id, lost_qubit=qubit,
                       incident_checks=elig['checks'],
                       endpoint_degrees=sorted(elig['endpoint_degrees']),
                       **geo, **res)
            ck.write_text(json.dumps(row) + '\n')
            rows.append(row)
            print(f'{tag}: n={res["n"]} elapsed={res["elapsed"]}s whole_ne={res["whole_ne_thick"]} '
                  f'rt={res["roundtrip_mismatches"]}/{res["roundtrip_checked"]}', flush=True)
    out = dict(mode='sampled', n_k2=N_K2, k2_total=total, k2_sha256=shah,
               seed=pr.SEED, p=pr.P, caps=dict(w_frame=3, w_dec=3),
               n_sites=len(rows), rows=rows,
               elapsed_total=round(time.time() - t_all, 1))
    (RESULTS / 'edges_raw.json').write_text(json.dumps(out, indent=2) + '\n')
    print('WROTE results/edges_raw.json  total', out['elapsed_total'], 's', flush=True)


if __name__ == '__main__':
    main()
