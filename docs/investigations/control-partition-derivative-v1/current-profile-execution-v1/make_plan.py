"""Materialize exact prospective argv/cwd/env; never executes commands."""
from pathlib import Path
import json,hashlib,ast
D=Path(__file__).resolve().parent;C=D.parent;S=Path('/private/tmp/atlas-control-partition-support-v3/source');BASE=Path('/private/tmp/atlas-control-partition-profile-execution-v1');A=D/'adapters';old=json.loads((C/'qualification-support-v1/profile-targets.json').read_text());profiles=[]
for row in old['profiles'][:7]:
 name=row['profile'];N=BASE/name/'native-build';W=BASE/name/'wasm-build';O=BASE/name/'evidence';env={'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(S),'ATLAS_QUALIFICATION_SOURCE':str(S),'ATLAS_QUALIFICATION_OUTPUT':str(O)};steps=[]
 def add(stage,args,extra=None):steps.append(dict(stage=stage,cwd=str(S),env={**env,**(extra or{})},argv=[str(x)for x in args],retain_process=True))
 extra=[]
 if name=='norsand':extra=['-DATLAS_PATH_MODELS='+';'.join(str(S/p)for p in ['models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'])]
 for backend,B in [('native',N),('wasm',W)]:
  add(backend+'-configure',(['emcmake']if backend=='wasm'else[])+['cmake','-S',str(S/row['cmake_directory']),'-B',str(B),'-DCMAKE_BUILD_TYPE='+row['build_type'],*extra]);add(backend+'-build',['cmake','--build',B,'--target',row['target'],'--parallel','1'])
  if name=='power-creep':
   if backend=='native':add('native-collect',['python3','-B',S/'tools/power_creep_refined_study.py','native','--solver',N/'atlas_power_creep_solver','--output',O/'native'])
   else:add('wasm-collect',['node',S/'tools/collect_power_creep_wasm.mjs',S/(row['policy_root']+'/study.json'),W/'power-creep.js',O/'wasm'])
   add(backend+'-assess',['python3','-B',S/'tools/power_creep_refined_study.py','assess','--output',O/backend]+(['--native',str(O/'native')]if backend=='wasm'else[]))
  elif name=='burgers':add(backend+'-collect-assess',['python3','-B',A/'test_burgers_native.py',N/'atlas_burgers_solver'if backend=='native'else W/'burgers.mjs',O/backend]+(['--wasm']if backend=='wasm'else[]))
  elif name=='sls':
   if backend=='native':add('native-collect-assess',['python3','-B',S/'tools/test_sls_native.py','--solver',N/'atlas_sls_solver','--output',O/'native-envelope.json'])
   else:add('wasm-collect',['node',S/'docs/ingestion/sls-comsol63/execution-v1/collect_wasm.mjs',W/'sls.js',S/'docs/ingestion/sls-comsol63/execution-v1/cases.json',O/'wasm-raw.json'])
  elif name=='j2':
   if backend=='native':add('native-collect-assess',['python3','-B',S/'tools/test_j2_native.py','--solver',N/'atlas_j2_solver','--output',O/'native'])
   else:
    for label,ref in [('main','references.json'),('defaults','default-references.json')]:add('wasm-'+label,['node',S/'tools/collect_j2_wasm.mjs',W/'j2.js',S/'docs/ingestion/j2-linear-hardening/execution-v2'/ref,O/('wasm-'+label+'-raw.json')])
    add('wasm-paths-preset',['node',S/'tools/collect_j2_paths.mjs',W/'j2.js',C/'qualification-support-v2/j2-paths-with-public-preset.json',O/'wasm-paths-raw.json']);add('wasm-assess',['python3','-B',A/'assess_fresh.py','j2','--main',O/'wasm-main-raw.json','--defaults',O/'wasm-defaults-raw.json','--paths',O/'wasm-paths-raw.json','--report-name','wasm-assessment.json'])
  elif name=='orthotropic':
   if backend=='native':add('native-collect-assess',['python3','-B',S/'tools/test_orthotropic_native.py','--solver',N/'atlas_orthotropic_solver','--output',O/'native'])
   else:add('wasm-collect',['node',S/'tools/test_orthotropic_wasm.mjs',W,S/'docs/ingestion/orthotropic-ogs/execution-v1/references.json',O/'wasm-raw.json']);add('wasm-assess',['python3','-B',A/'assess_fresh.py','orthotropic','--raw',O/'wasm-raw.json','--report-name','wasm-assessment.json'])
  elif name=='maxwell':
   if backend=='native':add('native-collect-assess',['python3','-B',S/'tests/test_maxwell.py','--solver',N/'atlas_maxwell_solver','--output',O/'native-raw.json'])
   else:add('wasm-collect',['node',S/'tools/test_maxwell_wasm.mjs',W/'maxwell.js',S/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json',O/'wasm-raw.json']);add('wasm-assess',['python3','-B',S/'tests/test_maxwell.py','--assess',O/'wasm-raw.json'])
   add(backend+'-transactions',['python3','-B',A/'check_maxwell_transactions.py','--backend',backend]+(['--solver',str(N/'atlas_maxwell_solver')]if backend=='native'else['--module',str(W/'maxwell.js')]))
  elif name=='norsand':
   Q=S/'docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json'
   if backend=='native':add('native-collect',['python3','-B',S/'docs/ingestion/norsand-1993/e2-v3/run_native_requests_v2.py',N/'libatlas_path_capability.dylib',Q,O/'native.json'])
   else:add('wasm-collect',['node',S/'docs/ingestion/norsand-1993/e2-v3/run_wasm_requests_v2.mjs',W/'atlas_path_capability.mjs',W/'atlas_path_capability.wasm',Q,O/'wasm.json'])
   add(backend+'-assess',['python3','-B',S/'docs/ingestion/norsand-1993/e2-v3/check_backend_results_v3.py',Q,O/(backend+'.json')])
 if name=='burgers':add('paired-replay-assess',['python3','-B',D/'assess_pairs.py','burgers',O/'native/calls.json',O/'wasm/calls.json',O/'paired-assessment.json'])
 if name=='sls':
  add('both-reference-assess',['python3','-B',A/'prepare_sls_reports.py']);add('paired-assess',['python3','-B',A/'check_sls_saved.py'])
 if name=='j2':
  for label,ref in [('main','references.json'),('defaults','default-references.json')]:add('paired-'+label,['python3','-B',A/'study_j2.py','parity',O/'native'/(label+'-raw.json'),O/('wasm-'+label+'-raw.json')],{'ATLAS_J2_REFERENCE':str(S/'docs/ingestion/j2-linear-hardening/execution-v2'/ref)})
 if name=='orthotropic':add('paired-source-gates',['python3','-B',D/'assess_pairs.py','orthotropic',O/'native/raw.json',O/'wasm-raw.json',O/'paired-assessment.json'])
 if name=='maxwell':
  add('paired-references-transactions',['python3','-B',A/'compare_maxwell.py']);add('actual-unreviewed-preset-metadata',['python3','-B',D/'prepare_maxwell_identity.py',S,W,O/'unreviewed-preset-identity.json']);add('presets-replay-before-review',['node',S/'tools/test_maxwell_public_presets.mjs',W,O/'presets.json',O/'unreviewed-preset-identity.json']);add('saved-preset-source-assessment',['python3','-B',D/'assess_maxwell_presets.py',O/'presets-assessment.json']);add('interface-contract-lifecycle',['node','--test',S/'tests/test_maxwell_atlas_contract.mjs',S/'tests/test_maxwell_atlas_runtime.mjs'])
 if name=='norsand':add('paired-assess',['python3','-B',S/'docs/ingestion/norsand-1993/e2-v3/check_backend_results_v3.py',S/'docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json',O/'native.json',O/'wasm.json'])
 profiles.append(dict(profile=name,native_build=str(N),wasm_build=str(W),output=str(O),status='BLOCKED on exact93-file documentary support addition'if name=='power-creep'else'BLOCKED Wasm on exact wasm_host.mjs support addition'if name=='burgers'else'prospective; independent plan review required',steps=steps))
plan=dict(identity='generic-current-profile-execution-v1',source_directory=str(S),source_freeze=str(C/'qualification-support-v4/source-freeze.json'),source_files=2628,execution_base=str(BASE),profiles=profiles,build_order='one explicit target at a time; native qualification precedes Wasm per profile; never overlap another coordinator slot',cwd=str(S),platform='macOS: NorSand .dylib; Linux requires separately recorded suffix-only platform resolution',preserved_profiles=['Lade exact reviewed versioned assets','Hill exact reviewed historical assets'],post_independent_build_review_only=[dict(profile='maxwell',cwd=str(S),argv=['python3','-B',str(S/'tools/check_maxwell_ci.py'),'--build',str(BASE/'maxwell/wasm-build'),'--output',str(BASE/'maxwell/evidence/guarded-ci')]),dict(profile='norsand',cwd=str(S),argv=['python3','-B',str(S/'tools/build_controlled_path_web.py'),str(BASE/'norsand/evidence/guarded-package'),str(BASE/'norsand/wasm-build')])],no_execution_by_author=True)
(D/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(dict(profiles=len(profiles),prospective_commands=sum(len(x['steps'])for x in profiles),compiled_calls=0)))
