"""Independent bounded read-only Git/blob overlay audit; no Git writes."""
from pathlib import Path
import hashlib,json,subprocess,collections
R=Path(__file__).resolve().parents[4];P=R/'docs/ingestion/hypoplastic-interface-2016';A=P/'publication-assembly-v1';O=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def read(p):return json.loads(p.read_bytes())
def tree(ref):
 out={}
 for row in git('ls-tree','-r','-z',ref).split(b'\0'):
  if not row:continue
  meta,p=row.split(b'\t',1);mode,kind,oid=meta.decode().split();assert kind=='blob';out[p.decode()]=(mode,oid)
 return out
plan=read(A/'plan.json');assert sha((A/'plan.json').read_bytes())=='d4f11564af271a3dffc77e58bc7d732dcf1b9f5ee0338beef91a03f4dee5a7fe'
assert plan['published']=='106a9cf8c327c9c262a97eb86aa04dae3f6cadb8' and plan['own']=='136636f14ce12b0dd83e65a8c37d3af9a5cc1381'
assert plan['ref']=='refs/heads/delivery/interface2016-release-v3'
head=git('rev-parse','HEAD').decode().strip();ih=sha((R/'.git/index').read_bytes());assert head==plan['root_head'] and ih==plan['root_index_sha256']
base,pub,own=map(tree,[plan['common_base'],plan['published'],plan['own']]);overlay=dict(pub);payload={}
for e in plan['entries']:
 p=e['path'];assert p not in payload and not Path(p).is_absolute() and '..' not in Path(p).parts and '\n' not in p and '\t' not in p
 b=git('show',e['git_source']) if 'git_source' in e else (R/e['local_source']).read_bytes()
 assert sha(b)==e['sha256'] and len(b)==e['bytes'] and e['mode'] in ('100644','100755')
 oid=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();payload[p]=(e['mode'],oid);overlay[p]=payload[p]
assert len(payload)==729 and len(overlay)>=len(pub) and set(pub)<=set(overlay)
assert all(pub.get(p)!=v for p,v in payload.items())
ownchanges={p for p,v in own.items() if base.get(p)!=v};pubchanges={p for p,v in pub.items() if base.get(p)!=v};assert len(ownchanges)==584
published_only=pubchanges-ownchanges;assert len(published_only)==268 and all(overlay[p]==pub[p] for p in published_only)
install=read(P/'publication-composition-v1/install-map.json');composed={e['target'] for e in install['targets']}
for p in ownchanges-composed:assert overlay[p]==own[p],p
for e in install['targets']:
 b=(P/'publication-composition-v1'/e['source']).read_bytes();assert sha(b)==e['sha256'];oid=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert overlay[e['target']]==(e['mode'],oid)
upper='docs/ingestion/hypoplastic-interface-2016/publication-composition-v1/MANIFEST.json';lower=upper.replace('MANIFEST.json','manifest.json');assert payload[upper]==payload[lower]
casegroups=collections.defaultdict(list)
for p in payload:casegroups[p.casefold()].append(p)
collisions=[g for g in casegroups.values() if len(g)>1];assert collisions==[[upper,lower]],collisions
closure=read(P/'publication-composition-v1/required-ledger-closure.json')
for e in closure:
 b=git('show',plan['own']+':'+e['path']);assert sha(b)==e['sha256'] and overlay[e['path']]==own[e['path']]
run=subprocess.check_output(['python3','-B',str(A/'create_commit.py')],cwd=R).decode();preflight=json.loads(run);assert preflight['files']==730
assert git('rev-parse','HEAD').decode().strip()==head and sha((R/'.git/index').read_bytes())==ih
result={'passed':True,'plan_sha256':sha((A/'plan.json').read_bytes()),'planned_entries':len(payload),'commit_entries_including_plan':730,'published_only_paths_preserved':len(published_only),'own_delta_paths':len(ownchanges),'accepted_composition_targets':49,'no_deletions':True,'case_aliases':collisions,'required_ledger_documents_exact':len(closure),'default_read_only_preflight':preflight,'root_HEAD_and_index_unchanged':True,'Git_or_shared_writes':False,'compiled_material_package_browser_remote_calls':0}
(O/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
