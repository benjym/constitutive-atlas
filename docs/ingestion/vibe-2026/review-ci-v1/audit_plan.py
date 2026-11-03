"""Independent portable-plan review: stdlib only, no material imports."""
from pathlib import Path
import json,hashlib,copy,sys
ROOT=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
OLD=ROOT/'docs/ingestion/vibe-2026/numerical-qualification-v1/plan-v2.json'
NEW=Path(sys.argv[1]);old=json.loads(OLD.read_text());new=json.loads(NEW.read_text());checks=[]
def check(x,label):
 if not x:raise AssertionError(label)
 checks.append(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check(sha(OLD)=='b70950d1981602d9bc053f708214fde7c93efda1dde97420b10295c015d890da','original frozen plan SHA')
restored=copy.deepcopy(new);restored['identity']=old['identity'];changed=[]
check(len(old['source_files'])==len(new['source_files']),'all source pins retained')
for i,(a,b) in enumerate(zip(old['source_files'],new['source_files'])):
 check(a['sha256']==b['sha256'],'source pin unchanged '+str(i))
 p=Path(b['path']);check(not p.is_absolute() and '..' not in p.parts,'portable bounded source path '+str(i))
 check(sha(ROOT/p)==b['sha256'],'actual repo source bytes '+str(i))
 expected=a['path'].removeprefix('/Users/bmar5496/code/constitutive-atlas/')
 check(b['path']==expected,'only exact repository prefix removed '+str(i))
 restored['source_files'][i]['path']=a['path']
 if a['path']!=b['path']:changed.append(dict(old=a['path'],new=b['path']))
check(restored==old,'reverse path/identity restoration exact entire original plan')
for key,n in [('points',32),('histories',8),('invalid_cases',7)]:
 check(len(new[key])==n,'retained complete '+key)
 check(new[key]==old[key],'exact original '+key+' including cases inputs expected values/settings')
for key in ['bounds','settings','refinement_max_steps']:
 check(new[key]==old[key],'unchanged '+key)
report=dict(identity='independent-portable-plan-audit-v1',checks=checks,count=len(checks),changes=changed,old_sha256=sha(OLD),new_sha256=sha(NEW),compiled_calls=0)
(Path(__file__).resolve().parent/'plan-results.json').write_text(json.dumps(report,indent=2)+'\n')
print('Portable plan source checks:',len(checks))
