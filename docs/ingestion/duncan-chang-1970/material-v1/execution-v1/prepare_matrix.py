"""Freeze the remaining full material study before its compiled observations."""
from pathlib import Path
from decimal import Decimal as Q,localcontext
import json,math,hashlib,sys,struct
B=Path(__file__).resolve().parent;P=B.parent;sys.path.insert(0,str(P))
from reference import q,eigen,compliance,history,residual
R=B.parents[4];old=json.loads((P/'candidate.json').read_text());m=json.loads((P/'candidate.json').read_text());m['name']='Duncan–Chang (1970), constant ν, endpoint-average';m['description']='Original 1970 effective-stress, constant-Poisson, isotropic incremental 3D closure with project endpoint-principal averaging, maximum stress-difference history, explicit primary/equality/unloading branches and a positive numerical postfailure modulus. Compression-positive Mandel components; fixed spatial infinitesimal zero-spin frame; explicit stress/history preparation. Selected scalar cluster-average tie rows are not unique classical or proven whole-residual Clarke derivatives. Parameter examples illustrate source coefficients; no calibration, experimental validation, finite-rotation or arbitrary-path convergence claim.'
(B/'candidate.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');assert {k for k in m if m[k]!=old[k]}=={'name','description'}
refs=json.loads((P/'references.json').read_text())
for case in refs['cases']:
 if case['id'].endswith('-signed-permutation'):case.update(rotation=[[0,1,0],[-1,0,0],[0,0,-1]],rotation_partner=case['id'].split('-')[0]+'-distinct')
hyp=json.loads((P/'refinement-references.json').read_text());dense=refs['cases'][0]['parameters'];loose=next(c['parameters'] for c in refs['cases'] if c['id']=='loose-history-0');params={'dense':dense,'loose':loose};paths=[]
for r in hyp['rows']:
 paths.append(dict(id=r['id'],kind='hyperbola',parameters=r['parameters'],initial=r['initial'],increments=[r['de']]*r['steps'],expected_D=r['expected_D'],hyperbola_D=r['hyperbola_D'],F=r['F']))
for label,p in params.items():
 group=[next(c for c in refs['cases'] if c['id']==f'{label}-history-{i}') for i in range(8)]
 paths.append(dict(id=label+'-propagated-source-history',kind='known-history',parameters=p,initial=group[0]['initial'],increments=[c['de'] for c in group],targets=[c['target'] for c in group]))
 Ei=p['K']*p['pa']*(100000./p['pa'])**p['n'];F=2*(p['c_cohesion']*math.cos(p['phi'])+100000.*math.sin(p['phi']))/(1-math.sin(p['phi']));failure_strain=F/(Ei*(1-p['Rf']));total_failure=2*failure_strain
 for kind,initial,total in [('max-crossing',history([150000,100000,100000,0,0,0],100000.),.003),('failure-crossing',history([100000]*3+[0]*3),total_failure)]:
  for n in (16,32,64,128):
   de=total/n;paths.append(dict(id=f'{label}-{kind}-{n}',kind=kind,parameters=p,initial=initial,increments=[[de,-p['nu']*de,-p['nu']*de,0.,0.,0.]]*n,partitions=n,source_failure_strain=failure_strain if kind=='failure-crossing' else None))
# Domain-valid discontinuity-root gap derived before observing these requests.
p=dense|{'phi':0.,'c_cohesion':100000.,'nu':0.};initial=history([190000,100000,100000,0,0,0],100000.);de=[.00008,-p['nu']*.00008,-p['nu']*.00008,0.,0.,0.]
with localcontext() as c:
 c.prec=160;Ei=q(p['K'])*q(p['pa'])*(Q(100000)/q(p['pa']))**q(p['n']);Eur=q(p['Kur'])*q(p['pa'])*(Q(100000)/q(p['pa']))**q(p['n']);Eprimary=Ei*(1-q(p['Rf'])*Q(95000)/Q(200000))**2;lo=Q(10000)/Eur;hi=Q(10000)/Eprimary;assert lo<q(de[0])<hi and q(de[0])/2<lo
proof=dict(source='fixedconfinement cohesive phi0,F200000,Dn90000,hn100000',Eur=str(Eur),Eprimary_at_history_boundary=str(Eprimary),gap_min_axial_strain=str(lo),gap_max_axial_strain=str(hi),wire_axial_strain=de[0],half_below_gap=True,interpretation='At D<h_n root requires eps<lo; at D>=h_n primary root requires eps>=hi locally and monotone primary compliance through this boundary. Chosen unsplit increment has no supported root; no posthoc failure reclassification.')
transactions=[dict(id='analytical-gap-unsplit',parameters=p,initial=initial,de=de,settings=[2e-10,1e-6,45,0,20000,11],expect_success=False,min_internal_substeps=0),dict(id='analytical-gap-late-parent-rollback',parameters=p,initial=initial,de=de,settings=[2e-10,1e-6,45,14,1,11],expect_success=False,min_internal_substeps=1)]
additional=[]
# General rounded rotation of distinct stresses: reference uses actual stored matrix.
a=.37;axis=[1/math.sqrt(14),2/math.sqrt(14),3/math.sqrt(14)];K=[[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]];rot=[[math.cos(a)*(i==j)+(1-math.cos(a))*axis[i]*axis[j]+math.sin(a)*K[i][j] for j in range(3)] for i in range(3)]
for label,p in params.items():
 source=next(c for c in refs['cases'] if c['id']==label+'-distinct');v=source['target'];A=[[v[0],v[3]/math.sqrt(2),v[5]/math.sqrt(2)],[v[3]/math.sqrt(2),v[1],v[4]/math.sqrt(2)],[v[5]/math.sqrt(2),v[4]/math.sqrt(2),v[2]]];cart=[[sum(rot[i][k]*A[k][l]*rot[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)];stress=[cart[i][i] for i in range(3)]+[math.sqrt(2)*cart[i][j] for i,j in [(0,1),(1,2),(0,2)]];z=history(stress);zn=history([100000]*3+[0]*3)
 values=[]
 for precision in (100,160):
  with localcontext() as c:
   c.prec=precision;eps,h,branch,S,E=compliance(z,zn,p);values.append(list(eps))
 convergence=max(abs(a-b) for a,b in zip(*values));assert convergence<Q('1e-70')
 with localcontext() as c:
  c.prec=160;eps=list(map(float,values[-1]));rr=residual(z,zn,eps,p);exact_h=max(eigen(z[:6]))-min(eigen(z[:6]));h_error=q(z[6])-exact_h
 additional.append(dict(id=label+'-rounded-general-rotation',parameters=p,initial=zn,target=z,de=eps,branch=branch,wire_residual=[str(x) for x in rr],rotation=rot,rotation_partner=label+'-distinct',reference_convergence=str(convergence),exact_history=str(exact_h),history_encoding_error=str(h_error)))
# Explicit near-distinct diagnostic at a *specified residual evaluation*, not a
# relaxed required successful material update. Numerical primitive policy rejects.
near=history([150000.,100000.,math.nextafter(100000.,math.inf),0.,0.,0.]);diagnostics=[dict(id='near-distinct-unresolved-selected-min',current=near,previous=history([100000]*3+[0]*3),de=[0.]*6,parameters=dense,expect_success=False)]
invalids=[];base=[100000.]*3+[0.]*4
for name,value in [('p_ref',0.),('pa',0.),('K',0.),('Kur',dense['K']-1),('Rf',0.),('Rf',1.),('c_cohesion',-1.),('phi',-1.),('phi',math.pi/2),('nu',-1.),('nu',.5),('E_failure',0.)]:invalids.append(dict(id=f'parameter-{name}-{value}',parameters=dense|{name:value},initial=base,de=[0.]*6))
for name in dense:
 invalids.append(dict(id='nonfinite-parameter-'+name,parameters_csv=','.join('nan' if k==name else repr(v) for k,v in dense.items()),initial=base,de=[0.]*6))
for name,z in [('missing',[]),('short',base[:-1]),('long',base+[0.]),('history',[150000.,100000.,100000.,0.,0.,0.,0.]),('negative-history',base[:-1]+[-1.]),('zero-confinement',[100000.,100000.,0.,0.,0.,0.,100000.]),('negative-confinement',[100000.,100000.,-1.,0.,0.,0.,100001.])]:invalids.append(dict(id='initial-'+name,parameters=dense,initial=z,de=[0.]*6))
invalids.append(dict(id='zero-strength',parameters=dense|{'phi':0.,'c_cohesion':0.},initial=base,de=[0.]*6))
for k in range(7):invalids.append(dict(id='nonfinite-state-'+str(k),parameters=dense,initial_csv=','.join('nan' if j==k else repr(v) for j,v in enumerate(base)),de=[0.]*6))
for k in range(6):invalids.append(dict(id='nonfinite-loading-'+str(k),parameters=dense,initial=base,de_csv=','.join('nan' if j==k else '0' for j in range(6))))
request=dict(identity='duncan-complete-material-api-v1',model=m['id'],candidate_sha256=hashlib.sha256((B/'candidate.json').read_bytes()).hexdigest(),settings=[2e-10,1e-6,45,14,20000,11],cases=refs['cases']+additional,paths=paths,transactions=transactions,diagnostics=diagnostics,invalids=invalids,derivatives=json.loads((P/'smooth-v2.json').read_text())['derivatives'],presets=[dict(id=label+'-source-drained',parameters=p,initial=base,protocol=1,target=.005,steps=128,cycles=0) for label,p in params.items()],proof=proof)
(B/'requests.json').write_text(json.dumps(request,indent=2,allow_nan=False)+'\n')
def bitify(x):
 if isinstance(x,float):return struct.pack('>d',x).hex()
 if isinstance(x,list):return [bitify(y) for y in x]
 if isinstance(x,dict):return {k:bitify(v) for k,v in x.items()}
 return x
(B/'requests-binary64.json').write_text(json.dumps(bitify(request),indent=2)+'\n');print(json.dumps({k:len(request[k]) for k in ['cases','paths','transactions','diagnostics','invalids','derivatives','presets']}))
