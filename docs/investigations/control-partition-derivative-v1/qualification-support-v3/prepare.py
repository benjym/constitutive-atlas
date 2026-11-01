"""One-shot exact isolated copy and explicitly authorized literal/test restoration."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;ROOT=D.parents[3];PRIOR=D.parent/'qualification-support-v2';OLD=Path('/private/tmp/atlas-control-partition-support-v1/source');NEW=Path('/private/tmp/atlas-control-partition-support-v2/source');BASE='3873a48b256ed37cbc78378ee6b41d73139676f8'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((PRIOR/'support-source-freeze-v3.json').read_text());assert len(freeze['files'])==2611
actual={p.relative_to(OLD).as_posix():sha(p)for p in OLD.rglob('*')if p.is_file()};assert actual==freeze['files']
assert not NEW.exists(),'preserve isolated tree'
NEW.mkdir(parents=True)
for name,digest in actual.items():
 p=NEW/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/name,p);assert sha(p)==digest
paths=['docs/admission/power-creep-approved-v1/approval.json','docs/ingestion/power-creep-itasca900/manifest.json','docs/ingestion/power-creep-itasca900/review-v1/manifest.json','tests/test_j2_main_routing.mjs'];changes=[]
for name in paths:
 data=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT);before=sha(NEW/name)if(NEW/name).exists()else None
 target=NEW/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 changes.append(dict(path=name,base=BASE,before_sha256=before,after_sha256=sha(target),authorization='coordinator explicit additive support-v3 literal restoration / latest routing-test overlay'))
assert changes[1]['after_sha256'].startswith('dc9001e7')and changes[2]['after_sha256'].startswith('0569adee')
for name,digest in actual.items():assert sha(OLD/name)==digest
files={p.relative_to(NEW).as_posix():sha(p)for p in NEW.rglob('*')if p.is_file()}
assert [n for n,h in actual.items()if files[n]!=h]==['tests/test_j2_main_routing.mjs']
(D/'preparation.json').write_text(json.dumps(dict(identity='generic-qualified-support-correction-v3',prior_manifest_sha256=sha(PRIOR/'manifest.json'),prior_source_freeze_sha256=sha(PRIOR/'support-source-freeze-v3.json'),old_source=str(OLD),new_source=str(NEW),base=BASE,changes=changes,old_files_preserved_and_verified=2611,new_files=len(files),compiled_calls=0,builds=0),indent=2)+'\n')
(D/'source-freeze.json').write_text(json.dumps(dict(identity='generic-control-support-source-v3',source_directory=str(NEW),files=files,file_count=len(files),parent_freeze_sha256=sha(PRIOR/'support-source-freeze-v3.json'),qualification_ready=False),indent=2,sort_keys=True)+'\n')
print(json.dumps({'files':len(files),'changes':changes},indent=2))
