"""Exact minimal-delta and AST flag checks; no freezer/helper main or assets."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;P=HERE.parent/'package-v6';OLD=HERE.parent/'package-v5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sha(P/'MANIFEST.json')=='c566be0e484973342ea3b52c15465fb52d80236f851d6f43c9a62dfb97e052bf'
 manifest=json.loads((P/'MANIFEST.json').read_text());assert all(sha(P/n)==h for n,h in manifest['files'].items())
 before=(OLD/'freeze_inputs.py').read_text();after=(P/'freeze_inputs.py').read_text()
 old="if not arg.endswith('-wasm-dir'):continue";new="if not (arg.startswith('--') and arg.endswith('-wasm-dir')):continue"
 assert before.count(old)==1 and before.replace(old,new)==after
 assert (P/'run_package.py').read_bytes()==(OLD/'run_package.py').read_bytes()
 assert (P/'owned_process.py').read_bytes()==(OLD/'owned_process.py').read_bytes()
 prior=json.loads((OLD/'plan.json').read_text());plan=json.loads((P/'plan.json').read_text());expected=list(prior['argv']);expected[-1]=expected[-1].replace('site-v5','site-v6');assert plan['argv']==expected and plan['cwd']==prior['cwd'] and plan['parents']==prior['parents']
 mainfn=next(n for n in ast.parse(after).body if isinstance(n,ast.FunctionDef) and n.name=='main')
 loop=next(n for n in mainfn.body if isinstance(n,ast.For) and ast.unparse(n.target)=='(i, arg)')
 expression=ast.Expression(loop.body[0].test.operand);code=compile(expression,'exact-v6-asset-predicate','eval')
 def matches(s):return eval(code,{'arg':s})
 fixture={'--wasm-dir':True,'--burgers-wasm-dir':True,'--hill-wasm-dir':True,'/tmp/burgers-wasm-dir':False,'/tmp/--hill-wasm-dir':False,'--output':False,'--not-wasm-dir-value':False,'relative-wasm-dir':False}
 assert all(matches(s)==want for s,want in fixture.items())
 recognized=[{'option':s,'directory':plan['argv'][i+1]} for i,s in enumerate(plan['argv']) if matches(s)]
 flags=[s for s in plan['argv'] if s.startswith('--') and s!='--output'];assert [r['option'] for r in recognized]==flags and len(recognized)==14
 assert all(not row['directory'].startswith('--') for row in recognized)
 for n in ['freeze_inputs.py','run_package.py','owned_process.py']:ast.parse((P/n).read_text())
 result={'status':'passed-independent-minimal-source-regression','manifest_sha256':sha(P/'MANIFEST.json'),'all_seven_members_match':True,'sole_freezer_change_exact':True,'wrapper_lifecycle_byte_identical_v5':True,'full_argv_only_site6_output_change':True,'same_cwd_parents':True,'predicate_fixture_cases':len(fixture),'actual_plan_asset_options':recognized,'source_assets_bytes_hashed':False,'freeze_package_compiled_child_browser_remote_calls':0}
 (HERE/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
