"""Freeze exact published/current dispatch inputs; no build or material call."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;ROOT=D.parents[3];BASE='37d70660e3561c342bb114716c233a3d06651bcb';OLD='3873a48b256ed37cbc78378ee6b41d73139676f8';SOURCE=Path('/private/tmp/atlas-control-partition-v1/source')
def sha(data):return hashlib.sha256(data).hexdigest()
paths=['tools/check_native_fixture_contracts.py','catalogue/laboratory-package-policy.json','.github/workflows/verify.yml','tests/test_solver.cpp','tests/test_recorded.cpp','tests/test_ci_profiles.py','tests/test_native_fixture_contracts.py','models/ramberg-osgood-ansys242.json']
inputs={}
for commit,label,names in [(BASE,'published-37d',paths),(OLD,'archival-14',paths[:2])]:
 for name in names:
  data=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT);p=D/label/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);inputs[str(p.relative_to(D))]={'git_source':commit+':'+name,'sha256':sha(data)}
current={}
for name in paths:
 if(ROOT/name).is_file():current[name]=sha((ROOT/name).read_bytes())
policy15=json.loads((D/'published-37d/catalogue/laboratory-package-policy.json').read_text());policy14=json.loads((D/'archival-14/catalogue/laboratory-package-policy.json').read_text());m14=policy14['models'];m15=policy15['models'];assert len(m14)==14 and len(m15)==15 and m15=={**m14,'ramberg-osgood-ansys242':'c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2'}
md='manzari-dafalias-1997-constant-m-be-v1';m16={**m15,md:'28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'};identities={}
for size,mapping in [(14,m14),(15,m15),(16,m16)]:
 models=[]
 for name,h in sorted(mapping.items()):
  b=(SOURCE/'models'/(name+'.json')).read_bytes();assert sha(b)==h;models.append(json.loads(b))
 digest=sha(json.dumps(models,sort_keys=True,separators=(',',':')).encode());record={'schema_version':'0.1','sha256':digest,'models':models};blob=(json.dumps(record,indent=2)+'\n').encode()
 identities[str(size)]={'models':mapping,'catalogue_embedded_sha256':digest,'catalogue_file_sha256':sha(blob),'policy_id':policy14['id']if size==14 else policy15['id']if size==15 else 'prospective16qualification-map; no scientific admission/policy16 fabricated'}
assert identities['16']['catalogue_file_sha256']=='f38da28fd2857e03e1def0c2ed70dc2a5b999984ef087360b324c933a2da3a99'
(D/'catalogue-identities.json').write_text(json.dumps({'identity':'native-ci-exact-catalogue-dispatch-v2','authoritative_published_base':BASE,'archival_base':OLD,'catalogues':identities},indent=2)+'\n')
extra=['docs/investigations/control-partition-derivative-v1/native-admissible-fixture-plan-v1/manifest.json','docs/investigations/control-partition-derivative-v1/native-admissible-fixture-plan-v1/POLICY.md','docs/investigations/control-partition-derivative-v1/native-admissible-fixture-review-v1/manifest.json','docs/ingestion/manzari-dafalias-1997/delivery-v1/ordinary-regression-v7/policy.json']
(D/'inputs.json').write_text(json.dumps({'published_snapshots':inputs,'checkout_readonly_drift_baseline':current,'repository_dependencies':{name:sha((ROOT/name).read_bytes())for name in extra}},indent=2)+'\n')
print(json.dumps({'published_base':BASE,'catalogues':{n:{'models':len(v['models']),'catalogue_file_sha256':v['catalogue_file_sha256']}for n,v in identities.items()},'root_shared_edits':0,'compiled_calls':0},indent=2))
