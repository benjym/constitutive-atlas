"""Independent residual row operation from frozen references; no Atlas imports.
The independently generated returned states and their directions remain unchanged.
"""
from pathlib import Path
from decimal import Decimal as D,localcontext
import argparse,copy,gzip,hashlib,importlib.util,json,sys
P=Path(__file__).parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imported_reference(root):
    ref=root/'docs/reviews/tresca-rounded-reference-v1';sys.path.insert(0,str(ref))
    spec=importlib.util.spec_from_file_location('tresca_independent_projection',ref/'generate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g

def run(root,precision):
    pins=json.loads((P/'source-pins.json').read_text())
    for n,h in pins.items():assert sha(root/n)==h,n
    g=imported_reference(root);ref=root/'docs/reviews/tresca-rounded-reference-v1';source=ref/('reference-p'+str(precision)+'.json.gz');old=json.loads(gzip.decompress(source.read_bytes()));data=json.loads((ref/'inputs.json').read_text());cases={c['id']:c for c in data['cases']};out=copy.deepcopy(old)
    out.update(version='tresca-pressure-split-reference-0.1',source_reference_sha256=sha(source),candidate_sha256=sha(P/'model.json'))
    checked=0;worst=D(0);worst_path=''
    with localcontext()as ctx:
        ctx.prec=precision;seeds=g.decoded_seeds(data)
        def compare(a,b,path):
            nonlocal checked,worst,worst_path
            for i,(x,y)in enumerate(zip(a,b)):
                error=abs(x-y)/max(D(1),abs(y));checked+=1
                if error>worst:worst=error;worst_path=path+'/'+str(i)
                assert error<=D('1e-55'),(path,i,error)
        def transform_row(row,case,use_seeds):
            pars=g.parameters(case);lam,mu=pars['lame_lambda'],pars['mu'];current=g.vec(case['current']);direct=g.evaluate(pars,current,g.vec(case['parent']),g.vec(case['loading']),use_seeds,precision)
            oldres=list(map(D,row['residual']));newres=oldres[:6]+[x-y for x,y in zip(oldres[6:],g.inverse(oldres[:6],lam,mu))]
            compare(newres,[x-y for x,y in zip(current,direct['returned_state'])],case['id']+'/value')
            row['residual']=g.encode(newres)
            for j,direction in enumerate(row['directions']):
                oldd=list(map(D,direction['residual']));newd=oldd[:6]+[x-y for x,y in zip(oldd[6:],g.inverse(oldd[:6],lam,mu))]
                cv=use_seeds[j]['current'];compare(newd,[x-y for x,y in zip(cv,direct['directions'][j]['returned_state'])],case['id']+'/column'+str(j))
                direction['residual']=g.encode(newd)
        for row in out['cases']:transform_row(row['reference'],cases[row['id']],seeds)
        for row in out['history']:transform_row(row['reference'],dict(row['input'],id='history'+str(row['step'])),[])
        out['row_transform_checks']=dict(components=checked,maximum_normalized_error=str(worst),maximum_error_path=worst_path,gate='1e-55',method='old_ep_residual-C_inverse(old_sigma_residual) compared to current-independent_updated_state; same operation on all38 columns')
    # Transformation must change no source result except residual row representation.
    for before,after in zip(old['cases'],out['cases']):
        assert before['reference']['returned_state']==after['reference']['returned_state']
        for a,b in zip(before['reference']['directions'],after['reference']['directions']):assert a['returned_state']==b['returned_state']
    for a,b in zip(old['history'],out['history']):assert a['input']==b['input'] and a['committed']==b['committed'] and a['reference']['returned_state']==b['reference']['returned_state']
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--precision',type=int,choices=[200,280],required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists();result=run(args.root,args.precision);args.output.write_bytes(gzip.compress((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));print(json.dumps(result['row_transform_checks']))
