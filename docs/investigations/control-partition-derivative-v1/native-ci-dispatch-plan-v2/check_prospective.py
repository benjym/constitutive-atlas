"""Pure policy mocks and frozen analytical helpers; no subprocess/material calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import copy,hashlib,importlib.util,json,math,difflib
D=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/atlas-control-partition-v1/source')
identities=json.loads((D/'catalogue-identities.json').read_text())['catalogues']
contracts=json.loads((D/'process-contracts.json').read_text())
checks=[]
ROOT=D.parents[3]
ordinary=json.loads((ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/ordinary-regression-v7/policy.json').read_text())
assert {c['model']:c['definition_sha256']for c in ordinary['cases']}==identities['16']['models']
assert len(ordinary['cases'])==16
assert ordinary['generated_catalogue_sha256']==identities['16']['catalogue_file_sha256']
def sha(b):return hashlib.sha256(b).hexdigest()
def check(name,fn,reject=False):
 try:fn()
 except (AssertionError,ValueError,KeyError,TypeError) as exc:
  assert reject,(name,str(exc));checks.append({'id':name,'expected':'reject','observed':'reject'});return
 assert not reject,name+' accepted corruption'
 checks.append({'id':name,'expected':'accept','observed':'accept'})
def load_helper(relative,name):
 spec=importlib.util.spec_from_file_location(name,D/relative);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
published=load_helper('published-37d/tools/check_native_fixture_contracts.py','frozen_published_helper')
archived=load_helper('archival-14/tools/check_native_fixture_contracts.py','frozen_archival_helper')
source_bytes={name:(SOURCE/'models'/(name+'.json')).read_bytes()for name in identities['16']['models']}
source_hashes={k:sha(v)for k,v in source_bytes.items()}
def catalogue(size):
 models=[json.loads(source_bytes[k])for k in sorted(identities[str(size)]['models'])]
 return {'schema_version':'0.1','sha256':sha(json.dumps(models,sort_keys=True,separators=(',',':')).encode()),'models':models}
def classify(blob,hashes):
 assert blob['schema_version']=='0.1'
 models=blob['models'];ids=[m['id']for m in models]
 assert ids==sorted(set(ids))
 mapping={name:hashes[name]for name in ids}
 matches=[n for n,v in identities.items()if v['models']==mapping]
 assert len(matches)==1
 size=matches[0];frozen=identities[size]
 assert blob['sha256']==frozen['catalogue_embedded_sha256']
 assert sha((json.dumps(blob,indent=2)+'\n').encode())==frozen['catalogue_file_sha256']
 assert models==[json.loads(source_bytes[k])for k in ids]
 return size
for size in [14,15,16]:check('exact-catalogue-'+str(size),lambda size=size:classify(catalogue(size),source_hashes))
mutations={
 'wrong-schema':lambda b:b.update(schema_version='0.3'),
 'duplicate-id':lambda b:b['models'].append(copy.deepcopy(b['models'][0])),
 'missing-model':lambda b:b['models'].pop(),
 'reordered-models':lambda b:b['models'].reverse(),
 'wrong-embedded-digest':lambda b:b.update(sha256='0'*64),
 'altered-generated-object':lambda b:b['models'][0].update(title='corruption'),
 'unknown-same-count-id':lambda b:b['models'][0].update(id='unknown'),
 'extra-model':lambda b:b['models'].append({'id':'zz-unknown'})}
for name,mutation in mutations.items():
 b=catalogue(16);mutation(b);check(name,lambda b=b:classify(b,source_hashes),True)
for name in ['ramberg-osgood-ansys242','manzari-dafalias-1997-constant-m-be-v1',published.OCC]:
 hashes=dict(source_hashes);hashes[name]='0'*64
 check('source-hash-'+name,lambda hashes=hashes:classify(catalogue(16),hashes),True)
# Independently calculate the same original cone endpoint from source data, then
# exercise exact unchanged published/archived analytical functions (never main).
model=json.loads(source_bytes[published.OCC]);p={k:v['default']for k,v in model['parameters'].items()}
volume=model['state'][1]['initial']/(1+1e-4)
pressure=p['pref']*math.exp((p['Gamma']+p['lambda_c']-p['kappa']-volume)/p['lambda_c'])
residual=abs(pressure-100000)/100000
message=f'failed knot 1 residual {residual:.17g} trials 1 de0 0.0001 de1 0\ndrained replay failed: {published.OCC} singular mixed-control system; last committed knot retained\n'
for size,helper in [(14,archived),(15,published)]:check('unchanged-analytical-'+str(size),lambda size=size,helper=helper:helper.check_recorded_failure(message,identities[str(size)]['models'],root=SOURCE))
check('inherited-thirteen',lambda:published.check_recorded_failure(message,published.PRIOR_THIRTEEN,root=SOURCE))
check('inherited-twelve-GIS',lambda:published.check_recorded_failure(published.GIS_FAILURE,{k:v for k,v in published.PRIOR_THIRTEEN.items()if k!=published.OCC},root=SOURCE))
spy=[]
def projected(blob,hashes,msg=message):
 assert classify(blob,hashes)=='16' # mandatory before projection/delegation
 mapping={m['id']:hashes[m['id']]for m in blob['models']}
 del mapping['manzari-dafalias-1997-constant-m-be-v1']
 assert mapping==identities['15']['models']
 spy.append('called');return published.check_recorded_failure(msg,mapping,root=SOURCE)
check('exact16-validated-before-projection',lambda:projected(catalogue(16),source_hashes))
for name in identities['16']['models']:
 hashes=dict(source_hashes);hashes[name]='0'*64;before=len(spy)
 check('no-projection-before-validation-'+name,lambda hashes=hashes:projected(catalogue(16),hashes),True)
 assert len(spy)==before
for name,bad in {
 'wrong-residual':message.replace(f'{residual:.17g}','1'),
 'nan-residual':message.replace(f'{residual:.17g}','nan'),
 'wrong-knot':message.replace('knot 1','knot 2'),
 'wrong-trials':message.replace('trials 1','trials 2'),
 'wrong-axial':message.replace('de0 0.0001','de0 0.0002'),
 'wrong-de1':message.replace('de1 0','de1 1'),
 'GIS-instead-of-OCC':published.GIS_FAILURE,
 'missing-newline':message.rstrip(),
 'extra-output':message+'extra\n'}.items():
 check('strict-recorded-'+name,lambda bad=bad:projected(catalogue(16),source_hashes,bad),True)

def process_rows():
 rows=copy.deepcopy(contracts['cases'])
 for row in rows:
  row['timeout']=False;row['argv']=['/mock/build/'+row['target']]
  if row['id']=='atlas_recorded_tests-default':row['stderr']=message
 return rows

def verify_rows(rows):
 assert [r['id']for r in rows]==[r['id']for r in contracts['cases']]
 for row,expected in zip(rows,contracts['cases']):
  assert row['target']==expected['target']
  assert row['argv']==['/mock/build/'+expected['target']]
  assert not row['timeout']
  for key in ['native_selector','numerical_selector','returncode','stdout']:assert row[key]==expected[key]
  if row['id']=='atlas_recorded_tests-default':projected(catalogue(16),source_hashes,row['stderr'])
  else:assert row['stderr']==expected['stderr']
check('eight-exact-process-contracts',lambda:verify_rows(process_rows()))
process_mutations={
 'missing-call':lambda r:r.pop(),
 'extra-call':lambda r:r.append(copy.deepcopy(r[0])),
 'duplicate-call':lambda r:r.__setitem__(1,copy.deepcopy(r[0])),
 'reordered-calls':lambda r:r.reverse(),
 'unexpected-success':lambda r:r[0].update(returncode=0),
 'signal':lambda r:r[0].update(returncode=-9),
 'timeout':lambda r:r[0].update(timeout=True),
 'wrong-target':lambda r:r[0].update(target='other'),
 'wrong-argv':lambda r:r[0].update(argv=['/other/build/atlas_numerical_tests']),
 'inherited-selector':lambda r:r[0].update(numerical_selector='md1997-source-admissible-v1'),
 'wrong-model-count14':lambda r:r[0].update(stdout=r[0]['stdout'].replace('16','14')),
 'wrong-model-count15':lambda r:r[0].update(stdout=r[0]['stdout'].replace('16','15')),
 'wrong-unknown-error':lambda r:r[1].update(stderr='FD test outside domain\n'),
 'extra-stdout':lambda r:r[1].update(stdout='unexpected\n'),
 'truncated-error':lambda r:r[0].update(stderr=r[0]['stderr'].rstrip()),
 'legacy-success':lambda r:r[4].update(returncode=0),
 'missing-compatibility-error':lambda r:r[6].update(stderr='')}
for name,mutation in process_mutations.items():
 rows=process_rows();mutation(rows);check('process-'+name,lambda rows=rows:verify_rows(rows),True)

def env_for(size,suite):
 assert str(size)in identities and suite in ['macos-main','linux-main','recorded']
 env={'ATLAS_NATIVE_FIXTURES':'poison','ATLAS_NUMERICAL_FIXTURES':'poison','KEEP':'yes'}
 for key in contracts['sanitize_selectors']:env.pop(key,None)
 env['ATLAS_NATIVE_FIXTURES']='explicit-gis20-occ-restart-duncan-v5'
 if size==16 and suite!='recorded':env['ATLAS_NUMERICAL_FIXTURES']='md1997-source-admissible-v1'
 return env
for size in [14,15,16]:
 for suite in ['macos-main','linux-main','recorded']:
  env=env_for(size,suite)
  check(f'environment-{size}-{suite}',lambda size=size,suite=suite,env=env:(_ for _ in ()).throw(AssertionError())if (('ATLAS_NUMERICAL_FIXTURES'in env)!=(size==16 and suite!='recorded')or env['KEEP']!='yes')else None)
check('unknown-suite',lambda:env_for(16,'skip-numerical'),True)
check('unknown-catalogue',lambda:env_for(17,'macos-main'),True)
for rc in [1,-9,124]:check('positive-CTest-nonzero-'+str(rc),lambda rc=rc:(_ for _ in ()).throw(AssertionError())if rc!=0 else None,True)
# Reconstruct review-only workflow and verify both reversible edit and all bytes
# outside its single bounded native block. No YAML/CI workflow is executed.
proof=json.loads((D/'workflow-diff-proof.json').read_text())
original=(D/'published-37d/.github/workflows/verify.yml').read_text()
assert original.count(proof['replaced_original_block'])==1
proposal=original.replace(proof['replaced_original_block'],proof['proposed_block'],1)
assert sha(original.encode())==proof['published_sha256']
assert sha(proposal.encode())==proof['proposed_sha256']
assert proposal.replace(proof['proposed_block'],proof['replaced_original_block'],1)==original
expected=''.join(difflib.unified_diff(original.splitlines(True),proposal.splitlines(True),fromfile='a/.github/workflows/verify.yml',tofile='b/.github/workflows/verify.yml'))
assert expected==(D/'workflow-proposal.diff').read_text()
for needle in ['scalar-native','orthotropic','ramberg','hill-native','Linux portable Python suite','Verify recorded-path JSON replay','  wasm:','  deploy:']:
 assert needle.lower()in original.lower() and needle.lower()in proposal.lower(),needle
assert 'continue-on-error'not in proof['proposed_block']
assert proof['proposed_block'].index('contracts.json')<proof['proposed_block'].index('--suite macos-main')
checks.append({'id':'reversible-workflow-and-non-native-byte-preservation','expected':'accept','observed':'accept'})
assert not list(D.rglob('*.pyc')) and not list(D.rglob('__pycache__'))
result={'identity':'native-ci-dispatch-v2-source-only-mock-checks','status':'passed','checks':checks,'count':len(checks),'compiled_calls':0,'live_subprocesses':0,'scope':'policy mocks and frozen analytical helper functions; not implementation acceptance','OCC_source_derived_residual':residual}
(D/'static-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'compiled_calls':0}))
