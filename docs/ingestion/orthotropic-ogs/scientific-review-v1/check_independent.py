"""Reviewer-only Decimal Cholesky source-compliance oracle; never runs binaries."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import json, hashlib, sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/ingestion/orthotropic-ogs'
def dec(x):
 return D.from_float(x) if isinstance(x,float) else D(x)
def source_compliance(p):
 e1,e2,e3,g12,g23,g13,n12,n23,n13=map(dec,p)
 return [[1/e1,-n12/e1,-n13/e1],[-n12/e1,1/e2,-n23/e2],[-n13/e1,-n23/e2,1/e3]], [2*g12,2*g23,2*g13]
def cholesky(A):
 L=[[D(0)]*3 for _ in range(3)]
 for i in range(3):
  for j in range(i+1):
   v=A[i][j]-sum(L[i][k]*L[j][k] for k in range(j))
   if i==j:
    assert v>0, 'not SPD'
    L[i][j]=v.sqrt()
   else:L[i][j]=v/L[j][j]
 return L
def increment(p,de):
 A,g=source_compliance(p);L=cholesky(A);y=[D(0)]*3;x=[D(0)]*3
 for i in range(3): y[i]=(dec(de[i])-sum(L[i][k]*y[k] for k in range(i)))/L[i][i]
 for i in reversed(range(3)):x[i]=(y[i]-sum(L[k][i]*x[k] for k in range(i+1,3)))/L[i][i]
 return x+[dec(de[i+3])*g[i] for i in range(3)]
def main():
 assert hashlib.sha256((ROOT/'models/research/orthotropic/orthotropic-linear-elastic-ogs.json').read_bytes()).hexdigest()=='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14'
 refs=json.loads((BASE/'execution-v1/references.json').read_text()); cases=refs['cases'];out={'oracle':'independent reviewer Decimal80 Cholesky of inspected OGS compliance; neither production cofactors nor parent Fraction oracle imported','precision':80,'cases':len(cases),'reference_scalars':0,'tangent_scalars':0,'saved_backends':{},'max_reference_difference_Pa':0.,'source_hashes_verified':0}
 for r in json.loads((BASE/'source-v1/source-receipts.json').read_text()):
  assert hashlib.sha256((ROOT/r['private_path']).read_bytes()).hexdigest()==r['sha256'];out['source_hashes_verified']+=1
 with localcontext() as ctx:
  ctx.prec=80
  for c in cases:
   if not c['ok']:continue
   v=[float(dec(a)+b) for a,b in zip(c['initial'],increment(c['parameters'],c['strain']))]
   for a,b in zip(v,c['expected_state']):
    d=abs(a-b);assert d<=1e-7,(c['id'],a,b);out['max_reference_difference_Pa']=max(out['max_reference_difference_Pa'],d);out['reference_scalars']+=1
   if c['mode']=='linearize':
    for j in range(6):
     e=[int(i==j) for i in range(6)];col=increment(c['parameters'],e)
     for i,x in enumerate(col):assert abs(float(x)-c['expected_tangent'][i][j])<=1e-6;out['tangent_scalars']+=1
  for file in sys.argv[1:]:
   rows=json.loads(Path(file).read_text());assert len(rows)==len(cases);count=reject=tangent=0;maxerr=0.;lookup={}
   for c,row in zip(cases,rows):
    assert c['id']==row['id'];r=row['response'];assert r['ok']==c['ok'];lookup[c['id']]=r
    if not c['ok']:
     reject+=1
     if 'state' in r:assert r['state']==c['initial']
     continue
    assert len(r['state'])==6 and r['model']=='orthotropic-linear-elastic-ogs'
    incoming=lookup[c['previous']]['state'] if c.get('previous') else c['initial']
    want=[float(dec(a)+b) for a,b in zip(incoming,increment(c['parameters'],c['strain']))]
    for a,b in zip(r['state'],want):
     d=abs(a-b);assert d<=5e-10+2e-11*max(c['parameters'][:6]),(c['id'],d);count+=1;maxerr=max(maxerr,d)
    if c['mode']=='linearize':
     assert r['tangent_ok'] and len(r['state_tangent'])==6 and all(len(row)==6 for row in r['state_tangent'])
     for j in range(6):
      col=increment(c['parameters'],[int(i==j) for i in range(6)])
      for i,x in enumerate(col):assert abs(r['state_tangent'][i][j]-float(x))<=1e-7+2e-10*max(c['parameters'][:6]);tangent+=1
   out['saved_backends'][str(file)]={'cases':len(rows),'state_scalars':count,'tangent_scalars':tangent,'rejections':reject,'max_state_error_Pa':maxerr,'raw_sha256':hashlib.sha256(Path(file).read_bytes()).hexdigest()}
 print(json.dumps(out,indent=2));return out
if __name__=='__main__':main()
