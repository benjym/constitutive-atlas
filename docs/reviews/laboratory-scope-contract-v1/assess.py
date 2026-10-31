"""Recheck saved laboratory scope receipts without binaries or subprocesses."""
import copy
import hashlib
import json
import re
from pathlib import Path
import struct
import sys

def read(path):return json.loads(Path(path).read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
def clean(data):return {k:v for k,v in data.items() if k!='elapsed_ms'}
def descriptor(data,scope,protocol):
    assert data['ok'] and data['api_version']=='experimental-laboratory-scope-0.1'
    assert data['stress']==dict(source='state',name='sigma',measure='cauchy',scope=scope,tensor_representation='mandel',sign='compression_positive')
    expected=dict(quantity='change',availability='reconstructed',assumption='fixed_radial_total_stress_incompressible_fluid_and_grains') if scope=='effective' and protocol in [2,3] else dict(quantity='change',availability='unavailable',reason='total_stress_without_pore_pressure_law' if scope=='total' else 'not_reconstructed_for_protocol')
    assert data['pore_pressure']==expected
    if expected['availability']=='unavailable':assert all(p['u'] is None for p in data['points'])
    else:assert all(type(p['u']) in [int,float] for p in data['points']) and data['points'][0]['u']==0

def mechanics(a,b,protocol):
    b=copy.deepcopy(b)
    for k in ['stress','pore_pressure','api_version']:b.pop(k)
    if 'api_version' in a:b['api_version']=a['api_version']
    assert len(a['points'])==len(b['points'])
    for x,y in zip(a['points'],b['points']):
        if protocol not in [2,3]:y['u']=x['u']
    assert clean(a)==clean(b)

def assess(packet):
    packet=Path(packet);summary=read(packet/'observations/summary.json');catalogue=read(packet/'generated-models.json');pre=read(packet/'pre-build.json')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(packet/'generated-models.json')==pre['generated_sha256']['generated/models.json']
    freeze=read(packet/'assessment-freeze.json');assert sha(packet/'exercise.py')==freeze['exercise_sha256'] and sha(packet/'freeze.json')==freeze['policy_sha256']
    records=[read(packet/'observations'/name) for name in summary['receipts']];assert len(records)==summary['processes']==48
    by={record['label']:record for record in records};assert len(by)==len(records)
    public=[m for m in catalogue['models'] if m['id']!='scope-synthetic-total-elastic'];assert len(public)==9
    expected={prefix+m['id'] for m in public for prefix in ['legacy-public-','current-public-']}
    expected|={f'{prefix}-elastic-{p}' for prefix in ['legacy','current','scoped'] for p in range(5)}
    expected|={'legacy-explicit','current-explicit','scoped-explicit',*[f'total-analytical-{p}' for p in range(5)],'legacy-total-reject-run','legacy-total-reject-run-controls','invalid-contract-run','invalid-contract-evaluate','invalid-contract-run-research-controls','invalid-explicit-controls','direct-c-api'}
    assert set(by)==expected
    def data(label):
        receipt=by[label];driver=label=='direct-c-api'
        binary='atlas_scope_api_driver' if driver else 'atlas_scope_legacy_solver' if label.startswith('legacy-public-') or label.startswith('legacy-elastic-') or label=='legacy-explicit' else 'atlas_scope_solver'
        assert Path(receipt['command'][0]).name==binary and receipt['binary_sha256']==summary['binary_sha256'][binary]
        if driver:
            assert receipt['returncode']==0;return [json.loads(line) for line in receipt['stdout'].splitlines()]
        out=json.loads(receipt['stdout']);assert receipt['returncode']==(0 if out['ok'] else 1)
        if out['ok']:
            assert out['catalogue_hash']==catalogue['sha256']
            args=dict(zip(receipt['command'][1::2],receipt['command'][2::2]));assert out['model']==args['--model']
            assert out['protocol']==int(args.get('--protocol',1))
            if label.startswith('scoped-') or label.startswith('total-'):assert args['--response-contract']=='stress-scope-0.1'
        return out
    def raw_legacy_equal(left,right):
        strip=lambda text:re.sub(r'("elapsed_ms":)[0-9eE.+-]+',r'\1<elapsed>',text)
        assert strip(by[left]['stdout'])==strip(by[right]['stdout'])
    for model in public:
        left='legacy-public-'+model['id'];right='current-public-'+model['id']
        a=data(left);b=data(right);assert a['ok'] and clean(a)==clean(b);raw_legacy_equal(left,right)
    for p in range(5):
        a=data(f'legacy-elastic-{p}');b=data(f'current-elastic-{p}');c=data(f'scoped-elastic-{p}');assert a['ok'] and clean(a)==clean(b);descriptor(c,'effective',p);mechanics(b,c,p);raw_legacy_equal(f'legacy-elastic-{p}',f'current-elastic-{p}')
    a=data('legacy-explicit');b=data('current-explicit');c=data('scoped-explicit');assert a['ok'] and clean(a)==clean(b);descriptor(c,'effective',1);mechanics(b,c,1);raw_legacy_equal('legacy-explicit','current-explicit')
    policy=read(packet/'freeze.json')['analytical_gate'];values=[0.,policy['strain_target']/2,policy['strain_target'],0.]
    assert c['loading']['controls']==values and c['loading']['controls_bits']==[struct.pack('>d',x).hex() for x in values]
    E=policy['E'];nu=policy['nu'];G=E/(2*(1+nu));K=E/(3*(1-2*nu));lam=K-2*G/3;p0=policy['initial_pressure'];max_stress=0.;max_strain=0.
    for p in range(5):
        out=data(f'total-analytical-{p}');descriptor(out,'total',p);assert len(out['points'])==policy['steps']+1
        for point in out['points']:
            axial=point['control']/(3*G) if p==3 else point['control'];radial=0 if p==0 else -nu*axial if p==1 else axial if p==4 else -.5*axial
            strain=[axial,radial,radial,0,0,0];stress=[p0+lam*(axial+2*radial)+2*G*v for v in strain[:3]]+[0,0,0]
            max_stress=max(max_stress,max(abs(x-y) for x,y in zip(point['state'][:6],stress)));max_strain=max(max_strain,max(abs(x-y) for x,y in zip(point['strain'],strain)))
    assert max_stress==summary['max_stress_error_Pa'] and max_strain==summary['max_strain_error']
    assert max_stress<=policy['stress_absolute_tolerance_Pa'] and max_strain<=policy['strain_absolute_tolerance']
    for mode in ['run','run-controls']:assert data('legacy-total-reject-'+mode)==dict(ok=False,message='legacy laboratory contract requires effective stress')
    for mode in ['run','evaluate','run-research-controls']:
        out=data('invalid-contract-'+mode);assert not out['ok'] and 'response contract' in out['message']
    out=data('invalid-explicit-controls');assert not out['ok'] and 'finite' in out['message']
    driver=data('direct-c-api');assert len(driver)==5
    for out in driver[:3]:assert out==dict(ok=False,message='legacy laboratory contract requires effective stress')
    for out in driver[3:]:descriptor(out,'total',2)
    assert summary['status']=='passed' and summary['scientific_admission'] is False
    return dict(status='passed',saved_processes=len(records),max_stress_error_Pa=max_stress,max_strain_error=max_strain,native_calls=0,builds=0)
if __name__=='__main__':print(json.dumps(assess(Path(__file__).parent)))
