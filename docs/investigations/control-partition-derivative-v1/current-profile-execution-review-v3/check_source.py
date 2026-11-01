"""Independent profile v3 source/reversal review. No collectors or artifacts."""
import sys
sys.dont_write_bytecode=True
import ast,hashlib,importlib.util,json,os
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'current-profile-execution-v3';V=C/'current-profile-execution-v2';read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('manifest exact',h(D/'manifest.json')=='b0e0e3e33e973ec1f3c735f1457a94408e15668da9ebf67ef7304b41bc98f078');manifest=read(D/'manifest.json')['files'];ck('packet inventory exact',set(manifest)|{'manifest.json'}=={p.relative_to(D).as_posix()for p in D.rglob('*')if p.is_file()})
for n,v in manifest.items():ck('packet '+n,h(D/n)==v)
proof=read(D/'rebind-proof.json');ck('oldv2 manifest unchanged',h(V/'manifest.json')==proof['old_manifest']=='eebf5d8be93aa8d385fdf74d793d6dde22d6f571e21889f7a924fa2429455669')
for n,e in proof['files'].items():
 ck('old/new hash '+n,h(V/n)==e['old_sha256'] and h(D/n)==e['new_sha256']);s=(D/n).read_text()
 for a,b in reversed(proof['replacements']):s=s.replace(b,a)
 ck('exact reversible '+n,s==(V/n).read_text())
p=read(D/'plan.json');old=read(V/'plan.json');r=json.loads(json.dumps(p));r['stage_receipts']['required']=old['stage_receipts']['required'];steps=[s for row in r['profiles']for s in row['steps']]+r['post_independent_build_review_only'];ck('65+2 stages',len(steps)==67)
for s in steps:ck('unoptimized stage '+str(s.get('stage',s.get('profile'))),s['env'].pop('PYTHONOPTIMIZE')=='0' and not any(a in ['-O','-OO']for a in s['argv']))
s=json.dumps(r)
for a,b in reversed(proof['replacements']):s=s.replace(b,a)
ck('complete exact numerical plan reversal',json.loads(s)==old)
t=read(D/'toolchain.json');v=read(V/'toolchain.json');ck('all6821exact tool pins',t['files']==v['files']and len(t['files'])==6821);a=json.loads(json.dumps(t));ck('toolpolicyPYOPT0',a['environment'].pop('PYTHONOPTIMIZE')=='0');a['identity']=v['identity'];ck('other toolpolicy exact',a==v)
ck('zero staticmissing',read(D/'collector-closure.json')['missing']==[])
for n,v in read(D/'collector-closure.json')['files'].items():ck('collectorclosure '+n,h(Path(n))==v)
for n,v in read(D/'input-pins.json').items():ck('inputpin '+n,h(Path(n))==v)
spec=importlib.util.spec_from_file_location('independent_profile_receipt_v3',D/'stage_receipt.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);ident=m.verify({**os.environ,**p['profiles'][0]['steps'][0]['env']});ck('actual source2722/tool6821',ident['source_files']==2722 and ident['tool_files']==6821)
for q in D.rglob('*.py'):ast.parse(q.read_text())
# Old verify instruction preservation, with only first nonassert optimizer guard added.
a=ast.parse((V/'stage_receipt.py').read_text());b=ast.parse((D/'stage_receipt.py').read_text());before=next(n for n in a.body if isinstance(n,ast.FunctionDef)and n.name=='verify');after=next(n for n in b.body if isinstance(n,ast.FunctionDef)and n.name=='verify');ck('verify firstinstruction nonassert debug guard',isinstance(after.body[0],ast.If)and '__debug__'in ast.unparse(after.body[0])and isinstance(after.body[0].body[0],ast.Raise));after.body=after.body[1:];ck('all old verify assertions preserved exact AST',ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False))
# Exact pure verify source must fail before any dependency lookup when optimized.
tree=ast.parse((D/'stage_receipt.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='verify');ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'exact-optimized-verify','exec',optimize=1),ns)
try:ns['verify']({'PATH':'/unreviewed/no-tools','EMCC_CORES':'999'})
except RuntimeError as e:ck('oldB1 optimize bypass rejected',str(e)=='Unoptimized Python is required')
else:raise AssertionError('optimizer bypass accepted')
print(json.dumps({'identity':'independent-current-profile-v3-source-review','checks':len(checks),'check_names':checks,'actual_identity':ident,'reverse_files':len(proof['files']),'commands':65,'guarded_commands':2,'source_files':2722,'tool_files':6821,'compiled_calls':0,'collector_main_calls':0,'assessment_main_calls':0},indent=2))
