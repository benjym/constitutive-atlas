"""One-time exact private byte retention; no material or author code is executed."""
import hashlib,json,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIVATE=ROOT/'.local/private-evidence/kfs-development-campaign-v1'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def main():
    bindings_path=ROOT/'docs/benchmarks/kfs-development-agent-v1/private-input-bindings.json'
    bindings=json.loads(bindings_path.read_text())
    expected=dict(bindings['root_inputs'])
    expected.update({s['path']:s['sha256'] for s in bindings['private_sources']})
    for study in bindings['study_metadata']:
        expected.update({str(Path(study['root'])/n):h for n,h in study['metadata_files'].items()})
    for name,h in expected.items():assert digest(Path(name))==h,('original binding mismatch',name)
    roots={Path(s['root']):'studies/'+Path(s['root']).name for s in bindings['study_metadata']}
    roots[ROOT/'paper/results/pilot-matched96']='pilot-matched96'
    roots[ROOT/'.local/private-evidence/kfs-current-tmd7-v1']='prior-tmd7-retention'
    files={}
    counts={}
    for source,prefix in roots.items():
        assert source.is_dir(),source
        count=0
        for p in sorted(source.rglob('*')):
            assert not p.is_symlink(),('source symlink',p)
            if p.is_file():files[p]=prefix+'/'+p.relative_to(source).as_posix();count+=1
            else:assert p.is_dir(),p
        counts[prefix]=count
    for name in expected:
        p=Path(name)
        if p not in files:files[p]='review-inputs/'+hashlib.sha256(str(p).encode()).hexdigest()[:16]+'/'+p.name
    for p in [bindings_path,ROOT/'docs/benchmarks/kfs-development-agent-v1/manifest.json',ROOT/'docs/benchmarks/kfs-development-agent-v1/decision.json',ROOT/'docs/benchmarks/kfs-development-agent-v1/check.py']:
        if p not in files:files[p]='governing/'+p.name
    records=[]
    for source,dest in sorted(files.items(),key=lambda x:x[1]):
        assert source.is_file() and not source.is_symlink(),source
        raw=source.read_bytes();records.append({'origin':str(source),'retained_path':dest,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    assert len({r['retained_path'] for r in records})==len(records)
    receipt={'kind':'private-benchmark-retention','id':'kfs-development-campaign-retention-v1','date':'2026-11-01','private_root':str(PRIVATE.relative_to(ROOT)),'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'scope':'Complete named trees and explicit private review bindings only; not a claim of full transitive historical replay closure.','review_bindings_sha256':digest(bindings_path),'explicit_review_bindings':len(expected),'tree_counts':counts,'files':records}
    freeze=HERE/'inventory-before.json';assert not freeze.exists(),'Existing freeze must not be replaced';write(freeze,receipt)
    assert not PRIVATE.exists(),'Existing private retention must not be replaced'
    PRIVATE.mkdir(parents=True,mode=0o700)
    for r in records:
        source=Path(r['origin']);dest=PRIVATE/r['retained_path'];dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        assert digest(source)==r['sha256'],('source changed during retention',source)
        shutil.copyfile(source,dest);dest.chmod(0o600)
        assert digest(dest)==r['sha256'] and dest.stat().st_size==r['bytes'],dest
    # Verify exact source tree membership after copying, as well as every source byte.
    for source,prefix in roots.items():
        before={r['origin'] for r in records if r['retained_path'].startswith(prefix+'/')}
        after={str(p) for p in source.rglob('*') if p.is_file()}
        assert before==after,('source membership changed',source)
    for r in records:assert digest(Path(r['origin']))==r['sha256'],r['origin']
    write(HERE/'receipts.json',receipt)
    print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records),'explicit_review_bindings':len(expected),'tree_counts':counts}))
if __name__=='__main__':main()
