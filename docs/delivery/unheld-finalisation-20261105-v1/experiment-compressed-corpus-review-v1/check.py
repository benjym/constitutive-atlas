from pathlib import Path
import gzip,hashlib,json,tarfile
O=Path(__file__).resolve().parent;N=O.parent;ROOT=N.parents[2];P=N/'experiment-compressed-transport-actual-v1';R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');S=R.parent/'site-compressed-v1';sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((P/'plan.json').read_bytes())=='f6f96c47124d89c5a6075b9b052edc04ff9e35c14b1f61b01dc995924334a4b0';assert sha((N/'experiment-compressed-transport-review-v1/decision.json').read_bytes())=='393aa0381ca96210b61c02cebf91ef1f08cc7d2df79357efc5599a33674d78e9'
oldinv={x['path']:x for x in json.loads((N/'package-inventory-v1.json').read_text())['files']};inventory=json.loads((P/'inventory.json').read_text());newinv={x['path']:x for x in inventory['files']};assert len(newinv)==len(inventory['files'])==1549
assert set(newinv)=={p.relative_to(S).as_posix() for p in S.rglob('*') if p.is_file()}
for name,pin in newinv.items():
 f=S/name;assert not f.is_symlink() and f.stat().st_size==pin['bytes'] and sha(f.read_bytes())==pin['sha256'],name
manifest=json.loads((S/'experiments/index.json').read_text());entries={x['path']:x for x in manifest['experiments']};assert len(entries)==len(manifest['experiments'])==994
report=json.loads((P/'report.json').read_text());reported={x['id']:x for x in report['records']};checked=set();oldmembers=set();logical=0;transport=0;oldmanifest=None
with tarfile.open(ROOT/'.local/retained-evidence/baseline-five-local-site-20261105-v1.tar.gz','r|gz') as archive:
 for member in archive:
  if not member.isfile():continue
  assert member.name in oldinv and member.name not in oldmembers;oldmembers.add(member.name)
  content=archive.extractfile(member).read();assert len(content)==oldinv[member.name]['bytes'] and sha(content)==oldinv[member.name]['sha256']
  if member.name=='experiments/index.json':oldmanifest=json.loads(content);continue
  if not member.name.startswith('experiments/'):continue
  key=member.name.removeprefix('experiments/');entry=entries[key];assert key==entry['id']+'.json' and entry['content_encoding']=='gzip';t=entry['transport'];assert set(t)=={'path','sha256','size_bytes'} and t['path']==key+'.gz'
  zipped=(S/'experiments'/t['path']).read_bytes();assert len(zipped)==t['size_bytes'] and sha(zipped)==t['sha256'];assert zipped[:3]==b'\x1f\x8b\x08' and zipped[3]==0 and zipped[4:8]==bytes(4) and zipped[9]==255
  raw=gzip.decompress(zipped);assert raw==content and len(raw)==entry['size_bytes'] and sha(raw)==entry['sha256'];assert 0<len(raw)<=32*1024*1024 and 0<len(zipped)<=32*1024*1024
  assert reported[entry['id']]=={'id':entry['id'],'rows':entry['rows'],'logical_bytes':len(raw),'logical_sha256':sha(raw),'transport_bytes':len(zipped),'transport_sha256':sha(zipped)}
  logical+=len(raw);transport+=len(zipped);checked.add(key)
assert oldmembers==set(oldinv) and len(checked)==994
logicalmanifest=dict(manifest,experiments=[{k:v for k,v in x.items() if k not in ['content_encoding','transport']} for x in manifest['experiments']]);assert logicalmanifest==oldmanifest
other=[name for name in oldinv if not name.startswith('experiments/') and name!='experiments.mjs'];assert len(other)==553
for name in other:assert newinv[name]==oldinv[name],name
assert {x for x in newinv if x.startswith('experiments/')}=={'experiments/index.json',*['experiments/'+x['transport']['path'] for x in entries.values()]}
assert sha((S/'experiments.mjs').read_bytes())==sha((R/'web/experiments.mjs').read_bytes())=='d3615cb2041be9ef969de636a7cc6f1b0ba8b0c3b9d8b91b6efb4d682b207dbf'
assert logical==report['logical_bytes']==1082424236 and transport==report['transport_bytes']==232611386
assert sum(x['bytes'] for x in newinv.values())==report['package_bytes']==260275679
freeze=json.loads((N/'current16-qualification-plan-v1/source-freeze-v1.json').read_text());changed={}
for x in freeze['inputs']:
 p=Path(x['path']);actual=sha(p.read_bytes())
 if actual!=x['sha256']:changed[p.relative_to(R).as_posix()]=actual
expected={'tools/build_experiments.py':'ac4a43fb38f9282db5972084cd911b1bef6125bb9b37ac0a070f944b26bb61b4','tools/test_experiments.mjs':'31f380d1668fdbd04a4e9ba9542b463d58bf30322e688a5f5ae34f70226b6906','tools/test_numerics.mjs':'8381f20d6523b28698bb0f951bbbf211161e1cf292091c1b96fb0841d057b146','tools/test_recorded.mjs':'64ce5390fedda14aaff03a44ee6794ced587be4359e7ae6b4fb92457eec0a459'};assert changed==expected
controlled=json.loads((R/'docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/plan-v1.json').read_text())
for name,pin in controlled['source_closure'].items():assert sha((R/name).read_bytes())==pin
assert (P/'attempt-1-receipt.json').is_file() and json.loads((P/'failure.json').read_text())=={'type':'KeyError','message':"'decision'"}
result={'status':'PASS','original_archive_members_verified':len(oldmembers),'new_package_members_verified':1549,'experiment_count':994,'all_original_decoded_bytes_exact':True,'all_nontransport_metadata_exact':True,'logical_bytes':logical,'transport_bytes':transport,'package_bytes':260275679,'unchanged_nonmeasurement_assets':553,'ordinary_runtime_model_review_catalogue_assets_unchanged':True,'all250_controlled_source_hashes_exact':True,'only_broad_source_delta':changed,'compiled_material_browser_network_git_calls':0}
(O/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
