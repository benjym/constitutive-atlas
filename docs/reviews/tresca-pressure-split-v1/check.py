"""Independent pressure-shift and saved-row reference checks; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext,InvalidOperation
import argparse,gzip,hashlib,importlib.util,json
P=Path(__file__).parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_text())
def run(root=ROOT):
    for n,h in load(P/'pre-transformation-freeze.json').items():assert sha(P/n)==h,n
    amendment=load(P/'full-precision-amendment-freeze.json');assert sha(P/'transform_full_precision.py')==amendment['new_script_sha256']
    spec=importlib.util.spec_from_file_location('tresca_full_reference_transform',P/'transform_full_precision.py');transform=importlib.util.module_from_spec(spec);spec.loader.exec_module(transform);g=transform.imported_reference(root)
    data=load(root/'docs/reviews/tresca-rounded-reference-v1/inputs.json');new=[];checked=0;worst=D(0);cross=0;crossworst=D(0);pressurechecks=0;pressureworst=D(0)
    def compare(a,b):
        nonlocal checked,worst
        for x,y in zip(a,b):
            error=abs(x-y)/max(D(1),abs(y));assert error<=D('1e-55'),error;checked+=1;worst=max(worst,error)
    for precision in (200,280):
        old=load(root/('docs/reviews/tresca-rounded-reference-v1/reference-p'+str(precision)+'.json.gz'));current=load(P/('reference-full-row-p'+str(precision)+'.json.gz'));new.append(current)
        def invariant(a,b):
            if isinstance(a,dict):
                assert a.keys()==b.keys()
                for k in a:
                    if k=='residual':
                        assert a[k][:6]==b[k][:6] # original stress residual rows are immutable
                    else:invariant(a[k],b[k])
            elif isinstance(a,list):
                assert len(a)==len(b)
                for x,y in zip(a,b):invariant(x,y)
            else:assert a==b
        invariant(old['cases'],current['cases']);invariant(old['history'],current['history'])
        with localcontext()as ctx:
            ctx.prec=precision
            for case,row in zip(data['cases'],old['cases']):
                assert case['id']==row['id'];pars=g.parameters(case);lam,mu=pars['lame_lambda'],pars['mu'];parent=g.vec(case['parent']);loading=g.vec(case['loading']);pd=sum(parent[:3])/3;ed=sum(loading[:3])/3
                dv=[parent[i]-(pd if i<3 else 0)+2*mu*(loading[i]-(ed if i<3 else 0))for i in range(6)];mean=pd+(lam+2*mu/3)*sum(loading[:3]);full=[v+(mean if i<3 else 0)for i,v in enumerate(dv)]
                compare(full,list(map(D,row['reference']['trial'])))
                vals,ps,_,_=g.spectrum(g.cart(dv),precision);r,_,_=g.project(vals,2*pars['k']);returned_dev=g.mandel(g.matrix_return(vals,ps,r));updated=[v+(mean if i<3 else 0)for i,v in enumerate(returned_dev)]+[parent[6+i]+(dv[i]-returned_dev[i])/(2*mu)for i in range(6)]
                for x,y in zip(updated,map(D,row['reference']['returned_state'])):
                    error=abs(x-y)/max(D(1),abs(y));assert error<=D('1e-55'),(case['id'],error);pressurechecks+=1;pressureworst=max(pressureworst,error)
    def crosscheck(a,b):
        nonlocal cross,crossworst
        if isinstance(a,dict):
            assert a.keys()==b.keys()
            for k in a:crosscheck(a[k],b[k])
        elif isinstance(a,list):
            assert len(a)==len(b)
            for x,y in zip(a,b):crosscheck(x,y)
        elif isinstance(a,str):
            try:x,y=D(a),D(b)
            except InvalidOperation:assert a==b
            else:
                error=abs(x-y)/max(D(1),abs(y));assert error<=D('1e-55'),error;cross+=1;crossworst=max(crossworst,error)
        else:assert a==b
    with localcontext()as ctx:
        ctx.prec=300;crosscheck(new[0]['cases'],new[1]['cases']);crosscheck(new[0]['history'],new[1]['history'])
    return dict(version='tresca-pressure-split-source-checks-0.1',cases=61,columns=38,history_rows=12,unchanged_original_updates_and_stress_rows=True,row_transform_components_per_precision=new[0]['row_transform_checks']['components'],row_transform_maximum_errors=[v['row_transform_checks']['maximum_normalized_error']for v in new],pressure_split_updated_components=pressurechecks,maximum_pressure_split_error=str(pressureworst),cross_precision_numeric_fields=cross,maximum_cross_precision_error=str(crossworst),gate='1e-55 unchanged',initial_membership_resolution=False,candidate_material_calls=0,compiled_calls=0)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();result=run()
    if args.output:
        assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
