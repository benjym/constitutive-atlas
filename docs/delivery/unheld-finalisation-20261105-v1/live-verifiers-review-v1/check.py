from pathlib import Path
import hashlib,json,importlib.util,tempfile,subprocess,sys,io
H=Path(__file__).resolve().parent;ROOT=H.parents[3];P=H.parent/'live-release-artifact-plan-v1';D=ROOT/'output/playwright/baseline-five-e7-20261105-v1';S=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def ok(name,cond=True):assert cond,name;checks.append(name)
for n,pin in [('manifest.json','342c878025ab331dfe7c62667efe4cb2eeace71c81b7d4d75c42025f8b986d0d'),('browser-validator-v1.manifest.json','bde302f9c8e341ca9adc47d40ec30e764ec7959f1b4fb750dddfab74b5d55f47')]:
 b=(P/n).read_bytes();ok(n+' exact',sha(b)==pin)
 for row in json.loads(b)['files']:
  b=(P/row['path']).read_bytes();ok(row['path']+' bytes',len(b)==row['bytes'] and sha(b)==row['sha256'])
for name in ['model-linear-elastic.js','model-drucker-prager.js','model-modified-cam-clay.js','model-hypoplastic-sand-vw96.js','model-hypoplastic-sand-igs97.js','named.js','negative-mobile.js']:
 old=(D/name).read_text();new=(D/'live'/name).read_text();ok(name+' exact substitutions only',new==old.replace('http://127.0.0.1:8875/constitutive-atlas/','https://benjym.github.io/constitutive-atlas/').replace(str(D),str(D/'live')))
c=json.loads((P/'contract.json').read_text());ok('1549 unique names',len(c['member_paths'])==len(set(c['member_paths']))==1549);ok('16 exact models',len(c['models'])==16);ok('9 exact examples',len(c['example_ids'])==9);ok('14 specialized roles plus ordinary',len(c['roles'])==14)
policy=json.loads((P/'browser-validator-v1.POLICY.json').read_text())
for row in policy['pins']:ok('browser authority '+row['path'],sha(Path(row['path']).read_bytes())==row['sha256'])
gate=json.loads(Path(policy['parity_policy']).read_text());ok('original 1e-10',gate['parity_relative_tolerance']==1e-10)
# Manufactured saved-data fixture: only one CSV data cell differs; all other files link immutable originals.
with tempfile.TemporaryDirectory(prefix='csv-witness-',dir=H)as tmp:
 t=Path(tmp);downloads=t/'downloads';downloads.mkdir()
 for p in D.glob('*.json'): (downloads/p.name).symlink_to(p)
 for p in D.glob('*.csv'):
  if p.name!='linear-elastic-default.csv':(downloads/p.name).symlink_to(p)
 csv=(D/'linear-elastic-default.csv').read_text().splitlines();rows=[r.split(',')for r in csv];at=rows[0].index('axial_strain_1');rows[1][at]='Infinity';(downloads/'linear-elastic-default.csv').write_text('\n'.join(','.join(r)for r in rows)+'\n')
 proc=subprocess.run(['node',str(P/'browser-validator-v1.validate.mjs'),str(downloads),str(S),str(t/'report.json')],capture_output=True,text=True)
 (H/'csv-nonfinite-witness.json').write_text(json.dumps({'mutated':'linear-elastic-default.csv row1 axial_strain_1=Infinity','exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'expected':'reject nonfinite numeric CSV; current source accepts'},indent=2)+'\n');ok('CSV nonfinite witness reproduced',proc.returncode==0)
# Pure mocked HTTP failure, not a network request; use actual main failure/write ordering.
spec=importlib.util.spec_from_file_location('reviewed_artifact',P/'verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='http-witness-',dir=H)as tmp:
 t=Path(tmp);rev='a'*40
 objects={'run':{'head_sha':rev,'conclusion':'success','status':'completed','name':'Publish Pages','id':11},'artifact':{'name':'github-pages','expired':False,'workflow_run':{'id':11,'head_sha':rev},'digest':'sha256:'+'b'*64,'id':22},'deployment':{'sha':rev,'environment':'github-pages','id':33},'status':{'state':'success','deployment_url':'https://api.example/deployments/33','environment_url':'https://example.invalid/site/'}}
 for name,obj in objects.items():(t/(name+'.json')).write_text(json.dumps(obj))
 (t/'artifact.zip').write_bytes(b'owned-inert-fixture')
 members={n:{'sha256':c['exact_pins'].get(n,'c'*64),'bytes':2,'mode':'0o644'}for n in c['member_paths']}
 captured={n:b'{}'for n in c['semantic_json']}
 captured['models.json']=json.dumps({'sha256':c['catalogue_hash'],'models':c['models']}).encode();captured['evidence-records/catalogue/approved-models.json']=json.dumps({'models':[{}]*30}).encode();captured['laboratory-examples.json']=json.dumps({'catalogue_hash':c['catalogue_hash'],'examples':[{'id':i,'document_url':'./laboratory-examples/'+i+'.json','document_sha256':members['laboratory-examples/'+i+'.json']['sha256']}for i in c['example_ids']]}).encode();captured['engine/identity.json']=json.dumps({'release_revision':rev}).encode()
 m.verify_archive=lambda *a:(members,captured)
 class Response(io.BytesIO):
  status=200;url='https://example.invalid/site/mismatch';headers={'X-Witness':'owned-mock'}
 m.urllib.request.urlopen=lambda *a,**k:Response(b'bad bytes')
 oldargs=sys.argv;sys.argv=['verify.py','--revision',rev,'--pages-run',str(t/'run.json'),'--artifact-metadata',str(t/'artifact.json'),'--deployment',str(t/'deployment.json'),'--deployment-status',str(t/'status.json'),'--zip',str(t/'artifact.zip'),'--base-url','https://example.invalid/site/','--output',str(t/'output')]
 try:
  try:m.main()
  except AssertionError as e:
   files=list((t/'output').iterdir());ok('HTTP mismatch rejects',True);ok('HTTP mismatch loses evidence witness',files==[]);(H/'http-failure-witness.json').write_text(json.dumps({'actual_network_calls':0,'failure':str(e),'output_files_after_failure':[str(p)for p in files],'expected':'persist row/hash/status/headers before rejection'},indent=2)+'\n')
  else:raise AssertionError('Expected mismatch failure')
 finally:sys.argv=oldargs
(H/'checks.json').write_text(json.dumps({'status':'SOURCE_REVIEW_WITH_TWO_REPRODUCED_FINDINGS','checks':checks,'count':len(checks),'compiled_browser_network_calls':0,'temporary_resources_remaining':0},indent=2)+'\n');print(json.dumps({'checks':len(checks),'findings':2}))
