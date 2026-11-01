"""Prospectively frozen independent-reference and transaction assessor."""
import json,math,sys
from pathlib import Path
from decimal import Decimal as D,localcontext
P=Path(__file__).parent

def assess(text,refs):
 rows=[json.loads(line) for line in text.splitlines()]
 assert len(rows)==len(refs['cases'])+1
 summary=rows[-1];assert summary=={'summary':True,'cases':len(refs['cases']),'nonfinite_checks':1404,'controls_pass':1}
 checks=0;success=0;failure=0;worst=D(0)
 with localcontext() as ctx:
  ctx.prec=500
  eps=D(2)**-52;tiny=D(2)**-1073
  seeds=[[D.from_float(float.fromhex(v)) for v in row] for row in refs['seeds']]
  norms=[sum(v*v for v in seed).sqrt() for seed in seeds]
  for index,(row,case) in enumerate(zip(rows,refs['cases'])):
   assert row['index']==index and row['classifier_ok']==1
   assert row['repeated']==list(map(int,case['repeated'])),case['id']
   assert all(row[k]==1 for k in ('double_jet_parity','model_structure','history_structure','history_rollback','history_recovery')),case['id']
   values=[D.from_float(float.fromhex(v)) for v in case['mandel_hex']];norm=sum(v*v for v in values).sqrt()
   vbound=512*eps*norm+tiny
   def close(got,target,bound):
    nonlocal checks,worst
    assert type(got) in (int,float) and math.isfinite(got)
    err=abs(D.from_float(float(got))-D(target));assert err<=bound,(case['id'],str(err),str(bound))
    checks+=1;worst=max(worst,err/bound if bound else 0)
   for key,expected in zip(('hi','lo'),case['extremes']):
    actual=row[key];assert (actual is not None)==expected['ok'],(case['id'],key,expected['ok'])
    if actual is None:failure+=1;continue
    success+=1;close(actual['value'],expected['value'],vbound)
    assert len(actual['derivatives'])==38 and len(expected['derivatives'])==38
    gap=D(expected['selected_gap']);conditioning=max(D(1),norm/gap)
    for got,target,hnorm in zip(actual['derivatives'],expected['derivatives'],norms):
     close(got,target,2048*eps*conditioning*hnorm+tiny)
   hi,lo=case['extremes']
   both=hi['ok'] and lo['ok']
   gapvalue=D(hi['value'])-D(lo['value']) if both else D(0)
   representable=both and abs(gapvalue)<=D.from_float(sys.float_info.max)
   assert bool(row['model_ok'])==representable,(case['id'],'model')
   assert bool(row['history_ok'])==representable,(case['id'],'history')
   if representable:
    close(row['model']['value'],gapvalue,2*vbound+eps*abs(gapvalue))
    close(row['history_value'],gapvalue,2*vbound+eps*abs(gapvalue))
    assert len(row['model']['derivatives'])==38
    cond=max(D(1),norm/D(hi['selected_gap']),norm/D(lo['selected_gap']))
    for got,a,b,hnorm in zip(row['model']['derivatives'],hi['derivatives'],lo['derivatives'],norms):
     close(got,D(a)-D(b),4096*eps*cond*hnorm+tiny)
 return {'pass':True,'cases':len(refs['cases']),'successful_extrema':success,'expected_failed_extrema':failure,'accuracy_checks':checks,'nonfinite_checks':1404,'worst_error_over_bound':str(worst)}

if __name__=='__main__':
 refs=json.loads((P/'references.json').read_text())
 print(json.dumps(assess(Path(sys.argv[1]).read_text(),refs),indent=2))
