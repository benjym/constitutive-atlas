"""Freeze source-only profile commands and reversible path adapters; no execution."""
import ast,difflib,hashlib,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;C=D.parent;S=Path('/private/tmp/atlas-control-partition-support-v3/source');B='3873a48b256ed37cbc78378ee6b41d73139676f8';sha=lambda b:hashlib.sha256(b).hexdigest()
f=json.loads((C/'qualification-support-v4/source-freeze.json').read_text());files=f.get('files',f.get('source_files'));assert len(files)==2628
for n,h in files.items():assert sha((S/n).read_bytes())==h,n
assert sorted(files)==sorted(str(p.relative_to(S))for p in S.rglob('*')if p.is_file())
A=D/'adapters';A.mkdir(exist_ok=True);proof={};inputs={}
def pin(p):inputs[str(p)]=sha(p.read_bytes())
def adapt(name,src,replacements):
 old=src.read_text();new=old
 for a,b in replacements:assert new.count(a)>0,(name,a,new.count(a));new=new.replace(a,b)
 reverse=new
 for a,b in reversed(replacements):assert reverse.count(b)>0;reverse=reverse.replace(b,a)
 assert reverse==old
 (A/name).write_text(new);(D/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(src),tofile='adapters/'+name)))
 proof[name]=dict(source=str(src),source_sha256=sha(old.encode()),adapter_sha256=sha(new.encode()),replacements=[dict(original=a,replacement=b)for a,b in replacements],exact_reverse=True);pin(src)
for n in ['assess_fresh.py','check_j2_paths.py','prepare_sls_reports.py','check_sls_saved.py','check_maxwell_transactions.py']:
 src=C/'qualification-support-v2/adapters'/n;(A/n).write_bytes(src.read_bytes());pin(src);proof[n]=dict(exact_reuse=True,source=str(src),sha256=sha(src.read_bytes()))
adapt('compare_maxwell.py',S/'docs/ingestion/maxwell-itasca900/integration-v1/compare_backends_v2.py',[("BASE=Path(__file__).resolve().parent","import os\nBASE=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve()\nassert BASE.is_dir() and not BASE.is_relative_to(Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve())")])
adapt('study.py',S/'docs/ingestion/burgers-itasca900/integration-v1/study.py',[("R=Path(__file__).resolve().parent","import os\nR=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()/'docs/ingestion/burgers-itasca900/integration-v1'"),("R/'model.json'","R.parents[3]/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json'")])
adapt('test_burgers_native.py',S/'tools/test_burgers_native.py',[("ROOT=Path(__file__).resolve().parents[1]","import os\nROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()"),("from study import Backend,execute,assess","sys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom study import Backend,execute,assess")])
# Frozen original parity code, retained unedited; a new dispatcher extracts its function.
raw=subprocess.check_output(['git','show',B+':docs/ingestion/burgers-itasca900/integration-v1/verify.py']);(D/'burgers-original-verify.py').write_bytes(raw)
originalmodel=subprocess.check_output(['git','show',B+':docs/ingestion/burgers-itasca900/integration-v1/model.json']);assert originalmodel==(S/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json').read_bytes()
proof['burgers_model_path']=dict(original_sha256=sha(originalmodel),canonical_sha256=sha(originalmodel),exact_byte_equal=True)
# Literal Power collector freeze closure. Capture exact missing old bytes here,
# never install them in the frozen2628 source.
P=S/'docs/ingestion/power-creep-itasca900/execution-v1/refinement-v2';freeze=json.loads((P/'freeze.json').read_text());missing=[]
for n,h in freeze['files'].items():
 p=(P/n).resolve();rel=str(p.relative_to(S))
 if p.exists():assert sha(p.read_bytes())==h
 else:
  try:b=subprocess.check_output(['git','show',B+':'+rel],stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError:b=None
  if b is not None:assert sha(b)==h
  missing.append(dict(path=rel,sha256=h,available_exact=b is not None,git_source=B+':'+rel if b is not None else None))
pin(P/'freeze.json');pin(S/'tools/power_creep_study.py');pin(S/'tools/power_creep_refined_study.py')
(D/'literal-gaps.json').write_text(json.dumps(dict(identity='current-profile-literal-preflight-v1',power_freeze_files=len(freeze['files']),power_missing=missing,power_present_wrong=0,burgers_model_literal_missing=not(S/'docs/ingestion/burgers-itasca900/integration-v1/model.json').exists(),burgers_model_path_resolved_by_exact_adapter=True,source_mutations=0),indent=2)+'\n')
for p in [C/'qualification-support-v4/manifest.json',C/'qualification-support-v4/source-freeze.json',C/'qualification-support-v4/patched-source-manifests.json',C/'qualification-support-v4-review/manifest.json',C/'qualification-support-v1/profile-targets.json',C/'qualification-support-v2/adapter-proof.json',C/'qualification-support-v2/j2-paths-with-public-preset.json',C/'qualification-support-v2/retained-assets.json']:pin(p)
(D/'adapter-proof.json').write_text(json.dumps(proof,indent=2)+'\n');(D/'preparation-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
for p in A.glob('*.py'):ast.parse(p.read_text())
print(json.dumps(dict(source_files=2628,adapters=len(proof),power_missing=len(missing),power_unavailable=sum(not x['available_exact']for x in missing),compiled_calls=0)))
adapt('study_j2.py',S/'tools/study_j2.py',[("ROOT = Path(__file__).resolve().parents[1]","import os\nROOT = Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()"),("BASE/'references.json'","Path(os.environ['ATLAS_J2_REFERENCE'])")])
(D/'adapter-proof.json').write_text(json.dumps(proof,indent=2)+'\n');(D/'preparation-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
