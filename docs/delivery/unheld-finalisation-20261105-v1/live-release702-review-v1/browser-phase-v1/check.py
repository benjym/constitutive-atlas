"""Read saved production browser evidence; replay only source-qualified pure validator."""
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
R=Path(__file__).resolve().parent;N=R.parents[1];B=N/'live-release702-browser-v1';A=N/'live-release702-actual-v1';P=N/'live-release-artifact-plan-v1';checks=[]
def ck(name,value=True):assert value,name;checks.append(name)
def read(f):return json.loads(f.read_text())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
ck('exact frozen browser manifest',sha(B/'manifest.json')=='be2c3fdae05c1994c3c5bb98626a6f7b86745fb1ad43ef10b87a6dffbbffe7b9')
m=read(B/'manifest.json')
for x in m['files']:ck('member '+x['path'],sha(B/x['path'])==x['sha256']and (B/x['path']).stat().st_size==x['bytes'])
ck('all97 members exact namespace',{str(f.relative_to(B))for f in B.rglob('*')if f.is_file()}=={'manifest.json',*[x['path']for x in m['files']]})
report=read(B/'report.json');ck('production exact702',report['revision']=='70251ec7ab4d18029d9a5e6ad30114acd31a662f'and report['base_url']=='https://benjym.github.io/constitutive-atlas/'and report['status']=='PASSED_ACTUAL_PRODUCTION_BROWSER_AND_SAVED_DOWNLOADS')
members=read(A/'verified-upload-http-v1/members.json');models=['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']
for name,result in report['results'].items():
 raw=(B/name).read_text();value=json.loads(raw.split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0]);ck('raw summary exact '+name,value==result)
 script=(B/name.removesuffix('.result.txt')).read_text();embedded=raw.split('await (async (page) => {',1)[1].split('\n})(page);',1)[0];ck('raw actual script '+name,embedded.rstrip()==script.rstrip())
for id in models:
 value=report['results']['model-'+id+'.js.result.txt'];ck('model workflow '+id,value['model']==id and value['checks']==['profile-to-laboratory/default/exports','invalid-controls-disable','parameter/state/latest/reset/import-replay'])
 for x in value['hashes']:
  path=x['url'].removeprefix(report['base_url']);ck('live accepted model/review/registry '+id+' '+path,x['status']==200 and x['sha256']==members[path]['sha256'])
 ck('exact three model scientific authorities '+id,len(value['hashes'])==3 and {x['url'].removeprefix(report['base_url'])for x in value['hashes']}=={'evidence-records/catalogue/agent-reviews/'+id+'-v03-agent-v1.json','evidence-records/catalogue/agent-reviews/definitions/'+id+'-v03-agent-v1.json','evidence-records/catalogue/approved-models.json'})
 valueprofile=value['profile'];ck('profile behaviour/state/limits '+id,all(term in valueprofile for term in ['Starting state','Scope and limitations','Read more']))
named=report['results']['named.js.result.txt'];expected=read(Path('/private/tmp/atlas-baseline-delivery-20261105/source/catalogue/laboratory-examples.json'))['examples']
ck('all nine named IDs exact order',[x['id']for x in named]==[x['id']for x in expected])
negative=report['results']['negative-mobile.js.result.txt'];ck('cross-model and wrong-catalogue rejected',negative['checks'][:2]==['cross-model-example-invalidated','wrong-catalogue-import-rejected-inputs-preserved'])
ck('all five mobile routes',set(negative['checks'][2:])=={'mobile-profile-to-lab:'+x for x in models})
compression=report['results']['compression-live-v1.js.result.txt'];ck('normalized/native rows',compression['normalizedRows']==3600 and compression['nativeRows']==200000 and 'No model overlay.'in compression['nativeStatus'])
for x in compression['assets']:
 ck('production compressed HTTP exact '+x['path'],x['url']==report['base_url']+x['path']and x['status']==200 and x['bytes']==members[x['path']]['bytes']and x['sha256']==members[x['path']]['sha256'])
ck('four compression assets',len(compression['assets'])==4)
requesttext=(B/'requests-all-cli.txt').read_text();rows=re.findall(r'^\d+\. \[(\w+)\] (\S+) => \[(\d+)\]',requesttext,re.M)
ck('all929 recorded HTTP200',len(rows)==929 and all(x[2]=='200'for x in rows))
ck('console raw zero', (B/'console-cli.txt').read_text().strip()=='### Result\nTotal messages: 0 (Errors: 0, Warnings: 0)')
ck('18 saved screenshots',len([x for x in m['files']if x['path'].endswith('.png')])==18)
ck('frozen v2 source manifest',sha(P/'manifest-v2.json')=='62e7dea099f881bc6b0a32d0b781dc0319e590ef35828883cc2b6da209757f9e')
for x in read(P/'manifest-v2.json')['files']:ck('v2 source member '+x['path'],sha(P/x['path'])==x['sha256']and (P/x['path']).stat().st_size==x['bytes'])
ck('independent v2 source acceptance',sha(N/'live-verifiers-review-v1/v2/decision.json')=='dba212a978acaa3e9f0c39206b5997c959ef60803a86258e3fc897cd6fcdc6fa')
ck('validator source exact',sha(P/'browser-validator-v2.validate.mjs')=='ba5cf01cf2ab36770187e607e3778d3d5d1d30cf7111e50f1ce65040f8185d15')
with tempfile.TemporaryDirectory(prefix='pure-validator-',dir=R)as tmp:
 output=Path(tmp)/'result.json';argv=['node',str(P/'browser-validator-v2.validate.mjs'),str(B),'/private/tmp/atlas-baseline-delivery-20261105/source',str(output)];p=subprocess.run(argv,capture_output=True)
 (R/'validator.stdout.txt').write_bytes(p.stdout);(R/'validator.stderr.txt').write_bytes(p.stderr);(R/'validator.receipt.json').write_text(json.dumps({'argv':argv,'exit_code':p.returncode,'scope':'pure saved JSON/CSV validation; no browser/compiled module/network'},indent=2)+'\n')
 ck('pure validator true exit0',p.returncode==0)
 replay=read(output);(R/'validator-replay.json').write_text(json.dumps(replay,indent=2)+'\n');ck('original579 unchanged saved gates',replay['checks']==579 and replay['status']=='PASS_SAVED_DOWNLOADS')
 ck('exact parent validator report',replay==read(B/'browser-download-validation.json'))
ck('temporary purevalidator output removed',not Path(tmp).exists())
print(json.dumps({'status':'PASS_PRODUCTION_BROWSER_PHASE_ONLY','independent_saved_checks':len(checks),'source_qualified_download_checks':579,'checks':checks,'compiled_module_browser_network_calls':0},indent=2))
