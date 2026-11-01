"""Recompute saved reference grid differences and source/input bindings only."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def audit():
 p=ROOT/'catalogue/investigations/gis2024-path-reference-v1/reference.json';r=json.loads(p.read_text());count=0
 assert r['source_sha256']=='39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3'
 for path,expected in r['dependency_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
 for c in r['cases']:
  assert hashlib.sha256(json.dumps(c['input'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==c['input_sha256']
  assert [g['steps_per_segment']for g in c['grids']]==[16,32,64]
  for g in c['grids']:
   assert [s['segment']for s in g['trajectory']]==[0,1,2,3]
   assert all(not x['branch_crossing_observed']for x in g['stage_diagnostics']['segments'])
  for key,left,right in [('coarse_difference',0,1),('fine_difference',1,2)]:
   for name,lo,hi in [('stress',0,6),('e',6,7),('h',7,13),('Omega',13,14)]:
    value=max(abs(a-b)for x,y in zip(c['grids'][left]['trajectory'],c['grids'][right]['trajectory'])for a,b in zip(x['state'][lo:hi],y['state'][lo:hi]));assert value==c[key][name],(key,name);count+=1
 return {'saved_reference_audit_pass':True,'recomputed_channel_differences':count,'new_reference_integrations':0}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
