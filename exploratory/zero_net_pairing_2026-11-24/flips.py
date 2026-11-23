"""Collect every credit-moving history for the studied endpoint omissions, and reproduce
the committed local-witness-omission lost/gained rows. Engine imported unchanged."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent / 'fresh_site_address_audit_2026-11-20'
sys.path.insert(0, str(AUDIT))
import audit                      # noqa: E402  (sets up engine = run.py)
E = audit.engine
RESULTS = ROOT / 'results'

# frozen sites and the endpoint (X) checks studied for zero/near-zero net cost
SITES = [
    dict(patch='Penrose_2', edge=4, checks=['X0', 'X5']),
    dict(patch='Penrose_1', edge=14, checks=['X4', 'X6']),
]


def collect(site):
    code = audit.CorrectedPatchCode(audit.SOURCE / (site['patch'] + '.json'))
    d = code.json
    e = next(x for x in d['eligible'] if x['edge'] == site['edge'])
    q = e['qubit']
    nx, nz = len(d['HX']), len(d['HZ'])
    D = E.Indexed(code, q)
    star = list(D.star)
    idx = {c: audit.check_index(c, nx, nz) for c in e['checks']}
    studied = {c: [i for i in star if i != idx[c]] for c in site['checks']}
    ODDS = E.prior.ODDS
    # aggregate accumulators per check, by fault weight k (0,1,2)
    agg = {c: dict(flips=0, tie_changes=0, lost=[0., 0., 0.], gained=[0., 0., 0.]) for c in site['checks']}
    counts = [0, 0, 0]
    flips = {c: [] for c in site['checks']}
    pool = E.prior.ordinary_pool(code)
    assert len(pool) == 310
    n = 0
    t0 = time.time()
    for cid, k, extra in E.prior.config_stream(pool):
        for onset, vx, vz in E.prior.VARIANTS:
            loss = ([('X', q, onset)] if vx else []) + ([('Z', q, onset)] if vz else [])
            dz, dx, truth, _ = code.simulate(*E.prior.nd_run.compose(extra + tuple(loss)))
            stored = E.unpack(D, D.serialize(dz, dx, 'diamond'))
            intact = E.query(D, stored, star)
            ci = E.prior.cred(intact, truth)
            for c in site['checks']:
                om = E.query(D, stored, studied[c])
                co = E.prior.cred(om, truth)
                delta = co - ci
                if om['label'] != intact['label']:
                    agg[c]['flips'] += 1
                elif om['tie'] != intact['tie']:
                    agg[c]['tie_changes'] += 1
                if delta < 0:
                    agg[c]['lost'][k] += -delta
                elif delta > 0:
                    agg[c]['gained'][k] += delta
                if delta != 0 or om['label'] != intact['label'] or om['tie'] != intact['tie']:
                    flips[c].append(dict(
                        cid=cid, k=k, onset=onset, vx=vx, vz=vz, weight=ODDS ** k,
                        extra=[list(f) for f in extra], truth=truth,
                        intact_label=intact['label'], intact_p0=intact['p0'], intact_tie=intact['tie'],
                        omit_label=om['label'], omit_p0=om['p0'], omit_tie=om['tie'],
                        delta=delta,
                        direction=('R2W' if (intact['label'] == truth and om['label'] != truth)
                                   else 'W2R' if (intact['label'] != truth and om['label'] == truth)
                                   else 'tie')))
            counts[k] += 1
            n += 1
        if len(D._mcache) > 500000:
            D._mcache.clear()
        if cid % 8000 == 0:
            print(f"  {site['patch']} cid={cid} n={n} {round(time.time()-t0,1)}s", flush=True)
    assert n == 385648
    mass = sum(counts[k] * ODDS ** k for k in range(3))
    out = dict(patch=site['patch'], edge=site['edge'], qubit=q, histories=n,
               counts=counts, odds=ODDS, mass=mass, star=star, check_index=idx, checks={})
    for c in site['checks']:
        lost_pp = 100 * sum(agg[c]['lost'][k] * ODDS ** k for k in range(3)) / mass
        gained_pp = 100 * sum(agg[c]['gained'][k] * ODDS ** k for k in range(3)) / mass
        out['checks'][c] = dict(omitted_index=idx[c], retained_indices=studied[c],
                                flips=agg[c]['flips'], tie_changes=agg[c]['tie_changes'],
                                lost_pp=lost_pp, gained_pp=gained_pp, net_pp=lost_pp - gained_pp,
                                movers=len(flips[c]), records=flips[c])
        print(f"  {site['patch']} {c}: flips={agg[c]['flips']} tie_changes={agg[c]['tie_changes']} "
              f"lost={lost_pp:.8f} gained={gained_pp:.8f} net={lost_pp-gained_pp:.8f}", flush=True)
    return out


def main():
    RESULTS.mkdir(exist_ok=True)
    for site in SITES:
        out = collect(site)
        (RESULTS / f"flips_{site['patch']}_e{site['edge']}.json").write_text(json.dumps(out) + '\n')
        print(f"WROTE flips_{site['patch']}_e{site['edge']}.json", flush=True)


if __name__ == '__main__':
    main()
