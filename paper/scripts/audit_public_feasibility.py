"""Inventory curated fields and evidence gaps, without fitting or plotting responses."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.data_feasibility import classify
from analysis.reservations import assert_development_ids

sys.path.insert(0, str(ROOT))
from atlas.public_data import load_curated


def audit():
    index_path = ROOT/'data/curated/index.json'
    source_path = ROOT/'data/public_sources.json'
    before = {str(p.relative_to(ROOT)): digest(p) for p in (index_path, source_path)}
    index = read_json(index_path)
    # Fail before reading any response assets if the shared collection expands
    # into a reserved or unassigned KFS series.
    assert_development_ids([entry['id'] for entry in index['records']])
    records = load_curated(ROOT)
    entries = {entry['id']: entry for entry in index['records']}
    results = []
    for record in records:
        info = classify(record)
        provenance = record['provenance']
        results.append(dict(id=record['id'], material=record['material'], kind=record['kind'],
                            protocol=record['protocol'], row_count=len(record['rows']),
                            curated_path='data/curated/'+entries[record['id']]['path'],
                            curated_sha256=entries[record['id']]['sha256'],
                            source_url=provenance['source_url'], source_id=provenance['source_id'],
                            archive_sha256=provenance['archive_sha256'],
                            source_member=provenance.get('member'),
                            member_sha256=provenance.get('member_sha256'),
                            conservative_related_record_block=[provenance['source_id'],
                                provenance['archive_sha256'], provenance.get('member')],
                            source_columns=record.get('columns'),
                            initial_fields=sorted(record.get('initial', {})),
                            warnings=record.get('warnings', []), **info))
    results.sort(key=lambda r: r['id'])
    after = {str(p.relative_to(ROOT)): digest(p) for p in (index_path, source_path)}
    if before != after:
        raise ValueError('shared curated manifests changed during the audit; rerun on a consistent snapshot')
    materials = defaultdict(list)
    for record in results:
        materials[record['material']].append(record)
    material_summary = [dict(material=name, record_count=len(rows),
                             kind_counts=dict(Counter(r['kind'] for r in rows)),
                             protocol_counts=dict(Counter(r['protocol'] for r in rows)),
                             minimum_triaxial_fields=sum(r['minimum_triaxial_fields_present'] for r in rows),
                             native_drained_field_candidates=sum(r['native_drained_field_candidate'] for r in rows))
                        for name, rows in sorted(materials.items())]
    return dict(paper_record_version=1, status='development_field_inventory_not_benchmark_admission',
                inputs=before, code={str(p.relative_to(ROOT)): digest(p) for p in
                    (Path(__file__).resolve(), ROOT/'paper/analysis/data_feasibility.py',
                     ROOT/'atlas/public_data.py', ROOT/'paper/analysis/reservations.py')},
                exposure='Machine audit reads curated rows to count channel availability; no response curves, errors or parameter fits are produced. No blind-data claim.',
                limits=['Records and material labels are not verified independent specimens or materials.',
                        'Source worksheet blocks are conservative grouping hints, not proven experimental batches.',
                        'Complete fields do not establish valid conventions, control fidelity, uniformity, history, uncertainty or applicability.',
                        'Original workbook/archive identities are pinned; independent transcription and experimental review remain open.',
                        'The current paper calibration adapter uses KFS normalized records. These candidates require explicit adaptation and review.'],
                counts=dict(records=len(results), material_labels=len(materials),
                            by_kind=dict(Counter(r['kind'] for r in results)),
                            by_disposition=dict(Counter(r['disposition'] for r in results))),
                materials=material_summary, records=results)


def report(value):
    lines = ['# Curated-data feasibility audit', '',
             'This is a field inventory, not benchmark admission. Counts refer to records, not independent specimens.', '',
             '| Material label | Records | Minimum triaxial fields | Drained field candidates |',
             '| --- | ---: | ---: | ---: |']
    for row in value['materials']:
        lines.append(f"| {row['material']} | {row['record_count']} | {row['minimum_triaxial_fields']} | {row['native_drained_field_candidates']} |")
    lines += ['', '## Limits', ''] + ['- '+s for s in value['limits']]
    lines += ['', 'The JSON retains record hashes, source identities, related-record blocks, channel completeness, initial fields and warnings. No measurements are copied into this report.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'paper/results/public-feasibility')
    args = parser.parse_args()
    result = audit()
    write_json(args.output/'report.json', result)
    (args.output/'report.md').write_text(report(result))
    print(result['counts'])
