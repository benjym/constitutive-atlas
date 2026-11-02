"""Post-observation diagnostic only; original frozen assessor remains decisive."""
import hashlib,json,pathlib,sys,math
BASE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from study import resolve

def main():
 raw=BASE/'native-attempt1.json';rows=json.loads(raw.read_text());cases=json.loads((BASE/'cases.json').read_text())['cases']
 assert len(rows)==len(cases)==136
 violations=[];comparisons=0;worst={'state':0.,'stress':0.};failed=set()
 for i,(src,row) in enumerate(zip(cases,rows)):
  assert src['id']==row['id']
  case=resolve(src,rows[:i]);response=json.loads(row['calls'][0]['stdout'])
  for point in response.get('points',[]):
   reference=next((v for v in case.get('references',[]) if abs(v['time']-point['time'])<1e-12),None)
   if reference is None:continue
   coarse=case['id']=='refinement-coarse'
   for kind,key,floor in [('state','state',.001 if coarse else 3e-7),('stress','observables',1000. if coarse else 3.)]:
    for component,(value,target) in enumerate(zip(point[key],reference[kind])):
     comparisons+=1;error=abs(value-target);bound=max(floor,2e-5*abs(target));worst[kind]=max(worst[kind],error)
     if not math.isfinite(error) or error>bound:
      failed.add(case['id']);violations.append(dict(case=case['id'],time=point['time'],kind=kind,component=component,value=value,reference=target,error=error,bound=bound))
 h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 output=dict(identity='bingham-v2-post-observation-physical-diagnostic-v1',qualification=False,reason='Supplementary exhaustive physical comparisons; frozen assessor unchanged and authoritative',raw_sha256=h(raw),cases_sha256=h(BASE/'cases.json'),assessor_sha256=h(BASE/'study.py'),diagnostic_sha256=h(pathlib.Path(__file__)),cases=len(rows),calls=sum(len(r['calls']) for r in rows),comparisons=comparisons,violating_cases=sorted(failed),violations=violations,worst_absolute_error=worst)
 (BASE/'native-attempt1-component-diagnostics.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:v for k,v in output.items() if k not in ['violations','violating_cases']},indent=2));print('Violating cases:',len(failed),'components:',len(violations))
if __name__=='__main__':main()
