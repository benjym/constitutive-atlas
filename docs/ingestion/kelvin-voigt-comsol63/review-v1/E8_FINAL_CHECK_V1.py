"""Saved E8 evidence audit. Writes only new E8_FINAL_* review addenda.
No network, builds, compiled calls, Git mutation or production imports.
"""
import hashlib, importlib.util, json, math, sys, tarfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
SOURCE=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source')
PACKET=Path('docs/ingestion/kelvin-voigt-comsol63')
R=SOURCE/PACKET/'release-v3'
SITE=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/tested-upload-v3/site')
OUT=ROOT/PACKET/'review-v1'
COMMIT='ecd1f3b12381dd8edec34fe6121b80a0bd5792aa'
MID='kelvin-voigt-comsol63-deviatoric-zero-spin-ode'
inputs={}
def sha(p):
 p=Path(p)
 with p.open('rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()
 inputs[str(p)]={'sha256':h,'bytes':p.stat().st_size};return h
def read(p):sha(p);return json.loads(Path(p).read_text())
def write(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+'\n')
def main():
 for p in ['AGENTS.md','IMPLEMENTATION_PLAN.md','docs/MODEL_DELIVERY_CHECKLIST.md','docs/AGENT_REVIEW_POLICY.md','docs/PUBLIC_MODEL_PROFILES.md','docs/RESEARCH_CHARTER.md','docs/FORMULATION_CONTRACT.md']:
  sha(ROOT/p)
 for p in ['README.md','FINAL_LOCAL_RELEASE_REVIEW_V1.md','E8_ECD_PREPARATION_REVIEW_V1.md','E8_ECD_SOURCE_PRELIMINARY_V1.json','E8_LIVE_PRELIMINARY_CHECK_V1.json','CHECKLIST_CROSSWALK_V3.json','check_committed_upload_database.py']:
  sha(ROOT/PACKET/'review-v1'/p)
 for p in R.rglob('*'):
  if p.is_file():sha(p)
 sha(SOURCE/PACKET/'DELIVERY.md')
 preservation=read(Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/closeout-docs/preservation.json'))
 for entry in preservation:assert sha(SOURCE/entry['archive'])==entry['sha256']
 w=read(R/'workflow.json')
 expected={'native (ubuntu-latest, 3.12)','native (macos-26, 3.14)','wasm','wasm-linux','controlled-path','deploy'}
 assert w['headSha']==COMMIT and w['status']=='completed' and w['conclusion']=='success'
 assert {j['name'] for j in w['jobs']}==expected
 assert all(j['status']=='completed' and j['conclusion']=='success' for j in w['jobs'])
 manifest=read(R/'tested-upload-manifest.json');assert manifest['application_revision']==COMMIT and manifest['workflow']==41357170257
 files=manifest['files'];assert len(files)==manifest['assets']==1049
 assert {p.relative_to(SITE).as_posix() for p in SITE.rglob('*') if p.is_file()}==set(files)
 for name,h in files.items():assert sha(SITE/name)==h,name
 tarpath=SITE.parent/'artifact.tar';assert sha(tarpath)==manifest['tar_sha256']
 # Verify exact extracted file set and contents independently against upload tar.
 with tarfile.open(tarpath) as archive:
  members={m.name.removeprefix('./'):m for m in archive.getmembers() if m.isfile()}
  assert set(members)==set(files)
  for name,member in members.items():
   with archive.extractfile(member) as stream:h=hashlib.file_digest(stream,'sha256').hexdigest()
   assert h==files[name],name
 engine=SITE/'engine-kelvin-voigt';identity=read(engine/'identity.json')
 assert identity['model']==MID and identity['release_revision']==COMMIT
 assert identity['model_sha256']==sha(engine/(MID+'.json'))=='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
 assert identity['module_sha256']==sha(engine/'kv.mjs') and identity['wasm_sha256']==sha(engine/'kv.wasm')
 assert identity['review_sha256']==sha(engine/'review.json')=='7dc232c311541aea981981e1efcfc97448509fbc31d9602b9cead4a7890223c4'
 assert identity['approval_sha256']==sha(engine/'approval.json')
 for name,h in read(engine/'package-manifest.json')['files'].items():assert sha(SITE/name)==h
 sql=read(OUT/'E8_FINAL_DATABASE_CHECK_V1.json');assert sql['passed'] and sql['application_commit']==COMMIT
 assert sql['database_sha256']==sha(SITE/'atlas.sqlite')
 # Inspected repository reference/assessor imports standard library only;
 # call assess on saved observations, never collect_native/main/compiled code.
 Q=SOURCE/PACKET/'execution-v3'
 for name in ['study.py','reference.py','cases.json','freeze.json']:sha(Q/name)
 sys.path.insert(0,str(Q));spec=importlib.util.spec_from_file_location('kelvin_e8_saved_assessor',Q/'study.py');study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
 study.verify_freeze();cases=read(Q/'cases.json')['cases'];reports={}
 for name in ['native-ci/native-linux.json','native-ci/native-macos.json','wasm-ci/macos/report.json','wasm-ci/linux/report.json']:
  wrapper=read(R/name);report=wrapper.get('report',wrapper)
  rows=wrapper['capture'] if 'capture' in wrapper else read(R/name.replace('report.json','raw.json'))
  actual=study.assess(cases,rows);assert actual==report
  assert report['passed'] and report['cases']==43 and report['calls']==86 and report['negative_recovery_pairs']==8
  reports[name]={'sha256':sha(R/name),'saved_assessor_replay':True,'preset_strain_error':report['errors']['creep-preset']['strain']}
 B=R/'live-browser-v1';ui=read(B/'default-ui.json');assert ui['provenance']==identity
 assert ui['model']==MID and ui['panelVisible'] and ui['exportEnabled']
 assert 'Completed 8 physical seconds' in ui['status']
 c=ui['controls'];K,G,tau=json.loads(c['parameters']);D=json.loads(c['initialRates'])
 assert json.loads(c['initial'])==[0]*6 and abs(sum(D[:3]))<1e-15 and c['mode']=='creep'
 assert len(ui['rows'])==11 and all(len(row)==14 for row in ui['rows'])
 ee=se=0.
 for row in ui['rows'][1:]:
  t=float(row[0])-float(c['start'])
  for i in range(6):
   ee=max(ee,abs(float(row[2+i])-tau*D[i]*(-math.expm1(-t/tau))))
   se=max(se,abs(float(row[8+i])-2*G*tau*D[i]))
 assert ee<3e-8 and se<1
 y=lambda plot:[float(pair.split(',')[1]) for pair in plot['points'].split()]
 span=lambda a:max(a)-min(a)
 assert span(y(ui['plots'][0]))<1e-8 and span(y(ui['plots'][1]))>100
 for name in ['profile-desktop.json','profile-mobile.json']:
  p=read(B/name);assert p['technicalClosed'] and p['documentWidth']==p['width'] and p['bodyScrollWidth']<=p['bodyWidth']
  assert p['profileFirst']=='model-profile'
 p=read(B/'profile-desktop.json');assert len(p['parameterRows'])==4
 assert p['parameterRows'][1].endswith('Pa') and p['parameterRows'][2].endswith('Pa') and p['parameterRows'][3].endswith('s')
 assert 'all six initial total-strain components' in p['body'] and 'halve every incoming' in p['body']
 p=read(B/'laboratory-mobile.json');assert p['documentWidth']==p['width']==390
 assert len(p['plots'])==2 and all(0<x<=390 for x in p['plots'])
 assert read(B/'related-navigation.json')['heading']=='Maxwell viscoelasticity'
 assert read(B/'laboratory-profile-return.json')['technicalClosed']
 assert read(B/'technical-details.json')['open'] and read(B/'console.json')==[]
 links=[]
 from urllib.parse import urlparse,unquote
 for name in ['default-ui.json','profile-desktop.json','profile-mobile.json','technical-details.json']:
  for link in read(B/name).get('links',[]):
   href=link['href'];parsed=urlparse(href)
   if parsed.netloc=='benjym.github.io' and parsed.path.startswith('/constitutive-atlas/'):
    rel=unquote(parsed.path[len('/constitutive-atlas/'):]) or 'index.html'
    assert rel in files,(name,href);links.append(rel)
 pending=[];livepath=R/'live-assets.json'
 if not livepath.exists():pending.append('Complete 1049-asset live response comparison is not yet present.')
 else:
  live=read(livepath);assert live['passed'] and live['assets']==1049 and live['failures']==[]
  assert live['base_url']=='https://benjym.github.io/constitutive-atlas/'
  assert {v['path'] for v in live['results']}==set(files)
  for row in live['results']:
   assert row['passed'] and row['status']==200
   assert row['expected_sha256']==row['actual_sha256']==files[row['path']]
 result={'identity':'kelvin-independent-final-E8-audit-v1','reviewer':'/root/maxwell_scientific_review','prior_involvement':'No Kelvin implementation or prior review authorship; prior separate-agent source/E0-E7 acceptance carried explicitly.','application_commit':COMMIT,'workflow':41357170257,'six_terminal_jobs_pass':True,'tested_upload_tar_and_all_assets_exact':1049,'engine_model_review_approval_exact':True,'backend_saved_replay':reports,'exact_git_database':sql,'live_default_comparisons':120,'max_displayed_strain_error':ee,'max_displayed_stress_error_Pa':se,'fetched_live_engine_identity_exact_upload':True,'same_site_link_targets_bound':sorted(set(links)),'profile_desktop_mobile_and_plots_supported':True,'console_warnings_errors':0,'live_all1049_assets_pass':not pending,'pending':pending,'E8_technical_acceptance':not pending,'compiled_or_network_calls_by_this_script':0}
 write('E8_FINAL_CHECK_V1.json',result)
 write('E8_FINAL_INPUTS_V1.json',{'files':[{'path':p,**v} for p,v in sorted(inputs.items())],'notes':'Asset hashes are actual tested-upload bytes. Source-only prior reviews are inherited and bound, not reauthored. Screenshots visually examined by this reviewer.'})
 print(json.dumps({k:v for k,v in result.items() if k not in ['backend_saved_replay','exact_git_database','same_site_link_targets_bound']},indent=2))
if __name__=='__main__':main()
