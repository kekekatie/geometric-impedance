import os,sys,json,pickle,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];PILOT=HERE.parent
sys.path.insert(0,str(PILOT/'scar_continuation_pilot/archive_free_2026-11-04/src'))
sys.path.insert(0,str(PILOT/'scar_continuation_pilot/archive_free_2026-11-04/supplement_2026-11-04'))
import af_common as AF
import isolated_worker as IW
import scar_continuation as SCN
import verify_supplement as VS
L,D,S,E,dk=AF.L,AF.D,AF.S,AF.E,AF.dk
OLD=Path(os.environ['AMBER_BASE_CACHE']).resolve()
CACHE=Path(os.environ['AMBER_CACHE']).resolve();CACHE.mkdir(parents=True,exist_ok=True)
RESULTS=HERE/'results';RESULTS.mkdir(exist_ok=True)
AF.RD.FORKS=Path(os.environ['AMBER_FORK_CACHE']).resolve()
def old(name):return pickle.loads((OLD/name).read_bytes())
def save(name,v):(CACHE/name).write_bytes(pickle.dumps(v,protocol=5))
def load(name):return pickle.loads((CACHE/name).read_bytes())
def h(v):return hashlib.sha256(repr(v).encode()).hexdigest()
def keys(ts):return [repr(dk(t)) for t in ts]
def scars(s):return sorted(tuple(sorted(e)) for e in s)
def front(P):return [AF.frontier_id(e) for e in P.frontier()]
def dump(path,v):path.write_text(json.dumps(v,indent=2,default=repr)+'\n',encoding='utf-8')
