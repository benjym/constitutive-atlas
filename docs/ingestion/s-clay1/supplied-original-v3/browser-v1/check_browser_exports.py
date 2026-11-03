"""Compare actual downloaded browser documents to the same native controls."""
from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[5];P=Path(__file__).parent;B=R/'.local/sclay1-sixteen/native/atlas_solver';rows=[];worst=0;scalars=0
csv=lambda v:','.join(format(float(x),'.17g') for x in v)
for path in sorted(P.glob('*-run-v4.json')):
 d=json.loads(path.read_text());s=d['specification'];b=d['result'];assert b['ok'] and len(b['points'])==101;assert s['model']=='s-clay1';assert d['catalogue_hash']==json.loads((R/'.local/sclay1-sixteen/wasm/generated/models.json').read_text())['sha256']
 c=P/(path.stem+'-controls.csv');c.write_text(','.join(s['loading']['controls_bits']))
 settings=[s['integration_settings'][k] for k in ['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks']]
 args=[str(B),'--response-contract','stress-scope-0.1','--mode','run-controls','--model',s['model'],'--parameters',csv(s['parameters']),'--initial',csv(s['initial']),'--protocol',str(s['protocol']),'--laboratory-controls-file',str(c),'--integration-settings',csv(settings)]
 p=subprocess.run(args,capture_output=True,text=True,timeout=60);(P/(path.stem+'-native-raw.json')).write_text(json.dumps({'argv':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');assert p.returncode==0 and not p.stderr; a=json.loads(p.stdout);assert a['ok'];assert len(a['points'])==101
 for i,(ap,bp) in enumerate(zip(a['points'],b['points'])):
  for k in ['state','strain','p','q','q_signed','u']:
   av=ap[k] if isinstance(ap[k],list) else [ap[k]];bv=bp[k] if isinstance(bp[k],list) else [bp[k]]
   for x,y in zip(av,bv):
    if x is None or y is None:assert x==y;continue
    e=abs(x-y)/max(1,abs(x),abs(y));assert e<=2e-8,(path,i,k,e);worst=max(worst,e);scalars+=1
  for k in ['iterations','substeps','rejected']:assert ap[k]==bp[k]
 rows.append({'document':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'protocol':s['protocol'],'parameters':s['parameters'],'points':101,'passed':True})
report={'passed':True,'requests':rows,'compared_physical_scalars':scalars,'maximum_relative_difference':worst,'tolerance':2e-8,'native_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'browser_replay_exact':json.loads((P/'drained-run-v4.json').read_text())['result']['points']==json.loads((P/'import-replay-run-v4.json').read_text())['result']['points']}
(P/'native-browser-parity.json').write_text(json.dumps(report,indent=2)+'\n');print('browser/native parity',len(rows),scalars,worst)
