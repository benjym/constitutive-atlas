"""One frozen archived-solver replay per invocation; raw outputs stay private."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from atlas.curve_metrics import compare_acquisition_linear
from tools.check_study_parameters import check as check_parameters
from tools.strict_observation_json import loads
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def load_inputs():
    policy_bytes = (HERE/'policy.json').read_bytes()
    freeze = loads((HERE/'freeze.json').read_bytes())
    require(digest(policy_bytes) == freeze['policy_sha256'], 'policy changed')
    require(digest((HERE/'run_case.py').read_bytes()) == freeze['runner_sha256'], 'runner changed')
    policy = loads(policy_bytes)
    base = ROOT/'studies/kfs-development-v1'
    check_parameters(base/'parameters-v1/parameter-policy.json',base/'allocation.json',
                     base/'reservation-policy.json',base/'parameters-v1/models')
    for name, sha in policy['input_sha256'].items():
        require(digest((ROOT/name).read_bytes()) == sha,'input changed: '+name)
    allocation = loads((base/'allocation.json').read_bytes())
    require(set(policy['experiment_sha256']) <= set(allocation['evaluation_ids']),
            'diagnostic includes unallocated evaluation ID')
    report = loads((ROOT/'paper/results/pilot-matched96/report.json').read_bytes())
    states = loads((base/'initialization-v1/states.json').read_bytes())
    return policy, freeze, report, {r['experiment_id']:r for r in states['records']}


class RecordedProcesses:
    def __init__(self, directory, catalogue_hash):
        self.directory = directory
        self.catalogue_hash = catalogue_hash
        self.records = []

    def run(self, command, **kwargs):
        index = len(self.records)
        record = {'index':index,'command':command,'returncode':None,'accepted':False}
        kwargs['check'] = False
        try:
            process = subprocess.run(command, **kwargs)
            stdout, stderr = process.stdout, process.stderr
            record['returncode'] = process.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b'', exc.stderr or b''
            record['error'] = 'timeout'
            self.retain(record, stdout, stderr)
            raise
        except OSError as exc:
            record["error"] = str(exc)
            self.retain(record, b"", b"")
            raise
        try:
            require(process.returncode == 0, 'native process returned nonzero')
            raw = loads(stdout)
            if '--describe' in command:
                require(raw['sha256'] == self.catalogue_hash, 'describe catalogue mismatch')
            else:
                require(raw.get('ok') is True, 'native response is not successful')
                require(raw.get('catalogue_hash') == self.catalogue_hash, 'native catalogue mismatch')
            record['accepted'] = True
        except (ValueError, KeyError, TypeError) as exc:
            record['error'] = str(exc)
            raise ValueError(str(exc)) from exc
        finally:
            self.retain(record, stdout, stderr)
        return process

    def retain(self, record, stdout, stderr):
        for label, value in (('stdout',stdout),('stderr',stderr)):
            content = value.encode() if isinstance(value,str) else value
            path = self.directory/f"process-{record['index']:04d}.{label}"
            path.write_bytes(content)
            record[label] = path.name
            record[label+'_sha256'] = digest(content)
        self.records.append(record)
        write(self.directory/'processes.json', self.records)


def adapter_class(tracker):
    # Load the exact archived package; never import independently owned paper code.
    directory = ROOT/'paper/results/pilot-matched96/source/paper/analysis'
    package = types.ModuleType('frozen_kfs_native')
    package.__path__ = [str(directory)]
    sys.modules[package.__name__] = package
    name = package.__name__+'.atlas_adapter'
    spec = importlib.util.spec_from_file_location(name,directory/'atlas_adapter.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    module.subprocess = types.SimpleNamespace(run=tracker.run,TimeoutExpired=subprocess.TimeoutExpired)
    module.json = types.SimpleNamespace(loads=loads,JSONDecodeError=json.JSONDecodeError)
    return module.NativeAdapter


def prepare_case(case, policy, report, states):
    eid = case['experiment_id']
    content = (ROOT/'paper/results/pilot-matched96/experiments'/(eid+'.json')).read_bytes()
    require(digest(content) == policy['experiment_sha256'][eid] == report['experiment_sha256'][eid],
            'experiment changed')
    experiment = loads(content)
    require(experiment['id'] == eid,'experiment ID mismatch')
    selected = [p for p in report['predictions'] if p.get('selected') is True and
                (p['model'],p['package'],p['experiment_id']) ==
                (case['model'],case['package'],eid)]
    require(len(selected) == 1,'missing unique saved selected prediction')
    saved = selected[0]
    calibration = [c for c in report['calibrations'] if
                   (c['model'],c['package']) == (case['model'],case['package'])]
    require(len(calibration) == 1,'missing calibration')
    fit = [f for f in calibration[0]['fits'] if f['seed'] == calibration[0]['selected_seed']]
    require(len(fit) == 1 and fit[0]['best']['completed'] is True,'selected fit incomplete')
    require(case['seed'] == saved['seed'] == calibration[0]['selected_seed'] and
            case['parameters'] == saved['parameters'] == fit[0]['best']['parameters'],
            'locked fit differs')
    state = states[eid][case['scenario']]
    require(state['sigma'] == experiment['initial']['effective_stress'],'changed effective stress')
    require(states[eid]['file_initial']['e'] == experiment['initial']['void_ratio'],'file e differs')
    experiment['initial']['void_ratio'] = state['e']
    rows = []
    for row in experiment['rows']:
        if row['axial_strain'] > policy['maximum_axial_strain']:
            break
        rows.append(row)
    require(len(rows) == case['expected_observations'] == len(saved['points']), 'changed window')
    require([r['axial_strain'] for r in rows] == [p['axial_strain'] for p in saved['points']],
            'changed acquisition coordinates')
    return experiment, rows, saved


def run(index, output):
    policy, freeze, report, states = load_inputs()
    require(type(index) is int and 0 <= index < len(policy['cases']),'invalid case index')
    for previous in range(index):
        result = loads((output/f'case-{previous:02d}'/'summary.json').read_bytes())
        require(result['status'] == 'success' and result['policy_sha256'] == freeze['policy_sha256'],
                'previous case failed or differs; stop serial run')
    case = policy['cases'][index]
    experiment, rows, saved = prepare_case(case,policy,report,states)
    directory = output/f'case-{index:02d}'
    directory.mkdir(parents=True, exist_ok=False)
    tracker = RecordedProcesses(directory,policy['catalogue_hash'])
    summary = {'index':index,'case':case,'policy_sha256':freeze['policy_sha256'],
               'runner_sha256':freeze['runner_sha256'],'status':'failed'}
    write(directory/'summary.json',summary)
    try:
        adapter = adapter_class(tracker)(ROOT/'paper/results/pilot-matched96/solver/atlas_solver',
                                        [case['model']],ROOT/'paper/results/pilot-matched96/models')
        require(adapter.solver_hash == policy['solver_sha256'],'solver changed')
        prediction = adapter.replay(case['model'],case['parameters'],experiment,
                                    [r['axial_strain'] for r in rows],policy['maximum_increment'],
                                    policy['timeout_per_case_seconds'])
        write(directory/'prediction.json',prediction)
        require(prediction['status'] == 'success','replay failed: '+prediction['message'])
        require(prediction['completed_observations'] == len(rows),'partial replay')
        if case['scenario'] == 'file_initial':
            require(prediction['points'] == saved['points'],'file control differs from saved points')
            summary['file_control_exact_numeric_reproduction'] = True
        scales = {'q':sum(experiment['initial']['effective_stress'][:3])/3,
                  'volumetric_strain':policy['volumetric_strain_scale']}
        summary['metrics'] = {c:compare_acquisition_linear(rows,prediction,c,scales[c])
                              for c in policy['channels']}
        summary['response_change_from_saved'] = {
            c:compare_acquisition_linear(saved['points'],prediction,c,scales[c])
            for c in policy['channels']}
        summary['native_calls'] = prediction['native_calls']
        summary['maximum_radial_stress_drift_Pa'] = prediction['maximum_radial_stress_drift_Pa']
        summary['status'] = 'success'
    except Exception as exc:
        summary['error'] = str(exc)
        raise
    finally:
        summary['processes'] = len(tracker.records)
        summary['process_receipts_sha256'] = digest((directory/'processes.json').read_bytes()) if tracker.records else None
        write(directory/'summary.json',summary)
    print(json.dumps(summary,indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    run(args.case,args.output_dir)


if __name__ == '__main__':main()
