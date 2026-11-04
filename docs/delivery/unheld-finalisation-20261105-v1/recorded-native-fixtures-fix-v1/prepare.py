from pathlib import Path
import json,hashlib
R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ids=['drucker-prager','hypoplastic-sand-igs97','hypoplastic-sand-vw96','linear-elastic','modified-cam-clay'];ledger=json.loads((R/'tests/fixtures/historical-test-contexts.json').read_text());pins=[x for x in ledger['models']if json.loads((R/x['path']).read_text())['id']in ids]
assert len(pins)==5
(O/'legacy-model-inputs.json').write_text(json.dumps({'catalogue_hash':'1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c','models':pins},indent=2)+'\n')
helper='''"""Explicit current recorded fixtures and separately bound historical runtime."""
import copy,hashlib,json,os,subprocess
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from atlas.model import ROOT
from atlas.recorded import execute_recorded
LEGACY_HASH='1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c'
LEGACY_INPUTS=__PINS__
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
'''.replace('__PINS__',repr(pins))
(O/'proposed/tests/recorded_native_fixtures.py').write_text(helper)
a=(R/'tests/test_recorded_api.py').read_text();a=a.replace('from atlas.stress import stress_scope\n','from atlas.stress import stress_scope\nfrom tests.recorded_native_fixtures import explicit_recorded_fixture\n');a=a.replace("return dict(version='experimental-recorded-run-0.1', model='linear-elastic', path=path)","return explicit_recorded_fixture(dict(version='experimental-recorded-run-0.1', model='linear-elastic', path=path))");a=a.replace("'--model','linear-elastic','--initial-strain'","'--model','linear-elastic','--initial',','.join(map(str,specimen()['initial'])),'--initial-strain'");(O/'proposed/tests/test_recorded_api.py').write_text(a)
b=(R/'tests/test_recorded_restarts.py').read_text();b=b.replace('from tests.test_recorded_api import specimen\n','from tests.test_recorded_api import specimen\nfrom tests.recorded_native_fixtures import explicit_recorded_fixture,historical_recorded_context\n');b=b.replace("    def run_spec(self,s):\n        r=execute_recorded", "    def run_spec(self,s):\n        s=explicit_recorded_fixture(s)\n        r=execute_recorded")
start=b.index('        with gzip.open(',b.index('    def test_disabled_legacy_responses_exact(self):'));end=b.index('\n    def test_three_coarse_paths',start);body=b[start:end];b=b[:start]+"        with historical_recorded_context(self,globals()):\n"+''.join('    '+line if line.strip()else line for line in body.splitlines(True))+b[end:];b=b.replace("'--model','linear-elastic','--initial-strain'","'--model','linear-elastic','--initial',','.join(map(str,specimen()['initial'])),'--initial-strain'").replace("'--model','linear-elastic','--strain'","'--model','linear-elastic','--initial',','.join(map(str,specimen()['initial'])),'--strain'");(O/'proposed/tests/test_recorded_restarts.py').write_text(b)
(O/'source-delta.json').write_text(json.dumps({'files':[{'path':p,'preimage_sha256':sha(R/p),'sha256':sha(O/'proposed'/p)}for p in ['tests/test_recorded_api.py','tests/test_recorded_restarts.py']]},indent=2)+'\n')
print('prepared source only')
