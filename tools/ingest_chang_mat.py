"""Read reviewed numeric MATLAB table exports, without executing MATLAB code.

The optional mat-io reader exposes MCOS table properties directly. Every source
channel remains distinct, including apparatus signals and author-processed views.
"""
from __future__ import annotations

import hashlib
import math


def scalar(value):
    if value.size != 1:
        raise ValueError('Expected scalar MATLAB metadata')
    item = value.item()
    return str(item) if value.dtype.kind in 'US' else float(item)


def decode_table(path):
    try:
        from matio import load_from_mat
    except ImportError as error:
        raise RuntimeError('MAT table ingestion needs Python 3.11+ and optional mat-io==1.0.2 (pip install ".[data]").') from error

    data = load_from_mat(str(path), raw_data=True)
    if set(data) != {'iExpEntry'} or data['iExpEntry'].shape != (1, 1):
        raise ValueError('Unreviewed MATLAB entry layout')
    entry = data['iExpEntry']
    table = entry['RawData'][0, 0]
    if table.classname != 'table':
        raise ValueError('Expected MATLAB table')
    props = table.properties
    names = [scalar(v) for v in props['varnames'].ravel()]
    raw_arrays = list(props['data'].ravel())
    nrows = int(props['nrows'].item())
    if any(v.shape != (nrows, 1) or v.dtype.kind not in 'fiu' for v in raw_arrays):
        raise ValueError('Expected scalar numeric MATLAB columns')
    arrays = [v.ravel() for v in raw_arrays]
    if (len(names) != int(props['nvars'].item()) or len(names) != len(arrays)
            or len(set(names)) != len(names) or any(len(v) != nrows for v in arrays)):
        raise ValueError('Unaligned MATLAB table channels')
    details = props['props'][0, 0]
    descriptions = [scalar(v) for v in details['VariableDescriptions'].ravel()]
    units = [scalar(v) for v in details['VariableUnits'].ravel()]
    if len(descriptions) not in (0, len(names)):
        raise ValueError('Unaligned MATLAB variable descriptions')
    metadata = {k: scalar(entry[k][0, 0]) for k in entry.dtype.names if k != 'RawData'}
    return names, arrays, descriptions, units, metadata


def read_chang_mat(source, raw_dir):
    records = []
    for file in source['files']:
        path = raw_dir / file['filename']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Source checksum mismatch: ' + file['filename'])
        names, arrays, descriptions, source_units, metadata = decode_table(path)
        if names != file['columns'] or descriptions != file['descriptions'] or source_units:
            raise ValueError('Unreviewed MATLAB channel metadata')
        if len(arrays[0]) != file['expected_observations']:
            raise ValueError('Unexpected MATLAB observation count')
        columns = [dict(key='c'+str(i), name=name, unit=file['units'].get(str(i), 'not specified'),
                        source_column=i, source_description=descriptions[i-1] if descriptions else '')
                   for i, name in enumerate(names, 1)]
        rows, native = [], []
        previous_time = None
        for index, values in enumerate(zip(*arrays), 1):
            numbers = [float(v) for v in values]
            if any(math.isinf(v) for v in numbers):
                raise ValueError('Infinite MATLAB measurement')
            row = {c['key']: v for c, v in zip(columns, numbers) if math.isfinite(v)}
            if not row:
                raise ValueError('Entirely missing MATLAB observation needs review')
            if 'c1' not in row:
                raise ValueError('Missing MATLAB elapsed time')
            time = row['c1']
            if previous_time is not None and time < previous_time:
                raise ValueError('Source time decreases')
            previous_time = time
            rows.append(row)
            native.append([index, *[v if math.isfinite(v) else None for v in numbers]])
        # File partitions meet the public loader's bound without downsampling.
        for start in range(0, len(rows), 200000):
            stop = min(start+200000, len(rows))
            provenance = {k: source[k] for k in ('source_url', 'license', 'license_url', 'attribution')}
            provenance.update(source_id=source['id'], archive=file['filename'], archive_sha256=digest,
                              member='iExpEntry.RawData', member_sha256=digest,
                              member_hash_scope='Complete original MAT-file bytes',
                              source_rows=list(range(start+1, stop+1)), matlab_metadata=metadata,
                              source_variable_units=source_units, unit_evidence=file['unit_evidence'],
                              experiment_number=file['experiment_number'],
                              summary_record_id='CHANG-CREEP-TEST-SUMMARY', summary_excel_row=file['experiment_number']+2,
                              processor='tools/ingest_chang_mat.py:chang-mcos-v1 (mat-io 1.0.2 raw properties)',
                              transformations=['All exported numeric channels retained in source order and native units; NaN cells retained as null in source_table and absent in numeric channels.',
                                               'No MATLAB code executed, no inferred bulk strain, no smoothing, fitting, interpolation, sign conversion or history reset.',
                                               'Source table has no VariableUnits; only reviewed time/slip bindings use source-summary units. Other channel units remain unresolved.'])
            records.append(dict(schema_version='0.1', kind='measurement-series',
                                id='CHANG-CREEP-RAW-'+str(file['experiment_number']).zfill(2)+'-'+str(start//200000+1).zfill(2),
                                material=file['material'], protocol='fluid-injection-ring-shear-creep-source',
                                conventions=dict(stress='source-defined', strain='source-defined', stress_unit='per-channel', strain_unit='per-channel'),
                                initial={}, columns=columns, rows=rows[start:stop], provenance=provenance,
                                source_plot=dict(x='c1', y='c'+str(file['slip_column'])),
                                source_table=dict(columns=['matlab_row', *names], units=['1', *[c['unit'] for c in columns]], values=native[start:stop]),
                                warnings=['Ring-shear slip displacement is not homogeneous bulk strain; no material-point overlay or automatic preparation/loading replay is qualified.',
                                          'Export contains apparatus and author-processed channels; these are retained as distinct columns and are not independent experiments.',
                                          'Most channel units are unspecified in the MAT table and remain unresolved; names alone do not authorize a unit conversion.',
                                          'MAT scalar loading-rate metadata may differ from the summary workbook. Source values are retained without choosing a replacement.',
                                          'Repeated shear can reuse a specimen; experiment numbers are not guaranteed independent specimens.']))
    return records
