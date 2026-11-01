from pathlib import Path
import json,hashlib,sys,subprocess,tempfile,importlib.util,unittest,io
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/web-tmd2-reporting-agent-v1';O=P/'independent-review';sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (O/'inputs.json').exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
plan=read(P/'archive-plan.json');scan=read(P/'prior-references.json');assert sha(R/'atlas/evidence.py')==scan['checked_receipt_source_sha256']
assert len(plan['maps'])==86 and len(plan['redirected_pairs'])==201 and len(plan['affected_secondary'])==1600
for p,h in plan['prior'].items():assert sha(R/p)==h,p
for p,h in plan['unchanged_documents'].items():assert sha(R/p)==h,p
for p,m in plan['maps'].items():
 if(R/p).exists():
  old=read(R/p);assert all(m['documents'].get(k)==v for k,v in old['documents'].items())and all(e in m['entries']for e in old['entries'])
 def pairs():return [(e['original_path'],e['sha256'])for e in m['entries']]
 assert len(pairs())==len(set(pairs()))
def check(root,row):
 if all(loc['shape']=='original_path-object'for loc in row['locations']):
  choices=[root/row['original_path'],root/'catalogue/source-snapshots'/row['sha256']/row['original_path']];assert any(p.is_file()and sha(p)==row['sha256']for p in choices)
 else:assert sha(checked_receipt(root,row['document'],row['original_path'],row['sha256']))==row['sha256']
rows=plan['redirected_pairs']+plan['affected_secondary']
for row in rows:check(R,row)
with tempfile.TemporaryDirectory(prefix='independent-tmd2-shadow-')as t:
 shadow=Path(t)
 def put(p,data):
  dest=shadow/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 for p,h in plan['prior'].items():put(str(Path('catalogue/source-snapshots')/h/p),(R/p).read_bytes())
 for row in rows:
  for p in [row['document'],row['original_path'],row.get('resolved_path')]:
   if p and(R/p).is_file():put(p,(R/p).read_bytes())
  side=str(Path(row['document']).parent/'source-archive-map.json')
  if(R/side).exists():put(side,(R/side).read_bytes())
 for p,m in plan['maps'].items():put(p,(json.dumps(m,indent=2)+'\n').encode())
 for p in ['tools/build_benchmark.py','tests/test_web_benchmark.py','web/index.html']:put(p,(P/'candidate'/p).read_bytes())
 for row in rows:check(shadow,row)
# Focused helper mutation/privacy tests, no engines or builds.
z=subprocess.run(['python3','-B','-m','unittest','discover','-s','tests','-p','test_web_tmd2_review.py'],cwd=R,capture_output=True,text=True);assert z.returncode==0,z.stderr
# Execute candidate builder tests with root injected to actual read-only source fixtures.
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
candidate=load(P/'candidate/tools/build_benchmark.py','candidate_benchmark');candidate.ROOT=R;candidate.bundle.__defaults__=(R,)
sys.modules['tools.build_benchmark']=candidate
ct=load(P/'candidate/tests/test_web_benchmark.py','candidate_tests');out=io.StringIO();res=unittest.TextTestRunner(stream=out,verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(ct));assert res.wasSuccessful(),out.getvalue()
from tools.build_tmd2_review import projection,MANIFEST_SHA256
review=R/'docs/benchmarks/kfs-tmd2-reporting-agent-v1';assert sha(review/'manifest.json')==MANIFEST_SHA256
assets={name:(R/candidate.PACKET/source).read_bytes()for name,source in candidate.FILES.items()};modelhash='83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86';published,section=projection(R,assets,modelhash)
decision=read(review/'decision.json');assert published['review/decision.json']==(review/'decision.json').read_bytes()and published['review/review.md']==(review/'README.md').read_bytes()
assert set(published)=={'review/decision.json','review/review.md','review/review.html'}
from html import escape
for q in decision['remaining_qualifications']:assert escape(q)in section
assert all(q['outcome']=='accept-with-stated-qualifications'for q in decision['questions'])
print(json.dumps({'passed':True,'live_source_pairs':len([r for r in scan['primary_references']if r['resolution']=='live']),'prior_files':len(plan['prior']),'maps_additive':86,'unchanged_receipt_documents':len(plan['unchanged_documents']),'shadow_direct_pairs':201,'shadow_secondary_pairs':1600,'preexisting_unresolved_primary':plan['preexisting_unresolved_primary'],'focused_helper_tests':5,'candidate_builder_tests':res.testsRun,'exact_review_assets':3,'six_questions':6,'public_projection_only':True,'reviewer_compiled_calls':0,'root_installation_reviewed':False,'browser_reviewed':False},indent=2))
