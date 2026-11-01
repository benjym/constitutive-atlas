"""Independent saved-data build review. Process and artifact calls forbidden."""
import sys
sys.dont_write_bytecode = True
import ast, contextlib, hashlib, importlib.util, io, json, os, runpy
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[4]
R = ROOT/'docs/investigations/control-partition-derivative-v1'
OLD = R/'current-profile-actual-review-v1'
spec = importlib.util.spec_from_file_location('previous_saved_review', OLD/'review.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)  # This installs subprocess.run/Popen/os.system denials.
r.D = D
I = R/'current-profile-build-review-inputs-v1'

def check(name, condition):
    r.check(name, condition)

def captured(fn, *args, **kwargs):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        fn(*args, **kwargs)
    return json.loads(output.getvalue())

def run_saved(path, argv, expected, label):
    old = sys.argv
    sys.argv = [str(path), *map(str, argv)]
    try:
        value = captured(runpy.run_path, str(path), run_name='__main__')
    finally:
        sys.argv = old
    check(label, value == r.read(expected))
    r.save(label+'.json', value)
    return value

def packet(name, expected, plan, freeze, tools):
    # Reuse the previously reviewed archive/process/strict-receipt validator,
    # excluding only its Power/Burgers-specific generated-model assertions.
    source = (OLD/'review.py').read_text()
    tree = ast.parse(source)
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name=='packet')
    loop = next(x for x in fn.body if isinstance(x, ast.For) and isinstance(x.target, ast.Name) and x.target.id=='kind')
    cut = next(i for i,x in enumerate(loop.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='generated' for t in x.targets))
    loop.body = loop.body[:cut]
    class BuildMode(ast.NodeTransformer):
        def visit_Constant(self,node):
            if node.value=='CMAKE_BUILD_TYPE:STRING=Release':
                return ast.copy_location(ast.Constant('CMAKE_BUILD_TYPE:STRING='+('Debug' if name=='norsand' else 'Release')),node)
            return node
    fn = BuildMode().visit(fn)
    scope = dict(r.__dict__)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])), 'saved-profile-common-binding', 'exec'), scope)
    spec, work = scope['packet'](name,expected,plan,freeze,tools)
    for kind in ['native','wasm']:
        build = work/(kind+'-build')
        if name!='norsand':
            generated=build/'generated';g=r.read(generated/'models.json')
            model='models/research/orthotropic/orthotropic-ogs-linear-elastic.json' if name=='orthotropic' else 'models/research/maxwell/maxwell-itasca900-dry-zero-spin-ode.json'
            # Exact model path is established by the generated entry and source inventory.
            check(name+kind+' single generated model', len(g['models'])==1)
            matches=[p for p in r.S.glob('models/**/*.json') if r.read(p)==g['models'][0]]
            check(name+kind+' exact source model',len(matches)==1)
            canonical=hashlib.sha256(json.dumps(g['models'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
            check(name+kind+' canonical generated/header',g['sha256']==canonical and canonical in (generated/'models.hpp').read_text())
        else:
            g=r.read(build/'generated/path_catalogue.json')
            check(kind+' NorSand generated same across builds',g==r.read(work/'wasm-build/generated/path_catalogue.json'))
    return work

def orthotropic(work):
    study=r.load('saved_orthotropic_source',r.S/'tools/orthotropic_reference.py')
    cases=r.read(r.S/'docs/ingestion/orthotropic-ogs/execution-v1/references.json')['cases']
    check('orthotropic exact rational source corpus reproduced',study.corpus()==cases)
    for kind,path in [('native',work/'evidence/native/raw.json'),('wasm',work/'evidence/wasm-raw.json')]:
        raw=r.read(path); report=study.assess(cases,raw)
        if kind=='native':report['solver_sha256']=r.sha(work/'native-build/atlas_orthotropic_solver')
        expected=work/('evidence/native/assessment.json' if kind=='native' else 'evidence/wasm-assessment.json')
        check('orthotropic '+kind+' unchanged source assessor',report==r.read(expected))
        r.save('orthotropic-'+kind+'-recomputed.json',report)
    dest=D/'orthotropic-paired-recomputed.json'
    if dest.exists(): dest.unlink()
    run_saved(r.P/'assess_pairs.py',['orthotropic',work/'evidence/native/raw.json',work/'evidence/wasm-raw.json',dest],work/'evidence/paired-assessment.json','orthotropic-paired')

def maxwell(work):
    m=r.load('saved_maxwell_source',r.S/'tests/test_maxwell.py')
    cases=r.read(r.S/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json')['cases']
    check('Maxwell regenerated original references',m.make_cases()==cases)
    transactions=r.load('saved_maxwell_transactions',r.P/'adapters/check_maxwell_transactions.py')
    for kind in ['native','wasm']:
        rows=r.read(work/('evidence/'+kind+'-raw.json'))
        report=m.assess_rows(cases,rows)
        expected=work/('evidence/processes/'+('native-collect-assess' if kind=='native' else 'wasm-assess')+'/stdout')
        check('Maxwell '+kind+' source assessment exact', report == r.read(expected))
        r.save('maxwell-'+kind+'-source.json',report)
        tc=transactions.cases_for(work/('evidence/'+kind+'-raw.json'))
        check('Maxwell '+kind+' transaction requests reproduced', tc==r.read(work/('evidence/'+kind+'-transaction-cases.json'))['cases'])
        errors=transactions.assess(tc,r.read(work/('evidence/'+kind+'-transactions-raw.json')))
        saved=r.read(work/('evidence/'+kind+'-transactions.json'))
        check('Maxwell '+kind+' source transaction errors exact',errors==saved['errors_Pa'] and saved['passed'] is True and saved['recovery_pairs']==6 and saved['actual_endpoint_restarts']==2)
        r.save('maxwell-'+kind+'-transaction-recomputed.json',errors)
    check('Maxwell CLI exact saved replay',r.read(work/'evidence/cli/first.json')==r.read(work/'evidence/cli/replay.json')==r.read(work/'evidence/cli-creep-result.json'))
    check('Maxwell untimed rejection',r.read(work/'evidence/native-transactions.json')['CLI_replay_exact'] is True and json.loads(r.read(work/'evidence/native-transactions.json')['untimed_rejection_raw'])['ok'] is False)
    # Execute the original parity block after removing ONLY its output-file write.
    tree=ast.parse((r.P/'adapters/compare_maxwell.py').read_text())
    tree.body=[x for x in tree.body if not (isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Attribute) and x.value.func.attr=='write_text')]
    ns={'__name__':'saved_only_parity'};out=io.StringIO()
    with contextlib.redirect_stdout(out):exec(compile(tree,'saved-Maxwell-parity','exec'),ns)
    report=json.loads(out.getvalue());check('Maxwell original parity exact',report==r.read(work/'evidence/parity-results-v2.json'));r.save('maxwell-parity-recomputed.json',report)
    dest=D/'maxwell-presets-recomputed.json'
    if dest.exists():dest.unlink()
    run_saved(r.P/'assess_maxwell_presets.py',[dest],work/'evidence/presets-assessment.json','maxwell-presets')
    interface=(work/'evidence/processes/interface-contract-lifecycle/stdout').read_text()
    check('Maxwell actual interface suite passes', 'ℹ fail 0' in interface and 'ℹ pass 21' in interface and 'ℹ skipped 0' in interface and 'ℹ cancelled 0' in interface)

def norsand(work):
    path=r.S/'docs/ingestion/norsand-1993/e2-v3'
    checker=r.load('saved_norsand_source',path/'check_backend_results_v3.py')
    req=path/'backend-requests-v2.json'
    rows=r.read(req)['requests']
    policy=r.read(path/'reference_policy-v2.json');refs=r.read(path/'references-v2.json');qual=r.read(path/'interpreter-qualification-v1.json')
    check('NorSand independent reference policy/script bindings',refs['policy_sha256']==r.sha(path/'reference_policy-v2.json') and refs['script_sha256']==r.sha(path/'build_references_v2.py'))
    check('NorSand independent reference/interpreter inventory',len(refs['cases'])==len(qual['rows'])==9 and qual['references_sha256']==r.sha(path/'references-v2.json') and qual['source_policy_sha256']==r.sha(path/'reference_policy-v2.json'))
    for row in refs['cases']:
        check('NorSand independent reference refinement '+row['id'],float(row['refinement_error'])<=float(policy['reference_refinement_max_normalized']) and float(row['precision_error'])<=float(policy['reference_precision_max_normalized']))
    for row in qual['rows']:
        check('NorSand interpreter independent reference agreement '+row['id'],row['max_reference_error']<=float(policy['candidate_reference_max_normalized']) and row['kinematic_invariant_relative']<=float(policy['kinematic_invariant_max_relative']) and row['rejection_checks']==5)
    check('NorSand exact request outcome inventory',len(rows)==58 and sum(x['expected_status']==1 for x in rows)==40 and sum(x['expected_status']==0 for x in rows)==18)
    for names,label in [(['native'],'native-assess'),(['wasm'],'wasm-assess'),(['native','wasm'],'paired-assess')]:
        report=captured(checker.main,str(req),*[str(work/('evidence/'+n+'.json')) for n in names])
        check('NorSand original '+label+' exact',report==r.read(work/('evidence/processes/'+label+'/stdout')))
        r.save('norsand-'+label+'-recomputed.json',report)

def build_binding(name,work):
    request=r.read(I/(name+'-review-request.json'));body=r.read(I/(name+'-qualification-body.json'))
    matcher=r.read(I/(name+('-source149.json' if name=='maxwell' else '-source121.json')))
    check(name+' qualification body/request exact',r.sha(I/(name+'-qualification-body.json'))==request['qualification_body_sha256'] and body['binding']==request['required_review']['binding'] and body['gates']==request['required_review']['gates'] and body['implementation_run']=='/root')
    files=matcher['files'];check(name+' exact matcher count',len(files)==(149 if name=='maxwell' else 121))
    for path,h in files.items():check(name+' matched source '+path,r.sha(r.S/path)==h)
    digest=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    check(name+' source matcher canonical hash',matcher['sha256']==digest)
    binding=body['binding'];build=work/'wasm-build'
    if name=='maxwell':
        builder=r.load('saved_maxwell_builder_for_hashes_only',r.S/'tools/build_maxwell_laboratory.py')
        check('Maxwell matcher equals actual builder source closure',builder.source_manifest()==matcher)
        actual={'model_sha256':r.sha(r.S/builder.DEFINITION),'catalogue_file_sha256':r.sha(build/'generated/models.json'),'module_sha256':r.sha(build/'maxwell.js'),'wasm_sha256':r.sha(build/'maxwell.wasm'),'source_manifest_sha256':digest,'reference_policy_sha256':r.sha(r.S/builder.REFERENCE)}
        check('Maxwell exact actual build binding',binding==actual)
    else:
        required={p.relative_to(r.S).as_posix() for p in (r.S/'cpp/include/atlas').rglob('*.hpp')}
        required.update(p.relative_to(r.S).as_posix() for p in (r.S/'cpp/scalar-functions').rglob('*') if p.is_file())
        required.update(p.relative_to(r.S).as_posix() for p in (r.S/'atlas').rglob('*.py') if '__pycache__' not in p.parts)
        required.update(p.relative_to(r.S).as_posix() for p in (r.S/'schemas').rglob('*.json'))
        required.update(('cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'))
        check('NorSand exact actual builder source closure',set(files)==required and binding['sources']==files)
        check('NorSand exact actual artifacts/generated',binding['artifacts']=={n:r.sha(build/n) for n in ['atlas_path_capability.mjs','atlas_path_capability.wasm']} and binding['generated']=={n:r.sha(build/'generated'/n) for n in ['path_catalogue.json','path_models.hpp','path_api.cpp']})
    return body

def main():
    r.manifest(I/'manifest.json','968fb1bfb0ada14ddd38548d1ca0bbe9f4bb89b50abfa42b4d7c894f8fd614e7')
    for name,h in r.read(I/'inputs.json').items():check('review input '+name,r.sha(name)==h)
    plan,freeze,tools=r.common()
    # Reuse independently accepted prior four studies only after exact review bindings.
    for name,h in [('power-burgers','3529db32e43aa763acd269d3497e88a8d5758c0c7e4ee6ec9a9f54f458f00791'),('sls','ee4220efd55c22392d0e79c9e898da654d1e09f77076fe0292b1cc4530f5215b'),('j2','c197f6c1420eb36ebafe28b6d41f41087629d4d98379f2ebde362edd3a0314fc')]:
        check('prior accepted exact manifest '+name,r.sha(OLD/(name+'-manifest-v1.json'))==h)
        data=r.read(OLD/(name+'-manifest-v1.json'))
        for key in ['files','review_files','inputs']:
            for p,h in data.get(key,{}).items():
                q=Path(p) if Path(p).is_absolute() else OLD/p
                check('prior accepted review '+str(q),r.sha(q)==h)
    for name,h,fn in [('orthotropic','bdeacdc3e55d35a351aec8503a4778d363042ea05e39375184b1b6051d5e6729',orthotropic),('maxwell','11fec3d0450f62ac861bf0a2556dce6aace59cac20babe2833c9ab2a1e21ce5b',maxwell),('norsand','4c4dd4c91b9db1152bf19e606fcf67f86be02d6f388008430103ef0558dfb50c',norsand)]:
        work=packet(name,h,plan,freeze,tools)
        os.environ['ATLAS_QUALIFICATION_SOURCE']=str(r.S)
        os.environ['ATLAS_QUALIFICATION_OUTPUT']=str(work/'evidence')
        sys.path.insert(0,str(r.S))
        fn(work)
        if name in ['maxwell','norsand']:build_binding(name,work)
    r.save('checks-final-v1.json',{'passed':True,'count':len(r.checks),'checks':r.checks,'compiled_calls':0,'process_execution_disabled':True})
    print(json.dumps({'passed':True,'checks':len(r.checks),'compiled_calls':0}))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        r.save('retained-failure-'+str(len(list(D.glob('retained-failure-*.json'))))+'.json',{'type':type(exc).__name__,'error':str(exc),'checks':r.checks})
        raise
