"""Replay the retained harness failure; no candidate execution or numerical pass claim."""
from pathlib import Path
import json,hashlib,subprocess,sys
s=Path(__file__).resolve().parent
pins=json.loads((s/'manifest.json').read_text())
for name,pin in pins.items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
result={'frozen_files':len(pins),'source_bytes_unchanged':True,'backends':{},'numerical_accuracy':'not assessed; retained model-field TypeError','candidate_calls_during_replay':0}
for backend in ('native','wasm'):
 r=json.loads((s/backend/'receipt.json').read_text());j=s/backend/'journal.json';assert hashlib.sha256(j.read_bytes()).hexdigest()==r['journal_sha256']and r['completed']is True
 rows=json.loads(j.read_text());assert len(rows)==15
 assert [x['request']for x in rows[1:]]==json.loads((s/'requests.json').read_text())
 values=[json.loads(x['raw'])for x in rows[1:]];assert all(x['ok']is True for x in values)
 p=subprocess.run([sys.executable,'-B',str(s/'assess_paths.py'),str(j)],capture_output=True,text=True)
 assert p.returncode==1 and "TypeError: string indices must be integers, not 'str'"in p.stderr,(backend,p.returncode,p.stderr)
 result['backends'][backend]={'requests_completed':14,'points_returned':sum(len(v['points'])for v in values),'original_assessor_failure_reproduced':True}
print(json.dumps(result,indent=2))
