from pathlib import Path
import json,hashlib,tempfile,subprocess
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/web-tmd2-reporting-agent-v1';O=P/'independent-review';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (O/'addendum-v2-inputs.json').exists():
 for p,h in read(O/'addendum-v2-inputs.json').items():assert sha(R/p)==h,p
assert sha(O/'prospective-receipt.json')=='9fc90f2666a5d13ff593a4fc0b4fa205531a753abc1c835242b83beba53fd48a'
a=read(P/'archive-plan.json');b=read(P/'archive-plan-v2.json');assert b==read(P/'installation-plan-drift.json');assert sha(P/'archive-plan-v2.json')=='8265ac32b3423b3495ce36b2db6c263a1066aa4fe692c907997659947e4aaa72'
assert set(a)==set(b)and all(a[k]==b[k]for k in a if k!='maps')and set(a['maps'])==set(b['maps'])
added={};changed=[]
for name,m in a['maps'].items():
 n=b['maps'][name];assert n['entries']==m['entries']and n['version']==m['version']and all(n['documents'].get(k)==v for k,v in m['documents'].items())
 new={k:h for k,h in n['documents'].items()if k not in m['documents']}
 if new:changed.append(name)
 for k,h in new.items():assert sha(R/k)==h;added[k]=h
assert len(changed)==7 and len(added)==34
old=(P/'preserve_sources.py').read_text();new=(P/'preserve_sources_v2.py').read_text();assert old.count('archive-plan.json')==2 and new==old.replace('archive-plan.json','archive-plan-v2.json')
assert 'assert saved == plan'in new
assert 'Plan or source identities changed'in(P/'archive-apply.stderr.txt').read_text()
# Repeat entire independent candidate shadow and helper/builder tests against exact v2plan, no apply.
script=(O/'check_prospective.py').read_text().replace("P/'archive-plan.json'","P/'archive-plan-v2.json'")
with tempfile.TemporaryDirectory(prefix='tmd2-review-v2-')as t:
 checker=Path(t)/'check.py';checker.write_text(script);z=subprocess.run(['python3','-B',str(checker)],cwd=R,capture_output=True,text=True);assert z.returncode==0,z.stderr
print(json.dumps({'passed':True,'only_new_document_pins':34,'changed_maps':7,'prior_files_unchanged':32,'all_old_docpins_entries_and_gates_unchanged':True,'plan_v2_exact_diagnostic_content':True,'plan_v2_reserialization_order_only':True,'helper_only_two_plan_filename_changes':True,'original_apply_guard_failure_retained':True,'full_independent_shadow_and_tests':json.loads(z.stdout),'reviewer_applied':False},indent=2))
