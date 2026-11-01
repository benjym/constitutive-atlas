"""Verify exact source, archive and browser evidence without executing any runtime."""
from pathlib import Path
import hashlib,json
from urllib.parse import urlsplit,unquote
import sys
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def main():
    plan=read(HERE/'archive-plan-v2.json')
    prospective=read(HERE/'independent-review/prospective-receipt.json')['binding']
    for name,expected in prospective['candidates'].items():
        assert sha(ROOT/name)==expected,name
    assert sha(ROOT/'tools/build_tmd2_review.py')==prospective['helper_sha256']
    assert sha(ROOT/'tests/test_web_tmd2_review.py')==prospective['helper_tests_sha256']
    for name,expected in plan['prior'].items():
        assert sha(ROOT/'catalogue/source-snapshots'/expected/name)==expected,name
    for name,expected in plan['unchanged_documents'].items():
        assert sha(ROOT/name)==expected,name
    for name,node in plan['maps'].items():
        assert read(ROOT/name)==node,name
    for row in plan['redirected_pairs']+plan['affected_secondary']:
        if all(loc['shape']=='original_path-object' for loc in row['locations']):
            paths=[ROOT/row['original_path'],ROOT/'catalogue/source-snapshots'/row['sha256']/row['original_path']]
            assert any(p.is_file() and sha(p)==row['sha256'] for p in paths)
        else:
            assert sha(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']))==row['sha256']
    package=read(HERE/'package-manifest.json');site=Path(package['path'])
    assert len(package['files'])==957 and len(package['added'])==3
    assert package['changed']==['index.html','tmd2.html'] and not package['removed']
    for name,row in package['files'].items():
        assert sha(site/name)==row['sha256'],name
    browser=HERE/'browser'
    desktop=read(browser/'desktop-observation.json')
    entries=read(browser/'entry-assets-observation.json')
    responses=desktop['responses']+entries['rows']
    for row in responses:
        assert row['status']==200
        path=unquote(urlsplit(row['url']).path)
        assert path.startswith('/constitutive-atlas/')
        name=path.removeprefix('/constitutive-atlas/')
        assert row['sha256']==package['files'][name]['sha256']
        assert row['bytes']==package['files'][name]['bytes']
    review=ROOT/'docs/benchmarks/kfs-tmd2-reporting-agent-v1'
    decision=read(review/'decision.json')
    assert sha(review/'decision.json')=='ae2591b574efec5ef63db8782e6333d3f880ae8cbcb0b4f7464be39862e0d4dc'
    for name in ['desktop-observation.json','mobile-observation.json']:
        observed=read(browser/name)
        text=observed.get('reviewSection',observed.get('reviewText'))
        assert all(q in text for q in decision['remaining_qualifications'])
        assert 'General IGS model admission and experimental validation remain open' in text
        assert observed['documentWidth']==observed['width']
        assert all(i['complete'] and i['naturalWidth']>0 for i in observed['image'])
    for name in ['review-observation.json','mobile-review-observation.json']:
        observed=read(browser/name)
        assert observed['documentWidth']==observed['width']
        assert (review/'README.md').read_text().strip() in observed['text']
        assert all('## Q'+str(i) in observed['text'] for i in range(1,7))
    methods=read(browser/'methods-observation.json')
    assert methods['url'].endswith('index.html#methods')
    assert 'Independent agent review accepts qualified reporting' in methods['card']
    assert methods['links'][0]['href'].endswith('/constitutive-atlas/tmd2.html')
    assert '0 (Errors: 0, Warnings: 0)' in (browser/'final-console.txt').read_text()
    assert 'favicon.ico' in (browser/'all-console.txt').read_text()
    report={'passed':True,'source_and_map_direct_pairs':len(plan['redirected_pairs']),
            'secondary_pairs':len(plan['affected_secondary']),'exact_package_files':len(package['files']),
            'http_response_records':len(responses),'unique_http_assets':len({r['url'] for r in responses}),
            'mobile_width':390,'no_horizontal_overflow':True,'six_reasons_visible':True,
            'initial_favicon_404_retained':True,'new_compiled_study_calls':0,'builds':0}
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
