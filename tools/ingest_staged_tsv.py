"""Read checksum-pinned, reviewed staged TSV histories without resampling.

Records split at source procedure-label changes and the storage size limit.
Time and strain origins remain
those of the original file, and preparation/shearing files are never joined.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
import zipfile


def read_staged_tsv(source, raw_dir):
    records = []
    for file in source['files']:
        archive_bytes = (raw_dir / file['filename']).read_bytes()
        digest = hashlib.sha256(archive_bytes).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Source checksum mismatch: ' + file['filename'])
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            for config in file['tables']:
                raw = archive.read(config['member'])
                member_digest = hashlib.sha256(raw).hexdigest()
                if member_digest != config['sha256']:
                    raise ValueError('TSV member checksum mismatch')
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(raw), encoding=config['encoding']), delimiter='\t')
                headers = next(reader)
                if headers != config['headers']:
                    raise ValueError('Unreviewed TSV header: ' + config['member'])
                stage_column = config.get('stage_column', len(headers))
                if stage_column not in (0, len(headers)):
                    raise ValueError('Only a final procedure column is reviewed')
                if len(config['units']) != len(headers) - (1 if stage_column else 0):
                    raise ValueError('TSV unit configuration does not match columns')
                columns = [dict(key='c'+str(i), name=headers[i-1], unit=unit, source_column=i)
                           for i, unit in enumerate(config['units'], 1)]
                segments, blanks = [], []
                previous_time = None
                for line, cells in enumerate(reader, 2):
                    if len(cells) != len(headers):
                        raise ValueError('Unreviewed TSV row width')
                    if not any(cells):
                        blanks.append(line)
                        continue
                    numbers = [float(v) for j, v in enumerate(cells, 1) if j != stage_column]
                    if not all(math.isfinite(v) for v in numbers):
                        raise ValueError('Invalid TSV numeric measurement')
                    if previous_time is not None and numbers[0] < previous_time:
                        raise ValueError('Source time decreases')
                    previous_time = numbers[0]
                    label = cells[stage_column-1] if stage_column else None
                    # A storage partition is not a physical stage boundary.
                    if not segments or segments[-1]['label'] != label or len(segments[-1]['rows']) == 200000:
                        segments.append(dict(label=label, rows=[], native=[], lines=[]))
                    segment = segments[-1]
                    segment['rows'].append({c['key']: n for c, n in zip(columns, numbers)})
                    segment['native'].append([line, *numbers, *([label] if stage_column else [])])
                    segment['lines'].append(line)
                if sum(len(s['rows']) for s in segments) != config['expected_observations']:
                    raise ValueError('Unexpected TSV observation count')
                for i, segment in enumerate(segments, 1):
                    provenance = {k: source[k] for k in ('source_url', 'license', 'license_url', 'attribution')}
                    provenance.update(source_id=source['id'], archive=file['filename'], archive_sha256=digest,
                                      member=config['member'], member_sha256=member_digest,
                                      member_hash_scope='Original TSV member bytes', source_encoding=config['encoding'],
                                      source_rows=segment['lines'], source_headers=headers,
                                      source_stage_label=segment['label'], stage_index=i,
                                      segments_in_file=len(segments),
                                      partition_rule='Source procedure-label changes and 200000-row storage limit; no inferred physical stage boundaries.',
                                      specimen=config['specimen'],
                                      phase=config['phase'], blank_source_lines=blanks,
                                      boundary_conditions=config['boundary_conditions'],
                                      readme_url=file['readme_url'], readme_sha256=file['readme_sha256'],
                                      processor='tools/ingest_staged_tsv.py:staged-tsv-v1',
                                      transformations=[
                                          'TSV numeric cells parsed using the explicitly configured encoding, in native units; every numeric observation retained in acquisition order.',
                                          'Records split at source procedure-label changes when supplied and at the 200000-row storage limit; labels, source line numbers and blank-line positions retained.',
                                          'No time/strain reset, interpolation, stress inference, sign change or concatenation of separately zeroed phases.'])
                    records.append(dict(schema_version='0.1', kind='measurement-series',
                                        id=config['id_prefix']+'-'+str(i).zfill(2),
                                        material=file['material']+' — '+config['specimen'], protocol=config['protocol'],
                                        conventions=dict(stress='source-defined', strain='source-defined',
                                                         stress_unit='per-channel', strain_unit='per-channel'),
                                        initial={}, columns=columns, rows=segment['rows'], provenance=provenance,
                                        source_plot=dict(x='c1', y='c2'),
                                        source_table=dict(columns=['source_line', *headers],
                                                          units=['1', *config['units'], *(['text'] if stage_column else [])], values=segment['native']),
                                        warnings=[
                                            'One segment of a continuous test history, not an independent specimen or reinitialized material-point experiment.',
                                            'Time and strain origins are local to the original phase file; preparation and shearing phases must not be directly concatenated.',
                                            'Source signs and measured fluid-flow signal are retained; fluid flow is not inferred to be specimen volumetric strain.',
                                            'Shaly Opalinus Clay is a clay rock, distinct from soft-soil clay.',
                                            'Not qualified for model overlays; initial state, bedding conventions and full replay protocol need review.',
                                            *config.get('warnings', [])]))
    return records
