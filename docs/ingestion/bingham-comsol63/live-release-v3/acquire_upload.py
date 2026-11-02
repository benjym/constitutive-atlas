"""Acquire only the exact successful Bingham CI Pages upload; never execute it."""
import hashlib,json,subprocess,tarfile,zipfile,shutil
from pathlib import Path
RUN=41388826742
HEAD="43ea5c45f0e6112661fe996b685a3adcdac12ce6"
HERE=Path(__file__).resolve().parent
PRIVATE=Path("/private/tmp/atlas-bingham-ci-upload-41388826742")
def sha(p):
 with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def api(path):return subprocess.check_output(["gh","api","repos/benjym/constitutive-atlas/"+path])
assert not PRIVATE.exists(),"Retain previous attempt; choose distinct identity before retry"
PRIVATE.mkdir()
run=json.loads(api(f"actions/runs/{RUN}"))
assert run["head_sha"]==HEAD and run["status"]=="completed" and run["conclusion"]=="success"
(HERE/"ci-terminal.json").write_text(json.dumps(run,indent=2)+"\n")
raw=api(f"actions/runs/{RUN}/artifacts");data=json.loads(raw)
(HERE/"github-artifact-api.json").write_bytes(raw)
items=[x for x in data["artifacts"] if x["name"]=="github-pages"]
assert len(items)==1
a=items[0];assert a["workflow_run"]["id"]==RUN and a["workflow_run"]["head_sha"]==HEAD and not a["expired"]
z=PRIVATE/"github-pages.zip"
with z.open("xb") as f:subprocess.run(["gh","api",f"repos/benjym/constitutive-atlas/actions/artifacts/{a['id']}/zip"],stdout=f,check=True)
assert a["digest"]=="sha256:"+sha(z)
with zipfile.ZipFile(z) as f:
 assert f.namelist()==["artifact.tar"]
 with f.open("artifact.tar") as src,(PRIVATE/"artifact.tar").open("xb") as dst:shutil.copyfileobj(src,dst,1024*1024)
t=PRIVATE/"artifact.tar";site=PRIVATE/"site";site.mkdir()
with tarfile.open(t) as f:
 for m in f.getmembers():
  n=Path(m.name);assert not n.is_absolute() and ".." not in n.parts
  assert m.isfile() or m.isdir(),("non-regular upload member",m.name)
 f.extractall(site,filter="data")
files={str(p.relative_to(site)):{"sha256":sha(p),"bytes":p.stat().st_size} for p in sorted(site.rglob("*")) if p.is_file()}
(HERE/"UPLOAD-MANIFEST.json").write_text(json.dumps({"run_id":RUN,"source_revision":HEAD,"files":files},indent=2)+"\n")
r={"run_id":RUN,"source_revision":HEAD,"artifact":a,"zip_sha256":sha(z),"tar_sha256":sha(t),"private_directory":str(PRIVATE),"site":str(site),"files":len(files),"all_members_regular_and_safe":True}
(HERE/"ARTIFACT-RECEIPT.json").write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r))
