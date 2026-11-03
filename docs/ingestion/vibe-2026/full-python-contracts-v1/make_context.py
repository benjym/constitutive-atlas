"""Preserve exact Git31125 compiler/default top-level model glob before replay."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;plan=json.loads((P/'plan-v1.json').read_text())
def materialize(item):
 blob=subprocess.check_output(['git','show',plan['historical_commit']+':'+item['path']],cwd=R);assert hashlib.sha256(blob).hexdigest()==item['sha256'];target=R/item['archived_path']
 if target.exists():assert target.read_bytes()==blob
 else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
 return item
baseline='docs/ingestion/vibe-2026/controlled-time-qualification-v1/baseline'
data={'version':'controlled-time-historical-ordinary-v1','source_commit':plan['historical_commit'],'emitter':materialize(plan['historical_emitter']),'models':[materialize(x) for x in plan['historical_models']],'baseline_manifest':{'path':baseline+'/manifest.json','sha256':hashlib.sha256((R/baseline/'manifest.json').read_bytes()).hexdigest()},'expected_outputs':plan['original_expected_output_pins'],'current_imported_dependencies':['atlas/dsl.py','atlas/model.py','atlas/stress.py','schemas/model-v0.3.schema.json'],'dependency_policy':'Only emitter and complete original15modelinputs are historical. Imported validation/DSL/stress/schema remain current; unchanged original exactoutputhash gates detect any effect. No currentcompiler fallback.'}
out=P/'historical-context-v1.json';assert not out.exists();out.write_text(json.dumps(data,indent=2)+'\n');print(hashlib.sha256(out.read_bytes()).hexdigest())
