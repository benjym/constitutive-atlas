"""Independent source/retained-font calculation; no browser or compiled calls."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PACKET=ROOT/'docs/ingestion/vibe-2026/plot-presentation-v1'
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
freeze=PACKET/'source-manifest-v3.json'
assert sha(freeze)=='525adf7950d87f4ee240038d6f07b603d111b5305ef7c17216bf25558deb1f20'
manifest=json.loads(freeze.read_text())
for pin in manifest['files']:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
v2=json.loads((PACKET/'source-manifest-v2.json').read_text())
recovery=json.loads((PACKET/'v2-recovery.json').read_text())['files']
assert len(recovery)==len(v2['files'])==35
for pin in v2['files']:
    row=next(row for row in recovery if row['original']==pin['path'])
    assert row['sha256']==pin['sha256']==sha(ROOT/row['retained'])
old=PACKET/'source-freeze-v2'
app=(old/'web/app.js').read_text()
assert app.count('  const top=27,h=211,all=')==1
assert app.count("{x:12,y:top-12,class:'axis-label'}")==1
expected=app.replace('  const top=27,h=211,all=','  const top=40,h=198,all=').replace("{x:12,y:top-12,class:'axis-label'}","{x:12,y:17,class:'axis-label'}")
assert expected==(ROOT/'web/app.js').read_text()
for name in ['web/plot-labels.mjs','tests/test_plot_labels.mjs','tools/build_web.py']:
    assert (old/name).read_bytes()==(ROOT/name).read_bytes()
# Preserve this review's previously frozen positive and negative decisions.
for name in ['manifest-v1.json','manifest-v2.json']:
    for path,digest in json.loads((OUT/name).read_text())['files'].items():assert sha(ROOT/path)==digest
doc=Path('catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json')
review=json.loads((ROOT/doc).read_text())
assert sha(ROOT/doc)=='8e36c1984af615ece3ef4a05546871defbe05a64f6a483d295f9056f29f3ae99'
assert sha(ROOT/review['model']['path'])==review['model']['sha256']=='a7d3f0f61ff6654f1dc924178a3551a740ca39212a99813c2b9ce5c15b16c987'
for pin in review['artifacts']:
    assert sha(ROOT/pin['path'])==pin['sha256']==sha(checked_receipt(ROOT,doc,pin['path'],pin['sha256']))
assert len(review['artifacts'])==281
raw=PACKET/'raw-plot-bounds-browser-v3.log'
assert raw.read_bytes()==(ROOT/'output/playwright/vibe-browser-v3/raw-plot-bounds.log').read_bytes()
charts=json.loads(raw.read_text().split('### Result\n',1)[1].split('\n### Ran Playwright',1)[0])
proof=[]
for chart in charts:
    texts=chart['text'];boxes=[]
    # Actual chart generation emits alternating y/x ticks followed by x/y titles.
    assert len(texts)==12
    for i,box in enumerate(texts):
        delta=2 if i==11 else 13-3.25*(i//2) if i<10 and i%2==0 else 0
        moved={**box,'y':box['y']+delta}
        assert moved['x']>=0 and moved['x']+moved['w']<=480
        assert moved['y']>=0 and moved['y']+moved['h']<=300
        boxes.append(moved)
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:
            assert not (a['x']<b['x']+b['w'] and b['x']<a['x']+a['w'] and a['y']<b['y']+b['h'] and b['y']<a['y']+a['h']), (chart['id'],a,b)
    title,top=boxes[-1],boxes[0]
    proof.append(dict(chart=chart['id'],title_top=title['y'],title_bottom=title['y']+title['h'],highest_tick_top=top['y'],vertical_gap=top['y']-title['y']-title['h'],all_text_bounds_and_pairwise_nonoverlap=True))
(OUT/'retained-font-translation-v3.json').write_text(json.dumps(dict(raw_sha256=sha(raw),kind='source-calculation-not-new-browser-observation',charts=proof),indent=2)+'\n')
for name,argv in [('pure-tests-v3.log',['node','--test','tests/test_plot_labels.mjs']),('app-syntax-v3.log',['node','--check','web/app.js']),('independent-format-cases-v3.json',['node',str(OUT/'independent-format-cases.mjs')]),('independent-layout-cases-v3.json',['node',str(OUT/'independent-layout-cases-v2.mjs')])]:
    r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True);(OUT/name).write_text(r.stdout+r.stderr);assert r.returncode==0,name
for pin in manifest['files']:assert sha(ROOT/pin['path'])==pin['sha256']
result=dict(status='accepted-source-only',source_manifest_sha256=sha(freeze),frozen_source_files=len(manifest['files']),recovered_v2_files=35,scientific_supports_exact=281,production_delta='Only plot top/height and y-title baseline; plot bottom remains 238.',retained_browser_boxes_translated=36,pairwise_nonoverlap=True,blocking_findings=[],compiled_calls=0,build_calls=0,browser_calls=0,limitation='Font translations predict clearance from retained actual measurements; a newly packaged actual browser pass remains required.')
(OUT/'audit-results-v3.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
