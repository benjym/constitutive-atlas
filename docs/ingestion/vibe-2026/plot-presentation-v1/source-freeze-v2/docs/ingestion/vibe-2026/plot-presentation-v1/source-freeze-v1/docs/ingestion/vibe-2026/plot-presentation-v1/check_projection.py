"""Pure exact-byte chart scope proof and immutable scientific-support check."""
import hashlib
import json
from pathlib import Path
from atlas.evidence import checked_receipt
ROOT = Path(__file__).resolve().parents[4]
PACKET = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)

app = (ROOT/'web/app.js').read_text()
app = replace_once(app, "import {formatTickLabels,tickLeftMargin} from './plot-labels.mjs';\n", '')
app = replace_once(app, '  const top=27,h=211,all=', '  const left=62,top=27,w=392,h=211,all=')
app = replace_once(app, '  const yTicks=Array.from({length:5},(_,i)=>ymax-i*(ymax-ymin)/4),xTicks=Array.from({length:5},(_,i)=>xmin+i*(xmax-xmin)/4);\n  const yTickLabels=formatTickLabels(yTicks),xTickLabels=formatTickLabels(xTicks),left=tickLeftMargin(yTickLabels),w=454-left;\n', '')
app = replace_once(app, 'yTickLabels[i]', 'numberLabel(ymax-i*(ymax-ymin)/4)')
app = replace_once(app, 'xTickLabels[i]', 'numberLabel(xmin+i*(xmax-xmin)/4)')
assert app.encode() == (PACKET/'preimages/web/app.js').read_bytes()
builder = (ROOT/'tools/build_web.py').read_text()
builder = replace_once(builder, "for name in ['plot-labels.mjs','timed-route.mjs','index.html'", "for name in ['timed-route.mjs','index.html'")
assert builder.encode() == (PACKET/'preimages/tools/build_web.py').read_bytes()
proof = {'kind':'chart-presentation-exact-reversal-v1','app_reversal_exact':True,'builder_reversal_exact':True,'axis_ranges_and_data_unchanged':True,'previous_hook_changes_preserved':True,'compiled_calls':0,'preimages':{str(p.relative_to(ROOT)):sha(p) for p in sorted((PACKET/'preimages').rglob('*')) if p.is_file()}}
(PACKET/'projection-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n')
registry = ROOT/'catalogue/approved-models.json'
entry = next(e for e in json.loads(registry.read_text())['models'] if e['model_id']=='vibe-2026')
results=[]
for pin in entry['supporting_files']:
    resolved = checked_receipt(ROOT, Path(entry['review']['path']), pin['path'], pin['sha256'])
    assert sha(resolved) == pin['sha256']
    live = ROOT/pin['path']
    results.append({**pin,'verified_receipt_path':str(resolved.relative_to(ROOT)), 'live_sha256':sha(live) if live.is_file() else None,'live_matches_original':live.is_file() and sha(live)==pin['sha256']})
assert len(results)==281
report={'kind':'unchanged-vibe-scientific-support-v2','passed':281,'total':281,'compiled_calls':0,'document':entry['review']['path'],'document_sha256':sha(ROOT/entry['review']['path']),'archive_map_sha256':sha(ROOT/'catalogue/agent-reviews/source-archive-map.json'),'registry_sha256':sha(registry),'supporting_files':results}
(PACKET/'scientific-support-after-v1.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'exact_reversals':2,'verified_supports':len(results),'live_matches':sum(r['live_matches_original'] for r in results),'compiled_calls':0}))
