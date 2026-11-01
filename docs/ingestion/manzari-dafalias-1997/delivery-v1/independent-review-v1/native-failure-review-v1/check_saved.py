from pathlib import Path
import json,gzip,hashlib,math,collections
D=Path(__file__).resolve().parent;P=D.parents[1];Q=Path('/private/tmp/atlas-md1997-delivery-v1/qualification-native-v3');O=Path('/private/tmp/atlas-md1997-delivery-v1/ordinary-native-v5');B=P/'build-native-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((B/'receipt.json').read_text());report=json.loads((Q/'report.json').read_text());checks=json.loads((Q/'checks.json').read_text());ordinary=json.loads((O/'report.json').read_text())
for n,h in receipt['files'].items():assert sha(B/n)==h
assert sha(Path(receipt['executable']))==receipt['executable_sha256']==report['identity']['artifact_sha256']
gen=Path(receipt['executable']).parent/'generated';assert sha(gen/'models.json')==receipt['generated_models_sha256'];assert sha(gen/'models.hpp')==receipt['generated_header_sha256']
assert json.loads((B/'describe.json').read_text())==json.loads((gen/'models.json').read_text())
assert checks['reports'][0]['sha256']==sha(Q/'report.json')
caseinfo=[];calls=0;rollback=True;no_errors=True
for name,c in report['cases'].items():
 records=[json.loads(x) for x in gzip.open(Q/(name+'.jsonl.gz'),'rt')];calls+=len(records)
 for r in records:
  assert json.loads(r['raw_stdout'])==r['response'];assert r['request']['model']=='manzari-dafalias-1997-constant-m-be-v1'
  no_errors=no_errors and 'harness_error' not in r['response']
  if r['request']['mode']=='integrate' and not r['response']['ok']:
   rollback=rollback and r['response']['state']==r['request']['initial'] and r['response']['diagnostics']['partition_committed'] is False
 ans=c.get('failed_response',c.get('response_metadata',{}))
 caseinfo.append({'case':name,'ok':c['ok'],'returned_points':len(c['points']),'last_coordinate':c['points'][-1]['coordinate'] if c['points'] else None,'failed_index':c.get('failed_index'),'message':ans.get('message')})
special=[json.loads(x) for x in gzip.open(Q/'special.jsonl.gz','rt')];calls+=len(special)
assert calls==report['call_count']==46
assert len(report['cases'])==35 and sum(x['ok'] for x in report['cases'].values())==3
assert checks['checks']==1881 and checks['failures']==334 and not checks['passed']
assert rollback and no_errors
assert len(ordinary['cases'])==16 and not ordinary['passed']
assert [c['model'] for c in ordinary['cases'] if not c['passed']]==['manzari-dafalias-1997-constant-m-be-v1']
# Source-derived elastic predictor algebra for first saved fixed-coaxial request.
r=json.loads(next(iter(gzip.open(Q/'dense-cos3theta-+0-128.jsonl.gz','rt'))));z=r['request']['initial'];de=r['request']['strain'];params=r['request']['parameters']
p=math.fsum(z[:3])/3;G=params[2]*(p/params[0])**params[4];dt=math.sqrt(math.fsum(x*x for x in de));pred=z.copy()
for i in range(6):pred[i]+=2*G*de[i]
press=math.fsum(pred[:3])/3;f=math.sqrt(math.fsum((pred[i]-(press if i<3 else 0)-press*pred[7+i])**2 for i in range(6)))-math.sqrt(2/3)*params[14]*press
assert f/params[1]>1e-8
predictor={'p_Pa':p,'G_Pa':G,'strain_norm':dt,'elastic_predictor_yield_excess_Pa':f,'yield_scaled':f/params[1],'physical_constraint_upper':1e-8,'ideal_depth14_excess_scaled':2*G*dt/(2**14*params[1]),'candidate_equations_or_gates_changed':False}
result={'reviewer':'/root/md1997_review','compiled_execution_by_reviewer':False,'build_identity_verified':True,'ordinary_expected_cases_passed':15,'case_summary':caseinfo,'raw_calls':calls,'direct_backend_responses_no_harness_error':no_errors,'failed_direct_integrations_return_parent':rollback,'checker':{'checks':checks['checks'],'failures':checks['failures'],'failed_channel_prefixes':dict(collections.Counter(x['channel'].split('-')[0] for x in checks['results'] if not x['passed']))},'source_elastic_predictor_example':predictor,'AD_status':report['special']['linearize']}
(D/'saved-evidence-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'saved_identity_and_raw_bindings':'PASS','native_qualification':'FAIL','cases':35,'operational_successes':3,'raw_calls':46,'checks':1881,'failed_checks':334,'source_predictor':predictor},indent=2))
