"""Exact preimage/source archival and additive document-bound map closure."""
from pathlib import Path
import json,gzip,hashlib,sys
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def archive(path,blob):
 h=sha(blob);name='catalogue/source-snapshots/'+h+'/'+path;target=R/name
 if target.exists():assert target.read_bytes()==blob
 else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
 return {'original_path':path,'sha256':h,'archived_path':name}
def prepare():
 raw=json.loads((P/'raw-inventory-retention-v1.json').read_text());blob=Path(raw['retained_private_path']).read_bytes();assert sha(blob)==raw['sha256'];data=json.loads(gzip.decompress(blob));maps={};old={};bindings={};skipped=[]
 source={n:(P/'preimages'/n).read_bytes() for n in ['tests/test_catalogue.py','tests/test_controlled_time.py']}
 for n in ['atlas/initialization.py','atlas/cli.py']:source[n]=(R/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/preimages/base-31125e2e8'/n).read_bytes()
 for n,b in source.items():archive(n,b)
 def add(document,path,h):
  dp=R/document;docsha=sha(dp.read_bytes());side=str(Path(document).parent/'source-archive-map.json')
  if side not in maps:
   target=R/side;old[side]=target.read_bytes() if target.exists() else None
   if old[side] is None:
    maps[side]={'version':'immutable-source-archive-map-0.1','documents':{str(x.relative_to(R)):sha(x.read_bytes()) for x in target.parent.glob('*.json')},'entries':[]}
   else:
    archive(side,old[side]);maps[side]=json.loads(old[side]);assert maps[side]['version']=='immutable-source-archive-map-0.1'
  mapping=maps[side];assert mapping['documents'].get(document,docsha)==docsha;mapping['documents'][document]=docsha
  b=source[path] if path in source else old[path];assert b is not None and sha(b)==h
  entry=archive(path,b);matches=[e for e in mapping['entries'] if e['original_path']==path and e['sha256']==h];assert not matches or matches==[entry]
  if not matches:mapping['entries'].append(entry)
  bindings[(document,path,h)]={'document':document,'document_sha256':docsha,**entry}
 rows=[r for r in data['primary_references'] if r['original_path'].startswith('tests/') and r['expected_equals_current_live'] and r['resolution']!='unresolved']
 repairs=[r for r in data['primary_references'] if r['document'] in ['catalogue/investigations/tresca-certified-corners-v5/source-pins.json','catalogue/investigations/tresca-solution-constraints-v4/source-pins.json','catalogue/investigations/tresca-mixed-catalogue-v1/source-pins.json'] and r['original_path'] in source and r['resolution']=='unresolved']
 assert len(rows)==49 and len(repairs)==4
 for row in rows+repairs:add(row['document'],row['original_path'],row['sha256'])
 # Prior-map reverse consumers must retain exact old map bytes. Secondary map
 # entries already use canonical snapshots; preserve those snapshots directly.
 changed=True
 while changed:
  changed=False
  for row in data['secondary_source_map_references']:
   path=row['original_path'];document=row['document'];h=row['sha256'];key=(document,path,h)
   if not any(x['shape'] in ('direct-map','path-object') for x in row['locations']):continue
   if path not in maps or document.endswith('/source-archive-map.json') or old[path] is None or sha(old[path])!=h or key in bindings:continue
   side=R/Path(document).parent/'source-archive-map.json'
   if side.exists():
    m=json.loads(side.read_text());docsha=sha((R/document).read_bytes())
    if m['documents'].get(document)!=docsha:skipped.append({'document':document,'path':path,'reason':'preexisting document identity mismatch'});continue
    matches=[e for e in m['entries'] if e['original_path']==path and e['sha256']==h]
    if matches:
     if len(matches)!=1 or sha((R/matches[0]['archived_path']).read_bytes())!=h:raise ValueError('Corrupt preexisting archive')
     continue # Already resolves archived exact old map; no change needed.
   add(document,path,h);changed=True
 for side in maps:
  if old[side] is not None:archive(side,old[side])
 payload={'kind':'exact-full-python-preservation-plan-v1','bindings':list(bindings.values()),'maps':[{'path':n,'before_sha256':sha(old[n]) if old[n] is not None else None,'before_archive':'catalogue/source-snapshots/'+sha(old[n])+'/'+n if old[n] is not None else None,'after':m} for n,m in maps.items()],'initial_tests':rows,'tresca_repairs':repairs,'preexisting_unresolved_summary':{'primary':sum(r['resolution']=='unresolved' for r in data['primary_references']),'skipped_map_consumers':skipped}}
 (P/'preservation-plan-v2.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps({'bindings':len(bindings),'maps':len(maps),'old_maps':sum(v is not None for v in old.values()),'skipped_consumers':len(skipped)}))
def apply():
 d=json.loads((P/'preservation-plan-v2.json').read_text())
 for row in d['maps']:
  path=R/row['path'];assert sha(path.read_bytes())==row['before_sha256'] if row['before_sha256'] else not path.exists()
 for row in d['bindings']:assert sha((R/row['document']).read_bytes())==row['document_sha256']
 for row in d['maps']:(R/row['path']).write_text(json.dumps(row['after'],indent=2)+'\n')
 # Resolve every genuine document binding through the production fail-closed API.
 sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
 for row in d['bindings']:assert checked_receipt(R,row['document'],row['original_path'],row['sha256'])==R/row['archived_path']
 (P/'preservation-applied-v2.json').write_text(json.dumps({'bindings':len(d['bindings']),'maps':len(d['maps']),'original_documents_unchanged':True,'all_production_resolvers_pass':True},indent=2)+'\n')
if __name__=='__main__':
 if sys.argv[1:] == ['prepare']:prepare()
 elif sys.argv[1:] == ['apply']:apply()
 else:raise ValueError('Explicit prepare/apply required')
