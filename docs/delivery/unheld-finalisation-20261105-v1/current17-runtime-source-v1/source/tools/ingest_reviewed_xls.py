"""Explicitly configured XLS blocks from checksum-pinned public archives.

Read values only. Spreadsheet errors remain text, never numeric observations.
Each configured curve retains its specimen context and source coordinates.
"""
from __future__ import annotations

import hashlib
import io
import zipfile

from tools.ingest_tables import source_series


def read_reviewed_xls(source, raw_dir):
    import xlrd

    records = []
    for file in source['files']:
        raw = (raw_dir / file['filename']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Source checksum mismatch: ' + file['filename'])
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            data = archive.read(file['member'])
        member_digest = hashlib.sha256(data).hexdigest()
        if member_digest != file['member_sha256']:
            raise ValueError('XLS member checksum mismatch')
        workbook = xlrd.open_workbook(file_contents=data, on_demand=True)
        try:
            for config in file['tables']:
                sheet = workbook.sheet_by_name(config['sheet'])
                rows = []
                for i in range(sheet.nrows):
                    row = []
                    for cell in sheet.row(i):
                        if cell.ctype == xlrd.XL_CELL_ERROR:
                            row.append(xlrd.error_text_from_code[cell.value])
                        elif cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                            row.append(None)
                        elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
                            row.append(bool(cell.value))
                        else:
                            row.append(cell.value)
                    rows.append(row)
                record = source_series(source, file, rows, config,
                                       archive_sha256=digest,
                                       member_sha256=member_digest,
                                       workbook_info=[
                                           [i + 1, *row[:12]]
                                           for i, row in enumerate(rows)
                                           if any(v is not None for v in row[:12])])
                record['provenance'].update(
                    member=file['member'], sheet=config['sheet'],
                    processor='tools/ingest_reviewed_xls.py:reviewed-xls-v1')
                record['source_table']['original_rows'] = [
                    [i + 1, *row] for i, row in enumerate(rows)
                    if any(v is not None for v in row)]
                records.append(record)
        finally:
            workbook.release_resources()
    return records
