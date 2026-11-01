import ast,copy,hashlib,json,runpy,sys,tempfile,subprocess
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent; P=D.parent; R=P.parents[2]; S=Path('/private/tmp/atlas-predictor-constraints-v1/source')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError(name)
m=json.loads((P/'manifest.json').read_text()); check('packet identity',h(P/'manifest.json')=='1fef4b10498f8ed6b94a9855db46b73b44a088c61db68b09b6545baa47b4b560')
check('all packet files bound',all(h(R/k)==v for k,v in m['files'].items()))
check('three modified/additional sources bound',all(h(S/k)==v for k,v in m['source_files'].items()))
f=json.loads((P/'coordinator-v1/source-freeze.json').read_text()); b=json.loads((R/'docs/ingestion/manzari-dafalias-1997/delivery-v1/source-freeze-v2.json').read_text())
check('closure identity',h(P/'coordinator-v1/source-freeze.json')=='126d9bc3a221b6e0098c769eee267306d5be3d03f2b02725c824a6063243aa44')
check('578 closure files exact',len(f['source_files'])==578 and all(h(S/k)==v for k,v in f['source_files'].items()))
changed=[k for k in b['source_files'] if f['source_files'].get(k)!=b['source_files'][k]]; added=set(f['source_files'])-set(b['source_files'])
check('575 old unchanged one solver changed two added',changed==['cpp/include/atlas/solver.hpp'] and added==set(m['source_files'])-set(changed),{'changed':changed,'added':sorted(added)})
check('cache inventory explicit and exact',len(f['excluded_generated_python_caches'])==8 and all(h(S/k)==v for k,v in f['excluded_generated_python_caches'].items()) and {str(p.relative_to(S)) for p in S.rglob('*') if p.is_file()}==set(f['source_files'])|set(f['excluded_generated_python_caches']))
old=(P/'original/solver.hpp').read_text(); new=(S/'cpp/include/atlas/solver.hpp').read_text(); before='if(err<settings.residual_tolerance && solution_admissible(model,z,p)){if(predictor){predictor=false;continue;}return true;}'
after='''if(err<settings.residual_tolerance){
            // evaluate_model has checked the predictor domain. Its elastic trial
            // need not satisfy final physical constraints before plastic correction.
            if(predictor){predictor=false;continue;}
            if(solution_admissible(model,z,p))return true;
        }'''
check('exact single generic phase replacement',old.replace(before,after)==new and old.count(before)==1)
check('original source solver exact',h(P/'original/solver.hpp')==b['source_files']['cpp/include/atlas/solver.hpp'])
requests=json.loads((P/'requests.json').read_text()); cases=requests['cases']; byid={c['id']:c for c in cases}; execution=cases+[byid[i] for pair in requests['recovery_pairs'] for i in pair]
check('11 cases 4 recovery pairs 19 calls',len(cases)==11 and len(requests['recovery_pairs'])==4 and len(execution)==19)
for c in cases:
 K,Y,cap=c['parameters']; z=c['initial']; trial=z[0]+K*sum(c['strain'][:3]); pressure=min(trial,Y); gamma=max((trial-Y)/K,0)
 if c['expected']['ok']:check('closed form '+c['id'],max(abs(a-b) for a,b in zip([pressure]*3+[0]*3+[z[6]+gamma,gamma],c['expected']['state']))<1e-14)
for p in [P/'run_fixture.py',P/'check_parity.py',P/'check_source.py']:ast.parse(p.read_text())
# Run author collector against mocked Python transport only. No executable is invoked.
def collector(label,corruption=None):
 out=D/('mock-'+label); counter=[0]
 def fake_run(cmd,**kw):
  i=counter[0];counter[0]+=1;c=execution[i]; initial=[float(x) for x in cmd[cmd.index('--initial')+1].split(',')]
  response={'ok':c['expected']['ok'],'state':copy.deepcopy(c['expected'].get('state',initial))}
  if corruption:corruption(i,response)
  return subprocess.CompletedProcess(cmd,0,json.dumps(response),'')
 with patch.object(sys,'argv',[str(P/'run_fixture.py'),'--solver',str(P/'requests.json'),'--output',str(out)]),patch('subprocess.run',fake_run):
  try:runpy.run_path(str(P/'run_fixture.py'),run_name='__main__')
  except SystemExit:pass
 report=json.loads((out/'report.json').read_text());return report
ideal=collector('ideal');check('ideal collector 19 calls',ideal['status']=='passed' and len(ideal['rows'])==19)
for label,fn in [('shear',lambda i,r:r['state'].__setitem__(3,.001) if i==0 else None),('ep',lambda i,r:r['state'].__setitem__(6,.001) if i==0 else None),('gamma',lambda i,r:r['state'].__setitem__(7,-.01) if i==0 else None),('rollback',lambda i,r:r['state'].__setitem__(7,.1) if i==5 else None),('outcome',lambda i,r:r.update(ok=True) if i==7 else None),('nonfinite',lambda i,r:r['state'].__setitem__(0,float('nan')) if i==0 else None)]:check('collector rejects '+label,collector(label,fn)['status']=='failed')
def parity(label,n,w):
 for suffix,report in [('n',n),('w',w)]: (D/(label+'-'+suffix+'.json')).write_text(json.dumps(report))
 output=D/(label+'-parity.json')
 with patch.object(sys,'argv',[str(P/'check_parity.py'),str(D/(label+'-n.json')),str(D/(label+'-w.json')),'--output',str(output)]):
  try:runpy.run_path(str(P/'check_parity.py'),run_name='__main__')
  except SystemExit:pass
 return json.loads(output.read_text())['status']
w=copy.deepcopy(ideal);w['backend']='wasm';check('ideal parity accepted',parity('ideal',ideal,w)=='passed')
x=copy.deepcopy(w);x['rows'][0]['response']['state'][4]=.01;check('parity rejects state corruption',parity('state-corrupt',ideal,x)=='failed')
x=copy.deepcopy(w);x['rows'].pop();check('parity rejects asymmetric missing row',parity('missing-row',ideal,x)=='failed')
# Deliberate equal-side corruption: checker currently trusts report claims.
n=copy.deepcopy(ideal);w=copy.deepcopy(w);n['rows']=[];w['rows']=[]
accepted=parity('equal-empty',n,w)=='passed';checks.append({'name':'equal empty reports false-accept witness','observed_false_accept':accepted})
n=copy.deepcopy(ideal);w=copy.deepcopy(ideal)
for r in (n,w):r['request_sha256']='wrong';r['rows'][0]['request']['parameters']=[200,20,100]
accepted=parity('equal-wrong-binding',n,w)=='passed';checks.append({'name':'equal wrong frozen binding false-accept witness','observed_false_accept':accepted})
(D/'checks.json').write_text(json.dumps({'status':'prospective-blockers-found','compiled_calls':0,'checks':checks},indent=2)+'\n')
