"""Download pinned public source archives without overwriting local evidence."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def main():
    manifest=json.loads((ROOT/'data/sources.json').read_text());raw=ROOT/'data/raw';raw.mkdir(parents=True,exist_ok=True)
    for source in manifest['sources']:
        path=raw/source['filename']
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:raise ValueError(f'Existing raw file differs from pinned evidence: {path}')
            print('Already verified:',path.name);continue
        req=urllib.request.Request(source['url'],headers={'User-Agent':'ConstitutiveAtlas/0.1 research data retrieval'})
        with urllib.request.urlopen(req,timeout=60) as response:content=response.read(100_000_001)
        if len(content)>100_000_000:raise ValueError('archive exceeds the 100 MB download limit')
        if hashlib.sha256(content).hexdigest()!=source['sha256']:raise ValueError('Provider content changed; review and version the source manifest before ingestion')
        with path.open('xb') as f:f.write(content)
        print('Downloaded and verified:',path.name)


if __name__=='__main__':main()
