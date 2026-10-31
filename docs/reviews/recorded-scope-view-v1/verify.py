"""Saved-only recorded browser qualification; no compiled artifact required."""
import copy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.recorded_scope_execution import verify_scoped_recorded_response
from tests.scoped_recorded_execution_cases import retained

def read(p):return json.loads(p.read_text())
def compare(a,b):
    if type(b) in (float,int):
        assert type(a) in (float,int) and math.isfinite(a)
        assert abs(a-b)<=1e-9*max(1,abs(b))
        if float(b).is_integer():assert a==b
    elif isinstance(b,dict):
        assert isinstance(a,dict) and set(a)==set(b)
        for k in b:compare(a[k],b[k])
    elif isinstance(b,list):
        assert isinstance(a,list) and len(a)==len(b)
        for x,y in zip(a,b):compare(x,y)
    else:assert type(a)==type(b) and a==b

def assess(packet):
    packet=Path(packet);data=read(packet/'inputs.json');catalogue,retained_rows=retained()
    assert data['catalogue']==catalogue
    labels=['scope-reversal','scope-failed-1','total-mixed']
    public=[m for m in catalogue['models'] if m['id']!='scope-synthetic-total-elastic']
    assert len(public)==9 and len(data['rows'])==12
    assert [r['label'] for r in data['rows']]==labels+['new-public-'+m['id'] for m in public]
    expected={r['label']:r for r in retained_rows}
    for row in data['rows'][:3]:assert row==expected[row['label']]
    native=ROOT/'docs/reviews/recorded-scope-native-v1';cases=read(native/'cases.json')
    for row in data['rows'][3:]:
        i=next(i for i,c in enumerate(cases) if c['label']==row['label']);case=cases[i]
        assert row['response']==json.loads(read(native/'observations'/f'{i:03d}.json')['stdout'])
        assert row['request']['model']==case['model'] and row['request']['initial']==case['initial']
        assert row['request']['version']=='experimental-recorded-run-0.1'
        assert [v for knot in row['request']['path']['knots'] for v in [knot['coordinate'],*knot['targets']]]==case['knots']
        assert [v for c in row['request']['path']['controls'] for v in [int(c['kind']=='stress'),*c['coefficients']]]==case['controls']
    actual=read(packet/'responses.json');assert len(actual)==12
    for row,observation in zip(data['rows'],actual):
        assert observation['label']==row['label'];compare(observation['result'],row['response'])
        s=copy.deepcopy(row['request']);out=copy.deepcopy(observation['result'])
        if s['version']=='experimental-recorded-run-0.1':
            s.update(version='experimental-recorded-run-0.2',stress_scope='effective')
            out.update(api_version='experimental-recorded-replay-0.2',stress=dict(source='state',name='sigma',measure='cauchy',scope='effective',tensor_representation='mandel',sign='compression_positive'))
        verify_scoped_recorded_response(out,s,catalogue)
    for label,name in [('scope-reversal','effective'),('scope-failed-1','failure'),('total-mixed','total')]:
        doc=read(packet/f'browser-{name}.json');row=expected[label]
        assert set(doc)=={'schema_version','catalogue_hash','specification','result'}
        assert doc['schema_version']=='experimental-recorded-replay-export-0.2' and doc['catalogue_hash']==catalogue['sha256']
        assert doc['specification']==row['request'];compare(doc['result'],row['response'])
        verify_scoped_recorded_response(doc['result'],doc['specification'],catalogue)
    doc=read(packet/'browser-legacy.json');assert doc['schema_version']=='experimental-recorded-replay-export-0.1' and doc['catalogue_hash']==catalogue['sha256']
    assert doc['specification']==read(ROOT/'protocols/recorded-linear-elastic-run.json')
    assert doc['result']['api_version']=='experimental-recorded-replay-0.1' and doc['result']['ok'] is True and len(doc['result']['points'])==5 and 'stress' not in doc['result']
    total=read(packet/'browser-total.json')['result'];labels=['xx','yy','zz','sqrt2_xy','sqrt2_yz','sqrt2_xz']
    header=['coordinate_1',*['strain_'+c+'_1' for c in labels],*['total_stress_'+c+'_Pa' for c in labels],'control_error','iterations','substeps','stress_scope','pore_pressure_availability','pore_pressure_change_Pa']
    lines=(packet/'browser-total.csv').read_text().splitlines();assert lines[0].split(',')==header and len(lines)==len(total['points'])+1
    for line,point in zip(lines[1:],total['points']):
        cells=line.split(',');assert len(cells)==len(header) and cells[-3:]==['total','unavailable','']
        compare([float(x) for x in cells[:-3]],[point['coordinate'],*point['strain'],*point['state'][:6],point['control_error'],point['diagnostics']['iterations'],point['diagnostics']['substeps']])
    assert read(packet/'configure.json')['returncode']==0 and read(packet/'build.json')['returncode']!=0 and read(packet/'build-resume.json')['returncode']==0
    assert read(packet/'exercise-process.json')['returncode']==0
    assert read(packet/'packaging-process.json')['returncode']!=0 and read(packet/'packaging-current-process.json')['returncode']==0
    return dict(wasm_pairs=12,browser_scoped_exports=3,browser_total_csv=True,legacy_export=True,native_calls=0)
if __name__=='__main__':print(json.dumps(assess(Path(__file__).parent),indent=2))
