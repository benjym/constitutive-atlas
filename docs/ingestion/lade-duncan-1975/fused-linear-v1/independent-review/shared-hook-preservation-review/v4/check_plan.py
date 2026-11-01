"""Current-state, additive union, allowed-write and consumer coverage proof only."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
sys.path.insert(0,str(HERE))
from check_composition import pairs
A='docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
P=ROOT/A/'shared-hook-install-v1/revision-v4'
PREV=P.parent/'revision-v3'
sha=lambda data:hashlib.sha256(data).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())

def main():
    plan=load(P/'PLAN.json');previous=load(PREV/'PLAN.json');whitelist=load(P/'APPLY_WHITELIST.json')
    assert plan['passed'] and not plan['issues'] and not plan['failed']
    assert plan['replacements']==previous['replacements'] and len(plan['replacements'])==11
    for row in plan['replacements']:
        assert sha((ROOT/row['original_path']).read_bytes())==row['old_sha256']
        assert sha((ROOT/row['future_copy']).read_bytes())==row['new_sha256']
    provisional='--provisional' in sys.argv
    for row in ([] if provisional else load(P/'SOURCE_FREEZE.json')['files']):
        assert sha((ROOT/row['original_path']).read_bytes())==row['old_sha256'],row
    for row in load(P/'SOURCE_PINS.json')['files']:
        assert sha((ROOT/row['original_path']).read_bytes())==row['old_sha256'],row
    oldmaps={r['original_path']:r for r in previous['maps']}
    archive_pairs={(r['original_path'],r['old_sha256']):r for r in plan['archives']}
    writes={};merged=[];phys={}
    def verify_subset(before,after):
        assert before['version']==after['version']=='immutable-source-archive-map-0.1'
        assert all(after['documents'].get(k)==v for k,v in before['documents'].items())
        assert all(e in after['entries'] for e in before['entries'])
    for row in plan['maps']:
        name=row['original_path'];live=ROOT/name;old=live.read_bytes() if live.exists() else None
        assert (sha(old) if old is not None else None)==row['old_sha256']
        candidate=P/row['candidate'];data=candidate.read_bytes();assert sha(data)==row['new_sha256'];after=json.loads(data)
        assert after['version']=='immutable-source-archive-map-0.1'
        assert len({(e['original_path'],e['sha256']) for e in after['entries']})==len(after['entries'])
        for e in after['entries']:assert e['archived_path']==f"catalogue/source-snapshots/{e['sha256']}/{e['original_path']}"
        if old is not None:
            verify_subset(json.loads(old),after)
            assert (P/'prior-map-bytes'/name).read_bytes()==old
            assert (name,sha(old)) in archive_pairs
        if name in oldmaps:
            prior=oldmaps[name];verify_subset(load(PREV/prior['candidate']),after)
            if prior['old_sha256']!=(sha(old) if old is not None else None):merged.append(name)
        writes[name]=(row['old_sha256'],row['new_sha256'])
        phys[str(candidate.relative_to(ROOT))]=sha(data)
    assert set(merged)==set(plan['merged_concurrent_maps']) and len(merged)==8
    for row in plan['archives']:
        canonical=f"catalogue/source-snapshots/{row['old_sha256']}/{row['original_path']}"
        assert row['canonical_archive']==canonical
        snapshot=P/row['snapshot'];data=snapshot.read_bytes();assert sha(data)==row['old_sha256']
        if row['already_present']:assert (ROOT/canonical).read_bytes()==data
        else:assert not (ROOT/canonical).exists();writes[canonical]=(None,row['old_sha256'])
        phys[str(snapshot.relative_to(ROOT))]=sha(data)
    for old in previous['archives']:
        pair=(old['original_path'],old['old_sha256']);assert pair in archive_pairs
        assert (P/archive_pairs[pair]['snapshot']).read_bytes()==(PREV/old['snapshot']).read_bytes()
    assert {r['original_path']:(r['old_sha256'],r['new_sha256']) for r in whitelist['writes']}==writes
    assert whitelist['future_source_installs']==plan['replacements']
    known=load(P/'CHECK_RESULTS.json')['checks']
    prior=load(PREV/'CHECK_RESULTS.json')['checks']
    knownkeys={(r['document'],r['original_path'],r['old_sha256']) for r in known}
    knownkeys|={(r['document'],r['original_path'],r['old_sha256']) for r in prior if r['outcome']=='passed'}
    excluded=(A+'shared-hook-install-v1/',A+'profile-install-v1/',str(HERE.relative_to(ROOT))+'/')
    missing=[];scan=0;unreadable=[]
    for directory in ['docs','catalogue']:
        for path in (ROOT/directory).rglob('*.json'):
            doc=path.relative_to(ROOT).as_posix()
            if doc.startswith(excluded) or doc.startswith('catalogue/source-snapshots/') or path.name=='source-archive-map.json':continue
            data=path.read_bytes()
            try:node=json.loads(data)
            except (ValueError,UnicodeDecodeError):
                if any(p.encode() in data and h.encode() in data for p,h in archive_pairs):unreadable.append(doc)
                continue
            scan+=1
            for name,h in pairs(node)&set(archive_pairs):
                if (doc,name,h) not in knownkeys:missing.append((doc,name,h))
    assert not missing,missing
    assert not unreadable,unreadable
    drift=load(P/'DRIFT.json');outside={r['original_path'] for r in drift['outside_write_paths']}
    assert outside=={'catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json','tools/build_benchmark.py','web/index.html'}
    assert not outside & set(writes) and not outside & {r['original_path'] for r in plan['replacements']}
    result=dict(status='provisional' if provisional else 'passed',scope='Preservation/allowed-write identities only; source code approval separate',maps=len(plan['maps']),archives=len(plan['archives']),metadata_writes=len(writes),source_installs=11,additive_merges=merged,prior_archive_pairs_preserved=len(previous['archives']),current_immutable_consumer_scan=scan,missing_affected_consumers=missing,outside_changes_untouched=sorted(outside))
    prefix='provisional-' if provisional else ''
    (HERE/(prefix+'plan-results.json')).write_text(json.dumps(result,indent=2)+'\n')
    (HERE/(prefix+'plan-pins.json')).write_text(json.dumps(dict(files=phys),indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
