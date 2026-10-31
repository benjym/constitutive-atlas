"""Independent exact-stored-input MC Decimal references. No Atlas imports."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import json,math,argparse,gzip,hashlib
import spectral_source as sp
Z=D(0);O=D(1)
I=lambda:sp.eye()
add,sub,sc,mm,tr,norm=sp.add,sp.sub,sp.sc,sp.mm,sp.tr,sp.norm

def txt(x):return format(x,'.72E')if x else'0'
def encode(x):
 if isinstance(x,D):return txt(x)
 if isinstance(x,(tuple,list)):return [encode(v)for v in x]
 if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
 return x

def frac(x):
 v=float.fromhex(x)
 if not math.isfinite(v):raise ValueError('nonfinite stored binary64 input')
 return F.from_float(v)
def fd(x):return D(x.numerator)/D(x.denominator)
def vec(xs):return [frac(x)for x in xs]
def mandel(a):
 s=D(2).sqrt();return[a[0][0],a[1][1],a[2][2],s*a[0][1],s*a[1][2],s*a[0][2]]
def cart(v):return sp.mat(v,D(2).sqrt())
def el(v,K,G):
 t=sum(v[:3]);return [K*t+2*G*(v[i]-t/3)if i<3 else 2*G*v[i]for i in range(6)]
def lintrial(parent,loading,K,G):return[-a-b for a,b in zip(parent,el(loading,K,G))]
def sincos(x):
 # Stored source angles lie within(0,pi/2); no argument reduction needed.
 import decimal
 cutoff=D(10)**(-(decimal.getcontext().prec+8));xx=x*x
 s=term=x;k=1
 while abs(term)>cutoff:
  term*= -xx/D((2*k)*(2*k+1));s+=term;k+=1
  if k>decimal.getcontext().prec*2:raise ArithmeticError('sin series budget')
 c=term=O;k=1
 while abs(term)>cutoff:
  term*= -xx/D((2*k-1)*(2*k));c+=term;k+=1
  if k>decimal.getcontext().prec*2:raise ArithmeticError('cos series budget')
 return s,c

def atan_inverse(n):
 import decimal
 x=O/n;xx=x*x;term=x;total=x;k=1;cutoff=D(10)**(-(decimal.getcontext().prec+8))
 while abs(term)>cutoff:
  term*= -xx;total+=term/(2*k+1);k+=1
 return total

def pi():return 16*atan_inverse(5)-4*atan_inverse(239)
def magnitude_span(v):
 ds=[fd(abs(x)).adjusted()for x in v if x]
 return max(ds)-min(ds)if ds else 0

def precision_extra(case,seeds):
 p={k:frac(v)for k,v in case['parameters'].items()};E,nu=p['E'],p['nu']
 if E<=0 or not -1<nu<F(1,2):return 0
 K=E/(3*(1-2*nu));G=E/(2*(1+nu));t=lintrial(vec(case['parent']),vec(case['loading']),K,G)
 dirs=[lintrial(vec(s['parent']),vec(s['loading']),K,G)for s in seeds]
 allv=t+sum(dirs,[])
 digits=max([len(str(abs(x.numerator)))for x in allv]+[len(str(x.denominator))for x in allv],default=1)
 return max(0,2*magnitude_span(t)-100,digits-60)

def spectral_data(a,hs,precision):
 vals,method=sp.root_cubic(a,precision);ps={};dps={};dls={};res=[];a_scale=norm(a)or O
 for i in range(3):
  if any(vals[i]==vals[j]for j in range(3)if j!=i):continue
  p=sp.project(a,vals,i);ps[i]=p;dls[i]=[];dps[i]=[]
  res.extend([norm(sub(mm(a,p),sc(p,vals[i])))/a_scale,norm(sub(mm(p,p),p)),abs(tr(p)-1)])
  js=[j for j in range(3)if j!=i]
  for h in hs:
   dl=tr(mm(p,h));dp=[[Z]*3 for _ in range(3)]
   if vals[js[0]]==vals[js[1]]:
    co=sub(I(),p);dp=sc(add(mm(mm(co,h),p),mm(mm(p,h),co)),O/(vals[i]-vals[js[0]]))
   else:
    for j in js:
     pj=sp.project(a,vals,j);dp=add(dp,sc(add(mm(mm(pj,h),p),mm(mm(p,h),pj)),O/(vals[i]-vals[j])))
   dls[i].append(dl);dps[i].append(dp)
   res.extend([norm(sub(add(mm(p,dp),mm(dp,p)),dp))/max(norm(dp),O),abs(tr(dp))/max(norm(dp),O),norm(sub(add(mm(h,p),mm(a,dp)),add(sc(p,dl),sc(dp,vals[i]))))/max(norm(h),D('1e-100000'))])
 return vals,method,ps,dls,dps,max(res,default=Z)

def law(p):
 K,G,c,s,d,cf=p['K'],p['G'],p['c'],p['sf'],p['sd'],p['cf']
 A=2*(K-2*G/3)*d;h=2*c*cf
 ds=4*K*d*s+4*G*(1+d*s/3);dl=4*K*d*s+G*(3-s-d+d*s/3);dr=4*K*d*s+G*(3+s+d+d*s/3);da=4*K*d*s
 return dict(A=A,h=h,face=ds,left=dl,right=dr,apex=da)

def classify(v,p,l):
 t1,t2,t3=v;s,d,G=p['sf'],p['sd'],p['G'];h=l['h']
 a=(t1-t2)/(2*G*(1+d));b=(t2-t3)/(2*G*(1-d));L=(t1+t2-2*t3)/(2*G*(3-d));R=(2*t1-t2-t3)/(2*G*(3+d))
 ns={'face':(1+s)*t1-(1-s)*t3-h,'left':(1+s)*(t1+t2)/2-(1-s)*t3-h,'right':(1+s)*t1-(1-s)*(t2+t3)/2-h,'apex':D(2)/3*s*sum(v)-h}
 roots={k:ns[k]/l[k]for k in ns}
 chosen='elastic'if ns['face']<=0 else'apex'if roots['apex']>=max(L,R)else'face'if roots['face']<min(a,b)else'left'if a<b else'right'
 admissible={'elastic':ns['face']<=0,'face':ns['face']>0 and 0<roots['face']<min(a,b),'left':ns['face']>0 and roots['left']>0 and a<=roots['left']<L,'right':ns['face']>0 and roots['right']>0 and b<=roots['right']<R,'apex':ns['face']>0 and roots['apex']>0 and roots['apex']>=max(L,R)}
 guards={'Ftrial':ns['face'],'apex_minus_upper':roots['apex']-max(L,R),'face_minus_lower':roots['face']-min(a,b),'gsl_minus_gsr':a-b}
 distances={'face':{'gamma':roots['face'],'upper_minus_gamma':min(a,b)-roots['face']},'left':{'gamma':roots['left'],'gamma_minus_lower':roots['left']-a,'upper_minus_gamma':L-roots['left']},'right':{'gamma':roots['right'],'gamma_minus_lower':roots['right']-b,'upper_minus_gamma':R-roots['right']},'apex':{'gamma':roots['apex'],'gamma_minus_lower':roots['apex']-max(L,R)}}
 return chosen,roots,guards,admissible,distances

def parameter_changes(p):
 E,nu,c,s,cf,d,cd=p['E'],p['nu'],p['c'],p['sf'],p['cf'],p['sd'],p['cd'];K,G=p['K'],p['G']
 changes=[]
 for name in('E','nu','c','phi','psi'):
  v={k:Z for k in('K','G','c','sf','cf','sd')}
  if name=='E':v.update(K=K/E,G=G/E)
  if name=='nu':v.update(K=2*K/(1-2*nu),G=-G/(1+nu))
  if name=='c':v['c']=O
  if name=='phi':v.update(sf=cf,cf=-s)
  if name=='psi':v['sd']=cd
  changes.append((name,v))
 return changes

def branch_result(branch,v,p,l,roots,ps,dls,dps,hs,changes):
 needed={'elastic':[],'face':[0,1,2],'left':[2],'right':[0],'apex':[]}[branch]
 if any(i not in ps for i in needed):return {'status':'undefined-selected-repeated-spectrum','required_isolated_indices':needed}
 t1,t2,t3=v;A,K,G,s,d,c,cf=l['A'],p['K'],p['G'],p['sf'],p['sd'],p['c'],p['cf'];g=Z if branch=='elastic'else roots[branch]
 if branch=='elastic':r=tuple(v);value=None
 elif branch=='face':r=(t1-g*(A+2*G*(1+d)),t2-g*A,t3-g*(A-2*G*(1-d)))
 elif branch=='left':r=((t1+t2)/2-g*(A+G*(1+d)),)*2+(t3-g*(A-2*G*(1-d)),)
 elif branch=='right':r=(t1-g*(A+2*G*(1+d)),)+((t2+t3)/2-g*(A-G*(1-d)),)*2
 else:r=(c*cf/s,)*3
 if branch=='face':value=add(add(sc(I(),r[1]),sc(ps[0],r[0]-r[1])),sc(ps[2],r[2]-r[1]))
 elif branch=='left':value=add(sc(I(),r[0]),sc(ps[2],r[2]-r[0]))
 elif branch=='right':value=add(sc(I(),r[2]),sc(ps[0],r[0]-r[2]))
 elif branch=='apex':value=sc(I(),r[0])
 derivatives=[]
 for j,(h,dp)in enumerate(zip(hs,changes)):
  if branch=='elastic':derivatives.append(h);continue
  dK,dG,dc,ds,dcf,dd=[dp[k]for k in('K','G','c','sf','cf','sd')]
  dh=2*dc*cf+2*c*dcf;dA=2*(dK-2*dG/3)*d+2*(K-2*G/3)*dd
  if branch=='apex':derivatives.append(sc(I(),dc*cf/s+c*dcf/s-c*cf*ds/(s*s)));continue
  dgproduct=dd*s+d*ds
  dD={'face':4*dK*d*s+4*K*dgproduct+4*dG*(1+d*s/3)+4*G*dgproduct/3,'left':4*dK*d*s+4*K*dgproduct+dG*(3-s-d+d*s/3)+G*(-ds-dd+dgproduct/3),'right':4*dK*d*s+4*K*dgproduct+dG*(3+s+d+d*s/3)+G*(ds+dd+dgproduct/3)}[branch]
  dtmax=dls[0][j]if 0 in dls else None;dtmin=dls[2][j]if 2 in dls else None
  if branch=='face':
   dtmid=dls[1][j];dN=(1+s)*dtmax-(1-s)*dtmin+ds*(t1+t3)-dh
  elif branch=='left':
   dtpair=tr(h)-dtmin;dN=(1+s)*dtpair/2-(1-s)*dtmin+ds*((t1+t2)/2+t3)-dh
  else:
   dtpair=tr(h)-dtmax;dN=(1+s)*dtmax-(1-s)*dtpair/2+ds*(t1+(t2+t3)/2)-dh
  dg=(dN-g*dD)/l[branch]
  if branch=='face':
   dr1=dtmax-dg*(A+2*G*(1+d))-g*(dA+2*dG*(1+d)+2*G*dd)
   dr2=dtmid-dg*A-g*dA
   dr3=dtmin-dg*(A-2*G*(1-d))-g*(dA-2*dG*(1-d)+2*G*dd)
   dv=add(add(sc(I(),dr2),sc(ps[0],dr1-dr2)),sc(ps[2],dr3-dr2));dv=add(add(dv,sc(dps[0][j],r[0]-r[1])),sc(dps[2][j],r[2]-r[1]))
  elif branch=='left':
   drl=dtpair/2-dg*(A+G*(1+d))-g*(dA+dG*(1+d)+G*dd)
   dr3=dtmin-dg*(A-2*G*(1-d))-g*(dA-2*dG*(1-d)+2*G*dd)
   dv=add(add(sc(I(),drl),sc(ps[2],dr3-drl)),sc(dps[2][j],r[2]-r[0]))
  else:
   dr1=dtmax-dg*(A+2*G*(1+d))-g*(dA+2*dG*(1+d)+2*G*dd)
   drr=dtpair/2-dg*(A-G*(1-d))-g*(dA-dG*(1-d)+G*dd)
   dv=add(add(sc(I(),drr),sc(ps[0],dr1-drr)),sc(dps[0][j],r[0]-r[2]))
  derivatives.append(dv)
 return {'status':'defined','source_principal_return':r,'gamma':g,'matrix':value,'dmatrices':derivatives}

def interface(case,seeds,precision,resolved=False):
 raw={k:frac(v)for k,v in case['parameters'].items()};E,nu,c=raw['E'],raw['nu'],raw['c'];phi,psi=fd(raw['phi']),fd(raw['psi']);halfpi=pi()/2
 if E<=0 or c<=0 or not -1<nu<F(1,2)or not 0<phi<halfpi or not 0<psi<halfpi:return {'status':'invalid-source-domain'}
 Kf=E/(3*(1-2*nu));Gf=E/(2*(1+nu));s,cf=sincos(phi);d,cd=sincos(psi)
 p=dict(E=fd(E),nu=fd(nu),c=fd(c),sf=s,sd=d,cf=cf,cd=cd,K=fd(Kf),G=fd(Gf))
 if resolved:
  co=case.get('resolved_coefficients')
  if co is None:return {'status':'not-supplied'}
  Kf,Gf=frac(co['K']),frac(co['G']);p.update({k:fd(frac(co[k]))for k in('K','G','sf','sd','cf')})
  if min(p[k]for k in('K','G','c','cf'))<=0 or not 0<p['sf']<1 or not 0<p['sd']<1:return {'status':'invalid-resolved-coefficient-domain'}
 parent,loading,current=vec(case['parent']),vec(case['loading']),vec(case['current']);tf=lintrial(parent,loading,Kf,Gf);a=cart(list(map(fd,tf)))
 params=[]if resolved else parameter_changes(p)
 hf=[]if resolved else[lintrial(vec(seed['parent']),vec(seed['loading']),Kf,Gf)for seed in seeds]
 hs=[cart(list(map(fd,h)))for h in hf]
 zero_change={k:Z for k in('K','G','c','sf','cf','sd')};changes=[zero_change.copy()for _ in hf]
 for name,dp in params:
  hm=[-x for x in el(list(map(fd,loading)),dp['K'],dp['G'])];hs.append(cart(hm));changes.append(dp)
 vals,method,ps,dls,dps,sres=spectral_data(a,hs,precision);l=law(p);chosen,roots,guards,admissible,distances=classify(vals,p,l)
 branches={};stress_scale=max(norm(a),abs(p['c']),abs(l['h']),max(map(abs,map(fd,current))),D('1e-100000'))
 direction_scales=[max(max(map(abs,map(fd,vec(seed['current'])))),norm(hs[j]),D('1e-100000'))for j,seed in enumerate(seeds)]if not resolved else[]
 for branch in('elastic','face','left','right','apex'):
  b=branch_result(branch,vals,p,l,roots,ps,dls,dps,hs,changes)
  if b['status']!='defined':branches[branch]=b;continue
  source=a if branch=='elastic'else b.pop('matrix');dmat=b.pop('dmatrices');returned=[-x for x in mandel(source)]
  b['returned_atlas']=returned;b['residual']=[fd(x)-r for x,r in zip(current,returned)];b['source_interval_admissible']=admissible[branch]
  if not resolved:
   b['directions']=[]
   for j,dm in enumerate(dmat[:38]):
    ret=[-x for x in mandel(dm)];dc=list(map(fd,vec(seeds[j]['current'])))
    b['directions'].append({'returned_atlas':ret,'residual':[x-y for x,y in zip(dc,ret)]})
   b['parameter_directions']={}
   for (name,_),dm in zip(params,dmat[38:]):
    ret=[-x for x in mandel(dm)];b['parameter_directions'][name]={'returned_atlas':ret,'residual':[-x for x in ret]}
  else:b['derivative_status']='not-computed-optional-diagnostic'
  branches[branch]=b
 # KKT/reference identities checked for the strict-source selected branch only.
 b=branches[chosen];checks={'spectral_maximum_normalized_residual':sres,'source_selected_branch_defined':b['status']=='defined','interval_unique':sum(admissible.values())==1,'selected_interval_admissible':admissible[chosen]}
 if b['status']=='defined':
  r=b['source_principal_return'];g=b['gamma'];yieldr=(1+p['sf'])*r[0]-(1-p['sf'])*r[2]-l['h']
  checks['returned_order_violation']=max(Z,r[1]-r[0],r[2]-r[1])/stress_scale
  checks['selected_yield_violation']=max(Z,yieldr)/stress_scale if chosen=='elastic'else abs(yieldr)/stress_scale
  if chosen!='elastic'and g>0:
   v=[(vals[i]-r[i]-g*l['A'])/(2*p['G']*g)for i in range(3)]
   checks['flow_sum_error']=abs(sum(v)-2*p['sd'])
   checks['flow_bounds_or_order_violation']=max(Z,v[0]-1-p['sd'],v[1]-v[0],v[2]-v[1],-1+p['sd']-v[2])
   checks['flow_complementarity_error']=max(abs((v[0]-1-p['sd'])*(r[0]-r[1])),abs((v[2]+1-p['sd'])*(r[1]-r[2])))/stress_scale
   checks['flow_subgradient']=v
 return {'status':'reference','coefficients':{k:p[k]for k in('K','G','c','sf','sd','cf')},'trial_source_mandel':list(map(fd,tf)),'eigenvalues':vals,'eigen_method':method,'selected_branch':chosen,'eigen_gaps':[vals[0]-vals[1],vals[1]-vals[2]],'guards':guards,'branch_distances':distances,'branches':branches,'internal_checks':checks,'stress_scale':stress_scale,'direction_scales':direction_scales,'parameter_direction_scales':{name:max(norm(hs[38+j]),O)for j,(name,_)in enumerate(params)}}

def run(inputs,base):
 data=json.loads(Path(inputs).read_text());assert data['columns']==38 and len(data['seeds'])==38
 out={'identity':'mc-exact-stored-Mandel-independent-Decimal-reference-v1','base_precision':base,'input_sha256':hashlib.sha256(Path(inputs).read_bytes()).hexdigest(),'columns':38,'cases':[],'unresolved':[]}
 for case in data['cases']:
  try:
   extra=precision_extra(case,data['seeds']);precision=base+extra
   with localcontext()as ctx:
    ctx.prec=precision
    result={'id':case['id'],'working_precision':precision,'canonical':interface(case,data['seeds'],precision),'resolved_coefficients_diagnostic':interface(case,data['seeds'],precision,True)}
    out['cases'].append(encode(result))
  except (ArithmeticError,ValueError,KeyError,ZeroDivisionError)as e:out['unresolved'].append({'id':case['id'],'reason':type(e).__name__+': '+str(e)})
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('precision',type=int);p.add_argument('output');a=p.parse_args();result=run(a.inputs,a.precision)
 with gzip.GzipFile(filename=a.output,mode='wb',mtime=0)as f:f.write(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
 print(json.dumps({'base_precision':a.precision,'cases':len(result['cases']),'unresolved':result['unresolved'],'output':a.output}))
