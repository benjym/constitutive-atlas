"""Bounded software preview acceptance; no scientific admission."""
from pathlib import Path
import json,math,hashlib,struct
STUDY=Path(__file__).resolve().parent

def unique(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('duplicate JSON key:'+k)
        out[k]=v
    return out

def read(path):return json.loads(Path(path).read_text(),object_pairs_hook=unique)
def bits(x):return struct.pack('>d',float(x)).hex()
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def assess(study=STUDY):
    s=Path(study);errors=[]
    def check(ok,why):
        if not ok:errors.append(why)
    for name,pin in read(s/'manifest.json').items():
        if hashlib.sha256((s/name).read_bytes()).hexdigest()!=pin:raise ValueError('changed frozen input:'+name)
    for name,pin in read(s/'execution-freeze.json').items():
        if hashlib.sha256((s/name).read_bytes()).hexdigest()!=pin:raise ValueError('changed execution input:'+name)
    requests=read(s/'requests.json');model=read(s/'models/barodesy-clay-2017.json');parsed={};maximum_volume=0.
    for backend in ('native','wasm'):
        journal=read(s/backend/'journal.json')
        check([r['id']for r in journal]==['describe']+[r['id']for r in requests],backend+' complete ordered calls')
        if len(journal)!=len(requests)+1:continue
        desc=json.loads(journal[0]['raw'],object_pairs_hook=unique)
        check(desc['models']==[model]and list(desc['models'][0]['parameters'])==list(model['parameters']),backend+' exact ordered descriptor')
        parsed[backend]=[]
        for req,row in zip(requests,journal[1:]):
            check(row['request']==req,backend+'/'+req['id']+' literal controls')
            response=json.loads(row['raw'],object_pairs_hook=unique);parsed[backend].append(response)
            check(response.get('ok')is req['expected_ok'],backend+'/'+req['id']+' status')
            if not req['expected_ok']:
                check(bool(response.get('message')),backend+'/'+req['id']+' failure message');continue
            initial=[float(x)for x in req['initial'].split(',')]
            if req['mode']=='integrate':
                check([bits(x)for x in response['state']]==list(map(bits,initial)),backend+' zero-update identity');continue
            points=response.get('points',[])
            check(len(points)==33,backend+'/'+req['id']+' point count')
            for i,p in enumerate(points):
                state=p['state'];strain=p['strain']
                check(len(state)==7 and len(strain)==6 and all(finite(x)for x in state+strain+[p[k]for k in ('p','q','q_signed','u','control')]),backend+'/'+req['id']+' finite shape')
                check(p['p']>0 and state[6]>=0,backend+'/'+req['id']+' positive domain')
                exact=(1+initial[6])*math.exp(-sum(strain[:3]))-1
                error=abs(state[6]-exact);maximum_volume=max(maximum_volume,error)
                check(error<=1e-6,backend+'/'+req['id']+' independent volume closure')
                protocol=req['protocol'];control=p['control']
                if protocol in (0,1,2,4):check(abs(strain[0]-control)<=1e-7,backend+'/'+req['id']+' axial control')
                if protocol==0:check(abs(strain[1])+abs(strain[2])<=1e-7,backend+' oedometer')
                if protocol in (2,3):check(abs(sum(strain[:3]))<=1e-7,backend+' zero volume')
                if protocol==4:check(max(strain[:3])-min(strain[:3])<=1e-7,backend+' isotropic loading')
                if protocol==1:check(abs((state[1]+state[2])/2-(initial[1]+initial[2])/2)<=.002+1e-7*max(abs(initial[1]),abs(initial[2])),backend+' radial stress')
                if protocol==3:check(abs(p['q_signed']-(initial[0]-(initial[1]+initial[2])/2)-control)<=.002+1e-7*abs(control),backend+' q control')
    maximum_parity=0.
    if set(parsed)=={'native','wasm'}:
        for req,n,w in zip(requests,parsed['native'],parsed['wasm']):
            if not req['expected_ok']:continue
            channels=(lambda x:[x['state']])if req['mode']=='integrate'else(lambda x:[p['state']+p['strain']+[p[k]for k in ('p','q','q_signed','u','control')]for p in x['points']])
            ns,ws=channels(n),channels(w);check(len(ns)==len(ws),'parity points')
            for a,b in zip(ns,ws):
                check(len(a)==len(b),'parity shape')
                for x,y in zip(a,b):
                    error=abs(x-y)/max(1.,abs(x),abs(y));maximum_parity=max(maximum_parity,error)
                    check(error<=1e-10,req['id']+' channel parity')
    return {'version':'barodesy2017-preview-assessment-v1','pass':not errors,'errors':errors,'requests_per_backend':len(requests),'maximum_void_error':maximum_volume,'maximum_scaled_backend_difference':maximum_parity,'scientific_admission':False,'deployment':False}
if __name__=='__main__':
    result=assess();print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass']else 1)
