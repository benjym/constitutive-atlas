"""Source-only translation of retained real-font boxes; no browser execution."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
raw=P/'raw-plot-bounds-browser-v3.log'
text=raw.read_text();charts,_=json.JSONDecoder().raw_decode(text.split('### Result\n',1)[1]);rows=[]
for chart in charts:
    title=chart['text'][-1]; first=chart['text'][0]
    assert title['y']<0 and title['x']<first['x']+first['w'] and title['x']+title['w']>first['x']
    title_top=title['y']+2 # baseline15 ->17
    title_bottom=title_top+title['h']
    tick_top=first['y']+13 # plot top27 ->40
    assert title_top>=0 and tick_top-title_bottom>=5
    rows.append({'chart':chart['id'],'original_title_top':title['y'],'amended_title_top':title_top,'amended_title_bottom':title_bottom,'amended_top_tick_top':tick_top,'gap':tick_top-title_bottom})
assert len(rows)==3
(P/'vertical-clearance-proof-v3.json').write_text(json.dumps({'kind':'retained-real-font-box-translation-v3','raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'old_plot_bottom':27+211,'new_plot_bottom':40+198,'browser_calls':0,'cases':rows},indent=2)+'\n')
print(json.dumps({'translated_boxes':len(rows),'minimum_gap':min(r['gap'] for r in rows),'browser_calls':0}))
