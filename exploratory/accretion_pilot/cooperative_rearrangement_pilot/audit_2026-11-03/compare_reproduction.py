"""Compare immutable committed files to the disposable reproduction checkout."""
import sys,json,hashlib,subprocess,shutil,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PIN='fea9554d8626334b09c4744a2f71897a862923cc'

def differences(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,old=a,new=b)]
    if isinstance(a,dict):
        return sum((differences(a[k],b[k],path+'/'+k) if k in a and k in b else [dict(path=path+'/'+k,missing=True)] for k in sorted(set(a)|set(b))),[])
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,lengths=[len(a),len(b)])]
        return sum((differences(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    if a==b:return []
    r=dict(path=path,old=a,new=b)
    if isinstance(a,(int,float)) and not isinstance(a,bool):r['absolute_difference']=abs(a-b);r['within_atol_1e12']=abs(a-b)<=1e-12
    return [r]

def main():
    repro=Path(sys.argv[1]).resolve();out=[]
    for rel in ['input/retained_state.json','input/evaluator_historical.json','results/part3_necessary.json','results/part4_search.json','results/part5_score.json']:
        path='exploratory/accretion_pilot/cooperative_rearrangement_pilot/'+rel
        raw=subprocess.check_output(['git','show',PIN+':'+path],cwd=ROOT)
        made=(repro/path).read_bytes();norm=made.replace(b'\r\n',b'\n')
        diff=differences(json.loads(raw),json.loads(made))
        out.append(dict(file=rel,git_blob_sha256=hashlib.sha256(raw).hexdigest(),reproduced_sha256=hashlib.sha256(made).hexdigest(),exact_bytes=raw==made,exact_after_CRLF_normalization=raw==norm,structured_exact=not diff,differences=diff))
        dest=HERE/'reproduced'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(made)
    (HERE/'results'/'comparison.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
