"""Prepare an explicitly owned source/evidence commit in the isolated checkout."""
from pathlib import Path
import hashlib,json,subprocess
H=Path(__file__).resolve().parent;N=H.parent;ROOT=N.parents[2]
S=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=S,text=True)
assert not(H/'paths.nul').exists()
assert git('rev-parse','HEAD').strip()=='023a67e4d83b96491fffda8d89c8479f2c8f38a3'
rows=json.loads((N/'supported-package-source-binding-v1/source-delta.json').read_text())['files']
assert set(git('diff','--name-only').splitlines())=={'tools/test_web_package.mjs'}
for r in rows:assert sha(S/r['path'])==r['sha256']
text='''\n## Standard package checkpoint and retained storage — 2026-11-05\n\nThe fresh full package passes all built-in special-engine checks, smoke, all994 dataset transports and four contract suites. The supported17 phase stopped before engine import on a historical controlled-time packager pin. [Failed study](../../delivery/unheld-finalisation-20261105-v1/standard-web-failure-v3/manifest.json) `89a84dc7` retains all observations and the exact1565-file site inventory. The independently accepted source-only correction `b0cd7165` preserves the historical authority and binds the reviewed current packager; it changes no model, numerical setting or artifact. The affected supported17 and original scoped-parity gates still require genuine execution. E8 remains open.\n\nCoordinator retains `/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v3` for active qualification, alongside the isolated source, C build/cache and three-file SLS recovery. The redundant failed `site-C-standard-v2` was removed after all1482files were verified recoverable from the durable original Pages702 ZIP plus a3,412,994B private delta. [Retention and cleanup receipts](../../delivery/unheld-finalisation-20261105-v1/cleanup-C-sites-v1/removal.json) preserve hashes and recovery instructions; free space increased259,809,280B during removal. All failed raw observations remain unchanged; other agents' resources are untouched.\n'''
paths=[r['path']for r in rows]
archives=[]
for mid in ['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']:
 rel=Path('docs/ingestion')/mid/'DELIVERY.md';p=ROOT/rel;q=S/rel
 assert p.read_bytes()==q.read_bytes(),rel
 archive=H/'preimages'/rel;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(p.read_bytes())
 archives.append(dict(path=str(rel),sha256=sha(p),bytes=p.stat().st_size))
 p.write_text(p.read_text()+text);q.write_bytes(p.read_bytes());paths.append(str(rel))
board_note='\n- [X] **FIX-C-supported-package-source-binding-v1 source handoff** — Exactaf2f176b proposal independently acceptedb0cd7165;132independent+67authorchecks PASS. Two explicit paths installed archive-first c088a015; genuine813source/full1565site continuation passes. Reuse original six passed/reaped observations and unchanged site-v3; parent must run supported17 then originalscoped under fresh guarded identity. Failurev3 retained89a84; no package/browser/live acceptance. Removed only redundant failedv2site after1482file lossless recovery via original Pages702ZIP and3.4MBdelta; cleanup receipt records259.8MB free-space delta. All5MODEL/E8 remainopen.\n'
for label,base in [('root',ROOT),('isolated',S)]:
 p=base/'IMPLEMENTATION_PLAN.md';a=H/'preimages'/label/p.name;a.parent.mkdir(parents=True,exist_ok=True);a.write_bytes(p.read_bytes());p.write_text(p.read_text()+board_note)
paths.append('IMPLEMENTATION_PLAN.md')
(H/'preimages.json').write_text(json.dumps(archives,indent=2)+'\n')
directories=['supported-package-source-binding-v1','shared-current17-review-v1/supported-package-source-binding-v1','standard-web-failure-v3','standard-web-delivery-actual-v3','standard-web-launch-v4','cleanup-C-sites-v1','board-preimages-before-supported-binding-v1','board-preimages-before-C-origin-plan-v1','supported-package-installation-v1','supported-source-commit-preparation-v1']
copied=[]
for name in directories:
 for p in sorted((N/name).rglob('*')):
  if not p.is_file()or'__pycache__'in p.parts:continue
  assert not p.is_symlink(),p
  rel=p.relative_to(ROOT);q=S/rel
  if q.exists():assert q.read_bytes()==p.read_bytes(),rel
  else:q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());copied.append(str(rel));paths.append(str(rel))
paths=sorted(set(paths))
(H/'paths.nul').write_bytes(b''.join(p.encode()+b'\0'for p in paths))
(H/'preparation.json').write_text(json.dumps(dict(parent='023a67e4d83b96491fffda8d89c8479f2c8f38a3',owned_paths=paths,copied_new_evidence=copied,root_git_mutated=False),indent=2)+'\n')
print(json.dumps(dict(owned_paths=len(paths),new_evidence_files=len(copied))))
