"""Adversarial synthetic receipts using exact published checked_receipt function."""
import ast,hashlib,json,shutil,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;report=json.loads((D/'audit.json').read_text());BASE=report['base'];sha=lambda b:hashlib.sha256(b).hexdigest();git=lambda p:subprocess.check_output(['git','show',BASE+':'+p]);plan=json.loads((D/'archive-plan.json').read_text())
# Retain old candidate bytes only within this packet; installation remains separate.
for item in plan['canonical_candidates']:
 b=git(item['original_path']);assert sha(b)==item['sha256'];q=D/'preservation-bytes'/item['canonical_archive'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
source=(D/'published-bytes/atlas/evidence.py').read_text();tree=ast.parse(source);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='checked_receipt');env={'Path':Path,'json':json,'_sha':lambda p:sha(p.read_bytes())};exec(compile(ast.Module(body=[fn],type_ignores=[]),'exact-published-checked_receipt','exec'),env);check=env['checked_receipt']
rp='catalogue/agent-reviews/vw96-agent-v1.json';target='cpp/include/atlas/solver.hpp';expected=report['critical_consumers'][target]['sha256'];canonical='catalogue/source-snapshots/'+expected+'/'+target;R=D/'synthetic-context';assert not R.exists(),'preserve existing test context'
def put(n,b):
 p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def mapping(value):put('catalogue/agent-reviews/source-archive-map.json',(json.dumps(value)+'\n').encode())
original=git(rp);old=git(target);patched=Path(report['patched_solver']['path']).read_bytes();put(rp,original);put(target,patched)
base={'version':'immutable-source-archive-map-0.1','documents':{rp:sha(original)},'entries':[{'original_path':target,'sha256':expected,'archived_path':canonical}]};results=[]
def trial(name,success):
 try:result=check(R,rp,target,expected);passed=result.read_bytes()==old
 except(ValueError,OSError)as e:passed=False
 assert passed==success,name;results.append({'name':name,'expected_success':success,'passed':True})
trial('new live solver cannot satisfy old pin without sidecar',False);mapping(base);trial('missing archive rejects without live fallback',False);put(canonical,old);trial('exact canonical header and document pin resolves historical bytes',True)
put(canonical,b'corrupt');trial('corrupt canonical rejects without fallback',False);put(canonical,old)
x=json.loads(json.dumps(base));x['documents'][rp]='0'*64;mapping(x);trial('wrong document pin rejects',False)
x=json.loads(json.dumps(base));x['entries']*=2;mapping(x);trial('ambiguous archive rejects',False)
x=json.loads(json.dumps(base));x['entries'][0]['archived_path']='elsewhere.hpp';mapping(x);trial('noncanonical archive rejects',False)
mapping(base);put(rp,original+b' ');trial('mutated review rejects',False);put(rp,original)
# A model/header mismatched expected hash is never silently accepted.
try:check(R,rp,target,report['patched_solver']['sha256']);raise AssertionError('wrong expected accepted')
except ValueError:results.append({'name':'new expected hash absent from old immutable review rejects','expected_success':False,'passed':True})
trial('restored historical binding recovers',True)
shutil.rmtree(R)
(D/'preservation-checks.json').write_text(json.dumps({'identity':'md1997-release-preservation-source-checks-v3','tests':results,'passed':True,'compiled_calls':0,'exact_published_function':True},indent=2)+'\n');print(json.dumps({'checks':len(results),'passed':True,'compiled_calls':0}))
