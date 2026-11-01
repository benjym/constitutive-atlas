"""Reviewed LEAP text/CSV series; retain cycles, signs and source channels."""
from __future__ import annotations

import csv
import hashlib
import io
import math


def read_leap(source, raw_dir):
    records = []
    for file in source['files']:
        raw = (raw_dir / file['filename']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != file['sha256']:
            raise ValueError('LEAP file checksum mismatch: ' + file['filename'])
        if file.get('role') == 'documentation':
            continue
        text = raw.decode('utf-8-sig')
        if file.get('layout') == 'multiline-whitespace':
            lines = text.splitlines()
            if lines[:file['data_start']-1] != file['original_header_lines']:
                raise ValueError('Unreviewed LEAP multiline headers')
            parsed = [file['headers'], *[line.split() for line in lines[file['data_start']-1:]]]
        elif file['delimiter'] == 'whitespace':
            parsed = [line.split() for line in text.splitlines()]
        else:
            parsed = list(csv.reader(io.StringIO(text), delimiter=file['delimiter']))
        footer = []
        if file.get('data_end'):
            footer = [[i+1, *r] for i,r in enumerate(parsed) if i >= file['data_end']]
            parsed = parsed[:file['data_end']]
        # Trailing empty columns are present in several source TSV files.
        for row in parsed:
            while len(row) > len(file['headers']) and not row[-1].strip():
                row.pop()
        if parsed[0] != file['headers']:
            raise ValueError('Unreviewed LEAP source headers: ' + file['filename'])
        width = len(parsed[0])
        rows, source_rows, missing = [], [], []
        for number, cells in enumerate(parsed[1:], file.get('data_start', 2)):
            if not cells:
                continue  # blank CSV padding carries no measurement
            if len(cells) > width:
                raise ValueError('Unexpected LEAP source column count')
            row = {}
            for i in range(width):
                token = cells[i].strip() if i < len(cells) else ''
                if not token:
                    missing.append([number, i+1, token])
                    continue
                try:
                    value = float(token)
                except ValueError as e:
                    raise ValueError('Unreviewed nonnumeric LEAP observation') from e
                if math.isfinite(value):
                    row[f'c{i+1}'] = value
                else:
                    missing.append([number, i+1, token])
            if row:
                rows.append(row)
                source_rows.append(number)
        if not rows or len(rows) > 200000:
            raise ValueError(f'LEAP record has {len(rows)} observations outside reviewed limits: ' + file['filename'])
        provenance = {k: source[k] for k in ('source_url','license','license_url','attribution')}
        provenance.update(source_id=source['id'], archive=file['filename'],archive_sha256=digest,
                          member=file['source_path'],member_sha256=digest, source_rows=source_rows,
                          original_headers=file.get('original_header_lines', file['headers']), missing_source_cells=missing, source_footer=footer,
                          documentation=source.get('documentation', []),
                          processor='tools/ingest_leap.py:native-series-v1',
                          transformations=['Quoted multiline CSV headers parsed; trailing empty columns and blank padding omitted.',
                                           'All numeric observations retained in source order and native units; no interpolation, cycle sorting or stress/strain conversion.',
                                           'Nonfinite or empty observations remain missing and are documented by original record number.'])
        records.append(dict(schema_version='0.1',kind=file.get('kind','measurement-series'),id=file['id'],
            material='Ottawa F65 sand · '+source['campaign'],protocol=file['protocol'], initial={},
            columns=[dict(key=f'c{i+1}',name=' '.join(name.split()) or f'Unlabelled source column {i+1}',unit=file['units'][i]) for i,name in enumerate(file['headers'])],
            conventions=dict(stress='source-defined',strain='source-defined',stress_unit='per-channel',strain_unit='per-channel'),
            source_plot=dict(x=f'c{file["x"]}',y=f'c{file["y"]}'),rows=rows,provenance=provenance,
            warnings=['Source signs and native units are retained. This record is separate from normalized model overlays.',
                      'Zero-filled constrained channels remain source values; they are not evidence of independently measured zero volume change.',
                      'Campaigns and compilations can share experiments. These records do not establish independent validation populations.',
                      *file.get('warnings',[])]))
    return records
