"""Independent source/reference audit, no Atlas imports/material updates/builds."""
import hashlib,json,runpy
from decimal import Decimal as D,localcontext
from pathlib import Path
B=Path(__file__).resolve().parent.parent
ref=runpy.run_path(str(B/'reference.py'))
q=ref['q']; eigen=ref['eigen']

def matrix(v):
    a=[[D(0) for _ in range(3)]for _ in range(3)]
    for i in range(3):a[i][i]=q(v[i])
    for i,j,k in ((0,1,3),(1,2,4),(0,2,5)):a[i][j]=a[j][i]=q(v[k])/D(2).sqrt()
    return a

def det(a):
    return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])

def cosine(x):
    total=term=D(1);k=1
    while True:
        term*=-x*x/D((2*k-1)*(2*k));old=total;total+=term
        if old==total:return total
        k+=1

def gradient(v,which):
    # Implicit characteristic-polynomial derivative, no eigenvector/projector code.
    a=matrix(v);ev=eigen(v);lam=ev[which]
    m=[[lam*D(i==j)-a[i][j]for j in range(3)]for i in range(3)]
    cof=[]
    for i in range(3):
        row=[]
        for j in range(3):
            rr=[k for k in range(3)if k!=i];cc=[k for k in range(3)if k!=j]
            row.append(D((-1)**(i+j))*(m[rr[0]][cc[0]]*m[rr[1]][cc[1]]-m[rr[0]][cc[1]]*m[rr[1]][cc[0]]))
        cof.append(row)
    denominator=D(1)
    for i,vv in enumerate(ev):
        if i!=which:denominator*=lam-vv
    return [cof[i][i]/denominator for i in range(3)]+[D(2).sqrt()*cof[i][j]/denominator for i,j in ((0,1),(1,2),(0,2))]

def analytic_columns(case):
    z,zn,de,p=(case[k]for k in ('current','previous','de','parameters'))
    nu=q(p['nu']);dd=list(map(q,de));tr=sum(dd[:3]);shape=[x/(1+nu)+(nu*tr/((1+nu)*(1-2*nu))if i<3 else 0)for i,x in enumerate(dd)]
    dc=eigen(z[:6]);dn=eigen(zn[:6]);cb=(dc[0]+dn[0])/2;dif=dc[-1]-dc[0];difn=dn[-1]-dn[0]
    sp=ref['sin'](q(p['phi']));F=2*(q(p['c_cohesion'])*cosine(q(p['phi']))+cb*sp)/(1-sp);S=(dif+difn)/(2*F)
    _,E,branch,_=ref['quantities'](z,zn,p)
    gc=[gradient(z[:6],i)for i in (0,2)];gn=[gradient(zn[:6],i)for i in (0,2)]
    columns=[]
    for j in range(20):
        dl=du=dln=dun=D(0)
        if j<6:dl,du=gc[0][j],gc[1][j]
        elif 7<=j<13:dln,dun=gn[0][j-7],gn[1][j-7]
        dcb=(dl+dln)/2;dD=du-dl;dDn=dun-dln;dF=2*sp*dcb/(1-sp);dS=(dD+dDn)/(2*F)-S*dF/F
        dE=E*(q(p['n'])*dcb/cb-(2*q(p['Rf'])*dS/(1-q(p['Rf'])*S)if branch=='primary' else 0))
        col=[-dE*x for x in shape]
        if j<6:col[j]+=1
        elif 7<=j<13:col[j-7]-=1
        elif j>=14:
            k=j-14
            for i in range(6):col[i]-=E*(D(i==k)/(1+nu)+(nu/((1+nu)*(1-2*nu))if i<3 and k<3 else 0))
        col.append(D(j==6)-(dD if dif>=q(zn[6]) else D(j==13)))
        scale=D(100000)if j<14 else D(1)
        columns.append([x*scale/D(100000)for x in col])
    return columns

def main():
    source=json.loads((B/'references.json').read_text());worst_invariant=D(0);derivative_errors=[]
    with localcontext()as ctx:
        ctx.prec=160
        for case in source['cases']:
            for stress in (case['initial'][:6],case['target'][:6]):
                a=matrix(stress);ev=eigen(stress);scale=max(D(1),*(abs(x)for row in a for x in row))
                errs=[abs(sum(ev)-sum(a[i][i]for i in range(3)))/scale,abs(sum(ev[i]*ev[j]for i,j in ((0,1),(0,2),(1,2)))-sum(a[i][i]*a[j][j]-a[i][j]**2 for i,j in ((0,1),(0,2),(1,2))))/scale**2,abs(ev[0]*ev[1]*ev[2]-det(a))/scale**3]
                worst_invariant=max(worst_invariant,*errs)
                assert max(errs)<D('1e-140')
            phi=q(case['parameters']['phi']);cp=ref['sin'](phi+D('1.570796326794896619231321691639751442098584699687552910487472296153908203143104499314017412671058533991074043256641153323546922304775291115862679704064240558725'))
            assert abs(cp-cosine(phi))<D('1e-145')
        for case in source['derivatives']:
            exact=analytic_columns(case);errors=[]
            for sweep in case['sweeps']:
                error=max(abs(q(x)-y)/max(D(1),abs(y))for col,ecol in zip(sweep['columns'],exact)for x,y in zip(col,ecol));errors.append(error)
            assert errors[-1]<D('2e-5')and errors[-2]<D('2e-5'),errors
            derivative_errors.append({'id':case['id'],'normalized_errors':[str(x)for x in errors]})
    out={'identity':'independent-duncan-reference-source-audit-v1','source_cases':len(source['cases']),'eigen_invariant_worst':str(worst_invariant),'derivatives':derivative_errors,'reference_sha256':hashlib.sha256((B/'references.json').read_bytes()).hexdigest(),'reference_code_sha256':hashlib.sha256((B/'reference.py').read_bytes()).hexdigest(),'pass':True,'compiled_calls':0,'material_updates':0}
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
