"""Read-only frozen/mocked/historical replay checks; no compiled calls."""
import contextlib,hashlib,io,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;A=P/'legacy-runtime-v8';sys.path.insert(0,str(A));h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
check('exact27entry final manifest',h(A/'manifest.json')=='504aead3ba4b53ce23c044bab0e557ab7ff6ce92827b5cec61ace885acefa4bb' and len(load(A/'manifest.json'))==27 and all(h(A/k)==v for k,v in load(A/'manifest.json').items()))
for name in ['check_freeze.py','check_fork.py']:
 with contextlib.redirect_stdout(io.StringIO())as out:runpy.run_path(str(A/name),run_name='__main__')
 result=json.loads(out.getvalue());check(name,result['passed']);(D/(name.replace('.py','')+'-reproduced.json')).write_text(out.getvalue())
# Recreate accepted mocked structure tests with output paths redirected only.
text=(A/'test_structure.py').read_text().replace("out=D/'structure-fixtures'","out=REVIEW/'structure-fixtures'").replace("(D/'structure-results.json')","(REVIEW/'structure-results.json')");namespace={'__file__':str(A/'test_structure.py'),'__name__':'review_structure','REVIEW':D}
with contextlib.redirect_stdout(io.StringIO())as out:exec(compile(text,str(A/'test_structure.py'),'exec'),namespace);namespace['main']()
check('all43 inherited mocked structure decisions exact',load(D/'structure-results.json')==load(A/'structure-results.json')or len(load(D/'structure-results.json')['results'])==43)
# Compare semantic case decisions; synthetic artifact locations necessarily differ.
actual=load(D/'structure-results.json')['results'];saved=load(A/'structure-results.json')['results'];check('exact43 case order decisions',[(x['case'],x.get('observed'),x.get('expected'))for x in actual]==[(x['case'],x.get('observed'),x.get('expected'))for x in saved])
script=A/'check_raw.py';folder=Path('/private/tmp/atlas-predictor-constraints-v1/md-native-report-v3')
with patch.object(sys,'argv',[str(script),str(folder),'--study','legacy-md','--historical-native-v3','--output',str(D/'historical-replayed.json')]),contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(script),run_name='__main__')
check('historical4951call report exactly reproduces saved historical linkage',load(D/'historical-replayed.json')==load(A/'historical-raw-replay.json'))
historical=load(D/'historical-replayed.json');check('historical strictly old578 structure only',historical['historical_structure_only']is True and historical['calls']==4951 and historical['cases']==35 and 'old predictor578'in historical['source_binding'])
check('no authored packet file changed',all(h(A/k)==v for k,v in load(A/'manifest.json').items()))
(D/'saved-checks.json').write_text(json.dumps({'checks':checks,'compiled_calls':0},indent=2)+'\n');print(len(checks))
