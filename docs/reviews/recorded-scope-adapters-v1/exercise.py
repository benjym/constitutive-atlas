"""Three explicit adapter requests, six raw process receipts, no build."""
import hashlib,json,subprocess,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.recorded_scope_execution import execute_scoped_recorded
from tests.scoped_recorded_execution_cases import retained

def exercise(destination):
    policy=json.loads(Path(__file__).with_name('freeze.json').read_text());solver=Path(policy['solver']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(solver)==policy['solver_sha256']
    output=Path(destination);output.mkdir(parents=True,exist_ok=False);catalogue,rows=retained();selected=[next(r for r in rows if r['label']==name) for name in policy['labels']]
    files=[ROOT/'atlas/recorded_scope_execution.py',ROOT/'atlas/recorded_scope.py',ROOT/'atlas/recorded.py',ROOT/'web/recorded-scope-execution.mjs',ROOT/'web/recorded-scope.mjs',ROOT/'tests/scoped_recorded_execution_cases.py',Path(__file__),Path(__file__).with_name('freeze.json')]
    (output/'pre-execution.json').write_text(json.dumps(dict(source_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},policy=policy,catalogue=catalogue,requests=[r['request'] for r in selected]),indent=2)+'\n')
    original=subprocess.run;receipts=[];material=0;metadata=0
    def captured(command,**kwargs):
        nonlocal material,metadata
        assert sha(solver)==policy['solver_sha256']
        if '--describe' in command:metadata+=1;assert metadata<=policy['max_metadata_calls']
        else:material+=1;assert material<=policy['max_material_calls']
        wires={key:Path(command[command.index(key)+1]).read_text() for key in ['--recorded-controls-file','--recorded-knots-file'] if key in command}
        process=original(command,**kwargs);receipt=dict(command=command,returncode=process.returncode,stdout=process.stdout,stderr=process.stderr,solver_sha256=sha(solver),wires=wires)
        name=f'{len(receipts):03d}.json';(output/name).write_text(json.dumps(receipt,indent=2)+'\n');receipts.append(name);return process
    native=[]
    with patch('subprocess.run',side_effect=captured):
        for row in selected:
            result=execute_scoped_recorded(row['request'],catalogue,solver,timeout=30);assert result==row['response'],row['label'];native.append(dict(label=row['label'],request=row['request'],response=result,accepted=True))
    assert material==3 and metadata==3 and sha(solver)==policy['solver_sha256']
    payload=dict(catalogue=catalogue,rows=native)
    browser=original(['node','tests/test_recorded_scope_execution_browser.mjs'],cwd=ROOT,input=json.dumps(payload),capture_output=True,text=True,timeout=30)
    (output/'browser-contract.json').write_text(json.dumps(dict(returncode=browser.returncode,stdout=browser.stdout,stderr=browser.stderr),indent=2)+'\n');assert browser.returncode==0,browser.stderr
    (output/'responses.json').write_text(json.dumps(payload,indent=2)+'\n')
    report=dict(status='passed',material_calls=material,metadata_calls=metadata,builds=0,receipts=receipts,exact_saved_responses=policy['labels'],javascript_scope_verification=True,wasm_execution=False,scientific_admission=False)
    (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':exercise(sys.argv[1])
