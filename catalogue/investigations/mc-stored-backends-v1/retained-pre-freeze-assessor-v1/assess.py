"""Frozen prospective MC source/branch/error/transaction assessor; no Atlas import."""
from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
import json,gzip,sys,math,re,collections
P=Path(__file__).resolve().parent
EPS=D(2)**-52;SUB=D(2)**-1074
BRANCHES=['elastic','face','left','right','apex']
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def number(x):
 if type(x)not in(int,float):raise ValueError('not a wire number')
 if not math.isfinite(x):raise ValueError('nonfinite wire number')
 return D.from_float(float(x))
def hexnumber(x):return D.from_float(float.fromhex(x))
def norm(x):return sum(t*t for t in x).sqrt()
def run(observations):
 requests=load(P/'requests.json');tables={r['id']:r for file in(P/'policy-audit/policy-table.json',P/'supplemental-policy-table.json')for r in load(file)['cases']}
 refs={r['id']:r['canonical']for file in(P/'reference/reference-p360.json.gz',P/'supplemental-reference/reference-p360.json.gz')for r in load(file)['cases']}
 fields=load(P/'trace-fields.json');failing_sites={};last='dispatch'
 for line in(P/'generated/models.hpp').read_text().splitlines():
  m=re.match(r'const auto (\w+) = ',line)
  if m:last=m[1]
  m=re.search(r'study_failure_line=(\d+); return false;',line)
  if m:failing_sites[int(m[1])]=('domain'if line.startswith('if (!(')else last)
 failures=[];counts=collections.Counter();conditional=[];limited=[];worst=D(0)
 def fail(r,reason,**kw):failures.append(dict(id=r['id'],reason=reason,**kw))
 def check_norm(r,actual,expected,budget,label,natural=None):
  nonlocal worst
  err=norm([a-b for a,b in zip(actual,expected)]);counts[label]+=1
  if budget>0:worst=max(worst,err/budget)
  if err>budget:fail(r,'source-error',channel=label,error=str(err),budget=str(budget))
  if natural and budget/abs(natural)>D('.01'):limited.append(dict(id=r['id'],channel=label,budget_over_natural=str(budget/abs(natural))))
 if len(observations)!=len(requests):fail({'id':'wire'},'row-count',actual=len(observations),expected=len(requests))
 with localcontext()as ctx:
  ctx.prec=220
  for r,o in zip(requests,observations):
   try:
    if o.get('id')!=r['id']or o.get('mode')!=r['mode']or o.get('kind')!=r['kind']:fail(r,'wire-identity');continue
    if type(o.get('ok'))is not bool:fail(r,'status-type');continue
    if o.get('input_unchanged')is not True:fail(r,'input-mutation')
    family=r['family'];ok=o['ok'];out=o.get('output');counts[family]+=1
    if not isinstance(out,list):fail(r,'output-shape');continue
    if family in('nonfinite','invalid-parameter','initial-reject','solver-initial-reject'):
     if ok:fail(r,'expected-rejection')
     if r['mode']=='eval'and out:fail(r,'failed-evaluation-scratch-not-discarded')
     if family=='solver-initial-reject'and [number(x['value'])for x in out]!=list(map(hexnumber,r['parent'])):fail(r,'initial-parent-rollback')
     continue
    if family.startswith('solver-')and r['mode']=='transaction':
     t=o.get('transaction',{})
     if ok:fail(r,'transaction-must-fail')
     for name in('returned_parent','committed_unchanged','recovery_ok','recovery_matches_fresh'):
      if t.get(name)is not True:fail(r,'transaction-'+name)
     for name in('committed_state','recovery_state','fresh_state'):
      if len(t.get(name,[]))!=6 or any(number(x)!=0 for x in t[name]):fail(r,'transaction-'+name+'-not-known-zero-state')
     if len(out)!=6 or any(number(x['value'])!=0 for x in out):fail(r,'transaction-return-not-known-zero-state')
     if family=='solver-rollback':
      if t.get('tentative_ok')is not False or t.get('tentative_changed')is not True or t.get('trial_iterations')!=1 or t.get('iterations')!=1 or t.get('rejected',0)<1 or not o.get('message','').startswith('integration failed'):fail(r,'missing-tentative-newton-rollback-witness')
     continue
    if family in('initial-valid','initial-unchecked'):
     if not ok or len(out)!=6:fail(r,'initial-analytic-success-required');continue
     if [number(x['value'])for x in out]!=list(map(hexnumber,r['current'])):fail(r,'analytic-zero-trial-residual')
     for k,x in enumerate(out):
      ds=x.get('derivatives',[])
      if len(ds)!=38:fail(r,'all38-directions-required');continue
      for j in range(6):
       if number(ds[j])!=D(int(j==k)):fail(r,'current-basis-identity')
     continue
    table=tables[r['case']];ref=refs[r['case']];trace=o.get('trace',[])
    if len(trace)!=len(fields):fail(r,'trace-shape');continue
    tr={name:(None if value is None else number(value))for name,value in zip(fields,trace)}
    for name,(low,high)in table['trace_envelopes'].items():
     if tr[name]is None:
      if ok:fail(r,'missing-success-trace',field=name)
     elif not D(low)<=tr[name]<=D(high):fail(r,'trace-outside-canonical-envelope',field=name,actual=str(tr[name]),enclosure=[low,high])
    branch=o.get('branch',-1)
    if branch not in range(5):fail(r,'missing-actual-branch');continue
    branch=BRANCHES[branch]
    if branch not in table['eligible_branches']:fail(r,'branch-not-prospectively-eligible',branch=branch)
    if all(tr[k]is not None for k in('ftrial','class_ga','class_gs','gsl','gsr','gla','gra')):
     selected='elastic'if tr['ftrial']<=0 else'apex'if tr['class_ga']>=max(tr['gla'],tr['gra'])else'face'if tr['class_gs']<min(tr['gsl'],tr['gsr'])else'left'if tr['gsl']<tr['gsr']else'right'
     if branch!=selected:fail(r,'trace-branch-control-disagrees')
    elif ok:fail(r,'incomplete-success-classifier')
    if not ok:
     if r['mode']=='eval'and out:fail(r,'failed-evaluation-scratch-not-discarded')
     if r['mode']=='solve'and [number(x['value'])for x in out]!=list(map(hexnumber,r['parent'])):fail(r,'solver-failed-state-not-parent')
     if table['must_succeed']:fail(r,'required-success-rejected');continue
     witness=None;site=failing_sites.get(o.get('failure_line'))
     if branch in('face','left','right')and all(tr[k]is not None for k in('v1','v2','v3')):
      vals=[tr['v1'],tr['v2'],tr['v3']];gap=min(vals[0]-vals[1],vals[1]-vals[2])if branch=='face'else vals[1]-vals[2]if branch=='left'else vals[0]-vals[1]
      threshold=1024*EPS*norm(vals)*(1+4096*EPS)+2*SUB
      if site in(branch+'_gamma','returned_source')and gap<=threshold:witness='selected-operation-failure-with-compatible-gap'
      gamma=tr.get(branch+'_gamma')
      if site=='domain'and gamma is not None and gamma<0:
       canonical=ref['branches'][branch]
       # Independent source margin must also be near zero; actual negative is never blanket permission.
       denname={'face':'ds','left':'dl','right':'dr'}[branch];den=tr[denname]
       if canonical['status']=='defined'and den and abs(D(canonical['gamma']))<=4096*EPS*D(ref['stress_scale'])/abs(den):witness='near-zero-selected-negative-multiplier'
     if witness is None:fail(r,'conditional-rejection-without-allowed-witness',site=site,branch=branch)
     conditional.append(dict(id=r['id'],outcome='rejected-coverage-gap',witness=witness,branch=branch,site=site));continue
    counts['successes']+=1
    if not table['must_succeed']:conditional.append(dict(id=r['id'],outcome='successful-conditional-branch',branch=branch))
    target=ref['branches'][branch]
    if target['status']!='defined':fail(r,'undefined-fixed-branch-reference');continue
    if len(out)!=6:fail(r,'successful-output-size');continue
    budget=D(table['branches'][branch]['value_norm_budget']);actual=[number(x['value'])for x in out]
    expected=list(map(D,target['returned_atlas']))if r['mode']=='solve'else[hexnumber(v)-D(w)for v,w in zip(r['current'],target['returned_atlas'])]
    if r['mode']=='solve':
     budget+=D(6).sqrt()*D('2e-10')*hexnumber(r['parameters']['p_ref'])
     if o.get('substeps')!=1 or o.get('iterations',0)<1:fail(r,'solver-diagnostics-not-one-unsplit-step')
    check_norm(r,actual,expected,budget,'values',D(ref['stress_scale']))
    if r['kind']=='jet':
     for j in range(38):
      if any(len(x.get('derivatives',[]))!=38 for x in out):fail(r,'all38-directions-required');break
      a=[number(x['derivatives'][j])for x in out];b=list(map(D,target['directions'][j]['residual']));bd=D(table['branches'][branch]['direction_norm_budgets'][j]);check_norm(r,a,b,bd,'directions',D(ref['direction_scales'][j]))
      if j<6 and a!=[D(int(k==j))for k in range(6)]:fail(r,'current-basis-identity',column=j)
    if table.get('mixed_component_gate'):
     # Off-parent mixed rows keep their middle and shear current zero to avoid unobservable cancellation.
     mid=abs(actual[1]-expected[1]);bound=128*EPS*abs(expected[1])+2*SUB;counts['mixed_middle_checks']+=1
     if mid>bound:fail(r,'lost-mixed-middle-component',error=str(mid),budget=str(bound))
     if any(actual[k]!=0 for k in(3,4,5)):fail(r,'mixed-exact-zero-shears')
   except Exception as exc:fail(r,'invalid-frame',exception=repr(exc))
 return {'identity':'mc-stored-backends-assessment-v1','passed':not failures,'requests':len(requests),'counts':dict(counts),'failures':failures,'conditional_outcomes':conditional,'resolution_limited_comparisons':limited,'maximum_error_over_budget':str(worst),'parameter_jet_tested':False,'scientific_admission':False}
if __name__=='__main__':
 observations=[json.loads(line)for line in Path(sys.argv[1]).read_text().splitlines()];result=run(observations);print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed']else 1)
