"""Cross-check geometric names, matrix supports, and decoder addresses before scoring."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'aperiodic_predict_2026-11-20/results'
sys.path.insert(0, str(ROOT.parent / 'penrose_e14_route_check_2026-11-20'))
import run as engine

def check_index(cid, nx, nz):
    assert cid[0] in ('X', 'Z') and cid[1:].isdigit(), cid
    i = int(cid[1:])
    assert 0 <= i < (nx if cid[0] == 'X' else nz), cid
    return i if cid[0] == 'X' else nx + i

class CorrectedPatchCode(engine.prior.FreshPatchCode):
    def __init__(self, path):
        super().__init__(path)
        self.legacy_star = dict(self.STAR)
        nx, nz = len(self.json['HX']), len(self.json['HZ'])
        for e in self.json['eligible']:
            self.STAR[e['qubit']] = sorted(check_index(c, nx, nz) for c in e['checks'])
            actual = [i for i, s in enumerate(self.STABS) if e['qubit'] in s['support']]
            assert self.STAR[e['qubit']] == actual

def audit():
    sites = []
    for patch in ('AB_1', 'Penrose_1', 'Penrose_2'):
        code = CorrectedPatchCode(SOURCE / (patch + '.json'))
        d = code.json
        cert = json.loads((SOURCE / (patch + '_certificate.json')).read_text())
        nx, nz = len(d['HX']), len(d['HZ'])
        assert (nx, nz) == (cert['rank_X'], cert['rank_Z']) == (11, 9)
        assert cert['checks']['commutation'] and cert['checks']['eight_coordinates']
        names = ['X'+str(i) for i in range(nx)] + ['Z'+str(i) for i in range(nz)]
        vertices = {v['id']: v for v in d['vertices']}
        faces = {f['id']: f for f in d['faces']}
        edges = {e['id']: e for e in d['edges']}
        for e in d['eligible']:
            edge = edges[e['edge']]
            geometric = [vertices[v]['xcheck'] for v in edge['vertices']] + [faces[f]['zcheck'] for f in edge['incident_faces']]
            assert len(set(geometric)) == 4 and set(geometric) == set(e['checks'])
            q = e['qubit']
            assert q == edge['qubit']
            matrix = [names[i] for i, s in enumerate(code.STABS) if q in s['support']]
            assert set(matrix) == set(geometric)
            assert {tuple(x) for x in e['query']} == {(c, t) for c in geometric for t in (1, 2)}
            assert e['weights'] == [len(code.STABS[check_index(c,nx,nz)]['support']) for c in e['checks']]
            sites.append(dict(patch=patch, edge=e['edge'], qubit=q, nx=nx, nz=nz,
                geometric_checks=sorted(geometric), matrix_incident_checks=matrix,
                legacy_indices=code.legacy_star[q], legacy_actual_checks=[names[i] for i in code.legacy_star[q]],
                corrected_indices=code.STAR[q], affected=code.legacy_star[q] != code.STAR[q]))
        assert len(d['eligible']) == cert['eligible_edges']
    # Ten-X-row pilot layouts retain their original addresses with the generic mapping.
    for nx, nz in ((10,10), (11,9)):
        assert [check_index('X'+str(i),nx,nz) for i in range(nx)] == list(range(nx))
        assert [check_index('Z'+str(i),nx,nz) for i in range(nz)] == list(range(nx,nx+nz))
    result = dict(starting_sha='5506cd138495b62d50af2765ba1615718cd262b2',
                  original_result_sha='fdeaa32a988224f98dc10b99175c99d806862522',sites=sites,
                  sites_checked=len(sites), affected_sites=sum(s['affected'] for s in sites))
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/address_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
