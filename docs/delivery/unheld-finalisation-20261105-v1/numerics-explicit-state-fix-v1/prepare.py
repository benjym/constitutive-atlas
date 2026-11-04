from pathlib import Path
import json,hashlib,gzip
P=Path(__file__).resolve().parent;ROOT=P.parents[3];W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
def sha(b):return hashlib.sha256(b).hexdigest()
path='tools/test_numerics.mjs';old=(W/path).read_bytes();s=old.decode();changes=[
("['--mode','run','--model',row.model,'--protocol'","['--mode','run','--model',row.model,'--initial',row.parent.join(','),'--protocol'"),
("[row.model,'','',1,.001,8,0,csv]","[row.model,'',row.parent.join(','),1,.001,8,0,csv]"),
("['--mode','run','--model','linear-elastic','--protocol'","['--mode','run','--model','linear-elastic','--initial',rows[0].parent.join(','),'--protocol'"),
("['linear-elastic','','',1,.001,8,0,settingsCsv(limited)]","['linear-elastic','',rows[0].parent.join(','),1,.001,8,0,settingsCsv(limited)]"),
("['--mode','integrate','--model','linear-elastic','--strain'","['--mode','integrate','--model','linear-elastic','--initial',rows[0].parent.join(','),'--strain'"),
("['linear-elastic','','','0,0,0,0,0,0',invalid]","['linear-elastic','',rows[0].parent.join(','),'0,0,0,0,0,0',invalid]")]
for a,b in changes:assert s.count(a)==1;s=s.replace(a,b)
q=P/'proposed'/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
archive='catalogue/source-snapshots/'+sha(old)+'/'+path;qold=P/'proposed'/archive;qold.parent.mkdir(parents=True,exist_ok=True);qold.write_bytes(old)
rows=json.loads(gzip.decompress((W/'catalogue/investigations/update-tangent-v1/results.json.gz').read_bytes()))[:5];proof=[]
for row in rows:
 modelpath='models/'+row['model']+'.json';current=(W/modelpath).read_bytes();legacyhash={'linear-elastic':'33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041','drucker-prager':'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877','modified-cam-clay':'e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14','hypoplastic-sand-vw96':'1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61','hypoplastic-sand-igs97':'83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86'}[row['model']]
 legacy_path=f'catalogue/source-snapshots/{legacyhash}/{modelpath}';legacy=(W/legacy_path).read_bytes();assert sha(legacy)==legacyhash
 def flatten(raw):return [v for f in json.loads(raw)['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
 assert flatten(legacy)==flatten(current)==row['parent']
 proof.append({'model':row['model'],'legacy':{'path':legacy_path,'sha256':sha(legacy)},'current':{'path':modelpath,'sha256':sha(current)},'declared_initial':flatten(current),'legacy_implicit_initial':flatten(legacy),'frozen_row_parent':row['parent'],'exact_equal':True})
(P/'initial-equivalence.json').write_text(json.dumps({'state_materialization_source':'cpp/include/atlas/solver.hpp:20 (field order, each size/initial component)','source_row_file':{'path':'catalogue/investigations/update-tangent-v1/results.json.gz','sha256':sha((W/'catalogue/investigations/update-tangent-v1/results.json.gz').read_bytes())},'rows':proof},indent=2)+'\n')
files=[]
for target in [path,archive]:
 data=(P/'proposed'/target).read_bytes();base=W/target
 files.append({'path':target,'preimage_sha256':sha(base.read_bytes()) if base.is_file() else None,'sha256':sha(data),'bytes':len(data),'mode':'100644','proposal':'proposed/'+target})
(P/'source-delta.json').write_text(json.dumps({'scope':'six exact explicit-initial argument substitutions only plus intrinsic original archive','files':files},indent=2)+'\n')
(P/'substitutions.json').write_text(json.dumps(changes,indent=2)+'\n')
failures=ROOT/'docs/delivery/unheld-finalisation-20261105-v1/publication-v1/ramberg-failure-v1';pins={f.relative_to(ROOT).as_posix():{'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in failures.glob('*-raw.log')};assert len(pins)>=2
for rel in ['cpp/include/atlas/solver.hpp','cpp/main.cpp','atlas/compiler.py','web/numerics.mjs']:
 pins[rel]={'sha256':sha((W/rel).read_bytes()),'bytes':(W/rel).stat().st_size}
(P/'source-and-failure-pins.json').write_text(json.dumps(pins,indent=2)+'\n');print('Prepared six exact wire substitutions; five legacy/default states equal frozen row parents')
