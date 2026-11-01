"""Frozen all-state controller assessment; a failed protocol remains failed."""
import json,math,sys
from pathlib import Path
from supplement import base,ref
B=Path(__file__).resolve().parent;path=Path(sys.argv[1]);req=json.loads((B/'public-requests.json').read_text());raw=json.loads(path.read_text());assert raw['request_sha256']==base.sha(B/'public-requests.json')
assert [r['name'] for r in raw['cases']]==[r['name'] for r in req['cases']]
reports=[]
for c,row in zip(req['cases'],raw['cases']):
 o=json.loads(row['stdout']);issues=[];worst=0.;boundary=0.
 if o['ok']!=c['expected_ok']:issues.append(o['message'])
 if len(o.get('points',[]))!=c['steps']+1:issues.append('incomplete path')
 points=o.get('points',[])
 if points:
  assert points[0]['state']==c['initial']
  assert all(len(x['state'])==7 and len(x['strain'])==6 and all(math.isfinite(v) for v in x['state']+x['strain']) for x in points)
  for old,new in zip(points,points[1:]):
   if new['substeps']!=1:issues.append('subdivided increment requires independent accepted-fraction trace');continue
   h=new['control']-old['control'];p=c['protocol']
   if p in (0,2,4):de=[h,0.,0.,0.,0.,0.];de[1]=de[2]=(h if p==4 else -.5*h if p==2 else 0.)
   else:de=[a-b for a,b in zip(new['strain'],old['strain'])]
   ex=ref.expected(old['state'],de)
   err=max(abs(a-b)/max(1000. if i<6 else 1.,abs(b)) for i,(a,b) in enumerate(zip(new['state'],ex)));worst=max(worst,err)
   if p==1:boundary=max(boundary,abs(.5*(new['state'][1]+new['state'][2])-100000)/100000)
   if p==3:boundary=max(boundary,abs(new['state'][0]-.5*(new['state'][1]+new['state'][2])-new['control'])/100000,abs(sum(new['strain'][:3])))
   if p==2:boundary=max(boundary,abs(sum(new['strain'][:3])),abs(new['state'][6]-c['initial'][6]))
 if worst>req['policy']['state_relative_budget']:issues.append('source finite-law error '+str(worst))
 if boundary>req['policy']['controller_relative_budget']:issues.append('controller boundary error '+str(boundary))
 reports.append(dict(name=c['name'],passed=not issues,returned_ok=o['ok'],issues=issues,points=len(points),source_error=worst,boundary_error=boundary))
r=json.loads(raw['reference_pressure']['stdout']);assert r['ok'];expected=req['reference_pressure']['expected'];err=max(abs(a-b)/max(1000. if i<6 else 1.,abs(b)) for i,(a,b) in enumerate(zip(r['state'],expected)))
report=dict(passed=all(r['passed'] for r in reports) and err<=2e-10,backend=raw['backend'],raw_sha256=base.sha(path),cases=reports,pressure_reference_conversion_error=err)
base.dump(path.with_name(path.stem+'-assessment.json'),report);print(json.dumps(report,indent=2));sys.exit(0 if report['passed'] else 1)
