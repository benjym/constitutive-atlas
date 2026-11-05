"""Source/read-only launcher check; never imports its executing top level."""
from pathlib import Path
import ast,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;N=H.parents[1];L=N/'standard-web-launch-v3';checks=0

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def check(value,label):
 global checks
 assert value,label;checks+=1
j=read(L/'launch.json');check(sha(L/'launch.json')=='0b1f14757dd91c767cf2cfb560236c75741166fdfbac3210623dd5db6e22f374','launch identity');s=(L/'launch.py').read_text();ast.parse(s);check(j['commit']=='e58fea4c8bdabc7ac51b6feb3a952de2e52f4a6f'and j['parent']=='87b00ae240899dafbdf43165962eb2553a0ba717','genuine parent-provided revision identity')
spec=importlib.util.spec_from_file_location('_pure_package_successor',N/'standard-web-delivery-plan-v2/adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);pre=read(N/'rate-restoration-qualification-actual-v3/source-freeze.json');expected=a.commands(pre['python']['path'],pre['node']['path'],j['commit']);expected=json.loads(json.dumps(expected).replace('standard-web-delivery-actual-v1','standard-web-delivery-actual-v2').replace('site-C-standard-v1','site-C-standard-v2'));check(j['recipe']==expected,'exact accepted v2 recipe all operations except reviewed OBS/SITE routing');check(j['SLS_recovery']==a.validate_recovery(a.RECEIPT_SHA),'exact live-published three-file SLS recovery')
check(j['inventory']==pre['source_inventory']and len(j['inventory'])==811,'historical811 inventory unchanged (not rawcurrent validation)');check(len(j['web_catalogue_data_inputs'])==11261 and len(j['retained18'])==18 and len(j['other_role_pins'])==50,'complete declared counts')
for group in ['web_catalogue_data_inputs','source_package_pins','retained18','other_role_pins','independent_reviews']:
 for r in j[group]:
  p=Path(r['path']);check(p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'exact pinned '+group)
spec=importlib.util.spec_from_file_location('_reviewed_packaging_continuation',N/'package-final-source-binding-v1/continuation.py');pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc);current=pc.guard(Path(j['recipe']['cwd']),'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9');check(current==j['postcompile_continuation'],'exact accepted packaging-only transition/source/artifact guard');check(current['historical_source_count']==811 and current['current_source_count']==812 and current['original_raw811_validator_pass_claimed']is False and j['original_raw811_validator_pass_claimed']is False,'honest changed current rawsource context');
for r in j['independent_reviews']:check(read(Path(r['path']))['accepted']is True,'accepted exact review')
S=Path(j['recipe']['cwd'])
def inventory(roots):
 paths=[]
 for root in map(Path,roots):
  for p in root.rglob('*'):
   if '__pycache__'in p.parts or p.name=='.DS_Store'or(S/'web/dist')in p.parents:continue
   if p.is_file():check(not p.is_symlink(),'no symlink file');paths.append(p)
 return [{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(paths)]
check(inventory(j['web_catalogue_data_input_roots'])==j['web_catalogue_data_inputs'],'whole web/catalogue/data namespace exact');check(inventory(j['other_role_roots'])==sorted(j['other_role_pins'],key=lambda r:r['path']),'whole other-role namespace exact')
check("result=pc.observe(operation,S,'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9',OUT/(phase+'-compiled-continuation.json'))"in s,'reviewed pre/final continuation observer wrapper');
for literal in ["assert previous['returncode']==0 and previous['mandatory_reap']is True and previous['reaped_returncode']==0","assert not OUT.exists()","assert not Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v2').exists()","assert digest(c.c.OBSERVER)==c.c.OBSERVER_SHA","env=c.c.closed_environment();env.update(launch['recipe']['publication_environment_addition'])","observed=o.observe(argv,str(S),OUT/('outer-'+phase),env=env,timeout=1800)","assert result.returncode==0,'first package failure retained; stop later phases'","finally:\n try:guard();post['source_post_passed']=True","post['primary_error']=repr(error);raise","post['post_binding_error']=repr(error)","if primary is None:raise"]:check(literal in s,'retained lifecycle '+literal[:70])
check([r['id']for r in j['recipe']['operations']]==['fast-source-contracts','retained-source-guards','standard-web-package','package-engine-smoke','all994-built-dataset-transport','original-package-contracts','supported17-public-inputs','original-scoped-parity'],'all eight original operations')
print(json.dumps({'identity':'standard-web-launch-v3-source-and-pins-check','passed':True,'checks':checks,'launch':{'path':str(L/'launch.json'),'sha256':sha(L/'launch.json')},'launcher':{'path':str(L/'launch.py'),'sha256':sha(L/'launch.py'),'bytes':(L/'launch.py').stat().st_size},'Git_network_module_material_process_calls':0,'actual_package_accepted':False,'remaining':'Complete frozen actual receipts/physical inventory and operation results required; this checks existing source bindings only.'},indent=2))
