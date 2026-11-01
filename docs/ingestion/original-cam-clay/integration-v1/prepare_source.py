"""Freeze normal-root build inputs and prospective thirteen-model integration gates."""
from pathlib import Path
import shutil,hashlib,json,datetime
B=Path(__file__).resolve().parent;R=B.parents[3];S=B/'source-snapshot';assert not S.exists()
for folder,pattern in [('cpp','**/*'),('atlas','**/*.py'),('schemas','*.json'),('models','**/*.json'),('tests','**/*.cpp'),('tests/fixtures','**/*.json'),('fixtures','**/*.json')]:
 for p in (R/folder).glob(pattern):
  if p.is_file():
   out=S/p.relative_to(R);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
shutil.copyfile(R/'CMakeLists.txt',S/'CMakeLists.txt')
tracked=['catalogue/manifest.json','catalogue/approved-models.json','catalogue/laboratory-package-policy.json','catalogue/laboratory-profile-policy.json','catalogue/laboratory-control-support.json','web/app.js','web/index.html','web/laboratory-support.mjs','tools/build_web.py','tools/laboratory_profile_policy.mjs','tools/test_wasm.mjs','tools/test_browser_loading.mjs','tests/test_laboratory_profile_policy.mjs','tests/test_laboratory_support.mjs','.github/workflows/verify.yml']
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()}
files.update({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in tracked})
plan=dict(identity='occ-thirteen-model-integration-v1-precompiled',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),common_catalogue_observations=0,files=files,gates=['Normal root atlas_solver native thenWasm, one target --parallel1 each; metadata same13definitions, no existing model loss','Native atlas_numerical_tests/atlas_recorded_tests with explicit-gis20-occ-v3; allprior derivative/covariance/reference checks unchanged; OCC anisotropic fixture made source-admissible pc150kPa','Complete policy35scopedcases across13models and originallegacyrequests; one explicitly retained OCCcyclicstressfailedprefix, allold12expectations unchanged','Supported fullpackage ordinarydrained1%100steps:13models includingOCC; retained GISordinaryfail andsameexplicitnamedexample; no new ordinaryOCCexception','Real browser default and protocols, state/parameter edits, invalid/recovery/reset/latestrequest, disabledcyclicstress, exactimport/export/replay, meaningfulplots, accepted review+source/dossier andoverlayunavailability','No remoteaction/liveclaim'],limitations=['OCC E5scope and material limitations unchanged','Strict originalall-default GISfailure remains; supportedpackage isdistinctgate','Otherexisting dedicated SLS/J2/powercreep modules must retainexactqualifiedidentities'])
(B/'prospective-freeze.json').write_text(json.dumps(plan,indent=2)+'\n')
stage=Path('/private/tmp/atlas-occ-integration-v1');shutil.copytree(S,stage/'source')
print('Frozen source and integration gates',len(files),'files')
