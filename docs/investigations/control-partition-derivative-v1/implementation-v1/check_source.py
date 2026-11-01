"""Read-only checks of exact whitelisted source edits and frozen fixture inputs."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;ROOT=D.parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 for n,h in json.loads((D/'parent-inputs.json').read_text()).items():assert sha(ROOT/n)==h,n
 parent=json.loads((ROOT/'docs/investigations/control-partition-derivative-v1/coordinator-v1/original-source.json').read_text());S=Path(parent['source_directory']);original=D/'original/solver.hpp';assert sha(original)==parent['source_files']['cpp/include/atlas/solver.hpp'];changed=[]
 for n,h in parent['source_files'].items():
  if sha(S/n)!=h:changed.append(n)
 assert changed==['cpp/include/atlas/solver.hpp'],changed
 old=original.read_text();new=(S/'cpp/include/atlas/solver.hpp').read_text();patch=json.loads((D/'exact-edits.json').read_text())
 expected=old
 for item in patch:
  assert expected.count(item['old'])==1,item['identity'];expected=expected.replace(item['old'],item['new'])
 assert new==expected,'unlisted source edit'
 marker='    // protocol 3: prescribed deviator stress change and zero volume change.'
 assert old[old.index(marker):]==new[new.index(marker):],'protocol3 or downstream change'
 for p in D.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 freeze=json.loads((D/'source-freeze.json').read_text());assert len(freeze['source_files'])==582
 for n,h in freeze['source_files'].items():assert sha(S/n)==h,n
 for n in ['cpp/include/atlas/solver.hpp',*freeze['added']]:assert (D/'proposed'/n).read_bytes()==(S/n).read_bytes(),n
 assert len(json.loads((D/'cases.json').read_text())['cases'])==25
 if (D/'manifest.json').exists():
  for n,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/n)==h,n
 print(json.dumps({'status':'passed','source_files':582,'original_source_files':578,'changed':changed,'added':4,'protocol3_and_downstream':'byte-identical','compiled_calls':0,'python_syntax':'passed'}))
if __name__=='__main__':main()
