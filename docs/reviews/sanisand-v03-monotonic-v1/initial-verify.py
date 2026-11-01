"""Saved-only verification of the failed native study; never build or integrate."""
import json
from assess import HERE, ROOT, context, load, sha, require, read_records, assess_records
from diagnose_saved import diagnose
from run import verify_execution_freeze


def verify():
    for name,expected in load(HERE/'manifest.json')['files'].items():
        require(sha(HERE/name)==expected,'packet pin: '+name)
    verify_execution_freeze()
    records=read_records(HERE/'native-results')
    require(len(records)==110,'exact response count')
    actual=assess_records(records,context());saved=load(HERE/'native-assessment.json')
    require(actual==saved,'assessment replay')
    require(saved['research_qualification_pass'] is False,'original failure must remain false')
    require(saved['successful_trajectory_checks']==77 and saved['probe_checks_passed']==24 and saved['transactions_pass'],'original result counts')
    require(diagnose(HERE/'native-results')==load(HERE/'saved-diagnosis.json'),'descriptive audit replay')
    require(load(HERE/'native-assessment-process.json')['returncode']==1,'original failed assessor exit')
    require(json.loads(load(HERE/'native-assessment-process.json')['stdout'])==saved,'original assessor stdout')
    require(load(HERE/'native-run-process.json')['returncode']==0,'runner completed')
    require(load(HERE/'native-configure.json')['returncode']==0 and load(HERE/'native-build.json')['returncode']==0,'build completed')
    require(load(HERE/'native-build.json')['argv'][-4:]==['--target','atlas_solver','--parallel','1'],'serial explicit target')
    require(load(HERE/'self-tests-process.json')['returncode']==0 and 'Ran 24 tests' in load(HERE/'self-tests-process.json')['stderr'],'self tests')
    require(load(HERE/'initial-self-test-failure.json')['returncode']==1,'retain initial test failure')
    return {'saved_evidence_valid':True,'research_qualification_pass':False,'native_paths_completed':81,
            'trajectory_checks_passed':77,'negative_and_recovery_checks_passed':24,'transactions_pass':True,
            'wasm_executed':False,'scientific_signature':None}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
