"""Frozen, source-first comparison; no fitting or gate modification."""
import argparse,bisect,hashlib,json,math,pathlib

def read(p):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise ValueError('duplicate key '+k)
            d[k]=v
        return d
    return json.loads(p.read_text(),object_pairs_hook=pairs,parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
def interp(x,y,t):
    assert len(x)==len(y) and all(a<b for a,b in zip(x,x[1:]))
    assert x[0]<=t<=x[-1]
    i=min(max(1,bisect.bisect_right(x,t)),len(x)-1)
    return y[i-1]+(y[i]-y[i-1])*(t-x[i-1])/(x[i]-x[i-1])
def metric(a,b):
    d=[x-y for x,y in zip(a,b)];return dict(rmse=math.sqrt(sum(x*x for x in d)/len(d)),mae=sum(map(abs,d))/len(d),maximum_absolute_error=max(map(abs,d)))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--observations',required=True);ap.add_argument('--data',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    base=pathlib.Path(__file__).resolve().parent;out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False)
    pins=read(base/'source-pins.json');assert hashlib.sha256(pathlib.Path(a.data).read_bytes()).hexdigest()==pins['data']['sha256']
    ref=read(base/'reference.json')['channels'];requests=read(base/'requests.json');summary={'paths':[],'refinement':[],'scientific_admission':False};paths=[]
    for r in requests:
        d=pathlib.Path(a.observations)/r['id'];receipt=read(d/'receipt.json');raw=d/'stdout.json'
        assert hashlib.sha256(raw.read_bytes()).hexdigest()==receipt['stdout_sha256']
        row={'id':r['id'],'returncode':receipt['returncode']};summary['paths'].append(row)
        try:
            z=read(raw);assert z['model']==r['model'] and z['parameters']==r['parameters'] and z['initial']==r['initial']
            assert z['catalogue_hash']==pins['metadata']['catalogue_hash'] and z['protocol']==r['protocol']
            assert z['api_version']=='experimental-laboratory-controls-0.1' and z['loading']['controls_bits']==r['controls_bits']
            assert z['steps']==r['steps'] and z['integration_settings']==r['integration_settings']
            pts=z['points'];x=[p['control'] for p in pts];channels={'q':[p['q_signed'] for p in pts],'volumetric_strain':[sum(p['strain'][:3]) for p in pts]}
            assert all(math.isfinite(v) for v in x+sum(list(channels.values()),[]))
            row.update(ok=z['ok'],message=z['message'],points=len(pts),last_control=x[-1],complete=z['ok'] and len(pts)==r['steps']+1 and x[-1]==.25)
            row['source']={}
            for k,c in ref.items():
                failures=[];values=[]
                for i,v in enumerate(c['rows']):
                    if not x[0]<=v['axial_coordinate']<=x[-1]: failures.append({'index':i,'reason':'outside completed prefix'});continue
                    value=interp(x,channels[k],v['axial_coordinate']);values.append(value)
                    if not v['lower']<=value<=v['upper']:failures.append({'index':i,'axial_coordinate':v['axial_coordinate'],'value':value,'lower':v['lower'],'upper':v['upper']})
                row['source'][k]={'pass':not failures,'failures':failures}
            paths.append((r['id'],x,channels))
        except (ValueError,KeyError,AssertionError,IndexError) as e: row['evidence_error']=repr(e)
    for left,right in zip(paths,paths[1:]):
        pair={'paths':[left[0],right[0]],'channels':{}}
        for k,c in ref.items():
            grid=[v['axial_coordinate'] for v in c['rows']];complete=left[1][-1]==right[1][-1]==.25
            diffs=[abs(interp(left[1],left[2][k],t)-interp(right[1],right[2][k],t)) for t in grid] if complete else []
            pair['channels'][k]={'pass':complete and max(diffs)<=c['refinement_limit'],'maximum_difference':max(diffs) if diffs else None,'limit':c['refinement_limit']}
        summary['refinement'].append(pair)
    rows=read(pathlib.Path(a.data))['rows'];clean=[]
    for r in rows:
        if not 0<=r['axial_strain']<=.25:continue
        if clean and r['axial_strain']==clean[-1]['axial_strain']:clean[-1]=r
        else:
            assert not clean or r['axial_strain']>clean[-1]['axial_strain'],'measured reversal'
            clean.append(r)
    for row,(_,x,c) in zip(summary['paths'],paths):
        lo=max(x[0],clean[0]['axial_strain']);hi=min(x[-1],clean[-1]['axial_strain']);grid=[lo+(hi-lo)*i/100 for i in range(101)]
        row['experimental_overlap']=[lo,hi];row['experimental_errors']={k:metric([interp(x,c[k],t) for t in grid],[interp([v['axial_strain'] for v in clean],[v[k] for v in clean],t) for t in grid]) for k in ref}
    summary['source_pass']=len(paths)==3 and all(r.get('complete') and all(c['pass'] for c in r['source'].values()) for r in summary['paths'])
    summary['refinement_pass']=len(summary['refinement'])==2 and all(c['pass'] for p in summary['refinement'] for c in p['channels'].values())
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for ax,(k,c) in zip(axes,ref.items()):
        scale=1e-3 if k=='q' else 100;grid=[r['axial_coordinate']*100 for r in c['rows']]
        ax.fill_between(grid,[r['lower']*scale for r in c['rows']],[r['upper']*scale for r in c['rows']],color='0.85',label='Frozen source-stroke envelope')
        ax.plot(grid,[r['value']*scale for r in c['rows']],color='black',label='Published model, extracted')
        for name,x,ys in paths:ax.plot([v*100 for v in x],[v*scale for v in ys[k]],label=name,linewidth=1)
        ax.set(xlabel='Accumulated axial coordinate (%)',ylabel='q (kPa)' if k=='q' else 'Normal strain trace (%)');ax.grid(alpha=.2)
    axes[0].legend(fontsize=7);fig.suptitle('TMD2: source-informed operational reconstruction; historical conversion unverified',fontsize=10);fig.tight_layout();fig.savefig(out/'reproduction.png',dpi=180);plt.close(fig)
    print(json.dumps({k:summary[k] for k in ['source_pass','refinement_pass']}))
if __name__=='__main__':main()
