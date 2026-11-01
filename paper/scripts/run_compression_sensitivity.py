"""Fixed-parameter first-loading stress/coordinate development diagnostic."""
import argparse
import itertools
import json
import math
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.atlas_adapter import NativeAdapter
from analysis.common import ROOT, digest, read_json, write_json
from analysis.reservations import POLICY_PATH, assert_development_ids
from audit_compression_protocol import run as audit_protocol


def validate_config(config):
    if (config['paper_record_version'] != 1 or config['phase'] != 'development_only_not_calibration_admission'
            or config['parameter_selection'] != 'baseline_parameters_in_frozen_report_config_not_selected_fits'):
        raise ValueError('unsupported compression sensitivity phase or parameter selection')
    if config['model_ids'] != ['linear-elastic', 'hypoplastic-sand-vw96']:
        raise ValueError('this diagnostic supports only the declared memory-free model panel')
    ratios = config['initial_radial_to_axial_stress_ratios']
    if (len(ratios) < 2 or len(set(ratios)) != len(ratios)
            or any(not math.isfinite(r) or r <= 0 for r in ratios)):
        raise ValueError('distinct positive finite initial stress ratios required')
    if config['coordinates'] != ['engineering_increment', 'log_height_increment']:
        raise ValueError('both declared coordinate mappings required')
    spacings = config['maximum_increments']
    if len(spacings) != 2 or not 0 < spacings[1] < spacings[0] or not all(math.isfinite(x) for x in spacings):
        raise ValueError('two strictly refining finite increment sizes required')
    if not math.isfinite(config['timeout_seconds_per_replay']) or config['timeout_seconds_per_replay'] <= 0:
        raise ValueError('positive finite replay timeout required')


def summarize(records, config):
    """Require the full schedule and paired observations before comparison."""
    thresholds = sorted({r['minimum_stress_Pa'] for r in records})
    experiments = sorted({r['experiment_id'] for r in records})
    keys = [(r['experiment_id'], r['model_id'], r['minimum_stress_Pa'], r['initial_stress_ratio'],
             r['coordinate'], r['maximum_increment']) for r in records]
    expected = list(itertools.product(experiments, config['model_ids'], thresholds,
                    config['initial_radial_to_axial_stress_ratios'], config['coordinates'], config['maximum_increments']))
    if len(keys) != len(set(keys)) or set(keys) != set(expected):
        raise ValueError('duplicate or incomplete compression sensitivity schedule')
    output = []
    coarse, fine = config['maximum_increments']
    for experiment, model, threshold in itertools.product(experiments, config['model_ids'], thresholds):
        group = [r for r in records if (r['experiment_id'], r['model_id'], r['minimum_stress_Pa']) == (experiment, model, threshold)]
        item = dict(experiment_id=experiment, model_id=model, minimum_stress_Pa=threshold,
                    requested_replays=len(group), successful_replays=sum(r['prediction']['status'] == 'success' for r in group))
        if item['successful_replays'] != len(group):
            item['comparison_status'] = 'incomplete_no_complete_aggregate'
            output.append(item)
            continue
        by_key = {(r['initial_stress_ratio'], r['coordinate'], r['maximum_increment']): r for r in group}
        observations = group[0]['source_lines']
        if any(r['source_lines'] != observations or len(r['prediction']['points']) != len(observations)
               or [p['observation_index'] for p in r['prediction']['points']] != list(range(len(observations))) for r in group):
            raise ValueError('compression comparisons require matched complete acquired observations')

        def points(ratio, coordinate, spacing=fine):
            return by_key[ratio, coordinate, spacing]['prediction']['points']

        ratios, coordinates = config['initial_radial_to_axial_stress_ratios'], config['coordinates']
        item.update(comparison_status='complete_development_sensitivity',
            maximum_initial_stress_scenario_difference_Pa=max(
                max(points(r, c)[i]['axial_stress'] for r in ratios)-min(points(r, c)[i]['axial_stress'] for r in ratios)
                for c in coordinates for i in range(len(observations))),
            maximum_coordinate_scenario_difference_Pa=max(
                abs(a['axial_stress']-b['axial_stress']) for r in ratios
                for a, b in zip(points(r, coordinates[0]), points(r, coordinates[1]))),
            maximum_step_refinement_difference_Pa=max(
                abs(a['axial_stress']-b['axial_stress']) for r in ratios for c in coordinates
                for a, b in zip(points(r, c, coarse), points(r, c, fine))),
            maximum_numerical_void_ratio_continuity_difference=max(
                abs(p['void_ratio']-((1+r['initial_void_ratio'])*math.exp(-p['imposed_axial_coordinate'])-1))
                for r in group for p in r['prediction']['points']))
        output.append(item)
    return output


def run(config_path, output):
    config = read_json(config_path)
    validate_config(config)
    protocol_path = ROOT/config['protocol']
    protocol = read_json(protocol_path)
    assert_development_ids(protocol['experiment_ids'])
    audit = audit_protocol(protocol_path)
    baseline_path = ROOT/config['baseline_report']
    baseline = read_json(baseline_path)
    models = config['model_ids']
    adapter = NativeAdapter(baseline_path.parent/'solver/atlas_solver', models, baseline_path.parent/'models')
    if adapter.solver_hash != baseline['solver_sha256'] or any(adapter.source_hashes[m] != baseline['model_sha256'][m] for m in models):
        raise ValueError('baseline executable or model snapshot changed')
    parameters = {m['id']: m['baseline_parameters'] for m in baseline['config']['models'] if m['id'] in models}
    if set(parameters) != set(models):
        raise ValueError('baseline report does not specify every diagnostic model')
    files = {identifier: ROOT/protocol['data_directory']/'normalized'/f'{identifier}.json' for identifier in protocol['experiment_ids']}
    inputs = [config_path.resolve(), protocol_path, baseline_path, POLICY_PATH,
              ROOT/protocol['source_manifest'], ROOT/protocol['data_directory']/'extraction.json', *files.values()]
    code = sorted((ROOT/'paper/analysis').glob('*.py'))+[Path(__file__).resolve(),
           ROOT/'paper/scripts/audit_compression.py', ROOT/'paper/scripts/audit_compression_protocol.py']
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in inputs+code}
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    adapter.freeze(output)
    for path in inputs+code:
        target = output/'inputs'/path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        if digest(target) != hashes[str(path.relative_to(ROOT))]:
            raise ValueError('input changed during snapshotting')
    write_json(output/'protocol_audit.json', audit)
    records = []
    for experiment in audit['experiments']:
        identifier = experiment['id']
        record = read_json(files[identifier])
        for interval in experiment['scenarios']:
            if interval['status'] != 'data_interval_available_not_model_admission':
                raise ValueError('configured development interval unavailable; revise protocol explicitly')
            rows = record['rows'][interval['start_index']:interval['end_index']+1]
            initial = rows[0]
            for model, ratio, coordinate, spacing in itertools.product(models,
                    config['initial_radial_to_axial_stress_ratios'], config['coordinates'], config['maximum_increments']):
                if coordinate == 'engineering_increment':
                    coordinates = [r['axial_strain']-initial['axial_strain'] for r in rows]
                else:
                    coordinates = [math.log1p(-initial['axial_strain'])-math.log1p(-r['axial_strain']) for r in rows]
                s = initial['axial_stress']
                stress = [s, ratio*s, ratio*s, 0., 0., 0.]
                prediction = adapter.replay_oedometer(model, parameters[model], stress,
                    initial['void_ratio'], coordinates, spacing, config['timeout_seconds_per_replay'])
                result = dict(experiment_id=identifier, model_id=model,
                    minimum_stress_Pa=interval['requested_minimum_axial_stress_Pa'],
                    initial_stress_ratio=ratio, coordinate=coordinate, maximum_increment=spacing,
                    actual_initial_axial_stress_Pa=s, initial_void_ratio=initial['void_ratio'],
                    parameters=parameters[model], source_lines=[r['source_line'] for r in rows], prediction=prediction)
                records.append(result)
                with (output/'journal.jsonl').open('a') as journal:
                    journal.write(json.dumps(result, allow_nan=False)+'\n')
            print(identifier, interval['requested_minimum_axial_stress_Pa'], 'Pa start threshold completed', flush=True)
    adapter.verify_unchanged()
    for name, sha in hashes.items():
        if digest(ROOT/name) != sha or digest(output/'inputs'/name) != sha:
            raise ValueError(f'{name}: input integrity changed during diagnostic')
    if {r['experiment_id'] for r in records} != set(protocol['experiment_ids']):
        raise ValueError('scheduled experiment missing')
    if {r['minimum_stress_Pa'] for r in records} != set(protocol['minimum_axial_stresses_Pa']):
        raise ValueError('scheduled start threshold missing')
    summary = summarize(records, config)
    report = dict(paper_record_version=1, kind='fixed_parameter_oedometer_initialization_development_diagnostic',
        config=config, protocol=protocol, input_sha256=hashes, solver_sha256=adapter.solver_hash,
        model_sha256=adapter.source_hashes, catalogue_hash=adapter.catalogue_hash,
        input_integrity='verified', origin_drift=adapter.origin_drift(), records=records, summary=summary)
    write_json(output/'report.json', report)
    lines = ['# First-loading compression sensitivity', '',
             'Fixed inherited baseline constants; no fitting, scenario selection, model ranking or benchmark admission. Initial lateral stresses are assumptions. Only first loading is replayed, with no physical time inferred.', '',
             '| Test | Model | Start threshold (kPa) | Complete replays | Max initial-stress difference (Pa) | Max coordinate difference (Pa) | Max refinement difference (Pa) |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in summary:
        values = ' | '.join(f"{r[k]:.6g}" for k in ('maximum_initial_stress_scenario_difference_Pa', 'maximum_coordinate_scenario_difference_Pa', 'maximum_step_refinement_difference_Pa')) if r['comparison_status'] == 'complete_development_sensitivity' else '— | — | —'
        lines.append(f"| {r['experiment_id']} | {r['model_id']} | {r['minimum_stress_Pa']/1000:g} | {r['successful_replays']}/{r['requested_replays']} | {values} |")
    lines += ['', 'Each difference pairs identical acquired observations and a fixed start threshold. Initial-stress differences hold coordinate mapping fixed; coordinate differences hold the initial stress fixed; numerical differences hold both fixed. These maxima are sensitivities, not uncertainty intervals or prediction errors.', '',
              'Different start thresholds use different observed initial states and intervals; do not treat them as a paired common-interval accuracy contrast. Log height improves geometric consistency but does not establish finite-strain stress-law validity. Two numerical resolutions provide a refinement diagnostic, not a proof of convergence.', '',
              'All attempted paths, failures, full predictions, source/data/code snapshots and archived executable/model hashes are retained beside this report.']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'paper/study/compression_sensitivity.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.config, args.output)
    print(f"Completed {len(result['records'])} attempted replays; report: {args.output/'report.md'}")
