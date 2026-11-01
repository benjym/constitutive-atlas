"""Run a fixed-parameter initial-state diagnostic without opening reserved tests."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.atlas_adapter import NativeAdapter
from analysis.common import ROOT, digest, read_json, write_json
from analysis.metrics import compare_acquisition
from analysis.reservations import POLICY_PATH, assert_development_ids


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'paper/study/replay_sensitivity.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = read_json(args.config)
    if config['phase'] != 'development_only' or config['paper_record_version'] != 1:
        raise ValueError('unsupported diagnostic phase')
    assert_development_ids(config['experiment_ids'])
    if config['initial_state_scenarios'] != ['file', 'original_table']:
        raise ValueError('both initial-state scenarios are required')
    if not 0 < config['maximum_axial_strain'] <= .02:
        raise ValueError('diagnostic window must lie in first two percent strain')
    spacings = config['maximum_increments']
    if len(spacings) != 2 or not 0 < spacings[1] < spacings[0]:
        raise ValueError('two strictly refining positive increment sizes required')
    baseline_path = ROOT/config['baseline_report']
    baseline = read_json(baseline_path)
    metadata_path = ROOT/'paper/study/experiment_metadata.json'
    conflicts_path = ROOT/'paper/study/metadata_conflicts.json'
    metadata = {e['experiment_id']: e for e in read_json(metadata_path)['experiments']}
    files = {identifier: ROOT/config['data_directory']/f'{identifier}.json' for identifier in config['experiment_ids']}
    inputs = [args.config.resolve(), baseline_path, metadata_path, conflicts_path, POLICY_PATH, *files.values()]
    code = sorted((ROOT/'paper/analysis').glob('*.py')) + [Path(__file__).resolve()]
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in inputs+code}
    models = config['model_ids']
    adapter = NativeAdapter(baseline_path.parent/'solver/atlas_solver', models, baseline_path.parent/'models')
    if adapter.solver_hash != baseline['solver_sha256'] or any(adapter.source_hashes[m] != baseline['model_sha256'][m] for m in models):
        raise ValueError('baseline executable or model snapshot changed')
    parameters = {}
    for mid in models:
        candidates = [c for c in baseline['calibrations'] if c['model'] == mid and c['package'] == config['calibration_package']]
        if len(candidates) != 1:
            raise ValueError('one selected calibration per model required')
        calibration = candidates[0]
        fit = next(f for f in calibration['fits'] if f['seed'] == calibration['selected_seed'])
        if fit['status'] != 'success' or not fit['best']['completed']:
            raise ValueError('successful baseline fit required')
        parameters[mid] = fit['best']['parameters']
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    adapter.freeze(output)
    for p in inputs+code:
        target = output/'inputs'/p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    records = []
    experiments = {}
    for identifier, path in files.items():
        experiment = read_json(path)
        assert_development_ids([experiment['id']])
        if experiment['id'] != identifier:
            raise ValueError('configured and actual experiment identity differ')
        rows = []
        for row in experiment['rows']:
            if row['axial_strain'] > config['maximum_axial_strain']:
                break
            rows.append(row)
        experiment['rows'] = rows
        experiments[identifier] = experiment
        for mid in models:
            for scenario in config['initial_state_scenarios']:
                trial = copy.deepcopy(experiment)
                if scenario == 'original_table':
                    trial['initial']['void_ratio'] = metadata[identifier]['void_ratio']
                for spacing in spacings:
                    prediction = adapter.replay(mid, parameters[mid], trial,
                        [r['axial_strain'] for r in rows], spacing, config['timeout_seconds_per_replay'])
                    metrics = None
                    if prediction['status'] == 'success':
                        pressure = sum(trial['initial']['effective_stress'][:3])/3
                        metrics = {channel: compare_acquisition(rows, prediction, channel, scale)
                                   for channel, scale in [('q', pressure), ('volumetric_strain', config['volume_error_scale'])]}
                    record = {'experiment_id': identifier, 'model_id': mid, 'scenario': scenario,
                              'initial_void_ratio': trial['initial']['void_ratio'], 'maximum_increment': spacing,
                              'parameters': parameters[mid], 'prediction': prediction, 'metrics': metrics}
                    records.append(record)
                    with (output/'journal.jsonl').open('a') as journal:
                        journal.write(json.dumps(record, allow_nan=False)+'\n')
                    print(identifier, mid, scenario, spacing, prediction['status'], flush=True)
    adapter.verify_unchanged()
    for name, sha in hashes.items():
        if digest(ROOT/name) != sha:
            raise ValueError(f'{name}: input changed during diagnostic')
        if digest(output/'inputs'/name) != sha:
            raise ValueError(f'{name}: archived input mismatch')
    summary = []
    for identifier in files:
        for mid in models:
            group = [r for r in records if r['experiment_id'] == identifier and r['model_id'] == mid]
            item = {'experiment_id': identifier, 'model_id': mid,
                    'all_replays_complete': all(r['prediction']['status'] == 'success' for r in group)}
            if item['all_replays_complete']:
                fine = {r['scenario']: r for r in group if r['maximum_increment'] == spacings[1]}
                for channel in ['q', 'volumetric_strain']:
                    item[channel] = {'maximum_source_scenario_difference': max(abs(a[channel]-b[channel]) for a, b in zip(fine['file']['prediction']['points'], fine['original_table']['prediction']['points'])),
                        'file_scenario_rmse': fine['file']['metrics'][channel]['rmse'],
                        'table_scenario_rmse': fine['original_table']['metrics'][channel]['rmse'],
                        'maximum_refinement_difference': max(abs(a[channel]-b[channel]) for scenario in config['initial_state_scenarios'] for a, b in zip(next(r for r in group if r['scenario'] == scenario and r['maximum_increment'] == spacings[0])['prediction']['points'], fine[scenario]['prediction']['points']))}
            summary.append(item)
    report = {'paper_record_version': 1, 'kind': 'fixed_parameter_initial_state_development_diagnostic',
              'config': config, 'input_sha256': hashes, 'solver_sha256': adapter.solver_hash,
              'model_sha256': adapter.source_hashes, 'catalogue_hash': adapter.catalogue_hash,
              'input_integrity': 'verified', 'origin_drift': adapter.origin_drift(),
              'records': records, 'summary': summary}
    write_json(output/'report.json', report)
    lines = ['# Initial-state development diagnostic', '',
        'Fixed earlier C2 parameters; no recalibration, source selection or model-ranking inference. Both initial-state interpretations are retained. All values use SI units.', '',
        'Metrics use trapezoidal endpoint errors over absolute axial-strain travel; they differ from the monotonic pilot metric. Recorded order is preserved, including the TMD12 reversal. Physical timing and measurement uncertainty are unresolved.', '',
        '| Test | Model | Complete (four replays) | Maximum q source difference (Pa) | Maximum q refinement difference (Pa) | Maximum volume-strain source difference |',
        '| --- | --- | --- | --- | --- | --- |']
    for item in summary:
        values = f"{item['q']['maximum_source_scenario_difference']:.6g} | {item['q']['maximum_refinement_difference']:.6g} | {item['volumetric_strain']['maximum_source_scenario_difference']:.6g}" if item['all_replays_complete'] else '— | — | —'
        lines.append(f"| {item['experiment_id']} | {item['model_id']} | {item['all_replays_complete']} | {values} |")
    lines += ['', 'Source and refinement differences are observed numerical sensitivities, not experimental uncertainty estimates or evidence that either metadata source is correct.', '',
              'Full predictions, both scenario errors, failure records, checksums, input snapshots and the native solver are retained beside this report.']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    print('Diagnostic report:', output/'report.md')


if __name__ == '__main__':
    main()
