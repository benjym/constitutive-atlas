"""Read-only merged atlas preservation audit. No model/build/material execution."""
from pathlib import Path
import subprocess,json,hashlib,sys
W=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent;sys.path.insert(0,str(W))
from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt
UP='ac22788b9';OWN='5081b088f';HEAD='8543a0dbe061b506ee09e442400f5015ee6a4ed4'
def git(*args):return subprocess.check_output(['git',*args],cwd=W)
def blob(ref,path):return git('show',ref+':'+path)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def old(ref,path):return json.loads(blob(ref,path))
def profiles(data):s=data.decode();return json.loads(s[s.index('=')+1:].strip().removesuffix(';'))
checks=[]
def check(x,label):
 if not x:raise AssertionError(label)
 checks.append(label)
check(git('rev-parse','HEAD').decode().strip()==HEAD,'exact merged HEAD')
parents=git('rev-list','--parents','-n','1',HEAD).decode().split();check(len(parents)==3 and parents[1].startswith(OWN) and parents[2].startswith(UP),'genuine merge has VIBE and current atlas parents')
reg='catalogue/approved-models.json';up=old(UP,reg);ours=old(OWN,reg);now=load(W/reg)
check({k:v for k,v in now.items() if k!='models'}=={k:v for k,v in up.items() if k!='models'},'all upstream registry top-level metadata exact')
vibe=next(a for a in ours['models'] if a['model_id']=='vibe-2026');check(now['models']==up['models']+[vibe],'registry exact upstream29 followed by exact VIBE v2')
check(len(up['models'])==29 and len(now['models'])==30,'29 upstream and1 new VIBE approval retained')
review=validate_review(W/vibe['review']['path'],root=W,for_approval=True);check(vibe==approval_entry(W/vibe['review']['path'],root=W),'VIBE v2 registry exact accepted generated approval')
check(vibe['review']['path'].endswith('vibe-2026-appendix-a-agent-v2.json'),'current VIBE v2 retained')
for p in vibe['supporting_files']:check(sha(W/p['path'])==p['sha256'],'VIBE support current live hash '+p['path'])
check(len(vibe['supporting_files'])==281,'all281 VIBE v2 support pins checked')
for a in now['models']:
 check(sha(W/a['definition']['path'])==a['definition']['sha256'],'current approved model exact '+a['id'])
 if a['review']['kind']=='agent-model-review':
  r=validate_review(W/a['review']['path'],root=W,for_approval=True);check(r['model']['id']==a['model_id'],'all-nine accepted review '+a['id'])
manifest='catalogue/manifest.json';a=old(UP,manifest);b=load(W/manifest)
check({k:v for k,v in a.items() if k!='models'}=={k:v for k,v in b.items() if k!='models'},'catalogue top-level metadata exact')
check(len(a['models'])==len(b['models']) and [r['id'] for r in a['models']]==[r['id'] for r in b['models']],'every upstream catalogue row and order retained')
for x,y in zip(a['models'],b['models']):
 if x['id']!='vibe-2026':check(x==y,'upstream catalogue entry exact '+x['id'])
 else:check(y==next(r for r in old(OWN,manifest)['models'] if r['id']=='vibe-2026'),'VIBE executable controlled-time route exact')
a=profiles(blob(UP,'web/model-profile-data.mjs'));b=profiles((W/'web/model-profile-data.mjs').read_bytes());c=profiles(blob(OWN,'web/model-profile-data.mjs'))
check(set(a)==set(b),'all upstream reader profile IDs retained')
for n,v in a.items():check(b[n]==(c[n] if n=='vibe-2026' else v),'reader profile exact '+n)
app=(W/'web/app.js').read_text();restored=app
for text,count in [("import {setupControlledTimeLaboratory} from './controlled-time-laboratory.mjs';\n",1),("setupControlledTimeLaboratory({chart,cancelOrdinary:()=>cancel('')}),",1),("||entry.controlled_time_laboratory==='index.html'",2)]:
 check(restored.count(text)==count,'exact additive VIBE app edit '+text);restored=restored.replace(text,'')
check(restored.encode()==blob(UP,'web/app.js'),'removing only VIBE additions restores complete upstream app byte-for-byte')
check('loadApplicability();' in app and 'async function loadApplicability()' in app,'upstream applicability setup and invocation retained')
check("setupControlledTimeLaboratory({chart" in app,'VIBE main laboratory setup retained')
mapname='catalogue/agent-reviews/source-archive-map.json';a=old(UP,mapname);b=load(W/mapname)
check(all(b['documents'].get(n)==h for n,h in a['documents'].items()),'all upstream immutable archive document pins exact')
check(set(b['documents'])-set(a['documents'])=={'catalogue/agent-reviews/s-clay1-agent-v1.json'},'only newly preserved S-CLAY1 document pin appended')
check(b['documents']['catalogue/agent-reviews/s-clay1-agent-v1.json']=='a144221194a97861bb91900108471c668c5e9fe98ee6bf5bd2a2e2a1c80f0a48','exact original S-CLAY1 document bytes pinned')
check(b['entries'][:len(a['entries'])]==a['entries'],'all upstream historical archive entries retained exact in order')
check(b['entries'][len(a['entries']):]==load(W/'docs/ingestion/vibe-2026/integration-v1/historical-preservation-receipt.json')['added'],'exact five previously reviewed historical source mappings appended upstream')
for item in git('ls-tree','-r',UP,'catalogue','web').decode().splitlines():
 metadata,path=item.split('\t',1);upstream_blob=metadata.split()[2]
 if path in [reg,manifest,mapname,'web/model-profile-data.mjs','web/app.js']:continue
 check((W/path).is_file() and hashlib.sha1(b'blob '+str((W/path).stat().st_size).encode()+b'\0'+(W/path).read_bytes()).hexdigest()==upstream_blob,'all upstream catalogue/web committed bytes retained '+path)
# The main VIBE public engine and all declared execution source hashes remain exact.
q=load(W/'web/engines/controlled-time/public-qualification.json')
for p in q['source_files']:check(sha(W/p['path'])==p['sha256'],'public compiled closure exact '+p['path'])
check((W/'web/engines/controlled-time/public-qualification.json').read_bytes()==(W/q['root_receipt_path']).read_bytes(),'qualified public receipt exact retained root bytes')
changed=git('diff','--name-only',OWN,HEAD,'atlas','cpp','schemas').decode().splitlines();check(changed==[],'merge changes no existing VIBE compiler/runtime/schema source bytes')
report=dict(identity='independent-vibe2026-current-main-merge-preservation-v1',head=HEAD,upstream=git('rev-parse',UP).decode().strip(),vibe_parent=git('rev-parse',OWN).decode().strip(),checks=checks,count=len(checks),approvals=dict(upstream=29,merged=30,vibe_supports=281,vibe_review_sha256=vibe['review']['sha256']),compiled_calls=0,scope='merge preservation/source integrity only; no new build or browser qualification')
(O/'preservation-results.json').write_text(json.dumps(report,indent=2)+'\n');print('Merge preservation checks:',len(checks))
