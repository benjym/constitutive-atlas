"""Independent componentwise checked-log1p replay; no model admission."""
import argparse,hashlib,json,math,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.reference_log1p import oracle,corpus
VERSION='checked-scalar-log1p-study-v1'
OPERATOR_VERSION='scalar-log1p-libm-checked-v1'
REFERENCE=ROOT/'catalogue/investigations/scalar-log1p-reference-v1/log1p.json'
ULP_BUDGET=4
CONTEXTS=frozenset('''derived_eager_masked_failure derived_check_only_failure derived_valid domain_masked_failure initial_active_failure initial_inactive_skipped lazy_bad_arm_skipped lazy_bad_arm_selected_failure timed_check_only timed_equation_failure observable_only_skips_bad_equation observable_failure observable_inactive reset_guard_failure reset_value_inactive reset_value_failure reset_rollback alias_success alias_failure_preserves last_derivative_nonfinite_rejected derivative_overflow_rejected large_seed_division_stays_finite sticky_failure history_values_and_counters history_lazy history_failure_rollback history_recovery'''.split())
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def number(x):require(type(x) in (int,float) and math.isfinite(x),'finite real scalar required');return float(x)
def vector(a,n):require(type(a) is list and len(a)==n,'vector shape');return [number(x) for x in a]
def distance(a,b):
 a=number(a);b=number(b)
 if a==b:return 0
 def key(x):
  bits=struct.unpack('>Q',struct.pack('>d',x))[0]
  return (~bits & ((1<<64)-1)) if bits>>63 else bits|(1<<63)
 return abs(key(a)-key(b))
def check(actual,expected):
 actual=number(actual);expected=number(expected)
 require((actual==0)==(expected==0),'zero/nonzero channel identity')
 d=distance(actual,expected);require(d<=ULP_BUDGET,'four ULP channel budget');return d
def catalogue():
 from atlas.model import load
 models=[load(p) for p in sorted((ROOT/'tests/fixtures/log1p').glob('*.json'))]
 require(len(models)==9,'nine isolated fixtures');return models,hashlib.sha256(json.dumps(models,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def reference():
 ref=read(REFERENCE);require(ref==corpus(),'exact independent reference binding');return ref
def request(c):return {'text':repr(c['x']),'input':c['x'],'input_hex':c['x_hex']}
def invalid_requests():
 return [{'id':name,'text':text,'parseable':parseable,**({'input':x} if parseable else {})} for name,text,parseable,x in [('minus-one','-1.0',True,-1.),('below-minus-one',repr(math.nextafter(-1.,-math.inf)),True,math.nextafter(-1.,-math.inf)),('minus-two','-2',True,-2.),('nan','nan',False,None),('inf','inf',False,None),('minus-inf','-inf',False,None),('empty','',False,None),('text','true',False,None),('trailing','0junk',False,None),('comma','0,1',False,None)]]
def response(r,x,h,success=True):
 require(type(r) is dict,'response object')
 require(r.get('operator_version')==OPERATOR_VERSION and r.get('catalogue_hash')==h,'runtime identity')
 number(r.get('input'));require(r['input']==x,'input echo')
 for k in ('ok','primitive_ok','schema_ok'):require(r.get(k) is success,'response status '+k)
 require(type(r.get('contexts')) is dict and set(r['contexts'])==CONTEXTS and all(v is True for v in r['contexts'].values()),'exact contexts')
 require(type(r.get('negative_zero')) is bool,'negative zero flag type')
 if not success:
  require(all(r.get(k,1) is None for k in ('value','derivatives','schema_values','schema_derivatives')) and r['negative_zero'] is False,'failure channels');return
 number(r.get('value'));vector(r.get('derivatives'),38);vector(r.get('schema_values'),6)
 require(type(r.get('schema_derivatives')) is list and len(r['schema_derivatives'])==6,'schema derivative rows')
 for row in r['schema_derivatives']:vector(row,38)
def compare(r,x):
 v,d=map(float,oracle(float(x),650));require(r['negative_zero'] is (x==0 and math.copysign(1.,x)<0),'signed-zero flag')
 maxima={'value':check(r['value'],v),'derivative':max(check(a,d) for a in r['derivatives']),'schema_value':0,'schema_derivative':0}
 for i in range(6):
  maxima['schema_value']=max(maxima['schema_value'],check(r['schema_values'][i],1.+v if i<3 else 0.))
  maxima['schema_derivative']=max(maxima['schema_derivative'],max(check(a,d if i<3 else 0.) for a in r['schema_derivatives'][i]))
 return maxima
def assess(report):
 require(type(report) is dict and report.get('version')==VERSION and report.get('backend') in ('native','wasm'),'protocol')
 require(report.get('operator_version')==OPERATOR_VERSION and type(report.get('ulp_budget')) is int and report['ulp_budget']==4,'operator/budget')
 ref=reference();_,h=catalogue();require(report.get('catalogue_hash')==h and report.get('reference_sha256')==sha(REFERENCE),'bindings')
 rows=report.get('records');require(type(rows) is list and len(rows)==38,'complete38cases')
 maximum=dict.fromkeys(('value','derivative','schema_value','schema_derivative'),0)
 for row,c in zip(rows,ref['cases']):
  require(type(row) is dict and row.get('id')==c['id'],'ordered case identity')
  q=row.get('request');require(type(q) is dict,'request object');number(q.get('input'));require(q==request(c),'request binding');response(row.get('response'),c['x'],h)
  for k,v in compare(row['response'],c['x']).items():maximum[k]=max(maximum[k],v)
 invalid=report.get('invalid_records');requests=invalid_requests();require(type(invalid) is list and len(invalid)==len(requests),'complete invalid cases')
 for row,q in zip(invalid,requests):
  a=row.get('request');require(type(a) is dict and type(a.get('parseable')) is bool,'invalid request typing')
  if q['parseable']:number(a.get('input'))
  require(a==q,'invalid request identity');r=row.get('response')
  if q['parseable']:response(r,q['input'],h,False)
  else:require(type(r) is dict and set(r)=={'ok','error'} and r['ok'] is False and r['error']=='invalid input','parser rejection')
  if report['backend']=='wasm':
   recovery=row.get('recovery');response(recovery,ref['cases'][0]['x'],h);compare(recovery,ref['cases'][0]['x']);require(recovery==rows[0]['response'],'persistent recovery')
 return {'cases':38,'contexts_per_call':27,'invalid_cases':len(requests),'maximum_ulp_errors':maximum,'fresh_decimal_precision':650}
def native(binary):
 models,h=catalogue();desc=json.loads(subprocess.check_output([str(binary),'--describe'],text=True,timeout=30));require(desc['models']==models and desc['sha256']==h,'native descriptor')
 def call(text):
  r=subprocess.run([str(binary),text],capture_output=True,text=True,timeout=30);out=json.loads(r.stdout);require(r.returncode==(0 if out.get('ok') is True else 1),'exit status');return out
 records=[{'id':c['id'],'request':request(c),'response':call(request(c)['text'])} for c in reference()['cases']]
 return {'version':VERSION,'backend':'native','operator_version':OPERATOR_VERSION,'ulp_budget':4,'catalogue_hash':h,'reference_sha256':sha(REFERENCE),'binary_sha256':sha(binary),'records':records,'invalid_records':[{'request':q,'response':call(q['text'])} for q in invalid_requests()]}
def verify_parity(wasm,native_report,native_path):
 assess(wasm);assess(native_report)
 require(wasm['backend']=='wasm' and native_report['backend']=='native','parity backends')
 require(wasm.get('native_report_sha256')==sha(native_path),'native report binding')
 maximum=0
 for a,b in zip(wasm['records'],native_report['records']):
  require(a['id']==b['id'] and a['request']==b['request'],'parity requests')
  for key in ('value','derivatives','schema_values','schema_derivatives'):
   def flat(x):
    if type(x) is list:return [v for item in x for v in flat(item)]
    return [x]
   for x,y in zip(flat(a['response'][key]),flat(b['response'][key])):maximum=max(maximum,check(x,y))
 return maximum
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--binary',type=Path);ap.add_argument('--report',type=Path);ap.add_argument('--native-report',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();require(bool(a.binary)!=bool(a.report),'one binary or report required')
 r=native(a.binary) if a.binary else read(a.report)
 # Persist raw evidence before assessment; failures leave inspectable inputs/outputs.
 a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');r['assessment']=assess(r)
 if a.native_report:r['assessment']['maximum_native_parity_ulps']=verify_parity(r,read(a.native_report),a.native_report)
 a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps(r['assessment']))
if __name__=='__main__':main()
