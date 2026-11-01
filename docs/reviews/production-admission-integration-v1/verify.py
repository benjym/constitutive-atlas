"""Saved-only integration verification; no private-source or material execution."""
from pathlib import Path
import collections,hashlib,json,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def load(p):return json.loads(p.read_text())
def verify():
 manifest=load(P/'manifest.json')
 for path,h in (manifest['files']|manifest['dependencies']).items():checked_receipt(ROOT,(P/'manifest.json').relative_to(ROOT),path,h)
 resolution=load(P/'input-resolution.json');rows=resolution['review_inputs']
 assert len(rows)==193 and resolution['strict_inventory_pass']is False
 missing=[x for x in rows if x['resolved_path']is None]
 assert len(missing)==1 and missing[0]['path']=='IMPLEMENTATION_PLAN.md'
 for row in rows:
  if row['resolved_path']is not None:checked_receipt(ROOT,(P/'input-resolution.json').relative_to(ROOT),row['path'],row['sha256'])
 agent=ROOT/'docs/reviews/production-admission-agent-v1'
 for n,h in load(agent/'output-hashes.json')['files'].items():assert hashlib.sha256((agent/n).read_bytes()).hexdigest()==h,n
 decisions=load(agent/'decisions.json')
 assert decisions['canonical_admission']is False and decisions['scientific_signature']is None
 counts=dict(collections.Counter(x['judgment']for x in decisions['decisions']))
 assert len(decisions['decisions'])==41 and len({x['id']for x in decisions['decisions']})==41
 assert counts=={'supported':23,'conditional':11,'unresolved':7}
 original=load(agent/'checks.json');actual=load(P/'replayed-checks.json')
 assert {k:v for k,v in original.items()if k!='input_hashes'}=={k:v for k,v in actual.items()if k!='input_hashes'}
 assert actual['input_hashes']['strict_integrity_gate']=='failed_live_board_drift'
 assert [x['path']for x in actual['input_hashes']['mismatches']]==['IMPLEMENTATION_PLAN.md']
 for name,code in [('review',2),('baseline',0),('barodesy',0),('terracotta',0)]:
  process=load(P/(name+'-replay-process.json'));assert process['returncode']==process['expected_returncode']==code
  assert not process['stderr']
 assert json.loads(load(P/'review-replay-process.json')['stdout'])==actual
 assert load(P/'negative-live-context-failure.json')['returncode']==1
 assert load(P/'negative-historical-tests-replay-process.json')['returncode']==0
 assessment=load(P/'assessment.json');assert assessment['decision_counts']==counts
 assert assessment['strict_inventory_pass']is False and assessment['canonical_admission']is False and assessment['compiled_calls']==0
 actions=load(P/'next-actions.json');assert actions['canonical_admission']is False and len(actions['actions'])==4
 assert all(x['next']and x['limits']and x['ready']for x in actions['actions'])
 return {'delivery_integrity':'passed','review_judgments':counts,'unaffected_algebra':'exact_reproduction','original_strict_inventory':'failed_missing_coordination_snapshot','canonical_admission':False,'compiled_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
