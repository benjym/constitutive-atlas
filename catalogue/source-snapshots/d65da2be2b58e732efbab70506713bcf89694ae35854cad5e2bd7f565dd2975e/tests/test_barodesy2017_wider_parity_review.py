"""Additional synthetic parity regression; never invokes a compiled backend."""
import copy,unittest,json,tempfile
from pathlib import Path
from unittest.mock import patch
from tools import barodesy2017_wider_study as s
from atlas.model import load
from tests.test_barodesy2017_wider_study import synthetic,response
class IndependentParity(unittest.TestCase):
 def test_individually_accepted_well_chained_backend_bias_rejected(self):
  ref,cases,points=s.checked_reference();model=load(s.MODEL_PATH)
  original=s.sha;collector=Path(s.__file__).with_name('test_barodesy2017_wider_wasm.mjs')
  with patch.object(s,'sha',side_effect=lambda p:original(collector)if str(p)==str(s.ROOT/'tools/test_barodesy2017_wider_wasm.mjs')else original(p)):
   return self.compare(ref,cases,points,model)
 def compare(self,ref,cases,points,model):
  native=synthetic(ref,cases,points,model);wasm=copy.deepcopy(native)
  wasm.update(backend='wasm',persistent_recovery=True,native_report_sha256='f'*64,wasm_loader_sha256='1'*64,wasm_binary_sha256='2'*64);wasm.pop('native_sha256')
  for group in wasm['records']:
   initial=cases[group['case']]['initial'].copy()
   for call in group['calls']:
    call['request']['initial']=initial.copy();call['response']['initial']=initial.copy();call['response']['state'][0]+=1e-4;initial=call['response']['state'].copy()
  wasm['transaction_prefix'],wasm['recovery_control']=s.committed_controls(wasm['records'],cases)
  wasm['failure_probes']=[]
  for w in s.probe_requests(wasm['recovery_control']):wasm['failure_probes'].append(w|dict(response=response(w['request'],model,w['request']['initial'],ok=w['kind']=='zero',partial=w['kind']=='budget'),recovery=copy.deepcopy(wasm['recovery_control'])))
  def log(report,path):
   entries=[dict(request=dict(mode='describe'),response=report['runtime_descriptor'])]+[c for g in report['records']for c in g['calls']]+[c for p in report['failure_probes']for c in(p,p['recovery'])];raw=[]
   for index,c in enumerate(entries):
    q=c['request']
    if report['backend']=='native':
     args=['synthetic','--describe']if index==0 else['synthetic','--mode','integrate','--model',q['model'],'--parameters',s.csv(q['parameters']),'--initial',s.csv(q['initial']),'--strain',s.csv(q['strain']),'--integration-settings',s.csv(q['settings'])]
     raw.append(dict(backend='native',request=q,args=args,stdout=json.dumps(c['response']),stderr='',returncode=0 if index==0 or c['response']['ok']else 1))
    else:raw.append(dict(backend='wasm',request=q,name='atlas_describe'if index==0 else'atlas_integrate_with_settings',types=[]if index==0 else['string']*5,args=[]if index==0 else[q['model']]+[s.csv(q[k])for k in('parameters','initial','strain','settings')],raw=json.dumps(c['response'])))
   path.write_text(''.join(json.dumps(r)+'\n'for r in raw));report['transport_sha256']=s.sha(path)
  with patch.object(s.reference,'study',side_effect=lambda:copy.deepcopy(ref)),patch.object(s.subprocess,'run',side_effect=AssertionError('compiled execution forbidden')),tempfile.TemporaryDirectory()as directory:
   d=Path(directory);nr=d/'native.json';nt=d/'native.jsonl';wt=d/'wasm.jsonl';log(native,nt);nr.write_text(json.dumps(native));wasm['native_report_sha256']=s.sha(nr);log(wasm,wt)
   s.verify(native);s.verify(wasm);s.verify_transport(native,nt);s.verify_transport(wasm,wt)
   with self.assertRaisesRegex(ValueError,'native/Wasm state parity budget'):s.parity(wasm,native,nr,wt,nt)
if __name__=='__main__':unittest.main()
