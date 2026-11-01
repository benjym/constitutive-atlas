"""Independent regular-direction material AD study; no integration/branch-limit claim."""
import argparse,copy,json,math,pathlib,re,subprocess
from tools import barodesy2017_rate_study as rate
from tools import reference_barodesy2017 as oracle
VERSION='barodesy2017-material-ad-study-v1'
COLUMNS=['sigma_xx','sigma_yy','sigma_zz','sigma_xy_mandel','sigma_yz_mandel','sigma_xz_mandel','e','de_xx','de_yy','de_zz','de_xy_mandel','de_yz_mandel','de_xz_mandel']
STEPS=[8e-5,4e-5,2e-5,1e-5]
FD_BUDGET=2e-8
REFINEMENT_BUDGET=2e-8
IDENTITY_BUDGET=2e-10
FIELDS=rate.FIELDS|{'jacobian','columns'}
def selected():return [c for c in rate.reference()['cases']if c['oracle']['branch']=='regular'and 'nearhydro'not in c['id']]
def scales(w):return [max(1.,math.hypot(*w['state'][:6]))]*6+[max(1.,abs(w['state'][6]))]+[math.hypot(*w['increment'])]*6
def independent(w,model):
 p=dict(zip(model['parameters'],w['parameters']));p.pop('sigma_star')
 out=oracle.rate({'sigma':w['state'][:6],'e':w['state'][6]},w['increment'],p,precision=100)
 rate.require(out['branch']=='regular','finite differences left regular source branch')
 return out['sigma_rhs']+[out['e_rhs']]
def difference_reference(w,model):
 s=scales(w);levels=[]
 for h in STEPS:
  columns=[]
  for j in range(13):
   a,b=copy.deepcopy(w),copy.deepcopy(w);key='state'if j<7 else'increment';k=j if j<7 else j-7
   a[key][k]+=h*s[j];b[key][k]-=h*s[j]
   x,y=independent(a,model),independent(b,model);columns.append([(u-v)/(2*h)for u,v in zip(x,y)])
  levels.append(columns)
 f=independent(w,model);den=max(1.,math.hypot(*f))
 refinement=[max(math.hypot(*(x-y for x,y in zip(a,b)))/max(den,math.hypot(*b))for a,b in zip(levels[i-1],levels[i]))for i in range(1,len(levels))]
 rate.require(refinement[-1]<=REFINEMENT_BUDGET,'independent FD refinement unresolved')
 return {'steps':STEPS,'scaled_columns_by_step':levels,'successive_normalized_differences':refinement,'state_loading_scales':s,'primal':f}
def verify_frozen_reference(path=None):
 path=pathlib.Path(path)if path is not None else pathlib.Path(__file__).resolve().parents[1]/'catalogue/investigations/barodesy2017-material-ad-v1/fd-reference.json'
 m,_=rate.catalogue();rows=[]
 for c in selected():
  w=rate.wire(c,m);rows.append({'id':c['id'],'request':w,'reference':difference_reference(w,m)})
 expected={'version':'barodesy2017-independent-material-fd-reference-v1','scope':'Independent central differences only; no native or Wasm AD execution or validation','columns':COLUMNS,'steps':STEPS,'precision':100,'source_reference_sha256':rate.sha(rate.REFERENCE),'oracle_script_sha256':rate.sha(rate.ROOT/'tools/reference_barodesy2017.py'),'records':rows,'summary':{'regular_cases':len(rows),'maximum_final_refinement_difference':max(c['reference']['successive_normalized_differences'][-1]for c in rows),'zero_hydro_derivatives':False}}
 rate.require(rate.exact(rate.read(path),expected),'frozen FD reference mismatch');return expected['summary']
def commutator(v):
 a=oracle.cart(v);w=[[0.,-.7,.2],[.7,0.,-.4],[-.2,.4,0.]]
 return oracle.mandel([[sum(w[i][k]*a[k][j]-a[i][k]*w[k][j]for k in range(3))for j in range(3)]for i in range(3)])
def product(j,v):return [sum(a*b for a,b in zip(row,v))for row in j]
def error(a,b,scale=1.):return math.hypot(*(x-y for x,y in zip(a,b)))/max(scale,math.hypot(*b))
def validate_response(r,w,mh,success):
 rate.require(type(r)is dict and set(r)==FIELDS,'AD exact response fields')
 rate.validate_response({k:v for k,v in r.items()if k not in('jacobian','columns')},w,mh,success)
 # The base rate protocol has a distinct failure diagnostic.
 rate.require(rate.exact(r['columns'],COLUMNS),'AD column order')
 if success:
  rate.require(type(r['jacobian'])is list and len(r['jacobian'])==7,'Jacobian rows')
  for row in r['jacobian']:rate.vector(row,13)
 else:rate.require(r['jacobian']is None,'failed Jacobian unavailable')
def checked_response(r,w,mh,success):
 # Reuse strict rate envelope validator without weakening AD-specific message binding.
 rate.require(type(r)is dict and set(r)==FIELDS,'AD exact response fields')
 rate.require(r['message']==(''if success else'unsupported regular material AD request'),'AD diagnostic')
 adapted=copy.deepcopy(r);adapted['message']=''if success else'unsupported research rate request'
 validate_response(adapted,w,mh,success)
def assess_case(response,w,mh,fd):
 checked_response(response,w,mh,True);j=response['jacobian'];f=response['values'];den=max(1.,math.hypot(*fd['primal']))
 rate.require(error(f,fd['primal'],den)<=rate.BUDGET,'AD primal mismatch')
 s=fd['state_loading_scales'];candidate=[[j[i][k]*s[k]for i in range(7)]for k in range(13)]
 errors=[max(error(a,b,den)for a,b in zip(candidate,cols))for cols in fd['scaled_columns_by_step']]
 rate.require(errors[-1]<=FD_BUDGET,'material Jacobian/independent FD mismatch')
 hom=error(product(j,[0.]*7+w['increment']),f,den);rate.require(hom<=IDENTITY_BUDGET,'loading Euler homogeneity')
 rotation=product(j,commutator(w['state'][:6])+[0.]+commutator(w['increment']))
 rot=error(rotation,commutator(f[:6])+[0.],den);rate.require(rot<=IDENTITY_BUDGET,'infinitesimal rotation identity')
 expected=[0.]*6+[-sum(w['increment'][:3])]+[-(1+w['state'][6])]*3+[0.]*3
 for actual,wanted in zip(j[6],expected):
  if wanted==0:rate.require(actual==0,'analytic void-rate derivative exact zero')
  else:rate.require(rate.ulp_distance(actual,wanted)<=4,'analytic void-rate derivative four ULP')
 # Independent scalar body-law identities, not FD fit identities.
 model,_=rate.catalogue();params=dict(zip(model['parameters'],w['parameters']));params.pop('sigma_star')
 source=oracle.rate({'sigma':w['state'][:6],'e':w['state'][6]},w['increment'],params,precision=100)
 rate.channel_checks(f,source['sigma_rhs']+[source['e_rhs']],w,source['derived'])
 d=source['derived'];r=math.hypot(*w['increment']);void_plus_one=1+w['state'][6]
 e_column_expected=[d['c3']*r*d['c5']*d['density']**d['c5']*v/void_plus_one for v in w['state'][:6]]
 e_column_actual=[j[i][6]for i in range(6)]
 density_error=error(e_column_actual,e_column_expected,den)
 rate.require(density_error<=IDENTITY_BUDGET,'source density void-column identity')
 sigma_direction=w['state'][:6]+[0.]*7
 stress_scaling_actual=product(j,sigma_direction)
 stress_scaling_expected=[f[i]+params['lambda_star']*void_plus_one*j[i][6]for i in range(6)]+[0.]
 stress_scaling_error=error(stress_scaling_actual,stress_scaling_expected,den)
 rate.require(stress_scaling_error<=IDENTITY_BUDGET,'source pressure-density scaling identity')
 return {'normalized_derivative_errors_by_step':errors,'independent_refinement':fd['successive_normalized_differences'],'homogeneity_error':hom,'rotation_error':rot,'density_void_column_error':density_error,'pressure_density_scaling_error':stress_scaling_error}

def invalids(model):
 ref=rate.reference();out=rate.invalid_requests(model,ref)
 for name,de in [('excluded-zero',[0.]*6),('excluded-hydro',[1.,1.,1.,0.,0.,0.]),('excluded-hydro-point-one',[.1,.1,.1,0.,0.,0.]),('excluded-hydro-negative-point-one',[-.1,-.1,-.1,0.,0.,0.])]:
  w=rate.wire(selected()[0],model);w['increment']=de;out.append({'id':name,'request':w})
 return out
def write_report(path,report):
 if path is not None:pathlib.Path(path).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
def artifact(a):
 rate.require(type(a)is dict and set(a)=={'path','sha256'},'artifact shape')
 rate.require(type(a['path'])is str and bool(a['path'])and '\x00'not in a['path'],'artifact path shape')
 rate.require(type(a['sha256'])is str and re.fullmatch('[0-9a-f]{64}',a['sha256'])is not None,'artifact hash shape')
def native_transcript(report,override=None):
 artifact({'path':report.get('native_report_path'),'sha256':report.get('native_report_sha256')})
 resolved=override if override is not None else report['native_report_path']
 rate.require(isinstance(resolved,(str,pathlib.Path))and bool(str(resolved))and '\x00'not in str(resolved),'native report override path')
 native=rate.read(resolved);rate.require(native.get('backend')=='native'and rate.sha(resolved)==report['native_report_sha256'],'AD native transcript binding');return native
def native_exit(returncode,parsed,description=False):
 if description:rate.require(returncode==0,'AD description exit status')
 else:rate.require(type(parsed)is dict and type(parsed.get('ok'))is bool and returncode==(0 if parsed['ok']else 1),'AD native exit/status mismatch')
def collect(call,backend,artifacts,output=None):
 m,mh=rate.catalogue();rows=[];bad=[]
 report={'version':VERSION,'backend':backend,'catalogue_hash':mh,'model_definition':m,'model_sha256':rate.sha(rate.MODEL),'reference_sha256':rate.sha(rate.REFERENCE),'oracle_script_sha256':rate.sha(rate.ROOT/'tools/reference_barodesy2017.py'),'study_script_sha256':rate.sha(__file__),'parameter_order':list(m['parameters']),'columns':COLUMNS,'steps':STEPS,'budgets':{'FD':FD_BUDGET,'refinement':REFINEMENT_BUDGET,'identity':IDENTITY_BUDGET,'primal':rate.BUDGET},'claims':{'regular_instantaneous_material_AD':False,'zero_hydro_derivatives':False,'integrated':False,'admitted':False},'collection_complete':False,'artifacts':artifacts,'records':rows,'invalid_records':bad}
 write_report(output,report)
 for c in selected():
  w=rate.wire(c,m);row=dict(id=c['id'],request=w,response=call(w),reference=None,metrics=None);rows.append(row);write_report(output,report)
  row['reference']=difference_reference(w,m);write_report(output,report)
 control=rows[0]['request']
 for c in invalids(m):
  row=c|{'response':call(c['request']),'recovery':None};bad.append(row);write_report(output,report)
  row['recovery']=call(control);write_report(output,report)
 report['collection_complete']=True;write_report(output,report)
 return report
def assess(report,check_artifacts=True,*,native_report_path=None):
 m,mh=rate.catalogue();rate.require(report.get('version')==VERSION and report.get('backend')in('native','wasm'),'AD protocol')
 for key,expected in [('catalogue_hash',mh),('model_definition',m),('model_sha256',rate.sha(rate.MODEL)),('reference_sha256',rate.sha(rate.REFERENCE)),('oracle_script_sha256',rate.sha(rate.ROOT/'tools/reference_barodesy2017.py')),('study_script_sha256',rate.sha(__file__)),('parameter_order',list(m['parameters'])),('columns',COLUMNS),('steps',STEPS),('budgets',{'FD':FD_BUDGET,'refinement':REFINEMENT_BUDGET,'identity':IDENTITY_BUDGET,'primal':rate.BUDGET}),('claims',{'regular_instantaneous_material_AD':False,'zero_hydro_derivatives':False,'integrated':False,'admitted':False})]:rate.require(rate.exact(report.get(key),expected),'AD binding:'+key)
 rate.require(report.get('collection_complete')is True,'AD collection incomplete')
 artifacts=report.get('artifacts');rate.require(type(artifacts)is list and len(artifacts)==(1 if report['backend']=='native'else 2),'AD artifacts')
 for a in artifacts:
  artifact(a)
  if check_artifacts:rate.require(rate.sha(a['path'])==a['sha256'],'AD artifact bytes changed')
 rows=report.get('records');rate.require(type(rows)is list and len(rows)==len(selected()),'AD complete corpus');maximum=0.
 for row,c in zip(rows,selected()):
  w=rate.wire(c,m);rate.require(row.get('id')==c['id']and rate.exact(row.get('request'),w),'AD request binding')
  # Recompute independent differences, not trusting retained derivative/reference/metric claims.
  fd=difference_reference(w,m);rate.require(rate.exact(row.get('reference'),fd),'independent reference altered')
  metrics=assess_case(row['response'],w,mh,fd);rate.require(row.get('metrics')is None,'collected row metrics must be null');maximum=max(maximum,metrics['normalized_derivative_errors_by_step'][-1])
 bad=report.get('invalid_records');rate.require(type(bad)is list and len(bad)==len(invalids(m)),'AD invalid corpus')
 for row,c in zip(bad,invalids(m)):
  rate.require(row.get('id')==c['id']and rate.exact(row.get('request'),c['request']),'AD invalid identity');checked_response(row.get('response'),c['request'],mh,False);checked_response(row.get('recovery'),rows[0]['request'],mh,True);rate.require(rate.exact(row['recovery'],rows[0]['response']),'AD recovery mismatch')
 if report['backend']=='wasm':
  native=native_transcript(report,native_report_path);assess(native,check_artifacts)
  parity=0.
  for a,b in zip(rows,native['records']):
   rate.require(a['id']==b['id']and rate.exact(a['request'],b['request']),'AD parity requests');scale=max(1.,math.hypot(*b['response']['values']))
   rate.require(error(a['response']['values'],b['response']['values'],scale)<=rate.BUDGET,'AD primal native/Wasm parity')
   for k,s in enumerate(a['reference']['state_loading_scales']):
    av=[row[k]*s for row in a['response']['jacobian']];bv=[row[k]*s for row in b['response']['jacobian']];parity=max(parity,error(av,bv,scale))
  rate.require(parity<=2e-12 and rate.numeric(report.get('maximum_scaled_jacobian_native_parity'))and math.isclose(parity,report['maximum_scaled_jacobian_native_parity'],rel_tol=1e-12,abs_tol=1e-20),'AD native/Wasm parity metric')
 return {'regular_cases':len(rows),'invalid_recovery_pairs':len(bad),'maximum_final_FD_error':maximum,'zero_hydro_derivatives':False,'regular_instantaneous_material_AD_validated':True,'artifacts_verified_now':check_artifacts}
def native_report(binary,output=None):
 binary=pathlib.Path(binary).resolve();before=rate.sha(binary);m,mh=rate.catalogue()
 transport={'version':'barodesy2017-material-ad-transport-v1','backend':'native','artifact':{'path':str(binary),'sha256':before},'complete':False,'calls':[]}
 companion=pathlib.Path(str(output)+'.transport.json')if output is not None else None;write_report(companion,transport)
 def invoke(args,description=False):
  record={'arguments':args};transport['calls'].append(record)
  try:
   r=subprocess.run([str(binary),*args],capture_output=True,text=True,timeout=30);record.update(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);write_report(companion,transport)
   parsed=json.loads(r.stdout,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite JSON')))
   native_exit(r.returncode,parsed,description)
   return parsed
  except Exception as exc:
   if isinstance(exc,subprocess.TimeoutExpired):
    record['stdout']=exc.stdout.decode(errors='replace')if isinstance(exc.stdout,bytes)else exc.stdout
    record['stderr']=exc.stderr.decode(errors='replace')if isinstance(exc.stderr,bytes)else exc.stderr
   record['error']=type(exc).__name__+': '+str(exc);write_report(companion,transport);raise
 try:
  d=invoke(['--describe'],True);rate.require(d.get('sha256')==mh and rate.exact(d.get('models'),[m])and list(d['models'][0]['parameters'])==list(m['parameters']),'AD compiled catalogue/order')
  def call(w):return invoke([w['model'],','.join(map(repr,w['parameters'])),','.join(map(repr,w['state'])),','.join(map(repr,w['increment']))])
  report=collect(call,'native',[{'path':str(binary),'sha256':before}],output);rate.require(rate.sha(binary)==before,'AD binary changed');transport['complete']=True;write_report(companion,transport)
  assess(report);return report
 except Exception as exc:
  transport['error']=type(exc).__name__+': '+str(exc);write_report(companion,transport);raise

def main():
 p=argparse.ArgumentParser();p.add_argument('--native',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);p.add_argument('--verify',type=pathlib.Path);p.add_argument('--native-report-path',type=pathlib.Path);a=p.parse_args()
 if a.verify:print(json.dumps(assess(rate.read(a.verify),native_report_path=a.native_report_path),indent=2));return
 rate.require(a.native is not None and a.output is not None,'native and explicit output required');r=native_report(a.native,a.output);print(json.dumps(assess(r),indent=2))
if __name__=='__main__':main()
