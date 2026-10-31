"""Freeze determinant inputs/seeds and accuracy policy; no determinant/reference evaluation."""
import argparse,copy,hashlib,json,math
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def literal(x):return format(x,'.17g')if not isinstance(x,str)else x
def seeds():return [[literal(1. if c==r else 0.)if c<6 else '0'if c==6 else literal((((r+1)*(c+3))%11-5)/8)for c in range(38)]for r in range(6)]
def build(root):
 path=root/'catalogue/investigations/clay2005-rates-v3/protocol.json';p=json.loads(path.read_text());rows=[]
 def add(name,v,tags,seed=None,**extra):rows.append({'id':name,'values':[literal(x)for x in v],'seeds':seed or seeds(),'tags':tags,**extra})
 actual=['finite_only/tiny-positive-interior','finite_only/margin-above','finite_only/scaled-positive-1.0','finite_only/scaled-positive-1e+50','finite_only/oblique-tiny-positive','finite_only/shear-near-positive-interior']
 for name in actual:
  c=next(c for c in p['cases']if c['id']==name);add('actual/'+name,c['args'][2].split(',')[:6],['actual-clay-boundary'],origin={'protocol':str(path.relative_to(root)),'case_id':name})
 for name,v in [('sphere',[1,1,1,0,0,0]),('diagonal',[2,3,5,0,0,0]),('negative-definite',[-2,-3,-5,0,0,0]),('indefinite',[-2,3,5,.2,-.3,.4]),('mixed',[4,3,2,1,-.5,.75]),('zero',[0]*6)]:add('regular/'+name,v,['regular'])
 for name in ['accuracy/rotated-mixed','finite_only/oblique-safe']:
  c=next(c for c in p['cases']if c['id']==name);add('rounded-covariance/'+name,c['args'][2].split(',')[:6],['actual-rounded-covariance'],origin={'protocol':str(path.relative_to(root)),'case_id':name})
 add('exact-covariance/signed-reflection',[4,3,2,-1,.5,.75],['exact-reflection'],primal_equal_to='regular/mixed')
 for name,v in [('uniform-small',[1e-100,1e-100,1e-100,1e-100,2e-100,-1e-100]),('uniform-large',[1e100,1e100,1e100,1e100,2e100,-1e100]),('anisotropic',[1e200,1e-200,1,0,0,0]),('mixed-small',[1e-200,1e-100,1e100,0,0,0]),('mixed-sign',[1e100,-1e100,1e-100,1e20,-1e-20,1e-100])]:add('scale/'+name,v,['scale','anisotropic'])
 for name,v in [('half-minsub',[2.**-537,2.**-538,1,0,0,0]),('three-half-minsub',[3*2.**-537,2.**-538,1,0,0,0]),('five-half-minsub',[5*2.**-537,2.**-538,1,0,0,0]),('negative-half-minsub',[-2.**-537,2.**-538,1,0,0,0]),('upper-normal',[math.nextafter(1.,math.inf),1.5,1,0,0,0]),('negative-upper-normal',[-math.nextafter(1.,math.inf),1.5,1,0,0,0])]:add('rational-tie/'+name,v,['rational-midpoint'])
 add('special/rank-one',[3,0,0,0,0,0],['exact-rank-deficient'])
 add('special/rank-two',[3,5,0,0,0,0],['exact-rank-deficient'])
 add('special/huge-rank-one',[2.**900,0,0,0,0,0],['exact-rank-deficient','intermediate-overflow'])
 add('special/primal-overflow',[2.**600]*3+[0]*3,['rounded-primal-overflow'])
 add('special/derivative-overflow',[2.**600,2.**600,0,0,0,0],['rounded-derivative-overflow'])
 s=seeds()
 for i in range(6):s[i][37]='0'
 s[0][37]=literal(2.**600);s[1][37]=literal(-2.**600)
 add('special/directional-cancellation',[2.**500,2.**500,1,0,0,0],['derivative-cancellation','intermediate-overflow'],s)
 add('special/signed-zero',[-0.,0.,-0.,0.,-0.,0.],['signed-zero','canonical-positive-zero'])
 s=[[literal(((-1)**r)*math.ulp(0.))for c in range(38)]for r in range(6)]
 add('special/minsubnormal-seeds',[1,1,1,0,0,0],['subnormal-derivatives'],s)
 for i in range(6):
  v=[1,1,1,0,0,0];v[i]=['NaN','Infinity','-Infinity'][i%3];add('invalid/input-'+str(i),v,['nonfinite-input'],invalid_location={'kind':'value','row':i})
 for c in range(38):
  s=seeds();r=c%6;s[r][c]=['NaN','Infinity','-Infinity'][c%3];add('invalid/seed-column-'+str(c),[1,1,1,0,0,0],['nonfinite-seed'],s,invalid_location={'kind':'seed','row':r,'column':c})
 assert len(rows)==78 and len({r['id']for r in rows})==78
 return {'version':'symmetric-determinant-reference-v1-prospective-freeze','files':{str(path.relative_to(root)):sha(path)},'policy':{'input_layout':'Mandel[xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz]; seeds rows6 columns38','input_semantics':'each finite literal parsed to binary64 then exact integer ratio, offdiag Cartesian=u/sqrt2; NaN/Infinity strings are intentional invalid-input tokens, not JSON numbers','output_contract':'one bool status; success correctly-rounded-nearest-even finite binary64 primal and all38directional derivatives; reject any nonfinite6input/228seed values or rounded primal/derivative overflow; failed output unchanged; successful rounded zeros canonical+0','precision_digits':[160,320],'convergence':'relative-scaled Cartesian determinant and all38cofactor-dot directions difference <=1e-120 for160/320; exact rational midpoint cases use exact Cartesian rational/radical field to settle ties, not decimal approximations','rigorous_rounding':'independent Cartesian exact Fraction pairs a+b*sqrt2, determinant by ordinary3x3cofactor expansion and derivative full cofactor:seed. Enclose sqrt2 with integerisqrt rational lower/upper bounds at512decimaldigits. Both enclosure endpoints must round to same binary64; pure rational values use exact Fraction rounding. Otherwise retain unresolved reference failure; no guess or widening','acceptance':'exact hexadecimal equality to frozen finite primal/all38derivatives, Boolean status exact; rejectcases check unchanged output sentinel in later driver; signed-zero bits checked; no ULP/relative relaxation','covariance':'rounded rotated tensors are independent actual inputs; no exact covariance identity claimed. Exact signed reflection primitive primal agrees; directional covariance requires reflected seeds, not unrelated same numerical seeds','scope':'primitive only; no material rates, support changes, compiled execution or scientific admission'},'cases':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=build(a.root);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(len(r['cases']),sha(a.output))
