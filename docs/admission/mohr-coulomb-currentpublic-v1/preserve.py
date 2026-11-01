from pathlib import Path
import hashlib,json,tarfile,io
root=Path('/private/tmp/atlas-mc-admission-public-v1');p=Path('/private/tmp/atlas-mc-admission-evidence-v1');sha=lambda b:hashlib.sha256(b).hexdigest()
(p/'TESTS.json').write_text(json.dumps({'source_change_during_tests':False,'initial':{'argv':['python3','-B','-m','unittest','tests.test_agent_review','tests.test_agent_review_export','tests.test_database_approval_integrity','tests.test_database_package'],'session':3583,'exit_code':1,'tests':34,'passes':33,'errors':1,'error':'Sandbox PermissionError binding loopback HTTP server','log_sha256':sha((p/'metadata-tests.log').read_bytes())},'retry':{'argv':['python3','-B','-m','unittest','tests.test_database_package.DatabasePackage.test_download_links_resolve_under_a_project_path_with_matching_bytes'],'session':9473,'exit_code':0,'tests':1,'passes':1,'log_sha256':sha((p/'metadata-loopback-retry.log').read_bytes())},'result':'All34existing cases resolved; original sandbox failure retained. No full-suite exit0 rerun asserted.'},indent=2)+'\n')
plan=json.loads((p/'INSTALL.json').read_text());files={n:(root/n).read_bytes()for n in plan['new_files']};files['catalogue/approved-models.json']=(root/'catalogue/approved-models.json').read_bytes();assert len(files)==17
sourcepins={n:sha(b)for n,b in files.items()};outputs={f.relative_to(p).as_posix():f.read_bytes()for d in ('before','after')for f in (p/d).rglob('*')if f.is_file()}
for name,members in [('candidate-source.tar.gz',files),('projection-outputs.tar.gz',outputs)]:
 with tarfile.open(p/name,'w:gz')as t:
  for n,data in sorted(members.items()):
   assert not n.endswith(('.pdf','.wasm','.dylib','.so'))
   i=tarfile.TarInfo(n);i.size=len(data);i.mode=0o644;i.mtime=0;t.addfile(i,io.BytesIO(data))
 with tarfile.open(p/name,'r:gz')as t:
  assert set(t.getnames())==set(members)
  for n,data in members.items():assert t.extractfile(n).read()==data
rec={'base':plan['base'],'source_files':sourcepins,'source_archive':{'path':'candidate-source.tar.gz','sha256':sha((p/'candidate-source.tar.gz').read_bytes()),'bytes':(p/'candidate-source.tar.gz').stat().st_size,'files':len(files)},'projection_archive':{'path':'projection-outputs.tar.gz','sha256':sha((p/'projection-outputs.tar.gz').read_bytes()),'bytes':(p/'projection-outputs.tar.gz').stat().st_size,'files':len(outputs)},'private_originals_or_compiled_payloads':0,'scope':'Exact isolated17-file source delta and normal public database/evidence outputs; no full website or execution package.'};(p/'PRESERVATION.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({k:v for k,v in rec.items()if k!='source_files'}))
