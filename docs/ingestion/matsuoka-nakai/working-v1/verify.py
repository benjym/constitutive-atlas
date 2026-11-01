"""Read-only verification of exact evidence and installed research definition."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
from atlas.model import load,interpret

def data(name):
    f=P/name
    return f.read_bytes() if f.exists() else gzip.decompress((P/(name+'.gz')).read_bytes())

def document(name):return json.loads(data(name))

def main():
    manifest=document('manifest.json')
    for name,h in manifest['packet_files'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,name
    for name,h in manifest['installed_files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for name,row in document('compressed-receipts.json').items():
        raw=data(name);assert len(raw)==row['uncompressed_bytes'] and hashlib.sha256(raw).hexdigest()==row['uncompressed_sha256']
    for freeze in ['prospective-freeze.json','delivery-freeze.json']:
        for name,h in document(freeze)['files'].items():assert hashlib.sha256(data(name)).hexdigest()==h,(freeze,name)
    model=load(P/'model.json');installed=load(ROOT/'models/research/nh2004/nakai-hinokio-2004-clay-appendix-v-be.json')
    assert installed==model
    for name in ['qualification.json','wasm-report.json','laboratory-report.json','native-residual-report.json']:assert document(name)['status']=='pass',name
    def mapping(v):
        result={};offset=0
        for f in model['state']:
            n=6 if f['shape']=='sym' else 1
            result[f['name']]=v[offset:offset+n] if n==6 else v[offset];offset+=n
        return result
    for f in document('residual-fixtures.json'):
        values=interpret(model,mapping(f['current']),mapping(f['parent']),f['de'])
        for field in model['state']:
            value=values[field['name']];components=value.v if field['shape']=='sym' else [value]
            assert max(abs(x) for x in components)/(98000 if field['name']=='sigma' else 1)<=2e-8
    native=[json.loads(x)for x in data('native-responses.jsonl').decode().splitlines()]
    wasm=[json.loads(x)for x in data('wasm-responses.jsonl').decode().splitlines()]
    assert len(native)==len(wasm)==1383
    for a,b in zip(native,wasm):
        assert a['request']==b['request']
        x=a['response'];y=b['response'];assert x['ok']==y['ok'] and x['message']==y['message']
        assert len(x['state'])==len(y['state'])==16
        for v,w in zip(x['state'],y['state']):assert abs(v-w)<=1e-8*max(1,abs(v))
        if not x['ok']:assert x['state']==y['state']
    print('PASS: full v0.3 validation; installed bytes; exact receipts; six independent residual fixtures; 1383 saved native/Wasm pairs; finite-path and laboratory reports.')
if __name__=='__main__':main()
