"""Pin reviewed source and independently check old-request preservation."""
from pathlib import Path
import gzip,json,hashlib,argparse

def main(root,out):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
 a=load(root/'requests.json.gz');b=load(root/'reference/requests.json.gz')
 for current,old in zip(a,b):
  assert current['id']=='expr/'+old['id']
  for k in('case','operation','kind','values','seeds'):
   if k in old:assert current[k]==old[k],(current['id'],k)
  assert current['primitive_expected_status']==old['expected_status']
  assert current['expected_ok']==(old['expected_status']=='ok')
 assert len(b)==1136 and len(a)==1589
 proof={'identity':'generated-context-request-source-review-v1','old_requests':len(b),'first_primitive_requests_unchanged':True,'old_invalid_requests_without_case_metadata':sum('case'not in r for r in b),'actual_requests':len(a),'actual_models':len(list((root/'models').glob('*.json'))),'compiled_observations':0,'source_review_findings':[{'id':'R1','status':'fixed-before-freeze','scope':'full independent recovery/fresh vectors now emitted and checked'}]}
 (out/'source-review-checks.json').write_text(json.dumps(proof,indent=2)+'\n')
 paths=[root/p for p in('driver.cpp','CMakeLists.txt','generate.py','static_checks.py','execute.py','policy.json','slots.json','requests.json.gz','requests.txt.gz','wire.json','history.json')]
 for sub in('models','generated','frozen','reference'):paths.extend(p for p in(root/sub).rglob('*')if p.is_file()and '__pycache__'not in p.parts)
 entries={str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in sorted(set(paths))}
 (out/'source-pins.json').write_text(json.dumps({'identity':'spectral-context-assessor-source-pins-v1','root_at_review':str(root),'files':entries,'compiled_observations':0},indent=2,sort_keys=True)+'\n')
 print(json.dumps({'primitive_pairs':len(b),'source_pins':len(entries)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('out');a=p.parse_args();main(a.root,a.out)
