"""Restore the prior Tresca diagnostic observer; preserve the failed frozen harness."""
from pathlib import Path
import shutil,json,hashlib
B=Path(__file__).resolve().parent;R=B.parents[2];src=B/'qualification';dst=B/'qualification-v2';assert not dst.exists()
shutil.copytree(src,dst)
p=dst/'generated/models.hpp';s=p.read_text();assert 'study_branch' not in s
s=s.replace('namespace atlas {','namespace atlas {\ninline int study_branch=-1;',1)
needle='if (!atlas_eval_ok || !atlas::finite_value(branch)) return false;';assert s.count(needle)==1
s=s.replace(needle,needle+'\nstudy_branch=int(value(branch));',1);p.write_text(s)
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.rglob('*')) if p.is_file()}
for p in [B/'prepare_harness_v2.py',B/'native-regression-build.log',B/'qualification-freeze.json']:files[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
(B/'qualification-freeze-v2.json').write_text(json.dumps(dict(identity='bounded-partition-retry-diagnostic-harness-v2',reason='Restore exact prior branch observer omitted from new generated regression harness; no material/runtime/acceptance change',files=files),indent=2)+'\n')
print('Frozen v2',len(files),'files')
