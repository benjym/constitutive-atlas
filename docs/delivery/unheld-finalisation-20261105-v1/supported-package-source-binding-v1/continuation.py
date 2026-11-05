"""Prospective exact-artifact continuation, not the old raw811 validator.

Only the reviewed six packaging hooks (five Python and one JavaScript) may differ; two packaging helpers
are added (one retained, one newly installed). Historical source/build/qualification receipts remain unchanged. This
file does not launch processes, generate models or mutate the source checkout.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,traceback
HERE=Path(__file__).resolve().parent
ROOT=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
CHANGED={'tools/profile_source_compatibility.py','tools/profile_source_compatibility_baseline.py','tools/build_controlled_time_web.py','tools/build_interface2016_web.py','tools/build_interface2016_baseline_web.py','tools/test_web_package.mjs'}
ADDED={'tools/package_final_source_view_v1.py','tools/package_final_source_view_v2.py'}
def pin(path):
 p=Path(path);data=p.read_bytes()
 return {'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
def verify(row):
 if pin(row['path'])!=row:raise ValueError('changed continuation input '+row['path'])
def load(path):return json.loads(Path(path).read_text())
def validate_transition(original,current,byname,root,qualified):
 """Pure explicit vector comparison; tools are not generally exempted."""
 root=Path(root);expected=dict(original)
 for name in CHANGED:
  if original[str(root/name)]!=qualified[name]:raise ValueError('unknown qualified packaging preimage')
 for name in CHANGED|ADDED:expected[str(root/name)]={'path':str(root/name),'sha256':byname[name]['sha256'],'bytes':byname[name]['bytes']}
 if current!=expected:raise ValueError('source inventory differs beyond explicit six changed plus two added packaging tool')
def physical_site(site):
 import os,stat
 site=Path(site);actual={}
 for directory,dirs,files in os.walk(site,followlinks=False):
  for name in dirs:
   q=Path(directory)/name
   if q.is_symlink():raise ValueError('site directory symlink')
  for name in files:
   q=Path(directory)/name;st=q.lstat()
   if not stat.S_ISREG(st.st_mode):raise ValueError('nonregular site asset')
   relative=str(q.relative_to(site));actual[relative]={'path':relative,'sha256':pin(q)['sha256'],'size_bytes':st.st_size,'mode':stat.S_IMODE(st.st_mode)}
 return actual
def retained_site(authority):
 """Runtime only: complete immutable built-site and six passed raw-stage proof."""
 import os,stat
 verify(authority);failure=load(authority['path'])
 expected_phases=['fast-source-contracts','retained-source-guards','standard-web-package','package-engine-smoke','all994-built-dataset-transport','original-package-contracts']
 passed=failure['phase_results'][:6]
 if [r['phase']for r in passed]!=expected_phases or any(r['returncode']!=0 or r['mandatory_reap']is not True for r in passed):raise ValueError('six genuine completed/reaped phases required')
 for row in failure['files']:verify(row)
 inventory_pin=next(row for row in failure['files']if row['path'].endswith('/physical-site-inventory.json'));inventory=load(inventory_pin['path']);site=Path(inventory['site'])
 if site!=Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v3')or site.resolve()!=site:raise ValueError('exact retained built site required')
 expected={r['path']:r for r in inventory['files']};actual=physical_site(site)
 if actual!=expected or len(actual)!=1565:raise ValueError('complete retained site changed')
 return {'site':str(site),'inventory':inventory_pin,'members':len(actual),'six_passed_phases':passed}
def validate_review(review,manifest_sha256):
 if review.get('identity')!='supported-package-source-binding-independent-review-v1' or review.get('accepted')is not True or review.get('author_run')!='/root/baseline_migration' or review.get('reviewer_run')!='/root/publication_operations_review' or review.get('proposal_manifest_sha256')!=manifest_sha256 or review.get('unresolved_blockers')!=[]:raise ValueError('exact genuine independent supported checker acceptance required')
def guard(root,manifest_sha256):
 root=Path(root)
 if root!=ROOT or root.resolve()!=root:raise ValueError('exact physical qualified source root required')
 if sys.flags.optimize:raise ValueError('assertions must be enabled')
 if pin(HERE/'manifest.json')['sha256']!=manifest_sha256:raise ValueError('wrong reviewed continuation packet')
 for row in load(HERE/'manifest.json')['files']:
  name=Path(row['path'])
  if name.is_absolute()or'..'in name.parts:raise ValueError('unsafe continuation member')
  q=HERE/name
  if q.is_symlink()or pin(q)['sha256']!=row['sha256']or q.stat().st_size!=row['bytes']:raise ValueError('continuation packet member drift')
 review_path=HERE.parent/'shared-current17-review-v1/supported-package-source-binding-v1/decision.json'
 if review_path.is_symlink()or review_path.resolve()!=review_path:raise ValueError('review must be canonical regular')
 review_pin=pin(review_path);validate_review(load(review_path),manifest_sha256)
 refs=load(HERE/'continuation-authorities.json')
 for row in refs.values():verify(row)
 actual=load(refs['qualified_actual_review']['path'])
 if actual.get('accepted')is not True or actual.get('author_run')!='/root'or actual.get('reviewer_run')!='/root/controlled_refresh_review'or actual.get('complete_actual_manifest')!=refs['qualified_actual_manifest']:raise ValueError('genuine complete C runtime acceptance required')
 for row in load(refs['qualified_actual_manifest']['path'])['files']:verify(row)
 delta=[*load(refs['previous_receipt_delta']['path'])['files'],*load(HERE/'source-delta.json')['files']];byname={r['path']:r for r in delta}
 changed={r['path']for r in delta if r['preimage_sha256']is not None}
 added={r['path']for r in delta if r['path'].startswith('tools/')and r['preimage_sha256']is None}
 if changed!=CHANGED or added!=ADDED-{'tools/package_final_source_view_v1.py'}:raise ValueError('only literal six changed plus one newly installed packaging tool allowed')
 for row in delta:
  q=root/row['path']
  if q.is_symlink()or q.resolve()!=q or pin(q)['sha256']!=row['sha256']or q.stat().st_size!=row['bytes']:raise ValueError('installed exact packaging proposal changed '+row['path'])
 retained=next(r for r in load(refs['previous_packaging_delta']['path'])['files']if r['path']=='tools/package_final_source_view_v1.py')
 if retained['preimage_sha256']is not None:raise ValueError('originally added retained helper required')
 byname[retained['path']]=retained
 qualified=load(HERE/'qualified-preimages.json')
 if set(qualified)!=CHANGED:raise ValueError('exact original qualified six-path vector required')
 spec=importlib.util.spec_from_file_location('_current_package_view',root/'tools/package_final_source_view_v2.py');view=importlib.util.module_from_spec(spec);spec.loader.exec_module(view)
 proof=view.authority(root) # genuine separate CLOSED consumer review mandatory
 if proof['implementation']!={n:byname[n]['sha256']for n in (CHANGED|ADDED)-{'tools/test_web_package.mjs'}}:raise ValueError('closed current implementation differs')
 def qualified_pin(row):
  path=Path(row['path'])
  if path.is_relative_to(root)and str(path.relative_to(root))in CHANGED:
   name=str(path.relative_to(root));change=byname[name]
   if row!=qualified[name]:raise ValueError('unknown original qualified packaging input')
   archive=root/'catalogue/source-snapshots'/row['sha256']/name
   observed=pin(archive);observed['path']=row['path']
   if observed!=row:raise ValueError('exact historical packaging preimage missing')
  else:verify(row)
 pre=load(refs['source_freeze']['path']);f=load(refs['execution_freeze']['path'])
 if pre['repo']!=str(root)or f['repo']!=str(root)or pre['source_inventory']!=f['source_inventory']or f['source_freeze']!=refs['source_freeze']:raise ValueError('original source/artifact receipt closure differs')
 original={r['path']:r for r in pre['source_inventory']}
 spec=importlib.util.spec_from_file_location('_unchanged_source_inventory',refs['original_source_files_module']['path']);original_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(original_module)
 current={str(p):pin(p)for p in original_module.source_files(root)}
 validate_transition(original,current,byname,root,qualified)
 for row in [*pre['inputs'],*pre['build_tools'].values(),pre['node'],pre['python'],*f['inputs'],*f['artifacts'].values(),*f['candidates'].values()]:qualified_pin(row)
 binding=load(refs['plan_binding']['path']);verify(binding['launch_binding']);launch=load(binding['launch_binding']['path'])
 verify(launch['plan_review'])
 for item in launch['installations'].values():
  verify(item['receipt']);verify(item['review'])
  for row in item['source_pins']:qualified_pin(row)
 for key in ('supplemental_regression_test','supplemental_ensemble_test'):verify(binding[key])
 for row in load(refs['standard_package_sources']['path']):qualified_pin(row)
 site=retained_site(refs['retained_site_failure'])
 return {'identity':'supported-package-current-source-continuation-v1','retained_site':site,'independent_review':review_pin,'historical_source_count':len(original),'current_source_count':len(current),'changed':sorted(CHANGED),'added':sorted(ADDED),'compiled_source_and_artifacts_unchanged':True,'original_raw811_validator_pass_claimed':False,'current_inventory':list(current.values()),'artifacts':f['artifacts'],'source_view_proof_sha256':view.digest(view.regular(root,view.PROOF))}
def observe(operation,root,manifest_sha256,report):
 """Parent-owned lifecycle wrapper; never masks primary with postguard errors."""
 report=Path(report)
 if report.exists():raise ValueError('never overwrite continuation observation')
 before=guard(root,manifest_sha256);primary=None;post=[];after=None
 try:return operation()
 except BaseException as error:primary=error;raise
 finally:
  try:
   after=guard(root,manifest_sha256)
   if after!=before:raise ValueError('continuation binding changed while packaging')
  except BaseException as error:post.append(repr(error))
  record={'identity':'supported-package-source-continuation-operation-binding-v1','before':before,'after':after,'primary':repr(primary)if primary else None,'traceback':''.join(traceback.format_exception(type(primary),primary,primary.__traceback__))if primary else None,'post_errors':post,'passed':primary is None and not post}
  try:
   with report.open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
  except BaseException as error:
   post.append(repr(error));record['passed']=False;sys.stderr.write(json.dumps(record)+'\n')
  if primary is not None:primary.packaging_post_errors=[*getattr(primary,'packaging_post_errors',[]),*post]
  elif post:raise RuntimeError('postcompile packaging binding failed; retained receipt')
if __name__=='__main__':raise SystemExit('Source-only parent API: guard/observe require reviewed exact packet and genuine closed source-view acceptance.')
