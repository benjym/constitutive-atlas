from pathlib import Path
import json,hashlib,importlib.util,subprocess,time
O=Path(__file__).resolve().parent;N=O.parent;S=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
assert not(O/'launch.json').exists()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
pc=load('pc',N/'package-final-source-binding-v1/continuation.py')
cont=pc.guard(S,'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9')
old=json.loads((N/'standard-web-launch-v2/launch.json').read_text());a=load('a',N/'standard-web-delivery-plan-v2/adapter.py')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip();assert head=='e58fea4c8bdabc7ac51b6feb3a952de2e52f4a6f'
subprocess.run(['git','diff','--quiet'],cwd=S,check=True)
recipe=a.commands(old['recipe']['operations'][0]['argv'][0],old['recipe']['operations'][3]['argv'][0],head)
original=json.loads(json.dumps(recipe));prefixes=[(str(N/'standard-web-delivery-actual-v1'),str(N/'standard-web-delivery-actual-v2')),('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v1','/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v2')]
def relocate(value,reverse=False):
 for before,after in prefixes:value=value.replace(after,before)if reverse else value.replace(before,after)
 return value
for op in recipe['operations']:op['argv']=[relocate(x)for x in op['argv']]
inverse=json.loads(json.dumps(recipe))
for op in inverse['operations']:op['argv']=[relocate(x,True)for x in op['argv']]
assert inverse==original
inputs=[]
for root in map(Path,old['web_catalogue_data_input_roots']):
 for p in root.rglob('*'):
  if '__pycache__'in p.parts or p.name=='.DS_Store'or(S/'web/dist')in p.parents:continue
  if p.is_file():assert not p.is_symlink();inputs.append(p)
old.pop('full811_source_inventory_unchanged')
old.update(identity='reviewed-packaging-only-source-continuation-launch-v3',epoch=time.time(),commit=head,parent='87b00ae240899dafbdf43165962eb2553a0ba717',historical_compilation_source_inventory_retained=True,postcompile_continuation=cont,web_catalogue_data_inputs=[pc.pin(p)for p in sorted(inputs)],recipe=recipe,ready_for_actual=True,old_launch_sha256='7a38d01539bd257da227e03e99b4a383853f42687cf405b5ea1bc544686ca909',original_raw811_validator_pass_claimed=False)
old['source_package_pins']=[pc.pin(r['path'])for r in old['source_package_pins']]
old['independent_reviews'].append(pc.pin(N/'shared-current17-review-v1/package-final-source-binding-v1/decision.json'))
for row in old['retained18']+old['other_role_pins']:pc.verify({k:row[k]for k in('path','sha256','bytes')})
assert a.validate_recovery(a.RECEIPT_SHA)==old['SLS_recovery']
f=O/'launch.json';f.write_text(json.dumps(old,indent=2)+'\n');h=hashlib.sha256(f.read_bytes()).hexdigest()
s=(N/'standard-web-launch-v2/launch.py').read_text()
s=s.replace("LAUNCH_SHA='7a38d01539bd257da227e03e99b4a383853f42687cf405b5ea1bc544686ca909'",f"LAUNCH_SHA='{h}'")
s=s.replace("OUT=N/'standard-web-delivery-actual-v1'","OUT=N/'standard-web-delivery-actual-v2'").replace(prefixes[1][0],prefixes[1][1])
s=s.replace("a=load('reviewed_package_adapter',N/'standard-web-delivery-plan-v2/adapter.py')","a=load('reviewed_package_adapter',N/'standard-web-delivery-plan-v2/adapter.py')\npc=load('reviewed_packaging_continuation',N/'package-final-source-binding-v1/continuation.py')")
s=s.replace(" c.guard(pre,'50bc4648bc749bdac1c04313de861f6ea75fdec1cd954824198527c4b10f4f0e',launch['numerical_source_review'])"," assert pc.guard(S,'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9')==launch['postcompile_continuation']")
s=s.replace("'baseline-five-C-web-'","'baseline-five-C-web-v2-'")
s=s.replace(" result=o.observe(argv,str(S),OUT/('outer-'+phase),env=env,timeout=1800)"," def operation():\n  observed=o.observe(argv,str(S),OUT/('outer-'+phase),env=env,timeout=1800)\n  assert observed.returncode==0,'first package failure retained; stop later phases'\n  return observed\n result=pc.observe(operation,S,'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9',OUT/(phase+'-compiled-continuation.json'))")
assert'c.guard('not in s;compile(s,'launch.py','exec');(O/'launch.py').write_text(s)
print(json.dumps({'commit':head,'launch_sha256':h,'source_count':cont['current_source_count'],'operations_identical_except_output_prefixes':True,'engine_executed':False}))
