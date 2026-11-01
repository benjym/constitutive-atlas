"""Verify immutable inputs, including receipt-bound historical snapshots."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
receipts=[(BASE/'independent-review/review-receipt.json','078eb43542f4795c60201fef88fcde6d44d44c6277e2ba9fad6735cb00771871'),(BASE/'candidate-v1/failure-review/review-receipt.json','19de8687b2698da9ca6ac9b1e0414fc8200ed16ac3e4cfb44a7736868d0f743e'),(HERE/'lifecycle-review/review-receipt.json','03be20573be1b61a2e416f503081bba6e6585e8ff4b781256c5657737ae34c66')]
for receipt,want in receipts:
    check(str(receipt.relative_to(ROOT)),sha(receipt)==want)
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get('path'),str) and 'sha256' in x:
                try:
                    p=checked_receipt(ROOT,receipt.relative_to(ROOT),x['path'],x['sha256'])
                    check('review bound '+x['path'],sha(p)==x['sha256'])
                except Exception as e:check('review bound '+x['path'],False,str(e))
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(json.loads(receipt.read_text()))
manifest=BASE.parent/'manifest.json'
for row in json.loads(manifest.read_text())['files']:
    try:
        p=checked_receipt(ROOT,manifest.relative_to(ROOT),row['path'],row['sha256']);check('historical '+row['path'],sha(p)==row['sha256'])
    except Exception as e:check('historical '+row['path'],False,str(e))
for n in ['native-source-manifest.json','wasm-source-manifest.json']:
    for row in json.loads((HERE/n).read_text())['files']:
        p=ROOT/row['path'];check('build source '+row['path'],p.is_file() and sha(p)==row['sha256'])
for row in json.loads((HERE/'build-source-archive.json').read_text())['files']:
    p=ROOT/row['path'];check('public build-source archive '+row['path'],p.is_file() and sha(p)==row['sha256'])
for n in ['native-triaxial-results.json','wasm-results.json','wasm-corrected-results.json']:
    r=json.loads((HERE/n).read_text())
    for row in r.get('requests',r.get('records',[])):
        if 'raw_path' in row:check('raw '+row['raw_path'],sha(ROOT/row['raw_path'])==row['raw_sha256'])
for p in [HERE/'README.md',HERE/'CAPABILITY_GAP.md',BASE.parent.parent/'DELIVERY.md']:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' not in link and not link.startswith('#'):check('link '+str(p.relative_to(ROOT))+' '+link,(p.parent/link.split('#')[0]).exists())
check('candidate exact',sha(HERE/'model.json')=='e1a21278ac9ce65debd5bf81b181462509e57d7928cc8b8366c75cd6110c4e63')
check('private source exact',sha(ROOT/'.local/private-sources/lade-duncan-1975/original-1975-supplied.pdf')=='bdebd928dbe9e4bac47c0a0328ed0bab79ab3e440a25390f1d646e9ed3749fc5')
report={'id':'lade1975-gap-checkpoint-integrity-archive-resolved-v3','scope':'Integrity/links only; numerical/source-domain failures remain FAIL','supersedes_integrity_check':'checkpoint-integrity.json retained FAIL: one supplemental shared solver revision had changed concurrently; exact historical bytes recovered and canonical snapshots/receipt-bound sidecars added without receipt edits','checks':checks,'passed':all(x['passed'] for x in checks)}
(HERE/'checkpoint-integrity-resolved.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'failures':[x for x in checks if not x['passed']]},indent=2))
raise SystemExit(0 if report['passed'] else 1)
