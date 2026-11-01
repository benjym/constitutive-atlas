"""Saved-only final local browser integration audit; never run a material engine."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt,validate_record
load=lambda n:json.loads((P/n).read_text())
def pair(wires):
    req=[w['data']for w in wires if w['direction']=='request'];assert len(req)==1
    out=[w['data']for w in wires if w['direction']=='response' and w['data']['id']==req[0]['id']];assert len(out)==1
    return req[0]['specification'],out[0]['result']
def verify():
    for name in ['setup-freeze.json','state-freeze.json','context-disclosure-freeze.json','links-freeze.json','links-v2-freeze.json','context-corrected-freeze.json','context-initial-freeze.json','tresca-freeze.json','current-source-pins.json','outcome-pins.json']:
        for path,h in load(name)['files'].items():checked_receipt(ROOT,(P/name).relative_to(ROOT),path,h)
    for ref in load('archive-plan.json')['references']:checked_receipt(ROOT,ref['document'],ref['original_path'],ref['sha256'])
    for path,h in load('archive-plan.json')['original_bytes'].items():checked_receipt(ROOT,(P/'archive-plan.json').relative_to(ROOT),path,h)
    prior=ROOT/'docs/reviews/gis2024-installed-browser-v1/verify.py';run=subprocess.run([sys.executable,'-B',str(prior)],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr;old=json.loads(run.stdout);assert old['saved_audit_pass']
    compatibility=load('compatibility.json');names=list(compatibility['files']);oldapp=(ROOT/names[0]).read_text();newapp=checked_receipt(ROOT,(P/'compatibility.json').relative_to(ROOT),'web/app.js',compatibility['files']['web/app.js']).read_text();assert newapp==oldapp.replace("?'Use drainage protocol':'Use initial state & protocol'","?'Use drainage protocol':'Match measured stress, density & protocol'")
    previous=json.loads((ROOT/'docs/reviews/gis2024-draft-installation-v1/package-inventory.json').read_text())['files'];current=load('corrected-package-inventory.json')['files'];changes={n for n,h in current.items()if previous.get(n)!=h};assert changes=={'app.js','evidence.json','evidence-records/catalogue/evidence/research-hp-extracted-asbs-gis-2024-v03-laboratory-route-v1.json'} and not(set(previous)-set(current))
    state=load('browser/state-audit.json');origin=state['origin'];assert origin['state-h']=='0,0,0,0,0,0' and origin['state-Omega']=='0' and origin['state-e']=='0.595' and origin['confinement']=='100' and origin['stress-ratio']=='1';assert len([k for k in origin if k.startswith('param-')])==19
    spec,result=pair(state['selection']);assert spec['initial']==[100000,100000,100000,0,0,0,.595,0,0,0,0,0,0,0] and len(spec['parameters'])==19
    first,r=pair(state['edited']);again,q=pair(state['repeated']);assert first==again and r['ok'] and q['ok'] and r['points']==q['points'];assert first['initial'][7:13]==[2e-5,-1e-5,-1e-5,0,0,0] and first['initial'][13]==.25
    assert all(state[key]['state-h']=='0,0,0,0,0,0' and state[key]['state-Omega']=='0'for key in ['resetExample','switched','defaults'])
    spec,result=pair(state['reset']);assert spec['target']==.01 and spec['steps']==100 and spec['integration_settings']['max_depth']==14 and not result['ok'] and len(result['points'])==1
    context=load('browser/context-audit-v2.json');assert context['label']=='Match measured stress, density & protocol';assert set(context['changed_fields'])=={'confinement','state-e'};assert context['after']['confinement']=='103.72' and context['after']['state-e']=='0.416';assert not context['overlay_wires'];assert all(context['before'][k]==context['after'][k]for k in ['state-h','state-Omega']);assert 'preparation remains unassessed' in context['note']
    _,matched=pair(context['matching_wires']);assert not matched['ok'] and not matched.get('points'),'Unprepared matched-state rejection must remain visible'
    links=load('browser/links-audit.json');text=links['before']['text'].lower();assert all(x in text for x in ['zero spin','small strain 3d','strain path rate','f=0','norm(h)<=r','recorded source-review status: pending','recorded outcome: passed','ordinary drained1%']);review=links['before']['sourceReview'];assert review['status']=='pending' and not review['independent'] and not review.get('reviewer');assert len(links['before']['links'])==2 and links['before']['links'][0]['href']=='https://doi.org/10.1016/j.compgeo.2024.106480'
    assert load('source-download.json')['matches_pinned_source'];assert links['consistency']['actual_parameter_fields']==links['consistency']['expected_parameters'] and links['consistency']['state_fields']==links['consistency']['expected_state'];assert links['before']['definition']['url'].endswith('/models/research-hp-extracted-asbs-gis-2024-v03.json')
    tresca=load('browser/tresca-audit.json');s,t=pair(tresca['defaults']);assert t['ok'] and len(t['points'])==101 and t['stress']['scope']=='total' and t['pore_pressure']['availability']=='unavailable' and all(x['u']is None for x in t['points']);assert tresca['guard']['matching_disabled'] and tresca['guard']['overlay_points']==0 and tresca['guard']['wire_count']==0
    package=load('observations/gis-closure-package-results.json');assert package['stage_b_status']=='passed' and len(package['existing_ten'])==10 and all(x['result']['ok']and len(x['result']['points'])==101 for x in package['existing_ten']);assert package['named_example']['result']['ok'] and not package['ordinary_gis_default']['result']['ok']
    mid='research-hp-extracted-asbs-gis-2024-v03';record=validate_record(ROOT/'catalogue/evidence'/f'{mid}-laboratory-route-v1.json',current=True);assert record['outcome']=='passed' and not record['executor']['independent_review'] and any('fails its first update'in x for x in record['limitations'])
    assert len(load('case-status.json'))==12 and all(x['status']=='passed'for x in load('case-status.json'))
    return {'local_browser_gates':'12/12 bounded draft checks passed','prior_protocol_cases':20,'prior_full14_points':260,'current_defaults_passed':10,'ordinary_gis_default':'failed-retained','matched_unprepared_state':'initialization rejected-retained','scientific_review':'pending unsigned','builds':0,'deployment':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
