"""Audit exact frozen local-delivery evidence without rerunning compiled material calls."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=json.loads((OUT/'package-manifest-v2.json').read_text());site=Path(manifest['package']);assert site.is_dir()
 for name,h in manifest['files'].items():assert sha(site/name)==h,name
 for name,h in manifest['root_sources'].items():assert sha(ROOT/name)==h,name
 process=json.loads((OUT/'actual-browser-final-process-v6.json').read_text());assert process['returncode']==0
 raw=process['stdout'].split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0].strip();browser=json.loads(raw);assert browser['result']=='PASS';assert not browser['browser_errors'] and not browser['network_failures']
 for part in ('lifecycle','imported'):assert browser[part]['result']=='PASS'
 for name,h in browser['imported']['fetched'].items():assert manifest['files'][name]==h,name
 source=json.loads((OUT/'browser-default-run-v2.json').read_text());assert source==json.loads(Path('/private/tmp/atlas-norsand-main-atlas-v1/replayed-run.json').read_text())
 review=ROOT/'catalogue/agent-reviews/norsand-1993-agent-v1.json';validate_review(review,for_approval=True);entry=approval_entry(review);assert [a for a in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models'] if a['model_id']==source['model']]==[entry]
 for name in ('package-process-v4.json','package-test-v2.json'):assert json.loads((OUT/name).read_text())['returncode']==0
 assert json.loads((OUT/'supported-package-v2.json').read_text())['status']=='passed'
 assert json.loads((OUT/'database-check-v2.json').read_text())['result']=='PASS'
 download=json.loads((OUT/'downloads/download-receipt-v1.json').read_text());assert sha(ROOT/download['path'])==download['sha256']
 with zipfile.ZipFile(ROOT/download['path']) as z:assert z.testzip() is None;assert len(z.namelist())==download['files'];assert not any(n.lower().endswith('.pdf') for n in z.namelist())
 pins=[OUT/name for name in ('package-manifest-v2.json','package-process-v4.json','package-test-v2.json','supported-package-v2.json','database-check-v2.json','actual_browser_final_v6.js','actual-browser-final-process-v6.json','browser-default-run-v2.json','downloads/download-receipt-v1.json','downloads/download-replay-result-v1.json')]
 pins += sorted((ROOT/'output/playwright/norsand-v6').glob('*.png'))
 result={'result':'PASS','scope':'Exact NorSand active axial local main-atlas integration/browser/download; no global-suite/remote/live claim','package_files':len(manifest['files']),'current_root_source_bindings':len(manifest['root_sources']),'fetched_browser_assets':len(browser['imported']['fetched']),'browser':browser,'download':download,'artifacts':{p.relative_to(ROOT).as_posix():sha(p) for p in pins},'retained_limitations':['Unrelated global catalogue failure: concurrent duncan-chang-1970 discovery entry lacks capability_gap.','Shared ordinary Duncan native/Wasm parity/native fixture qualification remains separately owned; not waived.','No remote authorization, commit, push, remote CI or deployment performed.','Scientific approval is bounded exact9case/58request scope; no experimental/general3D claim.','Earlier strict browser v4/v5 abort findings retained; v6 uses actual catalogue navigation links and unchanged zero error/failure gate.']}
 (OUT/'delivery-check-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('result','package_files','current_root_source_bindings','fetched_browser_assets')}))
if __name__=='__main__':main()
