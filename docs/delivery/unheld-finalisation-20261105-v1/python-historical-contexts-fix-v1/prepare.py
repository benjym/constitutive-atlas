"""Source-only candidate preparation; never imports compiler or executes engines."""
from pathlib import Path
import hashlib,json,shutil
R=Path('/Users/bmar5496/code/constitutive-atlas');W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
O=R/'docs/delivery/unheld-finalisation-20261105-v1/python-historical-contexts-fix-v1'; P=O/'proposed'
def sha(b):return hashlib.sha256(b).hexdigest()
def emit(p,b):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b if isinstance(b,bytes)else b.encode())
def js(x):return json.dumps(x,indent=2)+'\n'
gates=json.loads((O/'GATES.json').read_text())
extra='catalogue/agent-reviews/source-archive-map.json'
emit(O/'SCOPE-ADDENDUM.json',js({'before_candidate':True,'purpose':'Parent explicitly authorized active SCLAY A-preimage archival binding; original registry/review bytes unchanged','preimages':{extra:sha((W/extra).read_bytes())}}))
old={}
def edit(name,func):
 b=(W/name).read_bytes();old[name]=b;emit(O/'original'/name,b);emit(P/name,func(b.decode()))
def archive(name,b):emit(P/'catalogue/source-snapshots'/sha(b)/name,b)
edit('tests/historical_generation.py',lambda s:s.replace('from atlas.model import ROOT, load','from atlas.model import ROOT, load\nfrom atlas.evidence import checked_receipt').replace("if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:\n        raise ValueError('historical context hash mismatch: ' + item['path'])", "if not path.is_relative_to(ROOT):\n        raise ValueError('historical context path escapes root: ' + item['path'])\n    if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:\n        path = checked_receipt(ROOT, LEDGER.relative_to(ROOT), item['path'], item['sha256'])"))
edit('tests/historical_sources.py',lambda s:s[:s.index('def preserved_model')]+'''def preserved_model(root, name, expected):
    """Verify the exact model hash supplied by the original preview receipt."""
    if Path(name).name != name:
        raise ValueError('model name must be a basename')
    if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise ValueError('invalid historical model hash')
    if name == 'drucker-prager.json':
        packet = 'catalogue/investigations/dp-dilatancy-domain-v1'
        document = packet + '/manifest.json'
        previous_hash = 'd40db28d8de98b7eb8597c90787d16d1f76bac0d145cabb9a5853e86d811650d'
        candidate_hash = 'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877'
        before = checked_receipt(root, document, packet + '/previous-definition.json', previous_hash)
        after = checked_receipt(root, document, packet + '/candidate-definition.json', candidate_hash)
        if pinned_source(root, 'models/' + name, candidate_hash).read_bytes() != after.read_bytes():
            raise ValueError('historical DP differs from its approved domain revision')
        if expected == previous_hash:
            return before.read_bytes()
    return pinned_source(root, 'models/' + name, expected).read_bytes()
''')
for n in ('tests/test_historical_generation.py','tests/test_controlled_time.py'):
 def change(s):
  s=s.replace('current-sixteen-sclay1-v1','current-sixteen-baseline-v03-v1')
  if n.endswith('test_historical_generation.py'):
   s=s.replace('self.assertTrue(set(paths) < current_paths)',"historical_names = {ROOT / item['path'] for item in data['current_models']}\n        self.assertTrue(historical_names < current_paths)")
  return s
 edit(n,change)
edit('tests/test_clay2005_lab_preview.py',lambda s:s.replace('preserved_model(ROOT,Path(name).name)','preserved_model(ROOT,Path(name).name,pin)'))
for n in ('tests/test_clay2013_lab_preview.py','tests/test_sand_lab_preview.py'):
 edit(n,lambda s:s.replace('preserved_model(ROOT,p.name)','preserved_model(ROOT,p.name,hashlib.sha256(p.read_bytes()).hexdigest())'))
edit('tests/test_burgers.py',lambda s:s.replace("str(R/'verify.py')","str(ROOT/'tests/historical_burgers.py')"))
edit('tests/test_isotropic_reference.py',lambda s:s.replace('from tools.analyze_mcc_continuous import analyze,analyze_followups','from tests.historical_mcc_reference import analyze,analyze_followups'))
models=[json.loads(p.read_text())for p in sorted((W/'models').glob('*.json'))]
catalogue={'schema_version':'0.1','sha256':sha(json.dumps(models,sort_keys=True,separators=(',',':')).encode()),'models':models}
assert catalogue['sha256']=='beb2f2b422c77502cc41c91b1c68921fd9db89f1b7dbc2e4f0368526d627e575'
metadata='tests/fixtures/current-sixteen-baseline-v03-v1.models.json';emit(P/metadata,js(catalogue))
emit(P/'tests/fixtures/current-sixteen-baseline-v03-v1.json',js({'id':'current-sixteen-baseline-v03-v1','models':[{'path':str(p.relative_to(W)),'sha256':sha(p.read_bytes())}for p in sorted((W/'models').glob('*.json'))],'catalogue':{'path':metadata,'sha256':sha((P/metadata).read_bytes())},'authority':{'decision':'docs/delivery/unheld-finalisation-20261105-v1/current16-qualification-result-review-v1/decision.json','sha256':'ccadd0e9daf6c87c804567dbea0ba44af97029f08026d35fb8eb0d5d344198c1'}}))
# Unchanged analyzers are imported under isolated names, with exact source pins.
bp='docs/ingestion/burgers-itasca900/integration-v1';mp='tools/analyze_mcc_continuous.py'
emit(P/'tests/fixtures/historical-routing-v1.json',js({'version':'historical-routing-v1','pins':{f'{bp}/verify.py':sha((W/bp/'verify.py').read_bytes()),f'{bp}/manifest.json':sha((W/bp/'manifest.json').read_bytes()),f'{bp}/freeze.json':sha((W/bp/'freeze.json').read_bytes()),mp:sha((W/mp).read_bytes())}}))
emit(P/'tests/historical_burgers.py','''"""Original saved Burgers verification plus every original installed assertion."""
from pathlib import Path
import hashlib, importlib.util, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
R=ROOT/'docs/ingestion/burgers-itasca900/integration-v1'
def verify():
    context=json.loads((ROOT/'tests/fixtures/historical-routing-v1.json').read_text())
    for name,digest in context['pins'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    sys.path.insert(0,str(R))
    spec=importlib.util.spec_from_file_location('_original_burgers_verify',R/'verify.py')
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    result=original.verify(installed=False)
    manifest=json.loads((R/'manifest.json').read_text())
    freeze=json.loads((R/'freeze.json').read_text())
    for name,digest in manifest['installed_files'].items():
        checked_receipt(ROOT,(R/'manifest.json').relative_to(ROOT),name,digest)
    assert (ROOT/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json').read_bytes()==(R/'model.json').read_bytes()
    assert (R/'target.cmake').read_text() in (ROOT/'CMakeLists.txt').read_text()
    for name,digest in freeze['prior_models'].items():
        checked_receipt(ROOT,(R/'freeze.json').relative_to(ROOT),name,digest)
    return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
''')
emit(P/'tests/historical_mcc_reference.py','''"""Delegate unchanged continuous-reference analysis to its exact historical MCC."""
import hashlib, importlib.util, json
from pathlib import Path
from atlas.evidence import checked_receipt
ROOT=Path(__file__).resolve().parents[1]
def _original(report):
    context=json.loads((ROOT/'tests/fixtures/historical-routing-v1.json').read_text())
    name='tools/analyze_mcc_continuous.py'
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==context['pins'][name],name
    case=next(c for c in report['cases'] if c['id']=='mcc-plastic-isotropic-strain')
    model=checked_receipt(ROOT,'catalogue/investigations/recorded-refinement-v1/manifest.json',
                          'models/modified-cam-clay.json',case['model_sha256'])
    spec=importlib.util.spec_from_file_location('_original_mcc_continuous',ROOT/name)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=model.parents[1]
    return module
def analyze(report):return _original(report).analyze(report)
def analyze_followups(report,followup):return _original(report).analyze_followups(report,followup)
''')
# Resolve only original canonical paths explicitly bound by applicable receipt maps.
def pairs(x):
 if isinstance(x,dict):
  if isinstance(x.get('path'),str)and isinstance(x.get('sha256'),str):yield x['path'],x['sha256']
  for k,v in x.items():
   if isinstance(v,str)and len(v)==64 and all(c in '0123456789abcdef'for c in v):yield k,v
   yield from pairs(v)
 elif isinstance(x,list):
  for v in x:yield from pairs(v)
def find(name,h):
 candidates=[W/'catalogue/source-snapshots'/h/name,R/'catalogue/source-snapshots'/h/name,W/name,R/name,O/'original'/name,
 R/'docs/delivery/unheld-finalisation-20261105-v1/python-explicit-fixtures-fix-v1/original'/name,
 R/'docs/delivery/unheld-finalisation-20261105-v1/experiment-compressed-transport-v1/preimages'/name]
 for p in candidates:
  if p.is_file()and sha(p.read_bytes())==h:return p.read_bytes()
 raise ValueError('No exact archive source '+name+' '+h)
maps=[n for n in gates['preimages']if n.endswith('source-archive-map.json')]+[extra]
audit=[]
for name in maps:
 mapping=json.loads((W/name).read_text()); docs=set(mapping['documents'])
 if name=='tests/fixtures/source-archive-map.json':docs.add('tests/fixtures/historical-test-contexts.json')
 for doc in sorted(docs):
  document=json.loads((W/doc).read_text());mapping['documents'][doc]=sha((W/doc).read_bytes())
  for path,h in sorted(set(pairs(document))):
   if not(path.startswith('models/')or path in old or path in ('tests/test_atlas.py','tests/test_capacity.py','tests/test_history_legacy.py','web/experiments.mjs')):continue
   if not (W/path).is_file():continue
   effective=P/path if(P/path).is_file()else W/path
   if sha(effective.read_bytes())==h and path not in maps:continue
   matches=[e for e in mapping['entries']if e.get('original_path')==path and e.get('sha256')==h]
   b=find(path,h);archive(path,b)
   if not matches:mapping['entries'].append({'original_path':path,'sha256':h,'archived_path':f'catalogue/source-snapshots/{h}/{path}'})
   audit.append({'document':doc,'path':path,'sha256':h,'new_entry':not bool(matches)})
 edit(name,lambda s,m=mapping:js(m))
for name,b in old.items():archive(name,b)
emit(O/'routing-audit.json',js(audit))
delta=[]
for p in sorted(P.rglob('*')):
 if p.is_file():
  n=str(p.relative_to(P));before=(W/n).read_bytes()if(W/n).is_file()else None
  delta.append({'path':n,'preimage_sha256':sha(before)if before is not None else None,'sha256':sha(p.read_bytes()),'size_bytes':p.stat().st_size,'mode':'0644'})
emit(O/'source-delta.json',js({'author_run':'/root/publication_operations_review','changes':[r for r in delta if r['preimage_sha256']!=r['sha256']],'retained_inputs':[r for r in delta if r['preimage_sha256']==r['sha256']]}))
print(js({'status':'source-preparation-complete','targets':len(delta),'routes':len(audit),'current_catalogue':catalogue['sha256']}))
