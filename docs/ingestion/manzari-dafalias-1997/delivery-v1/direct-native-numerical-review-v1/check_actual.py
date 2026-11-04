"""Saved local direct numerical review; no compiled calls."""
from pathlib import Path
import hashlib,json,runpy,sys
from decimal import Decimal,localcontext
O=Path(__file__).resolve().parent
S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
R=Path('/private/tmp/atlas-md1997-direct-app-v1')
D=R/'native-decimal';Q=S/'tools/md1997_decimal_reference_current17_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def require(v,n):
 if not v:raise ValueError(n)
 checks.append(n)
def read(p):return json.loads(p.read_text())
def main():
 require(sha(D/'build-binding.json')=='24807f1a5154cadbd490dff5ba4edd58aa1bbd83e6dd5a8f8db8b4a6eb77d521','exact binding')
 b=read(D/'build-binding.json');inputs=read(D/'source-inputs.json')
 require(len(inputs)==512 and sha(D/'source-inputs.json')==b['source_freeze_sha256'],'source freeze identity')
 for k,v in inputs.items():require(sha(S/k)==v,'unchanged source '+k)
 for p,k in [(S/'tests/test_solver.cpp','fixture_sha256'),(R/'native/generated/models.json','generated_catalogue_sha256'),(R/'native/atlas_numerical_tests','executable_sha256')]:require(sha(p)==b[k],'actual build endpoint '+k)
 sys.path.insert(0,str(Q));a=runpy.run_path(str(Q/'assess_saved.py'))
 replay=a['assess'](Q/'requests.json',Q/'reference.json',D/'process.json',D/'build-binding.json',sha(D/'build-binding.json'))
 require(replay==read(D/'assessment.json'),'unchanged accepted assessor exact report replay')
 require(replay['passed'] is True and replay['purpose']=='actual' and replay['comparisons']==588 and not replay['failures'],'all588 assessor comparisons pass')
 env=a['read'](D/'stdout');ref=read(Q/'reference.json');ad=env['ad_hex'];sec=ref['data']['120']['secants'];records=[]
 with localcontext() as ctx:
  ctx.prec=120
  for c in range(14):
   for l in (0,1):
    for r in range(14):
     f=Decimal(sec[2*c+l][r]);x=Decimal.from_float(float.fromhex(ad[r][c]));e=abs(f-x);budget=Decimal('3e-5')*max(1,abs(f),abs(x));require(e<budget,'independent AD/FD '+str((c,l,r)));records.append(('AD/FD',r,c,l,str(e),str(budget)))
   for r in range(14):
    x,y=(Decimal(sec[2*c+l][r]) for l in (0,1));e=abs(x-y);budget=Decimal('1.5e-5')*max(1,abs(x),abs(y));require(e<budget,'independent h/h2 '+str((c,r)));records.append(('h/h2',r,c,None,str(e),str(budget)))
 require(len(set((x[0],x[1],x[2],x[3]) for x in records))==588,'complete unique comparison coverage')
 for row,actual in zip(records,replay['results']):
  require((row[0],row[1],row[2],row[3],row[4],row[5])==(actual['gate'],actual['row'],actual['column'],actual.get('level'),actual['error'],actual['budget']),'independent exact error/budget agreement')
 # Corrupted saved objects must reject without executing any artifact.
 refusals=[];p=read(D/'process.json')
 for name,mutation in [('wrong selector',lambda x:x['selectors'].update(ATLAS_NUMERICAL_FIXTURES='md1997-decimal-fd-reference-v1')),('failed exit',lambda x:x.update(returncode=1)),('bool exit',lambda x:x.update(returncode=False)),('wrong executable',lambda x:x.update(executable_sha256='0'*64))]:
  import copy
  bad=copy.deepcopy(p);mutation(bad)
  try:a['transport'](bad,b)
  except Exception:refusals.append(name)
  else:raise ValueError('corruption accepted '+name)
 bindings={str(x):{'sha256':sha(x),'bytes':x.stat().st_size} for x in [D/'process.json',D/'stdout',D/'stderr',D/'assessment.json',D/'build-binding.json',D/'source-inputs.json',R/'native/atlas_numerical_tests',R/'native/generated/models.json',R/'native/generated/models.hpp']}
 out={'identity':'independent-direct-current17-native-numerical-checks-v1','passed':True,'assertions':len(checks),'refusals':refusals,'comparisons':588,'models':env['models'],'cpp_checks':env['cpp_checks'],'source_inputs_post_exact':512,'saved_assessment_exact_replay':True,'bindings':bindings,'compiled_calls':0,'scope':'local current17 Mac direct numerical test only; no fullCI/Linux/authority-wrapper acceptance','historical_binary64_failure_preserved':True}
 (O/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'assertions':len(checks),'refusals':len(refusals),'comparisons':588}))
if __name__=='__main__':main()
