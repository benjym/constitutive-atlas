from pathlib import Path
import ast,json,hashlib
P=Path(__file__).parent;S=Path('/private/tmp/atlas-laboratory-q-cancellation-v1');R=Path('/Users/bmar5496/code/constitutive-atlas');checks=[]
def check(name,b):
 checks.append({'name':name,'passed':b})
 if not b:raise AssertionError(name)
a=(R/'cpp/main.cpp').read_text();expected=a.replace('#include "atlas/recorded.hpp"','#include "atlas/recorded.hpp"\n#include "atlas/stress_observables.hpp"').replace('std::sqrt(1.5*atlas::dot(atlas::dev(sigma),atlas::dev(sigma)))','atlas::deviatoric_stress_magnitude(sigma)')
check('main exact include + one q call',expected==(S/'frozen/cpp/main.cpp').read_text())
rootfiles={str(p.relative_to(R/'cpp'))for p in(R/'cpp').rglob('*')if p.is_file()};newfiles={str(p.relative_to(S/'frozen/cpp'))for p in(S/'frozen/cpp').rglob('*')if p.is_file()}
check('only extra cpp is observable header',newfiles-rootfiles=={'include/atlas/stress_observables.hpp'}and not rootfiles-newfiles)
check('all other cpp exact',all((R/'cpp'/n).read_bytes()==(S/'frozen/cpp'/n).read_bytes()for n in rootfiles if n!='main.cpp'))
for folder in ['atlas','schemas','models']:
 check(folder+' unchanged',all(p.read_bytes()==(R/p.relative_to(S/'frozen')).read_bytes()for p in(S/'frozen'/folder).rglob('*')if p.is_file()))
B=Path('/private/tmp/atlas-browser-loading-provenance-v1')
for name in ['check_backends.mjs','generated/models.hpp','generated/models.json','web/loading.mjs','web/numerics.mjs']:
 check(name+' original browser bytes',(S/name).read_bytes()==(B/name).read_bytes())
Q=Path('/private/tmp/atlas-laboratory-q-reference-v1')
for name in ['inputs.json','policy.json','reference.py','references.json','prospective-freeze.json']:
 check('independent reference unchanged '+name,(S/'reference'/name).read_bytes()==(Q/name).read_bytes())
for name in ['freeze.py','execute.py','assess_probe.py','assess_invariance.py']:
 node=ast.parse((P/'final'/name).read_text()).body[0]
 # assessors have imports before guard; locate actual guard rather than running imports/main.
 nodes=ast.parse((P/'final'/name).read_text()).body;guard=next(n for n in nodes if isinstance(n,ast.If)and ast.unparse(n.test)=='not __debug__')
 try:exec(compile(ast.Module(body=[guard],type_ignores=[]),name,'exec',optimize=2),{})
 except RuntimeError:check(name+' rejects optimized',True)
 else:check(name+' rejects optimized',False)
s=(P/'final/assess_invariance.py').read_text();prefix=s[:s.index('newpath=')];namespace={'__name__':'__main__','__file__':str(P/'final/assess_invariance.py')};exec(prefix,namespace)
x=namespace['loads']('{"negative":-0,"positive":0,"real":0.0,"boolean":false}')
check('raw signedzero preserved',x['negative'].bits=='8000000000000000'and x['positive'].bits=='0000000000000000')
check('integer real boolean remain distinct',x['positive']!=x['real']and x['positive']!=x['boolean'])
check('exclusions scoped',"value.pop('elapsed_ms',None)"in s and "point.items()if k!='q'"in s and 'unchanged(v)'not in s)
e=(P/'final/execute.py').read_text();check('freeze hash and priorzero calls',"freeze['compiled_calls_at_freeze']==0"in e and "freeze['manifest_sha256']"in e)
check('native2 wasm4 artifact sets',"{'atlas_q_probe','atlas_solver'}"in e and "{'q-probe.js','q-probe.wasm','atlas.js','atlas.wasm'}"in e)
check('serial targets and worker',"for target in ['atlas_q_probe','atlas_solver']"in e and "'--parallel','1'"in e and "EMCC_CORES='1'"in e)
check('failed subprocess hard rejection','if p.returncode:raise RuntimeError'in e)
check('specified not verified domain','independently specified reference-study domain'in(P/'final/stress_observables.hpp').read_text())
(P/'source-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'candidate_calls':0,'compiled_calls':0},indent=2)+'\n');print(len(checks),'bounded source checks passed')
