"""Reviewed LEAP-Asia-2018 torsion sheets and complete apparatus acquisitions.

Time histories, per-cycle extrema and half-cycle strains have independent
coordinates. Never join those blocks by their shared spreadsheet row numbers.
"""
from __future__ import annotations

import csv
import hashlib
import io

from tools.ingest_tables import source_series


def read_torsion(source, raw_dir):
    records = []
    for file in source['files']:
        raw = (raw_dir / file['filename']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Torsion source checksum mismatch: ' + file['filename'])
        if file.get('role') in ('documentation', 'duplicate'):
            continue
        if file.get('raw_acquisition'):
            sheet = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
            if sheet[16] != file['original_headers'] or sheet[7] != file['original_units']:
                raise ValueError('Unreviewed torsion acquisition headers')
            if sheet[15][0] != 'NUM_SAMPS' or int(sheet[15][1]) != len(sheet)-17:
                raise ValueError('Torsion acquisition count mismatch')
            # The source first column is the acquisition sample number, not
            # seconds. Preserve it and the source RATE instead of inventing time.
            sheet[16][0] = 'Acquisition sample number'
            record = source_series(source, file, sheet, file['tables'][0], archive_sha256=digest)
            record['provenance']['original_headers'] = file['original_headers']
            record['provenance']['identical_source_paths'] = file.get('identical_source_paths', [])
            records.append(record)
            continue
        import xlrd
        workbook = xlrd.open_workbook(file_contents=raw, on_demand=True)
        try:
            context = {}
            if '波形データ' in workbook.sheet_names():
                s = workbook.sheet_by_name('波形データ')
                context['波形データ'] = [[i+1, *s.row_values(i)] for i in range(s.nrows)]
            for config in file['tables']:
                s = workbook.sheet_by_name(config['sheet'])
                sheet = []
                for i in range(s.nrows):
                    row = []
                    for cell in s.row(i):
                        # xlrd error cells contain numeric error codes. They
                        # must remain source errors, never measured numbers.
                        row.append(xlrd.error_text_from_code[cell.value] if cell.ctype == xlrd.XL_CELL_ERROR
                                   else None if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                                   else cell.value)
                    sheet.append(row)
                record = source_series(source, file, sheet, config, archive_sha256=digest)
                for column in record['columns']:
                    if str(column['source_column']) in config.get('names', {}):
                        column['name'] = config['names'][str(column['source_column'])]
                record['source_table']['columns'] = ['excel_row', *[c['name'] for c in record['columns']]]
                record['provenance'].update(documentation=source['documentation'],
                    workbook_context=context, processor='tools/ingest_torsion.py:reviewed-blocks-v1')
                if config.get('retain_original_rows'):
                    # These small summary tables contain specimen names beside
                    # the numeric columns. Keep that exact alignment for audit.
                    record['source_table']['original_rows'] = [[i+1, *r] for i,r in enumerate(sheet)]
                records.append(record)
        finally:
            workbook.release_resources()
    return records
