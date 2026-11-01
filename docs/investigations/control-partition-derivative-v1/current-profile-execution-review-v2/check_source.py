"""Independent rebind/source/tool checks; no collector mains or backend calls."""
import sys
sys.dont_write_bytecode=True
import ast,hashlib,importlib.util,json,os,shutil
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'current-profile-execution-v2';V=C/'current-profile-execution-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('author exact manifest',h(D/'manifest.json')=='eebf5d8be93aa8d385fdf74d793d6dde22d6f571e21889f7a924fa2429455669')
m=read(D/'manifest.json')['files']
for n,v in m.items():ck('packet '+n,h(D/n)==v)
ck('exact packet inventory',set(m)|{'manifest.json'}=={p.relative_to(D).as_posix()for p in D.rglob('*')if p.is_file()})
proof=read(D/'rebind-proof.json');p=read(D/'plan.json');old=read(V/'plan.json')
for n,e in proof['files'].items():
 ck('pinned old/new '+n,h(V/n)==e['old_sha256'] and h(D/n)==e['new_sha256']);text=(D/n).read_text()
 for a,b in reversed(proof['replacements']):text=text.replace(b,a)
 ck('reverse exact '+n,text==(V/n).read_text())
r=json.loads(json.dumps(p));r.pop('stage_receipts');r['source_freeze']=old['source_freeze'];r['source_files']=2628
for i,row in enumerate(r['profiles']):
 row['status']=old['profiles'][i]['status']
 for step in row['steps']:
  for k in ['PATH','EMCC_CORES','EM_CACHE']:step['env'].pop(k)
for step in r['post_independent_build_review_only']:step.pop('env')
text=json.dumps(r)
for a,b in reversed(proof['replacements']):text=text.replace(b,a)
ck('complete plan reverses exact numerical/command identity',json.loads(text)==old)
ck('65 commands',sum(len(x['steps'])for x in p['profiles'])==65)
ck('zero missing original94 resolved',read(D/'collector-closure.json')['missing']==[])
S=Path(p['source_directory']);f=read(Path(p['source_freeze']))['files'];ck('2722complete source',len(f)==2722 and set(f)=={q.relative_to(S).as_posix()for q in S.rglob('*')if q.is_file()})
for n,v in f.items():ck('source '+n,h(S/n)==v)
for n,v in read(D/'collector-closure.json')['files'].items():ck('collector '+n,h(Path(n))==v)
t=read(D/'toolchain.json');ck('6821 frozen tool files',len(t['files'])==6821)
for n,e in t['files'].items():ck('tool '+n,str(Path(n).resolve())==e['realpath'] and h(Path(n))==e['sha256'])
for n,e in t['commands'].items():
 found=shutil.which(n,path=t['PATH']);ck('resolution '+n,found==(e['path']if e else None) and (not found or str(Path(found).resolve())==e['realpath']))
for n,v in read(D/'input-pins.json').items():ck('input pin '+n,h(Path(n))==v)
for row in p['profiles']:
 for step in row['steps']:
  ck('stage required environment '+row['profile']+'/'+step['stage'],step['env']['EMCC_CORES']=='1' and step['env']['EM_CACHE']==t['environment']['EM_CACHE'] and step['env']['PATH']==t['PATH'] and step['cwd']==str(S))
  if step['argv'][0]=='cmake' and '--build'in step['argv']:ck('serial '+step['stage'],step['argv'][-2:]==['--parallel','1'])
for q in D.rglob('*.py'):ast.parse(q.read_text())
# Exact original function, Python optimizer only; no altered author file.
raw=(D/'stage_receipt.py').read_text();tree=ast.parse(raw);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='verify');ns={'D':D,'read':read,'sha':h,'Path':Path,'shutil':shutil}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'exact-verify-optimized-source','exec',optimize=1),ns)
env={**os.environ,**p['profiles'][0]['steps'][0]['env'],'PYTHONOPTIMIZE':'1','PATH':'/unreviewed/no-tools','EMCC_CORES':'999','EM_CACHE':'/unreviewed/shared-cache'}
observed=ns['verify'](env)
ck('B1 optimized exact checker accepts wrong PATH/core/cache',observed['source_files']==2722)
ck('B1 optimization not frozen/rejected','PYTHONOPTIMIZE'not in t['ambient_exact'] and all('PYTHONOPTIMIZE'not in st['env'] for row in p['profiles']for st in row['steps']) and 'if not __debug__'not in raw)
print(json.dumps({'identity':'independent-profile-plan-v2-source-review','checks':len(checks),'check_names':checks,'source_files':2722,'toolchain_files':6821,'reverse_adapters':len(proof['files']),'commands':65,'compiled_calls':0,'assessment_main_calls':0,'B1_witness':{'pure_exact_source_compile_optimize':1,'no_process_or_backend_executed':True,'environment':{k:env[k]for k in ['PYTHONOPTIMIZE','PATH','EMCC_CORES','EM_CACHE']},'checker_returned':observed},'decision':'BLOCKED'},indent=2))
