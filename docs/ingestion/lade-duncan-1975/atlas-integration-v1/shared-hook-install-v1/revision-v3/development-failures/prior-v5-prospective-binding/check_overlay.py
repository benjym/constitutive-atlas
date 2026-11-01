"""Pure saved-data overlay check; no source installation or compiled calls."""
from pathlib import Path
import hashlib,json,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from plan_preservation import pairs
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    plan=json.loads((HERE/'PLAN.json').read_bytes())
    previous=json.loads((HERE.parent/'revision-v2/CHECK_RESULTS.json').read_bytes())
    # Retain every previously passing result; preexisting failures remain diagnostics.
    previous['checks']=[r for r in previous['checks'] if r['outcome']=='passed']
    checks=plan['simulated']+plan['all_existing_candidate_map_bindings']+previous['checks']
    replacements={r['original_path']:r for r in plan['replacements']}
    extra=[]
    for row in plan['maps']:
        mapping=json.loads((HERE/row['candidate']).read_bytes())
        oldpairs={(e['original_path'],e['sha256']) for e in mapping['entries']}
        for document in mapping['documents']:
            for name,expected in sorted(pairs(json.loads((ROOT/document).read_bytes()))):
                if not Path(name).is_absolute() and '..' not in Path(name).parts and ((ROOT/name).is_file() or (name,expected) in oldpairs):
                    try:checked_receipt(ROOT,document,name,expected);before='passed'
                    except Exception as error:before=str(error)
                    extra.append(dict(document=document,original_path=name,old_sha256=expected,peer_baseline=before))
    checks+=extra
    scheduled_checks=len(checks)
    # A repeated exact document/path/hash predicate has identical semantics.
    # Keep mandatory/baseline-valid obligations ahead of optional invalid-peer diagnostics.
    unique={}
    for r in checks:
        key=(r['document'],r['original_path'],r['old_sha256'])
        if key not in unique or r.get('peer_baseline','passed')=='passed':unique[key]=r
    checks=list(unique.values())
    inputs={};results=[]
    def read(name):
        data=(ROOT/name).read_bytes();inputs[name]=sha(data);return data
    installed='docs/ingestion/lade-duncan-1975/atlas-integration-v1/profile-install-v1/coordinator-install-v1/INSTALLED.json'
    assert json.loads(read(installed))['status']=='passed'
    with tempfile.TemporaryDirectory(dir=HERE,prefix='.supplemental-overlay-') as tmp:
        overlay=Path(tmp)
        def put(name,data):
            p=overlay/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        for r in plan['maps']:
            actual=sha(read(r['original_path'])) if (ROOT/r['original_path']).exists() else None
            assert actual==r['old_sha256'],r['original_path']
            data=(HERE/r['candidate']).read_bytes();assert sha(data)==r['new_sha256'];put(r['original_path'],data)
        for r in plan['archives']:
            data=(HERE/r['snapshot']).read_bytes();assert sha(data)==r['old_sha256'];put(r['canonical_archive'],data)
        for r in plan['replacements']:
            assert sha(read(r['original_path']))==r['old_sha256']
            if r['future_copy']:
                data=read(r['future_copy']);assert sha(data)==r['new_sha256'];put(r['original_path'],data)
        for r in checks:
            document=r['document'];name=r['original_path'];expected=r['old_sha256']
            if not (overlay/document).exists():put(document,read(document))
            sidecar=(Path(document).parent/'source-archive-map.json').as_posix()
            if not (overlay/sidecar).exists() and (ROOT/sidecar).is_file():put(sidecar,read(sidecar))
            if (overlay/sidecar).exists():
                mapping=json.loads((overlay/sidecar).read_bytes())
                for e in mapping['entries']:
                    archive=e['archived_path']
                    if not (overlay/archive).exists() and (ROOT/archive).is_file():put(archive,read(archive))
            if name not in replacements and not (overlay/name).exists() and (ROOT/name).is_file():put(name,read(name))
            try:checked_receipt(overlay,document,name,expected);outcome='passed'
            except Exception as error:
                if r.get('peer_baseline','passed')=='passed':raise
                # Report unrelated already-invalid peer pairs without repairing them.
                # Their source must remain the same live bytes, outside replacements/maps.
                if name in replacements or name in {x['original_path'] for x in plan['maps']}:
                    original=(ROOT/name).read_bytes();canonical='catalogue/source-snapshots/'+sha(original)+'/'+name
                    assert (overlay/canonical).read_bytes()==original, (document,name)
                else:assert (overlay/name).read_bytes()==(ROOT/name).read_bytes(), (document,name)
                outcome='preexisting_peer_failure';r['peer_after']=str(error)
            results.append(dict(document=document,original_path=name,old_sha256=expected,outcome=outcome,**({'baseline_failure':r['peer_baseline'],'overlay_failure':r['peer_after']} if outcome!='passed' else {})))
    for document in sorted({r['document'] for r in checks}):
        data=read(document);target=HERE/'receipt-bytes'/document;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for name,expected in inputs.items():assert sha((ROOT/name).read_bytes())==expected,'Concurrent input drift: '+name
    output=dict(passed=True,shared_hook_bindings=len(plan['simulated'])+len(plan['all_existing_candidate_map_bindings']),current_peer_receipt_checks=len(extra),prior_profile_bindings=len(previous['checks']),scheduled_checks=scheduled_checks,total_checks=len(results),passing_checks=sum(r['outcome']=='passed' for r in results),preexisting_peer_failures=[r for r in results if r['outcome']!='passed'],checks=results,scope='Pure future-hook overlay including all previously verified six-source/profile/recovery bindings; all eleven exact prospective source copies installed in temporary overlay; no production changes')
    (HERE/'CHECK_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n')
    for n in ['atlas/evidence.py','docs/ingestion/lade-duncan-1975/atlas-integration-v1/hooks-proposed-v1/rebased-v5/PROPOSAL.json','docs/ingestion/lade-duncan-1975/atlas-integration-v1/workflow-v1/PROPOSAL.json']:
        read(n)
    (HERE/'SOURCE_PINS.json').write_text(json.dumps(dict(files=[dict(original_path=n,old_sha256=h) for n,h in sorted(inputs.items())]),indent=2)+'\n')
    print(json.dumps(dict(passed=True,total_checks=len(results),shared_hook_bindings=output['shared_hook_bindings'],prior_profile_bindings=output['prior_profile_bindings'],production_writes=0)))
if __name__=='__main__':main()
