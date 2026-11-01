"""Saved-only failed-default checkpoint. Does not run a model or browser."""
import hashlib,json,math,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(path,h):
 p=Path(path);relative=p.relative_to(ROOT)if p.is_absolute()else p;assert '..'not in relative.parts
 live=ROOT/relative
 if live.is_file()and sha(live)==h:return live
 archived=ROOT/'catalogue/source-snapshots'/h/relative;assert archived.is_file()and sha(archived)==h,(path,'exact archived source missing');return archived
def verify():
 for name in ['manifest.json','default-check-freeze.json']:
  for path,h in read(HERE/name)['files'].items():pin(path,h)
 old=read(HERE/'default-check-process.json');assert old['returncode']==1 and not old['stderr'];d=json.loads(old['stdout']);s=d['specification'];r=d['result'];assert not r['ok']and len(r['points'])==1 and r['points'][0]['state']==s['initial']and len(s['initial'])==14
 assert s['target']==.01 and s['steps']==100 and s['integration_settings']['max_depth']==14
 receipt=read(HERE/'diagnostic-process.json');assert receipt['returncode']==0;rows=json.loads(receipt['stdout'])['results'];assert len(rows)==5
 assert [v['response']['ok']for v in rows[:4]]==[True,False,True,True]
 assert [(v['depth'],v['amount'])for v in rows[:4]]==[(14,1.25e-6),(14,1e-4),(20,1.25e-6),(20,1e-4)]
 assert rows[1]['response']['state']==s['initial']and rows[1]['response']['diagnostics']['substeps']==0 and rows[1]['response']['diagnostics']['rejected']==15
 fractions=rows[3]['response']['diagnostics']['increment_fractions'];assert min(fractions)==2**-16 and math.fsum(fractions)==1
 assert rows[4]['response']['ok']and len(rows[4]['response']['points'])==101 and rows[4]['specification']['integration_settings']['max_depth']==20
 identity=read(HERE/'artifact-identity.json');assert identity['artifacts']==read(ROOT/'docs/reviews/gis2024-mixed-catalogue-v1/wasm-artifacts.json')['artifacts']and identity['new_builds']==0
 # Private engine paths in the diagnostic freeze are matched to the retained
 # artifact identity; replay does not require those private files to survive.
 for path,h in read(HERE/'diagnostic-freeze.json')['files'].items():
  if path.startswith('/private/tmp/atlas-gis2024-mixed-catalogue-v1/wasm/'):assert identity['artifacts'][path]==h
  else:pin(path,h)
 proposal=read(HERE/'example-proposal.json');p=read(HERE/'example-provenance.json');archive=ROOT/p['source_archive'];assert sha(archive)==p['source_archive_sha256']
 with tarfile.open(archive,'r:gz')as t:
  member=t.extractfile('receipts/'+str(p['raw_receipt']).zfill(4)+'.json');raw=member.read();assert hashlib.sha256(raw).hexdigest()==p['raw_receipt_sha256'];original=json.loads(json.loads(raw)['stdout'])['response'];assert proposal['result']==original
 spec=proposal['specification'];assert proposal['result']['ok']and len(proposal['result']['points'])==9 and len(spec['initial'])==14 and len(spec['parameters'])==19 and spec['target']==1e-5 and spec['steps']==8 and spec['integration_settings']['max_depth']==20
 assert read(HERE/'example-proposal-process.json')['returncode']==0
 return {'checkpoint_integrity_pass':True,'standard_default_pass':False,'failed_default_full14_rollback':True,'diagnostic_cases':5,'example_document_validation_pass':True,'public_installation':False,'browser_checks':0,'new_builds':0,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
