"""Pure source/receipt/database checks in owned sparse temporary context."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,tempfile,shutil,importlib.util,sqlite3,ast
P=Path(__file__).resolve().parent;BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source');OUT=P/'proposed'
def sha(b):return hashlib.sha256(b).hexdigest()
def data(p):return (OUT/p).read_bytes() if (OUT/p).is_file() else (BASE/p).read_bytes()
checks=[]
def ok(name,condition):
 assert condition,name
 checks.append(name)
for path,expected in json.loads((P/'base-pins.json').read_text()).items():
 ok('base guard '+path,sha((BASE/path).read_bytes())==expected)
rows=json.loads((P/'source-delta.json').read_text())['files']
for row in rows:
 p=row['path'];old=(BASE/p).read_bytes() if (BASE/p).is_file() else None
 ok('preimage '+p,(sha(old) if old is not None else None)==row['preimage_sha256'])
 if old is not None:ok('preimage mode '+p,((BASE/p).stat().st_mode & 0o111)==0 and row['preimage_mode']=='100644')
 ok('payload '+p,sha(data(p))==row['sha256'] and len(data(p))==row['bytes'])
 if old is not None:ok('archive '+p,data(f'catalogue/source-snapshots/{sha(old)}/{p}')==old)
old=json.loads((BASE/'catalogue/approved-models.json').read_text())['models'];new=json.loads(data('catalogue/approved-models.json'))['models']
ids={'linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97'}
ok('other25 ordered exact',[a for a in new if a['model_id'] not in ids]==[a for a in old if a['model_id'] not in ids] and len(new)==30)
history=json.loads(data('catalogue/approval-history/baseline-five-supersession-20261105-v1.json'))
ok('exact legacy registry retained',data(history['historical_registry']['path'])==(BASE/'catalogue/approved-models.json').read_bytes() and len(history['supersessions'])==5)
for p in ['atlas/research.py','web/app.js','web/model-profile-data.mjs','catalogue/laboratory-examples.json','catalogue/laboratory-control-support.json','.github/workflows/pages.yml','.github/workflows/verify.yml']:
 ok('preserved '+p,data(p)==(BASE/p).read_bytes())
a=json.loads((BASE/'catalogue/laboratory-package-policy.json').read_text());b=json.loads(data('catalogue/laboratory-package-policy.json'));a.pop('id');b.pop('id')
for mid in ['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']:
 a['models'][mid]=sha(data('models/'+mid+'.json'))
ok('all package gates unchanged',a==b)
a=json.loads((BASE/'catalogue/laboratory-profile-policy.json').read_text());b=json.loads(data('catalogue/laboratory-profile-policy.json'));a.pop('id');b.pop('id');a['supported_policy']['sha256']=sha(data('catalogue/laboratory-package-policy.json'));ok('all43 profile gates unchanged',a==b)
# Strict sparse view copies only files used by normal source validators; no symlinks/no binaries.
with tempfile.TemporaryDirectory(prefix='source-check-',dir=P) as tmp:
 root=Path(tmp)
 def cp(p):
  t=root/p
  if t.is_file():return
  t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(data(p))
 for directory in ['schemas','models','atlas']:
  for f in (BASE/directory).rglob('*'):
   if f.is_file() and f.suffix in {'.py','.json'}:cp(f.relative_to(BASE).as_posix())
 for p in ['catalogue/approved-models.json','catalogue/manifest.json','catalogue/publications.json','catalogue/screening.jsonl','catalogue/source-archive-map.json']:cp(p)
 reviewpaths={p.relative_to(BASE).as_posix() for p in (BASE/'catalogue/agent-reviews').glob('*.json')}|{r['path'] for r in rows if r['path'].startswith('catalogue/agent-reviews/')}
 for doc in sorted(reviewpaths):
  cp(doc)
  if doc.endswith('/source-archive-map.json'):continue
  rec=json.loads(data(doc));m=json.loads(data('catalogue/agent-reviews/source-archive-map.json'))
  for pin in [rec['model']]+rec['artifacts']:
   name,expected=pin['path'],pin['sha256'];cp(name)
   matches=[e for e in m['entries'] if e['original_path']==name and e['sha256']==expected]
   for entry in matches:cp(entry['archived_path'])
 m=json.loads(data('catalogue/source-archive-map.json'))
 for a in new:
  for entry in m['entries']:
   if entry['original_path']==a['definition']['path'] and entry['sha256']==a['definition']['sha256']:cp(entry['archived_path'])
 # Normal publication/screening validators inspect only their direct evidence pins.
 def references(x):
  if isinstance(x,dict):
   if isinstance(x.get('path'),str) and ('sha256' in x or 'hash' in x):
    if (BASE/x['path']).is_file() or (OUT/x['path']).is_file():cp(x['path'])
   for v in x.values():references(v)
  elif isinstance(x,list):
   for v in x:references(v)
 references(json.loads(data('catalogue/publications.json')))
 for line in data('catalogue/screening.jsonl').decode().splitlines():
  if line.strip():references(json.loads(line))
 sys.path.insert(0,str(root))
 from atlas import model,research,review_export
 defs,approvals=research.approved_definitions()
 ok('30 active approvals; current five definitions',len(approvals)==30 and all(defs[mid]==model.load(root/f'models/{mid}.json') for mid in ['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']))
 projected,originals,omitted=review_export.collect(root,{r['id'] for r in json.loads(data('catalogue/manifest.json'))['models']})
 ok('normal review projection no omissions',not omitted)
 oldfive=[r for r in projected if r['catalogue_id'] in ids and not r['definition_current']]
 ok('five exact historical reviews remain accepted unregistered',len(oldfive)==5 and all(r['status']=='accepted' and r['registered_approval_id'] is None for r in oldfive))
 dest=research.export_database(root/'metadata.sqlite')
 with sqlite3.connect(dest) as db:counts={table:db.execute('select count(*) from '+table).fetchone()[0] for table in ['models','sources','model_approvals','agent_reviews']}
 ok('normal database30 active approvals',counts['model_approvals']==30)
 # Archive corruption/missing, unapproved currentbytes and duplicated approvals fail closed.
 registry=root/'catalogue/approved-models.json';raw=registry.read_bytes();mapping=root/'catalogue/source-archive-map.json';mapraw=mapping.read_bytes()
 first=new[1] # choose any legacy five entry by path
 first=next(a for a in old if a['model_id']=='linear-elastic')
 archive=root/f"catalogue/source-snapshots/{first['definition']['sha256']}/{first['definition']['path']}";araw=archive.read_bytes()
 for label,mutate,restore in [('corrupt archive',lambda:archive.write_bytes(b'bad'),lambda:archive.write_bytes(araw)),('missing archive',lambda:archive.unlink(),lambda:archive.write_bytes(araw)),('duplicate approval',lambda:registry.write_text(json.dumps({'models':new+[new[-1]]})),lambda:registry.write_bytes(raw))]:
  mutate()
  try:
   (research.approved_definitions() if label=='duplicate approval' else review_export.collect(root,{r['id'] for r in json.loads(data('catalogue/manifest.json'))['models']}));raise AssertionError('accepted '+label)
  except (ValueError,OSError):checks.append('reject '+label)
  finally:restore()
 # Current bytes without an exact approval must never inherit historical approval.
 live=root/'models/linear-elastic.json';live_raw=live.read_bytes();obj=json.loads(live_raw);obj['name']+=' (unapproved edit)';live.write_text(json.dumps(obj))
 try:
  research.approved_definitions();raise AssertionError('changed current bytes accepted')
 except ValueError:checks.append('reject changed current bytes despite historical approval')
 finally:live.write_bytes(live_raw)
 # Matching review bytes cannot certify an altered approval scope/independence record.
 reg=json.loads(raw);reg['models'][-1]['scope']='forged scope';registry.write_text(json.dumps(reg))
 try:
  review_export.collect(root,{r['id'] for r in json.loads(data('catalogue/manifest.json'))['models']});raise AssertionError('forged scope accepted')
 except ValueError:checks.append('reject forged registered review scope')
 finally:registry.write_bytes(raw)
 # Every source function outside the explicitly scoped pair is AST identical.
 bt=ast.parse((BASE/'atlas/research.py').read_text());nt=ast.parse(data('atlas/research.py').decode())
 bf={n.name:ast.dump(n) for n in bt.body if isinstance(n,ast.FunctionDef)};nf={n.name:ast.dump(n) for n in nt.body if isinstance(n,ast.FunctionDef)}
 ok('all current research functions unchanged',bf==nf)
 summary={'status':'PASS','checks':len(checks),'counts':counts,'review_rows':len(projected),'originals':len(originals),'omissions':omitted,'checks_passed':checks,'temporary_context_removed_on_exit':True}
(P/'checks.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='checks_passed'},indent=2))
