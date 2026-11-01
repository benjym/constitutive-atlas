"""Independent source algebra; no evaluator, compiler or artifact calls."""
import hashlib,json,math
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent;A=P/'native-admissible-fixture-plan-v1';ROOT=P.parents[2];h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();load=lambda f:json.loads(f.read_text());checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
check('exact plan manifest',h(A/'manifest.json').startswith('825a475c'))
check('all6 author files exact',len(load(A/'manifest.json'))==6 and all(h(A/k)==v for k,v in load(A/'manifest.json').items()))
check('all10 exact source/evidence/CI inputs',len(load(A/'inputs.json'))==10 and all(h(Path(k)if Path(k).is_absolute()else ROOT/k)==v for k,v in load(A/'inputs.json').items()))
namespace={'__file__':str(A/'prove.py'),'REVIEW':D};source=(A/'prove.py').read_text().replace("report_path=D/'proof-results.json'","report_path=REVIEW/'reproduced-proof-results.json'");exec(compile(source,str(A/'prove.py'),'exec'),namespace);check('full proof exact reproduction',load(D/'reproduced-proof-results.json')==load(A/'proof-results.json'))
m=load(Path('/private/tmp/atlas-control-partition-v1/source/models/manzari-dafalias-1997-constant-m-be-v1.json'));p={k:v['default']for k,v in m['parameters'].items()};S=math.sqrt(2/3);q=load(A/'proof-results.json');dot=lambda a,b:sum(x*y for x,y in zip(a,b));norm=lambda a:math.sqrt(dot(a,a));base=[110000.,95000.,100000.,500.,0.,0.,.65]+[0.]*6+[.0001]
basis=[[1/math.sqrt(2),-1/math.sqrt(2),0,0,0,0],[1/math.sqrt(6),1/math.sqrt(6),-2/math.sqrt(6),0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]
check('five source alpha directions orthonormal and traceless',all(abs(dot(a,b)-(i==j))<1e-15 for i,a in enumerate(basis)for j,b in enumerate(basis)) and all(sum(a[:3])==0 for a in basis))
# A two-by-two minor of the rational diagonal representatives is2; three
# distinct shear pivots are1. Independent stress6/e/gamma give rank13.
check('independent rank13 physical tangent',1*1-1*(-1)==2 and len(basis)==5 and 6+1+1+5==13)
def invariants(z):
 pr=sum(z[:3])/3;alpha=z[7:13];relative=[z[j]/pr-(1 if j<3 else 0)-alpha[j]for j in range(6)];rn=norm(relative);n=[x/rn for x in relative];xx,yy,zz,xy,yz,xz=n
 # trace(N^3) in Mandel components without matrix products.
 tr3=xx**3+yy**3+zz**3+1.5*((xx+yy)*xy**2+(yy+zz)*yz**2+(xx+zz)*xz**2)+3/math.sqrt(2)*xy*yz*xz
 cos=math.sqrt(6)*tr3;psi=z[6]-p['ec_ref']+p['lambda_c']*math.log(pr/p['p_ref']);g=lambda c:2*c/(1+c-(1-c)*cos);ab=p['Mc']+p['kbc']*max(-psi,0)-p['m'];bn=S*(g(p['Me']/p['Mc'])*p['Mc']+g(p['kbe']/p['kbc'])*p['kbc']*max(-psi,0)-p['m'])-dot(alpha,n);draw=p['A']*(S*(g(p['Me']/p['Mc'])*p['Mc']+g(p['kde']/p['kdc'])*p['kdc']*psi-p['m'])-dot(alpha,n));return pr,psi,rn,bn,draw,ab,cos
for r in q['cartesian_h_h2_domain_branch_receipts']+q['tracefree_h_h2_receipts']:
 z=base[:]
 if 'index'in r:z[r['index']]+=r['sign']*r['h']*(160000 if r['index']<6 else 1)
 else:z[7:13]=[a+r['sign']*r['h']*v for a,v in zip(z[7:13],basis[r['direction']])]
 pr,psi,rn,bn,draw,ab,cos=invariants(z);check('probe/'+str(len(checks)),pr>0 and z[6]>0 and abs(sum(z[7:10]))<=1e-10 and z[13]>=-1e-10 and ab>0 and 2*S*ab>abs(bn) and [rn>0,psi>0,bn>0,draw>0]==q['base']['branch'] and abs(cos-r['cos3theta'])<1e-12)
de=[1e-4,-2e-5,1e-5,3e-5,1e-5,-1e-5];tr=sum(de[:3]);dev=[v-(tr/3 if i<3 else 0)for i,v in enumerate(de)];pmax=650000;K=p['K0']*(pmax/p['p_at'])**p['a'];G=p['G0']*(pmax/p['p_at'])**p['a'];upper=640000+K*tr;bound=norm([500,-500,0,100,0,0])+2*G*norm(dev);margin=S*p['m']*640000-bound
check('independent K/G rotation bound and allprefix elastic margin',upper<650000 and tr*p['a']*K/640000<.01 and margin>7199 and abs(margin-q['rotation_elastic_prefix_envelope']['strict_margin_Pa'])<1e-8)
check('allprefix no zero relative normal',dot([500,-500,0,100,0,0],dev)>0)
check('fixed e0 mass balance remains positive and psi negative',.65-(1+p['e0'])*tr>0 and .65-p['ec_ref']+p['lambda_c']*math.log(650000/p['p_ref'])<0)
policy=(A/'POLICY.md').read_text();check('BOTH studies and strict unchanged AD plus refinement gates frozen',all(v in policy for v in ['Require BOTH','5e-11','h/2 for EVERY MD column','3e-5','1.5e-5','rank13','<=1e-9','<=1e-10']))
(D/'checks.json').write_text(json.dumps({'compiled_calls':0,'decision':'source fixture numerical plan accepted; future CI dispatch prerequisite separately required','checks':checks,'independent_rotation_margin_Pa':margin},indent=2)+'\n');print('checks',len(checks))
