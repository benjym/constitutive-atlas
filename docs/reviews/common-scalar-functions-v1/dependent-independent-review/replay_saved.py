"""Reassess saved dependent data only, without solver calls or shared writes."""
from pathlib import Path
import json,sys,subprocess
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent;S=B/'dependent-results-v1'
src=Path(json.loads((B/'dependent-source-freeze-v1.json').read_text())['source']);base=src/'docs/ingestion/maxwell-itasca900/integration-v1';obs=S/'maxwell-observations'
def module(p,name):
    ns={'__name__':name,'__file__':str(p)};exec(compile(p.read_text(),str(p),'exec'),ns);return ns
m=module(src/'tests/test_maxwell.py','maxwell_saved_only')
t=module(base/'check_transactions.py','maxwell_transactions_saved_only')
cases=json.loads((base/'reference-cases.json').read_text())['cases'];summary={}
for backend in ['native','wasm']:
    rows=json.loads((obs/f'{backend}-raw.json').read_text());errors=m['assess_rows'](cases,rows)
    transaction_cases=t['cases_for'](obs/f'{backend}-raw.json')
    recorded=json.loads((obs/f'{backend}-transaction-cases.json').read_text())['cases'];assert transaction_cases==recorded
    trans=json.loads((obs/f'{backend}-transactions-raw.json').read_text());terr=t['assess'](transaction_cases,trans)
    assert len(rows)==24 and len(trans)==14
    summary[backend]=dict(main_calls=sum(len(r['calls']) for r in rows),supplement_calls=sum(len(r['calls']) for r in trans),max_main_error_Pa=max(errors.values()),max_supplement_error_Pa=max(terr.values()))
# Preserve exact original comparison function; redirect only its saved-data loop.
path=base/'compare_backends_v2.py';prefix=path.read_text().split("for suffix in ('raw','transactions-raw'):")[0]
p={'__file__':str(path),'__name__':'maxwell_parity_saved_only'};exec(compile(prefix,str(path),'exec'),p)
for suffix in ['raw','transactions-raw']:
    native=json.loads((obs/f'native-{suffix}.json').read_text());wasm=json.loads((obs/f'wasm-{suffix}.json').read_text())
    assert [x['id'] for x in native]==[x['id'] for x in wasm]
    for n,w in zip(native,wasm):
        assert len(n['calls'])==len(w['calls'])==2
        for nc,wc in zip(n['calls'],w['calls']):
            assert nc['returncode']==wc['returncode'];p['compare'](json.loads(nc['stdout']),json.loads(wc['stdout']))
parity=dict(passed=True,numeric_comparisons=p['COUNT'],maximum_stress_difference_Pa=p['MAX_STRESS'],maximum_strain_or_rate_difference=p['MAX_STRAIN'])
assert parity==json.loads((obs/'parity-results-v2.json').read_text()) and parity['numeric_comparisons']==5962
summary['Maxwell_parity']=parity
for label,command in [
 ('Maxwell_presets',[sys.executable,'-B',str(src/'docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py'),str(src),str(S/'maxwell-presets')]),
 ('NorSand',[sys.executable,'-B',str(src/'docs/ingestion/norsand-1993/e2-v3/check_backend_results_v3.py'),str(src/'docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json'),str(S/'norsand-native-results.json'),str(S/'norsand-wasm-results.json')])]:
    process=subprocess.run(command,capture_output=True,text=True);(O/(label+'-replay.log')).write_text(process.stdout+process.stderr);assert process.returncode==0
    summary[label]=json.loads(process.stdout)
summary['compiled_execution']=False;summary['pass_']=True
(O/'saved-replay-results.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
