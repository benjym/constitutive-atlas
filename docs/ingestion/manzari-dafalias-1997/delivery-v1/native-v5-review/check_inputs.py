"""Read-only input checks; no active numerical output is read."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;ROOT=P.parents[3];B=P/'qualification-native-v5';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());f=load(B/'freeze.json');checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
check('all8 pre-observation input identities exact',len(f['inputs'])==8 and all(h(ROOT/k)==v for k,v in f['inputs'].items()))
s=load(ROOT/'docs/investigations/control-partition-derivative-v1/implementation-v1/source-freeze.json');check('exact582source file bytes',len(s['source_files'])==582 and all(h(Path(s['source_directory'])/k)==v for k,v in s['source_files'].items()))
br=load(P/'build-native-v4/build-receipt.json');check('actual build artifact binding',h(Path(f['artifact_path']))==f['artifact_sha256']==br['artifact_sha256'] and br['source_freeze_sha256']==f['inputs']['docs/investigations/control-partition-derivative-v1/implementation-v1/source-freeze.json'])
for folder in ['raw-link-v7','resolution-study-v4','ordinary-regression-v7']:
 check(folder+'/frozen file closure',all(h(P/folder/k)==v for k,v in load(P/folder/'manifest.json').items()))
plan=load(P/'resolution-study-v4/requests.json');check('35cases original14path resolutions and publicdefault scope',len(plan['cases'])==35 and sorted(set(c['resolution']for c in plan['cases']if c.get('resolution')in[2048,4096]))==[2048,4096])
check('unchanged candidate hash',h(P/'manzari-dafalias-1997-constant-m-be-v1.json')==plan['model_sha256']=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064')
check('ordinary16 frozen complete expected cases',len(load(P/'ordinary-regression-v7/policy.json')['cases'])==16)
(D/'input-checks.json').write_text(json.dumps({'freeze_sha256':h(B/'freeze.json'),'checks':checks,'actual_results_observed_by_this_script':False,'compiled_calls':0},indent=2)+'\n');print(len(checks),h(B/'freeze.json'))
