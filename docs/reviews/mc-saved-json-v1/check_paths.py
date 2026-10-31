"""Check the revised path/parity decoders on synthetic observations only."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE/'revised'))
from assess_paths import assess
from assess_parity import assess as parity

fixture = json.loads(gzip.decompress((HERE/'fixture.json.gz').read_bytes()))
pins = json.loads((HERE/'fixture-pins.json').read_text())
for name,text in fixture.items():
    assert hashlib.sha256(text.encode()).hexdigest() == pins[name]
read = lambda name: json.loads(fixture[name])
rows, requests, catalogue = read('journal.json'), read('requests.json'), read('generated/models.json')
reference = ROOT/'docs/reviews/mc-browser-loading-paths-v1/reference-p360.json'
reference_hash = hashlib.sha256(reference.read_bytes()).hexdigest()
owner = json.loads((reference.parent/'manifest.json').read_text())
assert reference_hash == owner['files']['reference-p360.json']['sha256']
source_result = assess(rows,requests,json.loads(reference.read_bytes()),catalogue)
self_parity = parity(rows,rows,requests)
rejections = []
for label, transform in [
    ('duplicate main response key', lambda raw:'{"ok":false,'+raw[1:]),
    ('overflow in unused main response field', lambda raw:'{"extra":1e999,'+raw[1:]),
]:
    bad=copy.deepcopy(rows);bad[1]['raw']=transform(bad[1]['raw'])
    for name,call in [('path',lambda:assess(bad,requests,json.loads(reference.read_bytes()),catalogue)),
                      ('parity',lambda:parity(bad,rows,requests))]:
        try:call()
        except ValueError:rejections.append(label+' / '+name)
        else:raise AssertionError('invalid raw response accepted: '+label+' / '+name)
report={'passed':True,'source_ideal_path':source_result,'source_ideal_self_parity':self_parity,
        'rejected_raw_corruptions':rejections,'reference_sha256':reference_hash,'compiled_calls':0,
        'scope':'synthetic source-ideal assessor check; self parity is not backend or independent equation verification'}
(HERE/'path-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
