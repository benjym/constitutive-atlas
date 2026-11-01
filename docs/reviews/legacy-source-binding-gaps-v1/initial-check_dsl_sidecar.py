from pathlib import Path
import sys,json,hashlib,tempfile,shutil
root=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
p=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1');plan=json.loads((p/'DSL_PLAN.json').read_text());raw=(p/'proposed-dsl-source-archive-map.json').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)==plan['operation']['after_sha256'];checks=[]
with tempfile.TemporaryDirectory(prefix='atlas-dsl-binding-') as d:
 mini=Path(d);doc=plan['original_document'];files=[doc['path']]+[x['archived_path'] for x in plan['sources']]
 for rel in files:
  dest=mini/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
 sidecar=mini/plan['operation']['path'];sidecar.write_bytes(raw)
 for e in plan['sources']:
  resolved=checked_receipt(mini,doc['path'],e['original_path'],e['sha256']);assert resolved==mini/e['archived_path'];checks.append({'kind':'exact-positive','source':e['original_path'],'pass':True})
  # A matching live file must not rescue a corrupt/missing selected archive.
  live=mini/e['original_path'];live.parent.mkdir(parents=True,exist_ok=True);original=resolved.read_bytes();live.write_bytes(original)
  for mode in ['corrupt','missing']:
   if mode=='corrupt':resolved.write_bytes(original+b'\n# corrupt\n')
   else:resolved.unlink()
   try:checked_receipt(mini,doc['path'],e['original_path'],e['sha256'])
   except ValueError as ex:checks.append({'kind':mode+'-archive-no-live-fallback','source':e['original_path'],'pass':True,'error':str(ex).replace(d,'<fixture>')})
   else:raise AssertionError(mode+' accepted')
   resolved.write_bytes(original)
  before=(mini/doc['path']).read_bytes();(mini/doc['path']).write_bytes(before+b'\n')
  try:checked_receipt(mini,doc['path'],e['original_path'],e['sha256'])
  except ValueError as ex:checks.append({'kind':'changed-document-rejected','source':e['original_path'],'pass':True,'error':str(ex)})
  else:raise AssertionError('changed document accepted')
  (mini/doc['path']).write_bytes(before)
result={'pass':True,'production_verifier_sha256':sha((root/'atlas/evidence.py').read_bytes()),'plan_sha256':sha((p/'DSL_PLAN.json').read_bytes()),'checks':checks};(p/'DSL_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':True,'checks':len(checks)}))
