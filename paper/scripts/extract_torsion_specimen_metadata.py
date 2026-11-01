"""Read pinned XLS metadata cells without extracting response histories.

Run with xlrd 2.0.2 available (an isolated dependency directory is supported).
Cached workbook outputs are recorded, not recalculated or treated as independent
measurements. Source workbooks remain unchanged.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'paper/results/dependencies'))
import xlrd


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_cell(sheet, address):
    col = 0
    chars = ''.join(c for c in address if c.isalpha())
    for c in chars:
        col = col * 26 + ord(c) - ord('A') + 1
    row = int(address[len(chars):]) - 1
    cell = sheet.cell(row, col - 1)
    if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        return None
    if cell.ctype == xlrd.XL_CELL_ERROR:
        return {'source_error': xlrd.error_text_from_code[cell.value]}
    return cell.value


CELLS = {
    'specimen_label': 'O1', 'excel_test_date': 'L1',
    'target_Dr_percent_loading': 'B3',
    'initial_vertical_effective_stress_kpa': 'B4',
    'initial_radial_effective_stress_kpa': 'B5', 'K0': 'B6',
    'back_pressure_kpa': 'B7', 'maximum_dry_density_g_cm3': 'B9',
    'minimum_dry_density_g_cm3': 'B10', 'particle_density_g_cm3': 'B11',
    'frequency_hz': 'B14', 'sampling_interval_s': 'B16',
    'initial_outer_diameter_cm': 'H4', 'initial_inner_diameter_cm': 'H7',
    'initial_height_cm': 'H8', 'membrane_thickness_cm': 'F9',
    'dry_mass_g': 'F10', 'initial_volume_cm3': 'F11',
    'initial_dry_density_g_cm3': 'F12', 'initial_Dr_percent': 'F13',
    'consolidation_height_reduction_cm': 'K6',
    'consolidation_volume_reduction_cm3': 'K9',
    'consolidated_area_cm2': 'K10',
    'consolidated_outer_diameter_cm': 'N4',
    'consolidated_inner_diameter_cm': 'N5', 'consolidated_height_cm': 'N6',
    'consolidated_dry_mass_g': 'N7', 'consolidated_volume_cm3': 'N8',
    'consolidated_dry_density_g_cm3': 'N9', 'consolidated_Dr_percent': 'N10',
}


def main():
    inventory_path = ROOT / 'paper/study/ottawa_cyclic_inventory.json'
    inventory_sha = sha(inventory_path)
    inventory = json.loads(inventory_path.read_text())
    review_path = ROOT / 'paper/study/ottawa_source_metadata.json'
    review_sha = sha(review_path)
    review = json.loads(review_path.read_text())
    by_label = {r['specimen_label']: r for r in review['torsion']['specimens']}
    records = [r for r in inventory['records']
               if r['protocol'] == 'cyclic-torsional-shear-source']
    if len(records) != 9:
        raise ValueError('Expected the nine pinned processed workbooks')
    output = []
    for record in records:
        path = ROOT / 'tmp/dataset-survey' / record['source_file']
        if sha(path) != record['source_file_sha256']:
            raise ValueError(f'Source changed: {path}')
        workbook = xlrd.open_workbook(path, on_demand=True)
        try:
            loading = workbook.sheet_by_name('Loading')
            values = {key: read_cell(loading, address) for key, address in CELLS.items()}
            values['target_Dr_percent_summary'] = read_cell(
                workbook.sheet_by_name('波形データ'), 'E5')
            label = values['specimen_label']
            if label not in by_label:
                raise ValueError(f'Unmapped specimen: {label}')
            report = by_label[label]
            rhomin = values['minimum_dry_density_g_cm3']
            rhomax = values['maximum_dry_density_g_cm3']
            if not 0 < rhomin < rhomax:
                raise ValueError('Invalid density limits')
            checks = {}
            for state, report_key in [('initial', 'initial_Dr_percent'),
                                      ('consolidated', 'after_consolidation_Dr_percent')]:
                rho = values[f'{state}_dry_density_g_cm3']
                volume = values[f'{state}_volume_cm3']
                dr = rhomax * (rho - rhomin) / (rho * (rhomax - rhomin)) * 100
                checks[f'{state}_density_from_mass_volume_error_g_cm3'] = (
                    rho - values['dry_mass_g'] / volume)
                checks[f'{state}_Dr_from_density_error_percentage_points'] = (
                    values[f'{state}_Dr_percent'] - dr)
                checks[f'{state}_Dr_matches_report_at_one_decimal'] = (
                    round(values[f'{state}_Dr_percent'], 1) == report[report_key])
            checks['volume_balance_error_cm3'] = (
                values['initial_volume_cm3'] - values['consolidation_volume_reduction_cm3']
                - values['consolidated_volume_cm3'])
            checks['height_balance_error_cm'] = (
                values['initial_height_cm'] - values['consolidation_height_reduction_cm']
                - values['consolidated_height_cm'])
            checks['initial_annular_volume_error_cm3'] = (
                math.pi / 4 * (values['initial_outer_diameter_cm'] ** 2
                               - values['initial_inner_diameter_cm'] ** 2)
                * values['initial_height_cm'] - values['initial_volume_cm3'])
            flags = []
            if values['target_Dr_percent_loading'] != values['target_Dr_percent_summary']:
                flags.append('Loading!B3 target label conflicts with summary!E5; '
                             'do not use target labels as measured specimen density')
            if values['particle_density_g_cm3'] in (None, ''):
                flags.append('Particle-density cell is blank or cached empty; '
                             'void ratio is not assigned')
            output.append({
                'specimen_label': label, 'curated_loading_id': record['id'],
                'source_file': record['source_file'],
                'source_file_sha256': record['source_file_sha256'],
                'metadata': values, 'consistency_checks': checks, 'flags': flags,
            })
        finally:
            workbook.release_resources()
        if sha(path) != record['source_file_sha256']:
            raise ValueError('Workbook changed during extraction')
    if sha(inventory_path) != inventory_sha:
        raise ValueError('Inventory changed during extraction')
    if sha(review_path) != review_sha:
        raise ValueError('Report transcription changed during extraction')
    result = {
        'paper_record_version': 1, 'date': '2026-10-31',
        'status': 'cached_source_cell_extraction_not_initialization_assignment',
        'reader': f'xlrd {xlrd.__version__}',
        'source_cells': {'Loading': CELLS,
                         '波形データ': {'target_Dr_percent_summary': 'E5'}},
        'exposure': 'Reads selected metadata cells only; cached XLS workbook structures '
                    'are parsed by xlrd. No response-history rows extracted. Earlier '
                    'manual metadata inspection also exposed published/worksheet summaries.',
        'interpretation': 'Dry density and relative density are derived from shared '
                          'mass/volume and index inputs, not independent measurements. '
                          'Consistency checks do not establish metrological accuracy. '
                          'Particle density is not borrowed from another laboratory.',
        'inputs_sha256': {
            'paper/study/ottawa_cyclic_inventory.json': inventory_sha,
            'paper/study/ottawa_source_metadata.json': review_sha,
            'paper/scripts/extract_torsion_specimen_metadata.py': sha(Path(__file__)),
        },
        'specimens': output,
    }
    path = ROOT / 'paper/study/torsion_workbook_metadata.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    for row in output:
        v = row['metadata']
        print(row['specimen_label'], 'rho_d before/after:',
              v['initial_dry_density_g_cm3'], v['consolidated_dry_density_g_cm3'],
              'flags:', len(row['flags']))


if __name__ == '__main__':
    main()
