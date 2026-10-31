"""Prospectively bounded native response/compatibility exercise with raw receipts."""
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csv(values):return ','.join(format(x,'.17g') for x in values)
def flat(model):return [v for f in model['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
def clean(data):return {k:v for k,v in data.items() if k!='elapsed_ms'}
def bits(values):return [struct.pack('>d',x).hex() for x in values]
def decode(text):return json.loads(text,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))


def exercise(stage,output):
    stage=Path(stage).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    pins=json.loads((stage/'pre-build.json').read_text())
    for p,h in pins['source_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in pins['generated_sha256'].items():assert sha(stage/p)==h,p
    freeze=json.loads(Path(__file__).with_name('freeze.json').read_text());policy=freeze['analytical_gate']
    expected_freeze=json.loads((stage/'assessment-freeze.json').read_text())
    assert expected_freeze['exercise_sha256']==sha(__file__)
    assert expected_freeze['policy_sha256']==sha(Path(__file__).with_name('freeze.json'))
    binaries={name:stage/'build'/name for name in ['atlas_scope_solver','atlas_scope_legacy_solver','atlas_scope_api_driver']}
    binary_pins={name:sha(path) for name,path in binaries.items()}
    calls=[]
    def capture(name,args,label,driver=False):
        binary=binaries[name];assert sha(binary)==binary_pins[name]
        command=[str(binary),*args];result=subprocess.run(command,capture_output=True,text=True,timeout=30)
        receipt=dict(label=label,command=command,binary_sha256=binary_pins[name],returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        filename=f'{len(calls):03d}.json';(output/filename).write_text(json.dumps(receipt,indent=2)+'\n');calls.append(filename)
        if driver:
            assert result.returncode==0,result.stderr
            return [decode(line) for line in result.stdout.splitlines()]
        data=decode(result.stdout);assert isinstance(data.get('ok'),bool)
        assert result.returncode==(0 if data['ok'] else 1),(label,receipt)
        return data
    new='atlas_scope_solver';old='atlas_scope_legacy_solver';base_scope=['--response-contract','stress-scope-0.1']
    models=json.loads((stage/'generated/models.json').read_text())['models'];public=[m for m in models if m['id']!='scope-synthetic-total-elastic'];assert len(public)==9
    for model in public:
        args=['--model',model['id'],'--initial',csv(flat(model)),'--protocol','0','--target','0','--steps','1']
        a=capture(old,args,'legacy-public-'+model['id']);b=capture(new,args,'current-public-'+model['id'])
        assert a['ok'] and b['ok'];assert clean(a)==clean(b),model['id']
    def scope_descriptor(data,scope,protocol):
        assert data['ok'],data
        assert data['api_version']=='experimental-laboratory-scope-0.1'
        assert data['stress']==dict(source='state',name='sigma',measure='cauchy',scope=scope,tensor_representation='mandel',sign='compression_positive')
        pore=data['pore_pressure']
        if scope=='effective' and protocol in [2,3]:
            assert pore==dict(quantity='change',availability='reconstructed',assumption='fixed_radial_total_stress_incompressible_fluid_and_grains')
            assert all(type(p['u']) in [int,float] and math.isfinite(p['u']) for p in data['points']);assert data['points'][0]['u']==0
        else:
            assert pore==dict(quantity='change',availability='unavailable',reason='total_stress_without_pore_pressure_law' if scope=='total' else 'not_reconstructed_for_protocol')
            assert all(p['u'] is None for p in data['points'])
    def same_mechanics(legacy,scoped,protocol):
        candidate=copy.deepcopy(scoped)
        for key in ['stress','pore_pressure','api_version']:candidate.pop(key)
        if 'api_version' in legacy:candidate['api_version']=legacy['api_version']
        for a,b in zip(legacy['points'],candidate['points']):
            if protocol not in [2,3]:b['u']=a['u']
        assert clean(candidate)==clean(legacy)
    for protocol in range(5):
        args=['--model','linear-elastic','--protocol',str(protocol),'--target',str(policy['stress_target'] if protocol==3 else policy['strain_target']),'--steps',str(policy['steps']),'--integration-settings','']
        a=capture(old,args,f'legacy-elastic-{protocol}');b=capture(new,args,f'current-elastic-{protocol}');c=capture(new,args+base_scope,f'scoped-elastic-{protocol}')
        assert a['ok'] and b['ok'];assert clean(a)==clean(b)
        scope_descriptor(c,'effective',protocol);same_mechanics(b,c,protocol)
    values=[0.,policy['strain_target']/2,policy['strain_target'],0.];wire=','.join(bits(values));(output/'controls.txt').write_text(wire)
    args=['--model','linear-elastic','--mode','run-controls','--protocol','1','--laboratory-controls-file',str(output/'controls.txt')]
    a=capture(old,args,'legacy-explicit');b=capture(new,args,'current-explicit');c=capture(new,args+base_scope,'scoped-explicit')
    assert a['ok'] and clean(a)==clean(b);scope_descriptor(c,'effective',1);same_mechanics(b,c,1)
    assert c['loading']['controls']==values and c['loading']['controls_bits']==bits(values)
    total=next(m for m in models if m['id']=='scope-synthetic-total-elastic');initial=csv(flat(total));E=policy['E'];nu=policy['nu'];G=E/(2*(1+nu));K=E/(3*(1-2*nu));lam=K-2*G/3;p0=policy['initial_pressure']
    max_stress_error=0.;max_strain_error=0.
    for protocol in range(5):
        args=['--model',total['id'],'--initial',initial,'--protocol',str(protocol),'--target',str(policy['stress_target'] if protocol==3 else policy['strain_target']),'--steps',str(policy['steps'])]
        data=capture(new,args+base_scope,f'total-analytical-{protocol}');scope_descriptor(data,'total',protocol);assert len(data['points'])==policy['steps']+1
        for point in data['points']:
            a=point['control']/(3*G) if protocol==3 else point['control']
            radial=0 if protocol==0 else -nu*a if protocol==1 else a if protocol==4 else -.5*a
            strain=[a,radial,radial,0,0,0];trace=a+2*radial
            stress=[p0+lam*trace+2*G*v for v in strain[:3]]+[0,0,0]
            se=max(abs(x-y) for x,y in zip(point['state'][:6],stress));ee=max(abs(x-y) for x,y in zip(point['strain'],strain))
            max_stress_error=max(max_stress_error,se);max_strain_error=max(max_strain_error,ee)
            assert se<=policy['stress_absolute_tolerance_Pa'] and ee<=policy['strain_absolute_tolerance']
    for mode,extra in [('run',[]),('run-controls',['--laboratory-controls-file',str(output/'controls.txt')])]:
        data=capture(new,['--model',total['id'],'--mode',mode,'--parameters','bad','--initial','bad',*extra],'legacy-total-reject-'+mode)
        assert data==dict(ok=False,message='legacy laboratory contract requires effective stress')
    for mode,contract in [('run','unknown'),('evaluate','stress-scope-0.1'),('run-research-controls','stress-scope-0.1')]:
        data=capture(new,['--model','linear-elastic','--mode',mode,'--response-contract',contract],'invalid-contract-'+mode)
        assert not data['ok'] and 'response contract' in data['message']
    (output/'bad-controls.txt').write_text('7ff8000000000000,0000000000000000')
    data=capture(new,['--model','linear-elastic','--mode','run-controls','--laboratory-controls-file',str(output/'bad-controls.txt'),*base_scope],'invalid-explicit-controls')
    assert not data['ok'] and 'finite' in data['message']
    driver=capture('atlas_scope_api_driver',[],'direct-c-api',True);assert len(driver)==5
    for data in driver[:3]:assert data==dict(ok=False,message='legacy laboratory contract requires effective stress')
    for data in driver[3:]:scope_descriptor(data,'total',2)
    for name,path in binaries.items():assert sha(path)==binary_pins[name]
    report=dict(status='passed',processes=len(calls),public_legacy_cases=9,elastic_legacy_cases=5,explicit_control_legacy_cases=1,total_analytical_protocols=5,max_stress_error_Pa=max_stress_error,max_strain_error=max_strain_error,receipts=calls,binary_sha256=binary_pins,scientific_admission=False)
    (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['receipts','binary_sha256']}));return report
if __name__=='__main__':exercise(sys.argv[1],sys.argv[2])
