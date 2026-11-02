"""Create isolated clean-HEAD release input without copying retained gigabytes.
Docs/catalogue immutable inputs share links; any edits must atomically replace,
never overwrite a linked inode. Source/tool/web files are independent copies.
"""
from pathlib import Path
import os,subprocess,json,shutil,time
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
DEST=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2')
assert not DEST.exists()
revision=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
dirty=set(subprocess.check_output(['git','diff','origin/main','--name-only','-z'],cwd=ROOT).decode().strip('\0').split('\0'))
entries=subprocess.check_output(['git','ls-tree','-rz','origin/main'],cwd=ROOT).split(b'\0')
counts={'hardlinks':0,'copies':0,'restored_dirty':0,'symlinks':0};t=time.time()
for entry in entries:
 if not entry:continue
 meta,name=entry.split(b'\t',1);mode,kind,oid=meta.decode().split();name=name.decode();assert kind=='blob'
 target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);source=ROOT/name
 if mode=='120000':
  content=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT);os.symlink(content.decode(),target);counts['symlinks']+=1
 elif name in dirty or not source.is_file():
  target.write_bytes(subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT));counts['restored_dirty']+=1
 elif name.startswith(('docs/','catalogue/')):
  os.link(source,target);counts['hardlinks']+=1
 else:shutil.copyfile(source,target);counts['copies']+=1
 if mode=='100755' and not name.startswith(('docs/','catalogue/')):target.chmod(0o755)
(OUT/'release-preparation-v2.json').write_text(json.dumps({'revision':revision,'destination':str(DEST),'counts':counts,'seconds':time.time()-t,'root_index_or_HEAD_mutated':False,'linked_input_policy':'Docs/catalogue are retained immutable hardlinks. Before editing any isolated linked file, atomically replace with independent bytes. Unlink cleanup is safe; never chmod or overwrite shared inodes.','status':'source preparation only; no build/browser/remote'},indent=2)+'\n')
print(json.dumps(counts))
