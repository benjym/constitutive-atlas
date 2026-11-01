"""Audit local experiments without changing or redistributing their measurements."""
import argparse
from collections import Counter
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.reservations import assert_development_ids, load_policy


def audit(data_dir, source_manifest, metadata_path=None):
    sources = read_json(source_manifest)['sources']
    supplement = read_json(metadata_path) if metadata_path is not None else {'experiments': [], 'series_context': []}
    metadata = {r['experiment_id']: r for r in supplement['experiments']}
    if len(metadata) != len(supplement['experiments']):
        raise ValueError('duplicate supplemental experiment metadata')
    archives = {}
    for source in sources:
        path = ROOT/'data/raw'/source['filename']
        archives[source['sha256']] = {'source': source, 'path': path,
                                      'verified': path.exists() and digest(path) == source['sha256']}
    records = []
    policy = load_policy()
    roles = {r['id']: r['role'] for r in policy['experiments']}
    excluded = []
    for path in sorted(Path(data_dir).glob('*.json')):
        # Check filenames before opening responses; also check the actual ID
        # before touching rows or raw members to catch renamed records.
        if roles.get(path.stem) == 'reserved_final':
            excluded.append(path.stem)
            continue
        assert_development_ids([path.stem], policy)
        data = read_json(path)
        assert_development_ids([data['id']], policy)
        rows = data['rows']
        if not rows:
            raise ValueError(f'{path.name}: empty experiment')
        provenance = data['provenance']
        archive = archives.get(provenance['archive_sha256'])
        member_verified = False
        if archive and archive['verified']:
            with zipfile.ZipFile(archive['path']) as z:
                import hashlib
                member_verified = hashlib.sha256(z.read(provenance['member'])).hexdigest() == provenance['member_sha256']
        xs = [r['axial_strain'] for r in rows]
        deltas = [b-a for a, b in zip(xs, xs[1:])]
        # Direction describes the net path. Both signs may indicate measurement
        # noise or reversals; neither is automatically classified as cycling.
        direction = 'compression' if xs[-1] > xs[0] else 'extension' if xs[-1] < xs[0] else 'stationary'
        extra = metadata.get(data['id'])
        if extra and extra['direction'] != direction:
            raise ValueError(f"{data['id']}: measured and source-table loading directions disagree")
        channels = sorted(set.intersection(*(set(r) for r in rows)))
        gaps = ['preparation_and_consolidation_not_in_normalized_record',
                'measurement_uncertainty_not_recorded', 'replicate_group_not_recorded']
        if 'void_ratio' not in data['initial']:
            gaps.append('initial_void_ratio_requires_supplemental_overlay_and_review' if extra else 'initial_void_ratio_missing')
        if not member_verified:
            gaps.append('raw_member_not_verified')
        records.append({'id': data['id'], 'material': data['material'], 'protocol': data['protocol'],
                        'normalized_sha256': digest(path), 'archive_sha256': provenance['archive_sha256'],
                        'member_sha256': provenance['member_sha256'], 'raw_verified': member_verified,
                        'source_url': provenance['source_url'], 'row_count': len(rows),
                        'measured_channels': channels, 'initial_fields': sorted(data['initial']),
                        'supplemental_metadata': extra,
                        'series_context': [r for r in supplement['series_context'] if data['id'] in r['test_ids']],
                        'tabulated_void_ratio_agrees_to_reported_precision':
                            abs(data['initial']['void_ratio']-extra['void_ratio']) <= .5*10**-extra['void_ratio_decimal_places']
                            if extra and 'void_ratio' in data['initial'] else None,
                        'net_direction': direction, 'strain_range': [min(xs), max(xs)],
                        'increasing_steps': sum(d > 0 for d in deltas),
                        'decreasing_steps': sum(d < 0 for d in deltas),
                        'duplicate_steps': sum(d == 0 for d in deltas),
                        'gaps': gaps, 'warnings': data['warnings'],
                        'development_compression_candidate': data['protocol'] == 'drained-triaxial'
                            and direction == 'compression' and all(d >= 0 for d in deltas)
                            and 'void_ratio' in data['initial'] and member_verified})
    if not records:
        raise ValueError('no normalized experiments found; ingest source archives first')
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate experiment IDs')
    return {'paper_record_version': 1, 'kind': 'local_data_audit',
            'source_manifest_sha256': digest(source_manifest), 'experiments': records,
            'excluded_reserved_ids': excluded,
            'supplemental_metadata_sha256': digest(metadata_path) if metadata_path else None,
            'counts': {'experiments': len(records), 'protocol': dict(Counter(r['protocol'] for r in records)),
                       'net_direction': dict(Counter(r['net_direction'] for r in records)),
                       'with_supplemental_metadata': sum(r['supplemental_metadata'] is not None for r in records),
                       'development_compression_candidates': sum(r['development_compression_candidate'] for r in records)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT/'data/normalized')
    parser.add_argument('--output', type=Path, default=ROOT/'paper/results/data-audit.json')
    parser.add_argument('--source-manifest', type=Path, default=ROOT/'data/sources.json')
    args = parser.parse_args()
    result = audit(args.data_dir, args.source_manifest, ROOT/'paper/study/experiment_metadata.json')
    write_json(args.output, result)
    print(result['counts'])
    print('Local audit:', args.output)


if __name__ == '__main__':
    main()
