from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
Q='7715103ecca3ce163d43de1d4d7aa424867dc4bb';I='be412bdc5f70fd7d47ff9ef4563f71d74f532728'
cache={}
def get(c,n):
 if (c,n) not in cache:
  x=subprocess.run(['git','show',c+':'+n],cwd=R,capture_output=True);cache[c,n]=x.stdout if x.returncode==0 else None
 return cache[c,n]
def put(c,n):
 if Path(n).is_absolute() or '..' in Path(n).parts:return
 p=O/c[:8]/n
 if p.exists():return
 b=get(c,n)
 if b is not None:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def outcome(root,z):
 try:p=checked_receipt(root,z['document'],z['original_path'],z['sha256']);return {'ok':True,'resolved':p.relative_to(root).as_posix()}
 except Exception as e:return {'ok':False,'error':str(e).replace(str(root),'<ROOT>')}
x=json.loads((O/'CONSUMER-CHECK.json').read_text());rows=[];newbreaks=[]
for z in x['changed_target_pairs']:
 row={**z,'parents':{}}
 for c in [Q,I]:
  if get(c,z['document']) is None:continue
  root=O/c[:8];put(c,z['document']);put(c,z['original_path']);side=(Path(z['document']).parent/'source-archive-map.json').as_posix();put(c,side)
  if (root/side).exists():
   m=json.loads((root/side).read_text())
   for e in m.get('entries',[]):
    if e.get('original_path')==z['original_path'] and e.get('sha256')==z['sha256']:put(c,e['archived_path'])
  row['parents'][c]=outcome(root,z)
  if row['parents'][c]['ok'] and not z['current']['ok']:newbreaks.append({'parent':c,**z})
 rows.append(row)
(O/'PARENT-OUTCOMES.json').write_text(json.dumps({'rows':rows,'before_pass_current_fail':newbreaks},indent=2)+'\n');print('rows',len(rows),'beforepassnowfail',len(newbreaks))
for z in newbreaks:print(z['parent'][:8],z['document'],z['original_path'])
