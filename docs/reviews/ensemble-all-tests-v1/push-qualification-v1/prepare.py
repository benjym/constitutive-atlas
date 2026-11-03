from pathlib import Path
import hashlib,json,shutil
src=Path('/Users/bmar5496/code/constitutive-atlas');dst=Path('/private/tmp/atlas-ensemble-all-tests-push-v1');evidence='docs/reviews/ensemble-all-tests-v1'
qualified=json.loads((src/evidence/'source-hashes.json').read_text())
for name,digest in qualified.items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==digest,name
files=['web/ensemble.mjs','web/ensemble-experiments.mjs','web/ensemble-view.mjs','web/ensemble-plots.mjs','web/ensemble.css','tools/build_ensemble_web.py','tests/test_ensemble_tests.mjs','tests/test_ensemble_plots.mjs','tests/test_ensemble_package.py']
for name in files:shutil.copy2(src/name,dst/name)
shutil.copytree(src/evidence,dst/evidence)
p=dst/'tools/build_web.py';s=p.read_text();assert "'ensemble.mjs', 'ensemble-plots.mjs'" in s;s=s.replace("'ensemble.mjs', 'ensemble-plots.mjs'","'ensemble.mjs', 'ensemble-experiments.mjs', 'ensemble-plots.mjs'",1);p.write_text(s)
# Exclude the same separate pre-existing confinement and Open-in-testing work
# excluded from the previous ensemble-only public commit.
p=dst/'web/ensemble.mjs';s=p.read_text();s='\n'.join(l for l in s.split('\n') if not l.startswith(('export const confinementControls=','export function studyConfinement(')) and 'require(Object.hasOwn(confinementControls' not in l)
s=s.replace(",confinement='recorded'",'').replace("Array(2).fill(confinement==='recorded'?r.radial_effective_stress:record.initial.effective_stress[1])",'[r.radial_effective_stress,r.radial_effective_stress]').replace("control:undrained?'constant-volume-axisymmetric-effective-stress':confinementControls[confinement]","control:undrained?'constant-volume-axisymmetric-effective-stress':'direct-author-membrane-corrected-radial-effective-stress'")
s=s.replace("confinement==='recorded'?'Conditional replay: measured volumetric strain contributes to membrane-corrected radial input.':'Idealized comparison: radial effective stress is held at its initial value; recorded confinement fluctuations are not imposed.'","'Conditional replay: measured volumetric strain contributes to membrane-corrected radial input.'").replace(',studyConfinement(study)','').replace(',studyConfinement(document.study)','');p.write_text(s)
p=dst/'web/ensemble-view.mjs';s=p.read_text().replace(',studyConfinement','');s='\n'.join(l for l in s.split('\n') if not l.startswith((' const confinementLabel=',' confinement.onchange=',' open.onclick=')) and 'confinementLabel.hidden=' not in l)
s=s.replace("confinement.value==='constant'?'Axial strain follows acquired endpoints; radial effective stress is held at its measured starting value. This is an idealized loading comparison; measured curves are unchanged.':",'').replace(',record.rows.length-1,confinement.value','').replace('confinement.value=studyConfinement(prepared);','')
s=s.replace("const open=node('button','Open in Model testing');open.id='ensemble-open-model';open.type='button';open.disabled=true;",'').replace('detailText,open,single','detailText,single').replace('single.disabled=open.disabled=','single.disabled=');p.write_text(s)
p=dst/'IMPLEMENTATION_PLAN.md';s=p.read_text();row=next(l for l in (src/'IMPLEMENTATION_PLAN.md').read_text().splitlines() if l.startswith('- [X] **WEB-ensemble-all-tests-v1**'));p.write_text(row+'\n\n'+s)
print('Prepared scoped all-tests changes; shared checkout untouched.')
