"""Freeze normalized determinant cases/policy before evaluating any references."""
import argparse,copy,hashlib,json,math
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def literal(x):return x if isinstance(x,str)else format(x,'.17g')
def seeds():return [[literal(1. if c==r else 0.)if c<6 else '0'if c==6 else literal((((r+1)*(c+3))%11-5)/8)for c in range(38)]for r in range(6)]
def run(root):
 prior='docs/reviews/symmetric-determinant-reference-v1/prospective-freeze.json';p=json.loads((root/prior).read_text());rows=[]
 for c in p['cases']:
  row={k:copy.deepcopy(c[k])for k in ('values','seeds','tags')};row['id']='prior/'+c['id'];row['origin_prior_id']=c['id'];row['tags']=['prior-determinant-'+t for t in row['tags']];rows.append(row)
 def add(name,v,tags,s=None):rows.append({'id':'normalized/'+name,'values':list(map(literal,v)),'seeds':s if s is not None else seeds(),'tags':tags})
 maximum=float.fromhex('0x1.fffffffffffffp+1023');tiny=math.ulp(0.)
 add('trace-zero-det-nonzero',[1,1,-2,0,0,0],['trace-zero'])
 add('trace-zero-det-zero',[1,-1,0,0,0,0],['trace-zero','det-zero'])
 add('max-isotropic',[maximum]*3+[0]*3,['trace-overflow','det-overflow','derivatives-exact-zero'])
 add('negative-max-isotropic',[-maximum]*3+[0]*3,['negative-trace','trace-overflow','det-overflow'])
 add('minsub-isotropic',[tiny]*3+[0]*3,['det-underflow','trace-cube-underflow','derivatives-exact-zero'])
 add('negative-minsub-isotropic',[-tiny]*3+[0]*3,['negative-trace','det-underflow'])
 add('minsub-anisotropic',[tiny,tiny,2*tiny,0,0,0],['primal-finite-derivative-overflow'])
 add('minsub-anisotropic-zero-seeds',[tiny,tiny,2*tiny,0,0,0],['finite-ratio-zero-seeds'],[['0']*38 for _ in range(6)])
 add('huge-anisotropic',[maximum,maximum,maximum/2,0,0,0],['trace-overflow','det-overflow','subnormal-derivatives'])
 add('small-nonisotropic',[1e-200,2e-200,3e-200,0,0,0],['det-underflow','finite-ratio'])
 add('large-nonisotropic',[1e200,2e200,3e200,0,0,0],['det-overflow','trace-cube-overflow','finite-ratio'])
 add('near-trace-cancel-finite-primal',[1,-1,2.**-500,0,0,0],['primal-finite-derivative-overflow'])
 add('near-trace-cancel-final-overflow',[1,-1,2.**-600,0,0,0],['final-primal-overflow'])
 add('huge-cancel-trace-small',[maximum,tiny,-maximum,0,0,0],['exact-trace-cancellation','final-primal-overflow'])
 add('power2-cancel-trace-finite',[2.**500,-2.**500,1,0,0,0],['exact-trace-cancellation','finite-ratio'])
 add('rational-midpoint-positive-even',[1,1,2,0,2.**-26,0],['normalized-rational-midpoint'])
 add('rational-midpoint-positive-other',[1,1,2,0,3*2.**-26,0],['normalized-rational-midpoint'])
 add('rational-midpoint-negative',[1,-1,4,0,2.**-25,0],['normalized-rational-midpoint'])
 for oldname in ['regular/mixed','actual/finite_only/oblique-tiny-positive']:
  c=next(c for c in p['cases']if c['id']==oldname);s=[[literal(float(c['values'][r])*(1 if j%2==0 else-1))for j in range(38)]for r in range(6)];add('homogeneity/'+oldname,c['values'],['all38-exact-homogeneous-directions'],s)
 assert len(rows)==98 and len({c['id']for c in rows})==98
 return {'version':'normalized-determinant-reference-v1-prospective-freeze','files':{n:sha(root/n)for n in [prior,'docs/NORMALIZED_DETERMINANT.md']},'policy':{'mathematical_primal':'det(A)/(exact trace(A))^3 on original exact binary64 Mandelinputs, zero trace alwaysrejects','mathematical_derivative':'(Cartesian cofactor(A):E*exacttrace(A)-3det(A)*exacttrace(E))/(exacttrace(A))^4','precision_digits':[640,960],'convergence':'scaled difference640/960<=1e-200 primal/all38directions. ExactCartesian radicalfield proves exactzero components separately; those use exactzero branch in convergence comparison and retain raw Decimalresiduals. Nonzero nonconvergence remains a referencefailure, not ignored. Exact rational ties settled by exact rational roundingcell, not Decimalapproximation','rounding_certification':'exact Cartesian Fractionpairs a+b*sqrt2 divided by exactFraction tracepowers; sqrt2 enclosed byintegerisqrt rational endpoints at512decimaldigits; identical endpoint nearest-even results required, otherwise unresolvedfailure. Pure rational uses exactroundingcell. No implementation module imported/pinned','output':'compact primal_expectation ok/hex; fullJet expectation ok/value_hex/38derivatives_hex. Reject exacttracezero/nonfiniteprimal/finalprimaloverflow; Jet additionallyrejects anynonfiniteseed/finalderivativeoverflow. Allroundedzeros+0; reject leavesentireoutputunchanged','acceptance':'exact status andhexadecimalbits, norelaxtolerance. Decimalconvergence is referencevalidity gate, notcompilednumericbudget','recovery':'coordinator expands unique fixture aftereach Jet rejection with identical prior/regular/sphere successful request; no recoveryrows addedhere','coverage':'old78determinantinputs/seeds retained asindependent originaltensors plus20normalizedcontractcases; no oldexpectedvalues reused','claims':'primitive referenceonly; no Atlasimports/newcoreexecution/compiledcalls/modeldomains/wholematerialrates/scientificadmission'},'cases':rows}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',required=True,type=Path);a.add_argument('--output',required=True,type=Path);v=a.parse_args();assert not v.output.exists();r=run(v.root);v.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(len(r['cases']),sha(v.output))
