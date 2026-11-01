import hashlib,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent; C=D.parents[1]/'coordinator-v1'; script=C/'check_fixture_v3.py'; h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((C/'supplement-manifest-v3.json').read_text());assert all(h(C/k)==v for k,v in m.items())
results=[]
for entry in json.loads((D/'checks.json').read_text())['results']:
 label=entry['case']
 for mode in ['paired','native-only']:
  output=D/('v3-'+label+'-'+mode+'.json');args=[str(script),str(D/(label+'-native.json'))]
  args+=['--native-only'] if mode=='native-only' else [str(D/(label+'-wasm.json'))]
  args+=['--output',str(output)]
  with patch.object(sys,'argv',args):
   try:runpy.run_path(str(script),run_name='__main__')
   except SystemExit as ex:code=ex.code
  r=json.loads(output.read_text());expected=entry['expected_pass'] or (mode=='native-only' and label in ['wire-divergence','equal-label'])
  assert r['passed']==expected and r['mode']==mode,(label,mode)
  results.append({'case':label,'mode':mode,'expected_pass':expected,'passed':r['passed'],'exit':code})
for label,args in [('missing-mode',[str(D/'ideal-native.json')]),('conflicting-mode',[str(D/'ideal-native.json'),str(D/'ideal-wasm.json'),'--native-only'])]:
 with patch.object(sys,'argv',[str(script)]+args+['--output',str(D/(label+'-unused.json'))]):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:assert ex.code==2
 results.append({'case':label,'expected_cli_rejection':True})
(D/'v3-checks.json').write_text(json.dumps({'compiled_calls':0,'supplement_manifest_sha256':h(C/'supplement-manifest-v3.json'),'results':results},indent=2)+'\n')
