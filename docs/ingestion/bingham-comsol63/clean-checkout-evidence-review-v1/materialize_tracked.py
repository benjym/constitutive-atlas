from pathlib import Path
import subprocess,os,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];T=Path('/private/tmp/atlas-bingham-clean-review-v1');T.mkdir(exist_ok=False)
rows=subprocess.check_output(['git','ls-files','-s','-z'],cwd=R).split(b'\0');inventory={}
for row in rows:
 if not row:continue
 metadata,name=row.split(b'\t',1);mode,oid,stage=metadata.decode().split();name=name.decode();assert stage=='0';src=R/name;dst=T/name;dst.parent.mkdir(parents=True,exist_ok=True)
 if mode=='120000':dst.symlink_to(os.readlink(src));data=os.readlink(src).encode()
 else:
  data=src.read_bytes();os.link(src,dst)
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name
 inventory[name]={'mode':mode,'git_blob':oid,'sha256':hashlib.sha256(data).hexdigest()}
(O/'TRACKED-INVENTORY.json').write_text(json.dumps({'source_root':str(R),'tracked_only_context':str(T),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'files':inventory},indent=2)+'\n');print('tracked exact',len(inventory))
