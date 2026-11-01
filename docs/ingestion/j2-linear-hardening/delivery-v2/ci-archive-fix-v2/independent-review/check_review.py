#!/usr/bin/env python3
"""Complete committed JSON scan and exact historical redirect audit; no compiled execution."""
import hashlib,json,pathlib,re,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[5];SOURCE=HERE/'source'
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda blob:hashlib.sha256(blob).hexdigest()
def git(name,head):return subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)
def run():
 receipts=json.loads((HERE/'manifest.json').read_text())
 for group in ['inputs','outputs']:
  for name,h in receipts[group].items():assert sha((ROOT/name).read_bytes())==h,name
 inv=json.loads((SOURCE/'inventory-before.json').read_text());head=inv['head'];targets={'tests/test_laboratory_view.mjs','tests/test_effective_experiment_browser.mjs'}
 files=subprocess.check_output(['git','ls-tree','-r','--name-only',head],cwd=ROOT,text=True).splitlines();files=[p for p in files if p.endswith('.json') and not p.startswith('catalogue/source-snapshots/')]
 data=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=''.join(head+':'+f+'\n' for f in files).encode(),capture_output=True,check=True).stdout
 def visit(node,out):
  if isinstance(node,dict):
   for path,h in node.items():
    if path in targets and isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h):out.add((path,h))
   if node.get('path') in targets:
    for key in ['sha256','hash']:
     h=node.get(key)
     if isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h):out.add((node['path'],h))
   for v in node.values():visit(v,out)
  elif isinstance(node,list):
   for v in node:visit(v,out)
 offset=0;pairs=set();mentions=0
 for f in files:
  end=data.index(b'\n',offset);size=int(data[offset:end].split()[2]);blob=data[end+1:end+1+size];offset=end+size+2
  if not any(t.encode() in blob for t in targets):continue
  mentions+=1;found=set();visit(json.loads(blob),found);pairs.update((f,*x) for x in found)
 expected={(x['document'],x['path'],x['sha256']) for x in inv['pairs']};assert pairs==expected and len(pairs)==19 and mentions==22
 groups={}
 for row in inv['pairs']:
  assert (SOURCE/row['document']).read_bytes()==git(row['document'],head)
  checked_receipt(SOURCE,row['document'],row['path'],row['sha256'])
  if not row['passed']:groups.setdefault(str(pathlib.Path(row['document']).parent/'source-archive-map.json'),[]).append(row)
 prior=0
 for name,rows in groups.items():
  result=subprocess.run(['git','show',head+':'+name],cwd=ROOT,capture_output=True)
  old=json.loads(result.stdout) if result.returncode==0 else dict(version='immutable-source-archive-map-0.1',documents={},entries=[])
  expected=json.loads(json.dumps(old))
  for row in rows:
   expected['documents'][row['document']]=sha(git(row['document'],head))
   expected['entries'].append(dict(original_path=row['path'],sha256=row['sha256'],archived_path='catalogue/source-snapshots/'+row['sha256']+'/'+row['path']))
  assert json.loads((SOURCE/name).read_text())==expected,name
  if result.returncode==0:
   assert (SOURCE/'catalogue/source-snapshots'/sha(result.stdout)/name).read_bytes()==result.stdout;prior+=1
 assert len(groups)==6 and sum(map(len,groups.values()))==8 and prior==5
 return dict(passed=True,verdict='accept exact eight additive historical redirects',committed_head=head,non_snapshot_JSON_files_scanned=len(files),documents_mentioning_fixture_paths=mentions,exact_receipt_pairs=19,passing_receipt_pairs=19,new_redirects=8,changed_maps=6,preserved_prior_maps=5,new_maps=1,reviewer_compiled_calls=0,scope='Committed bf8a JSON inventory outside immutable source snapshots; no claim about uncommitted or future references. Exact isolated proposal only; unrelated dirty-map additions excluded.',limits=['No historical pins, receipt documents, numerical gates, models, engines or application changed by this proposal.','Remote CI and release verification remain pending.'])
if __name__=='__main__':print(json.dumps(run(),indent=2))
