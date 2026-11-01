"""Check this packet and contract only; no trajectories or compiled execution."""
import hashlib,json,re
from pathlib import Path
from check_crosswalk import run,HERE,ROOT

def main():
 for name in ['inputs.json','manifest.json']:
  for rel,expected in json.loads((HERE/name).read_text())['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected,rel
 result=run();assert result==json.loads((HERE/'checks.json').read_text())
 for target in re.findall(r'\]\(([^)]+)\)',(HERE/'README.md').read_text()):
  if not target.startswith('https://'):assert (HERE/target).exists(),target
 print(json.dumps({'saved_packet_integrity':True,'v03_contract_pass':True,'initialization_negatives_rejected':len(result['rejected_initializations']),'historical_legacy_model_identity_matches':True,'existing_model_bytes_unchanged':True,'new_trajectory_or_compiled_calls':0,'scientific_admission':False},indent=2))
if __name__=='__main__':main()
