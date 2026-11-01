"""Apply independently accepted prospective maps and exact runtime after drift checks."""
from pathlib import Path
import json,hashlib,shutil
r=Path(__file__).resolve().parents[4];p=Path(__file__).parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
plan=json.loads((p/'tracking-preservation-v1/preservation-plan.json').read_text());proposal=json.loads((p/'tracking-proposal-freeze-v1.json').read_text());base=json.loads((p/'tracking-base-preflight-v1.json').read_text())['existing_destination_bases']
out=p/'tracking-installed-v1.json';assert not out.exists()
# Reviewer receipts are supplied and verified by coordinator before invoking.
assert (p/'tracking-independent-review/REVIEW_V1.md').is_file()
for n,h in plan['document_pins'].items():assert sha(r/n)==h,n
for n,row in plan['planned_sidecars'].items():
 f=r/n;assert (sha(f) if f.exists() else None)==row['original_sha256'],n
 assert sha(r/row['proposed_path'])==row['proposed_sha256'],n
for row in plan['bindings']:assert sha(r/row['archived_path'])==row['sha256']
for n,h in base.items():assert sha(r/n)==h,n
installed={}
for n,h in proposal['files'].items():
 f=r/n;assert sha(f)==h,n;dest=f.relative_to(p/'tracking-proposed-v1').as_posix();assert dest in base or not (r/dest).exists(),dest;installed[dest]=h
assert len(installed)==2
# Preserve evidence first, recheck original documents, then install exact bytes.
for n,row in plan['planned_sidecars'].items():
 f=r/n;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/row['proposed_path'],f);assert sha(f)==row['proposed_sha256']
for n,h in plan['document_pins'].items():assert sha(r/n)==h,n
for n,h in base.items():assert sha(r/n)==h,n
for n,h in installed.items():
 f=r/n;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/'tracking-proposed-v1'/n,f);assert sha(f)==h
out.write_text(json.dumps({'status':'installed exact reviewed2trackingparagraphs after reviewed preservation','files':installed,'preservation_plan_sha256':sha(p/'tracking-preservation-v1/preservation-plan.json'),'proposal_sha256':sha(p/'tracking-proposal-freeze-v1.json'),'documents_unchanged':True},indent=2)+'\n');print('Installed2trackingparagraphs;2sidecars;originaldocumentsunchanged')
