"""Nonmutating v2: merge recovered historical raw bindings into v1 proposal."""
from pathlib import Path
import hashlib,json,shutil,sys,tempfile
HERE=Path(__file__).resolve().parent
V1=HERE.parent
ROOT=V1.parents[4]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda b:hashlib.sha256(b).hexdigest()
enc=lambda v:(json.dumps(v,indent=2)+'\n').encode()
F='docs/ingestion/lade-duncan-1975/fused-linear-v1/'
DOC=F+'independent-review/saved-wasm-legacy-check-results.json'
MAP=F+'independent-review/source-archive-map.json'
REC=F+'legacy-prerequisite-recovery-v1/RECOVERY.json'
def main():
    # Preserve the entire initial owned proposal, including exact candidates/freezes.
    files=[p for p in V1.rglob('*') if p.is_file() and not p.is_relative_to(HERE)]
    prior=[]
    for p in sorted(files):
        name=p.relative_to(V1);data=p.read_bytes();target=HERE/'prior-v1'/name
        if target.exists():assert target.read_bytes()==data, str(name)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        prior.append(dict(original_path=p.relative_to(ROOT).as_posix(),old_sha256=sha(data)))
    (HERE/'PRESERVED_V1.json').write_bytes(enc(dict(files=prior)))
    plan=json.loads((HERE/'CURRENT_BASE.json').read_bytes());whitelist=json.loads((HERE/'CURRENT_BASE_WHITELIST.json').read_bytes())
    assert plan['passed'] and not (ROOT/MAP).exists(), 'Production sidecar appeared; replan required'
    recbytes=(ROOT/REC).read_bytes();docbytes=(ROOT/DOC).read_bytes();recovery=json.loads(recbytes);pins=json.loads(docbytes)['pins']
    for name,data in [(REC,recbytes),(DOC,docbytes)]:
        p=HERE/'recovery-inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    for row in plan['maps']:
        original=ROOT/row['original_path']
        assert (sha(original.read_bytes()) if original.exists() else None)==row['old_sha256'], row['original_path']
        data=(HERE/row['candidate']).read_bytes();assert sha(data)==row['new_sha256']
        target=HERE/row['candidate'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    mapping=json.loads((HERE/'candidates'/MAP).read_bytes());mapping['documents'][DOC]=sha(docbytes)
    recovered=[]
    for row in recovery['records']:
        name=row['original_path'];assert pins[name]==row['old_sha256'];assert sha((ROOT/name).read_bytes())==row['current_full_sha256']
        if not row['changed']:
            assert row['old_sha256']==row['current_full_sha256'];continue
        archive='catalogue/source-snapshots/'+row['old_sha256']+'/'+name
        assert row['archived_path']==archive and sha((ROOT/archive).read_bytes())==row['old_sha256']
        matches=[e for e in mapping['entries'] if e['original_path']==name and e['sha256']==row['old_sha256']]
        assert len(matches)==1 and matches[0]['archived_path']==archive
        recovered.append(dict(original_path=name,old_sha256=row['old_sha256'],current_full_sha256=row['current_full_sha256'],canonical_archive=archive,already_present=True))
    assert len(recovered)==24
    candidate=enc(mapping);(HERE/'candidates'/MAP).write_bytes(candidate)
    row=next(r for r in plan['maps'] if r['original_path']==MAP)
    row['new_sha256']=sha(candidate);row['document_pins']=[dict(original_document=d,old_document_sha256=h) for d,h in mapping['documents'].items()]
    row['entries']=[dict(original_path=e['original_path'],old_sha256=e['sha256'],canonical_archive=e['archived_path']) for e in mapping['entries']]
    next(r for r in whitelist['writes'] if r['original_path']==MAP)['new_sha256']=sha(candidate)
    results=[];baseline=[]
    for name,expected in pins.items():
        try:checked_receipt(ROOT,DOC,name,expected);outcome='passed'
        except Exception as error:outcome=str(error)
        baseline.append(dict(original_path=name,old_sha256=expected,outcome=outcome))
    with tempfile.TemporaryDirectory(dir=HERE,prefix='.overlay-') as temporary:
        overlay=Path(temporary)
        def put(name,data):
            p=overlay/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        for base in ['receipt-bytes','snapshots']:
            for p in (HERE/base).rglob('*'):
                if p.is_file():put(p.relative_to(HERE/base).as_posix(),p.read_bytes())
        put(DOC,docbytes)
        for r in plan['maps']:put(r['original_path'],(HERE/r['candidate']).read_bytes())
        put(plan['source']['original_path'],(ROOT/plan['source']['future_copy']).read_bytes())
        for r in plan['maps']:
            m=json.loads((HERE/r['candidate']).read_bytes())
            for d,pin in m['documents'].items():
                if not (overlay/d).exists():put(d,(ROOT/d).read_bytes())
                assert sha((overlay/d).read_bytes())==pin
            for e in m['entries']:
                for name in [e['original_path'],e['archived_path']]:
                    if not (overlay/name).exists() and (ROOT/name).is_file():put(name,(ROOT/name).read_bytes())
        for name in pins:
            if not (overlay/name).exists():put(name,(ROOT/name).read_bytes())
        checks=plan['simulated']+plan['all_existing_candidate_map_bindings']+[dict(document=DOC,original_path=n,old_sha256=h) for n,h in pins.items()]
        for r in checks:
            sidecar=(Path(r['document']).parent/'source-archive-map.json').as_posix()
            if not (overlay/sidecar).exists() and (ROOT/sidecar).is_file():put(sidecar,(ROOT/sidecar).read_bytes())
            try:checked_receipt(overlay,r['document'],r['original_path'],r['old_sha256'])
            except Exception:
                print(json.dumps(r));raise
            results.append(dict(document=r['document'],original_path=r['original_path'],old_sha256=r['old_sha256'],outcome='passed'))
        # Current full raw outputs remain directly verifiable; recovery does not overwrite them.
        for r in recovery['records']:assert sha((overlay/r['original_path']).read_bytes())==r['current_full_sha256']
    assert (ROOT/REC).read_bytes()==recbytes and (ROOT/DOC).read_bytes()==docbytes
    assert len([r for r in baseline if r['outcome']!='passed'])==24
    plan.update(identity='profile-install-preservation-proposal-v2',scope='nonmutating v2 proposal merging legacy raw recovery; no production mutation or scientific approval',prior_plan_sha256=sha((V1/'PLAN.json').read_bytes()),recovery_input=dict(original_path=REC,old_sha256=sha(recbytes)),recovery_document=dict(original_path=DOC,old_sha256=sha(docbytes)),recovered_raw_archives=recovered,recovery_baseline=baseline,combined_overlay_checks=results,combined_overlay_count=len(results),unchanged_current_raw_checks=57,passed=True)
    (HERE/'PLAN.json').write_bytes(enc(plan));whitelist['identity']='profile-install-preservation-proposal-v2';whitelist['already_present_recovery_archives']=recovered
    (HERE/'APPLY_WHITELIST.json').write_bytes(enc(whitelist))
    inputnames={REC,DOC,'atlas/evidence.py',plan['source']['original_path'],plan['source']['future_copy']}
    for r in checks:
        inputnames.add(r['document']);sidecar=(Path(r['document']).parent/'source-archive-map.json').as_posix()
        if (ROOT/sidecar).is_file():inputnames.add(sidecar)
    sourcepins=[dict(original_path=n,old_sha256=sha((ROOT/n).read_bytes())) for n in sorted(inputnames)]
    for r in plan['maps']:
        original=ROOT/r['original_path']
        assert (sha(original.read_bytes()) if original.exists() else None)==r['old_sha256'], 'Concurrent map change: '+r['original_path']
    for r in recovery['records']:assert sha((ROOT/r['original_path']).read_bytes())==r['current_full_sha256']
    (HERE/'SOURCE_PINS.json').write_bytes(enc(dict(files=sourcepins)))
    print(json.dumps(dict(passed=True,overlay_checks=len(results),new_recovery_bindings=24,current_full_raws_unchanged=57,production_writes=0,proposed_apply_paths=len(whitelist['writes']),sidecar_candidate_sha256=sha(candidate)),indent=2))
if __name__=='__main__':main()
