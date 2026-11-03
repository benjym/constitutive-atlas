"""Independent analytic void-ratio correction. Stdlib only; no Atlas imports."""
from pathlib import Path
from decimal import Decimal,localcontext
from copy import deepcopy
import hashlib,json,argparse
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OLD=ROOT/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/reference-corpus-v1.json'
OLD_SHA='7d29a8cb0598b55ed4db1253eb66b4d2a3ee8798557af81348e3eb4a3573d847'
def corrected_payload():
 assert hashlib.sha256(OLD.read_bytes()).hexdigest()==OLD_SHA,'Frozen original corpus changed'
 old=json.loads(OLD.read_text());new=deepcopy(old)
 new['identity']='controlled-time-independent-corpus-v2-trace-correction'
 # e_dot=-(1+e)*tr(D) implies log((1+e_end)/(1+e0))=-tr(delta strain).
 # Mandel shear components are off-diagonal; they do not contribute to trace.
 with localcontext() as ctx:
  ctx.prec=80
  for c in new['cases']:
   increment=[Decimal(str(c['controls_end']['strain'][i]))-Decimal(str(c['controls']['strain'][i])) for i in range(3)]
   c['expected_state']['e']=str((1+Decimal(str(c['state']['e'])))*(-sum(increment)).exp()-1)
 return old,new
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'reference-corpus-v2.json');a=p.parse_args();old,new=corrected_payload()
 with a.output.open('x') as f:json.dump(new,f,indent=2);f.write('\n')
 print('Created',len(new['cases']),'cases; only identity and expected e corrected; no equations/backend executed')
