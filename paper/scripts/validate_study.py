"""Check development inputs without imposing a schema on the atlas."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json
from analysis.annotations import validate_model_annotations
from analysis.pilot import validate_config
from analysis.reservations import assert_development_ids
from run_compression_sensitivity import validate_config as validate_compression_sensitivity
from analysis.survey_discovery import validate_full_text_screening, validate_title_screening
from analysis.source_reviews import validate_source_reviews
from analysis.cyclic_inventory import validate_assignments


def main():
    study = ROOT/'paper/study'
    source_reviews = validate_source_reviews()
    for name in ('source_reconciliation_2026-10-31.json', 'ottawa_cyclic_inventory.json',
                 'dss_pressure_identity_audit.json', 'torsion_workbook_metadata.json',
                 'torsion_processing_formulas.json', 'torsion_vba_source_inventory.json',
                 'torsion_processing_followup.json', 'torsion_acquisition_correspondence.json',
                 'leap2022_specimen_metadata.json', 'assumption_proposal.json',
                 'leap2022_core_development.json'):
        value = read_json(study/name)
        for path, expected in value['inputs_sha256'].items():
            if digest(ROOT/path) != expected:
                raise ValueError(f'{name}: evidence changed; review or regenerate the record')
    cyclic = read_json(study/'ottawa_cyclic_inventory.json')
    for specimen in read_json(study/'torsion_vba_source_inventory.json')['specimens']:
        for module in specimen['modules']:
            path = ROOT/module['local_copy']
            if path.exists() and digest(path) != module['source_sha256']:
                raise ValueError('Extracted VBA source differs from reviewed bytes')
    if any(r['role'] != 'unassigned' or r['scientific_admission'] != 'not_assessed'
           for r in cyclic['records']):
        raise ValueError('cyclic scoping inventory cannot assign study roles or admission')
    validate_assignments(cyclic, {})
    for name in ('ottawa_source_metadata.json', 'hostun_source_metadata.json',
                 'kfs_initialization_followup.json', 'kfs_void_ratio_followup.json',
                 'dss_methods_followup.json', 'leap2022_methods_review.json'):
        value = read_json(study/name)
        for path, expected in value['inputs_sha256'].items():
            if digest(ROOT/path) != expected:
                raise ValueError(f'{name}: upstream evidence changed; review source mapping')
        for source in (value.get('documents', []) + value.get('sources', [])
                       + value.get('metadata_snapshots', [])):
            path = ROOT/source['local_copy']
            if path.exists() and digest(path) != source['sha256']:
                raise ValueError(f'{name}: source bytes differ from reviewed snapshot')
        if value['decisions']['shared_data_modified']:
            raise ValueError(f'{name}: source review cannot silently modify shared data')
    leap2022 = read_json(study/'leap2022_specimen_metadata.json')
    if (len(leap2022['records']) != 54
            or len({r['filename_candidate'] for r in leap2022['records']}) != 54
            or any(r['role'] != 'unassigned' or r['scientific_admission'] != 'not_assessed'
                   for r in leap2022['records'])):
        raise ValueError('LEAP2022 transcription needs 54 unique unassigned candidates')
    approval = read_json(study/'assumption_proposal.json')
    if (approval['status'] != 'core_approved_optional_pending'
            or set(approval['approved_ids']) != set(approval['core_ids'])
            or not approval['assumptions_activated']
            or set(approval['approved_ids']) & set(approval['optional_scenario_ids'])):
        raise ValueError('Only the explicitly approved core assumptions may be active')
    core = read_json(study/'leap2022_core_development.json')
    if (len(core['records']) != 32 or core['panel']['dependency_blocks'] != 1
            or core['gates']['scientific_admission'] != 'not_granted'):
        raise ValueError('Approved DSS core is a32-candidate development panel, not admission')
    for record in core['records']:
        source = ROOT/record['local_copy']
        if source.exists() and digest(source) != record['sha256']:
            raise ValueError('DSS source differs from inspected header bytes')
        if [s['K0'] for s in record['initial_stress_scenarios']] != [.5, .35, .65, 1.0]:
            raise ValueError('DSS initial-stress scenarios differ from approved core')
    approved_compression = read_json(study/'compression_sensitivity_approved_core.json')
    validate_compression_sensitivity(approved_compression)
    if (approved_compression['initial_radial_to_axial_stress_ratios'] != [.5, .35, .65, 1.0]
            or approved_compression['assumption_approval']['sha256'] != digest(study/'assumption_proposal.json')):
        raise ValueError('Compression assumptions require the approved core record')
    progress = read_json(study/'approved_core_progress.json')
    for path, expected in progress['inputs_sha256'].items():
        source = ROOT/path
        if not source.exists() and path.startswith('paper/results/'):
            continue  # Local run artifacts are ignored; available copies must match.
        if digest(source) != expected:
            raise ValueError('Approved-core progress evidence changed; review or regenerate')
    questions = read_json(study/'dataset_clarification_questions.json')
    for path, expected in questions['inputs_sha256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError('Clarification questions need review after source findings change')
    downloads = read_json(study/'dataset_methods_downloads.json')
    for path, expected in downloads['inputs_sha256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError('Methods download listing changed; review retrieval record')
    for source in downloads['assets']:
        if source['status'] == 'downloaded':
            path = ROOT/source['local_copy']
            if path.exists() and (digest(path) != source['sha256']
                                  or path.stat().st_size != source['bytes']):
                raise ValueError('Downloaded methods source differs from pinned bytes')
    survey = read_json(study/'survey_protocol.json')
    searches = read_json(study/'survey_searches.json')
    if (searches['protocol_id'] != survey['id'] or searches['protocol_sha256'] != digest(study/'survey_protocol.json')
            or searches['status'] != 'completed_bounded_development_discovery_not_survey_completion'):
        raise ValueError('survey discovery requires matching bounded protocol')
    query_ids = [q['id'] for q in survey['bibliographic_pilot']['queries']]
    if (len(query_ids) != len(set(query_ids)) or len(searches['batches']) != len(query_ids)
            or {b['id'] for b in searches['batches']} != set(query_ids)):
        raise ValueError('survey discovery query coverage mismatch')
    validate_title_screening(read_json(study/'survey_screening.json'), survey, batches=searches['batches'])
    full_text = validate_full_text_screening(read_json(study/'survey_full_text_screening.json'), survey)
    for source in read_json(study/'survey_legacy_quality.json')['batches']:
        if digest(ROOT/source['path']) != source['sha256']:
            raise ValueError('legacy discovery differs from its search-quality audit')
    annotations = read_json(study/'model_annotations.json')
    records = validate_model_annotations(annotations)
    ids = [m['model_id'] for m in records]
    related = read_json(study/'related_work.json')['records']
    related_ids = {r['id'] for r in related}
    for source in related:
        if source.get('local_copy'):
            path = ROOT/source['local_copy']
            if path.exists() and digest(path) != source['sha256']:
                raise ValueError('related-work source differs from reviewed copy')
    information = read_json(study/'calibration_information.json')
    characterization = read_json(study/'kfs_characterization.json')['index_evidence']
    source_path = ROOT/characterization['local_copy']
    if source_path.exists() and digest(source_path) != characterization['sha256']:
        raise ValueError('KFS characterization source differs from reviewed copy')
    info_by_model = {m['model_id']: m for m in information['models']}
    if len(info_by_model) != len(information['models']):
        raise ValueError('duplicate model information record')
    for name, expected_hash in information['config_sha256'].items():
        path = study/name
        if digest(path) != expected_hash:
            raise ValueError('calibration information needs review after configuration change')
        for model in read_json(path)['models']:
            info = info_by_model[model['id']]
            fixed = {k: v['value'] for k, v in info['fixed'].items()}
            if fixed != model['fixed_parameters'] or set(info['fitted']) != set(model['fit']):
                raise ValueError('calibration information differs from configured partition')
            for value in info['fixed'].values():
                if not value.get('role') or not (value.get('source') or
                        (value.get('source_id') in related_ids and value.get('locator'))):
                    raise ValueError('fixed information lacks role or source evidence')
    inventory = read_json(study/'datasets.json')['datasets']
    known = {tid for data in inventory for tid in data.get('local_test_ids', [])}
    compression = read_json(study/'compression_protocol.json')
    assert_development_ids(compression['experiment_ids'])
    if (compression['phase'] != 'development_only_not_calibration_admission' or
            set(compression['experiment_ids']) - known):
        raise ValueError('invalid compression feasibility scope')
    for source in compression['source_evidence']:
        path = ROOT/source['local_copy']
        if path.exists() and digest(path) != source['sha256']:
            raise ValueError('compression initialization source differs from reviewed snapshot')
    compression_sensitivity = read_json(study/'compression_sensitivity.json')
    validate_compression_sensitivity(compression_sensitivity)
    if (ROOT/compression_sensitivity['protocol'] != study/'compression_protocol.json' or
            set(compression_sensitivity['model_ids']) - set(ids)):
        raise ValueError('compression sensitivity lacks reviewed protocol or model annotations')
    for config_path in (study/'pilot.json', study/'pilot_density.json', study/'pilot_matched.json'):
        config = read_json(config_path)
        validate_config(config)
        if any(m['id'] not in ids for m in config['models']):
            raise ValueError('pilot model lacks scientific annotation')
        if set(config['experiment_paths']) - known:
            raise ValueError('pilot test lacks inventory record')
    metadata = read_json(study/'experiment_metadata.json')
    entries = metadata['experiments']
    if len({e['experiment_id'] for e in entries}) != len(entries):
        raise ValueError('duplicate supplemental experiment metadata')
    sources = {s['id']: s for s in metadata['sources']}
    for entry in entries:
        if entry['experiment_id'] not in known or entry['source_id'] not in sources or not entry['locator']:
            raise ValueError('unresolved supplemental metadata source or test')
        if not 0 < entry['void_ratio'] < 2 or not 0 <= entry['relative_density'] <= 1:
            raise ValueError('invalid tabulated state metadata')
    for source in sources.values():
        path = ROOT/source['local_copy']
        if path.exists() and digest(path) != source['sha256']:
            raise ValueError('local source PDF differs from reviewed snapshot')
    conflicts = read_json(study/'metadata_conflicts.json')
    by_id = {entry['experiment_id']: entry for entry in entries}
    if len({e['experiment_id'] for e in conflicts['experiments']}) != len(conflicts['experiments']):
        raise ValueError('duplicate initial-state conflict ID')
    for entry in conflicts['experiments']:
        original = by_id[entry['experiment_id']]
        if (entry['original_void_ratio'] != original['void_ratio'] or
                not 0 < entry['later_void_ratio'] < 2 or not entry['later_locator']):
            raise ValueError('invalid or stale initial-state conflict evidence')
    replay = read_json(study/'replay_sensitivity.json')
    assert_development_ids(replay['experiment_ids'])
    if (replay['phase'] != 'development_only' or set(replay['experiment_ids']) - known or
            set(replay['model_ids']) - set(ids)):
        raise ValueError('invalid replay diagnostic scope')
    local_full_text = sum((ROOT/r['source']['local_copy']).exists() for r in full_text)
    print(f'Validated {len(records)} implementation annotation snapshots, {len(source_reviews)} provisional source reviews, {len(full_text)} assisted full-text screening records ({local_full_text} local PDFs available), {len(inventory)} inventory entries, and the development protocol.')


if __name__ == '__main__':
    main()
