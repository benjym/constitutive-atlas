"""Inspect first-row processing formulas, not response values, in pinned XLS files.

The small BIFF8 RPN reader below preserves every arithmetic grouping. xlrd's
general formula decompiler can omit necessary parentheses around denominators;
its text is therefore not used to infer the observation equations.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'paper/results/dependencies'))
import xlrd
from xlrd.formula import func_defs


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def address(row, col):
    return xlrd.formula.colname(col) + str(row + 1)


def grouped_formula(tokens, shared_origin=None):
    """Restricted BIFF8 arithmetic/Ref/fixed-function decoder; fail closed."""
    stack = []
    pos = 0
    while pos < len(tokens):
        op = tokens[pos]
        pos += 1
        if op in (3, 4, 5, 6, 7):
            right, left = stack.pop(), stack.pop()
            stack.append(f'({left}{ {3:"+",4:"-",5:"*",6:"/",7:"^"}[op]}{right})')
        elif op == 0x15:  # explicit parentheses; grouping already preserved
            pass
        elif op == 0x1E:
            stack.append(str(struct.unpack_from('<H', tokens, pos)[0]))
            pos += 2
        elif op == 0x1F:
            stack.append(repr(struct.unpack_from('<d', tokens, pos)[0]))
            pos += 8
        elif op in (0x24, 0x44, 0x64, 0x2C, 0x4C, 0x6C):
            row, packed_col = struct.unpack_from('<HH', tokens, pos)
            pos += 4
            # tRef stores row/column coordinates even when copying is relative.
            if packed_col & 0x3F00:
                raise ValueError('Unexpected BIFF8 column bits')
            col = packed_col & 0xFF
            if op in (0x2C, 0x4C, 0x6C):
                if shared_origin is None:
                    raise ValueError('Shared reference requires an origin')
                if packed_col & 0x8000:
                    row = shared_origin[0] + (row if row < 32768 else row - 65536)
                if packed_col & 0x4000:
                    col = shared_origin[1] + (col if col < 128 else col - 256)
            stack.append(('' if packed_col & 0x4000 else '$')
                         + xlrd.formula.colname(col)
                         + ('' if packed_col & 0x8000 else '$') + str(row + 1))
        elif op in (0x21, 0x41, 0x61):
            function_id = struct.unpack_from('<H', tokens, pos)[0]
            pos += 2
            name, min_args, max_args = func_defs[function_id][:3]
            if min_args != max_args:
                raise ValueError('Variable-argument function requires another decoder')
            args = stack[-min_args:] if min_args else []
            if min_args:
                del stack[-min_args:]
            stack.append(name + '(' + ','.join(args) + ')')
        else:
            raise ValueError(f'Unsupported token 0x{op:02x}')
    if len(stack) != 1:
        raise ValueError('Unbalanced formula stack')
    return stack[0]


def main():
    inventory_path = ROOT / 'paper/study/ottawa_cyclic_inventory.json'
    inventory_sha = sha(inventory_path)
    records = [r for r in json.loads(inventory_path.read_text())['records']
               if r['protocol'] == 'cyclic-torsional-shear-source']
    if len(records) != 9:
        raise ValueError('Expected nine pinned workbooks')
    results = []
    # First formula row only; do not evaluate formulas or read cached responses.
    columns = {12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}
    for record in records:
        path = ROOT / 'tmp/dataset-survey' / record['source_file']
        if sha(path) != record['source_file_sha256']:
            raise ValueError('Source hash mismatch')
        book = xlrd.open_workbook(path, on_demand=True)
        try:
            idx = book.sheet_names().index('Loading')
            sheet = book.sheet_by_index(idx)
            metadata = {cell: sheet.cell_value(row, col) for cell, row, col in (
                ('D2', 1, 3), ('F2', 1, 5), ('G2', 1, 6), ('H2', 1, 7),
                ('I2', 1, 8), ('I16', 15, 8), ('H17', 16, 7),
                ('I17', 16, 8), ('J17', 16, 9), ('K17', 16, 10))}
            book._position = book._sh_abs_posn[idx]
            formulas = {}
            shared = []
            shared_variants = {}
            while True:
                code, length, data = book.get_record_parts()
                if code == 0x0A:
                    break
                if code in (6, 0x206, 0x406):
                    row, col = struct.unpack_from('<HH', data)
                    if row == 21 and col in columns:
                        n = struct.unpack_from('<H', data, 20)[0]
                        tokens = data[22:22+n]
                        formulas[address(row, col)] = {
                            'biff8_rpn_hex': tokens.hex(),
                            'grouped_expression': grouped_formula(tokens)}
                elif code == 0x4BC:  # SHRFMLA: save source tokens, do not guess text
                    r0, r1, c0, c1, count, n = struct.unpack_from('<HHBBxBH', data)
                    if c0 <= 10 and c1 >= 7:
                        tokens = data[10:10+n]
                        key = tokens.hex()
                        group = shared_variants.setdefault(key, {
                            'biff8_rpn_hex': key, 'block_count': 0,
                            'example_range': address(r0, c0) + ':' + address(r1, c1),
                            'expression_at_example_top_left': grouped_formula(tokens, (r0, c0)),
                            'last_row': r1 + 1})
                        group['block_count'] += 1
                        group['last_row'] = max(group['last_row'], r1 + 1)
                        if r0 <= 21 <= r1:
                            shared.append({'range': address(r0, c0) + ':' + address(r1, c1),
                                           'biff8_rpn_hex': key,
                                           'status': 'decoded_shared_reference'})
            if set(formulas) != {address(21, c) for c in columns}:
                raise ValueError('Missing selected processing formulas')
            # Source-integrity audit at fixed metadata-selected rows only. Retain
            # residuals, not the measured values or response/threshold outcomes.
            checks = []
            for excel_row in sorted({22, int(metadata['I16']) + 1}):
                for col, unit in zip(range(7, 11), ('N m', 'degree', 'N', 'kPa')):
                    raw = sheet.cell_value(excel_row - 1, col - 5)
                    corrected = sheet.cell_value(excel_row - 1, col)
                    common_baseline = sheet.cell_value(17, 7)
                    own_baseline = sheet.cell_value(17, col)
                    checks.append({'cell': address(excel_row - 1, col), 'unit': unit,
                                   'cached_minus_raw_minus_H18': corrected - (raw - common_baseline),
                                   'cached_minus_raw_minus_own_baseline': corrected - (raw - own_baseline)})
            results.append({'curated_loading_id': record['id'],
                            'source_file': record['source_file'],
                            'source_file_sha256': record['source_file_sha256'],
                            'metadata_cells': metadata,
                            'first_processing_row_formulas': formulas,
                            'shared_channel_formulas': shared,
                            'shared_zeroing_variants': list(shared_variants.values()),
                            'fixed_row_cache_identity_checks': checks})
        finally:
            book.release_resources()
        if sha(path) != record['source_file_sha256']:
            raise ValueError('Source changed during read')
    if sha(inventory_path) != inventory_sha:
        raise ValueError('Inventory changed during read')
    output = {'paper_record_version': 1, 'date': '2026-10-31',
              'status': 'source_processing_formula_transcription_not_admission',
              'inputs_sha256': {'paper/study/ottawa_cyclic_inventory.json': inventory_sha,
                               'paper/scripts/extract_torsion_transformations.py': sha(Path(__file__))},
              'reader': 'xlrd ' + xlrd.__version__ + '; restricted BIFF8 RPN decoder',
              'exposure': 'Selected first-row formulas, all shared formula definitions '
                          'intersecting H:K, and cached metadata inspected. A subsequent '
                          'integrity check reads C:F/H:K at fixed rows22 and I16+1 plus '
                          'H18:K18 baseline summaries; only identity residuals retained. '
                          'No response fitting, scoring, plotting or threshold analysis.',
              'limits': 'Shared zeroing definitions are decoded and fixed-row cache '
                        'identities checked. No full-history cache evaluation, physical '
                        'validation, sensor-accuracy or correction-admission claim.',
              'interpretation': {
                  'geometry': 'D2 is consolidated height in cm; G2/H2 are consolidated '
                              'outer/inner radii in cm. Cross-check against the separately '
                              'extracted N4/N5/N6 geometry before use.',
                  'engineering_shear_strain': 'M22 = rotation_in_radians * '
                                             '(outer_radius + inner_radius) / (2*height) *100 percent.',
                  'shear_stress': 'N22 = 3*torque / (2*pi*(outer_radius^3-inner_radius^3)); '
                                  'using torque in N m and radii in cm, multiply by1000 for kPa.',
                  'pressure': 'P22 = K22 - initial_back_pressure; Q22 = P22 / I2. '
                              'I2 is the cached initial mean effective stress, not nominal100kPa.',
                  'normal_stress': 'S22 converts processed axial-force channel J22 in N over '
                                   'consolidated area K10 in cm2 to kPa; T22 adds it to '
                                   'initial vertical effective stress and subtracts excess pressure. '
                                   'R22 subtracts excess pressure from initial radial effective stress.',
                  'qualification': 'These identify the processed first-row observation map, '
                                   'not the normal boundary control or instrument/membrane calibration. '
                                   'Shared source tokens subtract absolute H18 from each '
                                   'channel five columns to the right of its raw input. '
                                   'This applies a torque baseline to unlike units; ON/OFF '
                                   'labels do not establish operational switch behaviour. '
                                   'Provider clarification is required before admission.'},
              'specimens': results}
    (ROOT / 'paper/study/torsion_processing_formulas.json').write_text(
        json.dumps(output, indent=2) + '\n')
    print('Extracted selected processing formulas from', len(results), 'pinned workbooks.')


if __name__ == '__main__':
    main()
