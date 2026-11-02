"""Manufactured CI orchestration checks only. Executes no compiler or model."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
from unittest.mock import patch

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
spec=importlib.util.spec_from_file_location('perzyna_ci',ROOT/'tools/check_perzyna_ci.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
reports=[]
for scenario in ['native','paired','consumer-failure','capture-failure','stale-metadata']:
    with tempfile.TemporaryDirectory(prefix='perzyna-ci-mock-') as directory:
        root=Path(directory);study=root/driver.STUDY;study.mkdir(parents=True)
        (study/'expected-catalogue.json').write_text('{}\n');output=root/'logs';commands=[]
        def fake(argv,cwd,stdout,stderr):
            assert Path(cwd)==root
            commands.append(argv);code=0
            if '-S' in argv:
                build=root/argv[argv.index('-B')+1];(build/'generated').mkdir(parents=True)
                (build/'generated/models.json').write_text('{"stale":true}\n' if scenario=='stale-metadata' else '{}\n')
            elif '--build' in argv:
                assert argv[-4:]==['--target','atlas_perzyna_solver','--parallel','1']
                build=root/argv[argv.index('--build')+1]
                for name in ['perzyna.js','perzyna.wasm','atlas_perzyna_solver']:(build/name).write_text('mock artifact\n')
            elif 'capture' in argv:
                assert argv[argv.index('--consumer-tool')+1]=='python3'
                if scenario=='capture-failure':code=8
                else:Path(argv[argv.index('--receipt')+1]).write_text('{"synthetic":true}\n')
            elif 'verify' in argv:Path(argv[argv.index('--output')+1]).write_text('{"synthetic":true}\n')
            elif 'native' in argv and '--raw' in argv:
                Path(argv[argv.index('--raw')+1]).write_text('[]\n')
                if scenario=='consumer-failure':code=7
            stdout.write(('MOCK ONLY: exit '+str(code)+'\n').encode())
            return subprocess.CompletedProcess(argv,code)
        argv=['check_perzyna_ci.py','--output',str(output)]+(['--paired'] if scenario=='paired' else [])
        error=None
        with patch.object(driver,'ROOT',root),patch.object(sys,'argv',argv),patch.object(driver.subprocess,'run',side_effect=fake):
            try:driver.main()
            except (subprocess.CalledProcessError,ValueError) as caught:error=caught
        report=json.loads((output/'summary.json').read_text())
        if scenario in ['native','paired']:
            assert error is None and report['passed'] and len(commands)==(5 if scenario=='native' else 12)
        else:
            assert error is not None and not report['passed']
            if scenario=='consumer-failure':
                assert [x['returncode'] for x in report['operations']]==[0,0,0,7,0]
                assert report['operations'][-1]['name']=='native-verify'
            elif scenario=='capture-failure':assert [x['returncode'] for x in report['operations']]==[0,0,8]
            else:assert len(commands)==2
        # Retain closed synthetic receipts/logs for audit without claiming genuine tool observations.
        evidence={p.name:p.read_text() for p in sorted(output.iterdir()) if p.is_file()}
        reports.append(dict(scenario=scenario,passed=True,commands=commands,evidence=evidence,error=type(error).__name__ if error else None))
(BASE/'RESULT.json').write_text(json.dumps(dict(passed=True,synthetic_only=True,compiled_calls=0,scenarios=reports),indent=2)+'\n')
print('PASS five manufactured CI sequencing/failure cases; zero compiled calls')
