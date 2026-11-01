"""Additive SLS saved-only review; prior Power/Burgers packet stays exact."""
import sys
sys.dont_write_bytecode=True
import ast,contextlib,io,json,os,runpy
import review as r
from pathlib import Path
def main():
 plan,f,tools=r.common()
 # Reuse our frozen evidence checks with only this profile's pinned Debug/model
 # identity substitutions. No author implementation or evidence is changed.
 tree=ast.parse((r.D/'review.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='packet')
 class Adapt(ast.NodeTransformer):
  changes=0
  def visit_Constant(self,node):
   values={'CMAKE_BUILD_TYPE:STRING=Release':'CMAKE_BUILD_TYPE:STRING=Debug','models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json':'models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json'}
   if isinstance(node.value,str)and node.value in values:self.changes+=1;return ast.copy_location(ast.Constant(values[node.value]),node)
   return node
 adapt=Adapt();fn=adapt.visit(fn);r.check('Exactly two SLS reviewer identity substitutions',adapt.changes==2)
 scope=dict(r.__dict__);exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'saved-sls-evidence-binding','exec'),scope)
 expected='ae7e31a7aeaecbade380a8ff18fb27454c02e49807b21c565f6ef951f2e616b1'
 spec,work=scope['packet']('sls',expected,plan,f,tools)
 study=r.load('independent_sls_saved',r.S/'docs/ingestion/sls-comsol63/execution-v1/study.py')
 cases=r.read(study.BASE/'cases.json')['cases'];r.check('SLS34 frozen cases',len(cases)==34)
 r.check('SLS source-generated cases exact',study.make_cases()==cases)
 envelope=r.read(work/'evidence/native-envelope.json');native=r.read(work/'evidence/native-observe-v2-raw.json');wasm=r.read(work/'evidence/wasm-raw.json')
 r.check('SLS native compatibility copy exact',envelope['capture']==native)
 observations={}
 for name,rows in [('native',native),('wasm',wasm)]:
  report=study.assess(cases,rows)
  if name=='native':r.check('SLS native envelope original assessment',report==envelope['report']);report['original_material_calls_preserved']=True
  r.check('SLS '+name+' full report exact',report==r.read(work/'evidence'/f'{name}-report.json'));r.save('sls-'+name+'-recomputed.json',report)
  observations[name]=sum('observation'in row for row in rows)
  for case,row in zip(cases,rows):
   for call in row['calls']:r.check('SLS expected response/status '+name+case['id'],type(call['returncode'])is int and call['returncode']==(0 if case['ok']else 1)and call['stderr']=='')
   if case.get('restart_from'):
    parent=next(x for x in rows if x['id']==case['restart_from']);initial=json.loads(parent['calls'][0]['stdout'])['state']
    r.check('SLS own-backend actual restart '+name+case['id'],json.loads(row['calls'][0]['stdout'])['initial']==initial)
 os.environ['ATLAS_QUALIFICATION_SOURCE']=str(r.S);os.environ['ATLAS_QUALIFICATION_OUTPUT']=str(work/'evidence')
 output=io.StringIO()
 with contextlib.redirect_stdout(output):runpy.run_path(str(r.P/'adapters/check_sls_saved.py'),run_name='independent_sls_pair')
 paired=json.loads(output.getvalue());r.check('SLS exact original paired report',paired==json.loads((r.R/'current-profile-actual-sls-v3/paired-assess.stdout').read_text()));r.save('sls-paired-recomputed.json',paired)
 artifacts={str(p.relative_to(work)):r.sha(p)for p in [work/'native-build/atlas_sls_solver',work/'wasm-build/sls.js',work/'wasm-build/sls.wasm']}
 r.save('sls-decision.json',{'identity':'independent-current-profile-actual-review-v1','profile':'sls','author_manifest_sha256':expected,'decision':'ACCEPT_BOUNDED_SAVED_NATIVE_WASM_STUDY','blocking_findings':[],'facts':{'build_type':'Debug, exactly as prospectively frozen','cases_per_backend':34,'repeated_material_calls_per_backend':68,'observations_per_backend':observations,'paired':paired,'artifacts':artifacts,'transport_scope':'retained response strings in call records; native process exits vs Wasm response-derived statuses distinct; outer process raw/exit retained'},'excluded':['full MD scientific/admission','all seven profiles','package approval','app/browser/live','general parameter or loading qualification'],'reviewer_compiled_calls':0})
 r.save('sls-checks.json',{'passed':True,'checks':len(r.checks),'results':r.checks,'process_execution_disabled':True});print(json.dumps({'sls_checks':len(r.checks),'compiled_calls':0}))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  r.save('sls-retained-failure-'+str(len(list(r.D.glob('sls-retained-failure-*.json'))))+'.json',{'type':type(exc).__name__,'error':str(exc),'checks':r.checks});raise
