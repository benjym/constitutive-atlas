"""Prepare proposed source/test artifacts only; never changes or executes the runtime."""
import copy,difflib,hashlib,json,pathlib
B=pathlib.Path(__file__).resolve().parent;R=B.parents[3]
source=R/'cpp/include/atlas/schedule.hpp';old=source.read_text()
helper='''// Optional admissible forward-Euler state guess; never a committed update.
// Current strain controls supply rates; solved prior rates seed stress controls.
inline bool controlled_forward_euler_guess(int model,const ControlledState& previous,const State& p,
                                           double t0,double t1,const ControlPath& path,const State& scales,
                                           const State& output_scales,State& u) {
    const int n=int(previous.state.size());const double h=t1-t0;
    if(!std::isfinite(t0)||!std::isfinite(t1)||!std::isfinite(h)||!(h>0))return false;
    Sym<double> rate=path.rates;
    for(int j:control_components(model))if(path.stress[j])rate.v[j]=previous.rate.v[j];
    if(models()[model].axisymmetric)rate.v[2]=rate.v[1];
    if(!std::isfinite(norm(rate)))return false;
    State f;
    if(!evaluate_model(model,previous.state,previous.state,rate,p,f,false,t0)||
       f.size()!=previous.state.size()||!finite(f))return false;
    State candidate=u;
    for(int i=0;i<n;++i)candidate[i]=previous.state[i]+h*f[i];
    State residual;
    if(!finite(candidate)||!controlled_residual(model,candidate,previous.state,p,t0,t1,path,scales,output_scales,residual)||
       !finite(residual))return false;
    u=std::move(candidate);return true;
}
'''
needle='inline bool controlled_backward_euler('
assert old.count(needle)==1
new=old.replace(needle,helper+needle,1)
needle2='    if(count>max_derivatives)return false;\n    for(int iteration=0;iteration<settings.maximum_iterations;++iteration){'
assert new.count(needle2)==1
new=new.replace(needle2,'    if(count>max_derivatives)return false;\n    // An inadmissible predictor leaves the original previous-state guess intact.\n    controlled_forward_euler_guess(model,previous,p,t0,t1,path,scales,os,u);\n    for(int iteration=0;iteration<settings.maximum_iterations;++iteration){',1)
(B/'proposed-schedule.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/cpp/include/atlas/schedule.hpp',tofile='b/cpp/include/atlas/schedule.hpp')))
base=json.loads((R/'docs/ingestion/bingham-comsol63/source-v1/candidate.json').read_text())
def fixture(name,states,eq,domain):
 d={k:copy.deepcopy(base[k]) for k in ['schema_version','formulation','status']}
 d.update(id=name,name='Synthetic '+name,family='engine verification only',description='Independent mathematical engine fixture, not a material admission.',sources=[{'url':'https://github.com/benjym/constitutive-atlas/blob/main/docs/TIMED_SCHEDULES.md','role':'analytical verification specification','locator':'Prospective generic predictor-plan-v1 synthetic law; no vendor identity'}],parameters={'tau':{'default':1,'min':1e-6,'max':1e6,'unit':'s'},'Kmod':{'default':1,'min':1e-6,'max':1e6,'unit':'Pa'}},state=[{'name':n,'shape':'scalar','unit':'1','scale':'1','initial':v,'semantics':{'role':'persistent','quantity':'verification_scalar','transformation':'scalar_invariant'}} for n,v in states],derived=[],equations=eq,domain=domain,initial_checks=domain,initialization={'method':'explicit_state','default_policy':'examples_only','required_state':[n for n,_ in states],'validation':'domain_and_initial_checks'},observables=[{'name':'stress','shape':'sym','unit':'Pa','scale':'Kmod','expr':'Kmod * ('+('x')+') * I'}])
 
 if name.endswith('clock'):
  d['parameters']['time_limit']={'default':1000,'min':.001,'max':1e9,'unit':'s'};d['domain']=['time < time_limit'];d['initial_checks']=d['domain']
 (B/'fixtures'/f'{name}.json').write_text(json.dumps(d,indent=2)+'\n')
fixture('test-predictor-boundary',[('x',.125),('alpha',0)],{'x':'trace(strain_rate)','alpha':'max(x,0) / tau'},['alpha >= 0'])
fixture('test-predictor-fallback',[('x',1)],{'x':'-x / tau'},['x >= 0'])
fixture('test-predictor-clock',[('x',0)],{'x':'time / tau**2'},[])
inputs=['cpp/include/atlas/schedule.hpp','cpp/include/atlas/time.hpp','tests/test_schedule.py','tests/test_time.cpp','tests/fixtures/time/kelvin.json','tests/fixtures/time/maxwell.json','tests/fixtures/time/maxwell-axisymmetric.json','docs/ingestion/bingham-comsol63/execution-v3-failure-review-v1/REPORT.md','docs/ingestion/bingham-comsol63/execution-v3-failure-review-v1/BINDINGS.json','docs/ingestion/bingham-comsol63/execution-v3/freeze-v1.json','docs/ingestion/bingham-comsol63/execution-v3/cases.json']
(B/'source-bindings.json').write_text(json.dumps({'identity':'generic-predictor-plan-source-bindings-v1','inputs':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in inputs},'source_edits':0,'compiled_calls':0,'builds':0},indent=2)+'\n')
print('Prepared patch and three independent synthetic fixture drafts; no runtime changed')
