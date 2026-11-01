from pathlib import Path
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
import math,json
D=Path(__file__).resolve().parent;a=Decimal(json.loads((D/'lattice-results.json').read_text())['analytic_derivative100']);rows=[]
with localcontext()as ctx:
 ctx.prec=100
 for h in [5e-11,2.5e-11]:
  stored=Decimal.from_float(h);spacing=Decimal(2)**-37/(2*stored);nearest=(a/spacing).to_integral_value(rounding=ROUND_HALF_EVEN)*spacing;division_bound=Decimal.from_float(math.ulp(float(nearest)));budget=Decimal('3e-5')*max(1,abs(a),abs(nearest)+division_bound);gap=abs(nearest-a)-division_bound
  rows.append(dict(stored_h=str(stored),spacing=str(spacing),nearest_quotient=str(nearest),division_rounding_conservative_bound=str(division_bound),minimum_error_lower_bound=str(gap),budget_upper_bound=str(budget),still_impossible=gap>budget))
result=dict(identity='exact-stored-binary64-step-lattice-v1',prior_result_preserved=True,rows=rows,compiled_calls=0)
(D/'ieee-lattice-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
