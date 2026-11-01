from pathlib import Path
import json,hashlib,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
for packet in [P,ROOT/'docs/reviews/gis-example-twelve-catalogue-v1',ROOT/'docs/reviews/mc-applicability-entry-v1']:
 for rel,expected in read(packet/'manifest.json')['files'].items():assert sha(packet/rel)==expected,rel
receipt=read(P/'package-receipt.json');assert receipt['returncode']==0
assert not (P/'package.stderr').read_text()
files=read(P/'package-files.json')['files'];assert len(files)==810
for name,expected in receipt['qualified_engine'].items():assert files[name]==expected
for group in ['overlays','example_fix_overlays','applicability_overlays']:
 for rel,expected in receipt[group].items():
  output='catalogue.json' if rel=='catalogue/manifest.json' else rel
  if output in files:assert files[output]==expected
x=read(P/'mc-default-browser.json');assert x['specification']['model']=='mohr-coulomb'
assert x['result']['ok'] and len(x['result']['points'])==101
assert all(len(p['state'])==6 for p in x['result']['points'])
assert x['catalogue_hash']==x['result']['catalogue_hash']=='d99e7eb1bdaf778fcdc0386b8828c5c633ff09d9ba0869196ec6e3eddda1ee12'
F=ROOT/'docs/reviews/gis-example-twelve-catalogue-v1';binding=read(F/'checks.json')
archive=ROOT/binding['source_archive'];assert sha(archive)==binding['source_archive_sha256']
with tarfile.open(archive) as t:raw=t.extractfile(binding['member']).read()
assert hashlib.sha256(raw).hexdigest()==binding['member_sha256']
saved=json.loads(next(x['raw']for x in json.loads(raw)['rows']if x['id']==binding['row_id']))
new=read(F/'proposed/protocols/gis2024-small-drained-twelve-v1.json')
old=read(ROOT/'protocols/gis2024-small-drained-example.json')
assert new['specification']==old['specification'] and new['result']==saved
strip=lambda r:{k:v for k,v in r.items()if k not in ['catalogue_hash','elapsed_ms']}
assert strip(saved)==strip(old['result'])
A=ROOT/'docs/reviews/mc-applicability-entry-v1'
oldmatrix=read(ROOT/'catalogue/applicability/kfs-development-v1.json')
newmatrix=read(A/'proposed/catalogue/applicability/kfs-development-v1.json')
assert newmatrix['rows'][:-1]==oldmatrix['rows']
assert newmatrix['rows'][-1]['assessment']=='not_assessed'
assert newmatrix['rows'][-1]['scientific_eligibility']=='undetermined'
assert len(list((ROOT/'models').glob('*.json')))==11
assert not (ROOT/'models/mohr-coulomb.json').exists()
print('PASS: package identity, saved default and proposed assets; browser disclosure failure retained; release incomplete')
