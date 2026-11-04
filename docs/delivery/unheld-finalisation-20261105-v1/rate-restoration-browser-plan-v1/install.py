"""Validate by default. Coordinator alone may --install after independent review."""
from pathlib import Path
import hashlib,json,sys
O=Path(__file__).resolve().parent

def validate(plan):
 root=Path(plan['output_directory'])
 if not root.is_absolute() or root.exists() or root.is_symlink():raise ValueError('new absolute output directory required')
 if any(p.is_symlink() for p in (root,*root.parents)):raise ValueError('symlink output ancestor')
 rows=plan['scripts']+plan['input_fixtures'];destinations=set();payload=[]
 for row in rows:
  src=Path(row.get('path',row.get('source')));dst=Path(row['install_path'])
  if not src.is_absolute() or not src.is_file() or src.is_symlink() or any(p.is_symlink() for p in src.parents):raise ValueError('unsafe or missing input')
  if dst.parent!=root or dst.name in ('','.', '..') or dst in destinations:raise ValueError('destination escape/duplicate')
  data=src.read_bytes()
  if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('input hash mismatch')
  destinations.add(dst);payload.append((dst,data))
 if set(plan['execution_order'])!={Path(r['install_path']).name for r in plan['scripts']} or len(plan['execution_order'])!=len(plan['scripts']):raise ValueError('incomplete execution order')
 return root,payload

if __name__=='__main__':
 if sys.argv[1:] not in ([],['--install']):raise SystemExit('usage: install.py [--install]')
 root,payload=validate(json.loads((O/'plan.json').read_text()))
 if sys.argv[1:]==['--install']:
  root.mkdir(parents=True,exist_ok=False)
  for dst,data in payload:
   with dst.open('xb')as stream:stream.write(data)
 print(json.dumps({'status':'installed'if sys.argv[1:]else'validated-only','members':len(payload),'output_directory':str(root)}))
