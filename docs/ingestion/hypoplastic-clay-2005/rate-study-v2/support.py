"""Independent high-precision actual-input support diagnostics, no Atlas imports."""
from decimal import Decimal,localcontext
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
MARGIN=Decimal.from_float(64*math.ulp(1.))


def diagnostics(case,precision=100):
    with localcontext() as ctx:
        ctx.prec=precision
        v=[Decimal.from_float(float(x)) for x in case['state'][:6]]
        x,y,z,u,v,w=v;r=Decimal(2).sqrt()
        a=[[x,u/r,w/r],[u/r,y,v/r],[w/r,v/r,z]]
        n=sum((q*q for row in a for q in row),Decimal(0)).sqrt()
        if not n:raise ValueError('nonzero diagnostic stress required')
        a=[[q/n for q in row]for row in a]
        minor=a[0][0]*a[1][1]-a[0][1]*a[1][0]
        det=a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
        positive_diagonals=all(a[i][i]>0 for i in range(3))
        accepted=positive_diagonals and minor>MARGIN and det>MARGIN
        spd=positive_diagonals and minor>0 and det>0
        return dict(precision=precision,normalized_minor2_decimal=str(minor),normalized_det_decimal=str(det),
                    ideal_arithmetic_support_accepts=accepted,actual_mandel_cartesian_spd=spd,
                    note='actual binary64 Mandel components divided by exact Decimal sqrt2; intended spectrum is secondary')


def build_support_reference():
    inp=json.loads((HERE/'support-inputs.json').read_text());out=[]
    for c in inp['cases']:
        lo,hi=diagnostics(c,80),diagnostics(c,120)
        if lo['ideal_arithmetic_support_accepts']!=hi['ideal_arithmetic_support_accepts'] or hi['ideal_arithmetic_support_accepts'] is not c['expected_accepted']:
            raise ValueError('unstable or unexpected support case:'+c['id'])
        out.append(dict(id=c['id'],expected_accepted=c['expected_accepted'],oracle80=lo,oracle120=hi))
    return dict(version='clay2005-independent-support-reference-v2',margin_binary64=float(MARGIN),cases=out,
                scope='classification of retained actual input witnesses; not a globalSPD theorem or source-rate accuracy certificate')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise SystemExit('fresh output path required')
    a.output.write_text(json.dumps(build_support_reference(),indent=2,allow_nan=False)+'\n')
