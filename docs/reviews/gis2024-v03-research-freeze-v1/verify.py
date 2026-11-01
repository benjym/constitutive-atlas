"""Saved-only request/provenance verification; no constitutive integration."""
import json,hashlib
from prepare import HERE,ROOT,read,sha,validate_inputs

def main():
 for rel,expected in read(HERE/'manifest.json')['files'].items():assert sha(ROOT/rel)==expected,rel
 report=read(HERE/'preflight.json');replay=validate_inputs()
 assert all(report[k]==v for k,v in replay.items())
 pair=read(HERE/'generation-reproduction.json');assert pair['first']['generated']==pair['second']['generated']==report['generated']
 model=read(HERE/'model.json');rows=read(HERE/'trajectory-requests.json.gz');old=read(ROOT/'catalogue/investigations/gis2024-integration-v1/native.json');ref=read(ROOT/read(HERE/'policy.json')['reference'])
 for row in rows:
  previous=next(g for g in old['records']if(g['case'],g['tolerance'],g['partitions'])==(row['case'],row['tolerance'],row['partitions']))
  assert row['increments']==[c['request']['strain']for c in previous['calls']]
  initial=next(c['input']for c in ref['cases']if c['input']['id']==row['case'])
  parameters=[sum(initial['initial'][:3])/3 if name=='p_scale'else initial['parameters'][name]for name in model['parameters']]
  assert row['parameters']==parameters==previous['calls'][0]['request']['parameters']
  assert row['settings']==[2e-10,row['tolerance'],45,20,20000,11]
  assert row['initial']==previous['calls'][0]['request']['initial']==initial['initial']
 print(json.dumps({'saved_packet_integrity':True,'literal_request_identity_pass':True,'deterministic_generation_pass':True,'requests':20,'updates_per_backend':204,'candidate_integrations':0,'compiled_builds':0,'backend_qualification':False,'scientific_admission':False},indent=2))
if __name__=='__main__':main()
