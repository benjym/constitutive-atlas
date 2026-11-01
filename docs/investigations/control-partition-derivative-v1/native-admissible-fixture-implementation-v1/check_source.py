"""No compiler/backend imports or execution; exact source and protected-text proof."""
import ast,difflib,hashlib,json,re
from pathlib import Path
D=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((D/'source-freeze.json').read_text());R=Path(f['source_directory']);O=json.loads(Path(f['original_receipt']).read_text());assert sha(Path(f['original_receipt']))==f['original_receipt_sha256']
assert len(f['source_files'])==len(O['source_files'])==582
assert sorted(f['source_files'])==sorted(str(p.relative_to(R))for p in R.rglob('*')if p.is_file())
for name,digest in json.loads((D/'inputs.json').read_text()).items():assert sha(Path(name))==digest,'input drift: '+name
for name,digest in f['source_files'].items():assert sha(R/name)==digest,name
for name,digest in O['source_files'].items():assert sha(Path(O['source_directory'])/name)==digest,'original drift: '+name
changed=[n for n,h in f['source_files'].items()if h!=O['source_files'][n]];assert changed==['tests/test_solver.cpp']
a=(D/'original_test_solver.cpp').read_text();b=(D/'test_solver.cpp').read_text();assert b==(R/changed[0]).read_text()
assert sha(D/'original_test_solver.cpp')==O['source_files'][changed[0]]
A=a.splitlines(True);B=b.splitlines(True);ops=difflib.SequenceMatcher(None,A,B,autojunk=False).get_opcodes();reverse=[];deletions=[]
for tag,i,j,k,l in ops:
 reverse+=A[i:j]
 if tag in ('delete','replace'):deletions+=A[i:j]
assert ''.join(reverse)==a
assert deletions==['            for(int j=0;j<n;++j){\n'],'only the original loop dispatch line replaced'
# Every old assertion, old fixture setup, loading/settings and final tests retained.
assert re.findall(r'require\([^\n]+',a)==[x for x in re.findall(r'require\([^\n]+',b)if x in re.findall(r'require\([^\n]+',a)]
assert b.index('unknown numerical fixture profile')<b.index('std::cout<<')
for s in ['5e-11:1e-6','level?h/2:h','<3e-5*std::max','<1.5e-5*std::max','md_fixture_branch(plus,p)==branch&&md_fixture_branch(minus,p)==branch','<=1e-9','<=1e-10','atlas::domain(int(m),z,p,true)','atlas::domain(int(m),zr,p,true)']:assert s in b,s
for p in D.glob('*.py'):ast.parse(p.read_text())
out=dict(identity='md1997-native-fixture-static-proof-v1',passed=True,compiled_calls=0,source_files=582,changed=changed,old_require_assertions=len(re.findall(r'require\([^\n]+',a)),protected_deleted_lines=deletions,reverse_restores_original=True,derivative_directions=dict(ambient=14,physical_source_tangent=13,levels=2,signs=2,probe_evaluations=108),no_compiled_result_observed=True)
encoded=json.dumps(out,indent=2)+'\n';dest=D/'static-checks.json'
if dest.exists():assert dest.read_text()==encoded
else:dest.write_text(encoded)
print(json.dumps(out))
