"""Verify the exact retained historical replay without rerunning scripts."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def main():
    report=read(HERE/'historical-replay.json')
    view=Path(report['view'])
    assert len(report['files'])==165
    assert report['archived_inputs']==['docs/reviews/tmd2-web-snapshot-v1/source-archive-map.json']
    for name,row in report['files'].items():
        assert sha(view/name)==row['sha256'],name
        assert sha(ROOT/row['selected'])==row['sha256'],name
    assert report['scientific_results_match_original'] is True
    assert not report['private_arrays_copied'] and not report['script_rewriting']
    assert report['compiled_calls']==report['builds']==0
    for row in report['results']:
        assert row['returncode']==0
        name=row['id']
        stdout=HERE/(name+'-historical.stdout.txt')
        stderr=HERE/(name+'-historical.stderr.txt')
        assert sha(stdout)==row['stdout_sha256']
        assert sha(stderr)==row['stderr_sha256']
        if name.startswith('scientific-'):
            expected=ROOT/'docs/benchmarks/kfs-tmd2-reporting-agent-v1'/('private-check-results.json' if name.endswith('private') else 'check-results.json')
            assert read(stdout)==read(expected)
    failures=read(HERE/'retained-live-path-failures.json')
    assert len(failures)==2 and all(r['returncode']!=0 for r in failures)
    print('PASS: unchanged scientific public/private and status checkers, 165 exact public files, one preserved historical map; original live-path failures retained.')
if __name__=='__main__':main()
