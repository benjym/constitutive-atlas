"""Portable packet/algebra integrity; optional reopening of private sources."""
from pathlib import Path
import argparse,hashlib,json,sys
p=Path(__file__).resolve().parent;root=p.parents[2];sys.path.insert(0,str(p))
from check_algebra import check
read=lambda f:json.loads(f.read_text())
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--private-sources',action='store_true');args=a.parse_args()
m=read(p/'manifest.json')
for n,h in m['files'].items():assert sha(p/n)==h,n
assert check()==read(p/'algebra-results.json') and check()['groups']==9
receipts=read(p/'source-receipts.json')['sources'];assert {r['id'] for r in receipts}=={'hoek','mohr','ssoft','pac'}
if args.private_sources:
 for r in receipts:assert sha(Path(r['private_path']))==r['sha256'] and Path(r['private_path']).stat().st_size==r['bytes']
ledger=read(p/'equation-ledger.json');assert {r['equation'] for r in ledger['main_equations']}==set(range(1,16))
assert all('#equation-' in r['url'] for r in ledger['main_equations'])
x=read(p/'crosswalk-v03.json');assert x['target_schema_version']=='0.3' and not x['executable'] and x['proposed_profile']['stress_scope'] is None
assert len(read(p/'gaps.json')['gates'])==8 and all(g['status']=='open' for g in read(p/'gaps.json')['gates'])
claim=read(p/'claim-receipt.json')['original_board'];assert sha(root/claim['archived_path'])==claim['sha256']
print('PASS: packet integrity,15 main equation locators, nine independent algebra groups; eight source/algorithm gates remain open. No executable or admission claim.')
