"""Independent exact-stored-input Tresca convex projection; no Atlas imports.
Principal projection enumerates six oriented planes and their rank-two intersections.
"""
from pathlib import Path
from decimal import Decimal as D,localcontext,getcontext
from itertools import combinations
import argparse,gzip,json,math,hashlib
import spectral_source as sp
Z=D(0);O=D(1)
add,sub,sc,mm,tr,norm=sp.add,sp.sub,sp.sc,sp.mm,sp.tr,sp.norm
I=sp.eye
PLANES=[(i,j)for i in range(3)for j in range(3)if i!=j]
def dec(x):
    v=float.fromhex(x)
    if not math.isfinite(v):raise ValueError('finite stored binary64 required')
    return D.from_float(v)
def vec(v):return [dec(x)for x in v]
def cart(v):return sp.mat(v,D(2).sqrt())
def mandel(a):
    s=D(2).sqrt();return[a[0][0],a[1][1],a[2][2],s*a[0][1],s*a[1][2],s*a[0][2]]
def elastic(v,lam,mu):return [2*mu*x+(lam*sum(v[:3])if i<3 else Z)for i,x in enumerate(v)]
def inverse(v,lam,mu):
    correction=lam*sum(v[:3])/(3*lam+2*mu)
    return [(x-(correction if i<3 else Z))/(2*mu)for i,x in enumerate(v)]
def plane(p):return [D(i==p[0])-D(i==p[1])for i in range(3)]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Z)
def equality_projection(t,width,active):
    N=[plane(p)for p in active];v=[dot(n,t)-width for n in N]
    if not N:return list(t),[]
    if len(N)==1:alpha=[v[0]/2]
    else:
        b=dot(N[0],N[1]);den=4-b*b
        if not den:return None,None
        alpha=[(2*v[0]-b*v[1])/den,(2*v[1]-b*v[0])/den]
    return [t[i]-sum((a*n[i]for a,n in zip(alpha,N)),Z)for i in range(3)],alpha

def project(t,width):
    tol=D(10)**(-(getcontext().prec-45))*max(O,width,*map(abs,t));valid=[]
    for count in range(3):
        for active in combinations(PLANES,count):
            r,alpha=equality_projection(t,width,active)
            if r is None or any(a < -tol for a in alpha):continue
            violation=max((r[i]-r[j]-width for i,j in PLANES),default=Z)
            if violation>tol:continue
            # Minimal cardinality declares elastic at yield and face at face/corner equality.
            valid.append((sum((x-y)**2 for x,y in zip(t,r)),active,r,alpha))
        if valid:break
    if not valid:raise ArithmeticError('no KKT active set')
    _,active,r,alpha=min(valid,key=lambda v:(v[0],v[1]))
    return r,list(active),alpha

def spectrum(a,precision):
    vals,method=sp.root_cubic(a,precision)
    diagonal=all(not a[i][j]for i in range(3)for j in range(3)if i!=j)
    if diagonal:
        indices=sorted(range(3),key=lambda i:(-a[i][i],i));ps=[[[D(i==j==k)for j in range(3)]for i in range(3)]for k in indices]
    else:
        if len(set(vals))<3:raise ArithmeticError('exact non-diagonal repeated spectrum unresolved')
        ps=[sp.project(a,vals,i)for i in range(3)]
    residual=max([norm(sub(mm(a,p),sc(p,v)))/max(O,norm(a))for v,p in zip(vals,ps)]+[norm(sub(sum_matrices(ps),I()))])
    return vals,ps,method,residual

def sum_matrices(ms):
    out=[[Z]*3 for _ in range(3)]
    for m in ms:out=add(out,m)
    return out

def matrix_return(vals,ps,r):return sum_matrices([sc(p,x)for p,x in zip(ps,r)])
def principal_jacobian(active):
    # Equality projection is affine. Evaluate it on basis directions at width0.
    return [[equality_projection([D(i==j)for i in range(3)],Z,active)[0][k]for j in range(3)]for k in range(3)]
def frechet(vals,ps,r,J,h):
    dv=[tr(mm(p,h))for p in ps]
    out=sum_matrices([sc(p,dot(row,dv))for p,row in zip(ps,J)])
    for i in range(3):
        for j in range(i+1,3):
            coeff=(r[i]-r[j])/(vals[i]-vals[j])if vals[i]!=vals[j]else J[i][i]-J[i][j]
            out=add(out,sc(add(mm(mm(ps[i],h),ps[j]),mm(mm(ps[j],h),ps[i])),coeff))
    return out

def branch(active,r):
    if not active:return 'elastic'
    if len(active)==1:return 'face'
    return 'upper'if len({b for a,b in active})==1 else 'lower'

def evaluate(parameters,current,parent,loading,seeds,precision,fixed_active=None):
    lam,mu,k=[parameters[n]for n in ('lame_lambda','mu','k')]
    trial=[x+y for x,y in zip(parent[:6],elastic(loading,lam,mu))];a=cart(trial)
    vals,ps,method,spectral_error=spectrum(a,precision)
    if fixed_active is None:r,active,alpha=project(vals,2*k)
    else:
        active=fixed_active;r,alpha=equality_projection(vals,2*k,active)
    returned=mandel(matrix_return(vals,ps,r));plastic=inverse([t-x for t,x in zip(trial,returned)],lam,mu);updated=returned+[x+y for x,y in zip(parent[6:],plastic)]
    residual=[x-y for x,y in zip(current[:6],returned)]+[x-y-z for x,y,z in zip(current[6:],parent[6:],inverse([t-x for t,x in zip(trial,current[:6])],lam,mu))]
    nflow=[sum((aa*plane(n)[i]for aa,n in zip(alpha,active)),Z)for i in range(3)]
    scale=max(O,2*k,*map(abs,vals));cert=max([spectral_error,abs(sum(vals)-sum(r))/scale,max(Z,max(r)-min(r)-2*k)/scale]+[abs(t-u-n)/scale for t,u,n in zip(vals,r,nflow)]+[max(Z,-x)/scale for x in alpha])
    stationarity=sub(sub(a,matrix_return(vals,ps,r)),matrix_return(vals,ps,nflow))
    cert=max(cert,norm(stationarity)/scale,abs(sum(plastic[:3]))/max(O,*map(abs,plastic)))
    for projector in ps:cert=max(cert,norm(sub(mm(projector,projector),projector)))
    J=principal_jacobian(active);directions=[]
    for seed in seeds:
        cv,pv,lv=[seed[n]for n in ('current','parent','loading')]
        dt=[x+y for x,y in zip(pv[:6],elastic(lv,lam,mu))]
        dr=mandel(frechet(vals,ps,r,J,cart(dt)))
        dp=inverse([x-y for x,y in zip(dt,dr)],lam,mu)
        residual_d=[x-y for x,y in zip(cv[:6],dr)]+[x-y-z for x,y,z in zip(cv[6:],pv[6:],inverse([x-y for x,y in zip(dt,cv[:6])],lam,mu))]
        directions.append(dict(returned_state=dr+[x+y for x,y in zip(pv[6:],dp)],residual=residual_d))
    parentvals,_,_,_=spectrum(cart(parent[:6]),precision);initial_gap=max(parentvals)-min(parentvals)-2*k
    boundary_distances=[vals[0]-vals[2]-2*k,3*vals[1]-sum(vals)-2*k,3*vals[1]-sum(vals)+2*k]
    return dict(branch=branch(active,r),active=active,eigenvalues=vals,returned_eigenvalues=r,multipliers=alpha,trial=trial,returned_state=updated,residual=residual,directions=directions,certificate_error=cert,spectral_method=method,parent_yield_excess=initial_gap,parent_admissible=initial_gap<=0,boundary_distances=boundary_distances,derivative_kind='selected-active-set-extension; no unique boundary tangent assertion')

def parameters(case):return {k:D.from_float(v)for k,v in case['parameters'].items()}
def decoded_seeds(data):return [{k:vec(v)for k,v in s.items()}for s in data['seeds']]
def encode(v):
    if isinstance(v,D):return format(v,'.72E')if v else '0'
    if isinstance(v,(tuple,list)):return [encode(x)for x in v]
    if isinstance(v,dict):return {k:encode(x)for k,x in v.items()}
    return v

def run(data,precision):
    with localcontext()as ctx:
        ctx.prec=precision;seeds=decoded_seeds(data);rows=[]
        for c in data['cases']:
            row=evaluate(parameters(c),vec(c['current']),vec(c['parent']),vec(c['loading']),seeds,precision)
            assert row['certificate_error']<=D('1e-100'),(c['id'],row['certificate_error'])
            rows.append(dict(id=c['id'],reference=encode(row)))
        h=data['history'];parent=vec(h['initial']);history=[];pars={k:D.from_float(v)for k,v in h['parameters'].items()}
        for i,loading in enumerate(h['loading']):
            c=dict(parameters=h['parameters'],current=[float(x).hex()for x in parent],parent=[float(x).hex()for x in parent],loading=loading)
            row=evaluate(pars,parent,parent,vec(loading),[],precision)
            assert row['certificate_error']<=D('1e-100'),('history',i,row['certificate_error'])
            committed=[float(x).hex()for x in row['returned_state']]
            history.append(dict(step=i,input=c,reference=encode(row),committed=committed));parent=vec(committed)
        return dict(version='tresca-independent-rounded-reference-0.1',precision=precision,input_sha256=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest(),cases=rows,history=history)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,default=Path(__file__).with_name('inputs.json'));ap.add_argument('--precision',type=int,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists(),'fresh output required';data=json.loads(args.inputs.read_text());result=run(data,args.precision)
    args.output.write_bytes(gzip.compress((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));print(json.dumps(dict(cases=len(result['cases']),history=len(result['history']),precision=args.precision)))
