from pathlib import Path
import json,hashlib,itertools
R=Path(__file__).resolve().parents[5];O=Path(__file__).parent;B=R/'output/playwright/vibe-browser-v4';D=R/'docs/ingestion/vibe-2026/browser-qualification-v4'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
a=(D/'plot-bounds-original.js').read_text();b=(B/'plot-bounds-corrected.js').read_text();assert (B/'plot-bounds.js').read_text()==a
changes=[('height:b.height,anchor:','height:b.height,baseline:Number(el.getAttribute(\'y\')),anchor:'),('el.y>240&&el.y<270','el.baseline===257')]
for old,new in changes:assert a.count(old)==b.count(new)==1;a=a.replace(old,new)
assert a==b
source=(R/'web/app.js').read_text();assert 'const top=40,h=198' in source and "y:top+h+19,'text-anchor':xLabelLayout[i].anchor" in source and 'y:282' in source
receipt=read(B/'raw-final-plot-bounds.receipt.json');assert receipt['returncode']==0 and h(B/'raw-final-plot-bounds.log')==receipt['log_sha256']
text=(B/'raw-final-plot-bounds.log').read_text();rows=json.JSONDecoder().raw_decode(text[text.index('[{'):])[0];assert len(rows)==3
stats=[]
for row in rows:
 boxes=row['text'];assert len(boxes)==12
 xs=[t for t in boxes if t['baseline']==40+198+19];ys=[t for t in boxes if t['anchor']=='end' and t['y']<230];titles=[t for t in boxes if t['baseline'] in [17,282]];assert len(xs)==len(ys)==5 and len(titles)==2;assert len({t['text'] for t in ys})==5
 assert [t['baseline'] for t in ys]==[44,93.5,143,192.5,242]
 for t in boxes:assert t['x']>=0 and t['x']+t['width']<=480 and t['y']>=0 and t['y']+t['height']<=290
 for u,v in itertools.combinations(boxes,2):assert not (u['x']<v['x']+v['width'] and u['x']+u['width']>v['x'] and u['y']<v['y']+v['height'] and u['y']+u['height']>v['y'])
 for u,v in zip(xs,xs[1:]):assert u['x']+u['width']<=v['x']
 bad=[t for t in boxes if 240<t['y']<270];assert len(bad)==6 and bad[-1]['baseline']==282 and bad[-1]['text']=='Physical time (s)' and bad[-2]['x']+bad[-2]['width']>bad[-1]['x']
 stats.append({'chart':row['id'],'boxes':12,'x_ticks':5,'y_ticks':5,'axis_titles':2,'all_pairwise_nonoverlap_checks':66,'actual_viewbox_480x290_bounds_pass':True,'original_false_positive':'Axis title baseline282 was sixth alleged x tick because bbox top266.809 falls within240..270.'})
assert 'Overlapping x ticks ct-stress' in (B/'mobile-bounds.log').read_text()
for name in ['mobile-bounds','raw-final-plot-bounds']:
 rc=read(B/(name+'.receipt.json'));assert rc['log_sha256']==h(B/(name+'.log'))
result={'status':'accepted-source-only-harness-correction','changes':'Only add DOM y baseline observation and replace bbox-based x tick classification by source-derived baseline257. All bounds, y uniqueness, adjacent x overlap, all-pairs text overlap, curve and viewport gates byte-identical.','original_sha256':h(D/'plot-bounds-original.js'),'corrected_sha256':h(B/'plot-bounds-corrected.js'),'chart_source_sha256':h(R/'web/app.js'),'raw_bounds_sha256':h(B/'raw-final-plot-bounds.log'),'stats':stats,'total_boxes':36,'pairwise_checks':198,'blocking_findings':[],'browser_build_material_calls':0,'requires':'Coordinator actual corrected browser check; this source/saved-box audit is not that execution.','cleanup':'No resources/processes/temp trees created; original failure and raw observation retained.'};(O/'decision.json').write_text(json.dumps(result,indent=2)+'\n')
paths=[O/'audit.py',O/'decision.json',D/'plot-bounds-original.js',B/'plot-bounds.js',B/'plot-bounds-corrected.js',R/'web/app.js',D/'package-manifest.json']+[B/(n+suffix) for n in ['mobile-bounds','raw-final-plot-bounds'] for suffix in ['.log','.receipt.json']]
manifest={'files':[{'path':str(p.relative_to(R)),'sha256':h(p)} for p in paths]};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('manifest',h(O/'manifest.json'));print('decision',h(O/'decision.json'));print('corrected',h(B/'plot-bounds-corrected.js'))
