"""Independent source-level checks; no atlas imports or compiled execution."""
import json
import math
from pathlib import Path

E, nu, sigma0, alpha, n = 390900e6, 0.3, 50e6, 0.5, 5.0
checks = []
def check(name, got, expected, rel=2e-13, absolute=1e-15):
    error = abs(got - expected)
    passed = error <= max(absolute, rel * max(abs(got), abs(expected)))
    checks.append(dict(name=name, actual=got, expected=expected, error=error, passed=passed))

def strain(stress):
    mean = sum(stress[:3])/3
    s = [stress[i] - (mean if i < 3 else 0) for i in range(6)]
    q = math.sqrt(1.5 * sum(v*v for v in s))
    a = (1+nu + 1.5*alpha*(q/sigma0)**(n-1))/E
    return [a*s[i] + ((1-2*nu)*mean/E if i<3 else 0) for i in range(6)]

# Closed uniaxial strain and lateral pseudo-incompressibility.
for x in (0.0, -sigma0, sigma0, 2*sigma0):
    e = strain([x,0,0,0,0,0])
    c = alpha/E * (abs(x)/sigma0)**(n-1) * x
    check(f'uniaxial axial {x}', e[0], x/E+c)
    check(f'uniaxial lateral {x}', e[1], -nu*x/E-c/2)
    check(f'uniaxial volume {x}', sum(e[:3]), (1-2*nu)*x/E)
check('yield nonlinear strain offset', strain([sigma0,0,0,0,0,0])[0]-sigma0/E, alpha*sigma0/E)
# Pure hydrostatic finite state, full reversal and zero origin.
for p in (-12e6, 0, 12e6):
    e = strain([p,p,p,0,0,0])
    check(f'hydrostatic trace {p}', sum(e[:3]), 3*(1-2*nu)*p/E)
sigma = [70e6,-15e6,32e6,7e6,-11e6,3e6]
a, b = strain(sigma), strain([-v for v in sigma])
for i in range(6): check(f'odd reversal {i}', a[i], -b[i])
# Scalar inversion is independently solved by bisection, not common-engine Newton.
for eq in (0.0, 1e-5, 0.001, 0.01):
    lo, hi = 0.0, max(E*eq, sigma0)
    for _ in range(160):
        q=(lo+hi)/2
        g=(2*(1+nu)/3*q + alpha*(q/sigma0)**(n-1)*q)/E
        if g<eq: lo=q
        else: hi=q
    q=(lo+hi)/2
    check(f'scalar inverse {eq}', (2*(1+nu)/3*q + alpha*(q/sigma0)**(n-1)*q)/E, eq)
# Hydrostatic energy inconsistency is a retained source diagnostic, not a gate failure.
p=12e6
correct_hydrostatic_energy = 1.5*(1-2*nu)*p*p/E
report={
 'identity':'ramberg-osgood-ansys242-source-algebra-v1',
 'method':'independent Python scalar arithmetic from transcribed primary equations; no atlas or compiled execution',
 'parameters':dict(E=E,nu=nu,sigma0=sigma0,alpha=alpha,n=n),
 'checks':checks, 'passed':all(c['passed'] for c in checks),
 'source_energy_diagnostic':{'hydrostatic_pressure_magnitude_Pa':p,'literal_source_W_el_Pa':0,'governing_relation_integral_W_el_Pa':correct_hydrostatic_energy,'status':'source inconsistency retained; source energy output excluded, governing mechanical equation unaffected'}
}
path=Path(__file__).with_name('algebra-results.json')
path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'passed':report['passed'],'output':str(path)}))
assert report['passed']
