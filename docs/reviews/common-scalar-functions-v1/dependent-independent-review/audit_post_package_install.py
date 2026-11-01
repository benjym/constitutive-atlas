"""Read-only post-install identity audit; no builder or compiled calls."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent;I=R/'docs/ingestion/duncan-chang-1970/integration-v2';pins={};errors=[]
def sha(p):
    p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def load(p):sha(p);return json.loads(Path(p).read_text())
def check(ok,label):
    if not ok:errors.append(label)
installed=load(B/'package-installed-v1.json');plan=load(B/'package-preservation-v1/preservation-plan.json');proposal=load(B/'package-proposal-freeze-v4.json')
check(installed['preservation_plan_sha256']==sha(B/'package-preservation-v1/preservation-plan.json') and installed['proposal_sha256']==sha(B/'package-proposal-freeze-v4.json'),'installed plan/proposal identity')
expected={str(Path(p).relative_to('docs/reviews/common-scalar-functions-v1/package-proposal-v4')):h for p,h in proposal['files'].items()}
check(installed['files']==expected and len(expected)==3 and installed['documents_unchanged'] is True,'three exact installed targets')
for p,h in expected.items():check(sha(R/p)==h,'installed '+p)
for p,row in plan['planned_sidecars'].items():check(sha(R/p)==row['proposed_sha256']==sha(R/row['proposed_path']),'installed map '+p)
for p,h in plan['document_pins'].items():check(sha(R/p)==h,'original document '+p)
for row in plan['bindings']:check(sha(R/row['archived_path'])==row['sha256'],'preserved archive '+row['archived_path'])
for p,h in load(O/'package-install-bindings-v1.json')['files'].items():check(sha(R/p)==h,'accepted pre-install review binding '+p)
maxmanifest=load(O/'build-local-v2/maxwell/source-manifest.json')
packager=R/'tools/build_maxwell_laboratory.py';tree=ast.parse(packager.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['source_manifest','digest']]
ns={'ROOT':R,'DEFINITION':'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json','hashlib':hashlib,'json':json};exec(compile(ast.Module(body=functions,type_ignores=[]),str(packager),'exec'),ns)
check(ns['source_manifest']()==maxmanifest and len(maxmanifest['files'])==149,'actual installed Maxwell149 closure')
for p,h in maxmanifest['files'].items():check(sha(R/p)==h,'Maxwell source '+p)
nor=load(O/'build-local-v1/norsand/controlled-path-qualification.json');sources=nor['binding']['sources'];required={p.relative_to(R).as_posix() for p in (R/'cpp/include/atlas').rglob('*.hpp')}
required.update(p.relative_to(R).as_posix() for p in (R/'cpp/scalar-functions').rglob('*') if p.is_file());required.update(p.relative_to(R).as_posix() for p in (R/'atlas').rglob('*.py') if '__pycache__' not in p.parts);required.update(p.relative_to(R).as_posix() for p in (R/'schemas').rglob('*.json'))
required.update(['cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'])
check(set(sources)==required and len(required)==121,'actual NorSand121 closure')
for p,h in sources.items():check(sha(R/p)==h,'NorSand source '+p)
current=load(I/'current-engine-inputs.json')['files'];check(len(current)==14,'fourteen current dependent inputs')
for row in current:check(sha(row['path'])==sha(row['source'])==row['sha256'],'current package input '+row['path'])
for name,version in [('maxwell',2),('norsand',1)]:
    folder=Path('/private/tmp/atlas-duncan-integration-v2/current-inputs')/name;q=load(folder/('maxwell-qualification.json' if name=='maxwell' else 'controlled-path-qualification.json'));review=load(folder/'build-review.json')
    check(sha(folder/'build-review.json')==q['independent_review']['sha256'] and review['binding']==q['binding'] and review['gates']==q['gates'] and review['reviewer_run']!=q['implementation_run'],'current accepted paired receipt '+name)
    for p in (O/f'build-local-v{version}'/name).iterdir():check(sha(p)==sha(folder/p.name),'exact supplied build local receipt '+name+'/'+p.name)
retained=load(I/'retained-engine-inputs.json');prior=load(R/'docs/ingestion/duncan-chang-1970/integration-v1/package-manifest-v2.json')
check(sha(R/'docs/ingestion/duncan-chang-1970/integration-v1/package-manifest-v2.json')==retained['prior_package_manifest_sha256'] and prior['file_count']==928,'prior928 package identity')
check(len(retained['artifacts'])==12,'twelve retained older engine inputs')
for row in retained['artifacts']:
    rel=Path(row['original_path']).relative_to(prior['source_path']).as_posix();check(prior['files'][rel]==row['sha256']==sha(row['original_path'])==sha(row['retained_input']),'unchanged retained input '+rel)
result=dict(identity='common-scalar-three-packager-post-install-independent-v1',pass_=not errors,failures=errors,installed_packagers=3,installed_maps=16,original_documents=27,archive_bindings=46,Maxwell_source_paths=149,NorSand_source_paths=121,current_dependent_inputs=14,retained_older_engine_inputs=12,compiled_execution=False,standard_package_acceptance=False,E6_E7_acceptance=False,checked_files=pins)
(O/'post-package-install-audit-results-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checked_files'},indent=2));raise SystemExit(bool(errors))
