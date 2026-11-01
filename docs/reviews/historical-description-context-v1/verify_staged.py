from pathlib import Path
import subprocess,json,hashlib,sys,tempfile
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/historical-description-context-v1'
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((P/'archive-plan.json').read_text())
for ref in plan['references']:assert sha(checked_receipt(R,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256']
for n,h in plan['original_bytes'].items():assert sha(checked_receipt(R,'docs/reviews/historical-description-context-v1/archive-plan.json',n,h))==h
base=Path(tempfile.mkdtemp(prefix='description-index-'))
def index(path):return subprocess.check_output(['git','show',':'+path],cwd=R)
paths=['web/app.js','web/formulation-view.mjs','web/state-contract.mjs','web/catalogue.mjs','tests/test_description_context.mjs','tests/test_formulation_view.mjs','tests/test_agent_review_browser.mjs']
paths+=subprocess.check_output(['git','ls-files','web'],cwd=R).decode().splitlines()
paths+=subprocess.check_output(['git','ls-tree','--name-only','HEAD:models'],cwd=R).decode().splitlines()
paths=[('models/'+n if '/' not in n else n) for n in paths if n.endswith(('.js','.mjs','.json'))]
for n in paths:p=base/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(index(n))
# Exact staged app matches the actual browser-tested overlay.
assert index('web/app.js')==(P/'tested-app.js').read_bytes()
result=subprocess.run(['node','--test','tests/test_description_context.mjs','tests/test_formulation_view.mjs','tests/test_agent_review_browser.mjs'],cwd=base,capture_output=True,text=True)
print(result.stdout);print(result.stderr);assert result.returncode==0,base
print(json.dumps({'staged_tree':str(base),'original_receipt_edges':len(plan['references']),'original_snapshot_bindings':len(plan['original_bytes']),'exact_tested_app':True}))
