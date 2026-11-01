"""Saved-only laboratory-route replay: no binaries, builds or ODE calls."""
import hashlib,json,tarfile,tempfile
from pathlib import Path
from assess import audit,read,ROOT,HERE,BASE
from parity import compare
from waveform_review import review
from tools.reference_gis2024_coupled import coupled_rates

def verify():
 for filename in ['freeze.json','dependencies.json','manifest.json']:
  for path,h in read(HERE/filename)['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,(filename,path)
 policy=read(BASE/'policy.json');model=read(ROOT/policy['identity']['model_path']);rates=read(HERE/'rate-references.json');assert len(rates)==26 and len({r['id']for r in rates})==26
 reference_error=0.
 for row in rates:
  z=row['initial'];p=dict(zip(model['parameters'],row['parameters']));expected=coupled_rates({'sigma':z[:6],'e':z[6],'h':z[7:13],'Omega':z[13]},row['strain'],{k:v for k,v in p.items()if k!='p_scale'})['derivative']
  for x,y in zip(expected,row['expected']):assert abs(x-y)<=1e-10+1e-10*abs(y);reference_error=max(reference_error,abs(x-y))
 saved={};summaries={}
 with tempfile.TemporaryDirectory()as td:
  for backend in ['native','wasm']:
   d=Path(td)/backend;d.mkdir()
   with tarfile.open(HERE/(backend+'-evidence.tar.gz'),'r:gz')as archive:
    for member in archive.getmembers():
     p=Path(member.name);assert not p.is_absolute()and '..'not in p.parts and(member.isfile()or member.isdir())
    archive.extractall(d,filter='data')
   saved[backend]=read(d/'result.json');assessment=audit(saved[backend],d);assert assessment==read(HERE/(backend+'-assessment.json'));summaries[backend]=assessment
   assert review(saved[backend])==read(HERE/'waveform-review.json')[backend]
  parity=compare(saved['native'],saved['wasm']);assert parity==read(HERE/'parity-assessment.json')
 reuse=read(HERE/'artifact-reuse.json');assert reuse['new_builds']==0
 for backend in ['native','wasm']:assert reuse['backends'][backend]==read(ROOT/'docs/reviews/gis2024-mixed-catalogue-v1'/(backend+'-artifacts.json'))
 return {'qualification_pass':True,'backends':summaries,'parity':parity,'literal_reference_replay_max_error':reference_error,'new_builds':0,'browser_checks':0,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
