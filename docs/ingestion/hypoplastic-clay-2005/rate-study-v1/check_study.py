"""Portable Python-only replay. No compiler or author implementation invocation."""
import argparse,hashlib,json,math,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--source',type=Path);a=p.parse_args()
    repo=a.repo
    if repo is None:repo=next((r for r in HERE.parents if(r/'atlas/model.py').is_file()),None)
    if repo is None:raise ValueError('supply --repo pointing to Atlas checkout for generic interpreter checks')
    sys.path.insert(0,str(repo.resolve()))
    import reference as independent
    if a.source and hashlib.sha256(a.source.read_bytes()).hexdigest()!=independent.SOURCE_SHA256:raise ValueError('wrong source bytes')
    from atlas.model import load,defaults,prepare_increment,evaluation_environment
    model=load(HERE/'model.json');params=defaults(model);reference=independent.build_reference()
    if reference!=json.loads((HERE/'reference.json').read_text()):raise ValueError('frozen reference does not match fresh oracle')
    observed=[];maximum_scaled=0.;maximum_void=0.
    for c in reference['cases']:
        z,E=c['state'],c['increment'];state=dict(sigma=z[:6],e=z[6]);par=params|c['parameters']
        prepare_increment(model,state,E,par);env=evaluation_environment(model,state,state,E,par)
        got=list(env['stress_rate'].v)+[env['e_rate']]
        stress=max(abs(x-y)for x,y in zip(got[:6],c['expected'][:6]));void=abs(got[6]-c['expected'][6])
        bound=reference['policy']['stress_absolute_floor_Pa']+reference['policy']['stress_relative_to_scale']*c['stress_scale']
        vbound=reference['policy']['void_absolute_floor']+reference['policy']['void_relative_to_scale']*c['void_scale']
        if stress>bound or void>vbound:raise ValueError('predeclared comparison failed '+c['id'])
        maximum_scaled=max(maximum_scaled,stress/max(c['stress_scale'],1e-300));maximum_void=max(maximum_void,void)
        observed.append(dict(id=c['id'],got=got,max_stress_error_Pa=stress,void_error=void,stress_bound_Pa=bound,void_bound=vbound))
    import test_rate
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_rate);result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise ValueError('unit groups failed')
    runtime_pins={str(q):hashlib.sha256((repo/q).read_bytes()).hexdigest()for q in ['atlas/dsl.py','atlas/model.py','schemas/model.schema.json']}
    report=dict(version='clay2005-python-rate-comparison-0.1',source_sha256=independent.SOURCE_SHA256,model_sha256=hashlib.sha256((HERE/'model.json').read_bytes()).hexdigest(),oracle_sha256=hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest(),reference_sha256=hashlib.sha256((HERE/'reference.json').read_bytes()).hexdigest(),runtime_pins=runtime_pins,passed=True,cases=len(observed),unittest_groups=result.testsRun,maximum_stress_error_over_scale=maximum_scaled,maximum_void_error=maximum_void,observations=observed,limitations=reference['limitations'],compiled_execution=False)
    a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(f'{len(observed)} all-seven Python comparisons and {result.testsRun} test groups passed')


if __name__=='__main__':main()
