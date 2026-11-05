"""Remove only the coordinator-owned redundant failed site after exact retention checks."""
from pathlib import Path
import hashlib,json,os,shutil,stat,subprocess,time
H=Path(__file__).resolve().parent
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
SITE=Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v2')
SOURCE=SITE.parent/'source'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
r=json.loads((H/'retention.json').read_text());assert not(H/'removal.json').exists()
assert r['site']==str(SITE)and r['removed']is False and SITE.is_dir()and not SITE.is_symlink()
for k in ['base_archive','delta_archive','source_inventory','failure_manifest']:
 p=Path(r[k]['path']);assert p.is_file()and not p.is_symlink()and sha(p)==r[k]['sha256']and p.stat().st_size==r[k]['bytes']
actual={str(p.relative_to(SITE)):p for p in SITE.rglob('*')if p.is_file()or p.is_symlink()}
assert set(actual)=={row['path']for row in r['files']}
for row in r['files']:
 p=actual[row['path']];assert not p.is_symlink()and sha(p)==row['sha256']and p.stat().st_size==row['bytes']and stat.S_IMODE(p.stat().st_mode)==row['mode']
assert not any(p.name=='.git'for p in SITE.rglob('*'))
git_status=subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE,text=True);assert not git_status
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,command='],text=True)
private=ROOT/'.local/retained-evidence/baseline-five-C-failed-site-v2-cleanup-processes-20261105.raw'
assert not private.exists();private.write_text(ps)
processes={}
for line in ps.splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:processes[int(parts[0])]=(int(parts[1]),parts[2])
ancestors=set();pid=os.getpid()
while pid in processes and pid not in ancestors:ancestors.add(pid);pid=processes[pid][0]
consumers=[pid for pid,(_,cmd)in processes.items()if str(SITE)in cmd and pid not in ancestors]
assert not consumers,consumers
before=shutil.disk_usage(SITE).free
shutil.rmtree(SITE)
assert not SITE.exists()
after=shutil.disk_usage(SITE.parent).free
out=dict(identity='C-failed-site-v2-cleanup-v1',removed_paths=[str(SITE)],epoch=time.time(),
 removed_logical_bytes=r['target_bytes'],durable_delta_bytes=r['delta_archive']['bytes'],
 exact_recovery_files=r['exact_verified_files'],retention_receipt_sha256=sha(H/'retention.json'),
 free_bytes_before=before,free_bytes_after=after,free_bytes_delta=after-before,
 source_git_status_clean=True,active_consumers=consumers,
 private_process_inventory=dict(path=str(private),sha256=sha(private)),
 retained_resources=['Full current site-C-standard-v3 required by active package/production checks',r['base_archive']['path'],r['delta_archive']['path'],'All original failure receipts, inventories and raw observations'])
(H/'removal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
