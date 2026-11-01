"""Saved-only verification; never repeat a trajectory or call candidate code."""
import json
from pathlib import Path
from trace_run import HERE,ROOT,sha,load
from replay_failure import replay
from domain_replay import audit

def verify():
 for name,expected in load(HERE/'manifest.json')['files'].items():assert sha(HERE/name)==expected,name
 for name,expected in load(HERE/'freeze.json')['files'].items():assert sha(ROOT/name)==expected,name
 result=load(HERE/'saved/result.json');assert result['status']=='failed' and result['exception']=="ValueError('diagnostic minimum step')"
 assert load(HERE/'run-process.json')['returncode']==2
 actual=replay(HERE/'saved');assert actual==load(HERE/'replay.json')
 assert audit(HERE/'saved')==load(HERE/'domain.json')
 assert actual['worst_component']==29 and actual['new_integration_commits']==0
 assert load(HERE/'all-tests-process.json')['returncode']==0 and 'Ran 5 tests' in load(HERE/'all-tests-process.json')['stderr']
 return {'saved_evidence_valid':True,'failure_reproduced':True,'rejected_trial_reproduced_exactly':True,
         'localized_cause':'componentwise variational error scaling at fabric activation',
         'original_full_study_pass':False,'original_native_qualification_pass':False,
         'process_status':'terminal','candidate_calls':0,'scientific_signature':None}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
