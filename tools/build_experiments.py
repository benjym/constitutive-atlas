"""Deterministic, lossless browser datasets from checksum-pinned source archives."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.data import normalize_member
from atlas.public_data import load_curated

CHANNELS = ('axial_strain', 'q', 'p', 'volumetric_strain', 'pore_pressure')
ATTRIBUTION = 'Wichtmann & Triantafyllidis (2016), Karlsruhe fine sand database, Parts I and II.'


def encode(record):
    """Keep all observations in acquisition order, with only plotted channels."""
    if record['kind'] != 'experiment':
        columns = [c['key'] for c in record['columns']]
        return dict(format='atlas-source-columns-v1',
                    metadata={k: v for k, v in record.items() if k not in ('rows', 'source_table')},
                    columns=columns, values=[[row.get(c) for c in columns] for row in record['rows']])
    columns = [c for c in CHANNELS if any(c in row for row in record['rows'])]
    return dict(format='atlas-experiment-columns-v1',
                metadata={k: v for k, v in record.items() if k not in ('rows', 'source_table')},
                columns=columns, values=[[row.get(c) for c in columns] for row in record['rows']])


def json_bytes(value):
    return (json.dumps(value, separators=(',', ':'), ensure_ascii=False, allow_nan=False)+'\n').encode()


def bundle(destination, *, preview=False, root=ROOT):
    destination = Path(destination)
    registry = json.loads((root/'data/sources.json').read_text())
    releases = json.loads((root/'data/experiment_releases.json').read_text())
    grants = {grant['archive_sha256']: grant for grant in releases['grants']}
    # A rebuild cannot accidentally retain files from an earlier/local release.
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    entries = []
    for source in registry['sources']:
        grant = grants.get(source['sha256'])
        if not preview and not grant:
            continue
        if grant and (not all(grant.get(k) for k in ('evidence', 'recorded_at', 'scope', 'attribution'))
                      or grant.get('public_hosting') is not True):
            raise ValueError('Public dataset grant needs evidence, date, scope, attribution and public_hosting=true')
        path = root/'data/raw'/source['filename']
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest != source['sha256']:
            raise ValueError('Archive differs from pinned source: '+path.name)
        source_entries = []
        with zipfile.ZipFile(path) as archive:
            members = sorted(archive.infolist(), key=lambda i: i.filename)
            for info in members:
                if not re.fullmatch(r'(TMD|TMU)\d+\.dat', Path(info.filename).name, re.IGNORECASE):
                    continue
                if info.file_size > 50_000_000:
                    raise ValueError('Archive member exceeds 50 MB')
                raw = archive.read(info)
                record = normalize_member(raw, info.filename, digest, hashlib.sha256(raw).hexdigest())
                record['provenance'].pop('normalized_at', None)
                record['provenance']['redistribution'] = grant['scope'] if grant else 'local preview; public permission unresolved'
                record['provenance']['attribution'] = grant['attribution'] if grant else ATTRIBUTION
                data = json_bytes(encode(record))
                filename = record['id']+'.json'
                (destination/filename).write_bytes(data)
                entry = dict(id=record['id'], protocol=record['protocol'], material=record['material'],
                             initial=record['initial'], rows=len(record['rows']), path=filename,
                             sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data))
                source_entries.append(entry)
        entries.extend(sorted(source_entries, key=lambda e: int(re.search(r'\d+$', e['id'])[0])))
    for record in load_curated(root):
        data = json_bytes(encode(record))
        filename = record['id'] + '.json'
        (destination/filename).write_bytes(data)
        entries.append(dict(id=record['id'], kind=record['kind'], protocol=record['protocol'], material=record['material'],
                            initial=record['initial'], rows=len(record['rows']), path=filename,
                            sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data)))
    if len({entry['id'] for entry in entries}) != len(entries):
        raise ValueError('Duplicate experiment IDs')
    manifest = dict(schema_version='0.1', release='local-preview' if preview else 'public',
                    attribution='Each test retains its own source, licence and transformation notices.', experiments=entries)
    (destination/'index.json').write_bytes(json_bytes(manifest))
    return manifest
