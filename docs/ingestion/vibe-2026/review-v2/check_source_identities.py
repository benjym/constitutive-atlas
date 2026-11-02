"""Independent published-source identities only; never evaluates a VIBE model.

No author code, compiler, material solver or browser is imported or executed.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
paper = ROOT / '.local/private-sources/vibe-2026/original-v2/vibe-2026-vor.pdf'
assert hashlib.sha256(paper.read_bytes()).hexdigest() == '90b1c3bc56bacf1294e3e8ea60a217ffa1651981c86c63b0c0d9354534764912'

# Eq42 fixes B = Id + q I tensor I; this tests its unique nonsingular inverse.
count = 0
for q in [F(-1,4), F(0), F(2,7), F(1), F(100)]:
    for x in [[F(i+1) for i in range(6)], [F(-3),F(2),F(9),F(1,3),F(-7),F(11)]]:
        y = [a - q/(1+3*q)*sum(x[:3]) if i<3 else a for i,a in enumerate(x)]
        z = [a + q*sum(y[:3]) if i<3 else a for i,a in enumerate(y)]
        assert z == x
        count += 6

# Eq27 norm of the sum versus separate absolute contributions in A6/A8.
# x,y stand for the two scalar internal contributions with common factors removed.
abs_witnesses = []
for x,y in [(F(2),F(3)), (F(2),F(-2)), (F(2),F(-1))]:
    combined, separated = abs(x+y), abs(x)+abs(y)
    abs_witnesses.append({'hydraulic':str(x),'thermal':str(y),
                          'combined':str(combined),'separated':str(separated),
                          'equal':combined==separated})
assert abs_witnesses[0]['equal']
assert not abs_witnesses[1]['equal']
assert not abs_witnesses[2]['equal']

# A15/A24/A25 at positive suction, drying from a_scan=0 with Table1 a_e=.9.
# se/sen = a_e, r_lambda=.1. Unit imposed suction rate leaves coefficient 8.1/s.
ae, scan = F(9,10), F(0)
rlambda = F(1,10)+F(9,10)*scan**3
coefficient = (ae+scan-ae*scan)*(1-rlambda)/(1-ae)
assert coefficient == F(81,10)
scan_rates = [{'suction':str(s),'scan_rate_for_unit_suction_rate':str(coefficient/s)}
              for s in [F(1),F(1,10),F(1,100)]]
# Its 1/s divergence cannot be repaired by the removable WRC derivative limit.

# Prospective generic explicit-clock oracle, independently computed with rationals.
t0, duration, tau, z0 = F(11), F(4), F(2), F(-7,2)
def clock(d):
    return z0 + ((t0+d)**2-t0**2)/(2*tau**2)
assert clock(F(2)) == F(5,2) and clock(duration) == F(19,2)
frozen_start = z0 + duration*t0/tau**2
elapsed_only = z0 + duration**2/(2*tau**2)
assert frozen_start == F(15,2) and elapsed_only == F(-3,2)

result = {
    'paper_sha256':hashlib.sha256(paper.read_bytes()).hexdigest(),
    'scope':'isolated exact identities and counterexamples, not VIBE integration/admission',
    'inverse_component_checks':count,
    'absolute_value_counterexamples':abs_witnesses,
    'saturated_start_scanning':{'ae':str(ae),'scan':str(scan),
        'positive_suction_coefficient':str(coefficient),
        'rates':scan_rates,'zero_suction_branch_defined_in_this_check':False},
    'generic_clock_oracle':{'midpoint':str(clock(F(2))),
        'endpoint':str(clock(duration)), 'wrong_frozen_start':str(frozen_start),
        'wrong_elapsed_only':str(elapsed_only)},
    'compiled_vendor_or_browser_execution':False,
}
(HERE/'source-identities-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
