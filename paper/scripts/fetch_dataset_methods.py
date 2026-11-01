"""Fetch a bounded set of public methods assets; never execute downloaded code."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'paper/results/sources/dataset-methods-2026-10-31'
LOG = ROOT / 'paper/study/dataset_methods_downloads.json'


def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'ConstitutiveAtlas-paper-source-review/1.0'}), timeout=30) as response:
        return response.read()


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    listing = ROOT / 'tmp/dataset-survey/PRJ-3484-files.json'
    assets = []
    for item in json.loads(listing.read_text()):
        if item['name'].endswith(('.pdf', '.m')):
            assets.append({
                'name': item['name'], 'provider': 'DesignSafe PRJ-3484',
                'source_url': 'https://www.designsafe-ci.org/api/datafiles/tapis/public/preview/designsafe.storage.published/' + quote(item['path'], safe=''),
                'expected_bytes': item['length'], 'resolve_preview': True,
            })
    assets += [{
        'name': 'GEOLAB-Record-of-Changes.txt', 'provider': 'Zenodo 12697903 v2',
        'source_url': 'https://zenodo.org/records/12697903/files/Record%20of%20Changes.txt?download=1',
        'expected_bytes': 495, 'resolve_preview': False,
    }]
    records = []
    for asset in assets:
        record = dict(asset)
        target = DEST / asset['name']
        try:
            url = asset['source_url']
            if asset['resolve_preview']:
                # Signed redemption URLs are transient and deliberately not logged.
                url = json.loads(get(url))['href']
            data = get(url)
            if len(data) != asset['expected_bytes']:
                raise ValueError(f"Expected {asset['expected_bytes']} bytes, received {len(data)}")
            if asset['name'].endswith('.pdf') and not data.startswith(b'%PDF-'):
                raise ValueError('Response is not a PDF')
            if asset['name'].endswith(('.m', '.txt')):
                if b'<html' in data[:200].lower() or b'<!doctype' in data[:200].lower():
                    raise ValueError('Received HTML instead of source text')
                data.decode('utf-8-sig')
            if target.exists() and target.read_bytes() != data:
                raise ValueError('Existing source differs; refusing to overwrite')
            target.write_bytes(data)
            record.update(status='downloaded', local_copy=str(target.relative_to(ROOT)),
                          bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        except Exception as exc:
            # Do not emit signed URLs from exception messages.
            record.update(status='failed', error_type=type(exc).__name__,
                          http_status=getattr(exc, 'code', None))
        records.append(record)
        print(asset['name'], record['status'], flush=True)
    LOG.write_text(json.dumps({
        'paper_record_version': 1, 'date': '2026-10-31',
        'scope': 'Public methods downloads only; no contacts, response CSV downloads, code execution, fitting or role assignment.',
        'inputs_sha256': {str(listing.relative_to(ROOT)): hashlib.sha256(listing.read_bytes()).hexdigest()},
        'assets': records,
        'review_status': 'retrieval_only_not_scientific_validation',
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
