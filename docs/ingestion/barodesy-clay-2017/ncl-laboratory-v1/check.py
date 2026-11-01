"""Saved-only independent isotropic reference; no production solver imports."""
from decimal import Decimal, localcontext
from pathlib import Path
import argparse, json, math
p=Path(__file__).resolve().parent

def assess(directory):
    directory=Path(directory)
    policy=json.loads((p/'policy.json').read_text()); gates=policy['gates']
    requests=json.loads((directory/'requests.json').read_text())
    rows={b:{x['id']:x['result'] for x in json.loads((directory/(b+'.json')).read_text())} for b in ('native','wasm')}
    report={'policy_id':policy['id'],'independent_reference':'Decimal90 source NCL reduction; no production math imports','backends':{},'parity_maximum':0.0,'passed':False}
    ids=[c['id'] for c in policy['cases']]
    for backend,results in rows.items():
        assert list(results)==ids
        metrics={}
        for case in requests:
            name=case['id'];s=case['specification'];r=results[name]
            if name=='invalid-initial':
                assert r['ok'] is False
                continue
            assert r['ok'] is True,(backend,name,r)
            assert len(r['points'])==s['steps']+1
            assert r['points'][0]['state']==s['initial']
            for point,bits in zip(r['points'],s['loading']['controls_bits']):
                import struct
                expected=struct.unpack('>d',bytes.fromhex(bits))[0]
                assert point['control']==expected
                assert len(point['state'])==7 and len(point['strain'])==6
                assert all(math.isfinite(x) for x in point['state']+point['strain']+[point['p'],point['q'],point['q_signed']])
            if name in ('ncl-isotropic','ncl-isotropic-refined','ncl-recovery'):
                pressure=void=dev=0.0
                with localcontext() as ctx:
                    ctx.prec=90
                    # Independent source Eq11/footnote13 integrated at each actual caller strain.
                    v0=Decimal(1)+Decimal.from_float(s['initial'][6]);p0=Decimal(100000);lam=Decimal('0.11')
                    for pt in r['points']:
                        eps=sum((Decimal.from_float(x) for x in pt['strain'][:3]),Decimal(0))
                        refp=float(p0*(eps/lam).exp());refe=float(v0*(-eps).exp()-1)
                        pressure=max(pressure,max(abs(x-refp)/refp for x in pt['state'][:3]))
                        void=max(void,abs(pt['state'][6]-refe))
                        dev=max(dev,abs(pt['q'])/refp,max(abs(x)/refp for x in pt['state'][3:6]))
                assert pressure<=gates['maximum_pressure_relative_error'],(backend,name,'pressure',pressure)
                assert void<=gates['maximum_void_ratio_absolute_error'],(backend,name,'e',void)
                assert dev<=gates['isotropic_deviatoric_relative_bound'],(backend,name,'dev',dev)
                metrics[name]={'pressure_relative_error':pressure,'void_ratio_absolute_error':void,'deviatoric_relative':dev}
            if name=='ncl-zero':assert all(pt['state']==s['initial'] for pt in r['points'])
        ordinary=metrics['ncl-isotropic'];fine=metrics['ncl-isotropic-refined']
        for field in ('pressure_relative_error','void_ratio_absolute_error'):
            assert fine[field]<=ordinary[field]+1e-10,(backend,'refinement',field)
        clean=lambda r:{k:v for k,v in r.items() if k!='elapsed_ms'}
        assert clean(results['ncl-recovery'])==clean(results['ncl-isotropic'])
        report['backends'][backend]=metrics
    for name in ids:
        if name=='invalid-initial':continue
        a,b=rows['native'][name],rows['wasm'][name]
        assert a['catalogue_hash']==b['catalogue_hash']
        for x,y in zip(a['points'],b['points']):
            for v,w in zip(x['state']+x['strain'],y['state']+y['strain']):
                delta=abs(v-w)/max(1,abs(v),abs(w));report['parity_maximum']=max(report['parity_maximum'],delta)
                assert delta<=gates['backend_full_state_normalized_difference'],(name,delta)
    report['passed']=True
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('directory',type=Path);a.add_argument('--output',type=Path);args=a.parse_args()
    result=assess(args.directory)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
