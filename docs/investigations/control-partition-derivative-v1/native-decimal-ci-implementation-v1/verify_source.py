"""Source hashes, exact overlay and AST preservation; no process execution."""
import sys
sys.dont_write_bytecode=True
import ast,difflib,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
S=Path('/private/tmp/atlas-md1997-decimal-ci-v1/source')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prep=json.loads((P/'preparation.json').read_text());base=prep['base_files'];old=Path(prep['source'])
changed=['tests/test_native_fixture_dispatch.py','tools/check_native_fixture_dispatch.py']
added=['tools/collect_md1997_decimal.py']+['tools/md1997_decimal_reference/'+n for n in ['assess_saved.py','decimal_dsl.py','POLICY.md','requests.json','reference.json','transport-schema.json']]
actual={str(p.relative_to(S)):sha(p)for p in S.rglob('*')if p.is_file()}
assert len(base)==594 and len(actual)==601
assert set(actual)-set(base)==set(added)and set(base)-set(actual)==set()
assert sorted(n for n in base if actual[n]!=base[n])==changed
assert all(sha(old/n)==h for n,h in base.items())
assert not any(p.is_symlink()or p.name=='__pycache__'or p.suffix=='.pyc'for p in S.rglob('*'))
for n in changed+added:
 if n.endswith('.py'):ast.parse((S/n).read_text(),filename=n)
# Pin every copied support byte directly to the independently accepted oracle.
O=Path('/Users/bmar5496/code/constitutive-atlas/docs/investigations/control-partition-derivative-v1/native-decimal-reference-v1')
for n in added[1:]:assert (S/n).read_bytes()==(O/Path(n).name).read_bytes()
name='tools/check_native_fixture_dispatch.py'
a=ast.parse((old/name).read_text());b=ast.parse((S/name).read_text())
fa={x.name:ast.dump(x,include_attributes=False)for x in a.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))};fb={x.name:ast.dump(x,include_attributes=False)for x in b.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
unchanged=sorted(n for n in fa if fa[n]==fb.get(n));modified=sorted(set(fa)-set(unchanged))
assert modified==['Receipt','check_contracts','context','ctest','execute','main']
report=dict(identity='decimal-ci-source-only-overlay-proof-v1',passed=True,base_count=594,new_count=601,unchanged_base_count=592,changed=changed,added=added,unchanged_dispatch_AST=unchanged,modified_dispatch_AST=modified,base_fixture_unchanged=True,cpp_fixture_composition_required=True,compiled_calls=0)
freeze=dict(identity='md1997-decimal-ci-source-freeze-v1',directory=str(S),files=actual)
for filename,obj in [('source-proof.json',report),('source-freeze.json',freeze)]:
 target=P/filename
 raw=json.dumps(obj,indent=2)+'\n'
 if target.exists():assert target.read_text()==raw
 else:target.write_text(raw)
for n in changed+added:
 target=P/'files'/n;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==(S/n).read_bytes()
 else:target.write_bytes((S/n).read_bytes())
diff=''.join(''.join(difflib.unified_diff((old/n).read_text().splitlines(True),(S/n).read_text().splitlines(True),fromfile='base/'+n,tofile='new/'+n))for n in changed)
target=P/'implementation.diff'
if target.exists():assert target.read_text()==diff
else:target.write_text(diff)
print(json.dumps(report,indent=2))
