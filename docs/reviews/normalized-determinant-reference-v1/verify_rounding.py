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
 r=json.loads((packet/'references.json').read_text());f=json.loads((packet/'prospective-freeze.json').read_text());assert r['input_freeze_sha256']==sha(packet/'prospective-freeze.json');assert r['all_reference_components_resolved']and r['all_precision_gates_passed'];n=0;rat=0;irr=0;poisons=set();convergence_count=0
 base=10**512;lower=F(math.isqrt(2*base*base),base);upper=lower+F(1,base);assert lower*lower<2<upper*upper
 def audit(pair,certificate):
  nonlocal n,rat,irr
  a=F(*map(int,pair['rational']));b=F(*map(int,pair['sqrt2_coefficient']));assert certificate['certified']
  if b==0:audit_rational(a,certificate);rat+=1
  else:
   lo,hi=(a+b*lower,a+b*upper)if b>0 else(a+b*upper,a+b*lower);assert lo<hi;audit_rational(lo,certificate);audit_rational(hi,certificate);irr+=1
  n+=1
 for raw,c in zip(f['cases'],r['cases']):
  assert all(raw[k]==c[k]for k in ('id','values','seeds'))
  if c['id'].startswith('prior/invalid/seed-column-'):poisons.add(int(c['id'].rsplit('-',1)[1]));assert not c['expectation']['ok']and c['primal_expectation']['ok']
  if 'primal_rounding_certificate'in c:
   audit(c['exact_primal_component'],c['primal_rounding_certificate'])
   assert c['primal_expectation']['ok']==(not c['primal_rounding_certificate']['overflow'])
   if c['primal_expectation']['ok']:assert c['primal_expectation']['hex']==c['primal_rounding_certificate']['hex']
  if 'rounding_certificates'in c:
   assert c['rounding_certificates'][0]==c['primal_rounding_certificate']
   for pair,certificate in zip(c['exact_cartesian_algebraic_components'][1:],c['rounding_certificates'][1:]):audit(pair,certificate)
   assert c['precision_check']['passed'];convergence_count+=1
   if c['expectation']['ok']:
    assert c['expectation']['value_hex']==c['primal_rounding_certificate']['hex'];assert c['expectation']['derivatives_hex']==[v['hex']for v in c['rounding_certificates'][1:]];assert len(c['expectation']['derivatives_hex'])==38
  if not c['expectation']['ok']:assert c['expectation']['unchanged_output']
 assert poisons==set(range(38));assert n==1988 and convergence_count==50
 # Specific contract distinctions that must not disappear in a harness adapter.
 by={c['id']:c for c in r['cases']}
 for name in ['normalized/minsub-anisotropic','normalized/near-trace-cancel-finite-primal']:
  assert by[name]['primal_expectation']['ok']and not by[name]['expectation']['ok']and by[name]['expectation']['reason']=='final-derivative-overflow'
 for name in ['normalized/max-isotropic','normalized/minsub-isotropic']:
  assert by[name]['expectation']['ok']and by[name]['expectation']['derivatives_hex']==['0x0.0p+0']*38
 assert by['normalized/minsub-anisotropic-zero-seeds']['expectation']['ok']
 return {'version':'normalized-determinant-reference-v1-exact-rounding-cell-audit','references_sha256':sha(packet/'references.json'),'script_sha256':sha(Path(__file__)),'all_exact_rounding_cells_verified':True,'certified_components':n,'rational_components':rat,'irrational_components':irr,'precision_checks_passed':convergence_count,'poison_columns_verified':sorted(poisons),'primal_vs_Jet_distinctions_verified':True,'compiled_calls':0,'core_execution':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.packet);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Verified',r['certified_components'],'roundingcells;',r['rational_components'],'rational;',r['irrational_components'],'irrational')
