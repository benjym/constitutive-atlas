"""Required Maxwell retained-engine CI regression; no compilation or new approval."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_maxwell_laboratory import bundle, source_manifest
from tests.test_maxwell import assess_rows, assess

REFERENCE = ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json'
PRESETS = {'relaxation':'relaxation-schedule', 'creep':'creep-schedule',
           'oedometer':'oedometer', 'load-hold-reverse':'load-hold-reverse'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(build, output):
    build, output = Path(build).resolve(), Path(output).resolve()
    if output.exists() or output.is_symlink():
        raise ValueError('Refusing to replace Maxwell CI evidence')
    output.mkdir(parents=True)
    before = source_manifest()
    cases = json.loads(REFERENCE.read_text())['cases']
    binding_paths = [REFERENCE, ROOT/'tests/test_maxwell.py',
                     ROOT/'tools/test_maxwell_wasm.mjs',
                     ROOT/'tools/test_maxwell_public_presets.mjs',
                     ROOT/'tools/check_maxwell_ci.py']
    binding = {str(p.relative_to(ROOT)):digest(p) for p in binding_paths}
    (output/'inputs.json').write_text(json.dumps({'source_manifest':before,'files':binding},indent=2)+'\n')
    records = []

    def command(args, name):
        record={'command':args,'timeout_seconds':120}
        try:
            result = subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=120)
            record.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        except subprocess.TimeoutExpired as failure:
            record.update(returncode=None,timeout=True,
                          stdout=(failure.stdout or b'').decode() if isinstance(failure.stdout,bytes) else failure.stdout,
                          stderr=(failure.stderr or b'').decode() if isinstance(failure.stderr,bytes) else failure.stderr)
            raise
        finally:
            records.append(record)
            (output/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
        if result.returncode:
            raise RuntimeError('Maxwell CI command failed: '+name)

    # This existing guard checks exact qualified source, engine, catalogue,
    # independent review and approval before executing any compiled artifact.
    identity=bundle(output/'guarded-package',build)
    (output/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    command(['node','--test','tests/test_maxwell_atlas_contract.mjs',
             'tests/test_maxwell_atlas_runtime.mjs'],'public contract/lifecycle')
    command(['node','tools/test_maxwell_wasm.mjs',str(build/'maxwell.js'),
             str(REFERENCE),str(output/'raw.json')],'frozen analytical corpus')
    errors=assess_rows(cases,json.loads((output/'raw.json').read_text()))
    command(['node','tools/test_maxwell_public_presets.mjs',str(build),
             str(output/'presets.json')],'public presets/replay')
    presets=json.loads((output/'presets.json').read_text())
    if [p['name'] for p in presets]!=list(PRESETS):
        raise ValueError('Missing or reordered public presets')
    preset_errors={}
    for row in presets:
        case=next(c for c in cases if c['id']==PRESETS[row['name']])
        source=json.loads((ROOT/'examples/maxwell'/f"{row['name']}.json").read_text())
        normalized={**source,'solver':row['controls']['solver']}
        if source!=case['specification'] or row['controls']!=normalized or any(row['controls']['solver'].get(k)!=v for k,v in source['solver'].items()):
            raise ValueError('Changed public preset/reference: '+row['name'])
        if row['result']!=row['replayed_result']:
            raise ValueError('Public full replay differs')
        preset_errors[row['name']]=assess(case,row['result'])
    if source_manifest()!=before or any(digest(ROOT/path)!=h for path,h in binding.items()):
        raise ValueError('Source/reference changed during Maxwell CI')
    # Recheck the actual copied engine and approval inputs after execution too.
    if bundle(output/'guarded-package-after',build)!=identity:
        raise ValueError('Qualified package identity changed during Maxwell CI')
    report={'status':'passed','frozen_cases':len(cases),'frozen_calls':2*len(cases),
            'public_presets':len(presets),'public_calls':2*len(presets),
            'reference_errors_Pa':errors,'preset_errors_Pa':preset_errors,
            'scope':'Exact retained reviewed Maxwell Wasm; no native rebuild, new approval, global regression or live qualification'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,default=ROOT/'build-maxwell-wasm')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.build,args.output),indent=2))
