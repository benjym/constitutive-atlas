#!/usr/bin/env python3
"""Read-only repository audit plus isolated Python receipt mutation probes."""
import copy,hashlib,json,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,CHECKLIST
from atlas.evidence import checked_receipt
from atlas.dsl import ValidationError
BASE=pathlib.Path(__file__).resolve().parent
REV='06f5214d2e18f4806a0a779204b6371fb38bafa6'
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
    prefixes=['docs/reviews/j2-scientific-v1','docs/reviews/j2-scientific-v2','docs/admission/j2-approved-v2','catalogue/agent-reviews/j2-linear-hardening-agent-v2.json','models/research/j2']
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',REV,*prefixes],cwd=ROOT,text=True).splitlines()
    identities=[]
    for name in names:
        old=subprocess.check_output(['git','show',REV+':'+name],cwd=ROOT)
        live=(ROOT/name).read_bytes();assert old==live,name
        identities.append(dict(path=name,sha256=sha(live)))
    old_registry=json.loads(subprocess.check_output(['git','show',REV+':catalogue/approved-models.json'],cwd=ROOT))
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
    def j2(v):
        if isinstance(v,list):return [x for x in v if 'j2' in str(x.get('model_id',''))]
        return j2(v['models'] if 'models' in v else v['approvals'])
    assert j2(old_registry)==j2(registry)
    review='catalogue/agent-reviews/j2-linear-hardening-agent-v2.json'
    validate_review(ROOT/review,ROOT,for_approval=True)
    # Check every explicit archive edge and immutable document pin directly.
    maps=['catalogue/agent-reviews/source-archive-map.json','docs/reviews/j2-scientific-v2/source-archive-map.json']
    archives=[]
    for name in maps:
        mapping=json.loads((ROOT/name).read_text())
        assert mapping['version']=='immutable-source-archive-map-0.1'
        for document,pin in mapping['documents'].items():
            assert sha((ROOT/document).read_bytes())==pin
            for entry in mapping['entries']:
                target=checked_receipt(ROOT,document,entry['original_path'],entry['sha256'])
                archives.append(dict(document=document,path=entry['original_path'],resolved=str(target.relative_to(ROOT)),sha256=sha(target.read_bytes())))
    # Review historical input dependencies honestly: retain the lost contextual board.
    manifest='docs/reviews/j2-scientific-v2/input-manifest.json';gaps=[];verified=0
    for item in json.loads((ROOT/manifest).read_text())['files']:
        try:checked_receipt(ROOT,manifest,item['path'],item['sha256']);verified+=1
        except ValueError as exc:gaps.append(dict(path=item['path'],sha256=item['sha256'],failure=str(exc)))
    assert [g['path'] for g in gaps]==['IMPLEMENTATION_PLAN.md'],gaps
    # Independently assembled registered-review fixture, no production files mutated.
    probes=[];concerns=[]
    with tempfile.TemporaryDirectory() as tmp:
        home=pathlib.Path(tmp);root=home/'repo';root.mkdir();(root/'models').mkdir();(root/'reviews').mkdir()
        model=root/'models/test.json';model.write_text('{"id":"test"}')
        report=root/'report.md';report.write_text('original bytes');digest=sha(report.read_bytes())
        original=report.read_bytes();archive=root/f'catalogue/source-snapshots/{digest}/report.md';archive.parent.mkdir(parents=True);archive.write_bytes(original)
        record=dict(schema_version='0.1',kind='agent-model-review',id='test',created_at='2026-11-01',source_commit='a'*40,model=dict(id='test',path='models/test.json',sha256=sha(model.read_bytes())),status='accepted',reviewer=dict(kind='agent',name='fixture',run_id='reviewer',independence_basis='Synthetic fixture only'),author_run_ids=['author'],scope='synthetic only',limitations=['No physical claim'],blocking_findings=[],artifacts=[dict(path='report.md',sha256=digest)],checklist=[dict(id=k,outcome='pass',reason='Synthetic only',evidence=['report.md']) for k in sorted(CHECKLIST)])
        document=root/'reviews/review.json';document.write_text(json.dumps(record))
        sidecar=root/'reviews/source-archive-map.json';mapping=dict(version='immutable-source-archive-map-0.1',documents={'reviews/review.json':sha(document.read_bytes())},entries=[dict(original_path='report.md',sha256=digest,archived_path=str(archive.relative_to(root)))])
        sidecar.write_text(json.dumps(mapping));report.write_text('new policy')
        validate_review(document,root,True);probes.append('registered historical artifact accepted')
        def rejected(label):
            try:validate_review(document,root,True)
            except (ValidationError,ValueError):probes.append(label)
            else:raise AssertionError('unexpected acceptance: '+label)
        # No live fallback, even if exact original content is restored there.
        report.write_bytes(original);archive.write_text('corrupt');rejected('corrupt archive rejects exact live fallback');archive.write_bytes(original)
        archive.unlink();rejected('missing archive rejects exact live fallback');archive.write_bytes(original)
        # Safe target-path check must survive symlinks, not just ../ checks.
        outside=home/'outside';outside.write_bytes(original);archive.unlink();archive.symlink_to(outside);rejected('symlink archive escape rejected');archive.unlink();archive.write_bytes(original)
        changed=copy.deepcopy(record);changed['scope']='broadened';document.write_text(json.dumps(changed));rejected('changed registered review rejected');document.write_text(json.dumps(record))
        # An archived old model must not replace the separate current model requirement.
        modelhash=sha(model.read_bytes());oldmodel=root/f'catalogue/source-snapshots/{modelhash}/models/test.json';oldmodel.parent.mkdir(parents=True);oldmodel.write_bytes(model.read_bytes())
        mapping['entries'].append(dict(original_path='models/test.json',sha256=modelhash,archived_path=str(oldmodel.relative_to(root))));sidecar.write_text(json.dumps(mapping));model.write_text('{"id":"test","changed":true}');rejected('archived model cannot bypass current model hash')
        model.write_bytes(oldmodel.read_bytes());mapping['documents']=['reviews/review.json'];sidecar.write_text(json.dumps(mapping))
        try:validate_review(document,root,True)
        except AttributeError:
            concerns.append(dict(id='AR-LOW-001',severity='low',blocking=False,detail='Malformed documents list containing the review path raises raw AttributeError instead of ValidationError. It fails closed; no hash/model/checklist gate bypass.'))
        else:raise AssertionError('unexpected malformed-map result')
    return dict(verdict='accept archive-resolution fix without broadening scientific approval',original_revision=REV,unchanged_original_files=identities,registry_j2_entry_unchanged=True,approval_validation_passed=True,archive_edges=archives,historical_inputs_verified=verified,context_retention_gaps=gaps,independent_probes=probes,code_concerns=concerns,compiled_calls=0,vendor_calls=0,limitations=['The unrecovered historical WIP board hash is a contextual retention gap, not an equation/reference/build input.','E6 public integration, E7 packaged website and E8 live delivery remain separate unfinished stages; this fix restores bounded E5 approval integrity only.'])
if __name__=='__main__':print(json.dumps(run(),indent=2))
