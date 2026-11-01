"""Replay saved delivery checks; no compilation, simulation or admission."""
from pathlib import Path
import argparse,hashlib,json
p=Path(__file__).resolve().parent;root=p.parents[2]
def read(f):return json.loads(f.read_text())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def norm(x):
    if isinstance(x,dict):return {k:norm(v) for k,v in x.items() if k!='elapsed_ms'}
    if isinstance(x,list):return [norm(v) for v in x]
    return x
args=argparse.ArgumentParser();args.add_argument('--package',type=Path);a=args.parse_args()
for name,h in read(p/'manifest.json')['files'].items():assert sha(p/name)==h,name
for name,h in read(p/'manifest.json')['references'].items():assert sha(root/name)==h,name
freeze=read(p/'package-freeze.json');protocol=read(p/'protocol.json');pkg=read(p/'package-check.json');b=p/'browser'
if a.package:
    assert {f.relative_to(a.package).as_posix():sha(f) for f in a.package.rglob('*') if f.is_file()}==freeze['files']
setup=read(b/'setup.json')
for name,r in protocol['qualified_artifacts'].items():
    assert freeze['files'][name]==r['sha256']
    assert setup['asset_hashes'][name]==r['sha256']
assert len(freeze['files'])==804
mixed=root/'catalogue/investigations/declared-loading-mixed-v1'
refs={r['id']:r['result'] for r in read(mixed/'wasm/observe.stdout.txt')['rows']}
requests={r['id']:r['specification'] for r in read(mixed/'requests.json')}
rows=[(r['id']+'/ordinary',r) for r in pkg['existing_ten']]+[('research-hp-extracted-asbs-gis-2024-v03/ordinary',pkg['ordinary_gis_default']),('research-hp-extracted-asbs-gis-2024-v03/named',pkg['named_example'])]
# Request identifiers are documentary: bind by full request bytes rather than suffix.
points=0
for _,r in rows:
    key=next(k for k,v in requests.items() if v==r['specification'])
    assert norm(r['result'])==norm(refs[key]),key
    points+=len(r['result']['points'])
assert len(rows)==12 and points==1020
for name,ref in [('named-run',pkg['named_example']),('imported-run',pkg['named_example']),('named-audit',pkg['named_example']),('import-audit',pkg['named_example']),('reset-audit',pkg['ordinary_gis_default']),('switch-back-audit',pkg['ordinary_gis_default']),('tresca-audit',next(r for r in pkg['existing_ten'] if r['id'].startswith('tresca')))]:
    observed=read(b/(name+'.json'));spec=observed.get('specification',observed.get('request',{}).get('specification'))
    assert spec==ref['specification'],name
    assert norm(observed['result'])==norm(ref['result']),name
named=read(b/'named-audit.json');assert named['preview']['inputs_unchanged']
assert any(x['href']=='https://doi.org/10.1016/j.compgeo.2024.106480' for x in named['source_links'])
for name in ['reset-audit','switch-back-audit']:
    o=read(b/(name+'.json'));assert o['controls']['target']=='1' and o['controls']['steps']=='100' and o['controls']['numerical-max_depth']=='14'
    assert o['controls']['state-h']=='0,0,0,0,0,0' and o['controls']['state-Omega']=='0'
tresca=read(b/'tresca-audit.json');assert tresca['matching_disabled'] and all(x['u'] is None for x in tresca['result']['points'])
disclosure=read(b/'disclosure-audit.json');review=disclosure['review']
assert review['status']=='pending' and not review.get('independent') and not review.get('reviewer')
assert all(t in disclosure['text'] for t in ['Retained numerical evidence','Pair assessment: not assessed.','Recorded source-review status: pending'])
assert read(p/'closure.json')['console']==dict(messages=0,errors=0,warnings=0)
print('PASS: pinned saved package/browser evidence; 12 requests/1020 points; exact import/reset/switch responses; draft disclosures. No scientific admission.')
