"""Prepare approved DSS metadata/configuration; read headers, not response rows."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'paper/study'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    approval = json.loads((STUDY / 'assumption_proposal.json').read_text())
    if not approval['assumptions_activated'] or set(approval['approved_ids']) != set(approval['core_ids']):
        raise ValueError('Core assumptions must be explicitly approved before preparation')
    meta_path = STUDY / 'leap2022_specimen_metadata.json'
    metadata = json.loads(meta_path.read_text())
    registry_path = ROOT / 'data/public_sources.json'
    source = next(s for s in json.loads(registry_path.read_text())['sources'] if s['id'] == 'leap-2022')
    by_path = {f['source_path']: f for f in source['files']}
    selected = [r for r in metadata['records'] if float(r['static_shear_ratio']) == 0]
    records = []
    for row in selected:
        declared = by_path[row['filename_candidate']]
        path = ROOT / 'tmp/dataset-survey' / declared['filename']
        if sha(path) != declared['sha256'] or path.stat().st_size != declared['size_bytes']:
            raise ValueError('Cached public source differs from registry identity')
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.reader(handle)
            header = next(reader)  # One logical record, potentially multiline.
            physical_lines = reader.line_num
        normalized = [' '.join(h.split()) for h in header]
        names = [re.sub(r'(kPa|%)$', '', h).strip() for h in normalized]
        if (normalized != [' '.join(h.split()) for h in declared['headers']]
                or names[0] not in ('Cycle', 'Cycle No')
                or names[1:3] != ['Shear Strain', 'Shear Stress']
                or names[3:5] not in (['Normal Strain', 'Normal Stress'], ['Axial Strain', 'Axial Stress'])
                or names[5] not in ('Pressure Ratio', 'Excess Pressure')
                or any(names[6:])):
            raise ValueError('Unreviewed source channel contract')
        last_unit = '1' if names[5] == 'Pressure Ratio' else 'kPa'
        if declared['units'] != ['cycles', '%', 'kPa', '%', 'kPa', last_unit] + ['not specified'] * (len(header) - 6):
            raise ValueError('Unexpected unit declaration')
        e = float(row['reported_void_ratio_eac'])
        vertical = row['vertical_consolidation_stress_kpa'] * 1000
        records.append({
            'id': row['id'], 'source_record_id': declared['id'],
            'source_path': row['filename_candidate'], 'local_copy': str(path.relative_to(ROOT)),
            'sha256': declared['sha256'], 'size_bytes': declared['size_bytes'],
            'header': header, 'header_physical_lines': physical_lines,
            'column6_source_name': names[5], 'column6_source_unit': last_unit,
            'trailing_empty_header_columns': len(header) - 6,
            'units_from_registry_and_report_plot_labels': declared['units'],
            'source_unit_limit': 'Header carries names only; unit mappings are adopted from registry/report/plot labels, not independently calibrated.',
            'void_ratio': {'value': e, 'provenance': 'adopted individual report eac', 'source_table': row['table'], 'test_number': row['test_number']},
            'vertical_stress_Pa': {'value': vertical, 'provenance': 'adopted nominal consolidation stress from report'},
            'initial_stress_scenarios': [
                {'K0': k, 'sigma_compression_positive_Pa': {'xx': k * vertical, 'yy': k * vertical, 'zz': vertical, 'xy': 0, 'xz': 0, 'yz': 0},
                 'provenance': 'assumed', 'kind': 'primary' if k == .5 else 'isotropic_diagnostic' if k == 1 else 'sensitivity'}
                for k in [.5, .35, .65, 1.0]],
            'dependency_block': 'LEAP-2022:PRJ-3484',
            'eligibility': 'approved_metadata_candidate_not_solver_or_benchmark_admission',
        })
    if len(records) != 32:
        raise ValueError('Expected exactly32 zero-static-shear candidates')
    paths = [meta_path, STUDY/'assumption_proposal.json', Path(__file__).resolve()]
    config = {
        'paper_record_version': 1, 'id': 'leap2022-approved-core-development-v1',
        'phase': 'approved_assumptions_header_preparation_not_response_replay',
        'inputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in paths},
        'source_registry_snapshot': {'path': str(registry_path.relative_to(ROOT)), 'sha256_at_preparation': sha(registry_path),
                                     'note': 'Relevant source identities retained per record; shared registry may evolve.'},
        'approved_assumptions': approval['approved_ids'], 'records': records,
        'panel': {'candidate_tests': 32, 'deferred_static_shear_tests': 22, 'dependency_blocks': 1,
                  'development_scope': 'Conditional protocol development; no reserved or unseen-data claim. Existing reservations unchanged.'},
        'pilot_id': 'LEAP2022-report-table3-test1',
        'kinematics': {'shear_plane': 'xz', 'vertical_axis': 'z', 'normal_strain_increments': [0, 0, 0],
                       'status': 'assumed ideal simple shear; solver sign/Mandel/spin mapping must be verified before use'},
        'objective_channels': ['unsupplied shear response appropriate to chosen control track', 'vertical_normal_stress'],
        'excluded_objectives': ['normal strain including apparatus compliance', 'column6 until reference convention established'],
        'row_policy': {'header': 'csv.reader one logical record, never fixed physical row skip', 'primary': 'all valid numeric acquisition rows, no decimation',
                       'sensitivity': 'omit final10 numeric rows only; preserve partial cycles and report censoring'},
        'gates': {'headers': 'passed_all32', 'source_byte_identity': 'passed_all32',
                  'full_response_row_validation': 'pending', 'control_mode_selection': 'pending',
                  'simple_shear_adapter': 'pending_scope_and_spin_review',
                  'model_specific_history': 'pending', 'Ottawa_calibration_information': 'pending',
                  'numerical_refinement': 'pending', 'scientific_admission': 'not_granted'},
        'exposure': 'Read32 logical headers and hashed cached source files; no numeric response records parsed or plotted. Prior atlas exposure and published summary exposure remain disclosed.',
    }
    (STUDY/'leap2022_core_development.json').write_text(json.dumps(config, indent=2) + '\n')
    print('Prepared32 byte-verified header contracts and128 assumed initial-stress scenarios; no response replay')
    print('Column6 families:', {name: sum(r['column6_source_name'] == name for r in records) for name in ['Pressure Ratio', 'Excess Pressure']})


if __name__ == '__main__':
    main()
