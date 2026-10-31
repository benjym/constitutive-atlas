"""Source-only validation and fixture generation; never invokes a compiler."""
import hashlib,json,pathlib,sys,tempfile
ROOT=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(ROOT))
from atlas.model import load
from atlas.compiler import generate
P=pathlib.Path(__file__).resolve().parent
models=[load(p) for p in sorted((P/'models').glob('*.json'))]
with tempfile.TemporaryDirectory(prefix='atlas-rollback-source-') as dest:
 generate(dest,list((P/'models').glob('*.json')))
 generated=pathlib.Path(dest,'models.hpp').read_bytes()
expected=json.loads((P/'expected.json').read_text());assert len(expected['rows'])==11
assert len(set(x['id'] for x in expected['rows']))==11
# Exact parent-read algebra is independent of interpreter/compiler implementations.
parent={'x':2,'y':5};assert {k:parent[v] for k,v in [('x','y'),('y','x')]}=={'x':5,'y':2}
# Constant d(sigma)/dt=I over duration1 gives +1 diagonal. Dyadic .25 subdivision is exact.
assert [2+1,3+1,4+1,0,0,0,2,5]==expected['rows'][6]['state']
assert 2*(1/.25)==expected['rows'][6]['substeps']
assert 2*(.5/.25)==expected['rows'][5]['substeps']
# Exercise the frozen assessor on synthetic data only, clearly distinct from backend observations.
import runpy
assessor=runpy.run_path(str(P/'assess.py'));raw={'version':'solver-rollback-observations-v1','rows':[],'preparation':[]}
for target in expected['rows']:
 row={k:v for k,v in target.items() if k not in ('state','time')};row['state_bits']=None if target['state'] is None else list(map(assessor['bits'],target['state']));row['time_bits']=None if target['time'] is None else assessor['bits'](target['time']);row.update(expected['all_rows']);raw['rows'].append(row)
for target in expected['preparation']:
 scratch=list(map(assessor['bits'],target['scratch']));scratch+=['unspecified']*(8-len(scratch));raw['preparation'].append(dict(id=target['id'],ok=target['ok'],scratch_bits=scratch,inputs_bitwise_unchanged=True))
with tempfile.TemporaryDirectory(prefix='atlas-rollback-assessor-') as dest:
 file=pathlib.Path(dest,'synthetic-only.json');file.write_text(json.dumps(raw));assert assessor['assess'](file)['passed']
 raw['rows'][5]['time_bits']=assessor['bits'](3);file.write_text(json.dumps(raw));assert not assessor['assess'](file)['passed']
 raw['rows']=raw['rows'][1:];file.write_text(json.dumps(raw));assert not assessor['assess'](file)['passed']
print(json.dumps(dict(models_validated=len(models),assessor_synthetic_selfchecks=3,ordered_expected_rows=11,generated_header_bytes=len(generated),generated_header_sha256=hashlib.sha256(generated).hexdigest(),compiled=False,executed_cpp=False,source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['atlas/compiler.py','atlas/dsl.py','atlas/model.py','cpp/include/atlas/solver.hpp','cpp/include/atlas/time.hpp','cpp/include/atlas/schedule.hpp','cpp/include/atlas/settings.hpp']}),indent=2))
