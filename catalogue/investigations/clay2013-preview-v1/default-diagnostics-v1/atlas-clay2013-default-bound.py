"""Independent spherical specialization; no DSL or compiled-rate references."""
import math,json,pathlib
out=pathlib.Path('/private/tmp/atlas-clay2013-default-diagnostics-v1')
phi=math.pi/6;lam=.12;kap=.025;N=1.1;nu=.2;e=.8;pref=1000.
pe=pref*math.exp((N-math.log1p(e))/lam);rows=[]
for p in (10000.,100000.):
 fs=1.5*p*(1/lam+1/kap)*(1-2*nu)/(1+nu);c=nu/(1-2*nu)
 # At sigma=p I, fm=0 and d=-I/sqrt(3), hence fdA=4.
 A=fs*c;B=fs*(1+2*c);C=((2*p/pe)**2)/4*(fs*(1+3*c)-3*p/lam)/math.sqrt(3)
 r={'pressure':p,'pe':pe,'radial_rate_formula':'A*x+B*y-C*sqrt(x*x+2*y*y)','A':A,'B':B,'C':C,'positive_axial_rate':True}
 if C>0 and C*C>B*B/2:
  maximum=A-math.sqrt(C*C-B*B/2);y=B/(2*math.sqrt(C*C-B*B/2))
  r.update(maximum_radial_rate_per_axial_rate=maximum,maximizing_radial_axial_ratio=y,no_constant_radial_stress_tangent=maximum<0)
 else:r.update(no_constant_radial_stress_tangent=False,note='This bound does not exclude a drained tangent.')
 rows.append(r)
assert rows[1]['maximum_radial_rate_per_axial_rate']<0
# Cross-check the specialization against every retained compiled initial rate,
# without using the rate values to derive or fit A/B/C.
checks=[]
for x in json.load(open(out/'observations.json')):
 r=next(r for r in rows if r['pressure']==x['pressure']);y=x['radial_axial_ratio'];expected=1e-4*(r['A']+r['B']*y-r['C']*math.sqrt(1+2*y*y));actual=x['derived']['stress_rate'][1]
 assert abs(expected-actual)<1e-10*max(1,abs(expected))
 checks.append({'pressure':x['pressure'],'ratio':y,'analytical_radial_increment':expected,'interpreted_initial_radial_increment':actual})
result={'identity':'clay2013-spherical-drained-tangent-bound-v1','source':'Masin 2013 Appendix Eqs43–58; source DOI and private source hash retained in preview plan','scope':'At exactly spherical sigma=pI and fixed illustrative parameters; necessary tangent for a differentiable positive-axial drained path. Not a theorem for finite endpoint roots or all states.','coefficients':rows,'specialization_checks':checks,'not_a_new_acceptance_gate':True}
(out/'analytical-bound.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))
