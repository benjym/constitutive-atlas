"""Synthetic assessor/transport tests only; these are not model evidence."""
import copy,json,math,tempfile,unittest,sys
from pathlib import Path
from assess import audit,load,digest,FROZEN,ROOT,csv
from driver import Transport,Recorder

class Fixture:
 def __init__(self,directory):
  self.directory=directory;(directory/'receipts').mkdir();self.model=load(FROZEN/'model.json');self.rows=load(FROZEN/'trajectory-requests.json.gz');self.probes=load(FROZEN/'probes.json');self.policy=load(FROZEN/'policy.json');self.reference=load(ROOT/self.policy['reference']);self.counter=0;self.data={'backend':'native','transport_error':None,'rows':[],'descriptors':[],'probes':[]};self.cat=digest([self.model]);self.ref={c['input']['id']:c for c in self.reference['cases']}
  self.descriptor('main')
  for row in self.rows:
   n=row['partitions'];group={'id':row['id'],'calls':[],'restart_same':[],'restart_fresh':[]};self.data['rows'].append(group);state=row['initial'][:];trace=0.
   targets=self.ref[row['case']]['grids'][-1]['trajectory'];previous=row['initial']
   for j,strain in enumerate(row['increments']):
    segment=j//n;fraction=(j%n+1)/n;start=targets[segment]['state'];end=targets[segment+1]['state'];target=[a+(b-a)*fraction for a,b in zip(start,end)];trace+=math.fsum(strain[:3]);target[6]=(1+row['initial'][6])*math.exp(-trace)-1
    r={'model':row['model'],'initial':state[:],'parameters':row['parameters'],'settings':row['settings'],'strain':strain};item=self.call(r,target,'main');group['calls'].append(item);state=target[:]
   self.descriptor('fresh:'+row['id'])
   for key,context in [('restart_same','main'),('restart_fresh','fresh:'+row['id'])]:
    for original in group['calls'][n:]:group[key].append(self.call(original['request'],original['response']['state'],context))
  control=self.data['rows'][2]['calls'][0]['response']['state'];self.data['control']=self.call(self.probes['control'],control,'main')
  for p in self.probes['probes']:
   r=p['request'];zero=p['id']=='zero-increment';item=self.call(r,r['initial'],'main',success=zero,malformed=p['id'].startswith('incomplete-'),late=p['id']=='late-budget');recovery=self.call(self.probes['control'],control,'main');self.data['probes'].append({'id':p['id'],'call':item,'recovery':recovery})
 def receipt(self,line,response,context):
  index=self.counter;self.counter+=1;pid=100 if context=='main'else 101+[r['id']for r in self.rows].index(context[6:]);d={'index':index,'context':context,'pid':pid,'command':['synthetic-not-evidence'],'line':line,'stdout':json.dumps(response)+'\n','process_poll':None};(self.directory/'receipts'/f'{index:04d}.json').write_text(json.dumps(d));return index
 def descriptor(self,context):
  d={'models':[self.model],'sha256':self.cat};self.data['descriptors'].append({'context':context,'descriptor':d,'receipt':self.receipt('D',d,context)})
 def call(self,r,state,context,success=True,malformed=False,late=False):
  a={'ok':success}
  if not malformed:a.update({k:r[k]for k in ['model','parameters','initial','strain']},state=state[:],catalogue_hash=self.cat,integration_settings={'version':'incremental-settings-0.1','norm':'scaled_component_max',**dict(zip(['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'],r['settings']))},diagnostics={'substeps':1,'iterations':0,'rejected':0,'increment_fractions':[.1 if late else 1.]})
  line='\t'.join(['I',r['model'],csv(r['parameters']),csv(r['initial']),csv(r['strain']),csv(r['settings'])]);return {'request':copy.deepcopy(r),'response':a,'receipt':self.receipt(line,a,context),'context':context}
 def sync(self,item):
  f=self.directory/'receipts'/f"{item['receipt']:04d}.json";r=load(f);r['stdout']=json.dumps(item['response'])+'\n';f.write_text(json.dumps(r))
 def assess(self):return audit(self.data,self.directory,self.model,self.rows,self.probes,self.policy,self.reference)
class AssessorTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.f=Fixture(Path(self.tmp.name))
 def test_complete_mock(self):self.assertTrue(self.f.assess()['backend_qualification_pass'])
 def test_missing_row(self):self.f.data['rows'].pop();self.assertRaisesRegex(ValueError,'coverage',self.f.assess)
 def test_missing_restart(self):self.f.data['rows'][0]['restart_fresh'].pop();self.assertRaisesRegex(ValueError,'restart coverage',self.f.assess)
 def test_request_poison(self):self.f.data['rows'][0]['calls'][1]['request']['initial'][13]+=.01;self.assertRaisesRegex(ValueError,'chain',self.f.assess)
 def test_wrong_catalogue(self):
  item=self.f.data['rows'][0]['calls'][0];item['response']['catalogue_hash']='bad';self.f.sync(item);self.assertRaisesRegex(ValueError,'catalogue',self.f.assess)
 def test_bad_settings(self):
  item=self.f.data['rows'][0]['calls'][0];item['response']['integration_settings']['rate_tolerance']=1.;self.f.sync(item);self.assertRaisesRegex(ValueError,'settings',self.f.assess)
 def test_accuracy_corruption(self):
  item=self.f.data['rows'][0]['calls'][0];item['response']['state'][0]+=100000.;self.f.sync(item);self.assertRaises(ValueError,self.f.assess)
 def test_temporary_raw_disagreement(self):
  self.f.data['rows'][0]['calls'][0]['response']['state'][0]+=1.;self.assertRaisesRegex(ValueError,'raw',self.f.assess)
 def test_full_history_rollback(self):
  item=self.f.data['probes'][0]['call'];item['response']['state'][13]+=.1;self.f.sync(item);self.assertRaisesRegex(ValueError,'rollback',self.f.assess)
 def test_late_failure_has_work(self):
  item=self.f.data['probes'][-2]['call'];item['response']['diagnostics']['substeps']=0;self.f.sync(item);self.assertRaisesRegex(ValueError,'accepted work',self.f.assess)
 def test_restart_poison(self):
  item=self.f.data['rows'][0]['restart_fresh'][0];item['response']['state'][13]+=.01;self.f.sync(item);self.assertRaisesRegex(ValueError,'restart equality',self.f.assess)
 def test_raw_receipt_missing(self):
  (self.f.directory/'receipts'/'0000.json').unlink();self.assertRaisesRegex(ValueError,'receipt',self.f.assess)
 def test_transport_error(self):self.f.data['transport_error']='timeout';self.assertRaisesRegex(ValueError,'transport',self.f.assess)
 def test_zero_mutation(self):
  item=self.f.data['probes'][-1]['call'];item['response']['state'][13]+=.01;self.f.sync(item);self.assertRaisesRegex(ValueError,'rollback',self.f.assess)
 def test_recovery_poison(self):
  item=self.f.data['probes'][0]['recovery'];item['response']['state'][13]+=.01;self.f.sync(item);self.assertRaisesRegex(ValueError,'persistent recovery',self.f.assess)
 def test_volume_poison(self):
  item=self.f.data['rows'][1]['calls'][0];item['response']['state'][6]+=.001;self.f.sync(item);self.assertRaisesRegex(ValueError,'volume',self.f.assess)
 def test_reference_adequacy(self):
  self.f.reference['cases'][0]['fine_difference']['h']=1.;self.assertRaisesRegex(ValueError,'adequacy',self.f.assess)
 def test_bad_descriptor(self):
  self.f.data['descriptors'][0]['descriptor']['sha256']='bad';self.assertRaisesRegex(ValueError,'catalogue identity',self.f.assess)
 def test_missing_probe(self):
  self.f.data['probes'].pop();self.assertRaisesRegex(ValueError,'probe coverage',self.f.assess)
class TransportTests(unittest.TestCase):
 def test_raw_saved_before_json_error(self):
  with tempfile.TemporaryDirectory()as d:
   r=Recorder(Path(d)/'receipts');t=Transport([sys.executable,'-c','import sys;sys.stdin.readline();print("broken-json",flush=True)'],r,'mock')
   try:
    with self.assertRaises(json.JSONDecodeError):t.send('D')
    self.assertIn('broken-json',load(r.directory/'0000.json')['stdout'])
   finally:t.close()
if __name__=='__main__':unittest.main()
