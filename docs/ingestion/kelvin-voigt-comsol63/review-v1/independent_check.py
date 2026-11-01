"""Independent review-run source/interpreter checks; no compiled artifacts."""
from pathlib import Path
import hashlib,json,math,random,sys
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parents[3]))
from atlas.model import load,observe,interpret
model=D.parents[3]/'models/research/kelvin-voigt/kelvin-voigt-comsol63-deviatoric-zero-spin-ode.json'
m=load(model)
assert hashlib.sha256(model.read_bytes()).hexdigest()=='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
r=json.loads((D.parent/'source-v1/source-receipt.json').read_text())
for s in r['sources']:
 b=Path(s['private_path']).read_bytes();assert len(b)==s['bytes'] and hashlib.sha256(b).hexdigest()==s['sha256']
P={'K':20e6,'G':12e6,'tau':2.};rnd=random.Random(20261102);mx=energy=0
for n in range(80):
 e=[rnd.uniform(-.007,.007) for _ in range(6)];d=[rnd.uniform(-.002,.002) for _ in range(6)];tr=sum(e[:3]);td=sum(d[:3]);lam=P['K']-2*P['G']/3;eta=P['G']*P['tau']
 # Cartesian Lame form and independently explicit shear transport conversion.
 ref=[]
 for i in range(6):
  factor=math.sqrt(2) if i>=3 else 1;E=e[i]/factor;Dij=d[i]/factor
  ref.append(factor*(2*P['G']*E+2*eta*Dij+(lam*tr-2*eta*td/3)*(i<3)))
 s=list(observe(m,{'eps':e},d,P,time=.3)['stress'].v)
 assert list(interpret(m,{'eps':e},None,d,P,time=.3)['eps'].v)==d
 mx=max(mx,max(abs(x-y) for x,y in zip(s,ref)));assert all(math.isclose(x,y,abs_tol=2e-8,rel_tol=1e-12) for x,y in zip(s,ref))
 ed=[x-(tr/3 if i<3 else 0) for i,x in enumerate(e)];dd=[x-(td/3 if i<3 else 0) for i,x in enumerate(d)]
 loss=2*eta*sum(x*x for x in dd);spring=P['K']*tr*td+2*P['G']*sum(x*y for x,y in zip(ed,dd));work=sum(x*y for x,y in zip(s,d))
 energy=max(energy,abs(work-spring-loss));assert loss>=0 and abs(work-spring-loss)<1e-9
result={'identity':'kelvin-voigt-independent-review-v1','reviewer_run':'/root/kelvin_scientific_review','model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'source_files_verified':len(r['sources']),'interpreter_cases':80,'stress_components':480,'max_stress_error_Pa':mx,'max_energy_balance_error_Pa_per_s':energy,'all_passed':True,'limitations':['Python source/interpreter audit only; backend evidence assessed separately','No experimental validation or finite-rotation claim']}
out=json.dumps(result,indent=2)+'\n';target=__import__('pathlib').Path(__file__).resolve().parent/'independent-check-results.json'
if target.exists():assert target.read_text()==out,'Refuse differing overwrite'
else:target.write_text(out)
print(out,end='')
