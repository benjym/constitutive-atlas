from pathlib import Path
import ast,hashlib,json
Q=Path(__file__).resolve().parent;N=Q.parents[1];P=N/'current17-runtime-reuse-plan-v1';OLD=N.parent/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
ok(H(P/'manifest.json')=='6eb6878970761d1cb7faa6357cc55afa377c328491cecf14a929545d01906288','exact reuse source proposal manifest')
m=json.loads((P/'manifest.json').read_text());ok(len(m['files'])==13,'all13members')
for name,r in m['files'].items():
 p=P/name;ok(p.is_file()and not p.is_symlink()and H(p)==r['sha256']and p.stat().st_size==r['bytes'],'exact frozen member '+name)
ok(H(P/'collector-reuse.py')=='44dfd1957d0b3dfe7a2f362ac4908de5b9a2d43347b14a10530ae7d41bc5c225','exact collector successor')
a=ast.parse((OLD/'collector.py').read_text());b=ast.parse((P/'collector-reuse.py').read_text());D=lambda n:ast.dump(n,include_attributes=False)
afunctions={x.name:x for x in a.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))};bfunctions={x.name:x for x in b.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))};first=lambda tree,name:next(x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name==name)
for name in afunctions.keys()&bfunctions.keys():
 if name in ('validate_execution_freeze','main','assess_pair','Transport'):continue
 ok(D(afunctions[name])==D(bfunctions[name]),'whole unchanged common function/class '+name)
ok(D(first(a,'Transport'))==D(first(b,'Transport')),'original Transport whole AST retained')
ok(ast.unparse(afunctions['assess_pair']).replace('baseline-five-prospective-execution-freeze-v1','baseline-five-current17-reused-execution-freeze-v1')==ast.unparse(bfunctions['assess_pair']),'whole pair science AST only expected freezeidentity change')
for n in ('policy.json','wasm-cli.mjs'):ok((P/n).read_bytes()==(OLD/n).read_bytes(),'exact original scientific dependency '+n)
g=json.loads((P/'GATES.json').read_text())
for n,entry in g['original'].items():ok(H(Path(entry['path']))==entry['sha256'],'exact old gate authority '+n)
# Production provenance functions exactly match separately supplied source section.
provenance=ast.parse((P/'reuse-provenance.py.txt').read_text());pb={x.name:x for x in provenance.body if isinstance(x,ast.FunctionDef)}
for name,x in pb.items():ok(D(x)==D(bfunctions[name]),'exact installed provenance function '+name)
wrapper=ast.parse((P/'per-call-bindings.py.txt').read_text());ok(D(wrapper.body[1])==D(bfunctions['Transport']),'exact actual per-call pin wrapper AST')
# Read-only complete inventory using only original source_files, unchanged constants, literal JSON/hashes.
ctx=N/'current17-runtime-source-v1/source';env={'Path':Path,'json':json,'hashlib':hashlib}
for node in a.body:
 if isinstance(node,ast.Assign)and any(isinstance(x,ast.Name)and x.id in('GATES','DP')for x in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'original-constants','exec'),env)
exec(compile(ast.Module(body=[afunctions['source_files']],type_ignores=[]),'original-source-only-inventory','exec'),env);files=env['source_files'](ctx);ok(len(files)==808,'current complete original-scope source discovery808')
policy=json.loads((P/'policy.json').read_text())
for n,pin in policy['unchanged_gate_sha256'].items():ok(H(ctx/n)==pin,'all original independent numerical gate hashes '+n)
for n,pin in policy['candidate_sha256'].items():ok(H(ctx/'models'/f'{n}.json')==pin,'all5 current exact candidate hashes '+n)
report={'status':'PASS_SOURCE_ONLY','checks':len(labels),'labels':labels,'source_map':{str(p.relative_to(ctx)):H(p)for p in files},'scope':'no tool/version/build/compiler/module/material/reference replay calls'}
(Q/'source-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS_SOURCE_ONLY','checks':len(labels)}))
