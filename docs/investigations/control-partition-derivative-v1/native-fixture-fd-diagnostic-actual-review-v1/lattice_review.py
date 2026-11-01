"""Independent exact-rational IEEE proof and direct matrix analytic derivative."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,math
from fractions import Fraction as F
from decimal import Decimal as Q,localcontext
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=Path(__file__).resolve().parent;actual=json.loads((D/'actual-checks.json').read_text())['actual'];A=C/'native-fixture-fd-analysis-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=json.loads((A/'manifest.json').read_text());assert sha(A/'manifest.json')=='8468d0d4629063470f19e3d3351514a63d34d7c767c3d21928f69e812e168004'
for n,h in manifest.get('files',manifest).items():assert sha(A/n)==h,n
ad=F(actual['ad']);tau=F(3e-5);ulp=F(1,2**37);epsilon=F(1,10**12);rows=[]
# If a rounded FD can pass, it is near235; then one ulp for quotient rounding
# plus one ulp of the budget and exact Sterbenz subtraction is far below epsilon.
assert epsilon>4*F(math.ulp(actual['ad']))+4*F(math.ulp(3e-5*abs(actual['ad'])))
for h in [actual['h'],actual['h']/2]:
 spacing=ulp/(2*F(h));low=(ad-epsilon)/(1-tau);high=ad*(1-tau)+epsilon
 first=math.ceil(low/spacing);last=math.floor(high/spacing);assert first>last
 nearest=round(ad/spacing);quotient=nearest*spacing;division_bound=F(math.ulp(float(quotient)));gap=abs(quotient-ad)-division_bound;budget=tau*max(F(1),abs(ad),abs(quotient)+division_bound);assert gap>budget
 rows.append({'h_hex':h.hex(),'h_exact':str(F(h)),'spacing_exact':str(spacing),'closest_index':nearest,'nearest_quotient':float(quotient),'minimum_error_lower_bound':float(gap),'budget_upper_bound':float(budget),'proof_epsilon':float(epsilon),'widened_acceptance_interval':[float(low),float(high)],'first_possible_integer_index':first,'last_possible_integer_index':last,'no_lattice_point_in_entire_acceptance_interval':True,'binade_condition_actual_at_h':h==actual['h'],'binade_condition_h2_remains_conditional':h!=actual['h']})
diff=F(actual['rp'])-F(actual['rm']);assert (diff/ulp).denominator==1 and float(diff/(2*F(actual['h'])))==actual['fd']
# Publication-derived analytic column8 at fixed stress/e/gamma using direct
# matrix contractions; no generated evaluator, source AD, or tiny-step secant.
params=[100000,160000,31400000,31400000,.6,1.14,1.14,.025,.8,3.975,2.,4.2,.07,1200,.05,2.64,.65]
def analytic(precision):
 with localcontext()as ctx:
  ctx.prec=precision;p=[Q.from_float(float(x))for x in params];z=[Q.from_float(x)for x in actual['state']];pressure=sum(z[:3])/3;u=[(z[i]-(pressure if i<3 else 0))/pressure-z[7+i]for i in range(6)];radius=sum(x*x for x in u).sqrt();n=[x/radius for x in u];j=1;dn=[-(Q(i==j)-n[i]*n[j])/radius for i in range(6)];sqrt2=Q(2).sqrt()
  matrix=lambda v:[[v[0],v[3]/sqrt2,v[5]/sqrt2],[v[3]/sqrt2,v[1],v[4]/sqrt2],[v[5]/sqrt2,v[4]/sqrt2,v[2]]];N=matrix(n);dN=matrix(dn)
  cubic=sum(N[i][j]*N[j][k]*N[k][i]for i in range(3)for j in range(3)for k in range(3));dcubic=3*sum(N[i][j]*N[j][k]*dN[k][i]for i in range(3)for j in range(3)for k in range(3));t=Q(6).sqrt()*cubic;dt=Q(6).sqrt()*dcubic;assert -1<t<1
  ratio=p[12]/p[11];den=1+ratio-(1-ratio)*t;dg=2*ratio*(1-ratio)*dt/den**2;psi=z[6]-p[8]+p[7]*(pressure/p[1]).ln();S=(Q(2)/3).sqrt();dD=p[15]*(S*p[11]*psi*dg-n[j]);factor=(p[4]*(pressure/p[0]).ln()).exp();K=p[2]*factor;G=p[3]*factor;return z[13]*(2*G*dn[0]+K*dD)
a70=analytic(70);a110=analytic(110);assert abs(a70-a110)<Q('1e-60');native_delta=abs(Q.from_float(actual['ad'])-a110);assert native_delta<Q('1e-6')
print(json.dumps({'identity':'independent-actual-fd-ieee-lattice-review','v1_manifest_sha256':sha(A/'manifest.json'),'actual_native_AD':actual['ad'],'actual_residual_difference_lattice_index':int(diff/ulp),'native_secant_recomputed_exact_rational':float(diff/(2*F(actual['h']))),'source_analytic_binary64_inputs_precision70':str(a70),'source_analytic_binary64_inputs_precision110':str(a110),'native_AD_source_analytic_delta':str(native_delta),'analytic_stability_bound':'1e-60','lattice_rows':rows,'conclusion':'Conditional lattice impossibility confirmed at logged native AD; h binade observed, h2 binade remains conditional. Native AD correctness/full derivative coverage not certified.','compiled_calls':0,'production_imports':0},indent=2))
