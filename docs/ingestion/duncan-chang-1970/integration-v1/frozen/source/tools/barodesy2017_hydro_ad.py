"""Exact nonzero hydrostatic generated-model AD assessment; no near-hydro claim."""
import argparse,copy,json,math,pathlib,subprocess
from decimal import Decimal,localcontext
from tools import barodesy2017_rate_study as rate
from tools import barodesy2017_material_ad as common
from tools import reference_barodesy2017_hydro as reference
ROOT=pathlib.Path(__file__).resolve().parents[1]
VERSION='barodesy2017-exact-hydro-ad-v1'
COLUMNS=common.COLUMNS
FIELDS=rate.FIELDS|{'jacobian','columns'}
BUDGET=2e-12
PRECISION_BUDGET='1e-94'
FAILURE='unsupported exact hydro material AD request'
CLAIMS={'exact_hydro_AD_validated':False,'near_hydro_AD':False,'zero_loading_AD':False,'integrated':False,'admitted':False}
def rotate_sigma(v):
 # Fixed dense orthogonal Cartesian basis, rounded into actual binary64 inputs.
 q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]];s=math.sqrt(2);a=[[v[0],v[3]/s,v[5]/s],[v[3]/s,v[1],v[4]/s],[v[5]/s,v[4]/s,v[2]]]
 b=[[sum(q[i][k]*a[k][l]*q[j][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)]
 return [b[0][0],b[1][1],b[2][2],s*b[0][1],s*b[1][2],s*b[0][2]]
def cases():
 sigma=[120000.,80000.,100000.,2000.,-3000.,4000.];out=[]
 for soil,p in reference.SOILS.items():
  for name,sig in [('anisotropic',sigma),('rotated-anisotropic',rotate_sigma(sigma))]:
   for s in(-1.,-.1,-.001,.001,.1,1.):out.append({'id':soil.lower()+'-'+name+'-'+str(s),'parameters':p,'state':{'sigma':sig,'e':.8},'increment':[s]*3+[0.]*3})
 return out
def wire(c,m):
 p=c['parameters']|{'sigma_star':1000.};return {'model':m['id'],'parameters':[p[n]for n in m['parameters']],'state':c['state']['sigma']+[c['state']['e']],'increment':c['increment']}
def expected(c):
 a=reference.exact_hydro(c['state']['sigma'],c['state']['e'],c['increment'],c['parameters'],100);b=reference.exact_hydro(c['state']['sigma'],c['state']['e'],c['increment'],c['parameters'],160)
 with localcontext()as ctx:
  ctx.prec=180;left=a['values']+[x for row in a['jacobian']for x in row];right=b['values']+[x for row in b['jacobian']for x in row];difference=max(abs(x-y)/max(Decimal(1),abs(y))for x,y in zip(left,right));rate.require(difference<=Decimal(PRECISION_BUDGET),'hydro reference precision unresolved')
 return {'values':list(map(float,b['values'])),'jacobian':[list(map(float,row))for row in b['jacobian']],'precision_digits':[100,160],'maximum_precision_difference':str(difference)}
def frozen_reference():
 return {'version':reference.VERSION,'source':{'url':'https://doi.org/10.1007/s11440-016-0458-4','locator':'body Eqs1–10, Table2; exact nonzero hydro derivative derived in independent review; body2p density'},'scope':'Exact nonzero hydrostatic first derivative only; no compiled AD result','columns':COLUMNS,'records':[{'case':c,'reference':expected(c)}for c in cases()]}
def verify_frozen(path=None):
 path=pathlib.Path(path)if path is not None else ROOT/'catalogue/investigations/barodesy2017-hydro-ad-v1/reference.json';r=frozen_reference();rate.require(rate.exact(rate.read(path),r),'entire frozen hydro reference mismatch');return len(r['records'])
def invalids(m):
 # Keep inherited requests exactly: nonhydro ones test scope rejection, not a hydro K0 law.
 out=copy.deepcopy(rate.invalid_requests(m,rate.reference()))
 base=wire(cases()[0],m)
 for name,de in [('zero',[0.]*6),('nonhydro',[.1,.1,.1,.001,0.,0.]),('one-ulp-nonhydro',[math.nextafter(.1,math.inf),.1,.1,0.,0.,0.]),('wrong-loading-count',[.1]*3+[0.]*2)]:
  w=copy.deepcopy(base);w['increment']=de;out.append({'id':'hydro-'+name,'request':w})
 # Domain rejection must also be exercised at supported exact hydro loading;
 # inherited nonhydro requests alone cannot reach state/domain validation.
 for sign in(-1.,1.):
  hydro=copy.deepcopy(base);hydro['increment']=[sign*.1]*3+[0.]*3
  states=[('indefinite-stress',[100000.,100000.,-100000.,0.,0.,0.,.8]),('zero-stress',[0.]*6+[.8]),('negative-void',hydro['state'][:6]+[-.1])]
  for name,state in states:
   w=copy.deepcopy(hydro);w['state']=state;out.append({'id':f'hydro-domain-{sign}-{name}','request':w})
  for j,(name,spec)in enumerate(m['parameters'].items()):
   for edge,direction in(('min',-math.inf),('max',math.inf)):
    w=copy.deepcopy(hydro);w['parameters'][j]=math.nextafter(spec[edge],direction);out.append({'id':f'hydro-domain-{sign}-{name}-outside-{edge}','request':w})
  w=copy.deepcopy(hydro);w['parameters'][list(m['parameters']).index('kappa_star')]=w['parameters'][list(m['parameters']).index('lambda_star')];out.append({'id':f'hydro-domain-{sign}-lambda-equals-kappa','request':w})
 return out

def response(r,w,mh,ok):
 rate.require(type(r)is dict and set(r)==FIELDS,'hydro exact response fields');rate.require(r['ok']is ok,'hydro strict status')
 rate.require(type(r['catalogue_hash'])is str and r['catalogue_hash']==mh,'hydro catalogue binding')
 for k in ('model','parameters','state','increment'):rate.require(rate.exact(r[k],w[k]),'hydro request echo:'+k)
 rate.require(rate.exact(r['columns'],COLUMNS),'hydro column order');rate.require(r['message']==(''if ok else FAILURE),'hydro diagnostic')
 if ok:
  rate.vector(r['values'],7);rate.require(type(r['jacobian'])is list and len(r['jacobian'])==7,'hydro Jacobian rows')
  for row in r['jacobian']:rate.vector(row,13)
 else:rate.require(r['values']is None and r['jacobian']is None,'hydro failure no usable output')
def numerical(r,ref,w):
 maximum=0.;max_void_ulps=0
 for i,(a,b)in enumerate(zip(r['values'],ref['values'])):
  if i==6:max_void_ulps=max(max_void_ulps,rate.ulp_distance(a,b));rate.require(max_void_ulps<=4,'hydro void primal ULPs')
  else:
   error=abs(a-b)/max(1.,abs(b));maximum=max(maximum,error);rate.require(error<=BUDGET,'hydro primal component')
 for i,(actual,wanted)in enumerate(zip(r['jacobian'],ref['jacobian'])):
  for a,b in zip(actual,wanted):
   if b==0:rate.require(a==0,'hydro structural derivative zero')
   elif i==6:max_void_ulps=max(max_void_ulps,rate.ulp_distance(a,b));rate.require(max_void_ulps<=4,'hydro void derivative ULPs')
   else:
    error=abs(a-b)/max(1.,abs(b));maximum=max(maximum,error);rate.require(error<=BUDGET,'hydro Jacobian component')
 # Algebraic Euler identity, checked independently from reference tables.
 for i,row in enumerate(r['jacobian']):
  euler=sum(row[7+k]*w['increment'][k]for k in range(6));rate.require(abs(euler-r['values'][i])<=BUDGET*max(1.,abs(r['values'][i])),'hydro Euler identity')
 return maximum,max_void_ulps

def metadata(backend,artifacts):
 m,mh=rate.catalogue();return {'version':VERSION,'backend':backend,'catalogue_hash':mh,'model_definition':m,'model_sha256':rate.sha(rate.MODEL),'parameter_order':list(m['parameters']),'columns':COLUMNS,'oracle_script_sha256':rate.sha(reference.__file__),'study_script_sha256':rate.sha(__file__),'rate_helper_sha256':rate.sha(rate.__file__),'common_helper_sha256':rate.sha(common.__file__),'budgets':{'component':BUDGET,'void_ULPs':4,'precision':PRECISION_BUDGET},'claims':CLAIMS,'execution_mode':'native-persistent-batch'if backend=='native'else'wasm-persistent-instance','collection_complete':False,'artifacts':artifacts,'records':[],'invalid_records':[]}
def collect(call,backend,artifacts,output=None):
 report=metadata(backend,artifacts);m=report['model_definition'];common.write_report(output,report)
 for c in cases():
  w=wire(c,m);row={'id':c['id'],'request':w,'response':call(w),'reference':None};report['records'].append(row);common.write_report(output,report);row['reference']=expected(c);common.write_report(output,report)
 control=report['records'][0]['request']
 for c in invalids(m):
  row=c|{'response':call(c['request']),'recovery':None};report['invalid_records'].append(row);common.write_report(output,report);row['recovery']=call(control);common.write_report(output,report)
 report['collection_complete']=True;common.write_report(output,report);return report

def assess(report,check_artifacts=True,*,native_report_path=None):
 rate.require(type(report)is dict and report.get('backend')in('native','wasm'),'hydro report protocol');meta=metadata(report['backend'],[])
 for k,v in meta.items():
  if k not in('collection_complete','artifacts','records','invalid_records'):rate.require(rate.exact(report.get(k),v),'hydro metadata binding:'+k)
 rate.require(report.get('collection_complete')is True,'hydro incomplete collection');artifacts=report.get('artifacts');rate.require(type(artifacts)is list and len(artifacts)==(1 if report['backend']=='native'else 2),'hydro artifact count')
 for a in artifacts:
  common.artifact(a)
  if check_artifacts:rate.require(rate.sha(a['path'])==a['sha256'],'hydro artifact bytes')
 m,mh=rate.catalogue();rows=report.get('records');rate.require(type(rows)is list and len(rows)==len(cases()),'hydro complete ordered corpus');maximum=0.;ulps=0
 for row,c in zip(rows,cases()):
  w=wire(c,m);rate.require(row.get('id')==c['id']and rate.exact(row.get('request'),w),'hydro record identity');response(row.get('response'),w,mh,True);ref=expected(c);rate.require(rate.exact(row.get('reference'),ref),'hydro independent reference altered');error,u=numerical(row['response'],ref,w);maximum=max(maximum,error);ulps=max(ulps,u)
 bad=report.get('invalid_records');items=invalids(m);rate.require(type(bad)is list and len(bad)==len(items),'hydro complete invalid corpus')
 for row,c in zip(bad,items):
  rate.require(row.get('id')==c['id']and rate.exact(row.get('request'),c['request']),'hydro invalid identity');response(row.get('response'),c['request'],mh,False);response(row.get('recovery'),rows[0]['request'],mh,True);rate.require(rate.exact(row['recovery'],rows[0]['response']),'hydro same-instance recovery')
 if report['backend']=='wasm':
  native=common.native_transcript(report,native_report_path);assess(native,check_artifacts);parity=0.
  for a,b in zip(rows,native['records']):
   rate.require(a['id']==b['id']and rate.exact(a['request'],b['request']),'hydro parity identity')
   av=a['response']['values']+[x for row in a['response']['jacobian']for x in row];bv=b['response']['values']+[x for row in b['response']['jacobian']for x in row]
   parity=max(parity,max(abs(x-y)/max(1.,abs(y))for x,y in zip(av,bv)))
  rate.require(parity<=BUDGET and rate.numeric(report.get('maximum_native_parity'))and math.isclose(parity,report['maximum_native_parity'],rel_tol=1e-12,abs_tol=1e-25),'hydro native/Wasm parity')
 return {'exact_hydro_cases':len(rows),'invalid_recovery_pairs':len(bad),'maximum_component_error':maximum,'maximum_void_ULPs':ulps,'exact_hydro_AD_validated':True,'near_hydro_AD':False,'zero_loading_AD':False,'artifacts_verified_now':check_artifacts}

def native_report(binary,output=None):
 binary=pathlib.Path(binary).resolve();before=rate.sha(binary);m,mh=rate.catalogue();plan=[wire(c,m)for c in cases()];control=plan[0]
 for c in invalids(m):plan.extend([c['request'],control])
 def command(w):return '\t'.join([w['model'],','.join(map(repr,w['parameters'])),','.join(map(repr,w['state'])),','.join(map(repr,w['increment']))])
 lines=['--describe']+[command(w)for w in plan];transport={'version':VERSION+'-transport','backend':'native','mode':'single-process-batch','artifact':{'path':str(binary),'sha256':before},'complete':False,'request_lines':lines};companion=pathlib.Path(str(output)+'.transport.json')if output is not None else None;common.write_report(companion,transport)
 try:
  r=subprocess.run([str(binary),'--stream'],input='\n'.join(lines)+'\n',capture_output=True,text=True,timeout=60);transport.update(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);common.write_report(companion,transport)
  rate.require(r.returncode==0,'hydro persistent native transport exit');raw=r.stdout.splitlines();rate.require(len(raw)==len(lines),'hydro native response count')
  parsed=[json.loads(x,parse_constant=lambda value:(_ for _ in()).throw(ValueError('nonfinite JSON')))for x in raw];d=parsed[0]
  rate.require(d.get('sha256')==mh and rate.exact(d.get('models'),[m])and list(d['models'][0]['parameters'])==list(m['parameters']),'hydro compiled catalogue/order')
  responses=iter(parsed[1:])
  def call(w):return next(responses)
  report=collect(call,'native',[{'path':str(binary),'sha256':before}],output);rate.require(next(responses,None)is None,'hydro unused batch response');rate.require(rate.sha(binary)==before,'hydro binary changed');transport['complete']=True;common.write_report(companion,transport);assess(report);return report
 except Exception as exc:
  if isinstance(exc,subprocess.TimeoutExpired):transport['stdout']=exc.stdout.decode(errors='replace')if isinstance(exc.stdout,bytes)else exc.stdout;transport['stderr']=exc.stderr.decode(errors='replace')if isinstance(exc.stderr,bytes)else exc.stderr
  transport['error']=type(exc).__name__+': '+str(exc);common.write_report(companion,transport);raise

def main():
 p=argparse.ArgumentParser();p.add_argument('--native',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);p.add_argument('--verify',type=pathlib.Path);p.add_argument('--native-report-path',type=pathlib.Path);p.add_argument('--verify-reference',action='store_true');a=p.parse_args()
 if a.verify_reference:print(verify_frozen());return
 if a.verify:print(json.dumps(assess(rate.read(a.verify),native_report_path=a.native_report_path),indent=2));return
 rate.require(a.native is not None and a.output is not None,'native and explicit output required');r=native_report(a.native,a.output);print(json.dumps(assess(r),indent=2))
if __name__=='__main__':main()
