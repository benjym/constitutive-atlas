"""Rebuild curated public records from checksum-pinned original measurements.

Run with the optional data dependencies: python -m pip install '.[data]'.
Network download is opt-in; the normal website build uses committed processed
assets and requires neither source-format libraries nor upstream availability.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import urllib.request
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.public_data import json_bytes, normalize_opara, load_curated
from tools.ingest_tables import read_tables, workbook_context
from tools.ingest_hurley import read_hurley
from tools.ingest_castlegate import read_castlegate
from tools.ingest_leap import read_leap
from tools.ingest_torsion import read_torsion
from tools.ingest_reviewed_xls import read_reviewed_xls
from tools.ingest_staged_tsv import read_staged_tsv
from tools.ingest_chang_mat import read_chang_mat
from tools.source_downloads import zip_member


def native(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    if hasattr(value, 'tolist'):
        return native(value.tolist())
    if isinstance(value, (tuple, list)):
        return [native(x) for x in value]
    return value


def read_opara(raw, provenance):
    try:
        import h5py
    except ImportError as error:
        raise RuntimeError('Install optional data dependencies: pip install ".[data]"') from error
    with h5py.File(io.BytesIO(raw)) as f:
        channels, attributes, inputs = {}, {}, {}
        for name, dataset in f.items():
            attrs = {k: native(v) for k, v in dataset.attrs.items()}
            if dataset.ndim == 0:
                inputs[name] = dict(value=native(dataset[()]), attributes=attrs)
            elif dataset.ndim == 1:
                channels[name], attributes[name] = native(dataset[()]), attrs
            else:
                raise ValueError('Unreviewed multidimensional source channel: ' + name)
        return normalize_opara(channels, attributes, inputs,
                               {k: native(v) for k, v in f.attrs.items()}, provenance)


def ingest(source, raw_dir):
    records = []
    for file in source['files']:
        content = (raw_dir / file['filename']).read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Source checksum mismatch: ' + file['filename'])
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = [x for x in archive.infolist() if not x.is_dir()]
            if len(members) != file['expected_tests']:
                raise ValueError('Unexpected source archive test count')
            for member in sorted(members, key=lambda x: x.filename):
                match = re.fullmatch(r'([1-6])_(TXCD|TXCU)_(20|40|60|100|200|300)kPa\.h5', member.filename)
                if not match or member.file_size > 50_000_000:
                    raise ValueError('Unreviewed source archive member')
                raw = archive.read(member)
                provenance = {k: source[k] for k in ('source_url', 'license', 'license_url', 'attribution')}
                provenance.update(archive_sha256=digest, archive=file['filename'], member=member.filename,
                                  member_sha256=hashlib.sha256(raw).hexdigest(), source_id=source['id'],
                                  test_id='OPARA-' + match[2] + '-' + match[3],
                                  redistribution='Public hosting under CC BY 4.0; Atlas unit/format conversions identified.',
                                  original_publication=source['original_publication'],
                                  processor='tools/ingest_public_data.py:opara-v1')
                records.append(read_opara(raw, provenance))
    return records


def number(value):
    """Excel source numbers include decimal-comma strings; blanks stay missing."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = float(value.replace(',', '.').strip() if isinstance(value, str) else value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def read_geolab(source, raw_dir):
    try:
        import openpyxl
    except ImportError as error:
        raise RuntimeError('Install optional data dependencies: pip install ".[data]"') from error
    records = []
    for file in source['files']:
        path = raw_dir / file['filename']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != file['sha256']:
            raise ValueError('Source checksum mismatch: ' + path.name)
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            for sheet_name in file.get('drained_sheets', []):
                sheet = workbook[sheet_name]
                all_rows = list(sheet.iter_rows(values_only=True))
                header = next((i for i, r in enumerate(all_rows[:30]) if len(r) >= 6 and
                               r[1:6] == ('Axial strain', 'Volumetric strain', 'Axial stress',
                                          'Radial stress', 'Deviatoric stress')), None)
                if header is None or all_rows[header + 1][1:6] != ('(%)', '(%)', '(kPa)', '(kPa)', '(kPa)'):
                    raise ValueError('Unreviewed GEOLAB layout: ' + sheet_name)
                # Retain the native table, including partial observations. The
                # normalized overlay only uses rows containing measured strain/q.
                table, rows, row_numbers = [], [], []
                for i, cells in enumerate(all_rows[header + 2:], header + 3):
                    values = list(cells[1:6])
                    if not any(x is not None for x in values):
                        continue
                    table.append([i, *values])
                    axial, volumetric, axial_stress, radial_stress, q = map(number, values)
                    if axial is None or q is None:
                        continue
                    row = dict(axial_strain=axial / 100, q=q * 1000)
                    if volumetric is not None:
                        row['volumetric_strain'] = volumetric / 100
                    if axial_stress is not None:
                        row['axial_reported_stress'] = axial_stress * 1000
                    if radial_stress is not None:
                        row['radial_reported_stress'] = radial_stress * 1000
                    rows.append(row)
                    row_numbers.append(i)
                if not rows:
                    raise ValueError('Selected GEOLAB sheet contains no usable observations')
                metadata = [[i + 1, *r] for i, r in enumerate(all_rows[:header]) if any(x is not None for x in r)]
                record_id = 'GEOLAB-' + file['material_id'] + '-' + re.sub(r'[^A-Za-z0-9_-]', '-', sheet_name).upper()
                provenance = {k: source[k] for k in ('source_url', 'license', 'license_url', 'attribution')}
                provenance.update(source_id=source['id'], archive=file['filename'], archive_sha256=digest,
                                  member=sheet_name, member_sha256=hashlib.sha256(json_bytes(table)).hexdigest(),
                                  member_hash_scope='Native B:F values and original Excel row numbers, canonical JSON.',
                                  source_metadata=metadata, source_rows=row_numbers,
                                  workbook_context=workbook_context(workbook),
                                  processor='tools/ingest_public_data.py:geolab-drained-v1',
                                  transformations=['Axial and volumetric strain: source percent divided by 100.',
                                                   'Source stress channels: kPa multiplied by 1000.',
                                                   'Reported principal stresses retain unspecified total/effective meaning; p is not inferred.',
                                                   'All native B:F observations retained in source_table; incomplete overlay rows are not zero-filled.'],
                                  redistribution='Public hosting under CC BY 4.0; source references and Atlas modifications retained.')
                warnings = ['Source principal-stress headers do not explicitly distinguish total and effective stress; mean effective stress and initial effective stress are not inferred.',
                            'Initial-state values are retained in source metadata; they are not automatically applied because several workbook conditions appear copied between sheets.',
                            'Original acquisition versus digitization status has not been established for this curve.',
                            'Post-localization specimen averages are not homogeneous material-point measurements.']
                if file['material_id'] == 'BASKARP':
                    # C=-B in parts of this source is suspicious. Keep it for
                    # audit, but do not publish it as measured volume change.
                    for row in rows:
                        row.pop('volumetric_strain', None)
                    warnings.append('Volumetric strain withheld from the overlay: source values need independent review; native values remain in the archival record.')
                records.append(dict(schema_version='0.1', kind='experiment', id=record_id,
                                    material=file['material'], protocol='drained-triaxial',
                                    conventions=dict(stress='compression-positive', strain='compression-positive',
                                                     stress_unit='Pa', strain_unit='1'),
                                    initial={}, warnings=warnings, provenance=provenance, rows=rows,
                                    source_table=dict(columns=['excel_row', *all_rows[header][1:6]],
                                                      units=['1', '%', '%', 'kPa', 'kPa', 'kPa'], values=table)))
        finally:
            workbook.close()
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=ROOT / 'data/raw/public')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--source', action='append', help='Rebuild only these source IDs; verify and retain other committed records')
    args = parser.parse_args()
    sources = json.loads((ROOT / 'data/public_sources.json').read_text())['sources']
    selected = set(args.source or [s['id'] for s in sources])
    if selected - {s['id'] for s in sources}:
        parser.error('Unknown source ID')
    records = ([r for r in load_curated(ROOT) if r['provenance']['source_id'] not in selected]
               if args.source else [])
    for source in sources:
        if source['id'] not in selected:
            continue
        if args.download:
            args.raw_dir.mkdir(parents=True, exist_ok=True)
            for file in source['files']:
                path = args.raw_dir / file['filename']
                if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == file['sha256']:
                    continue
                url = file['url']
                if file.get('download_resolution') == 'designsafe-preview':
                    with urllib.request.urlopen(url, timeout=45) as response:
                        preview = json.loads(response.read(2_000_000))
                    url = preview['href']
                    if urllib.parse.urlparse(url).hostname == 'view.officeapps.live.com':
                        url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('src', [''])[0]
                    if not url.startswith('https://designsafe.tapis.io/v3/files/postits/redeem/'):
                        raise ValueError('Unexpected public DesignSafe download host')
                if file.get('download_resolution') == 'zip-member':
                    content = zip_member(file)
                else:
                    with urllib.request.urlopen(url, timeout=60) as response:
                        content = response.read(file['size_bytes'] + 1)
                if len(content) != file['size_bytes'] or hashlib.sha256(content).hexdigest() != file['sha256']:
                    raise ValueError('Downloaded file differs from pinned source')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        if source['id'] == 'opara-sand-fines':
            records.extend(ingest(source, args.raw_dir))
        elif source['id'] == 'geolab-v2':
            records.extend(read_geolab(source, args.raw_dir))
            records.extend(read_tables(source, args.raw_dir))
        elif source.get('reader') == 'leap-native':
            records.extend(read_leap(source, args.raw_dir))
        elif source.get('reader') == 'leap-torsion':
            records.extend(read_torsion(source, args.raw_dir))
        elif source.get('reader') == 'castlegate-mts':
            records.extend(read_castlegate(source, args.raw_dir))
            records.extend(read_tables(source, args.raw_dir))
        elif source.get('reader') == 'hurley-3dxrd':
            records.extend(read_hurley(source, args.raw_dir))
        elif source.get('reader') == 'worksheet-tables':
            records.extend(read_tables(source, args.raw_dir))
        elif source.get('reader') == 'chang-mcos':
            records.extend(read_chang_mat(source, args.raw_dir))
        elif source.get('reader') == 'staged-tsv':
            records.extend(read_staged_tsv(source, args.raw_dir))
        elif source.get('reader') == 'reviewed-xls':
            records.extend(read_reviewed_xls(source, args.raw_dir))
        else:
            raise ValueError('Source needs a reviewed reader: ' + source['id'])
    dest = ROOT / 'data/curated'
    dest.mkdir(parents=True, exist_ok=True)
    # load_curated has already verified retained assets. A source-only rebuild
    # need not recompress or rewrite unrelated measurement histories.
    retained = ({entry['id']: entry for entry in
                 json.loads((dest / 'index.json').read_text())['records']}
                if args.source else {})
    entries = []
    for record in sorted(records, key=lambda r: r['id']):
        if args.source and record['provenance']['source_id'] not in selected:
            entries.append(retained[record['id']])
            continue
        content = gzip.compress(json_bytes(record), mtime=0)
        # gzip's OS byte varies across Python/zlib versions; it has no data
        # meaning. Fix it to "unknown" for portable deterministic packaging.
        content = content[:9] + b'\xff' + content[10:]
        filename = record['id'] + '.json.gz'
        (dest / filename).write_bytes(content)
        entries.append(dict(id=record['id'], kind=record['kind'], source_id=record['provenance']['source_id'], path=filename,
                            sha256=hashlib.sha256(content).hexdigest(), rows=len(record['rows'])))
    # Replace the manifest only after all source checks/readers have succeeded.
    (dest / 'index.json').write_bytes(json_bytes(dict(format='atlas-curated-experiments-v1', records=entries)))
    print(f'Ingested {len(entries)} curated measurement records; {sum(e["rows"] for e in entries)} observations.')


if __name__ == '__main__':
    main()
