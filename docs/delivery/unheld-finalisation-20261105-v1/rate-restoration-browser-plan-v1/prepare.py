from pathlib import Path
import json,hashlib,copy
R=Path('/Users/bmar5496/code/constitutive-atlas');N=R/'docs/delivery/unheld-finalisation-20261105-v1';P=N/'current17-browser-plan-v1';O=N/'rate-restoration-browser-plan-v1';oldout=json.loads((P/'plan.json').read_text())['output_directory'];out=str(R/'output/playwright/baseline-five-rate-restoration-20261105-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def emit(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
receipt=N/'retained-original702-browser-inputs-v1/receipt.json';routes=json.loads(receipt.read_text())['browser_pins'];mapping={x['path']:x['retained_path']for x in routes}
policy=json.loads((P/'POLICY.json').read_text());policy['identity']='baseline-five-rate-restoration-browser-download-policy-v1';policy['revision']='PENDING independently bound fixed-source production revision'
for row in policy['pins']:
 if row['path']in mapping:row['path']=mapping[row['path']]
policy['reference_index']=mapping[policy['reference_index']]
# Catalogue identity remains unchanged; immutable prior catalogue17 file and policy authorities remain pinned.
emit('POLICY.json',policy)
(O/'validate.mjs').write_bytes((P/'validate.mjs').read_bytes())
plan=json.loads((P/'plan.json').read_text());plan.update(identity='rate-restoration-browser-plan-v1',author_run='/root/controlled_refresh_review',output_directory=out,source_revision='PENDING fixed-source revision',actual_origin_package_API_binding='PENDING genuine fixed-source finalpackage/Pages/API/HTTP identity',runtime_regression_binding='PENDING accepted new-core original701/interface87/DP83/pair/MD/control and exact previously failing101point replay',ready_for_actual=False)
for row in plan['scripts']:
 previous=Path(row['path']);name=previous.name;dest=O/'scripts'/name;dest.write_text(previous.read_text().replace(oldout,out));row.update(source=str(previous),original_sha256=sha(previous),path=str(dest),install_path=out+'/'+name,sha256=sha(dest),delta='accepted current17 script; output path substitution only')
for row in plan['input_fixtures']:
 row['install_path']=row['install_path'].replace(oldout,out)
 fixture=O/'wrong-catalogue.json';fixture.write_bytes(Path(row['source']).read_bytes());row['source']=str(fixture)
pre=O/'scripts/measurement-precondition.js';pre.write_text('''const root='https://benjym.github.io/constitutive-atlas/';
await page.goto(root+'#laboratory?model=hypoplastic-sand-igs97');
await page.locator('#reset').waitFor({state:'visible'});
await page.locator('#reset').click();
await page.waitForFunction(()=>document.querySelector('#model')?.value==='hypoplastic-sand-igs97'&&!document.querySelector('#export-run')?.disabled,null,{timeout:30000});
const compare=page.locator('#measurements');
if(await compare.getAttribute('open')===null)await page.locator('#measurements > summary').click();
const picker=page.getByRole('combobox',{name:'Experimental test',exact:true});
await picker.waitFor({state:'visible'});
await page.waitForFunction(()=>!document.querySelector('#experiment-select')?.disabled,null,{timeout:30000});
if(await page.locator('#model').inputValue()!=='hypoplastic-sand-igs97'||await page.locator('#export-run').isDisabled()||await compare.getAttribute('open')===null)throw Error('measurement precondition failed');
return {status:'measurement-precondition-ready',model:await page.locator('#model').inputValue(),reset:true,compareOpen:true,experimentalPickerEnabled:await picker.isEnabled()};
''')
plan['scripts'].append({'path':str(pre),'install_path':out+'/'+pre.name,'sha256':sha(pre),'delta':'new explicit reset/open-Compare setup; no replacement assertion or data change'})
plan['execution_order']=['model-linear-elastic.js','model-drucker-prager.js','model-modified-cam-clay.js','model-hypoplastic-sand-vw96.js','model-hypoplastic-sand-igs97.js','named.js','negative-mobile.js','measurement-precondition.js','compression-live-v1.js','cycles-current17.js']
plan['reference_source_directory']=str(N/'retained-original702-browser-inputs-v1/source');plan['reference_relocation_receipt']={'path':str(receipt),'sha256':sha(receipt)}
plan['installation_recipe']='install.py is source-reviewable only; coordinator runs after separate source acceptance. It verifies all script/input fixture pins, installs all of both lists into a new directory, rejects existing output/path escape/symlink.'
plan['future_launch_binding_required']=['exact successful fixed-source build/runtime independent review','genuine production revision/Pages/API artifact and uploaded-origin JS/Wasm/model identity','pinned accepted browser-plan review and all installation hashes','original five/nine downloaded reference policy; actual console/screenshots/HTTP proof; final all requiredCI terminal success']
emit('plan.json',plan)
emit('relocation.json',{'receipt_sha256':sha(receipt),'paths':routes,'logical_input_hashes_unchanged':True})
emit('GATES.json',{'identity':'rate-restoration-browser-prospective-gates-v1','author_run':'/root/controlled_refresh_review','predecessor_review_sha256':'70ee0d026bfa51c4120cbcd2cdcaa49894dacd5de3796370e6a4eb5cb1e809da','scope':'Distinct successor; no actual restored-runtime browser observations','preserved':['all original579 saved download/CSV/finite/replay/mobile/named physical1e-10 exact-other gates','original9 exact named specifications/settings and original702 reference hashes','five profiles/definition/E5 technical disclosures and invalid/stale/mobile UI gates','original normalized/largest gzip assertions','current17 cycles retention/reset0 gate','all old640 failures and independent491fdbb6 finding immutable'],'changes':['new output identity only in original9 scripts','10 exact authority paths relocated via durable receipt; no reference policy or reference bytes edited','explicit all input_fixtures installation; original omission/failure retained','new measurement reset/openCompare precondition immediately before unchanged compression; cycles runs last'],'before_browser':['separate independent successor source acceptance','new-core native/Wasm failure101point replay and original701/42interfaces/87calls/DP83/pair plus MD/control gates','genuine exact fixed-source Pages/API/artifact/HTTP bindings, no640binary inheritance'],'final_E8':['all required fullCI terminal successes','all unchanged browser gates/579 validator successful and independently reviewed','exact uploaded/live package/runtime identity; failures retained'],'actual_status':'NOT_RUN'})
print('prepared successor sources only')
