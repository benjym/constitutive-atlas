#!/usr/bin/env python3
"""Bounded read-only Git assembly planning; outputs only owned plan/proof metadata."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PUB='106a9cf8c327c9c262a97eb86aa04dae3f6cadb8'
OWN='136636f14ce12b0dd83e65a8c37d3af9a5cc1381'
BASE='54f409b37deaed0ab82a85cdac9f489bc65e1309'
HEAD='feba9188376939a727fe8e69ba62cc3ca6ae73ca'
INDEX='342d4733f48857ecbab58e12c1e40fe8e1a40a0f22fae718bc89a9d9175b5b23'
COMPOSE=ROOT/'docs/ingestion/hypoplastic-interface-2016/publication-composition-v1'
REVIEW=ROOT/'docs/ingestion/hypoplastic-interface-2016/publication-composition-review-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,stderr=subprocess.PIPE)
def local(name):return (ROOT/name).read_bytes()
def changes(a,b):
 parts=git('diff','--name-status','-z','--no-renames',a,b).split(b'\0');out={}
 for i in range(0,len(parts)-1,2):
  status,path=parts[i].decode(),parts[i+1].decode();assert status in ('A','M'),(status,path);out[path]=status
 return out

def tree(ref,paths):
 if not paths:return {}
 rows={}
 for item in git('ls-tree','-r','-z',ref,'--',*sorted(paths)).split(b'\0'):
  if not item:continue
  meta,path=item.split(b'\t',1);mode,kind,oid=meta.decode().split();assert kind=='blob';rows[path.decode()]={'mode':mode,'oid':oid}
 return rows

def main():
 assert git('rev-parse','HEAD').decode().strip()==HEAD and sha((ROOT/'.git/index').read_bytes())==INDEX
 manifest_path=COMPOSE/'MANIFEST.json';manifest_bytes=manifest_path.read_bytes();manifest=json.loads(manifest_bytes)
 assert sha(manifest_bytes)=='8e550aa525163bd732520bacc6e96a6f3424883f47d8eac3e6fefa567b0f2b27' and len(manifest['files'])==107
 for item in manifest['files']:
  data=(COMPOSE/item['path']).read_bytes();assert sha(data)==item['sha256'] and len(data)==item['bytes'],item['path']
 decision=json.loads((REVIEW/'decision.json').read_bytes());assert decision['decision']=='accepted' and not decision['blocking_findings']
 assert decision['manifest_sha256']==sha(manifest_bytes)
 install_path=COMPOSE/'install-map.json';install_bytes=install_path.read_bytes();install=json.loads(install_bytes)
 assert sha(install_bytes)==decision['install_map_sha256']=='4456f57dcc131856ed4ea30184c077307031842bd94d35a23bfaa80fb5b0edcb'
 for item in decision['evidence']:
  data=local(item['path']);assert sha(data)==item['sha256'] and len(data)==item['bytes'],item['path']
 assert len(install['targets'])==49
 ownchanges=changes(BASE,OWN);pubchanges=changes(BASE,PUB);own_tree=tree(OWN,ownchanges);assert set(own_tree)==set(ownchanges)
 assert len(ownchanges)==584 and len(set(ownchanges)&set(pubchanges))==8
 entries={};provenance={};own_selected_bytes=0
 for path,meta in own_tree.items():
  data=git('show',OWN+':'+path);own_selected_bytes+=len(data)
  entries[path]={'path':path,'mode':meta['mode'],'git_source':OWN+':'+path,'sha256':sha(data),'bytes':len(data)};provenance[path]='own Git delta'
 def add_local(path,source,label):
  data=source.read_bytes();entries[path]={'path':path,'mode':'100644','local_source':str(source.relative_to(ROOT)),'sha256':sha(data),'bytes':len(data)};provenance[path]=label
 for item in install['targets']:
  source=COMPOSE/item['source'];data=source.read_bytes();assert sha(data)==item['sha256'] and len(data)==item['bytes']
  add_local(item['target'],source,'accepted composition target')
 for item in manifest['files']:
  source=COMPOSE/item['path'];add_local(str(source.relative_to(ROOT)),source,'accepted proposal member')
 add_local(str(manifest_path.relative_to(ROOT)),manifest_path,'original proposal manifest')
 alias=str((COMPOSE/'manifest.json').relative_to(ROOT));assert alias!=str(manifest_path.relative_to(ROOT));add_local(alias,manifest_path,'same-byte Linux lowercase manifest alias')
 review_files=['REPORT.md','check-results.json','check_saved_composition.py','decision.json','source-reassessment.json']
 for name in review_files:add_local(str((REVIEW/name).relative_to(ROOT)),REVIEW/name,'accepted independent composition review')
 closeout=ROOT/'docs/ingestion/hypoplastic-interface-2016/commit-closeout-v1/actual-commit.json';actual=json.loads(closeout.read_bytes());assert actual['commit']==OWN and actual['parent']=='dcc645785faa3c83d791fdad92e7f3a20cab9721' and not actual['pushed'] and not actual['deployed'];add_local(str(closeout.relative_to(ROOT)),closeout,'actual closeout receipt')
 for name in ['create_commit.py','README.md','prepare_plan.py']:add_local(str((HERE/name).relative_to(ROOT)),HERE/name,'assembly source metadata')
 closure=json.loads((COMPOSE/'required-ledger-closure.json').read_bytes())
 assert len(closure)==7
 for item in closure:
  assert sha(git('show',OWN+':'+item['path']))==item['sha256'];assert entries[item['path']]['sha256']==item['sha256']
 for f,key,count in [('catalogue/manifest.json','models',50),('catalogue/approved-models.json','models',28)]:assert len(json.loads(local(entries[f]['local_source']))[key])==count
 profile=local(entries['web/model-profile-data.mjs']['local_source']).decode();prefix='export const modelProfiles = ';profiles=json.loads(profile[profile.index(prefix)+len(prefix):].rstrip().removesuffix(';'));assert len(profiles)==50 and 'hvwe2016-reconciled-fixed-local' in profiles and 'perzyna-comsol63-mises-perfect-zero-spin-ode' in profiles
 # No proposed row can overwrite a published-only addition/change with unequal bytes.
 published_only=set(pubchanges)-set(ownchanges);published_tree=tree(PUB,set(entries)|published_only);identical=[]
 for path in list(entries):
  row=entries[path];published=published_tree.get(path)
  data=git('show',row['git_source']) if 'git_source' in row else local(row['local_source'])
  oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if published and oid==published['oid'] and row['mode']==published['mode']:identical.append(path);del entries[path]
 assert not (published_only & set(entries)),sorted(published_only & set(entries))
 assert str((HERE/'plan.json').relative_to(ROOT)) not in entries
 plan={'published':PUB,'own':OWN,'common_base':BASE,'root_head':HEAD,'root_index_sha256':INDEX,'ref':'refs/heads/delivery/interface2016-release-v3','scope':'Explicit accepted source composition only; no new package/browser/scientific/deployment acceptance','composition_manifest_sha256':sha(manifest_bytes),'composition_review_decision_sha256':sha((REVIEW/'decision.json').read_bytes()),'entries':[entries[k] for k in sorted(entries)]}
 plan_path=HERE/'plan.json';plan_path.write_text(json.dumps(plan,indent=2)+'\n')
 preflight=subprocess.check_output(['python3','-B',str(HERE/'create_commit.py')],cwd=ROOT).decode();result=json.loads(preflight);assert result['status']=='read-only assembly preflight passed' and result['files']==len(entries)+1
 assert git('rev-parse','HEAD').decode().strip()==HEAD and sha((ROOT/'.git/index').read_bytes())==INDEX
 proof={'passed':True,'source_only':True,'plan_sha256':sha(plan_path.read_bytes()),'assembly_script_sha256':sha((HERE/'create_commit.py').read_bytes()),'composition_manifest_sha256':sha(manifest_bytes),'review_files':{name:sha((REVIEW/name).read_bytes()) for name in review_files},'own_delta_paths':len(ownchanges),'own_delta_selected_bytes':own_selected_bytes,'accepted_composition_targets':49,'accepted_proposal_members':107,'proposal_manifest_destinations':[str(manifest_path.relative_to(ROOT)),alias],'manifest_alias_byte_equality':entries[str(manifest_path.relative_to(ROOT))]['sha256']==entries[alias]['sha256'],'published_only_paths_preserved':len(published_only),'identical_published_entries_filtered':len(identical),'filtered_paths':sorted(identical),'planned_entries':len(entries),'seven_ledger_documents_verified':True,'semantic_counts':{'models':50,'approvals':28,'profiles':50},'preflight':result,'root_head_unchanged':HEAD,'root_index_unchanged':INDEX,'Git_mutations_and_material_package_browser_compiler_remote_calls':0,'proof_not_circularly_included_in_plan':True}
 (HERE/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k] for k in ['passed','plan_sha256','own_delta_paths','planned_entries','identical_published_entries_filtered','published_only_paths_preserved']}));print(preflight.strip())
if __name__=='__main__':main()
