"""Independent read-only replay of saved OCC evidence; no compiled calls."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys
H=Path(__file__).resolve().parent
R=H.parents[5];B=H.parents[2]/'execution-v2'
spec=importlib.util.spec_from_file_location('e5_independent',H.parent/'candidate-v3-check.py')
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parsed(r):
    v=json.loads(r['stdout']);assert r['returncode']==(0 if v['ok'] else 1);return v
def state(a):assert len(a)==7 and all(math.isfinite(v) for v in a)
def error(a,b):
    state(a);state(b)
    return max(abs(x-y)/max(1000. if i<6 else 1.,abs(y)) for i,(x,y) in enumerate(zip(a,b)))
def close(a,b):
    e=error(a,b);assert e<=2e-10,e;return e

def backend(name):
    req=read(B/'requests.json');raw=read(B/f'{name}-raw.json')
    assert raw['requests_sha256']==sha(B/'requests.json')
    for key in ('cases','negatives','paths'):assert [v['id'] for v in raw[key]]==[v['id'] for v in req[key]]
    worst=0.;success=0;rejects=[]
    for c,row in zip(req['cases'],raw['cases']):
        assert len(row['calls'])==2
        a,b=map(parsed,row['calls']);assert a==b
        if not a['ok']:
            assert c['id']=='finite-404' and c['de']==[0.,0.,0.,float.fromhex('0x0.0000000000001p-1022'),0.,0.]
            assert a['message'] in ('stod','stod: out of range') and 'state' not in a
            rejects.append(c['id']);continue
        worst=max(worst,close(a['state'],ref.expected(c['initial'],c['de'])));success+=1
        if not any(c['de']):assert a['state']==c['initial']
    for c,row in zip(req['negatives'],raw['negatives']):
        bad,good=parsed(row['bad']),parsed(row['recovery']);assert not bad['ok'] and bad['state']==c['initial']
        assert good['ok'];close(good['state'],ref.expected(req['recovery']['initial'],req['recovery']['de']))
    undrained=[]
    for p,row in zip(req['paths'],raw['paths']):
        assert len(row['calls'])==p['count'];old=p['initial'];err=0.
        for i,r in enumerate(row['calls']):
            assert r['initial']==old
            out=parsed(r['call']);assert out['ok'];z=out['state'];close(z,ref.expected(old,p['increment']));old=z
            t=p['start']+(p['end']-p['start'])*(i+1)/p['count'];v=p['initial'][6]
            # Source6.30/6.31: ln(p/pu)=Lambda exp(-M*v*eps/kappa/Lambda).
            lam=.8;u=math.exp(-1.2*v*t/(.04*lam));pp=100000*math.exp(lam*(u-1));q=1.2*pp*(1-u)
            exact=[pp+2*q/3,pp-q/3,pp-q/3,0.,0.,0.,v]
            err=max(err,max(abs(a-b)/100000 for a,b in zip(z[:6],exact[:6])),abs(z[6]-v))
        off=p['count']//2;assert len(row['restart'])==p['count']-off
        assert all(parsed(a['call'])==parsed(b) for a,b in zip(row['calls'][off:],row['restart']))
        undrained.append(err)
    assert min(a/b for a,b in zip(undrained,undrained[1:]))>=1.8 and undrained[-1]<=.003
    sr=read(B/'supplement-requests.json');s=read(B/f'{name}-supplement-raw.json')
    assert len(s['cases'])==len(sr['cases'])==21 and len(s['tangents'])==len(sr['tangents'])==2
    for c,r in zip(sr['cases']+sr['tangents'],s['cases']+s['tangents']):
        z=parsed(r);assert z['ok'];close(z['state'],ref.expected(c['initial'],c['de']))
        if c['name']=='nonisotropic-exact-hold':assert z['state']==c['initial']
    tangent=[]
    for c,r in zip(sr['tangents'],s['tangents']):
        out=parsed(r);assert out['tangent_ok'];ac=out['state_tangent']
        assert len(ac)==7 and all(len(x)==6 and all(math.isfinite(v) for v in x) for x in ac)
        er=max(abs(ac[i][j]-c['expected_columns'][j][i])/max(1e5 if i<6 else 1.,abs(c['expected_columns'][j][i])) for i in range(7) for j in range(6))
        assert er<=1e-5;tangent.append(er)
    tr=read(B/'transaction-requests.json');tx=read(B/f'{name}-transaction-raw.json')
    assert [x['name'] for x in tx['cases']]==[x['name'] for x in tr['cases']]
    bad=parsed(tx['cases'][0]);assert not bad['ok'] and bad['state']==tr['cases'][0]['initial'] and bad['diagnostics']['substeps']>=1
    good=parsed(tx['cases'][1]);assert good['ok'];close(good['state'],tr['cases'][1]['expected'])
    hr=read(B/'hydro-requests.json');hy=read(B/f'{name}-hydro-raw.json');hydro=[];balances=[]
    assert [x['id'] for x in hy['paths']]==[x['id'] for x in hr['paths']]
    for p,row in zip(hr['paths'],hy['paths']):
        assert len(row['calls'])==p['count'];v0=p['initial'][6];err=0.;bal=0.
        for i,r in enumerate(row['calls']):
            out=parsed(r);assert out['ok'];z=out['state'];state(z)
            assert z[0]==z[1]==z[2] and z[3:6]==[0.,0.,0.]
            ve=v0*math.exp(.003*(i+1)/p['count']);pe=100000*math.exp((v0-ve)/.04)
            err=max(err,abs(z[0]-pe)/100000,abs(z[6]-ve));bal=max(bal,abs(z[6]+.04*math.log(z[0]/100000)-v0))
        hydro.append(err);balances.append(bal)
    assert min(a/b for a,b in zip(hydro,hydro[1:]))>=1.8 and hydro[-1]<=3e-6 and max(balances)<=2e-10
    pr=read(B/'public-requests.json');pub=read(B/f'{name}-public-raw.json')
    assert [c['name'] for c in pr['cases']]==[c['name'] for c in pub['cases']]
    for c,row in zip(pr['cases'],pub['cases']):
        out=parsed(row);assert out['ok'] and len(out['points'])==65 and out['points'][0]['state']==c['initial']
        for a,b in zip(out['points'],out['points'][1:]):
            assert b['substeps']==1;state(b['state'])
            h=b['control']-a['control'];p=c['protocol']
            de=[h, h if p==4 else -.5*h if p==2 else 0., h if p==4 else -.5*h if p==2 else 0.,0.,0.,0.] if p in (0,2,4) else [x-y for x,y in zip(b['strain'],a['strain'])]
            close(b['state'],ref.expected(a['state'],de))
            if p==1:assert abs((b['state'][1]+b['state'][2])/2-100000)/100000<=2e-8
            if p==3:assert abs(b['state'][0]-(b['state'][1]+b['state'][2])/2-b['control'])/100000<=2e-8 and abs(sum(b['strain'][:3]))<=2e-8
            if p==2:assert abs(sum(b['strain'][:3]))<=2e-8 and abs(b['state'][6]-c['initial'][6])<=2e-8
    conv=parsed(pub['reference_pressure']);assert conv['ok'];close(conv['state'],pr['reference_pressure']['expected'])
    return dict(successful_finite=success,transport_rejections=rejects,worst_independent_finite_error=worst,
                undrained_errors=undrained,hydro_errors=hydro,hydro_balance_errors=balances,tangent_errors=tangent,
                exact_repeat_hold_restart_rollback=True,public_protocols=8)

def main():
    model=R/'models/original-cam-clay-sw-electronic-log-recovery-v1.json'
    assert sha(model)=='637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34'
    freeze=read(B/'freeze-manifest.json')
    assert all((B/p).is_file() and sha(B/p)==h for p,h in freeze['files'].items())
    result=dict(passed=True,reviewer_compiled_calls=0,model_sha256=sha(model),frozen_files_verified=len(freeze['files']),
                source_sha256=sha(R/'.local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf'),
                native=backend('native'),wasm=backend('wasm'))
    for n in ('native','wasm'):
        for study in ('raw','supplement-raw','public-raw','transaction-raw','hydro-raw'):
            a=read(B/f'{n}-{study}-assessment.json');assert a['passed'] and a['raw_sha256']==sha(B/f'{n}-{study}.json')
    stage=Path('/private/tmp/atlas-occ-execution-v2')
    nr,wr=[read(B/f'{n}-artifact-receipt.json') for n in ('native','wasm')]
    assert sha(stage/'build-native/atlas_occ_solver')==nr['binary_sha256']
    assert sha(stage/'build-wasm/occ.js')==wr['module_sha256'] and sha(stage/'build-wasm/occ.wasm')==wr['wasm_sha256']
    for rc in (nr,wr):assert rc['model_sha256']==sha(model) and rc['source_freeze_sha256']==sha(B/'freeze-manifest.json')
    result['artifact_hashes_verified']=True
    (H/'evidence-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
