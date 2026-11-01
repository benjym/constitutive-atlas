"""Independent future metadata overlay; writes exclusively inside this review directory."""
from pathlib import Path
import hashlib,json,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
A='docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
P=ROOT/A/'shared-hook-install-v1/revision-v2'
sha=lambda data:hashlib.sha256(data).hexdigest()
load=lambda path:json.loads(Path(path).read_bytes())
pins={}
def read(name):
    name=str(name);data=(ROOT/name).read_bytes();pins[name]=sha(data);return data
def outcome(root,doc,name,digest):
    try:checked_receipt(root,doc,name,digest);return 'passed'
    except Exception as error:return str(error)
def pairs(node):
    result=set()
    valid=lambda x:isinstance(x,str) and len(x)==64 and all(c in '0123456789abcdef' for c in x)
    if isinstance(node,dict):
        for key,value in node.items():
            if valid(value):result.add((key,value))
            result.update(pairs(value))
        if isinstance(node.get('path'),str):
            for key in ['sha256','hash']:
                if valid(node.get(key)):result.add((node['path'],node[key]))
    elif isinstance(node,list):
        for value in node:result.update(pairs(value))
    return result

expected={'PLAN.json':'f63da59685f40e26bf31e744ec59690e97272ef75b85bbf6987f7d37d0394dab','APPLY_WHITELIST.json':'185bf2446833a99d1ea51760b9a610890a8bd012d014bbeb00aa6d2c1670985e','SOURCE_FREEZE.json':'686e45bd7e046ba86035a5493dd35cea308e334193036b223c06bc186202ea28'}
for name,digest in expected.items():assert sha(read((P/name).relative_to(ROOT)))==digest
plan=load(P/'PLAN.json');whitelist=load(P/'APPLY_WHITELIST.json');freeze=load(P/'SOURCE_FREEZE.json');saved=load(P/'CHECK_RESULTS.json')
assert plan['passed'] and not plan['issues'] and not plan['failed']
for row in freeze['files']:assert sha(read(row['original_path']))==row['old_sha256']
assert len(plan['maps'])==31 and len(plan['archives'])==33 and len(whitelist['writes'])==63
assert len(whitelist['future_source_installs'])==7
expected_writes={}
oldmap_preserved=0
for row in plan['maps']:
    name=row['original_path'];old=read(name) if (ROOT/name).exists() else None
    assert (sha(old) if old is not None else None)==row['old_sha256']
    candidate=read((P/row['candidate']).relative_to(ROOT));assert sha(candidate)==row['new_sha256']
    mapping=json.loads(candidate)
    assert mapping['version']=='immutable-source-archive-map-0.1'
    assert len({(e['original_path'],e['sha256']) for e in mapping['entries']})==len(mapping['entries'])
    for entry in mapping['entries']:
        assert entry['archived_path']==f"catalogue/source-snapshots/{entry['sha256']}/{entry['original_path']}"
    if old is not None:
        prior=json.loads(old)
        assert all(mapping['documents'].get(k)==v for k,v in prior['documents'].items())
        assert all(e in mapping['entries'] for e in prior['entries'])
        assert any(r['original_path']==name and r['old_sha256']==sha(old) for r in plan['archives'])
        oldmap_preserved+=1
    expected_writes[name]=(row['old_sha256'],row['new_sha256'])
for row in plan['archives']:
    name=row['canonical_archive'];data=read((P/row['snapshot']).relative_to(ROOT))
    assert sha(data)==row['old_sha256']
    assert name==f"catalogue/source-snapshots/{row['old_sha256']}/{row['original_path']}"
    if row['already_present']:assert read(name)==data
    else:
        assert not (ROOT/name).exists()
        expected_writes[name]=(None,row['old_sha256'])
assert {r['original_path']:(r['old_sha256'],r['new_sha256']) for r in whitelist['writes']}==expected_writes

# Independently find transitive consumers of every archived pair. Exclude mutable
# sidecar metadata as receipt identities, but scan all actual immutable consumers.
seedpairs={(r['original_path'],r['old_sha256']) for r in plan['archives']}
obligations={(r['document'],r['original_path'],r['old_sha256']) for r in plan['simulated']}
coverage_missing=[];scan=0;unreadable=[]
exclude=(A+'shared-hook-install-v1/',A+'profile-install-v1/',str(HERE.relative_to(ROOT))+'/')
for directory in ['docs','catalogue']:
    for path in (ROOT/directory).rglob('*.json'):
        name=path.relative_to(ROOT).as_posix()
        if name.startswith(exclude) or name.startswith('catalogue/source-snapshots/') or path.name=='source-archive-map.json':continue
        data=path.read_bytes()
        try:node=json.loads(data)
        except (ValueError,UnicodeDecodeError):
            if any(p.encode() in data and h.encode() in data for p,h in seedpairs):unreadable.append(name)
            continue
        scan+=1
        for original,digest in pairs(node)&seedpairs:
            if (name,original,digest) not in obligations:coverage_missing.append((name,original,digest))
assert not unreadable,unreadable

checks=saved['checks'];results=[]
with tempfile.TemporaryDirectory(dir=HERE,prefix='overlay-') as temp:
    overlay=Path(temp)
    def put(name,data):
        path=overlay/name
        if path.exists():assert path.read_bytes()==data,name
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    for row in plan['maps']:put(row['original_path'],read((P/row['candidate']).relative_to(ROOT)))
    for row in plan['archives']:put(row['canonical_archive'],read((P/row['snapshot']).relative_to(ROOT)))
    replacements={row['original_path'] for row in plan['replacements']}
    for row in plan['replacements']:
        assert sha(read(row['original_path']))==row['old_sha256']
        if row['future_copy']:
            data=read(row['future_copy']);assert sha(data)==row['new_sha256'];put(row['original_path'],data)
    loaded_sidecars=set()
    for row in checks:
        doc,name,digest=row['document'],row['original_path'],row['old_sha256']
        if not (overlay/doc).exists():put(doc,read(doc))
        sidecar=str(Path(doc).parent/'source-archive-map.json')
        if sidecar not in loaded_sidecars:
            if not (overlay/sidecar).exists() and (ROOT/sidecar).is_file():put(sidecar,read(sidecar))
            if (overlay/sidecar).exists():
                for entry in load(overlay/sidecar)['entries']:
                    archive=entry['archived_path']
                    if not (overlay/archive).exists() and (ROOT/archive).is_file():put(archive,read(archive))
            loaded_sidecars.add(sidecar)
        if name not in replacements and not (overlay/name).exists() and (ROOT/name).is_file():put(name,read(name))
        before=outcome(ROOT,doc,name,digest);after=outcome(overlay,doc,name,digest)
        if before=='passed':assert after=='passed',(doc,name,before,after)
        if row['outcome']=='passed':assert after=='passed',(doc,name,after)
        else:
            assert before!='passed' and after!='passed',(doc,name,before,after)
            # Failure cases retain target bytes, either live or immutable old archive.
            if name in replacements or name in expected_writes:
                live=read(name);assert (overlay/f'catalogue/source-snapshots/{sha(live)}/{name}').read_bytes()==live
            else:assert (overlay/name).read_bytes()==read(name)
        results.append(dict(document=doc,original_path=name,old_sha256=digest,before=before,after=after))
for name,digest in pins.items():assert sha((ROOT/name).read_bytes())==digest,'Concurrent drift: '+name
output=dict(status='blocked' if coverage_missing else 'passed',scope='preservation metadata only; no source installation or artifact execution',frozen_files=len(freeze['files']),maps=31,old_maps_preserved=oldmap_preserved,canonical_archives=33,new_archive_writes=32,whitelist_writes=63,independent_consumer_scan=scan,missing_affected_consumers=coverage_missing,total_checks=len(results),passing_after=sum(r['after']=='passed' for r in results),preexisting_failures=[r for r in results if r['after']!='passed'])
(HERE/'check-results.json').write_text(json.dumps(output,indent=2)+'\n')
(HERE/'checked-pins.json').write_text(json.dumps(dict(files=pins),indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k!='preexisting_failures'},indent=2))
