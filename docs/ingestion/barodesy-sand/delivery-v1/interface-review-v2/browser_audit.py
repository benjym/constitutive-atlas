"""Independent reassessment of saved actual-browser evidence; no compiled calls."""
from pathlib import Path
import json,hashlib,math
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
SRC=Path('/private/tmp/atlas-barodesysand-delivery-v1')
B=ROOT/'output/playwright/barodesy-sand-v2'
P=ROOT/'.local/barodesy-sand-delivery-v1/site-v4'
refs=json.loads((SRC/'docs/ingestion/barodesy-sand/delivery-v1/references.json').read_text())
ids=list(refs)+['default','edited','latest-request','reset-recovery','import-replayed-final','route-recovered']
rows=[]
def compare(a,b):
 if isinstance(a,dict):
  assert a.keys()==b.keys()
  return max([compare(v,b[k]) for k,v in a.items()]+[0.])
 if isinstance(a,list):
  assert len(a)==len(b)
  return max([compare(x,y) for x,y in zip(a,b)]+[0.])
 if isinstance(a,(float,int)) and not isinstance(a,bool):
  assert math.isfinite(a) and math.isfinite(b)
  return abs(a-b)/max(1,abs(a),abs(b))
 assert a==b
 return 0.
for name in ids:
 v=json.loads((B/(name+'.json')).read_text());n=json.loads((B/(name+'-native.txt')).read_text())
 assert v['result']['ok'] and n['ok']
 assert v['catalogue_hash']==v['result']['catalogue_hash']==n['catalogue_hash']
 assert v['specification']['model']=='barodesy-sand'
 assert len(v['result']['points'])==v['specification']['steps']+1
 d=compare(v['result']['points'],n['points']);assert d<=1e-10,(name,d)
 if name in refs or name=='default':assert v['result']['points']==n['points']
 errors=None
 if name in refs:
  ref=refs[name]; spec=v['specification']
  for k in ['protocol','target','steps','cycles']:assert spec[k]==ref['case'][k]
  assert len(ref['points'])==len(v['result']['points'])
  errors=[0.,0.,0.]
  for p,e in zip(v['result']['points'],ref['points']):
   errors=[max(errors[0],max(abs(x-y) for x,y in zip(p['state'][:3],e[:3]))),max(errors[1],abs(p['state'][6]-e[3])),max(errors[2],max(abs(x-y) for x,y in zip(p['strain'][:3],e[4:])))]
  assert errors[0]<=5 and errors[1]<=2e-7 and errors[2]<=2e-7,(name,errors)
 rows.append({'name':name,'points':len(v['result']['points']),'native_scaled_error':d,'independent_errors':errors})
a=json.loads((B/'edited.json').read_text());b=json.loads((B/'import-replayed-final.json').read_text())
assert a['specification']==b['specification'] and a['result']['points']==b['result']['points']
d=json.loads((B/'default.json').read_text());assert d['specification']['initial']==[100000,100000,100000,0,0,0,.75]
assert d['specification']['target']==.01 and d['specification']['steps']==100
ident=json.loads((B/'fetched-identities.json').read_text())
for asset in ident['assets']:
 raw=(P/asset['path']).read_bytes();assert asset['status']==200 and len(raw)==asset['bytes'] and hashlib.sha256(raw).hexdigest()==asset['sha256']
assert len(ident['assets'])==13
assert 'Errors: 0, Warnings: 0' in (B/'console-final.log').read_text()
assert 'Invalid scoped laboratory envelope or catalogue.' in (B/'tamper-rejection.log').read_text()
out={'pass':True,'reviewer':'/root/barodesy_sand_interface_review','browser_saved_runs':rows,'actual_fetched_assets_matching_final_package':13,'edited_import_specification_and_points_exact':True,'default_explicit_initial_and_preset_verified':True,'console_zero_errors_warnings':True,'tampered_import_rejected':True}
print(json.dumps(out,indent=2))
