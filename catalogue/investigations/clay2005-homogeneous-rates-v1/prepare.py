"""Assemble unchanged 120-call source/parity gates; never evaluate material rates."""
from pathlib import Path
import copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from atlas.evidence_sources import selected_files
OLD=ROOT/'catalogue/investigations/clay2005-determinant-rates-v1'
PACKET=ROOT/'docs/ingestion/hypoplastic-clay-2005/boundary-precision-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def candidate_contract():
 old=read(OLD/'model.json');new=read(HERE/'model.json');a=copy.deepcopy(old);b=copy.deepcopy(new)
 assert old['id']==new['id']and old['schema_version']==new['schema_version']=='0.3'
 assert new['description'].startswith(old['description']);a.pop('description');b.pop('description')
 od=next(x for x in a['derived']if x['name']=='detH');nd=next(x for x in b['derived']if x['name']=='detH')
 assert od['expr']=='determinant(H)'and nd['expr']=='normalized_determinant(sigma)'
 nd['expr']=od['expr'];assert a==b,'only detH and descriptive provenance may change'
 return new

def prepare():
 model=candidate_contract();old=read(OLD/'protocol.json')
 suffixes={'.py','.hpp','.cpp','.md','.json','.txt','.mjs'}
 sources=set()
 for packet in ('boundary-precision-v1','compiled-plan-v3','determinant-input-rounding-v1'):
  sources.update(selected_files(ROOT/'docs/ingestion/hypoplastic-clay-2005'/packet,suffixes))
 sources.update(selected_files(ROOT/'atlas',{'.py'}));sources.update(selected_files(ROOT/'schemas',{'.json'}));sources.update(selected_files(ROOT/'cpp/include/atlas',{'.hpp'}))
 sources.update(HERE/p for p in ('model.json','README.md','prepare.py','freeze.py','run_build.py','verify_study.py','test_study.py','reference-replay.json'))
 sources.update(HERE/'expected-generated'/p for p in ('models.hpp','models.json'))
 sources.update(OLD/p for p in ('protocol.json','model.json'))
 sources.update(ROOT/p for p in ('cmake/research-v3/CMakeLists.txt','tests/research_rate_driver_v3.cpp','tools/research_rate_observations_v3.py','tools/collect_research_rates_wasm_v3.mjs','tools/research_rate_parity_v3.py','docs/reviews/generic-rate-collection-v3/CONTRACT.md','docs/reviews/generic-rate-collection-v3/source-pins.json','docs/reviews/tagged-rate-transport-review-v3/manifest.json','docs/reviews/tagged-rate-transport-review-v3/observations-final.json','docs/NORMALIZED_DETERMINANT.md','docs/EVIDENCE_FREEZES.md'))
 assert not any('__pycache__'in p.parts or p.suffix in ('.pyc','.pyo')for p in sources)
 return {'version':'research-instantaneous-rate-protocol-0.3','study':'clay2005-homogeneous-rates-v1','model_file':str((HERE/'model.json').relative_to(ROOT)),'model_definition':model,'files':{str(p.relative_to(ROOT)):sha(p)for p in sorted(sources)},'cases':copy.deepcopy(old['cases']),'finite_only_parity':copy.deepcopy(old['finite_only_parity']),'policy':copy.deepcopy(old['policy'])}
if __name__=='__main__':
 path=HERE/'protocol.json';text=json.dumps(prepare(),indent=2,allow_nan=False)+'\n'
 if '--check'in sys.argv:assert path.read_text()==text,'frozen assembly changed'
 else:assert not path.exists(),'fresh protocol required';path.write_text(text)
