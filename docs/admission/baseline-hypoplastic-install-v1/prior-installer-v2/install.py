"""Guarded coordinator installation: default preflight; explicit reviewed --apply."""
if not __debug__:
    raise RuntimeError("Optimized Python disables required assertions; installation refused")
from pathlib import Path
import argparse,hashlib,json,os,sys,tempfile,uuid
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from atlas.agent_review import approval_entry
from atlas.evidence import checked_receipt
sha=lambda data:hashlib.sha256(data).hexdigest()
def safe(name):
    rel=Path(name)
    assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix()==name,name
    p=ROOT/rel
    assert p.resolve().is_relative_to(ROOT),name
    for part in [p,*p.parents]:
        if part==ROOT:break
        assert not part.is_symlink(),name
    return p
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--apply',action='store_true')
    ap.add_argument('--review')
    ap.add_argument('--review-sha256')
    args=ap.parse_args()
    freeze=json.loads((HERE/'INSTALL_SOURCE_FREEZE.json').read_text())
    for name,digest in freeze.items():assert sha(safe(name).read_bytes())==digest,name
    plan=json.loads((HERE/'PLAN.json').read_text())
    assert plan['passed'] and not plan['failed'] and not plan['issues']
    proposal=ROOT/'docs/admission/baseline-hypoplastic-canonical-v1'
    old=json.loads((proposal/'registry-observed.json').read_text())
    future=json.loads((proposal/'registry-proposed.json').read_text())
    additions=json.loads((proposal/'approval-entries.json').read_text())
    assert future==dict(old,models=old['models']+additions)
    for entry in additions:
        short='vw96' if entry['model_id']=='hypoplastic-sand-vw96' else 'igs97'
        source=ROOT/('docs/reviews/'+short+'-agent-v1/review.json')
        expected=approval_entry(source,root=ROOT)
        expected['review']['path']=entry['review']['path']
        assert expected==entry
        assert safe(entry['review']['path']).exists() is False
        assert (proposal/'proposed'/entry['review']['path']).read_bytes()==source.read_bytes()
    operations=[]
    for row in plan['archives']:
        dest=row['canonical_archive']
        if not row['already_present']:operations.append((dest,None,(HERE/row['snapshot']).read_bytes(),'snapshot'))
        else:assert sha(safe(dest).read_bytes())==row['old_sha256']
    for row in plan['maps']:
        operations.append((row['original_path'],row['old_sha256'],(HERE/row['candidate']).read_bytes(),'map'))
    for entry in additions:
        name=entry['review']['path']
        operations.append((name,None,(proposal/'proposed'/name).read_bytes(),'canonical-review'))
    operations.append(('catalogue/approved-models.json',sha((proposal/'registry-observed.json').read_bytes()),(proposal/'registry-proposed.json').read_bytes(),'registry'))
    for name,expected,data,kind in operations:
        dest=safe(name)
        assert (sha(dest.read_bytes()) if dest.exists() else None)==expected,name
    # Every existing affected binding must pass before changing production.
    for row in plan['baseline']+plan['all_existing_candidate_map_bindings']:
        checked_receipt(ROOT,row['document'],row['original_path'],row['old_sha256'])
    out={'apply':args.apply,'status':'preflight-pass','operations':[dict(path=n,before=o,after=sha(d),kind=k) for n,o,d,k in operations],'completed':[]}
    if args.apply:
        assert args.review and args.review_sha256,'Exact independent review required'
        review=safe(args.review)
        assert sha(review.read_bytes())==args.review_sha256
        decision=json.loads(review.read_text())
        assert decision.get('task')=='INSTALL-baseline-hypoplastic-v1' and decision.get('accepted') is True, 'Exact task acceptance required'
        assert decision.get('reviewer_run_id') not in (None,'','/root'), 'Actual separate reviewing run required'
        assert decision.get('installer_sha256')==sha((HERE/'install.py').read_bytes()), 'Installer review binding'
        assert decision.get('source_freeze_sha256')==sha((HERE/'INSTALL_SOURCE_FREEZE.json').read_bytes()), 'Freeze review binding'
        assert decision.get('operations')==out['operations'], 'Exact ordered operation review binding'
        out['review']={'path':args.review,'sha256':args.review_sha256}
        journal=HERE/'APPLY_JOURNAL.json'
        assert not journal.exists(),'Never restart an existing apply journal'
        journal.write_text(json.dumps(out,indent=2)+'\n')
        for name,expected,data,kind in operations:
            dest=safe(name)
            assert (sha(dest.read_bytes()) if dest.exists() else None)==expected,name
            dest.parent.mkdir(parents=True,exist_ok=True)
            temporary=dest.with_name(dest.name+'.atlas-install-'+uuid.uuid4().hex)
            temporary.write_bytes(data)
            assert sha(temporary.read_bytes())==sha(data)
            os.replace(temporary,dest)
            out['completed'].append(name)
            journal.write_text(json.dumps(out,indent=2)+'\n')
        for row in plan['baseline']+plan['all_existing_candidate_map_bindings']:
            checked_receipt(ROOT,row['document'],row['original_path'],row['old_sha256'])
        for entry in additions:assert approval_entry(safe(entry['review']['path']),root=ROOT)==entry
        assert json.loads(safe('catalogue/approved-models.json').read_text())==future
        out['status']='installed-pass'
        journal.write_text(json.dumps(out,indent=2)+'\n')
    else:(HERE/'PREFLIGHT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'operations':len(operations),'completed':len(out['completed'])},indent=2))
if __name__=='__main__':main()
