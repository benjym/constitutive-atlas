"""Independent pure source audit. Never invokes packaging, browser or material."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PACKET=ROOT/'docs/ingestion/vibe-2026/plot-presentation-v1'
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
freeze=PACKET/'source-manifest-v2.json'
assert sha(freeze)=='a099633d74beee299419d487f917feffa478c169eecb693db08b7d19f10a45ba'
manifest=json.loads(freeze.read_text())
for pin in manifest['files']:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
old=json.loads((PACKET/'source-manifest-v1.json').read_text())
recovery=json.loads((PACKET/'v1-recovery.json').read_text())['files']
assert len(old['files'])==len(recovery)==14
for pin in old['files']:
    row=next(row for row in recovery if row['original']==pin['path'])
    assert row['sha256']==pin['sha256']==sha(ROOT/row['retained'])

def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)
expected=(PACKET/'preimages/web/app.js').read_text()
expected="import {formatTickLabels,tickLeftMargin,layoutHorizontalTickLabels} from './plot-labels.mjs';\n"+expected
expected=once(expected,'  const left=62,top=27,w=392,h=211,all=','  const top=27,h=211,all=')
line='  const [xmin,xmax]=axisRange(all.map(p=>p[0])),[ymin,ymax]=axisRange(all.map(p=>p[1]),true);\n'
expected=once(expected,line,line+'''  const yTicks=Array.from({length:5},(_,i)=>ymax-i*(ymax-ymin)/4),xTicks=Array.from({length:5},(_,i)=>xmin+i*(xmax-xmin)/4);
  const yTickLabels=formatTickLabels(yTicks),xTickLabels=formatTickLabels(xTicks),left=tickLeftMargin(yTickLabels),w=454-left;
  const xLabelLayout=layoutHorizontalTickLabels(xTickLabels,Array.from({length:5},(_,i)=>left+i*w/4));
''')
expected=once(expected,'numberLabel(ymax-i*(ymax-ymin)/4)','yTickLabels[i]')
expected=once(expected,"'text-anchor':'middle'},numberLabel(xmin+i*(xmax-xmin)/4)","'text-anchor':xLabelLayout[i].anchor},xLabelLayout[i].text")
assert expected==(ROOT/'web/app.js').read_text()
expected=(PACKET/'preimages/tools/build_web.py').read_text()
expected=once(expected,"for name in ['timed-route.mjs','index.html'","for name in ['plot-labels.mjs','timed-route.mjs','index.html'")
assert expected==(ROOT/'tools/build_web.py').read_text()
# Existing hook files and defaults survive; the only hook-pinned file changed
# by this patch is the builder, whose complete one-entry change is proved above.
hook=json.loads((ROOT/'docs/ingestion/vibe-2026/main-integration-v1/hook-source-manifest-v1.json').read_text())
for pin in hook['files']:
    if pin['path']=='tools/build_web.py':assert sha(PACKET/'preimages/tools/build_web.py')==pin['sha256']
    else:assert sha(ROOT/pin['path'])==pin['sha256']
review_path=Path('catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json')
review=json.loads((ROOT/review_path).read_text())
assert sha(ROOT/review_path)=='8e36c1984af615ece3ef4a05546871defbe05a64f6a483d295f9056f29f3ae99'
assert sha(ROOT/review['model']['path'])==review['model']['sha256']=='a7d3f0f61ff6654f1dc924178a3551a740ca39212a99813c2b9ce5c15b16c987'
assert len(review['artifacts'])==281
for pin in review['artifacts']:
    assert sha(checked_receipt(ROOT,review_path,pin['path'],pin['sha256']))==pin['sha256']
    assert sha(ROOT/pin['path'])==pin['sha256']
commands=[('author-tests-v2.log',['node','--test','tests/test_plot_labels.mjs']),('app-syntax-v2.log',['node','--check','web/app.js']),('independent-format-cases-v2.json',['node',str(OUT/'independent-format-cases.mjs')]),('independent-layout-cases-v2.json',['node',str(OUT/'independent-layout-cases-v2.mjs')])]
for name,argv in commands:
    result=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True)
    (OUT/name).write_text(result.stdout+result.stderr)
    assert result.returncode==0,name
for pin in manifest['files']:assert sha(ROOT/pin['path'])==pin['sha256']
result=dict(status='accepted-source-only',reviewer_run='/root/vibe_scientific_review',implementation_run='/root/vibe_capability',source_manifest=dict(path=str(freeze.relative_to(ROOT)),sha256=sha(freeze)),frozen_files=len(manifest['files']),recovered_v1_files=14,exact_forward_reconstructions=2,original_hook_source_files_checked=len(hook['files']),scientific_supports_exact=281,scientific_review_sha256=sha(ROOT/review_path),archive_map_sha256=sha(ROOT/'catalogue/agent-reviews/source-archive-map.json'),registry_sha256=sha(ROOT/'catalogue/approved-models.json'),blocking_findings=[],compiled_calls=0,build_calls=0,browser_calls=0,limits=['Horizontal labels use a deterministic subset; extreme long labels may reduce visible labels further.','Geometry uses the existing seven-unit character estimate; actual font/layout and browser acceptance remain coordinator gates.','Existing axis range arithmetic and tooltip formatting remain unchanged.'])
(OUT/'audit-results-v2.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
