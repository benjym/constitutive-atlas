"""Independent source-only fixture review; no Atlas imports or process calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,difflib,math,re
D=Path(__file__).resolve().parent;CAP=D.parent;ROOT=CAP.parents[2]
A=CAP/'native-admissible-fixture-implementation-v1';PLAN=CAP/'native-admissible-fixture-plan-v1';PR=CAP/'native-admissible-fixture-review-v1'
checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def check(name,condition):
 checks.append({'id':name,'passed':bool(condition)});assert condition,name
check('exact author manifest',sha(A/'manifest.json')=='a80f24bfd03f0d8717fc492449f77fb431de0e5812d7ffe94580c1071211cf3f')
for name,h in load(A/'manifest.json').items():check('author-byte/'+name,sha(A/name)==h)
check('exact accepted numerical plan',sha(PLAN/'manifest.json')=='825a475ce35c23fbf0f78220737d865b6c836836d97e2b74af6af913721cb23b')
check('exact separate prospective plan review',sha(PR/'manifest.json')=='111b0817e512bfb594450d8fbd9f56c7bf5104b07ab1ce6d34b9248ad358e531')
for packet in [PLAN,PR]:
 receipt=load(packet/'manifest.json');files=receipt.get('review_files',receipt.get('files',receipt))
 for name,h in files.items():check(packet.name+'/'+name,sha(packet/name)==(h['sha256']if isinstance(h,dict)else h))
for name,h in load(A/'inputs.json').items():check('author-input/'+name,sha(ROOT/name)==h)
f=load(A/'source-freeze.json');S=Path(f['source_directory']);oldreceipt=ROOT/f['original_receipt'];old=load(oldreceipt);O=Path(old['source_directory'])
check('original closure identity',sha(oldreceipt)==f['original_receipt_sha256']=='4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8')
check('same exact582 paths',len(f['source_files'])==len(old['source_files'])==582 and f['source_files'].keys()==old['source_files'].keys())
check('no unbound files in isolated clone',sorted(f['source_files'])==sorted(str(p.relative_to(S))for p in S.rglob('*')if p.is_file()))
check('isolated582 all exact',all(sha(S/n)==h for n,h in f['source_files'].items()))
check('original582 all exact',all(sha(O/n)==h for n,h in old['source_files'].items()))
changed=[n for n in f['source_files']if f['source_files'][n]!=old['source_files'][n]]
check('only authorized test file changed',changed==['tests/test_solver.cpp'])
check('new file hash/public copy',sha(S/changed[0])==sha(A/'test_solver.cpp')=='0ff8a5a459203dc8f254e3c4dcc3f9d3d859285e460956b7a05c70e30486f44f')
check('original public copy exact',sha(A/'original_test_solver.cpp')==old['source_files'][changed[0]])
a=(A/'original_test_solver.cpp').read_text();b=(A/'test_solver.cpp').read_text()
ops=difflib.SequenceMatcher(None,a.splitlines(True),b.splitlines(True),autojunk=False).get_opcodes()
removed=[];inserted=[]
for tag,i,j,k,l in ops:
 if tag in ['delete','replace']:removed+=a.splitlines(True)[i:j]
 if tag in ['insert','replace']:inserted+=b.splitlines(True)[k:l]
check('only old loop dispatch line replaced',removed==['            for(int j=0;j<n;++j){\n'])
old_assertions=re.findall(r'^.*require\(.*$',a,re.M)
check('all25 complete original assertion lines retained',len(old_assertions)==25 and all(b.count(line)>=a.count(line)for line in set(old_assertions)))
check('all later transaction and refinement tests byte-identical',a[a.index('        // Hidden zero-history crossing:'):]==b[b.index('        // Hidden zero-history crossing:'):])
check('unchanged old FD body preserved',a[a.index('                double h=1e-6;'):a.index('        // A fixed 90-degree')]==b[b.index('                double h=1e-6;'):b.index('        // A fixed 90-degree')])
check('new derivative path guarded MD-only', 'if(md_admissible&&atlas::models()[model].id=="manzari-dafalias-1997-constant-m-be-v1")'in b)
check('rotation changes guarded MD-only','const bool md_rotation=md_admissible&&atlas::models()[m].id=="manzari-dafalias-1997-constant-m-be-v1";'in b)
check('legacy print expression unchanged', 'std::cout<<(explicit_fixtures?"Explicit valid-domain/GIS-depth20 fixtures":"Strict original default fixtures")<<"; models="<<atlas::models().size()<<\'\\n\';'in a and 'std::cout<<(explicit_fixtures?"Explicit valid-domain/GIS-depth20 fixtures":"Strict original default fixtures")<<"; models="<<atlas::models().size()<<\'\\n\';'in b)
# Guard ordering and closed tokens, by source inspection, not executable claims.
for token in ['unknown native fixture profile','unknown numerical fixture profile','MD numerical fixture requires exact v5 pairing','MD numerical fixture requires exact14 layout','MD numerical fixture parameter/layout identity','MD numerical fixture requires exactly one MD model']:
 check('pre-work guard/'+token,b.index(token)<b.index('std::cout<<')<b.index('// Independently finite-difference'))
check('native unknown precedence retained',b.index('unknown native fixture profile')<b.index('std::getenv("ATLAS_NUMERICAL_FIXTURES")'))
check('new selector closed empty string rejects','require(!numerical_profile||std::string(numerical_profile)=="md1997-source-admissible-v1"'in b)
check('new selector exact inherited v5 pairing','require(profile&&std::string(profile)=="explicit-gis20-occ-restart-duncan-v5"'in b)
layout='fields.size()==4&&fields[0].name=="sigma"&&fields[0].offset==0&&fields[0].size==6&&fields[1].name=="e"&&fields[1].offset==6&&fields[1].size==1&&fields[2].name=="alpha"&&fields[2].offset==7&&fields[2].size==6&&fields[3].name=="gamma"&&fields[3].offset==13&&fields[3].size==1&&fields[3].multiplier'
check('full ordered declared14 layout guard',layout in b and 'require(count==1' in b)
m=load(S/'models/manzari-dafalias-1997-constant-m-be-v1.json');p={k:v['default']for k,v in m['parameters'].items()};pv=list(p.values())
expected=[100000,160000,31400000,31400000,.6,1.14,1.14,.025,.8,3.975,2.,4.2,.07,1200,.05,2.64,.65]
check('exact17 parameter vector/source identity',pv==expected and sha(S/'models/manzari-dafalias-1997-constant-m-be-v1.json')=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064')
check('expected parameter order actually hardcoded', 'const atlas::State expected={100000,160000,31400000,31400000,.6,1.14,1.14,.025,.8,3.975,2.,4.2,.07,1200,.05,2.64,.65};'in b and 'atlas::default_parameters(int(m))==expected'in b)
check('original scaled AD seeds and immutable parent retained','auto p=atlas::default_parameters(int(model)),z=atlas::initial_state(int(model)),zn=z;'in a and 'x[i].d[i]=scales[i];xn[i]=atlas::Jet(zn[i]);'in b)
check('source scales p_ref6/unit8',[f['scale']for f in m['state']]==['p_ref','1','1','1'])
for token in ['for(int j=0;j<14;++j)','j>=7&&j<=9?5e-11:1e-6','for(int j: {0,1,2,3,4,5,6,13})','v[7]=1/std::sqrt(2.);v[8]=-v[7]','v[7]=v[8]=1/std::sqrt(6.);v[9]=-2/std::sqrt(6.)','for(int j: {10,11,12})','for(int level=0;level<2;++level)','const double step=level?h/2:h','plus[j]+=step*scales[j]*v[j];minus[j]-=step*scales[j]*v[j]','ad+=r[i].d[j]*v[j]','(rp[i]-rm[i])/(2*step)','<3e-5*std::max({1.,std::abs(fd[level][i]),std::abs(ad)})','<1.5e-5*std::max({1.,std::abs(fd[0][i]),std::abs(fd[1][i])})']:
 check('required dual derivative construction/'+token,token in b)
check('both studies mandatory sequential no fallback',b.index('// Full14 ambient')<b.index('// Independent rank13')and 'catch'not in b[b.index('void md_fixture_derivatives'):b.index('int main')])
check('every plus/minus generated residual finite and branch checked',all(t in b for t in ['md_fixture_branch(plus,p)==branch&&md_fixture_branch(minus,p)==branch','atlas::evaluate_model(model,plus,zn,de,p,rp)&&atlas::evaluate_model(model,minus,zn,de,p,rm)','rp.size()==14&&rm.size()==14&&atlas::finite(rp)&&atlas::finite(rm)','std::isfinite(ad)&&std::isfinite(fd[level][i])']))
# Independent scalar trace-cube form, distinct from author's triple matrix loop.
S2=math.sqrt(2/3)
def invariants(z):
 pressure=sum(z[:3])/3;alpha=z[7:13]
 rel=[v/pressure-(i<3)-alpha[i]for i,v in enumerate(z[:6])];rn=math.hypot(*rel);n=[v/rn for v in rel]
 xx,yy,zz,xy,yz,xz=n
 cube=xx**3+yy**3+zz**3+1.5*((xx+yy)*xy**2+(yy+zz)*yz**2+(zz+xx)*xz**2)+3/math.sqrt(2)*xy*yz*xz
 angular=math.sqrt(6)*cube;psi=z[6]-p['ec_ref']+p['lambda_c']*math.log(pressure/p['p_ref'])
 cs=[p['Me']/p['Mc'],p['kbe']/p['kbc'],p['kde']/p['kdc']];den=[1+c-(1-c)*angular for c in cs];g=[2*c/d for c,d in zip(cs,den)]
 dot=sum(u*v for u,v in zip(alpha,n));abc=p['Mc']+p['kbc']*max(-psi,0)-p['m'];bn=S2*(g[0]*p['Mc']+g[1]*p['kbc']*max(-psi,0)-p['m'])-dot
 draw=p['A']*(S2*(g[0]*p['Mc']+g[2]*p['kdc']*psi-p['m'])-dot);y=(pressure*rn-S2*p['m']*pressure)/p['p_ref']
 vals=[*z,pressure,rn,psi,abc,bn,draw,y,*den]
 domain=all(math.isfinite(x)for x in vals)and pressure>0 and z[6]>0 and z[13]>=-1e-10 and abs(sum(alpha[:3]))<=1e-10 and p['Mc']>p['m']and p['Me']>p['m']and abc>0 and 2*S2*abc>abs(bn)
 branch=(rn>0,psi>0,bn>0,draw>0)
 smooth=rn>0 and all(d>0 for d in den)and psi!=0 and bn!=0 and draw!=0 and math.hypot(z[13],y)>0
 return {'domain':domain,'smooth':smooth,'branch':branch,'yield_scaled':y,'relative_norm':rn,'trace':sum(alpha[:3]),'psi':psi,'bn':bn,'D_raw':draw,'bref_margin':2*S2*abc-abs(bn),'angular_denominators':den}
base=[110000.,95000.,100000.,500.,0.,0.,.65]+[0.]*6+[.0001]
scale=[160000.]*6+[1.]*8
basis=[]
for j in range(14):
 v=[0.]*14;v[j]=1;basis.append(('ambient-'+str(j),v,5e-11 if j in [7,8,9]else 1e-6))
for j in [0,1,2,3,4,5,6,13]:
 v=[0.]*14;v[j]=1;basis.append(('tangent-'+str(j),v,1e-6))
for k,w in enumerate([[1/math.sqrt(2),-1/math.sqrt(2),0,0,0,0],[1/math.sqrt(6),1/math.sqrt(6),-2/math.sqrt(6),0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]):basis.append(('tangent-alpha-'+str(k),[0.]*7+w+[0.],1e-6))
check('actual direction counts full14 plus physical13',len(basis)==27 and sum(s.startswith('ambient')for s,v,h in basis)==14)
physical=[v for name,v,h in basis if name.startswith('tangent')]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
check('physical basis orthonormal rank13 and tracefree',len(physical)==13 and all(abs(dot(v,w)-(i==j))<1e-15 for i,v in enumerate(physical)for j,w in enumerate(physical))and all(sum(v[7:10])==0 for v in physical))
basebranch=invariants(base)['branch'];receipts=[]
for name,v,h in basis:
 for level,step in enumerate([h,h/2]):
  for sign in [1,-1]:
   z=[x+sign*step*s*d for x,s,d in zip(base,scale,v)]
   inv=invariants(z)
   check(f'actual-probe/{name}/level{level}/sign{sign}',inv['domain']and inv['smooth']and inv['branch']==basebranch and z!=base)
   receipts.append({'direction':name,'h':step,'sign':sign,'state':z,**inv})
check('all108 actual repeated probes checked',len(receipts)==108)
# Inspect branch helper against all source domains and the nonsmooth nodes.
for token in ['atlas::finite(z)&&atlas::finite(p)','pressure>0&&z[6]>0&&z[13]>=-1e-10','std::abs(z[7]+z[8]+z[9])<=1e-10','p[5]>p[14]&&p[6]>p[14]','std::isfinite(rr)&&rr>0','std::isfinite(denominator)&&denominator>0','abc>0&&2*S*abc>std::abs(bn)','psi!=0&&bn!=0&&draw!=0','std::hypot(z[13],yield)>0']:
 check('source domain and smooth branch/'+token,token in b)
# Fixed proper Q reproduces the code's complete Mandel rotation, including shear.
Q=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
def rotate_matrix(v):
 x,y,z,xy,yz,xz=v;q=math.sqrt(2);M=[[x,xy/q,xz/q],[xy/q,y,yz/q],[xz/q,yz/q,z]]
 B=[[sum(Q[i][k]*M[k][l]*Q[j][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)]
 return [B[0][0],B[1][1],B[2][2],q*B[0][1],q*B[1][2],q*B[0][2]]
for i in range(6):
 v=[0.]*6;v[i]=1;want=[v[1],v[0],v[2],-v[3],v[5],-v[4]]
 check('proper rotation Mandel basis/'+str(i),all(abs(x-y)<1e-15 for x,y in zip(want,rotate_matrix(v))))
rotation=[640500.,639500.,640000.,100.,0.,0.,.65]+[0.]*7
zr=rotate_matrix(rotation[:6])+rotation[6:]
check('source admissible original and rotated parent',all(invariants(z)['domain']and invariants(z)['smooth']and invariants(z)['yield_scaled']<=1e-8 for z in [rotation,zr]))
de=[1e-4,-2e-5,1e-5,3e-5,1e-5,-1e-5];tr=sum(de[:3]);dev=[x-(tr/3 if i<3 else 0)for i,x in enumerate(de)]
K=p['K0']*(650000/p['p_at'])**p['a'];G=p['G0']*(650000/p['p_at'])**p['a'];norm=lambda v:math.sqrt(dot(v,v))
upper=640000+K*tr;devbound=norm([500,-500,0,100,0,0])+2*G*norm(dev);margin=S2*p['m']*640000-devbound
check('independent whole elastic prefix source envelope',upper<650000 and margin>7199 and tr*p['a']*K/640000<.01 and dot([500,-500,0,100,0,0],dev)>0 and .65-(1+p['e0'])*tr>0 and .65-p['ec_ref']+p['lambda_c']*math.log(650000/p['p_ref'])<0)
for token in ['z[0]=640500;z[1]=639500;z[2]=640000;z[3]=100;z[4]=z[5]=0','atlas::domain(int(m),z,p,true)&&atlas::domain(int(m),zr,p,true)','require(a.ok&&b.ok','a.state.size()==14&&b.state.size()==14&&atlas::finite(a.state)&&atlas::finite(b.state)','atlas::domain(int(m),a.state,p)&&atlas::domain(int(m),b.state,p)','auto alpha=rotate(atlas::tensor_from(a.state,7));for(int i=0;i<6;++i)','std::abs(alpha.v[i]-b.state[7+i])<=1e-9','std::abs(a.state[6]-b.state[6])<=1e-10&&std::abs(a.state[13]-b.state[13])<=1e-10','std::abs(want.v[i]-b.state[i])<.01']:
 check('complete rotation contract/'+token,token in b)
check('strain/rotation/settings/source setup inherited',all(t in a and t in b for t in ['de.v={.0001,-.00002,.00001,.00003,.00001,-.00001}','b.v={a.v[1],a.v[0],a.v[2],-a.v[3],a.v[5],-a.v[4]}','atlas::IntegrationSettings fixture_settings;','fixture_settings.max_depth=20']))
check('new-mode label requirement actually in accepted plan','Emit a distinct profile label for the new mode.'in (PLAN/'README.md').read_text())
label_missing='md_admissible'not in b[b.index('std::cout<<'):b.index('// Independently finite-difference')]
check('B1 missing distinct new-mode stdout independently confirmed',label_missing)
# No implementation is run. The absent label is a review finding, not a passing
# implementation assertion hidden behind this source-only check's success.
result={'identity':'independent-md1997-native-fixture-implementation-review-v1','reviewer':'/root/md1997_source','author':'/root/md1997_reference','independence':'reviewer did not author tests/test_solver.cpp or the numerical plan; authored separate CI compatibility plan only','checks_passed':len(checks),'checks':checks,'decision':'BLOCKED','blocking_findings':['B1'],'compiled_calls':0,'compiler_calls':0,'builds':0,'source_changes_verified':changed,'elastic_prefix_margin_Pa':margin,'all_probe_count':108,'source_review_only':True}
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
(D/'probe-receipts.json').write_text(json.dumps({'identity':'independent108-actual-fixture-domain-branch-probes-v1','compiled_calls':0,'receipts':receipts},indent=2)+'\n')
inputs={'author_manifest':{'path':str(A/'manifest.json'),'sha256':sha(A/'manifest.json')},'isolated_source_freeze':{'path':str(A/'source-freeze.json'),'sha256':sha(A/'source-freeze.json')},'accepted_plan_manifest':{'path':str(PLAN/'manifest.json'),'sha256':sha(PLAN/'manifest.json')},'accepted_plan_review_manifest':{'path':str(PR/'manifest.json'),'sha256':sha(PR/'manifest.json')},'additional_reviewed_sources':{n:sha(S/n)for n in ['atlas/compiler.py','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp','models/manzari-dafalias-1997-constant-m-be-v1.json']}}
(D/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
print(json.dumps({'source_checks_passed':len(checks),'decision':'BLOCKED','blocking_findings':['B1'],'compiled_calls':0}))
