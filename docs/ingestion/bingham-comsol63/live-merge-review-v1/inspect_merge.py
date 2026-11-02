from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent
Q='7715103ecca3ce163d43de1d4d7aa424867dc4bb';I='be412bdc5f70fd7d47ff9ef4563f71d74f532728'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def blob(c,n):return git('show',c+':'+n)
def sha(b):return hashlib.sha256(b).hexdigest()
x=json.loads((R/'docs/ingestion/bingham-comsol63/live-release-v1/MERGE-PREPARATION.json').read_text());changed=x['changed_paths'];checks=[];problems=[]
for n,h in x['current_hashes'].items():assert sha((R/n).read_bytes())==h,n
prod=git('diff','--name-only',Q,'--','atlas','cpp','cmake','web','tools','tests','schemas','models','runtimes','.github','CMakeLists.txt','catalogue/manifest.json','catalogue/approved-models.json').decode().splitlines();assert not prod,prod
mapname='docs/ingestion/barodesy-sand/delivery-v1/release-v3/source-archive-map.json';u=json.loads((R/mapname).read_text())
for c in [Q,I]:
 old=json.loads(blob(c,mapname));assert all(u['documents'].get(n)==h for n,h in old['documents'].items());assert all(e in u['entries'] for e in old['entries'])
board=(R/'IMPLEMENTATION_PLAN.md').read_text();boardchecks={}
for c in [Q,I]:
 old=blob(c,'IMPLEMENTATION_PLAN.md').decode();lines=[l for l in old.splitlines() if 'LIVE-bingham' in l or 'barodesy-sand' in l and ('live-e8-v3' in l or 'live-release-v3' in l)];boardchecks[c]={'selected_rows':len(lines),'all_rows_retained':all(l in board for l in lines)}
for n in changed:
 b=(R/n).read_bytes()
 if n not in ['IMPLEMENTATION_PLAN.md',mapname]:
  try:ib=blob(I,n)
  except subprocess.CalledProcessError:continue
  if b!=ib:problems.append({'path':n,'kind':'not_exact_incoming'})
 if n.startswith('catalogue/source-snapshots/'):
  assert sha(b)==n.split('/')[2],n
 checks.append({'path':n,'sha256':sha(b)})
(O/'STRUCTURAL-CHECK.json').write_text(json.dumps({'current_changed_paths':len(changed),'pins_exact':True,'production_diff_from_qualified':prod,'union_map_preserves_both_parent_documents_and_entries':True,'board_rows':boardchecks,'unexpected_nonconflict_bytes':problems,'files':checks},indent=2)+'\n');print('structural',len(changed),'unexpected',len(problems))
