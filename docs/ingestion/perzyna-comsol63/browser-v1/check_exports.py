from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parents[4];packet=Path(__file__).parent
art=packet/'artifacts';policy=json.loads((root/'docs/ingestion/perzyna-comsol63/interface-v2/POLICY.json').read_text());cases=json.loads((root/'docs/ingestion/perzyna-comsol63/execution-v2/cases.json').read_text())['cases'];site=root/'.local/perzyna-site-v2';identity=json.loads((site/'engine-perzyna/identity.json').read_text());report={'passed':False,'scope':'Actual browser-export values checked against prospectively frozen independent references; no experimental claim','modes':[]};comparisons=0
for mode in policy['modes']:
 run=json.loads((art/(mode+'.json')).read_text());reference=next(c for c in cases if c['id']=='public-'+mode);spec=reference['specification'];assert run['provenance']==identity;assert run['controls']['mode']==mode;assert run['controls']['parameters']==spec['parameters'];assert run['controls']['initial']==spec['initial'];assert run['request']['function']=='atlas_run_schedule';assert len(run['result']['points'])==6
 errors={'state':0.,'stress':0.}
 for point in run['result']['points']:
  expected=next(x for x in reference['references'] if x['time']==point['time'])
  assert len(point['state'])==13 and len(point['observables'])==6
  for key,refkey,absolute in [('state','state',policy['accuracy']['state_absolute']),('observables','stress',policy['accuracy']['stress_absolute_pa'])]:
   for actual,want in zip(point[key],expected[refkey]):
    error=abs(actual-want);assert error<=max(absolute,policy['accuracy']['relative']*abs(want));comparisons+=1;kind='state' if key=='state' else 'stress';errors[kind]=max(errors[kind],error)
 report['modes'].append({'mode':mode,'max_errors':errors,'points':6})
assert json.loads((art/'relaxation.json').read_text())==json.loads((art/'replayed.json').read_text());report['actual_import_replay_exact']=True
edit=json.loads((art/'edited.json').read_text());assert edit['controls']['parameters']==[24000000,11000000,110000,.003,3];assert edit['controls']['initial']==[.008,-.003,-.005,.001,-.001,.002,0,0,0,0,0,0,0];assert edit['result']['points'][0]['state']==edit['controls']['initial'];assert edit['result']['ok'];report['edited_complete_history']=True
latest=json.loads((art/'latest.json').read_text());assert latest['controls']['duration']==.5 and latest['result']['points'][-1]['time']==.5;report['latest_request']=True
results=json.loads((packet/'ACTUAL-TOOL-RESULTS.json').read_text());raw=results['fetched-assets']['content'][0]['text'];fetched=json.loads(raw.split('### Result\n',1)[1].split('\n### Ran',1)[0])
for item in fetched:
 data=(site/item['path']).read_bytes();assert item['status']==200 and len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
assert len(fetched)==23;report['fetched_asset_identities']=len(fetched);assert 'Errors: 0' in (art/'console-errors.txt').read_text();network=(art/'network.txt').read_text();assert not re.search(r'=> \[[45]\d\d\]',network);report['console_errors']=0;report['network_failures']=0;report['comparisons']=comparisons;report['passed']=True
(packet/'EXPORT-CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
