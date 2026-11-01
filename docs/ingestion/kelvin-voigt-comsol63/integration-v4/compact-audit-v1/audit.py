"""Read-only portable checks; replay is for use after coordinator installation."""
import hashlib,json,sys,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];sha=lambda b:hashlib.sha256(b).hexdigest()
def readarchive(path,members):
 result={}
 with tarfile.open(path,'r:gz')as t:
  for m in t.getmembers():
   assert m.isfile()and not Path(m.name).is_absolute()and '..'not in Path(m.name).parts and m.name not in result
   result[m.name]=t.extractfile(m).read()
 assert set(result)==set(members)
 for path,h in members.items():assert sha(result[path])==h,path
 return result
if __name__=='__main__':
 a=json.loads((B/'artifact.json').read_text());assert sha((B/'preservation-plan.tar.gz').read_bytes())==a['archive_sha256'];assert sha((B/'members.json').read_bytes())==a['members_sha256'];data=readarchive(B/'preservation-plan.tar.gz',json.loads((B/'members.json').read_text()));assert sha(data['plan.json'])==a['plan_sha256'];assert data['plan.json']==(B/'plan.json').read_bytes();p=json.loads(data['plan.json'])
 s=json.loads((B/'preproposal.json').read_text());assert sha((B/'preproposal-own-context.tar.gz').read_bytes())==s['archive_sha256'];assert sha((B/'preproposal-members.json').read_bytes())==s['members_sha256'];own=readarchive(B/'preproposal-own-context.tar.gz',json.loads((B/'preproposal-members.json').read_text()));assert len(own)==s['members'];v=json.loads((B/'virtual-check.json').read_text());assert v['passed']and v['archive_sha256']==a['archive_sha256'];print('PASS portable archive',len(data),'members; own snapshot',len(own),'members; virtual',v['checked'],'bindings')
 if len(sys.argv)>1 and sys.argv[1]=='replay':
  sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
  for row in p['required_edges']:
   assert sha((R/row['document']).read_bytes())==row['document_sha256'],row['document'];checked_receipt(R,row['document'],row['original_path'],row['sha256'])
  print('PASS all',len(p['required_edges']),'installed historical bindings')
