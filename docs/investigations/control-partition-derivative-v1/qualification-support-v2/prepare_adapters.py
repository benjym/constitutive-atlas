"""Generate exact path-only J2 adapter and retain v1 adapters unchanged."""
import ast,difflib,hashlib,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[3];BASE='3873a48b256ed37cbc78378ee6b41d73139676f8'
source='docs/ingestion/j2-linear-hardening/execution-v2/check_paths.py'
original=subprocess.check_output(['git','show',BASE+':'+source],cwd=ROOT).decode()
preamble="import os\nROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve();sys.path.insert(0,str(ROOT))\nOUTPUT=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve()\nassert OUTPUT.is_dir() and not OUTPUT.is_relative_to(ROOT), 'Fresh external output directory required'"
replacements=[('ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))',preamble),('BASE=Path(__file__).resolve().parent',"BASE=ROOT/'docs/ingestion/j2-linear-hardening/execution-v2'"),("BASE/'native-paths-raw.json'","OUTPUT/'native-paths-raw.json'")]
adapted=original
for a,b in replacements:assert adapted.count(a)==1;adapted=adapted.replace(a,b)
ast.parse(adapted);restored=adapted
for a,b in reversed(replacements):assert restored.count(b)==1;restored=restored.replace(b,a)
assert restored==original
(D/'adapters/check_j2_paths.py').write_text(adapted)
(D/'check_j2_paths.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),adapted.splitlines(True),fromfile=source,tofile='adapters/check_j2_paths.py')))
proof=dict(source=source,source_sha256=hashlib.sha256(original.encode()).hexdigest(),adapter='adapters/check_j2_paths.py',adapter_sha256=hashlib.sha256(adapted.encode()).hexdigest(),exact_reverse_substitution=True,replacements=[dict(original=a,replacement=b)for a,b in replacements])
reused={}
for p in (D.parent/'qualification-support-v1/adapters').glob('*.py'):
 b=p.read_bytes();(D/'adapters'/p.name).write_bytes(b);reused[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest()
(D/'adapter-proof.json').write_text(json.dumps(dict(j2=proof,v1_exact_reuse=reused,wrapper_policy='Additional assess_fresh wrappers call unchanged source assessment functions; no reference generation, numerical expressions or tolerances'),indent=2)+'\n')
