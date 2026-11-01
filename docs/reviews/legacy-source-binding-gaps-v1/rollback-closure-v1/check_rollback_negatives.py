from pathlib import Path
import json,sys,hashlib
root=Path('/Users/bmar5496/code/constitutive-atlas');p=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');mini=(p/'qualification-v1/repository').resolve();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
plan=json.loads((p/'PLAN.json').read_text());q=p/'qualification-v1';assert json.loads((q/'RESULT.json').read_text())['pass'];after=json.loads((q/'after.json').read_text());rollback=json.loads((q/'rollback.json').read_text());targets={r['file'] for r in plan['mutations']};selected=[]
for target in ['catalogue/investigations/solver-rollback-v1/'+x+'source-archive-map.json' for x in ['', 'native/','wasm/']]:
 selected.append(next(r for r in after if r['pass_'] and r['target']==target and r['selected']!=target and r['document'] not in targets))
rows=[]
for r in rollback+selected:
 doc=r['document'];path=r['target'];h=r['expected_digest'];archive=checked_receipt(mini,doc,path,h);original=archive.read_bytes();live=mini/path;live.parent.mkdir(parents=True,exist_ok=True);previous=live.read_bytes() if live.exists() else None;live.write_bytes(original)
 for mode in ['corrupt','missing']:
  if mode=='corrupt':archive.write_bytes(original+b'\n# deliberately corrupt isolated fixture\n')
  else:archive.unlink()
  try:checked_receipt(mini,doc,path,h)
  except ValueError as e:rows.append({'document':doc,'target_file':path,'case':mode+'-archive-no-live-fallback','pass':True,'error':str(e).replace(str(mini),'<fixture>')})
  else:raise AssertionError('accepted '+mode)
  archive.write_bytes(original)
 if previous is None:live.unlink()
 else:live.write_bytes(previous)
 raw=(mini/doc).read_bytes();(mini/doc).write_bytes(raw+b'\n')
 try:checked_receipt(mini,doc,path,h)
 except ValueError as e:rows.append({'document':doc,'target_file':path,'case':'modified-original-document','pass':True,'error':str(e).replace(str(mini),'<fixture>')})
 else:raise AssertionError('accepted modified original document')
 (mini/doc).write_bytes(raw)
for r in plan['mutations']:assert hashlib.sha256((mini/r['file']).read_bytes()).hexdigest()==r['after_digest']
for r in rollback+selected:checked_receipt(mini,r['document'],r['target'],r['expected_digest'])
result={'pass':True,'cases':len(rows),'checks':rows,'scope':'Six actual proposed source/map redirect consumers, corrupt/missing selected archive rejected despite matching live bytes, changed original document rejected, all candidate maps restored and positives rechecked. Isolated fixture only.'};(q/'NEGATIVES.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':True,'cases':len(rows)}))
