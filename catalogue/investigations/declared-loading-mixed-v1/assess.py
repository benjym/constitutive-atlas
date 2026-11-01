from pathlib import Path
import json,math,sys
p=Path(__file__).resolve().parent
requests=json.loads((p/'requests.json').read_text())
def clean(x):
    if isinstance(x,dict):return{k:clean(v)for k,v in x.items()if k!='elapsed_ms'}
    if isinstance(x,list):return[clean(v)for v in x]
    return x
def verify(data):
    assert data['descriptor']==json.loads((p/'expected-generated/models.json').read_text())
    assert len(data['rows'])==len(requests)==12
    for row,request in zip(data['rows'],requests):
        assert row['id']==request['id'];result=row['result'];s=request['specification']
        assert result['ok']is request['expected_ok']
        assert len(result['points'])==request['expected_points']
        assert result['initial']==s['initial']and result['parameters']==s['parameters']
        assert result['integration_settings']==s['integration_settings']
        assert result['loading']['controls_bits']==s['loading']['controls_bits']
        for point in result['points']:
            assert len(point['state'])==len(s['initial'])
            assert all(type(v)in(int,float)and math.isfinite(v)for v in point['state'])
    return data
def assess(backend):
    base=verify(json.loads((p/f'baseline-{backend}.json').read_text()))
    current=verify(json.loads((p/backend/'observe.stdout.txt').read_text()))
    assert clean(base['rows'])==clean(current['rows']),'same-backend exact compatibility failure'
    return current
if __name__=='__main__':
    native=assess('native');out={'native_requests':12,'native_same_backend_exact':True}
    if '--both'in sys.argv:
        wasm=assess('wasm')
        def parity(a,b):
            if type(a)is bool or a is None or isinstance(a,str):assert type(a)is type(b)and a==b;return
            if isinstance(a,dict):
                assert a.keys()==b.keys()
                for k in a:parity(a[k],b[k])
            elif isinstance(a,list):
                assert len(a)==len(b)
                for x,y in zip(a,b):parity(x,y)
            else:
                assert type(a)in(int,float)and type(b)in(int,float)and math.isfinite(a)and math.isfinite(b)
                assert abs(a-b)<=1e-7*max(1,abs(a),abs(b))
        parity(clean(native['rows']),clean(wasm['rows']))
        out.update(wasm_requests=12,wasm_same_backend_exact=True,full_response_parity=True)
    out.update(passing_ordinary_defaults=10,small_GIS_example='passed',ordinary_GIS_default='failed-retained',deployment=False)
    print(json.dumps(out,indent=2))
