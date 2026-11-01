"""Synthetic route-auditor fixtures. No physical trajectory or model evidence."""
import copy,json,math,tempfile,unittest
from pathlib import Path
from assess import audit,read,ROOT,HERE,BASE,bits
from driver import rate_request,lab_request
class Fixture:
 def __init__(self,directory):
  self.directory=directory;(directory/'receipts').mkdir();self.counter=0;self.data={'backend':'native','rates':[],'laboratory':[],'guards':[],'transport_error':None,'stopped':None}
  cat=read(ROOT/'docs/reviews/gis2024-mixed-catalogue-v1/generated-eleven/models.json');self.cat=cat
  self.data['descriptor']=self.emit({'function':'atlas_describe','types':[],'args':[],'cli':['--describe']},cat)
  for row in read(HERE/'rate-references.json'):self.data['rates'].append({'id':row['id'],'call':self.emit(rate_request(row),{'ok':True,'values':row['expected']})})
  for row in read(HERE/'laboratory-requests.json'):self.data['laboratory'].append({'id':row['id'],'call':self.lab(row['specification'])})
  control=read(HERE/'laboratory-requests.json')[0]['specification'];self.data['clean']=self.lab(control)
  for row in read(BASE/'guard-cases.json'):self.data['guards'].append({'id':row['id'],'call':self.emit(lab_request(row['specification']),{'ok':False,'message':'synthetic rejection'}),'recovery':self.lab(control)})
  self.data['failure']={'call':self.lab(read(BASE/'failure-case.json')['specification'],True),'recovery':self.lab(control)}
 def emit(self,request,response):
  request=copy.deepcopy(request)
  if 'controls_wire'in request:request['cli']=['/synthetic/wire-controls.txt'if v=='@CONTROLS@'else v for v in request['cli']]
  i=self.counter;self.counter+=1;row={'backend':'native','request':request,'stdout':json.dumps(response)+'\n','stderr':'','returncode':0 if request['function']=='atlas_describe'or response.get('ok')else 1,'synthetic_not_model_evidence':True};(self.directory/'receipts'/f'{i:04d}.json').write_text(json.dumps(row));return {'request':request,'response':copy.deepcopy(response),'receipt':i}
 def sync(self,item):
  file=self.directory/'receipts'/f"{item['receipt']:04d}.json";r=read(file);r['stdout']=json.dumps(item['response'])+'\n';file.write_text(json.dumps(r))
 def lab(self,s,forced=False):
  import struct
  controls=[struct.unpack('>d',bytes.fromhex(b))[0]for b in s['loading']['controls_bits']]if 'loading'in s else[s['target']*math.sin(2*math.pi*s['cycles']*i/s['steps'])if s['cycles']else s['target']*i/s['steps']for i in range(s['steps']+1)]
  protocol=s['protocol'];points=[]
  for index,c in enumerate(controls[:1]if forced else controls):
   z=s['initial'][:];strain=[c,0.,0.,0.,0.,0.]
   if protocol in[2,3]:strain=[c,-.5*c,-.5*c,0.,0.,0.]
   if protocol==3:strain=[0.]*6;z[0]+=c
   if protocol==4:strain=[c,c,c,0.,0.,0.]
   if index and s['target']!=0:z[6]=(1+s['initial'][6])*math.exp(-math.fsum(strain[:3]))-1
   mean=math.fsum(z[:3])/3;dev=[z[i]-mean if i<3 else z[i]for i in range(6)]
   points.append({'control':c,'state':z,'strain':strain,'p':mean,'q':math.sqrt(1.5*math.fsum(x*x for x in dev)),'q_signed':z[0]-.5*(z[1]+z[2]),'u':.5*(s['initial'][1]+s['initial'][2])-.5*(z[1]+z[2])if protocol in[2,3]else None,'iterations':0,'substeps':0,'rejected':0,'error':0.})
  r={'ok':not forced,'schema_version':'0.1','api_version':'experimental-laboratory-scope-0.1','catalogue_hash':self.cat['sha256'],'model':s['model'],'parameters':s['parameters'],'initial':s['initial'],'integration_settings':s['integration_settings'],'protocol':protocol,'steps':s['steps'],'stress':{'source':'state','name':'sigma','measure':'cauchy','scope':'effective','tensor_representation':'mandel','sign':'compression_positive'},'pore_pressure':{'quantity':'change','availability':'reconstructed','assumption':'fixed_radial_total_stress_incompressible_fluid_and_grains'}if protocol in[2,3]else{'quantity':'change','availability':'unavailable','reason':'not_reconstructed_for_protocol'},'points':points}
  if 'loading'in s:r['loading']={'version':'laboratory-controls-0.1','encoding':'ieee754-binary64-hex','controls':controls,'controls_bits':s['loading']['controls_bits']}
  else:r.update(target=s['target'],cycles=s['cycles'])
  return self.emit(lab_request(s),r)
 def audit(self):return audit(self.data,self.directory)
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.f=Fixture(Path(self.tmp.name))
 def poison(self,item,action):action(item['response']);self.f.sync(item);self.assertRaises(Exception,self.f.audit)
 def test_mock_complete(self):self.assertTrue(self.f.audit()['qualification_pass'])
 def test_missing_case(self):self.f.data['laboratory'].pop();self.assertRaisesRegex(ValueError,'coverage',self.f.audit)
 def test_rate_corruption(self):self.poison(self.f.data['rates'][0]['call'],lambda r:r['values'].__setitem__(0,r['values'][0]+1.))
 def test_wrong_catalogue(self):self.poison(self.f.data['descriptor'],lambda r:r.__setitem__('sha256','bad'))
 def test_history_size(self):self.poison(self.f.data['laboratory'][2]['call'],lambda r:r['points'][1]['state'].pop())
 def test_domain(self):self.poison(self.f.data['laboratory'][2]['call'],lambda r:r['points'][1]['state'].__setitem__(13,2.))
 def test_volume(self):self.poison(self.f.data['laboratory'][2]['call'],lambda r:r['points'][1]['state'].__setitem__(6,.62))
 def test_zero_memory(self):self.poison(self.f.data['laboratory'][0]['call'],lambda r:r['points'][1]['state'].__setitem__(7,1e-6))
 def test_settings(self):self.poison(self.f.data['laboratory'][0]['call'],lambda r:r['integration_settings'].__setitem__('max_depth',19))
 def test_exact_loading(self):self.poison(self.f.data['laboratory'][2]['call'],lambda r:r['loading']['controls_bits'].__setitem__(1,'0000000000000000'))
 def test_pore(self):self.poison(self.f.data['laboratory'][0]['call'],lambda r:r['points'][0].__setitem__('u',0.))
 def test_negative_committed(self):self.poison(self.f.data['guards'][0]['call'],lambda r:r.__setitem__('points',[{'state':[0]*14}]))
 def test_failure_prefix(self):self.poison(self.f.data['failure']['call'],lambda r:r['points'].append(copy.deepcopy(r['points'][0])))
 def test_recovery(self):self.poison(self.f.data['failure']['recovery'],lambda r:r['points'][1]['state'].__setitem__(13,.1))
 def test_raw_tamper(self):self.f.data['rates'][0]['call']['response']['values'][0]+=1.;self.assertRaisesRegex(ValueError,'raw',self.f.audit)
 def test_missing_raw(self):(self.f.directory/'receipts/0000.json').unlink();self.assertRaises(Exception,self.f.audit)
 def test_controller(self):self.poison(self.f.data['laboratory'][2]['call'],lambda r:r['points'][1]['strain'].__setitem__(1,1e-4))
 def test_wrong_initial(self):self.poison(self.f.data['laboratory'][2]['call'],lambda r:r['initial'].__setitem__(13,.1))
 def test_stopped(self):self.f.data['stopped']='a';self.assertRaisesRegex(ValueError,'stopped',self.f.audit)
 def test_parity(self):
  from parity import compare
  w=copy.deepcopy(self.f.data);w['backend']='wasm';self.assertTrue(compare(self.f.data,w)['parity_pass']);w['laboratory'][2]['call']['response']['points'][1]['state'][7]+=1e-4;self.assertRaisesRegex(ValueError,'parity',compare,self.f.data,w)
if __name__=='__main__':unittest.main()
