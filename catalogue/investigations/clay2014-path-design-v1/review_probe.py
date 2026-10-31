"""Independent retained-data review; Decimal scalar law, no production imports."""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib,json,math
ROOT=Path('/private/tmp/atlas-clay2014-path-reference-20261031-v1')
D=Decimal.from_float

def sine(x):
    term=x; value=x; j=1
    while True:
        term *= -x*x / Decimal((2*j)*(2*j+1))
        new=value+term
        if new==value:return value
        value=new;j+=1

def scalar(row,precision):
    with localcontext() as ctx:
        ctx.prec=precision
        p=row['input']['parameters']; initial=row['input']['initial']; la=D(p['lambda_star']);ka=D(p['kappa_star'])
        sinphi=sine(D(p['phi_c']));af=Decimal(3).sqrt()*(3-sinphi)/(2*Decimal(2).sqrt()*sinphi)
        alpha=(((la-ka)/(la+ka))*(3+af*af)/(af*Decimal(3).sqrt())).ln()/Decimal(2).ln()
        pe0=1000*((D(p['N'])-(1+D(initial[6])).ln())/la).exp()
        y=((pe0/D(initial[0])).ln()*alpha).exp();volume=Decimal(0);out=[]
        for knot in row['caller_points']:
            v=sum((D(x) for x in knot['increment'][:3]),Decimal(0));s=1 if v>0 else -1 if v<0 else 0
            if s:y=Decimal(s)+(y-s)*(-alpha*(1/ka-1/la)*v/2).exp()
            volume+=v;pe=pe0*(volume/la).exp();pressure=pe*(-y.ln()/alpha).exp()
            void=(1+D(initial[6]))*(-volume).exp()-1
            out.append((pressure,void))
        return out

record=json.loads((ROOT/'catalogue/investigations/clay2014-path-reference-v1/reference.json').read_text())
manifest=json.loads((ROOT/'catalogue/investigations/clay2014-path-reference-v1/manifest.json').read_text())
assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in manifest['files'].items())
metrics={'manifest_files_verified':len(manifest['files']),'scalar':[]}
for row in record['cases']:
    if not row['scalar_reference']:continue
    a=scalar(row,90);b=scalar(row,140)
    metrics['scalar'].append({'case':row['id'],
      'precision_pressure_max_Pa':float(max(abs(x[0]-y[0]) for x,y in zip(a,b))),
      'precision_void_max':float(max(abs(x[1]-y[1]) for x,y in zip(a,b))),
      'binary64_scalar_pressure_max_Pa':max(abs(float(x[0])-y['state'][0]) for x,y in zip(b,row['scalar_reference'])),
      'binary64_scalar_void_max':max(abs(float(x[1])-y['state'][6]) for x,y in zip(b,row['scalar_reference'])),
      'RK4_pressure_max_Pa':max(abs(float(x[0])-y['state'][0]) for x,y in zip(b,row['grids'][-1]['trajectory'])),
      'RK4_void_max':max(abs(float(x[1])-y['state'][6]) for x,y in zip(b,row['grids'][-1]['trajectory']))})
for label in ('coarse_middle','middle_fine'):
 metrics[label]={key:max(x[key] for row in record['cases'] for x in row[label]) for key in ('stress_Pa','void_ratio')}
metrics['max_volume_error']=max(row['max_volume_error'] for row in record['cases'])
metrics['covariance']={key:max(e[key] for row in record['covariance'] for e in row['errors']) for key in ('stress_Pa','void_ratio')}
print(json.dumps(metrics,indent=2))
