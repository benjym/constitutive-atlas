"""Publish only the exact accepted TMD2 reporting decision and readable reasons."""
import hashlib
from html import escape
import json
from pathlib import Path

REVIEW = Path('docs/benchmarks/kfs-tmd2-reporting-agent-v1')
MANIFEST_SHA256 = 'b21fd9e92e41e23482a1e5a65a31dae0f58a8843633aa7ee46a98908965fc8f4'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def projection(root, benchmark_assets, model_hash):
    root = Path(root)
    manifest_raw = (root / REVIEW / 'manifest.json').read_bytes()
    if digest(manifest_raw) != MANIFEST_SHA256:
        raise ValueError('TMD2 reporting review manifest mismatch')
    manifest = json.loads(manifest_raw)
    def checked(name):
        raw = (root / REVIEW / name).read_bytes()
        if digest(raw) != manifest['outputs'].get(name):
            raise ValueError('TMD2 reporting review output mismatch: ' + name)
        return raw
    decision_raw, reasons = checked('decision.json'), checked('README.md')
    decision = json.loads(decision_raw)
    if (decision.get('verdict') != 'accept-qualified-reporting'
            or decision.get('model_sha256') != model_hash
            or decision.get('summary_sha256') != digest(benchmark_assets['summary.json'])
            or decision.get('blocking_findings_for_stated_scope') != []
            or {q.get('id') for q in decision.get('questions', [])} != {f'Q{i}' for i in range(1, 7)}
            or len(decision['questions']) != 6
            or any(q.get('outcome') != 'accept-with-stated-qualifications' for q in decision['questions'])
            or not decision.get('remaining_qualifications')):
        raise ValueError('TMD2 reporting review scope mismatch')
    # A rewritten study manifest cannot attach the old verdict to new inputs.
    sources = {
        'parameters.json': 'inputs/parameter-set.json',
        'protocol.json': 'inputs/protocol.json',
        'requests.json': 'inputs/requests.json',
        'summary.json': 'results/summary.json',
        'reproduction.png': 'results/reproduction.png',
    }
    for asset, source in sources.items():
        key = 'docs/benchmarks/kfs-tmd2-research-range-v1/' + source
        if digest(benchmark_assets[asset]) != manifest['public_inputs'].get(key):
            raise ValueError('TMD2 reviewed benchmark asset mismatch: ' + asset)
    title = 'Independent TMD2 reporting review'
    readable = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>' + title + '</title><style>body{max-width:85ch;margin:2rem auto;'
                'padding:0 1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;'
                'overflow-wrap:anywhere;font:inherit}</style></head><body>'
                '<p><a href="../../tmd2.html">TMD2 benchmark</a> · '
                '<a href="./decision.json">Exact decision JSON</a> · '
                '<a href="./review.md">Original review text</a></p><h1>' + title
                + '</h1><pre>' + escape(reasons.decode('utf-8')) + '</pre></body></html>')
    assets = {'review/decision.json': decision_raw,
              'review/review.md': reasons,
              'review/review.html': readable.encode('utf-8')}
    qualifications = ''.join('<li>' + escape(q) + '</li>' for q in decision['remaining_qualifications'])
    section = ('<section aria-labelledby="reporting-review"><h2 id="reporting-review">'
               'Independent reporting review</h2><p>A separate agent accepted qualified '
               'reporting of this exact reconstruction on ' + escape(decision['date'])
               + ', covering all six review questions. General IGS model admission '
               'and experimental validation remain open.</p><p>'
               '<a href="./benchmark-tmd2/review/review.html">Read the decision and reasons</a> · '
               '<a href="./benchmark-tmd2/review/decision.json">Exact decision JSON</a>'
               '</p><p>Decision SHA-256 <code>' + digest(decision_raw) + '</code></p>'
               '<ul>' + qualifications + '</ul></section>')
    return assets, section
