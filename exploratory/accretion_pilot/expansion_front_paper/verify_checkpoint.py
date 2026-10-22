"""Verify the saved handover without executing scientific scripts or loading pickle."""
from pathlib import Path
import ast,hashlib,json,sys
H=Path(__file__).resolve().parent; manifest=H/'CHECKPOINT_MANIFEST.json'
def files():
    for p in sorted(H.rglob('*')):
        if not p.is_file() or p==manifest: continue
        parts=p.relative_to(H).parts
        if any(x in ('__pycache__','.venv','mpl-cache') for x in parts): continue
        yield p
def payload():
    return {p.relative_to(H).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files()}
if '--write-manifest' in sys.argv:
    manifest.write_text(json.dumps(payload(),indent=2)+'\n',encoding='utf-8')
expected=json.loads(manifest.read_text()); actual=payload()
assert actual==expected, 'Manifest differs: inspect added, missing or changed files before accepting a new snapshot.'
for p in files():
    if p.suffix=='.py': ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    if p.suffix=='.json': json.loads(p.read_text(encoding='utf-8-sig'))
active=json.loads((H/'active-skin/results.json').read_text())
restart=json.loads((H/'skin-restart/results.json').read_text())
assert sum(len(x['rows']) for x in active)==310
assert sum(r['edge_queries'] for x in active for r in x['rows'])==21185
assert sum(len(x['rows']) for x in restart)==130
assert sum(r['edge_queries'] for x in restart for r in x['rows'])==12078
assert [x['rows'][-1]['status'] for x in active]==['JAM','ok','ok']
for x in restart:
    p=H/'skin-restart'/(x['case']+'-skin-only.pkl')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
response=json.loads((H/'local-response/measurements.json').read_text())
assert response['additions']==19 and response['sufficient_singletons']==[2] and response['necessary_single_omissions']==[2]
assert all(x['same'] for x in response['local_checks'])
assert response['survivor_placed_at_46']
endurance=json.loads((H/'endurance/summary.json').read_text())
assert [r['max_candidate_chain_links'] for r in endurance]==[1,2,1]
print(f'Verified {len(actual)} files, JSON/Python syntax, checkpoint hashes and saved result totals. No simulations rerun.')
