import gzip,hashlib,io,json,shutil,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];W=Path('/Users/bmar5496/code/constitutive-atlas');D=Path('docs/ingestion/kelvin-voigt-comsol63');sha=lambda b:hashlib.sha256(b).hexdigest()
for name in ['plan.json','members.json','preservation-plan.tar.gz','artifact.json','audit.py']:
 shutil.copyfile(B/name,B/('candidate-v4-'+name))
with tarfile.open(B/'preservation-plan.tar.gz','r:gz')as t:payload={m.name:t.extractfile(m).read()for m in t.getmembers()}
p=json.loads(payload['plan.json']);inv=json.loads(gzip.decompress(payload['inventory.json.gz']));source='tools/test_kelvin_voigt_package.mjs';old=(W/D/'interface-v5/prior'/source).read_bytes();h=sha(old);assert h=='5b3980b4f543af1293662b238346715d8aa694dbc3287e6834b188c942f4bc00';assert(R/source).read_bytes()==old
archive='catalogue/source-snapshots/'+h+'/'+source;payload['prior-bytes/'+archive]=old;p['canonical_archives'].append({'original_path':source,'sha256':h,'archived_path':archive,'origin_namespace':'isolated','already_present_in_remote':False})
def contains(n):
 if isinstance(n,dict):return n.get(source)==h or(n.get('path')==source and(n.get('sha256')==h or n.get('hash')==h))or any(contains(v)for v in n.values())
 return isinstance(n,list)and any(contains(v)for v in n)
rows=[]
for folder in ['interface-v1','interface-v2','interface-v3','interface-v4','integration-v2','browser-v1','package-v1']:
 for file in (R/D/folder).glob('*.json'):
  if file.name=='source-archive-map.json':continue
  if not contains(json.loads(file.read_text())):continue
  doc=str(file.relative_to(R));row={'document':doc,'document_sha256':sha(file.read_bytes()),'original_path':source,'sha256':h,'locations':[{'pointer':'recursive-source-receipt','shape':'key'}],'namespace':'isolated','resolution':'live','resolved_path':source};rows.append(row)
  name=str(file.parent.relative_to(R)/'source-archive-map.json');key='proposed-sidecars/'+name
  if key in payload:m=json.loads(payload[key])
  else:
   target=R/name;prior=target.read_bytes()if target.exists()else None
   m=json.loads(prior)if prior else{'version':'immutable-source-archive-map-0.1','documents':{str(f.relative_to(R)):sha(f.read_bytes())for f in file.parent.glob('*.json')if f.name!='source-archive-map.json'},'entries':[]}
   p['sidecar_proposals'][name]={'remote_sha256':None,'isolated_premerge_sha256':sha(prior)if prior else None,'merged_remote_and_isolated_maps':False}
  m['documents'][doc]=row['document_sha256'];entry={'original_path':source,'sha256':h,'archived_path':archive}
  if entry not in m['entries']:m['entries'].append(entry)
  data=(json.dumps(m,indent=2)+'\n').encode();payload[key]=data;p['sidecar_proposals'][name].update(proposed_sha256=sha(data),documents=len(m['documents']),entries=len(m['entries']))
p['required_additive_edges']+=rows;inv['own_rows']+=rows;p['own_mutable_prior_sources'][source]=h;p['current_v4_files'][source]=sha((W/source).read_bytes());p['identity']='kelvin-origin-rebase-v4-v5-binding-plan-v4';p['summary']['own_source_edges']+=len(rows);p['summary']['proposed_maps']=len(p['sidecar_proposals']);p['summary']['prior_byte_snapshots']=len(p['canonical_archives']);p['v5_fixture_only_extension']={'new_sha256':p['current_v4_files'][source],'preserved_receipts':len(rows)}
payload['plan.json']=(json.dumps(p,indent=2)+'\n').encode();payload['inventory.json.gz']=gzip.compress(json.dumps(inv,indent=2).encode(),mtime=0)
(B/'plan.json').write_bytes(payload['plan.json']);(B/'members.json').write_text(json.dumps({k:sha(v)for k,v in sorted(payload.items())},indent=2)+'\n')
with(B/'preservation-plan.tar.gz').open('wb')as f:
 with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='')as gz:
  with tarfile.open(fileobj=gz,mode='w')as t:
   for name,data in sorted(payload.items()):
    info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;t.addfile(info,io.BytesIO(data))
(B/'artifact.json').write_text(json.dumps({'archive':'preservation-plan.tar.gz','archive_sha256':sha((B/'preservation-plan.tar.gz').read_bytes()),'members_sha256':sha((B/'members.json').read_bytes()),'plan_sha256':sha(payload['plan.json'])},indent=2)+'\n')
shutil.copyfile(W/source,R/source);shutil.copytree(W/D/'interface-v5',R/D/'interface-v5',dirs_exist_ok=True)
print(p['summary']);print('V5 additional rows',len(rows))
