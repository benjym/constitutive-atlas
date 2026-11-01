"""Additive saved J2 study review. Every process execution path is disabled."""
import sys
sys.dont_write_bytecode=True
import ast,contextlib,io,json,os,runpy
import review as r
def main():
 plan,f,tools=r.common()
 tree=ast.parse((r.D/'review.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='packet')
 class Adapt(ast.NodeTransformer):
  changes=0
  def visit_Constant(self,node):
   if node.value=='models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json':self.changes+=1;return ast.copy_location(ast.Constant('models/research/j2/j2-linear-isotropic-hardening-be.json'),node)
   return node
 adapt=Adapt();fn=adapt.visit(fn);r.check('Exactly one J2 reviewer model substitution',adapt.changes==1)
 scope=dict(r.__dict__);exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'saved-j2-evidence-binding','exec'),scope)
 expected='a2f4337620e0844cadbfa7482ba55d800bc344d29cce30e78e1baaf9e09b8f45';spec,work=scope['packet']('j2',expected,plan,f,tools)
 sys.path.insert(0,str(r.S));study=r.load('independent_saved_j2',r.S/'tools/study_j2.py');base=r.S/'docs/ingestion/j2-linear-hardening/execution-v2'
 history=r.load('independent_saved_j2_history',base/'check_paths.py')
 paths=r.read(base/'paths.json')+[r.read(r.S/'docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json')]
 combined=r.read(r.R/'qualification-support-v2/j2-paths-with-public-preset.json');r.check('J2 combined path/preset source exact',combined==paths)
 for path in paths:
  z=path['initial'];values=[]
  for de in path['increments']:z=study.oracle(z,de,path['parameters']);values.append(z)
  r.check('J2 independent analytical path expectations '+path['id'],values==path['expected'])
 results={}
 for name in ['native','wasm']:
  report={}
  for label,ref in [('main','references.json'),('defaults','default-references.json')]:
   cases=r.read(base/ref)['cases'];raw=r.read(work/'evidence'/('native/'+label+'-raw.json'if name=='native'else'wasm-'+label+'-raw.json'))
   if label=='main':r.check('J2115 main source cases exact',len(cases)==115 and study.cases()==cases)
   else:r.check('J216 defaults cases',len(cases)==16)
   for c in cases:
    if c['ok']:
     p,z,de=[list(map(float,c['args'][i].split(',')))for i in [1,2,3]]
     r.check('J2 source radial reference '+name+c['id'],study.oracle(z,de,p)==c['expected'])
     if 'tangent'in c:r.check('J2 source tangent reference '+name+c['id'],study.tangent(z,de,p)==c['tangent'])
   report[label]=study.assess_rows(cases,raw)
  raw=r.read(work/'evidence'/('native/paths-raw.json'if name=='native'else'wasm-paths-raw.json'));report['paths_and_public_preset']=history.assess(paths,raw)
  r.check('J2 exact full '+name+' assessment',report==r.read(work/'evidence'/('native/assessment.json'if name=='native'else'wasm-assessment.json')));r.save('j2-'+name+'-recomputed.json',report);results[name]=report
 os.environ['ATLAS_QUALIFICATION_SOURCE']=str(r.S)
 for label,ref in [('main','references.json'),('defaults','default-references.json')]:
  os.environ['ATLAS_J2_REFERENCE']=str(base/ref);old=sys.argv
  sys.argv=[str(r.P/'adapters/study_j2.py'),'parity',str(work/'evidence/native'/f'{label}-raw.json'),str(work/'evidence'/f'wasm-{label}-raw.json')]
  text=io.StringIO()
  try:
   with contextlib.redirect_stdout(text):runpy.run_path(str(r.P/'adapters/study_j2.py'),run_name='__main__')
  finally:sys.argv=old
  parity=json.loads(text.getvalue());r.check('J2 original paired '+label+' exact',parity==json.loads((r.R/'current-profile-actual-j2-v3'/f'paired-{label}.stdout').read_text()));r.save('j2-'+label+'-paired-recomputed.json',parity)
 artifacts={str(p.relative_to(work)):r.sha(p)for p in [work/'native-build/atlas_j2_solver',work/'wasm-build/j2.js',work/'wasm-build/j2.wasm']}
 r.save('j2-decision.json',{'identity':'independent-current-profile-actual-review-v1','profile':'j2','author_manifest_sha256':expected,'decision':'ACCEPT_BOUNDED_SAVED_NATIVE_WASM_STUDY','blocking_findings':[],'facts':{'stages':11,'strict_pre_post_receipts':22,'reports':results,'paired_scope':'unchanged main/default physical states and tangents; histories/public preset independently source-assessed on both backends','artifacts':artifacts,'transport_scope':'main/default retained stdout strings/status records; history paths parsed responses, not individual process raw/status; outer stage raw/process receipts retained'},'excluded':['full MD scientific/admission','all seven profiles','package/catalogue approval','app/browser/live','general parameter/loading qualification'],'reviewer_compiled_calls':0})
 r.save('j2-checks.json',{'passed':True,'checks':len(r.checks),'results':r.checks,'process_execution_disabled':True});print(json.dumps({'j2_checks':len(r.checks),'compiled_calls':0}))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  r.save('j2-retained-failure-'+str(len(list(r.D.glob('j2-retained-failure-*.json'))))+'.json',{'type':type(exc).__name__,'error':str(exc),'checks':r.checks});raise
