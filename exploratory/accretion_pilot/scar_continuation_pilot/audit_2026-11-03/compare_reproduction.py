import subprocess,shutil
from audit_common import *
PIN='98cfaa6ff24a805b846bcdffa6af0c6896e21305'
ROOT=HERE.parents[3]
def diff(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,old=a,new=b)]
    if isinstance(a,dict):return sum((diff(a[k],b[k],path+'/'+k) if k in a and k in b else [dict(path=path+'/'+k,missing=True)] for k in sorted(set(a)|set(b))),[])
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,lengths=[len(a),len(b)])]
        return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    if a==b:return []
    result=dict(path=path,old=a,new=b)
    if isinstance(a,(int,float)) and not isinstance(a,bool):result.update(absolute_difference=abs(a-b),within_atol_1e10=abs(a-b)<=1e-10)
    return [result]
def main():
    repro=Path(sys.argv[1]).resolve();prefix='exploratory/accretion_pilot/scar_continuation_pilot/';records=[]
    for name in ['phase1_arc_readout','phase2_scar_continuation','phase3_post_readout']:
        for ext in ['json','csv']:
            path=prefix+'results/'+name+'.'+ext;raw=subprocess.check_output(['git','show',PIN+':'+path],cwd=ROOT);made=(repro/path).read_bytes();dest=HERE/'reproduced'/(name+'.'+ext);dest.parent.mkdir(exist_ok=True);dest.write_bytes(made)
            rec=dict(file=name+'.'+ext,git_sha256=hashlib.sha256(raw).hexdigest(),produced_sha256=hashlib.sha256(made).hexdigest(),exact_bytes=raw==made,exact_after_line_ending_normalization=raw.replace(b'\r\n',b'\n')==made.replace(b'\r\n',b'\n'))
            if ext=='json':
                ds=diff(json.loads(raw),json.loads(made));rec.update(structured_exact=not ds,difference_count=len(ds),max_numeric_difference=max((d.get('absolute_difference',0) for d in ds),default=0),non_numeric_or_discrete_differences=[d for d in ds if not d.get('within_atol_1e10')],differences=ds)
            records.append(rec)
    dump('comparison.json',records)
    for r in records:print({k:v for k,v in r.items() if k not in ['differences','git_sha256','produced_sha256']},flush=True)

if __name__=='__main__':main()
