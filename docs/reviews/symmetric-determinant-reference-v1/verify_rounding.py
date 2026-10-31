"""Audit reference rounding by exact rational binary64 Voronoi cells, no oracle calls."""
import argparse,hashlib,json,math,struct
from fractions import Fraction as F
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit_rational(q,certificate):
 # Exact overflow halfway boundary: maxFinite + ulp(maxFinite)/2.
 threshold=F(2**1024-2**970)
 if certificate['overflow']:
  assert abs(q)>=threshold and (1 if q>0 else-1)==certificate['sign'];return
 x=float.fromhex(certificate['hex']);assert math.isfinite(x)
 if x==0:assert certificate['hex']=='0x0.0p+0'
 else:assert (q>0)==(x>0)
 a=abs(q);y=abs(x);bits=struct.unpack('>Q',struct.pack('>d',y))[0];even=bits%2==0
 previous=math.nextafter(y,-math.inf);following=math.nextafter(y,math.inf)
 lo=(F(previous)+F(y))/2;hi=threshold if math.isinf(following)else(F(y)+F(following))/2
 assert (lo<a<hi)or(even and a in (lo,hi)),(q,certificate)

def run(packet):
 r=json.loads((packet/'references.json').read_text());f=json.loads((packet/'prospective-freeze.json').read_text());assert r['input_freeze_sha256']==sha(packet/'prospective-freeze.json');assert r['all_reference_components_resolved']and r['all_decimal_convergence_passed']
 n=0;rat=0;irr=0;poisons=set();accepted=0
 base=10**512;lower=F(math.isqrt(2*base*base),base);upper=lower+F(1,base);assert lower*lower<2<upper*upper
 for raw,case in zip(f['cases'],r['cases']):
  assert all(raw[k]==case[k]for k in ('id','values','seeds'))
  if case['expectation']['reason']=='nonfinite-input-or-seed'if 'reason'in case['expectation']else False:
   assert any(not math.isfinite(float(s))for s in case['values']+sum(case['seeds'],[]))
   if case['id'].startswith('invalid/seed-column-'):poisons.add(int(case['id'].rsplit('-',1)[1]))
   continue
  for pair,certificate in zip(case['exact_cartesian_algebraic_components'],case['rounding_certificates']):
   a=F(*map(int,pair['rational']));b=F(*map(int,pair['sqrt2_coefficient']));assert certificate['certified']
   if b==0:audit_rational(a,certificate);rat+=1
   else:
    lo,hi=(a+b*lower,a+b*upper)if b>0 else(a+b*upper,a+b*lower);assert lo<hi;audit_rational(lo,certificate);audit_rational(hi,certificate);irr+=1
   n+=1
  if case['expectation']['ok']:
   accepted+=1;assert len(case['expectation']['derivatives_hex'])==38
   assert case['expectation']['value_hex']==case['rounding_certificates'][0]['hex']
   assert case['expectation']['derivatives_hex']==[c['hex']for c in case['rounding_certificates'][1:]]
 assert poisons==set(range(38));assert n==1326 and accepted==32
 return {'version':'symmetric-determinant-reference-v1-exact-rounding-cell-audit','references_sha256':sha(packet/'references.json'),'script_sha256':sha(Path(__file__)),'all_exact_rounding_cells_verified':True,'certified_components':n,'rational_components':rat,'irrational_components':irr,'single_poison_columns_verified':sorted(poisons),'compiled_calls':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.packet);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Exact rational rounding cells verified',r['certified_components'])
