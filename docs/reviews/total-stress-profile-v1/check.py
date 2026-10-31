"""Receipt/source-anchor checks only: no Atlas import, material or backend call."""
import argparse,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);args=a.parse_args()
pins=json.loads((P/'source-pins.json').read_text())['files']
for n,h in pins.items():assert sha(args.root/n)==h,n
m=json.loads((P/'source-map.json').read_text());anchors=0
for e in m['entries']:
 lines=(args.root/e['path']).read_text().splitlines()
 for a in e['anchors']:
  assert a['lines'],(e['path'],a['text'])
  assert [i for i,line in enumerate(lines,1)if a['text']in line]==a['lines'],(e['path'],a['text'])
  anchors+=1
g=json.loads((P/'prospective-gates.json').read_text());assert g['status']=='not_executed'and g['numerical_tolerances_added']is False
for n,h in json.loads((P/'manifest.json').read_text())['files'].items():assert sha(P/n)==h,n
print(json.dumps({'source_files':len(pins),'mapped_paths':len(m['entries']),'source_anchors':anchors,'prospective_gate_groups':len(g['groups']),'material_calls':0,'backend_calls':0,'checks':'receipt and source anchors only; implementation gates not executed'},indent=2))
