"""Explicit current recorded fixtures and separately bound historical runtime."""
import copy,hashlib,json,os,subprocess
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from atlas.model import ROOT
from atlas.recorded import execute_recorded
LEGACY_HASH='1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c'
LEGACY_INPUTS=[{'path': 'catalogue/investigations/clay2005-preview-v1/models/drucker-prager.json', 'receipt': {'path': 'catalogue/investigations/clay2005-preview-v1/manifest.json', 'sha256': 'e5ceffc187f07fe63a2c4e07ad03bbf9940cef6a65c020b36d7178d998d8372c'}, 'receipt_key': 'models/drucker-prager.json', 'sha256': 'd40db28d8de98b7eb8597c90787d16d1f76bac0d145cabb9a5853e86d811650d'}, {'path': 'catalogue/investigations/clay2005-preview-v1/models/hypoplastic-sand-igs97.json', 'receipt': {'path': 'catalogue/investigations/clay2005-preview-v1/manifest.json', 'sha256': 'e5ceffc187f07fe63a2c4e07ad03bbf9940cef6a65c020b36d7178d998d8372c'}, 'receipt_key': 'models/hypoplastic-sand-igs97.json', 'sha256': '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86'}, {'path': 'catalogue/investigations/clay2005-preview-v1/models/hypoplastic-sand-vw96.json', 'receipt': {'path': 'catalogue/investigations/clay2005-preview-v1/manifest.json', 'sha256': 'e5ceffc187f07fe63a2c4e07ad03bbf9940cef6a65c020b36d7178d998d8372c'}, 'receipt_key': 'models/hypoplastic-sand-vw96.json', 'sha256': '1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61'}, {'path': 'catalogue/investigations/clay2005-preview-v1/models/linear-elastic.json', 'receipt': {'path': 'catalogue/investigations/clay2005-preview-v1/manifest.json', 'sha256': 'e5ceffc187f07fe63a2c4e07ad03bbf9940cef6a65c020b36d7178d998d8372c'}, 'receipt_key': 'models/linear-elastic.json', 'sha256': '33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041'}, {'path': 'catalogue/investigations/clay2005-preview-v1/models/modified-cam-clay.json', 'receipt': {'path': 'catalogue/investigations/clay2005-preview-v1/manifest.json', 'sha256': 'e5ceffc187f07fe63a2c4e07ad03bbf9940cef6a65c020b36d7178d998d8372c'}, 'receipt_key': 'models/modified-cam-clay.json', 'sha256': 'e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14'}]
EXPLICIT_INITIALS={'linear-elastic':[100000,100000,100000,0,0,0,.7],
                   'drucker-prager':[100000,100000,100000,0,0,0,.7,0]}
def legacy_paths():
 result=[]
 for item in LEGACY_INPUTS:
  p=(ROOT/item['path']).resolve()
  if not p.is_relative_to(ROOT) or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('historical recorded model pin mismatch')
  result.append(p)
 models=[json.loads(p.read_text())for p in result]
 if hashlib.sha256(json.dumps(models,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=LEGACY_HASH:raise ValueError('historical recorded catalogue mismatch')
 return result
def explicit_recorded_fixture(spec):
 result=copy.deepcopy(spec)
 if 'initial'not in result:
  result['initial']=copy.deepcopy(EXPLICIT_INITIALS[result['model']])
 return result
@contextmanager
def historical_recorded_context(test,namespace):
 # No skip, default current-runtime fallback or saved-response substitution.
 executable=os.environ.get('ATLAS_RECORDED_LEGACY_SOLVER');expected=os.environ.get('ATLAS_RECORDED_LEGACY_SHA256')
 if not executable or not expected or len(expected)!=64:raise RuntimeError('genuine legacy recorded solver and SHA256 required')
 binary=Path(executable).resolve()
 def verify():
  if not binary.is_file()or hashlib.sha256(binary.read_bytes()).hexdigest()!=expected:raise RuntimeError('legacy recorded executable pin mismatch')
 verify();models=[json.loads(p.read_text())for p in legacy_paths()]
 catalogue=json.loads(subprocess.check_output([str(binary),'--describe'],text=True));verify()
 if catalogue.get('sha256')!=LEGACY_HASH or catalogue.get('models')!=models:raise RuntimeError('legacy recorded executable catalogue mismatch')
 def run(spec):
  verify();result=execute_recorded(spec,str(binary));verify()
  test.records.append(dict(request=copy.deepcopy(spec),response=copy.deepcopy(result)))
  return result
 with patch.object(test,'run_spec',side_effect=run),patch.dict(namespace,all_models=lambda:copy.deepcopy(models)):
  yield
 verify()
