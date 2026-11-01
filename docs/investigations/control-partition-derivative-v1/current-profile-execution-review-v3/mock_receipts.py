"""Independent pure receipt predicates and optimized startup guard; no mains."""
import sys
sys.dont_write_bytecode=True
import ast,copy,hashlib,importlib.util,json,os,subprocess
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'current-profile-execution-v3';spec=importlib.util.spec_from_file_location('review_receipt',D/'stage_receipt.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);read=lambda p:json.loads(p.read_text());p=read(D/'plan.json');checks=[]
def ck(n,v):assert v,n;checks.append(n)
st=p['profiles'][0]['steps'][0];expected=dict(identity='current-profile-stage-receipt-v3',phase='pre',profile='power-creep',stage=st['stage'],command=st,packet_manifest_sha256=hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),source_files=2722,tool_files=6821,source_freeze_sha256='synthetic-source-freeze',toolchain_sha256='synthetic-toolchain',plan_sha256='synthetic-plan');good={**expected,'passed':True};m.validate_pre(good,expected);ck('exact complete pre accepts',True)
for key in expected:
 for mode in ['missing','wrong']:
  q=copy.deepcopy(good)
  if mode=='missing':q.pop(key)
  else:q[key]='wrong'
  result={'passed':False}
  try:m.finish_post(result,q,expected,0,{'path':'synthetic-out','sha256':'out'},{'path':'synthetic-err','sha256':'err'},'synthetic-prehash')
  except ValueError:pass
  else:raise AssertionError('bad pre accepted '+mode+key)
  ck(mode+' pre '+key,result['passed']is False and result['exit_status']==0 and result['stdout']['sha256']=='out'and result['stderr']['sha256']=='err'and result['pre_receipt_sha256']=='synthetic-prehash')
for value in [False,1,0,'false','yes',None,[],{}]:
 q={**good,'passed':value}
 try:m.validate_pre(q,expected)
 except ValueError:pass
 else:raise AssertionError('truthy/nonbool pre accepted')
 ck('reject pre passed '+repr(value),True)
for status in [1,7,-9,None,False,True,0.0,'0']:
 r={'passed':False}
 try:m.finish_post(r,good,expected,status,{'sha256':'out'},{'sha256':'err'},'pre')
 except ValueError:pass
 else:raise AssertionError('bad status accepted')
 ck('reject status '+repr(status),r['passed']is False and type(r['exit_status'])is type(status)and r['exit_status']==status and r['stdout']=={'sha256':'out'}and r['stderr']=={'sha256':'err'})
r={'passed':False};m.finish_post(r,good,expected,0,{'sha256':'out'},{'sha256':'err'},'pre');ck('integer0 exact post accepts',r['passed']is True and r['exit_status']==0)
# Old actual witnesses, interpreted using original shape/missing identities.
for q in [{'passed':True,'command':st},{'passed':'false','command':st}]:
 try:m.validate_pre(q,expected)
 except ValueError:pass
 else:raise AssertionError('originalB2 witness still accepted')
 ck('oldB2 witness rejects',True)
for mode in ['-O','-OO']:
 cp=subprocess.run([sys.executable,mode,str(D/'stage_receipt.py'),'--help'],env={**os.environ,'PYTHONOPTIMIZE':'0','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True)
 ck('optimized entry '+mode+' rejects before main',cp.returncode!=0 and b'Unoptimized Python is required'in cp.stderr)
# Source order proof: post raw/status capture precedes packet/env/source/pre gates;
# exclusive saved receipt is after exception capture, retaining failed identity.
source=(D/'stage_receipt.py').read_text();ck('post raw binds before gates',source.index("result['exit_status']=a.exit_status")<source.index("manifest=read(D/'manifest.json')")<source.index('finish_post(result,q,wanted'))
ck('exclusive write after exception retention',source.index("except Exception as exc:result['error']=str(exc)")<source.index("with expected.open('x')"))
print(json.dumps({'identity':'independent-profile-v3-pure-receipt-mocks','checks':len(checks),'check_names':checks,'pure_synthetic_receipt_cases':True,'optimizer_startup_queries':2,'compiled_calls':0,'collector_main_calls':0,'assessment_main_calls':0,'passed':True},indent=2))
