"""Read-only pre-install verification; intercepts the default preflight file write."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import json,hashlib,runpy,sys,subprocess,tempfile,sqlite3
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=BASE.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 sys.path.insert(0,str(ROOT))
 freeze=json.loads((BASE/'INSTALL_SOURCE_FREEZE.json').read_text())
 for n,h in freeze.items():
  if sha(ROOT/n)!=h:raise RuntimeError('changed pre-install input '+n)
 installer=runpy.run_path(str(BASE/'install.py'),run_name='review_import')
 saved=(BASE/'PREFLIGHT.json').read_text();writes=[]
 def intercept(path,text,*args,**kwargs):
  if path!=BASE/'PREFLIGHT.json' or text!=saved:raise RuntimeError('unexpected attempted write')
  writes.append(str(path));return len(text)
 with patch.object(sys,'argv',['install.py']),patch.object(Path,'write_text',intercept):installer['main']()
 if len(writes)!=1:raise RuntimeError('preflight interception')
 optimized=subprocess.run([sys.executable,'-B','-O',str(BASE/'install.py')],capture_output=True,text=True)
 if optimized.returncode==0 or 'installation refused' not in optimized.stderr:raise RuntimeError('optimized installer not refused')
 bad_paths=['../outside','/tmp/outside','catalogue/../outside']
 for n in bad_paths:
  try:installer['safe'](n)
  except AssertionError:continue
  raise RuntimeError('unsafe destination accepted '+n)
 from atlas.evidence import checked_receipt
 plan=json.loads((BASE/'PLAN.json').read_text())
 with tempfile.TemporaryDirectory(prefix='clay2013-future-map-review-') as tmp:
  tmp=Path(tmp)
  for row in plan['maps']:
   dest=tmp/row['original_path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((BASE/row['candidate']).read_bytes())
   for pin in row['document_pins']:
    dest=tmp/pin['original_document'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/pin['original_document']).read_bytes())
  for row in plan['archives']:
   dest=tmp/row['canonical_archive'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((BASE/row['snapshot']).read_bytes())
  dest=tmp/'catalogue/approved-models.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((BASE/'registry-proposed.json').read_bytes())
  for row in plan['baseline']:
   actual=checked_receipt(tmp,row['document'],row['original_path'],row['old_sha256'])
   if sha(actual)!=row['old_sha256']:raise RuntimeError('future archive mismatch')
 old=json.loads((BASE/'registry-observed.json').read_text());new=json.loads((BASE/'registry-proposed.json').read_text())
 return {'status':'PASS','source_freeze_inputs':len(freeze),'default_preflight_write_intercepted_exactly':True,'operations':json.loads(saved)['operations'],'optimized_execution_refused':True,'unsafe_paths_rejected':bad_paths,'future_historical_archive_resolution':True,'registry_before':len(old['models']),'registry_after':len(new['models']),'production_mutations':0,'builds':0,'material_calls':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
