from pathlib import Path
import json,hashlib,re
Q=Path(__file__).resolve().parent;N=Q.parents[1];W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
for directory,planhash,code in [('python-full-portable-actual-v1','de6a7b7737b559301ba7a1be2a064946101e8692c9cf664b1a7028b77c9d5321',1),('python-localhost-actual-v1','573b78900d3e9a011a05f546100337fd7d86349620fcd3ad3f90e44b26fcebc0',0)]:
 A=N/directory;p=json.loads((A/'plan.json').read_text());r=json.loads((A/'observer/receipt.json').read_text());ok(H(A/'plan.json')==planhash,'frozen plan '+directory)
 ok(H(Path(p['observer']))==p['observer_sha256']=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e' and p['timeout']==1800,'unchanged observer/1800 '+directory)
 ok(r['argv']==p['argv']and r['cwd']==p['cwd'],'exact argv/cwd '+directory)
 ok(r['returncode']==r['reaped_returncode']==code and r['mandatory_reap'],'genuine observed exit and mandatory reap '+directory)
 ok(r['status']==('passed'if code==0 else'nonzero'),'truthful observed status '+directory)
 for key in ('stdout','stderr','executable'):
  x=r[key];ok(H(Path(x['path']))==x['sha256']and Path(x['path']).stat().st_size==x['bytes'],'exact '+key+' '+directory)
 ok(H(W/'tools/run_ci_tests.py')==p['suite_source_sha256']=='caac825cb79dd804688a24db92aab108815725db00590c8d36cf24f7d5967997','unchanged original suite runner '+directory)
 ok(H(W/'tools/ci_exact_replays.json')==p['portable_policy_sha256']=='70643558114f1a28f436e8f21ab0e95a4d40572103f0ebf85cc5742ce3ad784a','unchanged portable replay policy '+directory)
 ok(H(Path(p['env']['ATLAS_SOLVER']))==p['runtime_sha256']=='606852e570c5d9082cec8b7281096ca352397de7b9c029e0630b5dca26c90747','unchanged retained runtime '+directory)
 if code:
  ok(r['cleanup_errors']==[{'type':'ProcessLookupError','message':'[Errno 3] No such process','benign_race':True}],'retained observer benign cleanup race disclosed')
 else:
  ok(r['cleanup_errors']==[],'HTTP clean observer close')
  ok(H(W/'tests/test_database_package.py')==p['test_source_sha256']=='e87c4cc970a24beb87b21fa92ee9bb149e6b4d3519e331cff8577c12929aa6af','exact original HTTP test source')
  out=(A/'observer/stderr.raw').read_text();ok(bool(re.search(r'^test_download_links_resolve_under_a_project_path_with_matching_bytes .* \.\.\. ok\n',out,re.M))and 'Ran 1 test in 1.502s\n\nOK\n'in out,'single original localhost test actually passes all assertions')
A=N/'python-full-portable-actual-v1';out=(A/'observer/stderr.raw').read_text();diag=json.loads((A/'environment-diagnosis-v1.json').read_text());ok('Ran 1619 tests in 755.078s\n\nFAILED (errors=24, skipped=81)'in out,'original suite failure remains1619/24errors/81skipped')
ok(not re.search(r'^FAIL: ',out,re.M),'no unittest assertion FAIL block')
blocks=[b for b in out.split('='*70+'\n')if b.startswith('ERROR: ')];ok(len(blocks)==24,'independent exact24 error blocks')
rows=[]
for b in blocks:
 lines=b.splitlines();head=lines[0][7:];exceptions=[line for line in lines if line.startswith(('FileNotFoundError:','PermissionError:','AssertionError:','ValueError:','TimeoutError:'))];ok(len(exceptions)==1,'one terminal expected exception '+head)
 exception=exceptions[0]
 if exception.startswith('FileNotFoundError:'):
  ok(exception=="FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/atlas-baseline-delivery-20261105/source/build/atlas_time_solver'",'exact absent time solver '+head)
  ok(head.startswith(('test_analytical_matrix_and_python_preparation','test_failed_late_substep_restores_pre_reset_state','test_internal_crossing_and_explicit_caller_partition','test_repeated_outer_trials_do_not_accumulate_resets','test_reset_frozen_across_cutbacks_and_parent_partition','test_reversal_boundary_multiple_reversals_and_zero','test_generated_fixture_matches_cartesian_reference')),'expected unchanged time-solver consumer '+head);kind='missing-test-only-time-solver'
 else:
  ok(exception=='PermissionError: [Errno 1] Operation not permitted'and'test_download_links_resolve_under_a_project_path_with_matching_bytes'in head and 'socketserver.py'in b and 'socket.bind'in b,'exact localhost socket bind permission exception');kind='local-socket-permission'
 rows.append({'test':head,'exception':exception,'kind':kind})
ok(rows==diag['errors_detail'],'all24 independent exception classifications equal retained diagnosis')
ok(sum(x['kind']=='missing-test-only-time-solver'for x in rows)==23 and sum(x['kind']=='local-socket-permission'for x in rows)==1,'23absent time executable and1localhost permission')
ok(not(W/'build/atlas_time_solver').exists(),'local time solver actually absent at review')
for n in ('tests/test_parent_reset.py','tests/test_tensor_square.py'):
 ok("os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver')"in(W/n).read_text(),'unchanged explicit local time executable locator '+n)
ok('ATLAS_TIME_SOLVER'not in json.loads((A/'plan.json').read_text())['env'],'no supplied local time solver env override')
private=Path('.local/retained-evidence/baseline-five-full-portable-preflight-20261105.raw');p=json.loads((A/'plan.json').read_text());ok(H(private)==p['process_inventory_sha256'],'exact private fullpreflight bound without copying raw')
(Q/'checks.json').write_text(json.dumps({'status':'PASS_DIAGNOSIS_ONLY','checks':len(labels),'labels':labels,'errors':rows,'local_full_suite_pass':False,'private_inventory':{'path':str(private),'sha256':H(private)}},indent=2)+'\n');print(json.dumps({'status':'PASS_DIAGNOSIS_ONLY','checks':len(labels),'full_suite_pass':False}))
