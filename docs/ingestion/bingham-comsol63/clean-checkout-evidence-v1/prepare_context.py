"""Create private exact HEAD-member source context. Git commands are read-only."""
from pathlib import Path
import gzip,hashlib,json,os,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];C=Path('/private/tmp/atlas-bingham-clean-checkout-evidence-v1/tracked-context');assert not C.exists();C.mkdir(parents=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='28d4af2b1d4d6b9c1a58038a8ef9a99ec3279d8c'
raw=subprocess.check_output(['git','ls-tree','-rz','HEAD'],cwd=R);tree={};fallbacks=[]
for row in raw.split(b'\0'):
 if not row:continue
 meta,n=row.split(b'\t',1);mode,kind,oid=meta.decode().split();name=n.decode();assert kind=='blob';source=R/name;dst=C/name;dst.parent.mkdir(parents=True,exist_ok=True)
 data=os.readlink(source).encode() if mode=='120000' else source.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if actual!=oid:
  data=subprocess.check_output(['git','cat-file','blob',oid],cwd=R);fallbacks.append(name)
 if mode=='120000':dst.symlink_to(data.decode())
 elif actual==oid:os.link(source,dst)
 else:dst.write_bytes(data)
 tree[name]={'git_blob':oid,'sha256':hashlib.sha256(data).hexdigest(),'mode':mode}
(H/'TRACKED-INPUTS.json.gz').write_bytes(gzip.compress((json.dumps(tree,indent=2)+'\n').encode(),mtime=0));(H/'CONTEXT.json').write_text(json.dumps({'head':head,'tracked_members':len(tree),'private_context':str(C),'git_object_fallbacks':fallbacks,'extra_untracked_files_copied':0,'git_mutations':0},indent=2)+'\n');print('tracked',len(tree),'git-object fallback',fallbacks)
