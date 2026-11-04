"""Read/hash current702 actual saved proofs. No network, browser or compiled execution."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;N=R.parent;A=N/'live-release702-actual-v1';REV='70251ec7ab4d18029d9a5e6ad30114acd31a662f';checks=[];pins={}
def read(path):
 b=path.read_bytes();pins[str(path)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return json.loads(b)
def ck(name,value=True):assert value,name;checks.append(name)
run=read(A/'pages-run.json');fast=read(A/'fast-run.json');artifact=read(A/'artifact.json');deploy=read(A/'deployment.json');status=read(A/'deployment-status.json');report=read(A/'verified-upload-http-v1/report.json');members=read(A/'verified-upload-http-v1/members.json');transform=read(A/'verified-upload-http-v1/compressed-transform.json');download=read(A/'artifact-download.json')
for label,x,name in [('Pages',run,'Publish Pages'),('Fast',fast,'Fast CI')]:ck(label+' successful exact702',x['head_sha']==REV and x['name']==name and x['conclusion']=='success'and x['status']=='completed')
ck('Pages exact run41900677802',run['id']==41900677802)
ck('Fast exact run41900165577',fast['id']==41900165577)
ck('artifact exact run/id',artifact['id']==13358887724 and artifact['name']=='github-pages'and artifact['expired']is False and artifact['workflow_run']['head_sha']==REV and artifact['workflow_run']['id']==run['id'])
ck('deployment success exact702',deploy['id']==7556581310 and deploy['sha']==REV and deploy['environment']=='github-pages'and status['state']=='success'and status['deployment_url'].endswith('/7556581310')and status['environment_url']=='https://benjym.github.io/constitutive-atlas/')
ck('actual verifier success exact702',report['status']=='passed-artifact-and-selected-production-http'and report['revision']==REV and report['pages_run_id']==run['id']and report['artifact_id']==artifact['id'])
ck('members1548 exact byte sum',len(members)==report['members']==1548 and sum(x['bytes']for x in members.values())==report['tar_bytes']==260275679)
ck('actual ZIP size and hash receipt',report['download_zip_sha256']==download['sha256']=='ed215bc438e97151120be79c0e0b2fcb57d42f24f0939559ba2c87d2c3765f41'and report['download_zip_bytes']==download['bytes']==217252232)
path=Path(download['private_path']);h=hashlib.sha256();size=0
with path.open('rb')as stream:
 while chunk:=stream.read(1024*1024):h.update(chunk);size+=len(chunk)
ck('private retained ZIP independently SHA/size',h.hexdigest()==download['sha256']and size==download['bytes'])
contract=read(N/'live-release-compressed-verifier-v1/contract-v4.json')
for name,sha in contract['exact_pins'].items():ck('production archive exact pin '+name,members[name]['sha256']==sha)
ck('roles preserved15',len(contract['roles'])==14 and 'atlas.wasm'in members and all(any(p.startswith(role+'/')and p.endswith('.wasm')for p in members)for role in contract['roles']))
ck('production stamp8 exact702',len(report['revision_stamps'])==8 and set(report['revision_stamps'].values())=={REV})
ck('production41 HTTP allmatched',len(report['http'])==41 and all(x['observation_status']=='matched'and x['status']==200 and x['url']=='https://benjym.github.io/constitutive-atlas/'+x['path']and x['bytes']==members[x['path']]['bytes']and x['sha256']==members[x['path']]['sha256']for x in report['http']))
ck('all contract HTTP and revision stamps observed',set(x['path']for x in report['http'])==set(contract['http_paths'])|set(report['revision_stamps']))
compression=transform['compression'];original=read(N/'live-release-compressed-verifier-v1/original-index.json');expected={f"experiments/{e['path']}.gz":e for e in original['experiments']}
ck('all994 decoded mandatory',len(expected)==len(compression['decoded_members'])==compression['entries']==994 and set(expected)==set(compression['decoded_members']))
for name,e in expected.items():
 x=compression['decoded_members'][name]
 ck('decoded original SHA/size '+name,x['decoded']=={'sha256':e['sha256'],'bytes':e['size_bytes']}and x['compressed_sha256']==members[name]['sha256']and x['compressed_bytes']==members[name]['bytes'])
ck('actual index hash bound',compression['actual_index_sha256']==members['experiments/index.json']['sha256'])
ck('source report106 gates',transform['report']['status']=='passed-original-report-gates'and transform['report']['checks']==106 and len(transform['report']['source_literal_gate_names'])==24)
for path,sha in [(N/'live-release-compressed-verifier-v1/manifest.json','515985a2dc1affb2aab32dd4ca6efef2f8c873b0793fc101357fb2ff6e805a44'),(N/'live-release-compressed-verifier-review-v1/decision.json','42b15c7e44623bf30d13e7c784ed053ce7354a7193a77353897aa2f6493cbdc0'),(N/'compression-browser-review-v1/decision.json','16804cec2e6f87335dbdf3a453d2ce97b5f759cdb7d43178c8dc3b0dbad6cfe0')]:
 read(path);ck('exact source/local authority '+str(path),pins[str(path)]['sha256']==sha)
full=read(A/'observations-02/full-jobs.json');pending=[x['name']for x in full['jobs']if x['status']!='completed'or x['conclusion']!='success']
result={'status':'PRELIMINARY_ONLY_E8_PENDING','revision':REV,'count':len(checks),'checks':checks,'concrete_findings':[],'pending_gates':['FinalFullCI41900165308 success and engine identity closure','Frozen complete final live browser numerical validator/download/screenshot/console/negative/mobile/compression packet','Final cleanup/retention receipt'],'saved_FullCI_pending_jobs':pending,'scope':'Read/hash saved records and retained ZIP only; no network/browser/compiled/module/Git/source writes'}
(R/'preliminary-input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps(result,indent=2))
