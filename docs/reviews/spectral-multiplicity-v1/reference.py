"""Independent reference assembly; no Atlas imports or compiled observations."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import gzip,json,itertools,math,hashlib
P=Path(__file__).parent;ROOT=P.parents[2]
BASE=ROOT/'catalogue/investigations/symmetric-spectral-primitive-v1'

def build(precision):
 with localcontext() as ctx:
  ctx.prec=precision
  old=json.loads(gzip.decompress((BASE/'reference/reference-p360.json.gz').read_bytes()))
  requests=json.loads(gzip.decompress((BASE/'requests.json.gz').read_bytes()))
  status={(r['case'],r['operation']):r['expected_status']=='ok' for r in requests if r['kind']=='jet' and 'case' in r}
  seeds=[[D.from_float(float.fromhex(x)) for x in row] for row in old['seeds_mandel_hex']]
  cases=[]
  for c in old['cases']:
   x=c['input'];r=c['reference'];eig=list(map(D,r['eigenvalues']));rep=[r['selected'][side]['status']=='repeated-selected-no-classical-derivative' for side in ('max','min')]
   row={'id':x['id'],'mandel_hex':x['mandel_hex'],'repeated':rep,'origin':'existing independent stored-Mandel p360 corpus','extremes':[]}
   for i,side in enumerate(('max','min')):
    if rep==[True,True]:
     deriv=[sum(seed[:3])/3 for seed in seeds];ok=True;gap=D(1)
    elif rep[i]:
     pair='upper' if i==0 else 'lower';op=pair+'_sum';ok=status[(x['id'],op)]
     deriv=[D(t)/2 for t in r['pair_sums'][pair].get('directions',[])];gap=abs(eig[0]-eig[2])
    else:
     ok=status[(x['id'],side)];deriv=[D(t['eigenvalue']) for t in r['selected'][side].get('directions',[])];k=0 if i==0 else 2;gap=min(abs(eig[k]-eig[j]) for j in range(3) if j!=k)
    row['extremes'].append({'ok':ok,'value':str(eig[0 if i==0 else 2]),'derivatives':list(map(str,deriv)), 'selected_gap':str(gap)})
   cases.append(row)
  # Non-diagonal exact radical ties, known projectors from sign vectors.
  for exponent,sgn,sy,sz in itertools.product((-400,0,400),(-1,1),(-1,1),(-1,1)):
   scale=D(2)**exponent;v=[1,sy,sz];shears=[v[0]*v[1],v[1]*v[2],v[0]*v[2]]
   values=[0.,0.,0.]+[math.ldexp(float(sgn*t),exponent) for t in shears]
   rankone=[D(1)/3]*3+[D(2).sqrt()*t/3 for t in shears]
   cluster=[(D(1)-t)/2 if k<3 else -t/2 for k,t in enumerate(rankone)]
   vals=[D(2).sqrt()*scale,-scale/D(2).sqrt()]
   grads=[rankone,cluster]
   if sgn<0:vals=[-vals[1],-vals[0]];grads=grads[::-1]
   row={'id':f'radical-{exponent}-{sgn}-{sy}-{sz}','mandel_hex':[t.hex() for t in values],'repeated':[sgn<0,sgn>0],'origin':'exact signed rank-one/cluster eigensystem','extremes':[]}
   for val,g in zip(vals,grads):
    row['extremes'].append({'ok':True,'value':str(val),'derivatives':[str(sum(a*b for a,b in zip(g,seed))) for seed in seeds], 'selected_gap':str(3*scale/D(2).sqrt())})
   cases.append(row)
  # One-ULP *distinct* spectrum: neither side is a tie, both unresolved.
  a=[math.nextafter(1.,math.inf),1.,math.nextafter(1.,0.),0.,0.,0.]
  cases.append({'id':'one-ulp-distinct','mandel_hex':[x.hex() for x in a],'repeated':[False,False],'origin':'exact diagonal literals','extremes':[{'ok':False},{'ok':False}]})
  return {'identity':'selected-extreme-independent-reference-v1','seeds':old['seeds_mandel_hex'],'cases':cases}

if __name__=='__main__':
 a,b=build(100),build(160)
 with localcontext() as ctx:
  ctx.prec=180
  for x,y in zip(a['cases'][48:-1],b['cases'][48:-1]):
   for p,q in zip(x['extremes'],y['extremes']):
    for u,v in zip([p['value']]+p['derivatives'],[q['value']]+q['derivatives']):
     assert abs(D(u)-D(v))<=D('1e-90')*max(abs(D(v)),D('1e-200'))
 b['input_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'reference/reference-p360.json.gz',BASE/'requests.json.gz',Path(__file__)]}
 (P/'references.json').write_text(json.dumps(b,indent=2)+'\n')
 print('73 cases; existing360-digit references plus24 exact radical ties converge100/160 digits')
