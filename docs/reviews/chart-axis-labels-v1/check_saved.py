from pathlib import Path
import json,hashlib,subprocess,math
p=Path(__file__).resolve().parent;r=p.parents[2]
manifest=json.loads((p/'manifest.json').read_text())
for name,digest in manifest.items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
inputs=json.loads((p/'saved-inputs.json').read_text())
for name,digest in inputs.items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==digest,name
result=subprocess.run(['node',str(p/'test_labels.mjs')],capture_output=True,text=True,check=True)
labels=json.loads(result.stdout)
samples=json.loads((p/'saved-points.json').read_text())
expected=[]
for name,pts in samples.items():
 for channel,key in [('stress',lambda x:x['state'][0]/1000),('strain',lambda x:x['strain'][0]*100),('rate',lambda x:x['strain_rate'][0])]:
  expected.append({'id':name+'-'+channel,'points':[[x['time'],key(x)]for x in pts if key(x)is not None]})
expected.extend([{'id':'tiny','points':[[0,-1e-12],[1,1e-12]]},{'id':'wide','points':[[0,-1.234e-290],[1,1.234e-290]]},{'id':'ordinary','points':[[0,0],[100,-300],[200,400]]},{'id':'empty','points':[]}])
def axis(values):
 if not values:return 0,1
 lo,hi=min(values),max(values)
 pad=max(abs(lo)*.05,1e-3)if lo==hi else(hi-lo)*.07
 return lo-pad,hi+pad
for name in ['prior-mobile','candidate-mobile','candidate-desktop']:
 observation=json.loads((p/'browser'/f'{name}.json').read_text())
 assert observation['ready']is True and not observation.get('error')
 assert observation['documentWidth']==observation['width']
 assert observation['inputs']==expected
 assert len(observation['charts'])==16
 left,w=(62,392)if name.startswith('prior')else(82,354)
 for source,chart in zip(expected,observation['charts']):
  assert source['id']==chart['id']
  points=source['points']
  if points:
   xmin,xmax=axis([x for x,y in points]);ymin,ymax=axis([y for x,y in points])
   actual=[[float(v)for v in pair.split(',')]for pair in chart['polyline'].split()]
   assert len(actual)==len(points)
   for(x,y),(sx,sy)in zip(points,actual):
    assert math.isclose(sx,left+(x-xmin)/(xmax-xmin)*w,abs_tol=1e-10)
    assert math.isclose(sy,27+211-(y-ymin)/(ymax-ymin)*211,abs_tol=1e-10)
  else:assert chart['polyline']is None
  if name.startswith('candidate'):
   for text in chart['text']:
    assert text['font']=='11px',text
    assert text['x']>=0 and text['right']<=480,text
prior=json.loads((p/'browser/prior-mobile.json').read_text())
clipped=sum(t['x']<0 or t['right']>480 for c in prior['charts']for t in c['text'])
assert clipped==13
for mode in ['prior','candidate']:
 app=(p/f'{mode}-app.js').read_text()
 assert(p/f'{mode}-chart.js').read_text()==app[app.index('function axisRange('):app.index('function renderCharts(){')]
assert 'favicon.ico' in(p/'browser/console.txt').read_text()
print(json.dumps({'passed':True,'label_checks':labels,'prior_clipped_labels':clipped,'candidate_out_of_bounds_labels':0,'saved_points_and_rendered_coordinates_verified':True,'charts_per_view':16,'candidate_viewports':[390,1280],'shared_source_installed':False,'new_solver_calls':0,'builds':0},indent=2))
