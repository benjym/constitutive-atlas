"""Source-only, exact-Git selection and path-adapter generation; no imports of runtime."""
import ast, difflib, hashlib, json, subprocess
from pathlib import Path
BASE='3873a48b256ed37cbc78378ee6b41d73139676f8'
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def read(p): return git('show',BASE+':'+p)
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,v): (OUT/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
paths=set(git('ls-tree','-r','--name-only',BASE).decode().splitlines())
prior=json.loads((ROOT/'docs/investigations/implicit-predictor-constraints-v1/profile-regression-plan-v1/published-input-inventory.json').read_text())
selected=set(prior['files'])
# Bounded supporting trees, not recursive documentary closure.
selected|={p for p in paths if p.startswith(('tools/','tests/','cmake/','examples/','web/'))}
selected|={p for p in paths if p.startswith('docs/ingestion/hill-abaqus2025/')}
selected|={p for p in paths if p.startswith('models/') or p.startswith(('catalogue/agent-reviews/','catalogue/path-examples/')) or p in {'catalogue/approved-models.json'}}
maxwell={p for p in paths if (p.startswith('atlas/') and p.endswith('.py') or p.startswith('cpp/') and p.endswith(('.cpp','.hpp')) or p.startswith('schemas/') and p.endswith('.json') or p.startswith('cpp/scalar-functions/')) and '__pycache__' not in p.split('/')}
maxwell|={'cmake/maxwell/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'}
norsand={p for p in paths if (p.startswith('atlas/') and p.endswith('.py') or p.startswith('cpp/include/atlas/') and p.endswith('.hpp') or p.startswith('schemas/') and p.endswith('.json') or p.startswith('cpp/scalar-functions/')) and '__pycache__' not in p.split('/')}
norsand|={'cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'}
selected|=maxwell|norsand
# These guarded packaging receipts/text dependencies are explicit; their own supporting pins are not assumed closed.
selected|={'docs/admission/maxwell-agent-v2/approval.json','docs/ingestion/maxwell-itasca900/atlas-controller-v1/independent-review/receipt.json','docs/reviews/maxwell-checklist-v2/README.md','docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json','docs/ingestion/norsand-1993/approval-v1/REPORT.md'}
missing=sorted(selected-paths); selected &= paths
# Batch exact blobs without scanning nested catalogue snapshot archives.
ordered=sorted(selected)
raw=subprocess.check_output(['git','cat-file','--batch'],input=(''.join(BASE+':'+p+'\n' for p in ordered)).encode(),cwd=ROOT)
cache={};offset=0
for p in ordered:
 end=raw.index(b'\n',offset);header=raw[offset:end].split();size=int(header[2]);offset=end+1
 cache[p]=raw[offset:offset+size];offset+=size+1
files={p:{'sha256':sha(cache[p]),'bytes':len(cache[p]),'role':'runtime-baseline-only' if p.startswith(('cpp/','atlas/','schemas/')) else 'support-input'} for p in sorted(selected)}
save('support-selection.json',dict(base=BASE,method='Refresh prior 1128 names; bounded tools/tests/cmake/examples/web/model trees and selected registry/reviews; Hill packet; exact Maxwell/NorSand source sets and named packaging inputs.',closure_claim='Exact Maxwell/NorSand source-manifest name sets only; support and guarded packaging transitive documentary closure NOT established.',missing=missing,files=files))
save('source-manifest-sets.json',dict(base=BASE,profiles={k:{'files':{p:files[p]['sha256'] for p in sorted(v)},'baseline_manifest_sha256':sha(json.dumps({p:files[p]['sha256'] for p in sorted(v)},sort_keys=True,separators=(',',':')).encode())} for k,v in [('maxwell',maxwell),('norsand',norsand)]},overlay_rule='Recompute on final isolated patched source, including additions; never copy baseline runtime files over patch. Maxwell digest is exact packager algorithm; NorSand requires exact sources map rather than this convenience aggregate.'))
preamble="import os\nROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()\nBASE=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve()\nassert BASE != ROOT and not BASE.is_relative_to(ROOT), 'Fresh output must be outside support source'\nassert BASE.is_dir(), 'Create fresh output directory explicitly'\n"
specs=[('docs/ingestion/sls-comsol63/execution-v1/check_saved.py','adapters/check_sls_saved.py',[
('BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]',preamble+"INPUT_BASE=ROOT/'docs/ingestion/sls-comsol63/execution-v1'"),
("BASE/'study.py'","INPUT_BASE/'study.py'"),("BASE/'cases.json'","INPUT_BASE/'cases.json'")]),
('docs/ingestion/maxwell-itasca900/integration-v1/check_transactions.py','adapters/check_maxwell_transactions.py',[
('ROOT=Path(__file__).resolve().parents[4]',preamble+"INPUT_BASE=ROOT/'docs/ingestion/maxwell-itasca900/integration-v1'"),
('BASE=Path(__file__).resolve().parent',''),("BASE/'reference-cases.json'","INPUT_BASE/'reference-cases.json'"),
("Path('/private/tmp/atlas-maxwell-execution-v1/cli')","BASE/'cli'")])]
proof=[]
for source,target,replacements in specs:
 original=read(source).decode(); adapted=original
 for a,b in replacements:
  assert adapted.count(a)==1,(source,a,adapted.count(a)); adapted=adapted.replace(a,b)
 ast.parse(adapted)
 (OUT/target).write_text(adapted)
 restored=adapted
 for a,b in reversed(replacements):
  # Empty deletion restoration uses explicit unique source context.
  if b=='': restored=restored.replace("spec.loader.exec_module(m)\n\n", "spec.loader.exec_module(m)\n"+a+"\n",1)
  else: assert restored.count(b)==1; restored=restored.replace(b,a)
 assert restored==original,source
 proof.append(dict(source=source,source_sha256=sha(original.encode()),adapter=target,adapter_sha256=sha(adapted.encode()),exact_reverse_substitution=True,replacements=[dict(original=a,replacement=b)for a,b in replacements]))
 (OUT/(Path(target).stem+'.diff')).write_text(''.join(difflib.unified_diff(original.splitlines(True),adapted.splitlines(True),fromfile=source,tofile=target)))
save('adapter-proof.json',proof)
print(json.dumps(dict(selected=len(files),missing=missing,source_sets={k:len(v)for k,v in [('maxwell',maxwell),('norsand',norsand)]},adapters=len(proof))))
