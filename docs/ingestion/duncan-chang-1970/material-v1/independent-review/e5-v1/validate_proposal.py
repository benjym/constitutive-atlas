"""Test exact intended-path translation in a disposable owned mirror, not installation."""
from pathlib import Path
import tempfile,os,json,sys
P=Path(__file__).resolve().parent;M=P.parents[1];ROOT=M.parents[3]
sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
record=P/'proposed-agent-review.json';r=json.loads(record.read_text())
with tempfile.TemporaryDirectory(prefix='path-validation-',dir=P) as directory:
 root=Path(directory)
 for row in r['artifacts']:
  target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);os.link(ROOT/row['path'],target)
 target=root/r['model']['path'];target.parent.mkdir(parents=True,exist_ok=True);os.link(M/'execution-v2/candidate.json',target)
 proposed=root/'catalogue/agent-reviews/duncan-chang-1970-endpoint-average-agent-v1.json';proposed.parent.mkdir(parents=True,exist_ok=True);os.link(record,proposed)
 result=validate_review(proposed,root,for_approval=True);entry=approval_entry(proposed,root)
 assert entry['definition']['sha256']==r['model']['sha256']
 print(json.dumps({'pass':True,'record_status':result['status'],'all_nine_checklist_entries':'pass','hashed_artifacts_validated':len(r['artifacts']),'for_approval_validation':'pass in disposable intended-path mirror using exact candidate bytes','actual_installed_model_or_registry_modified':False,'coordinator_must_validate_actual_installed_path':True,'compiled_calls':0},indent=2))
