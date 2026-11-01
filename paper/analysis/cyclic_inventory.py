"""Metadata-only cyclic panel inventory; no response assets are opened."""
from collections import Counter, defaultdict

SOURCES = {'leap-2018-dss', 'leap-2018-torsion'}


def build_inventory(report, registry):
    sources = {s['id']: s for s in registry['sources'] if s['id'] in SOURCES}
    if set(sources) != SOURCES:
        raise ValueError('cyclic source declarations missing')
    locators, aliases = {}, defaultdict(list)
    for sid, source in sources.items():
        for file in source['files']:
            aliases[sid, file['sha256']].append(file['filename'])
            entries = ([file] if file.get('id') else []) + file.get('tables', [])
            for entry in entries:
                key = entry['id']
                if key in locators:
                    raise ValueError('ambiguous cyclic record source')
                locators[key] = (sid, file, entry)
    rows = []
    for record in report['records']:
        if record['source_id'] not in SOURCES:
            continue
        sid, file, entry = locators[record['id']]
        if sid != record['source_id'] or file['sha256'] != record['archive_sha256']:
            raise ValueError('cyclic source identity differs from field inventory')
        rows.append(dict(
            id=record['id'], source_id=sid, protocol=record['protocol'],
            curated_path=record['curated_path'], curated_sha256=record['curated_sha256'],
            source_file=file['filename'], source_file_sha256=file['sha256'],
            source_member=record['source_member'],
            source_aliases=sorted(set(aliases[sid, file['sha256']])),
            file_block=sid+':'+file['sha256'],
            split_block=sid, role='unassigned',
            initial_fields=record['initial_fields'], source_columns=record['source_columns'],
            warnings=record['warnings'],
            scientific_admission='not_assessed'))
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate cyclic record')
    return dict(
        paper_record_version=1, status='metadata_only_cyclic_task_design_not_admission',
        exposure='Uses existing field-audit metadata and source declarations; opens no response assets.',
        grouping='File blocks join worksheets from the same bytes. Campaign split blocks conservatively prevent cross-phase/raw-processed leakage until specimen and cross-campaign correspondence is reviewed. Neither grouping establishes independent specimens.',
        counts=dict(records=len(rows), by_source=dict(Counter(r['source_id'] for r in rows)),
                    by_protocol=dict(Counter(r['protocol'] for r in rows)),
                    file_blocks=len({r['file_block'] for r in rows}),
                    campaign_split_blocks=len({r['split_block'] for r in rows})),
        documentation={sid: source.get('documentation', []) for sid, source in sources.items()},
        records=rows)


def validate_assignments(inventory, assignments):
    """Reject phase leakage under the currently declared conservative blocks."""
    rows = {r['id']: r for r in inventory['records']}
    if set(assignments)-set(rows):
        raise ValueError('unknown cyclic assignment')
    blocks = defaultdict(set)
    for identifier, role in assignments.items():
        if role not in {'development', 'reserved_final', 'unused'}:
            raise ValueError('unsupported cyclic role')
        if role != 'unused':
            blocks[rows[identifier]['split_block']].add(role)
    if any(len(roles)>1 for roles in blocks.values()):
        raise ValueError('related cyclic records cross development/final split')
