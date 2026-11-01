"""Read-only reference crosscheck: AGM pi and exp(b ln a), 260 digits."""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from pathlib import Path
import json, struct

p = Path(__file__).parents[1] / 'qualification'
cs = json.loads((p/'requests.json').read_text())['cases']
rs = json.loads((p/'references.json').read_text())['rows']
with localcontext() as ctx:
    ctx.prec = 260
    one = Decimal(1)
    a, b, t, power = one, one/Decimal(2).sqrt(), one/4, one
    for _ in range(12):
        mean = (a+b)/2
        b = (a*b).sqrt()
        t -= power*(a-mean)**2
        a = mean
        power *= 2
    pi = (a+b)**2/(4*t)
    checks = 0
    for c,r in zip(cs,rs):
        if 'references' not in r:
            continue
        x = Decimal.from_float(struct.unpack('>d',bytes.fromhex(c['a_bits']))[0])
        y = Decimal.from_float(struct.unpack('>d',bytes.fromhex(c['b_bits']))[0])
        if c['reference']=='sine':
            z=x-(x/(2*pi)).to_integral_value(rounding=ROUND_HALF_EVEN)*(2*pi)
            terms=[]
            term=z
            for k in range(1,2000):
                terms.append(term)
                term *= -z*z/((2*k)*(2*k+1))
                if abs(term)<Decimal('1e-245'):
                    break
            values=[sum(reversed(terms),Decimal(0))]
        else:
            value=(y*x.ln()).exp()
            values=[value]
            if c['reference']=='jet':
                values.extend([y*((y-1)*x.ln()).exp(),value*x.ln()])
        for v,ref in zip(values,r['references']):
            bits=struct.pack('>d',float(v)).hex()
            assert bits==ref['rounded_bits'],(c['id'],bits,ref['rounded_bits'])
            checks+=1
print(json.dumps({'independent_260_digit_roundings_checked':checks,'all_match':True}))
