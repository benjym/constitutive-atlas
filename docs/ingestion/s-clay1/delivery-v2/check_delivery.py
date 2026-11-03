"""Frozen source-packet integrity only; this cannot approve a material model."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--private',action='store_true');args=a.parse_args();m=json.loads((OUT/'manifest-v2.json').read_text())
 for path,h in m['files'].items():assert digest(ROOT/path)==h,path
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 document=str((OUT/'independent-review/review.json').relative_to(ROOT));review=json.loads((ROOT/document).read_text())
 for row in review['inputs']:checked_receipt(ROOT,document,row['path'],row['sha256'])
 private=0
 if args.private:
  for row in json.loads((OUT/'acquisition-v2.json').read_text())['responses']:
   if 'private_path' not in row:continue
   p=ROOT/row['private_path'];assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256'];private+=1
 policy=json.loads((OUT/'checklist-source.json').read_text());checklist=(OUT.parent/'CHECKLIST.md').read_text();assert sum(checklist.count('- ['+v+']') for v in [' ','-','X'])==policy['items']==59
 assert review['source_complete'] is False and review['is_e5_model_approval'] is False
 r={'result':'PASS','scope':'Source packet hashes and historical source receipt resolution only','frozen_files':len(m['files']),'independent_review_input_bindings':len(review['inputs']),'private_receipts_verified':private,'canonical_checks_retained':59,'model_approved':False,'full_delivery_complete':False};print(json.dumps(r,indent=2))
if __name__=='__main__':main()
