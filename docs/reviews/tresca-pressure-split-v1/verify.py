"""Verify saved transformed residuals directly from frozen independent updates."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import gzip,hashlib,json,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2]
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_text())
def verify_rows(packet=P,root=ROOT):
    data=load(root/'docs/reviews/tresca-rounded-reference-v1/inputs.json');cases={c['id']:c for c in data['cases']};count=0;worst=D(0)
    with localcontext()as ctx:
        ctx.prec=300
        def check(actual,expected,path):
            nonlocal count,worst
            assert len(actual)==len(expected)
            for i,(x,y)in enumerate(zip(actual,expected)):
                error=abs(D(x)-y)/max(D(1),abs(y));assert error<=D('1e-55'),(path,i,error);count+=1;worst=max(worst,error)
        def vector(v):return [D.from_float(float.fromhex(x))for x in v]
        for precision in (200,280):
            old=load(root/('docs/reviews/tresca-rounded-reference-v1/reference-p'+str(precision)+'.json.gz'));new=load(packet/('reference-full-row-p'+str(precision)+'.json.gz'))
            for a,b in zip(old['cases'],new['cases']):
                assert a['id']==b['id'];current=vector(cases[a['id']]['current']);check(b['reference']['residual'],[x-D(y)for x,y in zip(current,a['reference']['returned_state'])],a['id']+'/residual')
                assert len(b['reference']['directions'])==38
                for j,(da,db)in enumerate(zip(a['reference']['directions'],b['reference']['directions'])):
                    seed=vector(data['seeds'][j]['current']);check(db['residual'],[x-D(y)for x,y in zip(seed,da['returned_state'])],a['id']+'/column'+str(j))
            for a,b in zip(old['history'],new['history']):check(b['reference']['residual'],[x-D(y)for x,y in zip(vector(a['input']['current']),a['reference']['returned_state'])],'history'+str(a['step']))
    return dict(components=count,maximum_normalized_error=str(worst),gate='1e-55')
def verify(packet=P,root=ROOT):
    pin=load(packet/'split-check-freeze.json')['sha256'];assert hashlib.sha256((packet/'check.py').read_bytes()).hexdigest()==pin
    spec=importlib.util.spec_from_file_location('tresca_split_checks',packet/'check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);result=module.run(root);assert result==load(packet/'checks.json')
    return dict(source_checks=result,direct_saved_row_checks=verify_rows(packet,root))
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
