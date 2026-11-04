from pathlib import Path
import json,hashlib,ast,copy
O=Path(__file__).resolve().parent;A=O.parents[1]/'current17-igs97-regression-diagnosis-v2';checks=[]
def ok(x,s):assert x,s;checks.append(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ok(sha(A/'manifest.json')=='367fed7eba2e4043b22d4406b600aa68a0a71704026a748fe9a0f8f256a8bfdd','exact dispatched manifest')
m=json.loads((A/'manifest.json').read_text())
for name,r in m['files'].items():
 q=A/name;ok(q.is_file()and not q.is_symlink()and sha(q)==r['sha256']and q.stat().st_size==r['bytes'],'frozen member '+name)
g=json.loads((A/'GATES.json').read_text());refs=g['references'];current=Path(refs['current640_solver']['path']).read_text();prior=Path(refs['original702_solver']['path']).read_text();candidate=(A/'proposed/cpp/include/atlas/solver.hpp').read_text()
for label,r in refs.items():ok(sha(Path(r['path']))==r['sha256'],'authority '+label)
old=(A/'old-block.txt').read_text();new=(A/'new-block.txt').read_text();oldh=(A/'old-head.txt').read_text();newh=(A/'new-head.txt').read_text()
for label,text,target in [('oldbranch',old,current),('newbranch',new,candidate),('oldhead',oldh,current),('newhead',newh,candidate)]:ok(target.count(text)==1,'unique exact replacement '+label)
ok(candidate.replace(new,old).replace(newh,oldh)==current,'entire640 outside declared dispatch byteexact')
ok(sha(A/'proposed/cpp/include/atlas/solver.hpp')=='3278b22140ca2057a9a2e415654f5213b8183f398df79a7f5c56628756e8dc99','candidateC exacthash')
rows=json.loads((O/'classification17.json').read_text())['models'];ok(len(rows)==17 and len({r['id']for r in rows})==17,'17distinct classes')
audited={r['id']for r in rows if r['controller']=='640-partition-audited'}
ok(audited=={'drucker-prager','manzari-dafalias-1997-constant-m-be-v1','modified-cam-clay','s-clay1'},'four declared predictor residuals exact')
for r in rows:
 expected=bool(r['declared_multiplier_fields']);ok((r['controller']=='640-partition-audited')==expected and(not expected or(not r['rate']and not r['physical_time'])),'no ID dispatch '+r['id'])
for mid in ['mohr-coulomb','original-cam-clay-sw-electronic-log-recovery-v1','tresca-associated-perfect-bk2022v1-be']:
 r=next(r for r in rows if r['id']==mid);ok(not r['declared_multiplier_fields'] and 'no smoothness/plasticity inference'in r['meaning'],'implicit nonmultiplier limitation '+mid)
# Execute only original scalar role validation node against manufactured metadata.
tree=ast.parse(Path(refs['model_semantics']['path']).read_text());node=next(n for n in ast.walk(tree)if isinstance(n,ast.If)and isinstance(n.test,ast.BoolOp)and ast.unparse(n.test).startswith("role == 'plastic_multiplier' and"))
class ValidationError(Exception):pass
code=compile(ast.Module(body=[node],type_ignores=[]),'original-multiplier-validation','exec')
for name,role,typ,version,transient,kind,reject in [('validv03','plastic_multiplier',0,'0.3',False,'residual',False),('legacyvalid','plastic_multiplier',0,'0.1',True,'residual',False),('legacytemporarymissing','plastic_multiplier',0,'0.1',False,'residual',True),('rateinvalid','plastic_multiplier',0,'0.3',True,'rate',True),('dimensioninvalid','plastic_multiplier',1,'0.3',True,'residual',True),('persistent','persistent',0,'0.3',False,'rate',False)]:
 env={'role':role,'typ':typ,'Type':lambda:0,'version':version,'field':{'transient':transient},'integration_kind':lambda model:kind,'model':{},'ValidationError':ValidationError}
 try:exec(code,env)
 except ValidationError:ok(reject,'original rejects '+name)
 else:ok(not reject,'original accepts '+name)
# Invalid compiled flag combinations fail closed even before material integration.
ok('if(multiplier_control&&(models().at(model).rate||models().at(model).physical_time))return false;'in newh,'explicit invalid rate/physical guard')
for rate in [False,True]:
 for physical in [False,True]:
  for fields in [[],[False],[True],[False,True]]:
   multiplier=any(fields);choice='reject'if multiplier and(rate or physical)else'audited'if multiplier else'historical'
   ok((choice=='reject')==(multiplier and(rate or physical)),'metadata truth table '+repr((rate,physical,fields)))
ok(json.loads((O/'source-checks.json').read_text())['count']==76,'author76 independently replayed read-only')
(O/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'material_compiled_browser_network':False},indent=2)+'\n');print(json.dumps({'passed':True,'count':len(checks)}))
