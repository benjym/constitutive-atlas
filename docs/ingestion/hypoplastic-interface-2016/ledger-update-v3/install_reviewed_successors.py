"""Guarded coordinator-only source installation proposal; defaults to read-only check.
Run --apply only after separate exact-evidence review. No Git/build/browser calls.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,tempfile
sys.dont_write_bytecode=True
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');OUT=Path(__file__).resolve().parent
P=argparse.ArgumentParser(description=__doc__);P.add_argument('--apply',action='store_true');a=P.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,message):
 if not ok:raise ValueError(message)
plan=json.loads((OUT/'install-plan.json').read_text());proposal=json.loads((OUT/'preservation-proposal.json').read_text())
for name,h in plan['proposal_input_pins'].items():need(sha(OUT/name)==h,'Proposal drift: '+name)
for name,h in plan['evidence_input_pins'].items():need(sha(ROOT/name)==h,'Evidence drift: '+name)
for name,h in proposal['live_ledger_pins'].items():need(sha(ROOT/name)==h,'Predecessor ledger drift: '+name)
for consumer in proposal['consumers']:need(sha(ROOT/consumer['path'])==consumer['sha256'],'Consumer drift: '+consumer['path'])
for item in proposal['sidecar_proposals']:
 target=ROOT/item['path'];need(target.exists()==item['exists_now'],'Sidecar existence drift: '+item['path'])
 if target.exists():need(sha(target)==item['old_sha256'],'Sidecar drift: '+item['path'])
 for name,h in item['documents'].items():need(sha(ROOT/name)==h,'Sibling receipt drift: '+name)
 siblings={p.relative_to(ROOT).as_posix() for p in target.parent.glob('*.json') if p.name!='source-archive-map.json'}
 need(siblings.issubset(item['documents']),'Unregistered new sibling receipt: '+item['path'])
for item in proposal['archive_first_operations']:
 need(sha(ROOT/item['source'])==item['sha256'],'Archive source drift')
 target=ROOT/item['canonical_target']
 if target.exists():need(sha(target)==item['sha256'],'Existing canonical archive differs')
if not a.apply:
 print(json.dumps({'status':'read-only installation preflight passed','actual_live_changes':False,'instruction':'Independent exact-evidence acceptance and coordinator action required before --apply.'}));sys.exit(0)
# Archives always precede any sidecar or ledger replacement. Never overwrite archives.
for item in proposal['archive_first_operations']:
 source=ROOT/item['source'];target=ROOT/item['canonical_target'];target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():
  with target.open('xb') as f:f.write(source.read_bytes());f.flush();os.fsync(f.fileno())
 need(sha(target)==item['sha256'],'Archive verification failed')
def atomic(target,data,expected):
 need((sha(target) if target.exists() else None)==expected,'Target changed immediately before replacement: '+str(target))
 fd,tmp=tempfile.mkstemp(prefix='.ledger-successor-',dir=target.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.chmod(tmp,0o644);os.replace(tmp,target)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
for item in proposal['sidecar_proposals']:atomic(ROOT/item['path'],(ROOT/item['proposal_file']).read_bytes(),item['old_sha256'])
sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
def check_receipts():
 count=0
 for consumer in proposal['consumers']:
  for name in consumer['documents']:
   h=proposal['live_ledger_pins'][name];need(sha(checked_receipt(ROOT,consumer['path'],name,h))==h,'Old receipt no longer resolves');count+=1
 return count
check_receipts()
for name in proposal['live_ledger_pins']:
 draft=OUT/(Path(name).stem+'.draft.md');atomic(ROOT/name,draft.read_bytes(),proposal['live_ledger_pins'][name])
count=check_receipts()
print(json.dumps({'status':'installed reviewed successor ledgers with predecessor archives','old_receipt_pairs':count,'new_ledgers':{n:sha(ROOT/n) for n in proposal['live_ledger_pins']},'git_build_material_browser_calls':0},indent=2))
