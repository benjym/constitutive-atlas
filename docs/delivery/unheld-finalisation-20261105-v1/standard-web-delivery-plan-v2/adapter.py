"""Pure recipe successor and bounded recovery guard; never executes a command."""
from pathlib import Path
import hashlib,importlib.util,json,stat
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'standard-web-delivery-plan-v1'
OLD_SHA='b31cbd5299903175d0ca4d7bb86caa3c00c7acabc0e542442008a8287259b63e'
RECOVERY=Path('/private/tmp/atlas-baseline-delivery-20261105/retained640-sls-v1')
RECEIPT=HERE.parent/'standard-web-retained-sls-recovery-v1.json'
RECEIPT_SHA='3b15e94030c1c486a33fb73026899c3fd87a10d205d378b1765be09e11144585'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def predecessor():
 if digest(OLD/'manifest.json')!=OLD_SHA:raise ValueError('wrong frozen v1manifest')
 for r in json.loads((OLD/'manifest.json').read_text())['files']:
  path=Path(r['path'])
  if path.is_absolute()or'..'in path.parts:raise ValueError('unsafe manifest path')
  q=OLD/path
  if q.is_symlink()or digest(q)!=r['sha256']or q.stat().st_size!=r['size_bytes']:raise ValueError('v1source drift')
 return json.loads((OLD/'retained-auxiliary-roles.json').read_text())
def expected_files():
 role=next(r for r in predecessor()['roles']if r['role']=='sls')
 return {name:dict(row)for name,row in zip(['sls.js','sls.wasm','generated/models.json'],role['assets'],strict=True)}
def validate_recovery(receipt_sha256):
 if receipt_sha256!=RECEIPT_SHA:raise ValueError('exact genuine recoveryreceipt SHA required')
 if RECEIPT.is_symlink()or digest(RECEIPT)!=receipt_sha256:raise ValueError('recoveryreceipt drift')
 document=json.loads(RECEIPT.read_text())
 if not isinstance(document,dict)or document.get('identity')!='exact-live640-SLS-three-file-recovery-v1'or document.get('all_match')is not True or document.get('no_engine_executed')is not True or document.get('directory')!=str(RECOVERY):raise ValueError('genuine exact recoveryreceipt identity required')
 if not RECOVERY.is_dir()or RECOVERY.resolve()!=RECOVERY or any(p.is_symlink()for p in(RECOVERY,*RECOVERY.parents)):raise ValueError('physical recovered directory required')
 expected=expected_files();declared=document.get('files',[])
 if len(declared)!=3 or{r['path']for r in declared}!={str(RECOVERY/n)for n in expected}:raise ValueError('recoveryreceipt namespace mismatch')
 for row in declared:
  name=str(Path(row['path']).relative_to(RECOVERY))
  if row['sha256']!=expected[name]['sha256']or row['bytes']!=expected[name]['bytes']:raise ValueError('recoveryreceipt published identity mismatch')
 files={}
 for p in RECOVERY.rglob('*'):
  if p.is_symlink():raise ValueError('recovered alias')
  mode=p.stat(follow_symlinks=False).st_mode
  if stat.S_ISDIR(mode):continue
  if not stat.S_ISREG(mode):raise ValueError('regular recovered files required')
  files[str(p.relative_to(RECOVERY))]=p
 if set(files)!=set(expected):raise ValueError('exact three-file recovered namespace required')
 for name,p in files.items():
  if digest(p)!=expected[name]['sha256']or p.stat().st_size!=expected[name]['bytes']:raise ValueError('published SLS identity mismatch: '+name)
 return {'receipt':{'path':str(RECEIPT),'sha256':receipt_sha256},'files':{name:{'path':str(files[name]),'sha256':r['sha256'],'bytes':r['bytes']}for name,r in expected.items()},'only_location_changed':True}
def commands(python,node,revision):
 predecessor();spec=importlib.util.spec_from_file_location('_frozen_v1_recipe',OLD/'recipe.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.commands(python,node,revision);op=next(x for x in result['operations']if x['id']=='standard-web-package');argv=op['argv']
 if argv.count('--sls-wasm-dir')!=1:raise ValueError('unique inherited SLS argument required')
 i=argv.index('--sls-wasm-dir')+1;old=argv[i];argv[i]=str(RECOVERY)
 result['SLS_location_successor']={'prior_directory':old,'new_directory':str(RECOVERY),'original_published_hashes_unchanged':True,'recovery_receipt':str(RECEIPT),'recovery_receipt_sha256':RECEIPT_SHA,'coordinator_must_validate_before_finally':True,'source_only_not_receipt_authentication':True}
 return result
if __name__=='__main__':raise SystemExit('No execution: coordinator binds genuine recoveryreceipt, calls validate_recovery before/finally and executes reviewed recipe under unchanged lifecycle.')
