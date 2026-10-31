"""Coordinator freeze: generate declarations, hash sources; no rate observation."""
import json,shutil,sys,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
from atlas.compiler import generate
from prepare import prepare,sha

def main():
 assert not (HERE/'prospective-freeze.json').exists() and not (HERE/'protocol.json').exists()
 assert not (HERE/'expected-generated').exists() and not (HERE/'frozen-sources').exists()
 generate(HERE/'expected-generated',[HERE/'model.json'])
 protocol=prepare();(HERE/'protocol.json').write_text(json.dumps(protocol,indent=2,allow_nan=False)+'\n')
 for name,pin in protocol['files'].items():
  source=ROOT/name;assert sha(source)==pin
  target=HERE/'frozen-sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 from tools.research_rate_observations_v3 import checked_protocol
 checked_protocol(HERE/'protocol.json')
 (HERE/'prospective-freeze.json').write_text(json.dumps({'version':'clay2005-homogeneous-rate-freeze-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled_observations_at_freeze':False,'files':{'protocol.json':sha(HERE/'protocol.json')},'source_files':len(protocol['files']),'calls_per_backend':len(protocol['cases']),'historical_cases_unchanged':109,'additional_accuracy_calls':11,'source_snapshot':'frozen-sources/'},indent=2)+'\n')
 print('frozen',len(protocol['files']),'source files,',len(protocol['cases']),'literal calls')
if __name__=='__main__':main()
