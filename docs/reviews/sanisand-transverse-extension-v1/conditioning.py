"""Descriptive conditioning of saved scaled current-state residual Jacobians."""
from decimal import Decimal as D,localcontext
import gzip
import json
from pathlib import Path
import sys
from covariance import load


def condition(matrix):
 with localcontext() as ctx:
  ctx.prec=70;n=len(matrix);a=[[D.from_float(float(x)) for x in row]+[D(int(i==j)) for j in range(n)] for i,row in enumerate(matrix)]
  norm=max(sum(abs(x) for x in row[:n]) for row in a)
  for col in range(n):
   pivot=max(range(col,n),key=lambda row:abs(a[row][col]))
   if a[pivot][col]==0:return None
   a[col],a[pivot]=a[pivot],a[col];divisor=a[col][col];a[col]=[x/divisor for x in a[col]]
   for row in range(n):
    if row==col:continue
    factor=a[row][col];a[row]=[x-factor*y for x,y in zip(a[row],a[col])]
  inverse_norm=max(sum(abs(x) for x in row[n:]) for row in a)
  # Check residual independently using retained original binary64 matrix.
  residual=max(abs(sum(D.from_float(float(matrix[i][k]))*a[k][n+j] for k in range(n))-D(int(i==j))) for i in range(n) for j in range(n))
  return {'infinity_condition_estimate':str(norm*inverse_norm),'inverse_residual_at_70digits':str(residual)}


def audit(requests,responses):
 rows=[]
 for i,parent in enumerate(requests['parents']):
  base=i*116
  matrix=[[responses[base+2*col]['directional'][row]/(100000. if row<6 else 1.) for col in range(26)] for row in range(26)]
  result=condition(matrix)
  rows.append({'id':parent['id'],'lateral_stress_gap_Pa':abs(parent['current'][1]-parent['current'][2]),'scaled_residual_jacobian':matrix,'conditioning':result})
 return {'kind':'post-observation-conditioning-audit','rows':rows,'new_acceptance_gates':False,'candidate_integrations':0,
         'scope':'Actual incoming/end-state inputs from completed native steps, all26 current-state columns. Model scales p_at=100000 for stress and1 for other fields. Inversion at70digits of stored binary64 Jacobian. Not exact source conditioning, transient Newton-iterate conditioning, full-update tangent or a cause certificate.'}


if __name__=='__main__':
 data=load(Path(sys.argv[1]));response_path=Path(sys.argv[2]);text=gzip.decompress(response_path.read_bytes()).decode() if response_path.suffix=='.gz' else response_path.read_text()
 print(json.dumps(audit(data,[json.loads(line) for line in text.splitlines()]),indent=2))
