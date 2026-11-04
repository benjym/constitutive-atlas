"""Pure argv recipe only. No process, build, packaging, provisioning or engine call."""
from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
WORK=Path('/private/tmp/atlas-baseline-delivery-20261105/rate-control-build-v1')
SITE=Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v1')
OBS=HERE.parent/'standard-web-delivery-actual-v1'
def commands(python,node,revision):
 if not all(isinstance(p,str)and Path(p).is_absolute()for p in [python,node]):raise ValueError('absolute qualified Python/Node required')
 if not isinstance(revision,str)or not re.fullmatch('[0-9a-f]{40}',revision)or revision=='64002531f0af5c06ad0402d0d80548102f8e6a38':raise ValueError('exact new owned local commit required after unchanged-source continuation; never stamp640 or invoke Git fallback')
 retained=json.loads((HERE/'retained-auxiliary-roles.json').read_text())['roles']
 args=[python,'-B',str(SOURCE/'tools/build_web.py'),'--wasm-dir',str(WORK/'wasm')]
 for role in retained:args +=[role['flag'],role['directory']]
 for flag,sub in [('--controlled-path-wasm-dir','web/engines/current17-compatible/norsand'),('--maxwell-wasm-dir','web/engines/current17-compatible/maxwell'),('--interface2016-wasm-dir','web/engines/current17-baseline-compatible/interface2016'),('--controlled-time-wasm-dir','web/engines/controlled-time'),('--hill-wasm-dir','web/engines/hill'),('--bingham-wasm-dir','build-bingham-public'),('--perzyna-wasm-dir','build-perzyna-public'),('--implicit-path-wasm-dir','build-implicit-path-wasm')]:args +=[flag,str(SOURCE/sub)]
 args+=['--output',str(SITE)]
 return {'ready_for_actual':False,'publication_environment_addition':{'GITHUB_SHA':revision},'cwd':str(SOURCE),'serial_parent_observer':{'sha256':'7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e','timeout_seconds':1800,'mandatory_reap':True,'preserve_first_failure':True},'operations':[
 {'id':'fast-source-contracts','argv':[python,'-B',str(SOURCE/'tools/ci_fast.py')]},
 {'id':'retained-source-guards','argv':[python,'-B',str(SOURCE/'tools/check_current_dependency_assets.py'),'--current17-baseline','--output',str(OBS/'dependency-guards')]},
 {'id':'standard-web-package','argv':args},
 {'id':'package-engine-smoke','argv':[node,str(SOURCE/'tools/ci_smoke.mjs'),'--native',str(WORK/'native/atlas_solver'),'--wasm',str(SITE/'atlas.js')]},
 {'id':'all994-built-dataset-transport','argv':[node,str(SOURCE/'tools/test_experiments.mjs'),'--built-assets',str(SITE/'experiments')]},
 {'id':'original-package-contracts','argv':[node,'--test',*[str(SOURCE/'tests'/n)for n in ['test_database_download_gate.mjs','test_web_package.mjs','test_supported_package.mjs','test_laboratory_profile_policy.mjs']]]},
 {'id':'supported17-public-inputs','argv':[node,str(SOURCE/'tools/test_supported_package.mjs'),'--directory',str(SITE),'--policy',str(SOURCE/'catalogue/laboratory-package-policy.json'),'--output',str(OBS/'supported-package.json')]},
 {'id':'original-scoped-parity','argv':[node,str(SOURCE/'tools/test_scoped_parity.mjs'),str(WORK/'native/atlas_solver'),str(WORK/'wasm'),str(OBS/'scoped-parity.json'),str(SOURCE/'catalogue/laboratory-profile-policy.json')]}
 ],'no_automatic_rebuild_provision_network':True}
if __name__=='__main__':raise SystemExit('Pure recipe: coordinator supplies qualified tool paths, exact revision and completed launch bindings; this file does not execute.')
