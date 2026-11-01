"""Replay unchanged scientific checkers in their exact retained public evidence view."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
REVIEW=Path('docs/benchmarks/kfs-tmd2-reporting-agent-v1')
STATUS=Path('docs/benchmarks/kfs-tmd2-reporting-status-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def main():
    manifest=read(ROOT/REVIEW/'manifest.json')
    assert sha(ROOT/REVIEW/'manifest.json')=='b21fd9e92e41e23482a1e5a65a31dae0f58a8843633aa7ee46a98908965fc8f4'
    wanted={}
    def add(name,expected):
        relative=Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        assert name not in wanted or wanted[name]==expected, name
        wanted[name]=expected
    for name,expected in manifest['public_inputs'].items(): add(name,expected)
    for name,expected in manifest['outputs'].items(): add(str(REVIEW/name),expected)
    for name in ['manifest.json','check-results.json','private-check-results.json']:
        add(str(REVIEW/name),sha(ROOT/REVIEW/name))
    integration=read(ROOT/STATUS/'integration.json')
    for name,expected in integration['files'].items(): add(name,expected)
    for name,expected in read(ROOT/STATUS/'parent-inputs.json').items(): add(name,expected)
    for name in ['integration.json','check_saved.py','parent-inputs.json','parent-replays.json','parent-review-check-private.json']:
        add(str(STATUS/name),sha(ROOT/STATUS/name))
    view=ROOT/'.local/private-evidence/web-tmd2-reporting-agent-v1/historical-review-view-v1'
    assert not view.exists(), 'Use a fresh separately identified replay; never overwrite evidence'
    view.mkdir(parents=True)
    selected={}
    for name,expected in sorted(wanted.items()):
        original=ROOT/name
        archive=ROOT/'catalogue/source-snapshots'/expected/name
        path=original if original.is_file() and sha(original)==expected else archive
        assert path.is_file() and sha(path)==expected, name
        dest=view/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(path.read_bytes())
        assert sha(dest)==expected
        selected[name]={'sha256':expected,'selected':str(path.relative_to(ROOT))}
    # Scripts, expected hashes and scientific policies are copied byte-for-byte.
    # No helper imports, evaluators, build tools or code rewriting are introduced.
    commands=[
        ('scientific-public',[sys.executable,'-B',str(view/REVIEW/'check_saved.py')]),
        ('scientific-private',[sys.executable,'-B',str(view/REVIEW/'check_saved.py'),'--private']),
        ('coordinator-status',[sys.executable,'-B',str(view/STATUS/'check_saved.py')])]
    results=[]
    for name,command in commands:
        result=subprocess.run(command,capture_output=True,text=True,timeout=60,cwd=view)
        (HERE/(name+'-historical.stdout.txt')).write_text(result.stdout)
        (HERE/(name+'-historical.stderr.txt')).write_text(result.stderr)
        assert result.returncode==0,result.stderr
        if name.startswith('scientific-'):
            expected=ROOT/REVIEW/('private-check-results.json' if name.endswith('private') else 'check-results.json')
            assert json.loads(result.stdout)==read(expected),name
        results.append({'id':name,'command':command,'returncode':result.returncode,
                        'stdout_sha256':hashlib.sha256(result.stdout.encode()).hexdigest(),
                        'stderr_sha256':hashlib.sha256(result.stderr.encode()).hexdigest()})
    report={'scope':'Exact historical saved-only scientific-review replay, not current live-path identity or new numerical qualification.',
        'view':str(view),'files':selected,'results':results,'scientific_results_match_original':True,
        'private_arrays_copied':False,'script_rewriting':False,'compiled_calls':0,'builds':0,
        'archived_inputs':[n for n,row in selected.items() if row['selected']!=n]}
    (HERE/'historical-replay.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: exact historical public/private scientific checks and coordinator status replay; '+str(len(wanted))+' public files; '+str(len(report['archived_inputs']))+' archived input(s).')
if __name__=='__main__': main()
