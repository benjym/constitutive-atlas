from pathlib import Path
import hashlib,json,shutil,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/mc-root-integration-v3';plan=json.loads((P/'archive-plan.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
for n,h in plan['original_bytes'].items():assert sha(R/n)==h,n
created=[]
for n,h in plan['original_bytes'].items():
 dest=R/'catalogue/source-snapshots'/h/n
 if dest.exists():assert sha(dest)==h
 else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,dest);created.append(dest.relative_to(R).as_posix())
for side,bindings in plan['sibling_document_bindings'].items():
 p=R/side;m=json.loads(p.read_text())if p.exists()else{'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 for n,h in bindings.items():
  assert n not in m['documents']or m['documents'][n]==h,(n,'existing document drift');m['documents'][n]=h
 for ref in plan['references']:
  if ref['sidecar']==side:
   n,h=ref['original_path'],ref['sha256'];entry={'original_path':n,'sha256':h,'archived_path':'catalogue/source-snapshots/'+h+'/'+n}
   if entry not in m['entries']:m['entries'].append(entry)
 js(p,m)
side=P/'source-archive-map.json';own={'version':'immutable-source-archive-map-0.1','documents':{(P/'archive-plan.json').relative_to(R).as_posix():sha(P/'archive-plan.json')},'entries':[{'original_path':n,'sha256':h,'archived_path':'catalogue/source-snapshots/'+h+'/'+n}for n,h in plan['original_bytes'].items()]};previous=json.loads(side.read_text())if side.exists()else{'documents':{},'entries':[]}
own['documents']={**previous['documents'],**own['documents']}
own['entries']=previous['entries']+[e for e in own['entries']if e not in previous['entries']]
js(side,own)
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
for ref in plan['references']:assert sha(checked_receipt(R,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256']
for n,h in plan['original_bytes'].items():assert sha(checked_receipt(R,(P/'archive-plan.json').relative_to(R),n,h))==h
js(P/'archive-result.json',{'created_snapshots':created,'sidecars_modified':list(plan['sibling_document_bindings']),'new_packet_sidecar':side.relative_to(R).as_posix(),'receipt_edges_preserved':len(plan['references'])})
