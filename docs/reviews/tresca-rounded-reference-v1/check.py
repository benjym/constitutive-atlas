"""Cross-precision, certificates, derivative and history self-checks; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,InvalidOperation,localcontext
import argparse,gzip,hashlib,json
import generate as g
P=Path(__file__).parent
def load(name):
    p=P/name;return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_text())
def compare(a,b,path='',stats=None):
    if stats is None:stats={'numeric_fields':0,'max_error':D(0)}
    if isinstance(b,str):
        try:aa,bb=D(a),D(b)
        except (InvalidOperation,ValueError):assert a==b,path
        else:
            error=abs(aa-bb)/max(D(1),abs(bb));assert error<=D('1e-55'),(path,error);stats['numeric_fields']+=1;stats['max_error']=max(stats['max_error'],error)
    elif isinstance(b,list):
        assert isinstance(a,list) and len(a)==len(b),path
        for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i),stats)
    elif isinstance(b,dict):
        assert a.keys()==b.keys(),path
        for k in b:
            if k!='precision':compare(a[k],b[k],path+'/'+k,stats)
    else:assert a==b,path
    return stats

def selfcheck(data,refs,policy):
    cases={c['id']:c for c in data['cases']};references={r['id']:r['reference']for r in refs['cases']};count=0;worst=D(0);linearity=0;wlin=D(0)
    chosen=['elastic','face','upper','lower','repeat-upper','repeat-lower','dense-face','dense-upper']
    with localcontext()as ctx:
        ctx.prec=policy['finite_difference']['precision'];seeds=g.decoded_seeds(data)
        for name in chosen:
            c=cases[name];base={k:g.vec(c[k])for k in ('current','parent','loading')};pars=g.parameters(c);ref=references[name];active=[tuple(p)for p in ref['active']]
            for column in policy['finite_difference']['columns']:
                seed=seeds[column]
                for raw in policy['finite_difference']['steps']:
                    h=D(raw);sides=[]
                    for sign in (-1,1):
                        perturbed={k:[x+sign*h*y for x,y in zip(base[k],seed[k])]for k in base}
                        sides.append(g.evaluate(pars,**perturbed,seeds=[],precision=ctx.prec,fixed_active=active))
                    for channel in ('residual','returned_state'):
                        for i,value in enumerate(ref['directions'][column][channel]):
                            observed=(sides[1][channel][i]-sides[0][channel][i])/(2*h);expected=D(value);error=abs(observed-expected)/max(D(1),abs(expected));assert error<=D(policy['finite_difference']['gate']),(name,column,raw,channel,i,error);count+=1;worst=max(worst,error)
        # Every mixed column is independently decomposed into all30 physical bases.
        for row in refs['cases']:
            directions=row['reference']['directions'];assert len(directions)==38
            for col in range(30,38):
                seed=seeds[col];weights=seed['current']+seed['parent']+seed['loading']
                for channel in ('residual','returned_state'):
                    for i in range(12):
                        expected=sum((w*D(directions[j][channel][i])for j,w in enumerate(weights)),D(0));actual=D(directions[col][channel][i]);error=abs(expected-actual)/max(D(1),abs(expected));assert error<=D('1e-55');linearity+=1;wlin=max(wlin,error)
        # Exact diagonal branch boundaries have declared one-sided source branches.
        boundary_checks=0
        for name,col,directions in [('yield',24,{-1:'elastic',1:'face'}),('face-upper-boundary',25,{-1:'face',1:'upper'}),('face-lower-boundary',25,{-1:'lower',1:'face'})]:
            c=cases[name];base={k:g.vec(c[k])for k in ('current','parent','loading')};pars=g.parameters(c)
            for sign,expected in directions.items():
                v={k:list(x)for k,x in base.items()};v['loading'][col-24]+=sign*D('1e-30')
                out=g.evaluate(pars,**v,seeds=[],precision=ctx.prec);assert out['branch']==expected,(name,sign,out['branch']);boundary_checks+=1
    return dict(centered_component_checks=count,max_centered_error=str(worst),mixed_linearity_checks=linearity,max_linearity_error=str(wlin),one_sided_boundary_branch_checks=boundary_checks)

def run():
    for name,pin in load('pre-generation-freeze.json').items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==pin,name
    # This copied characteristic-cubic implementation must retain its independent ancestry.
    source=load('sources.json');assert hashlib.sha256((P/'spectral_source.py').read_bytes()).hexdigest()==source['docs/reviews/mc-stored-reference-v1/spectral_source.py']
    data=load('inputs.json');a=load('reference-p200.json.gz');b=load('reference-p280.json.gz');policy=load('reference-policy.json')
    with localcontext()as ctx:ctx.prec=300;stats=compare(a,b)
    derivative=selfcheck(data,b,policy)
    branches={}
    for row in b['cases']:
        r=row['reference'];branches[r['branch']]=branches.get(r['branch'],0)+1
        assert D(r['certificate_error'])<=D('1e-100')
    for i,row in enumerate(b['history']):
        assert row['input']['parent']==(data['history']['initial']if i==0 else b['history'][i-1]['committed'])
        assert len(row['committed'])==12 and all(__import__('math').isfinite(float.fromhex(v))for v in row['committed'])
    return dict(version='tresca-independent-reference-checks-0.1',cases=len(b['cases']),columns=38,branches=branches,history_steps=len(b['history']),rounded_history_parents_outside_source_yield=[row['step']for row in b['history']if not row['reference']['parent_admissible']],cross_precision_fields=stats['numeric_fields'],maximum_cross_precision_error=str(stats['max_error']),**derivative,compiled_calls=0,candidate_material_calls=0)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();result=run()
    if args.output:
        assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
