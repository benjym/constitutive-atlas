"""AST regression fixture only; never actual assets/freezer/package."""
from pathlib import Path
import ast,json,hashlib
HERE=Path(__file__).resolve().parent
source=(HERE/'freeze_inputs.py').read_text();tree=ast.parse(source);guards=[]
for n in ast.walk(tree):
 if isinstance(n,ast.If) and isinstance(n.test,ast.UnaryOp) and ast.unparse(n.test).find("endswith('-wasm-dir')")>=0:guards.append(n.test)
assert len(guards)==1
expr=compile(ast.Expression(body=guards[0]),'<exact asset option guard>','eval')
def recognized(arg):return not eval(expr,{}, {'arg':arg})
cases={'--burgers-wasm-dir':True,'/qualified/burgers-wasm-dir':False,'--hill-wasm-dir':True,'/qualified/hill-wasm-dir':False,'--output':False,'--wasm-dir':True}
for arg,want in cases.items():assert recognized(arg)==want,(arg,want)
plan=json.loads((HERE/'plan.json').read_text());argv=plan['argv'];dirs=[argv[i+1] for i,arg in enumerate(argv) if recognized(arg)];assert len(dirs)==14 and all(not x.startswith('--') for x in dirs)
old=HERE.parent/'package-v5';assert (HERE/'run_package.py').read_bytes()==(old/'run_package.py').read_bytes();assert (HERE/'owned_process.py').read_bytes()==(old/'owned_process.py').read_bytes();assert source==(old/'freeze_inputs.py').read_text().replace("if not arg.endswith('-wasm-dir'):continue","if not (arg.startswith('--') and arg.endswith('-wasm-dir')):continue")
oldplan=json.loads((old/'plan.json').read_text());assert argv[:-1]==oldplan['argv'][:-1] and argv[-1]==oldplan['argv'][-1].replace('site-v5','site-v6');assert plan['parents']==oldplan['parents'] and plan['cwd']==oldplan['cwd']
result={'status':'passed exact AST/source-only regression; no actual source/asset bytes or package read','option_cases':cases,'recognized_asset_directories':len(dirs),'freeze_change':'single option recognition condition','wrapper_and_lifecycle_byte_identical_v5':True,'only_argv_change':'site-v6'}
with (HERE/'test-results.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
