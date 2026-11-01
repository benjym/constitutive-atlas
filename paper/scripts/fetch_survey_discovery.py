"""Fetch a bounded bibliographic pilot, retaining unmodified response bytes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json


def fetch(protocol_path, output):
    protocol = read_json(protocol_path)
    if protocol['status'] != 'development_search_protocol_not_completed_systematic_survey':
        raise ValueError('only the declared development search is implemented')
    search = protocol['bibliographic_pilot']
    if search['endpoint'] != 'https://api.crossref.org/works':
        raise ValueError('only the declared public Crossref endpoint is supported')
    if search['parameters']['filter'] != 'until-pub-date:'+protocol['cutoff']:
        raise ValueError('search cutoff and API filter differ')
    identifiers = [q['id'] for q in search['queries']]
    if (len(identifiers) != len(set(identifiers)) or
            any(not re.fullmatch(r'[a-z][a-z0-9-]*', name) for name in identifiers)):
        raise ValueError('distinct safe query IDs required before writing raw responses')
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(protocol_path, output/'protocol.json')
    shutil.copy2(__file__, output/'fetch_script.py')
    manifest = dict(paper_record_version=1, protocol_id=protocol['id'], protocol_sha256=digest(protocol_path),
                    fetch_script_sha256=digest(__file__), status='incomplete_development_discovery', batches=[])
    write_json(output/'manifest.json', manifest)
    previous_end = 0.
    for query in search['queries']:
        # Public API response headers currently allow one concurrent request and
        # one request per second. Sequential requests also keep attribution clear.
        delay = 1.1-(time.monotonic()-previous_end)
        if delay > 0:
            time.sleep(delay)
        params = dict(search['parameters'], **{'query.bibliographic': query['query']})
        url = search['endpoint']+'?'+urlencode(params)
        raw, headers = output/f"{query['id']}.json", output/f"{query['id']}.headers"
        started = datetime.now(timezone.utc).isoformat()
        process = subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
            '--max-time', '60', '--user-agent', 'constitutive-atlas-paper-discovery/0.1',
            '--dump-header', str(headers), '--output', str(raw), url], capture_output=True, text=True)
        previous_end = time.monotonic()
        if process.returncode:
            write_json(output/'failure.json', dict(query_id=query['id'], request_url=url,
                requested_at=started, curl_exit_code=process.returncode, message=process.stderr))
            raise RuntimeError(f"{query['id']}: metadata fetch failed; retained partial request evidence")
        response = json.loads(raw.read_bytes())
        if response.get('status') != 'ok' or response.get('message-type') != 'work-list':
            raise ValueError('unexpected discovery response; retain it for investigation')
        batch = dict(id=query['id'], query=query['query'], request_url=url, cursor_requested=params['cursor'],
                     requested_at=started, retrieved_at=datetime.now(timezone.utc).isoformat(),
                     raw_path=str(raw.relative_to(ROOT)), raw_sha256=digest(raw),
                     headers_path=str(headers.relative_to(ROOT)), headers_sha256=digest(headers),
                     returned_records=len(response['message']['items']), next_cursor=response['message'].get('next-cursor'),
                     screening_status='unscreened')
        manifest['batches'].append(batch)
        write_json(output/'manifest.json', manifest)
        print(query['id'], batch['returned_records'], 'unscreened records', flush=True)
    manifest['status'] = 'completed_bounded_development_discovery_not_survey_completion'
    write_json(output/'manifest.json', manifest)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=ROOT/'paper/study/survey_protocol.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    fetch(args.protocol.resolve(), args.output.resolve())
