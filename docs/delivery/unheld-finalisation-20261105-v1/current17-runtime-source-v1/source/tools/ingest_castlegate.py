"""Castlegate MTS acquisition blocks; preserve trigger groups and source units."""
from __future__ import annotations

import csv
from contextlib import nullcontext
import hashlib
import math
import zipfile


def read_castlegate(source, raw_dir):
    records = []
    for file in source['files']:
        if not file.get('acquisitions'):
            continue
        path = raw_dir / file['filename']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Castlegate archive checksum mismatch')
        with (zipfile.ZipFile(path) if file['filename'].endswith('.zip') else nullcontext(None)) as archive:
            for config in file['acquisitions']:
                raw = archive.read(config['member']) if archive else path.read_bytes()
                sheet = list(csv.reader(raw.decode('utf-8-sig').splitlines(), delimiter='\t'))
                starts = [i for i, row in enumerate(sheet) if row and row[0] == 'Data Acquisition']
                if len(starts) != config['expected_blocks']:
                    raise ValueError('Castlegate acquisition block count differs')
                for block, begin in enumerate(starts):
                    end = starts[block+1] if block+1 < len(starts) else len(sheet)
                    header, units = sheet[begin+1], sheet[begin+2]
                    reviewed = config['blocks'][block] if config.get('blocks') else config
                    if header != reviewed['headers'] or units != reviewed['units']:
                        raise ValueError('Unreviewed Castlegate channels or units')
                    rows, lines = [], []
                    for line, values in enumerate(sheet[begin+3:end], begin+4):
                        if not any(values):
                            continue
                        while len(values) > len(header) and not values[-1].strip():
                            values.pop()
                        if len(values) != len(header):
                            raise ValueError('Unexpected Castlegate row width')
                        values = [float(v) for v in values]
                        if not all(math.isfinite(v) for v in values):
                            raise ValueError('Nonfinite Castlegate acquisition')
                        rows.append({f'c{i+1}': v for i,v in enumerate(values)})
                        lines.append(line)
                    provenance = {k: source[k] for k in ('source_url', 'license', 'license_url', 'attribution')}
                    provenance.update(source_id=source['id'], archive=file['filename'], archive_sha256=digest,
                                      member=config['member'], member_sha256=hashlib.sha256(raw).hexdigest(),
                                      source_rows=lines, source_metadata=sheet[:starts[0]],
                                      enclosing_archive=file.get('enclosing_archive'), source_specimen=config['id'],
                                      acquisition_metadata=sheet[begin], processor='tools/ingest_castlegate.py:mts-blocks-v1',
                                      transformations=['Source tab-separated numeric readings retained in native units and order.',
                                                       'Original acquisition blocks stay separate; trigger groups are not joined or treated as separate specimens.'])
                    records.append(dict(schema_version='0.1',kind='measurement-series',
                        id=config['id'] + f'-BLOCK-{block+1:02}', material=config.get('material','Castlegate sandstone · hydrostatic specimen 4AT'),
                        protocol=config.get('protocol','hydrostatic-acquisition'), initial={}, provenance=provenance,
                        conventions=dict(stress='source-defined',strain='source-defined',stress_unit='per-channel',strain_unit='per-channel'),
                        columns=[dict(key=f'c{i+1}', name=h, unit=u) for i,(h,u) in enumerate(zip(header,units))],
                        source_plot=dict(x='c1',y='c'+str(header.index('Mean Stress')+1) if 'Mean Stress' in header else 'c8'),rows=rows,warnings=[
                            f"Acquisition block {block+1} from specimen {config['id']}; blocks are not independent tests.",
                            'Load-triggered and time-triggered records retain their own source ordering and time values. No combined elapsed-time axis is inferred.',
                            'Raw MTS signals include apparatus effects, command channels and initial contact/loading. Each channel retains its own stated unit; no specimen-average strain or effective stress is inferred.']))
    return records
