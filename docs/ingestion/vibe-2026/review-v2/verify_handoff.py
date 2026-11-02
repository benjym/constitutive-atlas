"""Verify frozen source/design receipts; read-only outside this review directory."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifests = [
    ('source-v2/manifest.json', '90603c5756a0a1a8f2edd8cbdcb6d21ad639f51796d2dba78ceaca04047f442c'),
    ('capability-v2/manifest.json', '5c63c2d3ae7e2d8098f017c17937310f80e1f874f2d5d3f69fb667d1fef79c76'),
    ('capability-v2/manifest-addendum.json', 'c6a1a5c607dd9af123d320d9d661ec3f0aa767e94f9e1a7e44448f356b038db3'),
    ('capability-v2/supplement-v3/manifest.json', '8bc98d90c131226ab3af69567035396918ef459432281db300f52d42cd487dc8'),
]
verified = []
for rel, expected in manifests:
    path = HERE.parent / rel
    assert sha(path) == expected, str(path)
    data = json.loads(path.read_text())
    entries = data.get('proposal_files', data.get('files', []))
    if 'addendum' in data:
        entries = entries + [data['addendum']]
    for entry in entries:
        assert sha(ROOT / entry['path']) == entry['sha256'], entry['path']
    verified.append({'path':str(path.relative_to(ROOT)), 'sha256':expected,
                     'bound_entries_verified':len(entries)})

receipt = json.loads((HERE.parent/'source-v2/source-receipt.json').read_text())
for entry in receipt['private_artifacts'] + [receipt['user_original']]:
    assert sha(ROOT / entry['path']) == entry['sha256'], entry['path']

pairs = [('algebra-results.json','reproduced-source-algebra.json'),
         ('initial-context-results.json','reproduced-source-initial-context.json'),
         ('stability-context-results.json','reproduced-source-stability-context.json')]
for original, reproduced in pairs:
    assert json.loads((HERE.parent/'source-v2'/original).read_text()) == json.loads((HERE/reproduced).read_text())

historical = json.loads((HERE.parent/'review-v1/manifest.json').read_text())
old_entries = [e for e in historical['files']
               if '/source-v1/' in e['path'] or '/capability-v1/' in e['path']]
for entry in old_entries:
    assert sha(ROOT / entry['path']) == entry['sha256'], entry['path']

result = {'reviewer':'/root/vibe_gap_review', 'status':'pass',
          'frozen_manifests':verified,
          'private_source_artifacts_verified':len(receipt['private_artifacts']),
          'user_original_verified':True, 'reproduced_source_result_reports_equal':len(pairs),
          'historical_v1_packet_files_unchanged':len(old_entries),
          'vendor_compiled_material_browser_execution':False,
          'cleanup':'Only durable review-v2 files created; no temporary trees/processes.'}
(HERE/'verification-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
