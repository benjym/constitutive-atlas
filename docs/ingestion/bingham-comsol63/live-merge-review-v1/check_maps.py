from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent
Q='7715103ecca3ce163d43de1d4d7aa424867dc4bb';I='be412bdc5f70fd7d47ff9ef4563f71d74f532728';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def show(c,n):return git('show',c+':'+n)
x=json.loads((R/'docs/ingestion/bingham-comsol63/live-release-v1/MERGE-PREPARATION.json').read_text());rows=[];problems=[]
for n in x['changed_paths']:
 if not n.endswith('/source-archive-map.json') or n.startswith('catalogue/source-snapshots/'):continue
 new=json.loads((R/n).read_text());row={'path':n,'parents':{}}
 for c in [Q,I]:
  try:b=show(c,n)
  except subprocess.CalledProcessError:continue
  old=json.loads(b);lostpins={p:h for p,h in old['documents'].items() if new['documents'].get(p)!=h};lostentries=[e for e in old['entries'] if e not in new['entries']]
  row['parents'][c]={'sha256':sha(b),'lost_pins':lostpins,'lost_entries':lostentries}
  if lostpins or lostentries:problems.append(row)
  for p,h in new['documents'].items():
   if not (R/p).is_file() or sha((R/p).read_bytes())!=h:problems.append({'map':n,'wrong_current_docpin':p,'expected':h})
  for e in new['entries']:
   p=e['archived_path']
   if p!='catalogue/source-snapshots/'+e['sha256']+'/'+e['original_path'] or not (R/p).is_file() or sha((R/p).read_bytes())!=e['sha256']:problems.append({'map':n,'bad_archive':e})
 rows.append(row)
(O/'MAP-CHECK.json').write_text(json.dumps({'maps':rows,'problems':problems},indent=2)+'\n');print('maps',len(rows),'problems',len(problems));print(json.dumps(problems[:3],indent=2))
