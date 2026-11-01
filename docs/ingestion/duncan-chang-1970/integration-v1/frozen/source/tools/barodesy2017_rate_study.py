"""Bounded instantaneous research rate study; no AD/integration/admission claim."""
import argparse,copy,hashlib,json,math,pathlib,re,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.model import load,interpret
from tools.barodesy2017_reference_check import verify_reference
from tools.reference_barodesy2017 import rate as independent_rate
MODEL=ROOT/'models/research/barodesy2017/body-zero-spin.json'
REFERENCE=ROOT/'catalogue/investigations/barodesy2017-rates-v1/reference.json'
VERSION='barodesy2017-instantaneous-rate-study-v1'
BUDGET=2e-13
STRESS_COMPONENT_BUDGET=2e-13
VOID_ULP_BUDGET=4
FIELDS={'ok','model','catalogue_hash','parameters','state','increment','values','message'}
def require(ok,msg):
 if not ok:raise ValueError(msg)
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(path):return json.loads(pathlib.Path(path).read_text(),parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfiniteJSON')))
def numeric(v):
 try:return type(v) in(int,float)and math.isfinite(v)
 except OverflowError:return False
def vector(v,n):
 require(type(v)is list and len(v)==n and all(numeric(x)for x in v),'finite numeric vector/shape');return v
def exact(actual,expected):
 if type(expected)is dict:return type(actual)is dict and set(actual)==set(expected)and all(exact(actual[k],v)for k,v in expected.items())
 if type(expected)is list:return type(actual)is list and len(actual)==len(expected)and all(exact(a,b)for a,b in zip(actual,expected))
 if type(expected)in(int,float):return numeric(actual)and actual==expected
 return type(actual)is type(expected)and actual==expected
def catalogue():
 m=load(MODEL);return m,digest([m])
def reference():
 r=read(REFERENCE);verify_reference(r);require(r.get('case_count')==111 and len(r.get('cases',[]))==111,'111referencecases required')
 for c in r['cases']:require(c['input_sha256']==digest(c['request']),'reference request hash')
 return r
def wire(case,model):
 r=case['request'];p=r['parameters']|{'sigma_star':1000.}
 return dict(model=model['id'],parameters=[p[n]for n in model['parameters']],state=r['state']['sigma']+[r['state']['e']],increment=r['increment'])
def support_cases(model):
 p={n:f['default']for n,f in model['parameters'].items()if n!='sigma_star'}
 out=[]
 for scale in (1e-50,1.,1e50):
  q={'state':{'sigma':[scale,scale,scale*1e-10,0.,0.,0.],'e':.8},'increment':[.001,0.,0.,0.,0.,0.],'parameters':p}
  out.append({'id':'strict-interior-scale-'+str(scale),'request':q,'oracle':independent_rate(q['state'],q['increment'],p,160)})
 return out
def invalid_requests(model,ref):
 base=wire(ref['cases'][0],model);out=[]
 for c in ref['rejected_cases']:out.append({'id':c['id'],'request':wire(c,model)})
 for name,field,value in [('zero-stress','state',[0.]*6+[.8]),('negative-void','state',base['state'][:6]+[-1.]),('normalization-underflow','increment',[1e-200,0.,0.,0.,0.,0.]),('tiny-nonhydro-underflow','increment',[.1,.1,.1,1e-200,0.,0.]),('wrong-parameter-count','parameters',base['parameters'][:-1]),('wrong-state-count','state',base['state'][:-1]),('wrong-loading-count','increment',base['increment'][:-1])]:
  w=copy.deepcopy(base);w[field]=value;out.append(dict(id=name,request=w))
 for name,sig in [('indefinite-invariant-cancellation',[9.348667422616327,1.9672983155680759,-3.9997926126179505e-17,0.,0.,0.])]+[('rank-diagonal-'+str(t),[1.,1.,t,0.,0.,0.])for t in(-1e-16,0.,1e-16)]:
  w=copy.deepcopy(base);w['state']=sig+[.8];out.append({'id':name,'request':w})
 n=[1/3,2/3,2/3]
 for t in(-1e-16,1e-16):
  a=[[float(i==j)+(t-1)*n[i]*n[j]for j in range(3)]for i in range(3)]
  sig=[a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]
  w=copy.deepcopy(base);w['state']=sig+[.8];out.append({'id':'rank-oblique-'+str(t),'request':w})
 return out

def validate_response(response,request,model_hash,success):
 require(type(response)is dict and set(response)==FIELDS,'exact response fields')
 require(response['ok']is success,'strict response status')
 require(response['catalogue_hash']==model_hash and type(response['catalogue_hash'])is str,'catalogue binding')
 for name in ('model','parameters','state','increment'):require(exact(response[name],request[name]),'response request binding:'+name)
 require(type(response['message'])is str,'message type')
 if success:require(response['message']=='','success message');vector(response['values'],7)
 else:require(response['values']is None and response['message']=='unsupported research rate request','failure shape/no usable rates')
def envelope(request,model_hash,values):return {'ok':values is not None,'catalogue_hash':model_hash,**copy.deepcopy(request),'values':values,'message':''if values is not None else'unsupported research rate request'}
def python_call(request,model,model_hash):
 try:
  vector(request['parameters'],len(model['parameters']));vector(request['state'],7);vector(request['increment'],6)
  p=dict(zip(model['parameters'],request['parameters']));require(request['model']==model['id'],'model')
  require(all(f['min']<=p[n]<=f['max']for n,f in model['parameters'].items()),'parameter bounds')
  z={'sigma':request['state'][:6],'e':request['state'][6]};out=interpret(model,z,z,request['increment'],p);v=list(out['sigma'].v)+[out['e']];vector(v,7)
 except(ValueError,ArithmeticError,TypeError):v=None
 return envelope(request,model_hash,v)
def write_report(path,report):
 pathlib.Path(path).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
def collect(call,backend,artifacts=None,checkpoint=None):
 model,mh=catalogue();ref=reference();records=[];invalid=[];support=[]
 report=dict(version=VERSION,backend=backend,budget=BUDGET,model_sha256=sha(MODEL),reference_sha256=sha(REFERENCE),oracle_script_sha256=sha(ROOT/'tools/reference_barodesy2017.py'),catalogue_hash=mh,model_definition=model,parameter_order=list(model['parameters']),artifacts=artifacts or[],records=records,support_records=support,invalid_records=invalid,claims={'instantaneous_primal_only':True,'AD_validated':False,'integrated':False,'admitted':False})
 def save():
  if checkpoint is not None:checkpoint(report)
 save()
 for case in ref['cases']:
  req=wire(case,model);row=dict(id=case['id'],request=req);records.append(row);save();row['response']=call(req);save()
 for case in support_cases(model):
  req=wire(case,model);row=dict(id=case['id'],request=req);support.append(row);save();row['response']=call(req);save()
 control=records[0]['request']
 for item in invalid_requests(model,ref):
  row=copy.deepcopy(item);invalid.append(row);save();row['response']=call(item['request']);save();row['recovery']=call(control);save()
 return report
def ulp_distance(a,b):
 require(numeric(a)and numeric(b),'ULP finite scalars')
 if a==b:return 0
 def key(x):
  bits=struct.unpack('>Q',struct.pack('>d',float(x)))[0]
  return (~bits&((1<<64)-1))if bits>>63 else bits|(1<<63)
 return abs(key(a)-key(b))
def channel_checks(actual,expected,req,derived):
 vector(actual,7);vector(expected,7)
 # Every exact zero retained by the independent oracle must remain exact.
 for a,b in zip(actual,expected):
  if b==0:require(a==0,'exact zero channel')
 de=req['increment'];void=-(1+req['state'][6])*sum(de[:3])
 require(ulp_distance(actual[6],void)<=VOID_ULP_BUDGET,'void closure four ULP')
 loading_norm=math.hypot(*de)
 scale=math.hypot(*req['state'][:6])*loading_norm*abs(derived['c3'])*(abs(derived['f'])+abs(derived['g']))if loading_norm else 0.
 stress_error=max(abs(a-b)for a,b in zip(actual[:6],expected[:6]))
 if scale==0:require(stress_error==0,'zero loading stress')
 else:require(stress_error/scale<=STRESS_COMPONENT_BUDGET,'percomponent input stress-rate scale')
 return stress_error/scale if scale else 0.,ulp_distance(actual[6],void)

def artifact_structure(artifacts,backend,check_files):
 require(type(artifacts)is list,'artifact list')
 require(len(artifacts)==(0 if backend=='python' else 1 if backend=='native' else 2),'complete backend artifacts')
 seen=set()
 for a in artifacts:
  require(type(a)is dict and set(a)=={'path','sha256'},'artifact fields')
  require(type(a['path'])is str and bool(a['path'])and a['path']not in seen,'artifact path')
  require(type(a['sha256'])is str and re.fullmatch('[0-9a-f]{64}',a['sha256'])is not None,'artifact digest')
  seen.add(a['path'])
  if check_files:require(sha(a['path'])==a['sha256'],'backend artifact changed')
def assess(report,check_artifacts=True,native_report_path=None):
 require(type(check_artifacts)is bool,'artifact policy must be Boolean')
 model,mh=catalogue();ref=reference()
 require(report.get('version')==VERSION and report.get('backend')in('python','native','wasm'),'protocol')
 require(type(report.get('budget'))is float and report['budget']==BUDGET,'fixed budget')
 require(report.get('model_sha256')==sha(MODEL)and report.get('reference_sha256')==sha(REFERENCE),'model/reference binding')
 require(report.get('oracle_script_sha256')==sha(ROOT/'tools/reference_barodesy2017.py'),'oracle source binding')
 require(report.get('catalogue_hash')==mh and exact(report.get('model_definition'),model) and exact(report.get('parameter_order'),list(model['parameters'])),'catalogue/order identity')
 require(exact(report.get('claims'),{'instantaneous_primal_only':True,'AD_validated':False,'integrated':False,'admitted':False}),'bounded claims')
 artifact_structure(report.get('artifacts'),report['backend'],check_artifacts)
 records=report.get('records');require(type(records)is list and len(records)==111,'complete ordered corpus')
 maximum=0.;worst=None;component_max=0.;void_max=0
 for row,case in zip(records,ref['cases']):
  req=wire(case,model);require(row.get('id')==case['id']and exact(row.get('request'),req),'record request binding')
  validate_response(row.get('response'),req,mh,True);expected=case['oracle']['sigma_rhs']+[case['oracle']['e_rhs']];actual=row['response']['values']
  ce,ve=channel_checks(actual,expected,req,case['oracle']['derived']);component_max=max(component_max,ce);void_max=max(void_max,ve)
  e=math.hypot(*(a-b for a,b in zip(actual,expected)))/max(1.,math.hypot(*expected));require(e<=BUDGET,'rate accuracy:'+case['id'])
  if e>=maximum:maximum=e;worst=case['id']
 support=report.get('support_records');support_expected=support_cases(model)
 require(type(support)is list and len(support)==len(support_expected),'complete support witnesses')
 for row,case in zip(support,support_expected):
  req=wire(case,model);require(row.get('id')==case['id']and exact(row.get('request'),req),'support witness binding')
  validate_response(row.get('response'),req,mh,True);actual=row['response']['values'];expected=case['oracle']['sigma_rhs']+[case['oracle']['e_rhs']]
  ce,ve=channel_checks(actual,expected,req,case['oracle']['derived']);component_max=max(component_max,ce);void_max=max(void_max,ve)
  e=math.hypot(*(a-b for a,b in zip(actual,expected)))/max(1.,math.hypot(*expected));require(e<=BUDGET,'support witness numerical budget')
  if e>=maximum:maximum=e;worst=case['id']
 invalid=report.get('invalid_records');expected_invalid=invalid_requests(model,ref)
 require(type(invalid)is list and len(invalid)==len(expected_invalid),'complete invalid corpus')
 for row,item in zip(invalid,expected_invalid):
  require(row.get('id')==item['id']and exact(row.get('request'),item['request']),'invalid request binding')
  validate_response(row.get('response'),item['request'],mh,False)
  validate_response(row.get('recovery'),records[0]['request'],mh,True)
  require(exact(row['recovery'],records[0]['response']),'persistent recovery differs from control')
 if report['backend']=='wasm':
  # Explicit override makes an immutable archived transcript relocatable.
  pinned=native_report_path if native_report_path is not None else report.get('native_report_path')
  require(isinstance(pinned,(str,pathlib.Path)),'pinned native report path required')
  native=read(pinned);require(native.get('backend')=='native'and sha(pinned)==report.get('native_report_sha256'),'native transcript binding')
  assess(native,check_artifacts=check_artifacts);parity=0.
  for a,b in zip(records+support,native['records']+native['support_records']):
   require(a['id']==b['id']and exact(a['request'],b['request']),'parity request identity')
   left,right=a['response']['values'],b['response']['values'];parity=max(parity,math.hypot(*(x-y for x,y in zip(left,right)))/max(1.,math.hypot(*right)))
  require(parity<=BUDGET and numeric(report.get('maximum_native_parity'))and math.isclose(parity,report['maximum_native_parity'],rel_tol=1e-12,abs_tol=1e-30),'native/Wasm parity metric')
 return {'cases':111,'support_cases':len(support),'invalids':len(invalid),'maximum_normalized_rate_error':maximum,'worst_case':worst,'maximum_stress_component_envelope_scaled_error':component_max,'maximum_void_closure_ulps':void_max,'stress_component_budget':STRESS_COMPONENT_BUDGET,'void_ulp_budget':VOID_ULP_BUDGET,'artifacts_verified_now':check_artifacts,'fresh_reference_verified':True,'AD_validated':False}
def native_report(binary,checkpoint=None,transport_path=None):
 binary=pathlib.Path(binary).resolve();before=sha(binary);model,mh=catalogue()
 def invoke(args,describe=False):
  r=subprocess.run([str(binary),*args],capture_output=True,text=True,timeout=30)
  # Raw transport survives malformed JSON, failed status binding and assessment.
  if transport_path is not None:
   with pathlib.Path(transport_path).open('a')as f:f.write(json.dumps({'arguments':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n')
  require(r.returncode in(0,1),'native abnormalexit')
  out=json.loads(r.stdout,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfiniteJSON')))
  if describe:require(r.returncode==0,'descriptor exit status')
  else:require(type(out)is dict and type(out.get('ok'))is bool and r.returncode==(0 if out['ok']else 1),'native response exit status')
  return out
 desc=invoke(['--describe'],True);require(desc.get('sha256')==mh and exact(desc.get('models'),[model]),'compiled complete catalogue mismatch')
 require(list(desc['models'][0]['parameters'])==list(model['parameters']),'compiled parameter order mismatch')
 def call(w):return invoke([w['model'],','.join(map(repr,w['parameters'])),','.join(map(repr,w['state'])),','.join(map(repr,w['increment']))])
 report=collect(call,'native',[dict(path=str(binary),sha256=before)],checkpoint);require(sha(binary)==before,'binary changed duringstudy');return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native',type=pathlib.Path);ap.add_argument('--verify',type=pathlib.Path);ap.add_argument('--output',type=pathlib.Path);ap.add_argument('--native-report',type=pathlib.Path);ap.add_argument('--historical-numerical-replay',action='store_true');args=ap.parse_args()
 if args.verify:
  print(json.dumps(assess(read(args.verify),check_artifacts=not args.historical_numerical_replay,native_report_path=args.native_report),indent=2));return
 require(args.output is not None,'explicit output required; tests never write retained evidence')
 require(not args.historical_numerical_replay,'historical replay only supported with --verify')
 checkpoint=lambda r:write_report(args.output,r)
 if args.native:
  transport=pathlib.Path(str(args.output)+'.transport.jsonl');transport.write_text('');report=native_report(args.native,checkpoint,transport)
 else:
  m,h=catalogue();report=collect(lambda w:python_call(w,m,h),'python',checkpoint=checkpoint)
 checkpoint(report);assessment=assess(report,native_report_path=args.native_report);report['assessment']=assessment;checkpoint(report);print(json.dumps(assessment,indent=2))
if __name__=='__main__':main()
