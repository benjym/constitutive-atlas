"""Supplemental exact parameter-layout check for actual retained study bytes.

Adds an identity check omitted by the frozen generic auditor; changes no model,
expected rate or numerical budget. No compiled calls are made.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.research_rate_observations import Snapshot,checked_protocol,require
from atlas.model import reject_duplicate_keys
HERE=Path(__file__).resolve().parent


def verify():
    snapshot=Snapshot();protocol,model,_=checked_protocol(HERE/'protocol.json',snapshot)
    order=list(model['parameters']);records={}
    for backend in ('native','wasm'):
        receipt=snapshot.read(HERE/(backend+'-observation.json'))
        rawpath=HERE/(backend+'-observation.transport.json');raw=snapshot.read(rawpath)
        require(receipt['transport_sha256']==snapshot.sha(rawpath),'retained raw binding')
        lines=raw['stdout'].splitlines() if backend=='native' else [row['raw'] for row in raw]
        parsed=[json.loads(line,object_pairs_hook=reject_duplicate_keys)for line in lines]
        generated=snapshot.read(HERE/(backend+'-generated-models.json'))
        for source,descriptor in (('actual',parsed[0]),('generated',generated)):
            require(len(descriptor['models'])==1,'single compiled model')
            require(list(descriptor['models'][0]['parameters'])==order,backend+' '+source+' positional parameter order')
        require(len(parsed)==71,'all actual responses checked')
        records[backend]={'parameter_order':order,'actual_and_generated_order_match':True,
                         'all_response_objects_have_unique_keys':True,'rows':len(parsed),
                         'observation_sha256':snapshot.sha(HERE/(backend+'-observation.json')),
                         'raw_sha256':snapshot.sha(rawpath),'generated_sha256':snapshot.sha(HERE/(backend+'-generated-models.json'))}
    result={'version':'barodesy2015-supplemental-actual-layout-v1','protocol_sha256':snapshot.sha(HERE/'protocol.json'),
            'checker_sha256':snapshot.sha(__file__),'passed':True,'backends':records,
            'scope':'Actual parameter insertion order and duplicate-key identity only; no numerical gate relaxation or scientific admission.'}
    snapshot.check();return result

if __name__=='__main__':
    result=verify()
    if '--check' in sys.argv:require(result==json.loads((HERE/'layout-check.json').read_text()),'retained layout evidence differs')
    else:
        output=HERE/'layout-check.json';require(not output.exists(),'fresh supplemental evidence required');output.write_text(json.dumps(result,indent=2)+'\n')
    print('Actual native/Wasm descriptor parameter order and unique response keys verified')
