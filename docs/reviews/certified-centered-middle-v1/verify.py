"""Saved-only independent design replay with pinned source receipts."""
from pathlib import Path
import json,hashlib,sys,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2]
def verify():
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 for n,h in json.loads((P/'source-pins.json').read_text()).items():checked_receipt(ROOT,str((P/'source-pins.json').relative_to(ROOT)),n,h)
 s=importlib.util.spec_from_file_location('centered_saved_checks',P/'check.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);report=m.run();assert report==json.loads((P/'checks.json').read_text())
 process=json.loads((P/'check-process.json').read_text());assert process['returncode']==0 and json.loads(process['stdout'])=={k:v for k,v in report.items()if k!='rows'}
 assert report['pass']and report['literal_cases']==1160 and report['original_tresca_trial_tensors']==61 and report['invalid_rejections']==78
 return report
if __name__=='__main__':print(json.dumps({'saved_evidence_verified':True,'design_pass':verify()['pass'],'builds':0,'material_calls':0}))
