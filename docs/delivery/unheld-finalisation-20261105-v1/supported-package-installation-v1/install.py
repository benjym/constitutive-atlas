"""Coordinator installation of two explicitly reviewed paths; retain exact old bytes first."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,time
H=Path(__file__).resolve().parent;N=H.parent
S=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
P=N/'supported-package-source-binding-v1'
R=N/'shared-current17-review-v1/supported-package-source-binding-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
assert not(H/'receipt.json').exists()
assert sha(P/'manifest.json')=='af2f176b9e943be9a0840e91cc5f28de51d9a1a62fceb665af112ce4be87a04f'
assert sha(R/'decision.json')=='b0cd71653ae9f0f0ce5467cc0a706954d0a54cb26cc3aa3d032cf9180dfda687'
decision=json.loads((R/'decision.json').read_text());assert decision['accepted']is True and not decision['unresolved_blockers']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip()=='023a67e4d83b96491fffda8d89c8479f2c8f38a3'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=S,text=True)
for directory in [P,R]:
 manifest=json.loads((directory/'manifest.json').read_text())
 for row in manifest['files']:
  rel=Path(row['path']);assert not rel.is_absolute()and'..'not in rel.parts
  q=directory/rel;assert not q.is_symlink()and sha(q)==row['sha256']and q.stat().st_size==row.get('bytes',row.get('size_bytes'))
delta=json.loads((P/'source-delta.json').read_text())['files'];assert len(delta)==2
for row in delta:
 q=S/row['path'];src=P/row['proposal']
 assert not q.is_symlink()and not src.is_symlink()and sha(src)==row['sha256']and src.stat().st_size==row['bytes']
 if row['preimage_sha256']is not None:assert sha(q)==row['preimage_sha256']
 else:assert not q.exists()
# Exact historical archive precedes mutation.
installed=[]
for row in sorted(delta,key=lambda r:r['preimage_sha256']is not None):
 q=S/row['path'];q.parent.mkdir(parents=True,exist_ok=True)
 if row['preimage_sha256']is None:
  with q.open('xb')as f:f.write((P/row['proposal']).read_bytes())
 else:q.write_bytes((P/row['proposal']).read_bytes())
 installed.append(pin(q))
spec=importlib.util.spec_from_file_location('supported_continuation',P/'continuation.py');pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
observed=pc.guard(S,sha(P/'manifest.json'))
receipt=dict(identity='reviewed-supported-package-source-installation-v1',epoch=time.time(),
 source=str(S),head_before='023a67e4d83b96491fffda8d89c8479f2c8f38a3',archive_first=True,
 proposal_manifest=pin(P/'manifest.json'),review=pin(R/'decision.json'),installed=installed,
 postcompile_continuation=observed,root_git_mutated=False)
(H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(installed=len(installed),receipt_sha256=sha(H/'receipt.json'),
 current_source_count=observed['current_source_count'],site_members=observed['retained_site']['members'])))
