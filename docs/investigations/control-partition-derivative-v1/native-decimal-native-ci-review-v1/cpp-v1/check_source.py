"""Read-only C++ overlay, data-flow and source identity review; never compiles."""
import json,hashlib,re,sys
from pathlib import Path
D=Path(__file__).resolve().parent;C=D.parent.parent;A=C/'native-decimal-fixture-v1';R=C/'native-decimal-reference-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
expected=sys.argv[1];ck('exact author manifest',sha(A/'manifest.json')==expected)
for n,v in read(A/'manifest.json')['files'].items():ck('author file '+n,sha(A/n)==v)
for n,v in read(D/'baseline-inputs.json').items():ck('baseline '+n,sha(Path(n))==v)
text=(A/'test_solver.cpp').read_text();base=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source/tests/test_solver.cpp').read_text();inv=text
for i,row in reversed(list(enumerate(read(A/'overlay.json')['changes']))):
 ck('unique inverse overlay '+str(i),inv.count(row['replacement'])==1);inv=inv.replace(row['replacement'],row['original'],1)
ck('complete inverse original bytes',inv==base)
# Inputs and resulting source inventory, whose receipt name is resolved only after final handoff.
freeze=read(A/'source-freeze.json');S=Path(freeze['directory']);old=read(A/'base-source-freeze.json');ck('594 inventory',len(freeze['files'])==len(old['files'])==594 and set(freeze['files'])==set(old['files']));ck('only fixture changed',{n for n,v in freeze['files'].items()if v!=old['files'][n]}=={'tests/test_solver.cpp'})
for n,v in freeze['files'].items():ck('frozen source '+n,sha(S/n)==v)
ck('complete isolated inventory',{str(p.relative_to(S))for p in S.rglob('*')if p.is_file()}==set(freeze['files']));ck('public private fixture equality',(S/'tests/test_solver.cpp').read_bytes()==(A/'test_solver.cpp').read_bytes())
# Required computed-data flow and unchanged numerical core are also reviewed manually.
start=text.index('std::string md_decimal_export(');end=text.index('\nint main()',start);export=text[start:end]
for name,fragment in {
 'actual Jet entries':'md_decimal_hex(out,r[row].d[column])',
 'actual native perturbations':'plus[j]+=step*scales[j]*direction[j];minus[j]-=step*scales[j]*direction[j];',
 'actual generated domain':'atlas::evaluate_model(model,plus,zn,de,p,rp)&&atlas::evaluate_model(model,minus,zn,de,p,rm)',
 'same branch guards':'md_fixture_branch(plus,p)==branch&&md_fixture_branch(minus,p)==branch',
 'finite generated residuals':'rp.size()==14&&rm.size()==14&&atlas::finite(rp)&&atlas::finite(rm)',
 'actual endpoint payload':'md_decimal_vector(out,sign==1?plus:minus)',
 'full14 columns':'for(int column=0;column<14;++column)',
 'both levels':'for(int level=0;level<2;++level)',
 'plusminus order':'for(int sign:{1,-1})',
 'actual parameters':'md_decimal_hex(out,p[i])',
 'actual state':'md_decimal_vector(out,z)',
 'actual previous':'md_decimal_vector(out,zn)',
 'actual scales':'md_decimal_vector(out,scales)',
 'classic locale':'out.imbue(std::locale::classic())'}.items():ck(name,fragment in export)
ck('no premature cout in export','std::cout'not in export)
reference=read(R/'reference.json')
for key in ['evaluator_sha256','policy_sha256','base_source_freeze_sha256','model_sha256','request_sha256']:
 ck('frozen reference literal '+key,reference[key]in export)
ck('frozen reference hash literal',sha(R/'reference.json')in export)
ck('binding runtime only','md_decimal_json_string(out,binding)'in export)
ck('buffered through final settings',text.index('decimal_payload=md_decimal_export(')<text.index('protocol failed to propagate material settings')<text.index('std::cout<<decimal_payload'))
ck('pairing before missing binding',text.index('MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5')<text.index('MD Decimal build binding must be 64 lowercase hex characters'))
ck('legacy full14 still unconditional outside newmode','if(!decimal_reference)for(int j=0;j<14;++j)'in text)
ck('only newmode skips full14 ref','md_fixture_derivatives(int(model),z,zn,p,scales,de,r,md_decimal);'in text)
print(json.dumps({'identity':'independent-decimal-cpp-source-review-v1','author_manifest_sha256':expected,'checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0,'source_only_no_numerical_pass':True},indent=2))
