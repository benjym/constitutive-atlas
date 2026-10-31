"""Replay old synthetic witnesses against independently preserved revised assessors."""
from pathlib import Path
import importlib.util,json,sys,subprocess
P=Path(__file__).resolve().parent

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
 a=module('assess_paths',P/'revised/assess_paths.py');b=module('assess_parity',P/'revised/assess_parity.py')
 f=P/'frozen';req=json.loads((f/'requests.json').read_text());ref=json.loads((f/'reference-p360.json').read_text());cat=json.loads((f/'generated/models.json').read_text())
 outcomes={}
 expected={'ideal':True,'parity_native':True,'parity_wasm':True}
 for path in sorted((P/'witnesses').glob('*.json')):
  try:a.assess(json.loads(path.read_text()),req,ref,cat);accepted=True;error=None
  except Exception as e:accepted=False;error=type(e).__name__+':'+str(e)
  outcomes[path.stem]={'accepted':accepted,'expected_accepted':expected.get(path.stem,False),'error':error}
 rows=lambda n:json.loads((P/'witnesses'/n).read_text())
 try:b.assess(rows('parity_native.json'),rows('parity_wasm.json'),req);rejected=False
 except Exception:rejected=True
 ideal=b.assess(rows('ideal.json'),rows('ideal.json'),req)
 code="import sys;sys.path.insert(0,sys.argv[1]);import assess_paths"
 proc=subprocess.run([sys.executable,'-I','-S','-B','-O','-c',code,str(P/'revised')],capture_output=True,text=True)
 checks={name:r['accepted']==r['expected_accepted']for name,r in outcomes.items()};checks['pair_witness_rejected']=rejected;checks['ideal_pair_accepted']=ideal['passed'];checks['optimized_refused_before_assessment']=proc.returncode!=0 and 'RuntimeError' in proc.stderr
 out={'identity':'mc-preview-assessor-revised-closure-v1','candidate_calls':0,'compiled_calls':0,'checks':checks,'status':'pass'if all(checks.values())else'fail','outcomes':outcomes,'ideal_pair':ideal,'optimized_process':{'exit':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}}
 (P/'revised-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'checks':checks}))
 if out['status']!='pass':raise SystemExit(1)
if __name__=='__main__':main()
