"""Disabled generic control must preserve retained v2 request results."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OLD=HERE.parent/'delivery-v1/supplied-original-v2/candidate-v2'
EXE=ROOT/'.local/lade-derivative-tail-v1/native-build/atlas_lade_domain_candidate'
RAW=ROOT/'.local/lade-derivative-tail-v1/native-legacy-requests';RAW.mkdir(exist_ok=True)
requests=[];checks=[]
def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
for kind,file in [('triaxial','native-triaxial-results.json'),('lifecycle','native-lifecycle-results.json')]:
    for i,row in enumerate(json.loads((OLD/file).read_text())['requests']):
        expected=row.get('response') or json.loads((ROOT/row['raw_path']).read_text());cmd=row['command'].copy();cmd[0]=str(EXE)
        proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120);r=json.loads(proc.stdout);raw=RAW/f'{kind}-{i}.json';raw.write_text(proc.stdout)
        a=[p['state'] for p in expected['points']] if 'points' in expected else expected.get('state');b=[p['state'] for p in r['points']] if 'points' in r else r.get('state')
        ok=r.get('ok')==expected.get('ok') and a==b;check(f'{kind}_{i}',ok)
        requests.append({'command':cmd,'returncode':proc.returncode,'raw_path':str(raw.relative_to(ROOT)),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'ok':r.get('ok')})
# The positive stress metric is not silently applied to a strain-path rate law.
rate=json.loads((HERE/'regression-models/hypoplastic-sand-vw96.json').read_text());z=[]
for field in rate['state']:z.extend(field['initial'] if isinstance(field['initial'],list) else [field['initial']])
params=','.join(str(v['default']) for v in rate['parameters'].values());settings=json.loads((HERE/'POLICY.json').read_text())['numerics']['default_study_settings']
cmd=[str(EXE),'--model',rate['id'],'--mode','integrate','--parameters',params,'--initial',','.join(map(str,z)),'--strain','0,0,0,0,0,0','--integration-settings',','.join(map(str,settings))]
proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120);r=json.loads(proc.stdout);check('unsupported_rate_reject',not r.get('ok') and 'requires an incremental residual' in r.get('message','') and r.get('state')==z,r)
raw=RAW/'unsupported-rate.json';raw.write_text(proc.stdout);requests.append({'command':cmd,'returncode':proc.returncode,'raw_path':str(raw.relative_to(ROOT)),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'ok':r.get('ok')})
report={'id':'lade-domain-control-disabled-legacy-v1','checks':checks,'requests':requests,'passed':all(c['passed'] for c in checks),'scope':'All56retained v2literal native requests compare every full state exactly with controller disabled; includes retained original failures, not scientific gate waiver'}
(HERE/'native-legacy-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'failures':[c for c in checks if not c['passed']]},indent=2));raise SystemExit(0 if report['passed'] else 1)
