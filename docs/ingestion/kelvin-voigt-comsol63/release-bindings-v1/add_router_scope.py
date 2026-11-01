import gzip
"""Add exact routing fixture edge inventory; publications has no planned mutation."""
import collections,hashlib,json,subprocess
from pathlib import Path
import scan
B=Path(__file__).resolve().parent;T=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source');x=json.loads((B/'inventory.json').read_text() if (B/'inventory.json').exists() else gzip.decompress((B/'inventory.json.gz').read_bytes()));commit=x['summary']['baseline'];target='tests/test_j2_main_routing.mjs';scan.TARGETS=[target];objs={l.split('\t',1)[1]:l.split()[2]for l in subprocess.check_output(['git','ls-tree','-r',commit],text=True).splitlines()};cache={}
def data(n):
 if n not in cache:
  b=(T/n).read_bytes()if(T/n).is_file()else b''
  if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=objs.get(n):b=subprocess.check_output(['git','show',commit+':'+n])
  cache[n]=b
 return cache[n]
sha=lambda b:hashlib.sha256(b).hexdigest();h=sha(data(target));paths=subprocess.check_output(['rg','-l','--glob','*.json','"tests/test_j2_main_routing\\.mjs"',str(T/'docs'),str(T/'catalogue')],text=True).splitlines();rows=[]
for name in sorted(str(Path(p).relative_to(T))for p in paths):
 if name not in objs or any(q in Path(name).parts for q in ['source-snapshots','frozen-sources']):continue
 b=data(name);n=json.loads(b);group=collections.defaultdict(list)
 for path,pin,loc,shape in scan.pairs(n):
  if path!=target or name.endswith('/source-archive-map.json'):continue
  group[(path,pin)].append({'pointer':'/'+'/'.join(str(v)for v in loc),'shape':shape})
 for(path,pin),locations in group.items():
  row=dict(document=name,document_sha256=sha(b),original_path=path,sha256=pin,locations=locations,expected_equals_baseline=pin==h);chosen=path;side=str(Path(name).parent/'source-archive-map.json')
  try:
   if all(z['shape']=='original_path'for z in locations):
    archive='catalogue/source-snapshots/'+pin+'/'+path
    if archive in objs and sha(data(archive))==pin:chosen=archive
   elif side in objs:
    m=json.loads(data(side));assert m['documents'].get(name)==sha(b),'document missing/changed in sibling sidecar';matches=[r for r in m['entries']if r.get('original_path')==path and r.get('sha256')==pin];assert len(matches)<=1
    if matches:chosen=matches[0]['archived_path'];assert chosen=='catalogue/source-snapshots/'+pin+'/'+path
   assert sha(data(chosen))==pin,'selected source hash mismatch';row.update(resolution=('live-sidecar-entry'if all(z['shape']=='original_path'for z in locations)else'live')if chosen==path else('archived-sidecar-entry'if all(z['shape']=='original_path'for z in locations)else'archived'),resolved_path=chosen)
  except Exception as e:row.update(resolution='unresolved',error=str(e))
  rows.append(row)
x['baseline_source_pins'][target]=h;x['unchanged_source_pins']={'catalogue/publications.json':x['baseline_source_pins'].pop('catalogue/publications.json')};x['primary_edges']=[r for r in x['primary_edges']if r['original_path']!='catalogue/publications.json']+rows;x['scope_revision']='v2: publications unchanged; include exact routing factory-list fixture';(B/'inventory-scope-v2.json').write_text(json.dumps(x,indent=2)+'\n');print('Routing',len(rows),'pairs',dict(collections.Counter(r['resolution']for r in rows)),h)
