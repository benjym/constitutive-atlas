"""Read-only workflow/transport audit. No generation, packaging or engine execution."""
from pathlib import Path
import collections, hashlib, json, subprocess, sys
R=Path('/Users/bmar5496/code/constitutive-atlas'); C=Path('/private/tmp/atlas-lade-release-v1'); A=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1'); H=R/A/'live-release-v1'; O=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]; pins={}
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)})
 if not condition: raise AssertionError(name)
def pin(p):
 p=Path(p);pins[str(p)]=sha(p);return p.read_bytes()
try:
 base=subprocess.check_output(['git','-C',str(C),'show','b04b0519398bad9e4b9bf854b2d6e8d4719b7f7b:.github/workflows/verify.yml'])
 (O/'remote-base.yml').write_bytes(base)
 for name in ['WORKFLOW_TRANSPORT-v1.json','WORKFLOW_TRANSPORT-v2.json','verify-candidate.yml','verify-candidate-v2.yml','DEPENDENCIES-v2.json','DEPENDENCIES-v3.json','restore_interface_request.py','interface-request.json']:
  (O/name).write_bytes(pin(H/name))
 v2=json.loads((H/'WORKFLOW_TRANSPORT-v2.json').read_text()); w=pin(C/'.github/workflows/verify.yml').decode(); old=base.decode(); e6=pin(R/'.github/workflows/verify.yml').decode()
 check('exact candidate v2 workflow',sha(C/'.github/workflows/verify.yml')==v2['workflow_sha256']==sha(H/'verify-candidate-v2.yml'))
 # Both jobs retain each baseline executable line, allowing only explicit build argument extension.
 commands=lambda t:collections.Counter(x.strip().removeprefix('- run: ') for x in t.splitlines() if x.strip().startswith(('python ','python -','node ','cmake ','emcmake ','ctest ','- run: ')))
 normalized=w.replace('python tools/build_web.py --controlled-path-wasm-dir '+str(A/'live-release-v1/qualified-norsand'),'python tools/build_web.py')
 check('all baseline run commands retained',not (commands(old)-commands(normalized)))
 check('deploy job exact base',w.split('\n  deploy:')[1]==old.split('\n  deploy:')[1])
 check('workflow header and native matrix/toolchain retained',w.split('\n  native:')[0]==old.split('\n  native:')[0])
 check('exact two explicit transport build args',w.count('--controlled-path-wasm-dir '+str(A/'live-release-v1/qualified-norsand'))==2)
 check('two witness restores before provision',w.count('restore_interface_request.py\n          python -B tools/provision_implicit_path_assets.py')==2)
 gates=['node --test tests/test_ensemble.mjs','python -B -m unittest tests.test_ensemble_package','node tools/test_ensemble_wasm.mjs']
 for gate in gates:check('two retained ensemble gates '+gate,w.count(gate)==2)
 for name,h in v2['files'].items():check('transport exact '+name,sha(C/name)==h)
 for dep in ['DEPENDENCIES-v2.json','DEPENDENCIES-v3.json']:
  for name,h in json.loads((H/dep).read_text())['files'].items():check('dependency exact '+name,sha(C/name)==h)
 B=C/A/'live-release-v1/qualified-norsand'; donor=Path('/private/tmp/atlas-duncan-integration-v2/current-inputs/norsand')
 q=json.loads(pin(B/'controlled-path-qualification.json')); review=json.loads(pin(B/'build-review.json')); binding=q['binding']
 check('seven exact E6 donor copies',all(sha(B/p)==sha(donor/p) for p in ['atlas_path_capability.mjs','atlas_path_capability.wasm','build-review.json','controlled-path-qualification.json','generated/path_api.cpp','generated/path_models.hpp','generated/path_catalogue.json']))
 required={p.relative_to(C).as_posix() for p in (C/'cpp/include/atlas').rglob('*.hpp')}; required.update(p.relative_to(C).as_posix() for p in (C/'cpp/scalar-functions').rglob('*') if p.is_file());required.update(p.relative_to(C).as_posix() for p in (C/'atlas').rglob('*.py') if '__pycache__' not in p.parts);required.update(p.relative_to(C).as_posix() for p in (C/'schemas').rglob('*.json'))
 required.update(['cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'])
 check('exact required NorSand source membership',set(binding['sources'])==required)
 for name,h in binding['sources'].items():check('NorSand source '+name,sha(C/name)==h);pin(C/name)
 for name,h in binding['artifacts'].items():check('NorSand artifact '+name,sha(B/name)==h)
 for name,h in binding['generated'].items():check('NorSand generated '+name,sha(B/'generated'/name)==h)
 gates={'native_requests':58,'wasm_requests':58,'native_successes':40,'native_rejections':18,'wasm_successes':40,'wasm_rejections':18,'source_analytical':True,'parity':True}
 check('NorSand qualified independent binding',q['status']=='passed' and q['schema_version']=='controlled-path-qualified-build-1' and q['gates']==review['gates']==gates and review['status']=='accepted' and review['binding']==binding and review['reviewer_run']!=q['implementation_run'] and sha(B/'build-review.json')==q['independent_review']['sha256'])
 # Imported validation reads JSON/source receipts only. Never call any bundle/provision entrypoint.
 sys.path.insert(0,str(C));from atlas.agent_review import validate_review,approval_entry
 registry=json.loads((C/'catalogue/approved-models.json').read_text())['models']
 for model in ['norsand-jefferies-1993-active-axial','maxwell-series-bulk-shear','lade-duncan-1975-midpoint-elastic-eq19-gap-v4']:
  rows=[x for x in registry if x['model_id']==model]
  if not rows and model=='maxwell-series-bulk-shear':
   rows=[x for x in registry if 'maxwell' in x['model_id']]
  check('single registry '+model,len(rows)==1);row=rows[0];p=C/row['review']['path'];pin(p);validate_review(p,root=C,for_approval=True);check('exact valid E5 registry '+model,row==approval_entry(p,root=C))
 # Every declared assembled input is materialized at exact digest; source-only closure evidence.
 overlay=json.loads(pin(H/'OVERLAY-v1.json'));bad=[]
 for name,entry in overlay['files'].items():
  if sha(C/name)!=entry['sha256']:bad.append(name)
 # Workflow intentionally replaced after assembly.
 check('assembled declared inputs exact',not bad)
 check('overlay unresolved empty',not overlay['unresolved'])
 result={'status':'passed','checks':checks,'pins':pins,'overlay_files':len(overlay['files']),'scope':'Source-only workflow/transport audit; no execution or complete broader-delta acceptance.'}
except Exception as exc:
 result={'status':'failed','error':repr(exc),'checks':checks,'pins':pins}
(O/'CHECK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['checks','pins']}));print('checks',len(checks));sys.exit(result['status']!='passed')
