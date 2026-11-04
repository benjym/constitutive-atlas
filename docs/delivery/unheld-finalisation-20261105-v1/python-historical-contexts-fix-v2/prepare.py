from pathlib import Path
import json,hashlib
R=Path('/Users/bmar5496/code/constitutive-atlas');W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');N=R/'docs/delivery/unheld-finalisation-20261105-v1';O=N/'python-historical-contexts-fix-v2';V=N/'python-historical-contexts-fix-v1';P=O/'proposed';D='docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2'
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,b):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b if isinstance(b,bytes)else b.encode())
def js(v):return json.dumps(v,indent=2)+'\n'
vdelta=json.loads((V/'source-delta.json').read_text());vrows={x['path']:x for k in('changes','retained_inputs')for x in vdelta[k]}
def base(n):
 if(V/'original'/n).is_file():return(V/'original'/n).read_bytes()
 if n in vrows and vrows[n]['preimage_sha256']is None:return None
 return(W/n).read_bytes()if(W/n).is_file()else None
excluded={'tests/historical_generation.py','tests/fixtures/source-archive-map.json','tests/fixtures/current-sixteen-baseline-v03-v1.json','tests/fixtures/current-sixteen-baseline-v03-v1.models.json','tests/fixtures/historical-routing-v1.json'}
for n in vrows:
 if n in excluded:continue
 b=(V/'proposed'/n).read_bytes()
 if n in('tests/historical_burgers.py','tests/historical_mcc_reference.py'):
  b=b.replace(b'tests/fixtures/historical-routing-v1.json',(D+'/historical-routing-v1.json').encode())
 if n in('tests/test_historical_generation.py','tests/test_controlled_time.py'):
  b=b.replace(b'tests/fixtures/current-sixteen-baseline-v03-v1.json',(D+'/current-sixteen-baseline-v03-v1.json').encode())
 if n=='tests/test_historical_generation.py':b=b.replace(b'from tests.historical_generation import contexts, public_models, public_paths, verified',b'from tests.historical_generation_v03 import contexts, public_models, public_paths, verified')
 put(P/n,b)
for name in('current-sixteen-baseline-v03-v1.models.json','historical-routing-v1.json'):
 put(P/D/name,(V/'proposed/tests/fixtures'/name).read_bytes())
fixture=json.loads((V/'proposed/tests/fixtures/current-sixteen-baseline-v03-v1.json').read_text());fixture['catalogue']['path']=D+'/current-sixteen-baseline-v03-v1.models.json';put(P/D/'current-sixteen-baseline-v03-v1.json',js(fixture))
ledger='tests/fixtures/historical-test-contexts.json';lb=(W/ledger).read_bytes();put(P/D/'historical-test-contexts.json',lb)
adapter='''"""Archive-aware current-context verification; original historical helper unchanged."""
import hashlib,json
from pathlib import Path
from atlas.model import ROOT
from atlas.evidence import checked_receipt
from tests.historical_generation import contexts, public_models, public_paths, catalogue, generate
LEDGER=ROOT/LEDGER_NAME
LEDGER_SHA=LEDGER_DIGEST

def verified(item):
    if hashlib.sha256(LEDGER.read_bytes()).hexdigest()!=LEDGER_SHA:
        raise ValueError('original historical ledger changed')
    path=(ROOT/item['path']).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('historical context path escapes root')
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
        path=checked_receipt(ROOT,LEDGER.relative_to(ROOT),item['path'],item['sha256'])
    if 'receipt' in item:
        document=json.loads(verified(item['receipt']).read_text())
        for key in item.get('receipt_keys',[item.get('receipt_key')]):document=document[key]
        if document!=item['sha256']:
            raise ValueError('historical source is not bound by its original receipt')
    return path
'''.replace('LEDGER_NAME',repr(D+'/historical-test-contexts.json')).replace('LEDGER_DIGEST',repr(sha(lb)))
put(P/'tests/historical_generation_v03.py',adapter)
# Own exact ledger sidecar, detached from controlled tests/fixtures closure.
oldmap=json.loads((V/'proposed/tests/fixtures/source-archive-map.json').read_text());mapping={'version':'immutable-source-archive-map-0.1','documents':{D+'/historical-test-contexts.json':sha(lb)},'entries':oldmap['entries']};put(P/D/'source-archive-map.json',js(mapping))
def effective(n):return(P/n).read_bytes()if(P/n).is_file()else base(n)
def archive(n,h):
 a=f'catalogue/source-snapshots/{h}/{n}'
 candidates=[P/a,W/a,R/a,V/'proposed'/a,R/n,R/'docs/delivery/unheld-finalisation-20261102-v1/baseline-migration/originals'/n]
 for p in candidates:
  if p.is_file()and sha(p.read_bytes())==h:put(P/a,p.read_bytes());return a
 raise ValueError('missing exact source '+n+' '+h)
audit=[];mixed='catalogue/investigations/tresca-mixed-catalogue-v1';review='docs/reviews/tresca-v5-source-integration-v1'
for folder in(mixed,review):
 m=folder+'/source-archive-map.json';mapping=json.loads((P/m).read_text())
 docs=['source-pins.json','dependency-pins.json','prospective-freeze.json','manifest.json']if folder==mixed else['source-pins.json','manifest.json']
 for name in docs:
  doc=folder+'/'+name;b=(W/doc).read_bytes();data=json.loads(b);mapping['documents'][doc]=sha(b)
  if isinstance(data.get('files'),list):pairs=[(r['path'],r['sha256'])for r in data['files']]
  else:pins=data.get('files',data);pairs=[(n,h)for n,h in pins.items()if isinstance(h,str)and len(h)==64]
  for n,h in pairs:
   current=effective(n);entries=[e for e in mapping['entries']if e.get('original_path')==n and e.get('sha256')==h]
   if entries or current is None or sha(current)!=h:
    a=archive(n,h)
    if not entries:mapping['entries'].append({'original_path':n,'sha256':h,'archived_path':a})
    selected=a
   else:selected=n
   audit.append({'document':doc,'path':n,'sha256':h,'selected':selected,'routed':selected!=n})
 put(P/m,js(mapping))
put(O/'tresca-full-receipt-audit.json',js(audit))
changes=[];retained=[]
for p in sorted(P.rglob('*')):
 if not p.is_file():continue
 n=str(p.relative_to(P));b=base(n);row={'path':n,'preimage_sha256':sha(b)if b is not None else None,'sha256':sha(p.read_bytes()),'size_bytes':p.stat().st_size,'mode':'0644'}
 (retained if row['preimage_sha256']==row['sha256']else changes).append(row)
 if b is not None and row['preimage_sha256']!=row['sha256']:put(O/'original'/n,b)
put(O/'source-delta.json',js({'author_run':'/root/publication_operations_review','baseline':'702 plus accepted A3; parent restores Bv1 first','changes':changes,'retained_inputs':retained}))
print(js({'changes':len(changes),'retained':len(retained),'all_tresca_receipts':len(audit),'routed':sum(r['routed']for r in audit)}))
