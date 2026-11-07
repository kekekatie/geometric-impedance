"""Run frozen experiment functions with separate audit outputs and fresh caches."""
import sys, os, json, hashlib, platform, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORIGINAL = HERE.parent / 'amber_lobe_ablation_2026-11-06'
sys.path.insert(0, str(ORIGINAL / 'src'))
import common as C
C.RESULTS = HERE / 'regenerated'
C.RESULTS.mkdir(parents=True, exist_ok=True)

def preflight():
    import numpy, scipy, matplotlib
    expected = json.loads((ORIGINAL/'results/provenance.json').read_text())
    hashes = {n:hashlib.sha256((C.OLD/n).read_bytes()).hexdigest() for n in expected['reused_audited_cache_sha256']}
    assert hashes == expected['reused_audited_cache_sha256']
    assert hashlib.sha256(C.AF.RD.FORKS.read_bytes()).hexdigest() == expected['fork_sha256']
    mods = {'engine':C.L,'candidates':C.D,'active_skin':C.E,'scheduler':C.SCN,'adapter':C.AF.RD}
    observed = {n:dict(path=m.__file__,sha256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()) for n,m in mods.items()}
    assert all(observed[n]['sha256']==expected['loaded_modules'][n]['sha256'] for n in mods)
    versions = dict(numpy=numpy.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__)
    assert all(versions[n]==expected[n] for n in versions)
    git=lambda *a:subprocess.check_output(['git',*a],cwd=HERE).decode().strip()
    git('merge-base','--is-ancestor','804542e41fbdddecb5a3003fe730d91bd7f24dc8','HEAD')
    assert not git('diff','804542e41fbdddecb5a3003fe730d91bd7f24dc8','--',str(ORIGINAL),str(HERE.parent/'scar_continuation_pilot'),str(HERE.parent/'referee_checks_2026-11-06'))
    assert git('-C',str(C.AF.EB.EFP.parents[2]),'rev-parse','HEAD')==expected['frozen_commit']
    assert not list(C.CACHE.glob('*')), 'Fresh audit cache required at preflight'
    C.dump(HERE/'preflight.json',dict(python=sys.version,platform=platform.platform(),versions=versions,modules=observed,input_hashes=hashes,
        env={n:os.environ[n] for n in ('EFP_SNAPSHOT','AMBER_BASE_CACHE','AMBER_CACHE','AMBER_FORK_CACHE')},all_passed=True))
    print('Pinned sources, versions and all baseline input hashes verified; audit cache empty.',flush=True)

def main():
    phase=sys.argv[1]
    if phase=='preflight':preflight()
    elif phase=='continuation':
        from run_continuation import run
        cases=[(7,0)]+[x for x in C.AF.B_JAMS if x!=(7,0)]
        for radius in (2,1,3):
            for w,si in cases:run(w,si,radius,0)
        print('Exactly 33 prescribed trials complete; no restoration policy invoked.',flush=True)
    elif phase=='reader':
        import readout_check
        readout_check.main()
    elif phase=='policy':
        sys.path.insert(0,str(ORIGINAL/'tests'))
        import test_policy
        test_policy.main()
    elif phase=='summary':
        import summarize
        summarize.main()
    elif phase=='query':
        import independent_query
        independent_query.main()
    elif phase=='inventory':
        import inventory
        inventory.main()
    elif phase=='compare':
        import compare
        compare.main()
    else:raise ValueError(phase)

if __name__=='__main__':main()
