from pathlib import Path
import hashlib,json,subprocess,difflib
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/reviews/ordinary-model-deeplinks-v1';O=P/'independent-review';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (O/'inputs.json').exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
f=read(P/'candidate-freeze-v1.json')
for p,h in f['files'].items():assert sha(R/p)==h,p
before=(P/'prior-app.js').read_text();after=(P/'candidate-app.js').read_text()
def fn(source,name):
 start=source.index('function '+name+'(');end=source.index('\n',start)
 return source[start:end]if source[start:end].endswith('}')else source[start:source.index('\n}',start)+2]
for name in ['selectLaboratory','selectJ2','specialLaboratoryActive','cancel','invalidate','simulate','startRun','importRun','loadExperiments','applyRunSpecification','populate','scheduleUpdate']:
 assert fn(before,name)==fn(after,name),name
assert "route({initial:true});simulate();"in after
assert "if(query.getAll('model').length!==1)toast"in after
assert "id!==$('model').value"in after
checks=[]
for saved in read(P/'candidate-checks-v1.json'):
 z=subprocess.run(saved['command'],cwd=R,capture_output=True,text=True);assert z.returncode==saved['exit_code']==0 and z.stdout==saved['stdout'] and z.stderr==saved['stderr'];checks.append(json.loads(z.stdout))
# Verify existing test delta is solely one marker-array line, all actual delayed import assertions retained.
a=(P/'prior-j2-routing-test.mjs').read_text().splitlines();b=(P/'candidate-j2-routing-test.mjs').read_text().splitlines();diff=[x for x in difflib.ndiff(a,b)if x.startswith(('- ','+ '))];assert len(diff)==2 and all('for(const marker of ['in x for x in diff)
assert read(P/'baseline-j2-routing-v1.json')['exit_code']!=0
print(json.dumps({'passed':True,'freeze_pins':len(f['files']),'pure_test_reports':checks,'unchanged_cancellation_async_and_material_functions':12,'existing_j2_test_changed_lines':1,'reviewer_compiled_calls':0,'reviewer_builds':0,'prospective_only':True,'limits':['Inert DOM/controller source tests; real history event order, actual controller workers and browser behavior require separate actual evidence.','Navigation resets selected ordinary model defaults through existing populate path; no numerical/model/reference/solver change.','Root installation/preservation and matching package remain separate.']},indent=2))
