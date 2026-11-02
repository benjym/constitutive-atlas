from pathlib import Path
import hashlib,json,subprocess,re,sys
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent;Q='7715103ecca3ce163d43de1d4d7aa424867dc4bb';I='be412bdc5f70fd7d47ff9ef4563f71d74f532728';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R,stderr=subprocess.DEVNULL)
def get(c,n):
 try:return git('show',c+':'+n)
 except subprocess.CalledProcessError:return None
x=json.loads((R/'docs/ingestion/bingham-comsol63/live-release-v1/MERGE-PREPARATION.json').read_text());old={}
for n in x['changed_paths']:
 b=get(Q,n)
 if b is not None and b!=(R/n).read_bytes():old[n]=sha(b)
valid=lambda v:isinstance(v,str) and bool(re.fullmatch('[0-9a-f]{64}',v))
def pairs(n):
 if isinstance(n,dict):
  for k,v in n.items():
   if valid(v) and ('/' in k or '.' in k):yield k,v
  if isinstance(n.get('path'),str):
   for k in ['hash','sha256']:
    if valid(n.get(k)):yield n['path'],n[k]
  for v in n.values():yield from pairs(v)
 elif isinstance(n,list):
  for v in n:yield from pairs(v)
rows=[];stale=[];mapcount=0;scanned=0
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
for folder in ['catalogue','docs','tools','tests','schemas']:
 for p in (R/folder).rglob('*.json'):
  n=p.relative_to(R).as_posix()
  if 'live-merge-review-v1' in p.parts:continue
  scanned+=1
  if p.name=='source-archive-map.json':
   try:m=json.loads(p.read_text())
   except (ValueError,UnicodeError):continue
   mapcount+=1
   for d,h in m.get('documents',{}).items():
    if old.get(d)==h and sha((R/d).read_bytes())!=h:stale.append({'map':n,'document':d,'expected':h})
  b=p.read_bytes()
  if not any(h.encode() in b for h in old.values()):continue
  try:node=json.loads(b)
  except ValueError:continue
  for target,h in sorted(set(pairs(node))):
   if old.get(target)!=h:continue
   # Pure owner classification mirrors accepted immutable copy exclusions.
   excluded=any(part in {'source-snapshots','before','candidates','installation-candidates','consumer-context','receipt-bytes','context','snapshots','source-snapshot','frozen-sources','proposal-inputs'} or 'preparation-v' in part or 'final-imported-context-v1'==part for part in p.parts)
   try:v=checked_receipt(R,n,target,h);result={'ok':True,'resolved':v.relative_to(R).as_posix()}
   except Exception as e:result={'ok':False,'error':str(e).replace(str(R),'<ROOT>')}
   rows.append({'document':n,'original_path':target,'sha256':h,'immutable_copied_namespace':excluded,'current':result})
(O/'CONSUMER-CHECK.json').write_text(json.dumps({'scanned_json_files':scanned,'changed_existing_qualified_paths':old,'maps_scanned':mapcount,'potential_stale_docpins':stale,'changed_target_pairs':rows},indent=2)+'\n');print('json',scanned,'maps',mapcount,'oldtargets',len(old),'pairs',len(rows),'potential_stale_docpins',len(stale));print(json.dumps(stale[:3],indent=2));print('noncopy failing pairs',sum(not v['immutable_copied_namespace'] and not v['current']['ok'] for v in rows))
