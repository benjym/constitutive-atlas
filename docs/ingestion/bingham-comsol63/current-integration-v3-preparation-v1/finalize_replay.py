"""Recheck the final candidate context; no shared mutation or material calls."""
from pathlib import Path
import gzip,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CONTEXT=HERE/'consumer-context'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
for p in (HERE/'candidates').rglob('*'):
 if p.is_file():
  target=CONTEXT/p.relative_to(HERE/'candidates');assert not target.is_symlink()
  if target.exists():assert target.is_file() and target.stat().st_nlink==1
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
proof=json.loads(gzip.decompress((HERE/'PROOF.json.gz').read_bytes()))
def outcome(root,e):
 try:
  value=checked_receipt(root,e['document'],e['original_path'],e['sha256'])
  return {'ok':True,'sha256':sha(value),'resolved':value.relative_to(root).as_posix()}
 except Exception as error:return {'ok':False,'error_type':type(error).__name__,'error':str(error).replace(str(root),'<ROOT>')}
for edge in proof['edges']:
 assert outcome(ROOT,edge)==edge['before'],edge
 assert outcome(CONTEXT,edge)==edge['after'],edge
for name in ['consumer-context-inventory-final.json.gz','FINAL-REPLAY.json']:assert not (HERE/name).exists()
inventory={p.relative_to(CONTEXT).as_posix():sha(p) for p in CONTEXT.rglob('*') if p.is_file()}
(HERE/'consumer-context-inventory-final.json.gz').write_bytes(gzip.compress((json.dumps(inventory,indent=2)+'\n').encode(),mtime=0))
result={'pass':True,'final_candidate_sha256':{p.relative_to(HERE/'candidates').as_posix():sha(p) for p in (HERE/'candidates').rglob('*') if p.is_file()},'proof_sha256':sha(HERE/'PROOF.json.gz'),'all_edges_replayed':len(proof['edges']),'summary':proof['summary'],'private_context_inventory_sha256':sha(HERE/'consumer-context-inventory-final.json.gz'),'source_only':True,'installed':False,'compiled_calls':0}
(HERE/'FINAL-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary'],indent=2))
