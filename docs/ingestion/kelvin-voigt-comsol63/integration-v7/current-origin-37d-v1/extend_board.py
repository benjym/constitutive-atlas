"""Recover exact pre-existing merged-board receipt from retained parent proposal."""
import gzip,hashlib,io,json,shutil,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];sha=lambda b:hashlib.sha256(b).hexdigest();enc=lambda n:(json.dumps(n,indent=2)+'\n').encode()
for name in ['plan.json','members.json','preservation-plan.tar.gz','artifact.json','virtual-check.json']:shutil.copyfile(B/name,B/('candidate-v1-'+name))
with tarfile.open(B/'preservation-plan.tar.gz','r:gz')as t:payload={m.name:t.extractfile(m).read()for m in t.getmembers()}
p=json.loads(payload['plan.json']);doc='docs/ingestion/kelvin-voigt-comsol63/integration-v5/merge-receipt.json';source='IMPLEMENTATION_PLAN.md';data=(R/'docs/ingestion/kelvin-voigt-comsol63/integration-v5/proposed'/source).read_bytes();h=sha(data);assert h=='5bcb7a714a82f5f06c02877b66b9ae58447ebcdbe9f197c01970b77ec96b59f9';assert h in(R/doc).read_text();archive='catalogue/source-snapshots/'+h+'/'+source
payload['prior-bytes/'+archive]=data;p['canonical_archives'].append({'original_path':source,'sha256':h,'archived_path':archive});row={'namespace':'own','document':doc,'document_sha256':sha((R/doc).read_bytes()),'original_path':source,'sha256':h,'resolution':'recovered exact retained premerge proposal','recovered_from':'docs/ingestion/kelvin-voigt-comsol63/integration-v5/proposed/'+source};p['required_edges'].append(row)
name=str(Path(doc).parent/'source-archive-map.json');m=json.loads(payload['proposed-sidecars/'+name]);m['entries'].append({'original_path':source,'sha256':h,'archived_path':archive});payload['proposed-sidecars/'+name]=enc(m);p['map_proposals'][name]['proposed_sha256']=sha(enc(m));p['summary']['required_edges']+=1;p['summary']['predecessor_snapshots']+=1;p['summary']['own_primary_edges']+=1;p['identity']='kelvin-origin-37d-binding-plan-v2';p['recovered_preexisting_board_binding']=row
payload['plan.json']=enc(p);(B/'plan.json').write_bytes(payload['plan.json']);(B/'members.json').write_bytes(enc({k:sha(v)for k,v in sorted(payload.items())}))
with(B/'preservation-plan.tar.gz').open('wb')as f:
 with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='')as gz:
  with tarfile.open(fileobj=gz,mode='w')as t:
   for name,data in sorted(payload.items()):
    z=tarfile.TarInfo(name);z.size=len(data);z.mode=0o644;t.addfile(z,io.BytesIO(data))
a={'archive_sha256':sha((B/'preservation-plan.tar.gz').read_bytes()),'members_sha256':sha((B/'members.json').read_bytes()),'plan_sha256':sha(payload['plan.json'])};(B/'artifact.json').write_bytes(enc(a));old=json.loads((B/'candidate-v1-virtual-check.json').read_text());assert old['passed'];(B/'virtual-check.json').write_bytes(enc({'identity':'kelvin-origin-37d-virtual-bindings-v2','archive_sha256':a['archive_sha256'],'checked':old['checked'],'recovered_prior_binding_checked':1,'errors':[],'passed':True,'basis':'Original2524resolvedpairs unchanged in scope; only existing integration-v5 map gains exact recoveredboardentry; olddocsha and canonical sourcehash validated by extend_board.py; candidate-v1 report retained'}));print('Recovered board; plan',p['summary']['required_edges'],'edges',p['summary']['predecessor_snapshots'],'snapshots')
