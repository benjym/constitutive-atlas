"""Run the explicitly exploratory drained-sand calibration pilot."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.atlas_adapter import NativeAdapter
from analysis.common import ROOT, digest, read_json, write_json
from analysis.evaluation import prepare_evaluation, predict_evaluation, refinement_changes, resolutions
from analysis.pilot import calibrate, prepare_experiment, validate_config
from analysis.reservations import POLICY_PATH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'paper/study/pilot.json')
    parser.add_argument('--solver', type=Path, default=ROOT/'build/atlas_solver')
    parser.add_argument('--output', type=Path, default=ROOT/'paper/results/pilot-frozen96')
    parser.add_argument('--model-dir', type=Path, default=ROOT/'models', help='current definitions or a prior frozen run models directory')
    parser.add_argument('--max-evaluations', type=int, help='explicit budget sensitivity override per start')
    args = parser.parse_args()
    config = read_json(args.config)
    overrides = {}
    if args.max_evaluations is not None:
        config['optimizer']['max_evaluations'] = args.max_evaluations
        overrides['max_evaluations'] = args.max_evaluations
    validate_config(config)
    # Each run directory is immutable. Interrupted runs retain their journal;
    # use a new output directory for a deliberate rerun.
    args.output.mkdir(parents=True, exist_ok=False)
    adapter = NativeAdapter(args.solver, [m['id'] for m in config['models']], args.model_dir)
    adapter.freeze(args.output)
    paths = {mid: ROOT/path for mid, path in config['experiment_paths'].items()}
    hashes = {mid: digest(path) for mid, path in paths.items()}
    report = {'paper_record_version': 1, 'kind': 'development_pilot', 'config': config,
              'config_sha256': digest(args.config), 'overrides': overrides,
              'effective_config_sha256': hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
              'experiment_sha256': hashes,
              'reservation_sha256': digest(POLICY_PATH),
              'reservation_policy': read_json(POLICY_PATH),
              'model_sha256': adapter.source_hashes, 'catalogue_hash': adapter.catalogue_hash,
              'solver_sha256': adapter.solver_hash, 'python': sys.version,
              'solver_origin': str(args.solver.resolve()), 'models_origin': str(args.model_dir.resolve()),
              'platform': platform.platform(), 'processor': platform.processor(),
              'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'working_tree_status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
              'code_sha256': {str(p.relative_to(ROOT)): digest(p)
                              for parent in [ROOT/'paper/analysis', ROOT/'paper/scripts']
                              for p in sorted(parent.glob('*.py'))},
              'compiled_models': adapter.models,
              'calibrations': [], 'predictions': [], 'baselines': []}
    # Preserve the actual dirty-worktree analysis code and executable used.
    # Hashes alone would not recover an uncommitted implementation after edits.
    for relative in report['code_sha256']:
        destination = args.output/'source'/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/relative, destination)
    # Keep measurements and study decisions recoverable if atlas files evolve.
    for identifier, path in paths.items():
        destination = args.output/'experiments'/f'{identifier}.json'
        destination.parent.mkdir(exist_ok=True)
        shutil.copy2(path, destination)
        if digest(destination) != hashes[identifier]:
            raise ValueError('experiment changed while snapshotting')
    shutil.copy2(args.config, args.output/'config-source.json')
    write_json(args.output/'reservation-policy.json', report['reservation_policy'])
    write_json(args.output/'inputs.json', report)
    def load_experiment(identifier, evaluation=False):
        experiment = read_json(paths[identifier])
        if experiment.get('id') != identifier:
            raise ValueError('experiment ID differs from configured identity')
        return prepare_evaluation(experiment, config) if evaluation else prepare_experiment(experiment, config)
    start = time.perf_counter()
    with (args.output/'calibration-journal.jsonl').open('x') as journal:
        for model in config['models']:
            for package, ids in config['packages'].items():
                # Evaluation records are loaded only after calibration is finished.
                calibration = [load_experiment(mid) for mid in ids]
                fits = []
                for seed in config['optimizer']['seeds']:
                    def checkpoint(row):
                        journal.write(json.dumps({'model': model['id'], 'package': package, 'seed': seed,
                                                  **row}, allow_nan=False)+'\n')
                        journal.flush()
                    fit = calibrate(model, calibration, config, adapter, seed, checkpoint)
                    fits.append(fit)
                    print(model['id'], package, seed, fit['termination'],
                          round(fit['best']['objective'], 6), flush=True)
                winner = min(fits, key=lambda fit: fit['best']['objective'])
                report['calibrations'].append({'model': model['id'], 'package': package,
                                                'selected_seed': winner['seed'], 'fits': fits})
                for eid in config['evaluation_ids']:
                    prepared = load_experiment(eid, evaluation=True)
                    for fit in fits:
                        if fit['status'] != 'success':
                            report['predictions'].append({'model': model['id'], 'package': package,
                                                          'experiment_id': eid, 'seed': fit['seed'],
                                                          'selected': fit['seed'] == winner['seed'],
                                                          'status': 'not_attempted_calibration_failure', 'metrics': None})
                            continue
                        parameters = fit['best']['parameters']
                        prediction, metrics = predict_evaluation(prepared, model['id'], parameters, adapter, config)
                        row = {'model': model['id'], 'package': package, 'seed': fit['seed'],
                               'selected': fit['seed'] == winner['seed'], 'experiment_id': eid,
                               'parameters': parameters, 'metrics': metrics, **prediction}
                        if row['selected']:
                            row['refinement'] = []
                            previous = prediction
                            for resolution in resolutions(config)[1:]:
                                refined, refined_metrics = predict_evaluation(
                                    prepared, model['id'], parameters, adapter, config, resolution)
                                changes = refinement_changes(prepared, previous, refined, config)
                                row['refinement'].append({**resolution, 'status': refined['status'],
                                                           'message': refined.get('message', ''),
                                                           'changes_from_previous': changes,
                                                           'metrics': refined_metrics,
                                                           'diagnostics': refined.get('diagnostics')})
                                previous = refined
                        report['predictions'].append(row)
                write_json(args.output/'partial.json', report)
            # Separate baseline track: no optimization, same development evaluation tests.
            for eid in config['evaluation_ids']:
                prepared = load_experiment(eid, evaluation=True)
                prediction, metrics = predict_evaluation(prepared, model['id'], model['baseline_parameters'], adapter, config)
                report['baselines'].append({'model': model['id'], 'experiment_id': eid,
                                             'metrics': metrics, **prediction})
    adapter.verify_unchanged()
    if digest(POLICY_PATH) != report['reservation_sha256']:
        raise ValueError('reservation policy changed during execution')
    if any(digest(ROOT/path) != value for path, value in report['code_sha256'].items()):
        raise ValueError('paper implementation changed during execution; inspect retained source snapshot')
    if any(digest(path) != hashes[mid] for mid, path in paths.items()) or digest(args.config) != report['config_sha256']:
        raise ValueError('study input changed during execution; inspect retained journal')
    report['elapsed_seconds'] = time.perf_counter()-start
    report['input_integrity'] = 'verified_unchanged'
    report['origin_drift'] = adapter.origin_drift()
    write_json(args.output/'report.json', report)
    print('Development report:', args.output/'report.json')


if __name__ == '__main__':
    main()
