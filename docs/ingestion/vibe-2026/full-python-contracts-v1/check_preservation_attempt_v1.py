"""Pure exact archive/approval/receipt proof, including fail-closed negatives."""
from pathlib import Path
import hashlib,json,tempfile,sys
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
from atlas.research import approved_definitions
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 plan=json.loads((P/'preservation-plan-v2.json').read_text());v3=json.loads((P/'preservation-plan-v3.json').read_text());rows=plan['bindings']+[{'document':v3['document'],'document_sha256':v3['document_sha256'],**v3['source_archive']}]
 for row in rows:
  assert sha(R/row['document'])==row['document_sha256'];target=checked_receipt(R,row['document'],row['original_path'],row['sha256']);assert target==R/row['archived_path'] and sha(target)==row['sha256']
 # Existing API rejects missing bindings, unknown hashes and corrupt/missing
 # archived bytes, even when an unchanged live source happens to exist.
 negatives=0
 with tempfile.TemporaryDirectory(prefix='atlas-receipt-negative-') as directory:
  root=Path(directory);document='receipt/check.json';source='tests/original.py';blob=b'original\n';h=hashlib.sha256(blob).hexdigest();archive='catalogue/source-snapshots/'+h+'/'+source
  def put(name,data):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  put(source,blob);put(archive,blob);receipt={'files':{source:h}};put(document,(json.dumps(receipt)+'\n').encode());mapping={'version':'immutable-source-archive-map-0.1','documents':{document:sha(root/document)},'entries':[{'original_path':source,'sha256':h,'archived_path':archive}]};put('receipt/source-archive-map.json',(json.dumps(mapping)+'\n').encode());assert checked_receipt(root,document,source,h)==root/archive
  for path,expected in [('tests/unbound.py',h),(source,'0'*64)]:
   try:checked_receipt(root,document,path,expected)
   except ValueError:negatives+=1
   else:raise AssertionError('Unbound source accepted')
  for corrupt in [True,False]:
   if corrupt:put(archive,b'corrupt')
   else:(root/archive).unlink()
   try:checked_receipt(root,document,source,h)
   except ValueError:negatives+=1
   else:raise AssertionError('Archive silently fell back to live source')
 definitions,records=approved_definitions();reviews=[]
 for record in records:
  if record.get('review',{}).get('kind')!='agent-model-review':continue
  path=R/record['review']['path'];validate_review(path,for_approval=True)
  if record.get('approval_authority',{}).get('kind')=='independent-agent-review':assert approval_entry(path)==record
  reviews.append({'path':record['review']['path'],'sha256':sha(path)})
 vibe=next(a for a in records if a['model_id']=='vibe-2026');supports=[]
 for pin in vibe['supporting_files']:
  target=checked_receipt(R,vibe['review']['path'],pin['path'],pin['sha256']);assert sha(target)==pin['sha256'];supports.append({**pin,'selected_exact_path':str(target.relative_to(R))})
 assert len(supports)==281 and len(records)==30 and len(reviews)==26
 return {'kind':'full-python-preservation-proof-v3','document_bound_resolutions':len(rows),'source_records_unchanged':True,'archive_negative_gates':negatives,'registry_approved_records':len(records),'exact_approved_definitions':len(definitions),'agent_reviews':reviews,'vibe_supporting_files':supports,'note':'Registry281artifactbytes remain exact; historical test source bindings are separately resolved to canonical archives. No claim changed test files match historical hashes at live paths.','compiled_calls':0}
if __name__=='__main__':
 out=check();(P/'preservation-proof-v3.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['agent_reviews','vibe_supporting_files']}))
