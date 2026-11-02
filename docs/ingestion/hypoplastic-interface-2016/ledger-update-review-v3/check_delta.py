"""Source/hash delta review only. Does not open/extract archive contents or apply."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';A=P/'ledger-update-v2';B=P/'ledger-update-v3';OUT=Path(__file__).parent
read=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert sha(A/'manifest.json')=='fd195c49a2b6ec4c2540f3436af2ec56f15830e6c73f99c79244dbcabc765d3d'
assert sha(B/'manifest.json')=='84b89699d4fca1e2d35b28cbb45cb1ca74ad6cbd2dd5710cecd54237f00cb8fd'
for directory in [A,B]:
 for n,h in read(directory/'manifest.json')['files'].items():assert sha(directory/n)==h
assert (A/'install_reviewed_successors.py').read_bytes()==(B/'install_reviewed_successors.py').read_bytes()
assert (A/'preservation-proposal.json').read_text()==(B/'preservation-proposal.json').read_text().replace('ledger-update-v3/','ledger-update-v2/')
for name,head,tail in [('DELIVERY.draft.md','Retain current release-v2/, successful site-v2/, failed site-v1/','\n## Ledger preservation and next action'),('CHECKLIST.draft.md','- [ ] E8 cleanup:','\n- [ ] Close final ledger/board')]:
 old=(A/name).read_text();new=(B/name).read_text()
 if name.startswith('DELIVERY'):newhead='The failed site-v1/ and source-guard-checks-v1/'
 else:newhead='- [X] Bounded cleanup:'
 assert old.split(head)[0]==new.split(newhead)[0] and old.split(tail)[1]==new.split(tail)[1]
plan=read(B/'install-plan.json')
for n,h in plan['proposal_input_pins'].items():assert sha(B/n)==h
for n,h in plan['evidence_input_pins'].items():assert sha(ROOT/n)==h
c=P/'cleanup-v3';creation=read(c/'archive-creation.json');stream=read(c/'archive-stream-verification.json');recovery=read(c/'recovery-drill.json');consumers=read(c/'consumer-check-before-removal.json');removal=read(c/'removal-receipt.json')
archive=Path(creation['archive']);assert archive.stat().st_size==243000472 and sha(archive)==creation['sha256']==recovery['archive_sha256']==removal['archive_sha256']=='a70787d63a3f4cf026dfd612911d8cdd68b48096aaa570c0eab2ea4301c35fe8'
assert creation['members']==stream['entries']==recovery['entries']==1546
assert sha(ROOT/creation['inventory'])==creation['inventory_sha256']==stream['recovery_inventory_sha256']
assert recovery['exact_bytes_modes_nanosecond_mtimes'] and recovery['recovery_disposable_removed']
assert consumers['time']<=removal['time'] and len(consumers['checks'])==2
for check in consumers['checks']:assert check['process_matches']==[] and check['lsof_exit']==1 and check['lsof_stdout']==check['lsof_stderr']=='' and check['path'] in removal['removed']
assert removal['status']=='completed' and removal['observed_free_increase']==1105551360
for n in removal['removed']:assert not Path(n).exists()
for n in ['release-v2','site-v2','source','native','wasm','em-cache']:assert (Path('/private/tmp/atlas-interface2016-delivery-v1')/n).exists()
obs=subprocess.run(['python3','-B',str(B/'install_reviewed_successors.py')],check=True,capture_output=True,text=True);assert json.loads(obs.stdout)['actual_live_changes'] is False
(OUT/'read-only-preflight.json').write_text(obs.stdout)
result={'passed':True,'v2_manifest_members_unchanged':len(read(A/'manifest.json')['files']),'v3_manifest_members_exact':len(read(B/'manifest.json')['files']),'preservation_logic_unchanged':True,'draft_changes_cleanup_only':True,'archive_sha256_verified':creation['sha256'],'archive_bytes':archive.stat().st_size,'saved_recovery_entries':1546,'observed_free_increase':1105551360,'installer_read_only_preflight':True,'archive_extraction_apply_material_browser_remote_calls':0}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
