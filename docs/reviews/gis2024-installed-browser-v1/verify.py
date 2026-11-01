"""Audit retained browser wire/download evidence only; never execute an engine."""
from pathlib import Path
import json,sys,math
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
load=lambda name:json.loads((P/name).read_text())
def response(wires):
    requests=[x['data'] for x in wires if x['direction']=='request'];assert len(requests)==1
    replies=[x['data'] for x in wires if x['direction']=='response' and x['data']['id']==requests[0]['id']];assert len(replies)==1
    return requests[0]['specification'],replies[0]
def verify():
    for freeze in ['initial-freeze.json','port-correction.json','protocols-freeze.json','continuation-freeze.json','guards-freeze.json','guards-v2-freeze.json','replay-freeze.json','outcome-pins.json']:
        for path,digest in load(freeze)['files'].items():checked_receipt(ROOT,(P/freeze).relative_to(ROOT),path,digest)
    cases=load('cases.json');assert len(cases)==20;points=0
    wires=load('browser/protocol-wires.json');requests=[x['data'] for x in wires if x['direction']=='request'];assert len(requests)==21
    for i,row in enumerate(cases):
        expected=load(row['relative']);got=load(f'browser/case-{i:02}.json');assert got['specification']==expected['specification'];assert got['result']['points']==expected['result']['points'];assert got['result']['ok']
        request=requests[i+1];assert request['specification']==got['specification'];assert request['catalogue']['sha256']==got['catalogue_hash']
        replies=[x['data'] for x in wires if x['direction']=='response' and x['data']['id']==request['id']];assert len(replies)==1 and replies[0]['result']==got['result']
        assert all(len(p['state'])==14 and all(math.isfinite(v)for v in p['state'])for p in got['result']['points']);points+=len(got['result']['points'])
    guards=load('browser/guards.json');assert len(guards['guards'])==7
    _,clean=response(guards['clean']);clean=clean['result'];assert clean['ok']
    for guard in guards['guards']:
        observation=guard['observation'];assert observation['disabled'] and observation['status']
        if observation['wires']:
            _,reply=response(observation['wires']);assert reply.get('error')or(reply['result']['ok']is False and not reply['result'].get('points'))
        _,recovered=response(guard['recovery']);assert recovered['result']['ok'] and recovered['result']['points']==clean['points']
    failed=guards['forced_failure'];spec,reply=response(failed['wires']);result=reply['result'];assert not result['ok'] and len(result['points'])==1 and result['points'][0]['state']==spec['initial'];assert len(spec['initial'])==14 and failed['status']
    _,recovered=response(failed['recovery']);assert recovered['result']['points']==clean['points']
    original=load('browser/case-13.json');replay=load('browser/replay.json');assert replay['specification']==original['specification'] and replay['result']['points']==original['result']['points']
    assert replay['specification']['initial'][13]==.25 and replay['specification']['initial'][7:13]==[2e-5,-1e-5,-1e-5,0,0,0]
    audit=load('browser/replay-audit.json');spec,reply=response(audit['replay']);assert spec==replay['specification'] and reply['result']==replay['result']
    assert len(audit['corrupt_imports'])==5
    for row in audit['corrupt_imports']:assert row['wire_count']==0 and row['message'] and not row['export_disabled']
    csv=(P/'browser/replay.csv').read_text().splitlines();assert len(csv)==18 and 'stress_scope' in csv[0] and 'state' not in csv[0] and 'Omega' not in csv[0]
    statuses=load('case-status.json');assert {x['id']for x in statuses if x['status']=='passed'}=={'B01','B05','B06','B07','B08','B09'}
    return {'saved_audit_pass':True,'actual_protocol_cases':20,'full14_points':points,'invalid_inputs':7,'recoveries':8,'forced_failures':1,'invalid_imports':5,'reload_replay':'exact full specification/points','completed_browser_cases':6,'pending_browser_cases':6,'scientific_admission':False,'builds':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
