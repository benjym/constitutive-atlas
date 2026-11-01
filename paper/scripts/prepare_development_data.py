"""Fetch pinned archives and normalize only unreserved development members."""
import argparse
import hashlib
from pathlib import Path
import sys
import urllib.request
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.reservations import POLICY_PATH, assert_development_ids, load_policy, select_members
from analysis.compression_data import normalize_oedometer
sys.path.insert(0, str(ROOT))
from atlas.data import normalize_member


def prepare(manifest_path, output, raw_dir=None):
    manifest = read_json(manifest_path)
    policy = load_policy()
    if manifest['reservation_id'] != policy['id']:
        raise ValueError('source manifest and reservation policy disagree')
    raw_dir = ROOT/'data/raw' if raw_dir is None else Path(raw_dir)
    output = Path(output)
    if output.exists():
        raise ValueError('output exists; use a new directory to preserve the extraction ledger')
    sources = manifest['sources']
    ids = [identifier for source in sources for identifier in source['development_ids']]
    assert_development_ids(ids, policy)
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate development test across archives')
    selected_sources = []
    for source in sources:
        if source.get('protocol', 'drained-triaxial') not in ('drained-triaxial', 'oedometer'):
            raise ValueError('unsupported development source protocol')
        raw_dir.mkdir(parents=True, exist_ok=True)
        path = raw_dir/source['filename']
        if not path.exists():
            request = urllib.request.Request(source['url'], headers={'User-Agent': 'ConstitutiveAtlas/paper-development'})
            with urllib.request.urlopen(request, timeout=50) as response:
                content = response.read(20_000_001)
            if len(content) > 20_000_000 or hashlib.sha256(content).hexdigest() != source['sha256']:
                raise ValueError('download differs from pinned source')
            with path.open('xb') as stream:
                stream.write(content)
        if digest(path) != source['sha256'] or path.stat().st_size != source['size_bytes']:
            raise ValueError('raw archive differs from pinned source; do not overwrite evidence')
        with zipfile.ZipFile(path) as archive:
            selected = select_members(archive.namelist(), source['development_ids'], policy)
            for member in selected.values():
                if archive.getinfo(member).file_size > 5_000_000:
                    raise ValueError('development member exceeds size limit')
        selected_sources.append((source, path, selected))
    output.mkdir(parents=True)
    ledger = {'paper_record_version': 1, 'kind': 'development_data_extraction',
              'manifest_sha256': digest(manifest_path), 'reservation_sha256': digest(POLICY_PATH),
              'normalizer_sha256': digest(ROOT/'atlas/data.py'),
              'compression_normalizer_sha256': digest(ROOT/'paper/analysis/compression_data.py'),
              'script_sha256': digest(__file__), 'read_member_ids': [], 'experiments': []}
    for source, path, selected in selected_sources:
        with zipfile.ZipFile(path) as archive:
            for identifier, member in selected.items():
                # Only these allowlisted members are decompressed and parsed.
                content = archive.read(member)
                member_hash = hashlib.sha256(content).hexdigest()
                normalize = normalize_oedometer if source.get('protocol') == 'oedometer' else normalize_member
                experiment = normalize(content, member, source['sha256'], member_hash)
                if experiment['id'] != identifier:
                    raise ValueError('normalizer changed experiment identity')
                destination = output/'normalized'/f'{identifier}.json'
                write_json(destination, experiment)
                ledger['read_member_ids'].append(identifier)
                ledger['experiments'].append({'id': identifier, 'normalized_sha256': digest(destination),
                                              'archive_sha256': source['sha256'], 'member_sha256': member_hash})
    if digest(POLICY_PATH) != ledger['reservation_sha256'] or digest(manifest_path) != ledger['manifest_sha256']:
        raise ValueError('acquisition inputs changed; inspect local output before reuse')
    write_json(output/'extraction.json', ledger)
    return ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'paper/study/development_sources.json')
    parser.add_argument('--output', type=Path, default=ROOT/'paper/results/development-data')
    args = parser.parse_args()
    result = prepare(args.manifest, args.output)
    print('Normalized development members:', ', '.join(result['read_member_ids']))
    print('Reserved members were excluded before response decompression.')


if __name__ == '__main__':
    main()
