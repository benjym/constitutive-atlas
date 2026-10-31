"""Independent input-binding audit; no material evaluator or solver execution."""
from pathlib import Path
import argparse,decimal,hashlib,json,math,struct
R=Path(__file__).resolve().parents[3] if 'docs' in Path(__file__).parts else Path('/Users/bmar5496/code/constitutive-atlas')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=R);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=a.root
 source=r/'docs/benchmarks/kfs-published-case-selection-v1'; study=r/'docs/benchmarks/kfs-tmd2-research-range-v1'; portable=r/'docs/benchmarks/kfs-tmd2-portable-v1'
 inputs=[];checks=[]
 def load(p):inputs.append({'path':str(p.relative_to(r)),'sha256':sha(p)});return read(p)
 def check(name,condition):checks.append({'id':name,'passed':bool(condition)})
 model=load(r/'models/hypoplastic-sand-igs97.json');case=load(source/'case.json');params=load(source/'parameter-set.json');protocol=load(study/'inputs/protocol.json');metadata=load(study/'generated-models.json')
 check('current-case-definition-identity',case['definition_sha256']==sha(r/'models/hypoplastic-sand-igs97.json'))
 check('compiled-study-full-model-identity',next(m for m in metadata['models']if m['id']==model['id'])==model)
 # Literal primary-table transcription, not defaults. Table source identity and printing are independently reviewed in worker packet.
 primary={'phi':math.radians(33.1),'hs':4000*10**6,'n':.27,'ed0':.677,'ec0':1.054,'ei0':1.212,'alpha':.14,'beta':2.5,'R':1e-4,'mR':2.2,'mT':1.1,'beta_r':.1,'chi':5.5}
 check('thirteen-primary-material-constants',params['material_parameter_count']==13 and params['parameters']==dict(p_ref=100000.,**primary))
 check('project-scale-separated',params['numerical_scale_parameters']==['p_ref'])
 check('named-parameter-order-identity',list(model['parameters'])==list(params['parameters']))
 check('parameter-bounds',all(p['min']<=params['parameters'][name]<=p['max'] for name,p in model['parameters'].items()))
 h=[]
 for precision in (80,120):
  with decimal.localcontext() as context:
   context.prec=precision;h.append(float(decimal.Decimal('0.0001')/decimal.Decimal(3).sqrt()))
 check('mobilized-history-independent-rounding',h[0]==h[1] and h[0].hex()==case['initial']['history_binary64'])
 initial=[100000.,100000.,100000.,0.,0.,0.,.975,h[0],h[0],h[0],0.,0.,0.]
 check('nominal-initial-state',case['initial']['flat_state']==initial)
 check('source-to-mandel-state-order',[v['name']for v in model['state']]==['sigma','e','h'] and [v['shape']for v in model['state']]==['sym','scalar','sym'])
 check('named-and-positional-state-binding',sum([case['initial']['named_state']['sigma'],[case['initial']['named_state']['e']],case['initial']['named_state']['h']],[])==initial)
 check('measured-initial-not-substituted',case['initial']['measured_initial_state_separate']['void_ratio']!=initial[6])
 check('example-default-not-substituted',next(v for v in model['state']if v['name']=='e')['initial']!=initial[6] and next(v for v in model['state']if v['name']=='h')['initial']!=initial[7:])
 sets=[]
 for label,directory in [('source-study',study),('portable-study',portable)]:
  request_path=directory/'inputs/requests.json' if (directory/'inputs/requests.json').exists() else study/'inputs/requests.json'
  protocol_path=directory/'inputs/protocol.json' if (directory/'inputs/protocol.json').exists() else study/'inputs/protocol.json'
  requests=load(request_path);settings=case['prospective_numerics']['settings'];freeze=load(directory/'inputs/freeze.json')
  check(label+'-frozen-request-bytes',sha(request_path)==freeze['files']['requests.json'])
  check(label+'-frozen-protocol-bytes',sha(protocol_path)==freeze['files']['protocol.json'])
  check(label+'-three-declared-resolutions',[q['steps']for q in requests]==[400,800,1600])
  check(label+'-full-parameter-initial-binding',all(q['model']==model['id'] and q['parameters']==list(params['parameters'].values()) and q['initial']==initial for q in requests))
  check(label+'-protocol-and-settings',all(q['protocol']==1 and q['target']==.25 and q['cycles']==0 and q['integration_settings']==settings for q in requests))
  check(label+'-full-control-history',all(len(q['controls_bits'])==q['steps']+1 and q['controls_bits']==[struct.pack('>d',q['target']*i/q['steps']).hex()for i in range(q['steps']+1)]for q in requests))
  sets.append(requests)
 check('portable-requests-exactly-unchanged',sets[0]==sets[1])
 check('no-fit-qualified-source-policy',protocol['no_fit'] is True and 'operational' in protocol['coordinate_policy']['source_limit'] and 'historical' in protocol['coordinate_policy']['source_limit'])
 # Descriptive saved-endpoint audit, not an integration-stage or acceptance check.
 endpoints=[]
 for request in sets[0]:
  response=load(study/'observations'/request['id']/'stdout.json')
  ratios=[math.sqrt(math.fsum(v*v for v in row['state'][7:13]))/params['parameters']['R']for row in response['points']]
  endpoints.append({'id':request['id'],'stored_point_count':len(ratios),'history_norm_over_R_min':min(ratios),'history_norm_over_R_max':max(ratios),'stored_norms_over_one':sum(v>1 for v in ratios),'scope':'Descriptive binary64 Euclidean norm of stored accepted points only; no internal-stage access, exact-inequality proof or new acceptance gate.'})
 a.output.write_text(json.dumps({'kind':'kfs-tmd2-input-binding-audit-v1','inputs':inputs,'checks':checks,'saved_endpoint_history':endpoints,'passed':all(c['passed']for c in checks),'scope':'Receipt/input identity only; literal primary table values require visual source audit. No material calls, source scientific signoff, historical-coordinate resolution or new acceptance policy.'},indent=2)+'\n')
 print(f"{sum(c['passed']for c in checks)}/{len(checks)} binding checks pass")
 if not all(c['passed']for c in checks):raise SystemExit(1)
if __name__=='__main__':main()
