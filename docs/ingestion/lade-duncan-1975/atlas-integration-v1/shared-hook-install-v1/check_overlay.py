"""Pure saved-data overlay check; no source installation or compiled calls."""
from pathlib import Path
import hashlib,json,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    plan=json.loads((HERE/'PLAN.json').read_bytes())
    previous=json.loads((HERE.parent/'profile-install-v1/revision-v2/PLAN.json').read_bytes())
    checks=plan['simulated']+plan['all_existing_candidate_map_bindings']+previous['combined_overlay_checks']
    replacements={r['original_path']:r for r in plan['replacements']}
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
            checked_receipt(overlay,document,name,expected)
            results.append(dict(document=document,original_path=name,old_sha256=expected,outcome='passed'))
    for document in sorted({r['document'] for r in checks}):
        data=read(document);target=HERE/'receipt-bytes'/document;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for name,expected in inputs.items():assert sha((ROOT/name).read_bytes())==expected,'Concurrent input drift: '+name
    output=dict(passed=True,shared_hook_bindings=len(plan['simulated'])+len(plan['all_existing_candidate_map_bindings']),prior_profile_bindings=len(previous['combined_overlay_checks']),total_checks=len(results),checks=results,scope='Pure future-hook overlay including all previously verified profile/recovery bindings; Maxwell live source absent because replacement is unspecified')
    (HERE/'CHECK_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n')
    for n in ['atlas/evidence.py','docs/ingestion/lade-duncan-1975/atlas-integration-v1/hooks-proposed-v1/rebased-v5/PROPOSAL.json','docs/ingestion/lade-duncan-1975/atlas-integration-v1/workflow-v1/PROPOSAL.json']:
        read(n)
    (HERE/'SOURCE_PINS.json').write_text(json.dumps(dict(files=[dict(original_path=n,old_sha256=h) for n,h in sorted(inputs.items())]),indent=2)+'\n')
    print(json.dumps(dict(passed=True,total_checks=len(results),shared_hook_bindings=output['shared_hook_bindings'],prior_profile_bindings=output['prior_profile_bindings'],production_writes=0)))
if __name__=='__main__':main()
