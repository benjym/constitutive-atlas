"""Recheck frozen release/CI/upload/live/browser receipts; no compiled calls."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for name,digest in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(HERE/name)==digest,name
 revision='5ae90008d44575ef4b92b2b9e6e34fe1ca1f47b3'
 ci=json.loads((HERE/'ci-run.json').read_text());assert ci['headSha']==revision and ci['status']=='completed' and ci['conclusion']=='success'
 assert len(ci['jobs'])==5 and all(j['status']=='completed' and j['conclusion']=='success' for j in ci['jobs'])
 artifact=json.loads((HERE/'upload-artifact.json').read_text());assert artifact['id']==13078482656 and artifact['workflow_run']['head_sha']==revision and artifact['workflow_run']['id']==41294049206
 upload=json.loads((HERE/'upload-check.json').read_text());assert upload['identity']['release_revision']==revision and upload['burgers_package_hashes_valid'] and upload['main_models']==12
 model_sha='1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c';assert upload['identity']['model_sha256']==model_sha
 live=json.loads((HERE/'live-assets.json').read_text());assert live['revision']==revision and live['identity']==upload['identity'] and live['all_equal'] and len(live['assets'])==44
 assert all(x['status']==200 and x['upload_sha256']==x['live_sha256'] for x in live['assets'])
 source=json.loads((HERE/'source-binding.json').read_text());assert source['revision']==revision and source['model_sha256']==model_sha
 for name,digest in source['production_files'].items():assert hashlib.sha256(subprocess.check_output(['git','show',revision+':'+name])).hexdigest()==digest,name
 browser=json.loads((HERE/'browser.txt').read_text().split('### Result\n',1)[1].split('\n### Ran',1)[0]);assert browser['state']['identity']==upload['identity'] and browser['plots']==3 and not browser['errors'] and not browser['network']
 assert len(browser['links'])==5 and all(x['status']==200 for x in browser['links']);assert browser['layout']==dict(width=390,scroll=390)
 a=json.loads((HERE/'live-relaxation.json').read_text());b=json.loads((HERE/'live-replay.json').read_text());assert a==b and a['provenance']==upload['identity'] and len(a['result']['points'])==10
 numerical=json.loads((HERE/'browser-analytical.json').read_text());assert numerical['exact_full_result_replay'] and numerical['frozen_gates']==dict(stress_Pa=20,Kelvin_strain=2e-6,strain=2e-6)
 for case in numerical['cases'].values():assert case['stress_Pa']<=20 and case['Kelvin_strain']<=2e-6 and case['strain']<=2e-6
 return dict(revision=revision,ci_jobs=5,all_success=True,live_assets_equal=44,actual_live_browser=True,independent_analytical_cases=2,exact_replay=True,compiled_calls=0,experimental_validation=False)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
