#!/usr/bin/env python3
"""Final integration source receipt check; optionally checks saved final package bytes."""
import hashlib,html,json,pathlib,re,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;REVIEW=HERE.parent;ROOT=REVIEW.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def text(p):return p.read_text()
def run(site=None):
 f=read(HERE/'release-freeze.json');assert f['before_final_package_execution']
 for p,h in f['files'].items():assert sha(HERE/'final-source'/p)==h,p
 old=REVIEW/'source-r3';new=HERE/'final-source'
 before=text(old/'tools/test_j2_laboratory_package.mjs');after=text(new/'tools/test_j2_laboratory_package.mjs')
 assert before.replace("'sls.html','power-creep.html','recorded.html'","'sls.html','recorded.html'")==after
 oldbuilder=text(old/'tools/build_j2_laboratory.py');builder=text(new/'tools/build_j2_laboratory.py')
 assert oldbuilder.split('    texts=')[0]==builder.split('    texts=')[0]
 assert oldbuilder.split("    (assets/'review.html').write_text(body)")[1]==builder.split("    (assets/'review.html').write_text(body)")[1]
 app=text(new/'web/app.js');r3app=text(old/'web/app.js')
 for start,end in [('function selectJ2(id){','function route(){'),('function route(){','function element('),('function cancel(','function calculationError('),('function startRun(','function simulate('),('function simulate(','function axisRange('),('async function importRun(','function describeExperiment(')]:
  if end not in app or end not in r3app:
   if start=='function route(){':continue
   raise AssertionError(end)
  assert app[app.index(start):app.index(end,app.index(start))]==r3app[r3app.index(start):r3app.index(end,r3app.index(start))],start
 base=json.loads(subprocess.check_output(['git','show',f['release_base']+':catalogue/manifest.json'],cwd=ROOT));catalogue=read(new/'catalogue/manifest.json');catalogue['models']=[e for e in catalogue['models'] if e['id']!='j2-linear-isotropic-hardening-be'];assert catalogue==base
 assert "if(timedRoute){location.href=timedRoute;return;}dialog.close();if(selectJ2(entry.id))" in app
 build=text(new/'tools/build_web.py')
 for checker in ['test_power_creep_package.mjs','test_j2_laboratory_package.mjs']:assert "str(ROOT/'tools/"+checker+"'),str(dest)],check=True" in build
 result=dict(passed=True,verdict='accept exact frozen merged integration source and review embedding',source_files=len(f['files']),J2_numerical_assessor_unchanged=True,J2_ownership_continuations_unchanged=True,other_catalogue_entries_semantically_unchanged=True,reviewer_compiled_calls=0,package_checked=False)
 if site:
  manifest=read(site/'material-point-j2/package-manifest.json')
  for p,h in manifest.items():assert sha(site/p)==h,p
  for p in ['web/app.js','web/j2-laboratory.mjs','web/j2-contract.mjs']:assert sha(site/pathlib.Path(p).name)==f['files'][p]
  oldmanifest=read(REVIEW.parent/'package-manifest-r3.json')
  for p,h in oldmanifest.items():
   if p!='material-point-j2/review.html':assert sha(site/p)==h,p
  for p in ['j2.html','sls.html','recorded.html','publications.html']:assert not (site/p).exists(),p
  assert (site/'power-creep.html').is_file()
  page=text(site/'material-point-j2/review.html');match=re.search(r'<h1 id="interface-review">.*?</h1><pre>(.*?)</pre>',page,re.S);assert match
  assert html.unescape(match[1])==text(REVIEW/'README.md')
  assert sha(site/'index.html')==sha(HERE/'stage/web/index.html')
  oldfreeze=read(REVIEW.parent/'interface-freeze-r3.json')
  for source,target in [('atlas.js','atlas.js'),('atlas.wasm','atlas.wasm'),('generated/models.json','models.json')]:assert sha(site/target)==oldfreeze['reused_engine']['/private/tmp/atlas-j2-delivery-v1/root-wasm/'+source]
  log=text(REVIEW.parent/'package-final.log');reports=[]
  for m in re.finditer(r'(?m)^\{',log):
   obj=json.JSONDecoder().raw_decode(log[m.start():])[0]
   if obj.get('calls')==327:reports.append(obj)
  assert len(reports)==1 and reports[0]['passed'] and reports[0]['stateComparisons']==1264 and reports[0]['tangentComparisons']==192
  assert reports[0]['identity']==read(site/'material-point-j2/identity.json')
  assert 'Packaged '+str(site) in log
  result.update(package_checked=True,public_exact_accepted_review=True,unchanged_J2_assets=9,unchanged_root_assets=3,normal_builder_J2_calls=327)
 return result
if __name__=='__main__':print(json.dumps(run(pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else None),indent=2))
