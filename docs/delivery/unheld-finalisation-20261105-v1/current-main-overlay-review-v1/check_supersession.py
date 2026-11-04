"""Manufactured integrity-only review history; no constitutive/model execution."""
from pathlib import Path
import copy,hashlib,json,sys,tempfile
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(ROOT))
from atlas.agent_review import approval_entry,validate_review
from atlas.review_export import collect
h=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def yes(ok,name):
 if not ok:raise AssertionError(name)
 checks.append(name)
def main():
 with tempfile.TemporaryDirectory(prefix='owned-supersession-',dir=P)as tmp:
  r=Path(tmp);(r/'models').mkdir();(r/'catalogue/agent-reviews').mkdir(parents=True);(r/'docs').mkdir();(r/'docs/fixture.txt').write_text('Manufactured integrity fixture; no scientific results.\n')
  canonical=r/'models/fixture.json';old=b'{"id":"fixture","version":"old"}';new=b'{"id":"fixture","version":"current"}';artifact={'path':'docs/fixture.txt','sha256':h((r/'docs/fixture.txt').read_bytes())}
  template=json.loads((ROOT/'catalogue/agent-reviews/linear-elastic-agent-v1.json').read_bytes())
  def record(which,data):
   x=copy.deepcopy(template);x.update(id='fixture-'+which,source_commit='0'*40,model={'id':'fixture','path':'models/fixture.json','sha256':h(data)},reviewer={'kind':'agent','name':'Manufactured reviewer','run_id':'fixture/reviewer','independence_basis':'Synthetic metadata only, not an actual scientific review.'},author_run_ids=['fixture/author'],scope='Manufactured integrity-only fixture, no scientific claim.',limitations=['Synthetic fixture only.'],artifacts=[artifact],checklist=[dict(id=c['id'],outcome='pass',reason='Synthetic integrity fixture only.',evidence=['docs/fixture.txt'])for c in template['checklist']]);return x
  oldrecord=record('old',old);newrecord=record('new',new);oldpath=r/'catalogue/agent-reviews/fixture-old.json';newpath=r/'catalogue/agent-reviews/fixture-new.json';registry=r/'catalogue/approved-models.json';sidecar=r/'catalogue/agent-reviews/source-archive-map.json';archive=r/'catalogue/source-snapshots'/h(old)/'models/fixture.json';archive.parent.mkdir(parents=True)
  def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
  canonical.write_bytes(old);write(oldpath,oldrecord);oldapproval=approval_entry(oldpath,root=r);originalregistry={'models':[oldapproval]};originalraw=json.dumps(originalregistry).encode();historicalregistry=r/'catalogue/source-snapshots'/h(originalraw)/'catalogue/approved-models.json';historicalregistry.parent.mkdir(parents=True);historicalregistry.write_bytes(originalraw)
  canonical.write_bytes(new);write(newpath,newrecord);newapproval=approval_entry(newpath,root=r)
  def reset():
   canonical.write_bytes(new);archive.write_bytes(old);write(oldpath,oldrecord);write(newpath,newrecord);write(registry,{'models':[newapproval]});write(sidecar,{'version':'immutable-source-archive-map-0.1','documents':{str(p.relative_to(r)):h(p.read_bytes())for p in [oldpath,newpath]},'entries':[{'original_path':'models/fixture.json','sha256':h(old),'archived_path':str(archive.relative_to(r))}]})
  def rejected(name,action=lambda:collect(r,{'fixture'})):
   try:action()
   except (ValueError,OSError):checks.append(name);return
   raise AssertionError('Corruption accepted: '+name)
  reset();rows,originals,omitted=collect(r,{'fixture'});by={x['id']:x for x in rows}
  yes(not omitted and len(rows)==2,'both old and current reviews exported without omission')
  yes(by['fixture-old']['definition_current']is False and by['fixture-old']['registered_approval_id']is None and by['fixture-old']['status']=='accepted','old exact review remains historical accepted/noncurrent/unregistered')
  yes(by['fixture-new']['definition_current']is True and by['fixture-new']['registered_approval_id']==newapproval['id'],'only exact current review actively registered')
  yes(originals['catalogue/agent-reviews/definitions/fixture-old.json']==old and historicalregistry.read_bytes()==originalraw,'old reviewed definition and old registry bytes remain exact')
  yes(validate_review(newpath,root=r,for_approval=True)['model']['sha256']==h(new),'current exact review validates for approval')
  rejected('historical archive cannot approve current bytes via approval API',lambda:validate_review(oldpath,root=r,for_approval=True))
  reset();archive.unlink();rejected('missing historical archive blocks projection')
  reset();archive.write_bytes(b'corrupt');rejected('historical archive corruption blocks projection')
  reset();mapping=json.loads(sidecar.read_bytes());mapping['entries']=[];write(sidecar,mapping);rejected('missing intrinsic archive mapping blocks projection')
  reset();recordbad=copy.deepcopy(oldrecord);recordbad['checklist'].pop();write(oldpath,recordbad);mapping=json.loads(sidecar.read_bytes());mapping['documents'][str(oldpath.relative_to(r))]=h(oldpath.read_bytes());write(sidecar,mapping);rejected('unregistered historical review still requires complete checklist')
  reset();bad=copy.deepcopy(newapproval);bad['scope']['use']='altered';write(registry,{'models':[bad]});rejected('active approval scope mismatch blocks projection')
  reset();recordbad=copy.deepcopy(newrecord);recordbad['reviewer']['run_id']='fixture/author';write(newpath,recordbad);mapping=json.loads(sidecar.read_bytes());mapping['documents'][str(newpath.relative_to(r))]=h(newpath.read_bytes());write(sidecar,mapping);rejected('current self-review still rejected')
  reset();canonical.write_bytes(b'{"id":"fixture","version":"wrong"}');rejected('current definition drift rejects without historical approval transfer')
 yes(not list(P.glob('owned-supersession-*'))and not list(Path(tempfile.gettempdir()).glob('atlas-review-export-*')),'owned fixture contexts cleaned')
 print(json.dumps({'identity':'current-source-active-supersession-integrity-witness-v1','status':'PASS','checks':len(checks),'names':checks,'constitutive_model_material_compiled_calls':0,'fixture_cleanup':'complete'},indent=2))
if __name__=='__main__':main()
