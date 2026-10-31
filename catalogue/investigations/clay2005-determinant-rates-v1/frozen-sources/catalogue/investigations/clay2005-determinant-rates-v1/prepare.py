"""Assemble literal requests and prospective gates; no material evaluation."""
from pathlib import Path
import copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OLD=ROOT/'catalogue/investigations/clay2005-rates-v3'
PACKET=ROOT/'docs/ingestion/hypoplastic-clay-2005/boundary-precision-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def candidate_contract():
 old=read(OLD/'model.json');new=read(HERE/'model.json');a=copy.deepcopy(old);b=copy.deepcopy(new)
 assert old['id']==new['id'] and old['schema_version']==new['schema_version']=='0.3'
 assert old['description'] in new['description'];a.pop('description');b.pop('description')
 od=next(x for x in a['derived']if x['name']=='detH');nd=next(x for x in b['derived']if x['name']=='detH')
 assert od['expr']=='1/27-j2/6+j3/3' and nd['expr']=='determinant(H)'
 nd['expr']=od['expr'];assert a==b,'only detH and descriptive provenance may change'
 return new

def prepare():
 model=candidate_contract();old=read(OLD/'protocol.json');freeze=read(PACKET/'prospective-freeze.json');results=read(PACKET/'results.json')
 assert results['all_cases_converged'] and results['freeze_sha256']==sha(PACKET/'prospective-freeze.json')
 references={c['id']:c for c in results['cases']};oldcases={c['id']:c for c in old['cases']}
 cases=copy.deepcopy(old['cases'])
 for c in freeze['cases']:
  ref=references[c['id']];assert ref['converged'] and c['args']==oldcases[c['id']]['args']
  values=list(map(float,ref['precision_results']['240']['values']))
  budgets=[1e-10*max(1.,abs(v))for v in values[:6]]+[1e-15+2e-13*abs(values[6])]
  cases.append({'id':'boundary-accuracy/'+c['id'],'origin':{'file':str((PACKET/'results.json').relative_to(ROOT)),'sha256':sha(PACKET/'results.json'),'case_id':c['id'],'precision_digits':240},'args':copy.deepcopy(c['args']),'expectation':{'kind':'accuracy','ok':True,'values':values,'absolute_budgets':budgets,'parity_budgets':budgets.copy()}})
 sources=set(p for p in PACKET.rglob('*')if p.is_file())
 for packet in ('compiled-plan-v3','determinant-input-rounding-v1'):
  sources.update(p for p in (ROOT/'docs/ingestion/hypoplastic-clay-2005'/packet).rglob('*')if p.is_file())
 for pattern in ('atlas/*.py','atlas/numerics/*.py','schemas/*.json','cpp/include/atlas/**/*.hpp'):
  sources.update(ROOT.glob(pattern))
 sources.update(HERE/p for p in ('model.json','README.md','prepare.py','freeze.py','run_build.py','verify_study.py','test_study.py','reference-replay.json'))
 sources.update((HERE/'expected-generated'/p)for p in ('models.hpp','models.json'))
 sources.update(OLD/p for p in ('protocol.json','model.json'))
 sources.update(ROOT/p for p in ('cmake/research-v3/CMakeLists.txt','tests/research_rate_driver_v3.cpp','tools/research_rate_observations_v3.py','tools/collect_research_rates_wasm_v3.mjs','tools/research_rate_parity_v3.py','docs/reviews/generic-rate-collection-v3/CONTRACT.md','docs/reviews/generic-rate-collection-v3/source-pins.json','docs/reviews/tagged-rate-transport-review-v3/manifest.json','docs/reviews/tagged-rate-transport-review-v3/observations-final.json'))
 policy=copy.deepcopy(old['policy']);policy['additional_boundary']={'calls':11,'stress_absolute_budget':'1e-10*max(1,abs(reference_component))','void_absolute_budget':'1e-15+2e-13*abs(reference_void)','parity':'same additional source budgets','actual_binary64_inputs':True,'historical_labels_unchanged':True}
 return {'version':'research-instantaneous-rate-protocol-0.3','study':'clay2005-determinant-rates-v1','model_file':str((HERE/'model.json').relative_to(ROOT)),'model_definition':model,'files':{str(p.relative_to(ROOT)):sha(p)for p in sorted(sources)},'cases':cases,'finite_only_parity':copy.deepcopy(old['finite_only_parity']),'policy':policy}
if __name__=='__main__':
 path=HERE/'protocol.json';text=json.dumps(prepare(),indent=2,allow_nan=False)+'\n'
 if '--check'in sys.argv:assert path.read_text()==text,'frozen assembly changed'
 else:assert not path.exists(),'fresh protocol required';path.write_text(text)
