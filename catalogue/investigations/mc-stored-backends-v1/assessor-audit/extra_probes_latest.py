"""Source-only synthetic assessor probes; no candidate evaluation."""
from pathlib import Path
import sys,copy,json
P=Path(__file__).resolve().parent;B=P/'latest';sys.path.insert(0,str(B));import assess as a
s=(B/'preflight.py').read_text();scope={'__file__':str(B/'preflight.py'),'__name__':'source_frame_builder'};exec(s.split('result=a.run(frames);')[0],scope)
frames,rows=scope['frames'],scope['rows'];results=[]
def probe(name,mutate):
 f=copy.deepcopy(frames);mutate(f);r=a.run(f);results.append({'name':name,'rejected':not r['passed'],'failures':r['failures'][:4]})
i=next(i for i,r in enumerate(rows)if r['family']=='initial-valid')
probe('initial-unchecked-column37',lambda f:f[i]['output'][0]['derivatives'].__setitem__(37,12345.))
# Fake classifier int via JSON bool is accepted as face1 in baseline.
j=next(i for i,r in enumerate(rows)if r['id']=='certificate/face/diagonal/jet')
probe('branch-bool-as-face1',lambda f:f[j].update(branch=True))
fields=a.load(B/'trace-fields.json');tabs={x['id']:x for f in(B/'policy-audit/policy-table.json',B/'supplemental-policy-table.json')for x in a.load(f)['cases']}
site=None
for line in(B/'generated/models.hpp').read_text().splitlines():
 if line.startswith('if (!(')and 'study_failure_line='in line:site=int(line.split('study_failure_line=')[1].split(';')[0]);break
for k,(r,f)in enumerate(zip(rows,frames)):
 if r['mode']!='eval'or r['family']not in('reference','off-parent','recovery'):continue
 if tabs[r['case']]['must_succeed']or f['branch']not in(1,2,3):continue
 name=a.BRANCHES[f['branch']];ref=scope['refs'][r['case']];den=f['trace'][fields.index({'face':'ds','left':'dl','right':'dr'}[name])]
 from decimal import Decimal as D
 if ref['branches'][name]['status']=='defined'and abs(D(ref['branches'][name]['gamma']))<=4096*a.EPS*D(ref['stress_scale'])/abs(D.from_float(den)):
  def mutate(fs,k=k,name=name):
   fs[k].update(ok=False,output=[],failure_line=site);fs[k]['trace'][fields.index(name+'_gamma')]=-1e300
  probe('arbitrary-negative-selected-gamma',mutate);break
else:results.append({'name':'arbitrary-negative-selected-gamma','status':'no suitable ideal frame found; source inspection finding only'})
(P/'extra-probe-results-latest.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
