from pathlib import Path
import hashlib,json,subprocess
from urllib.parse import urlsplit
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/ingestion/barodesy-clay-2017/browser-current-v3';B=P/'browser';O=P/'independent-review'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if (O/'inputs.json').exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
policy=read(P/'policy-v1.json');manifest=read(P/'evidence-manifest-v2.json')
for p,h in manifest['files'].items():assert sha(R/p)==h,p
for p,h in policy['files'].items():assert sha(R/p)==h,p
z=subprocess.run(['python3','-B',str(P/'check_saved.py')],cwd=R,capture_output=True,text=True);saved=read(P/'assessment-execution-v1.json');assert z.returncode==saved['exit_code']==0 and z.stdout==saved['stdout']and z.stderr==saved['stderr']==''
package=read(R/'docs/reviews/ordinary-model-deeplinks-v1/package-manifest-v1.json');site=R/policy['package'];assert site==Path(package['path'])and len(package['files'])==954
for p,x in package['files'].items():assert sha(site/p)==x['sha256']and(site/p).stat().st_size==x['bytes'],p
approval=read(R/'docs/admission/barodesy2017-agent-v1/approval-entry.json');canonical=approval['review'];assert canonical['sha256']=='e8c55ac7d5ae697f46fd79989fe9b9297adec9857ec08a7f218a5835df7df75e'and sha(R/canonical['path'])==canonical['sha256']
registry=read(R/'catalogue/approved-models.json');assert approval in registry['models']
reviews=read(B/'review-links-v2.json');canonicalasset=next(x for x in reviews['local']if urlsplit(x['url']).path.endswith('/'+canonical['path']));assert canonicalasset['sha256']==canonical['sha256']
local=urlsplit(canonicalasset['url']).path.removeprefix('/constitutive-atlas/');assert sha(site/local)==sha(R/canonical['path'])
# Full public export parser binds all request/settings/control bits and result state/strain/observable echoes.
js=r"""import{readFileSync,readdirSync}from'node:fs';import assert from'node:assert/strict';import{parseLaboratoryDocument}from'./web/laboratory-document.mjs';import{verifyScopedLaboratory}from'./web/laboratory-scope.mjs';const p='docs/ingestion/barodesy-clay-2017/browser-current-v3',read=x=>JSON.parse(readFileSync(x)),cat=read(read('docs/reviews/ordinary-model-deeplinks-v1/package-manifest-v1.json').path+'/models.json'),names=readdirSync(p+'/browser').filter(n=>n.endsWith('-export.json')||/^protocol-[0-4]\.json$/.test(n));assert.equal(names.length,12);for(const n of names){const d=read(p+'/browser/'+n);assert.deepEqual(parseLaboratoryDocument(JSON.stringify(d),cat),d.specification);verifyScopedLaboratory(d.result,d.specification,cat);assert.equal(d.result.points.length,d.specification.steps+1);assert.deepEqual(d.result.points[0].state,d.specification.initial);assert.equal(d.specification.model,'barodesy-clay-2017');}console.log('PASS: all12 actual UI exports full public request/loading/settings/result validation; no compiled calls');"""
y=subprocess.run(['node','--input-type=module','-e',js],cwd=R,capture_output=True,text=True);assert y.returncode==0,y.stderr
requests=read(R/'docs/ingestion/barodesy-clay-2017/ncl-current-v2/results/requests.json');cases={q['id']:q['specification']for q in requests}
for name in ['named','replayed','recovered','restored','reset']:
 d=read(B/(name+'-export.json'));assert d['specification']==cases['unchanged-default-drained'if name=='reset'else'ncl-isotropic']
cyclic=read(B/'cyclic-export.json');assert cyclic['specification']['protocol']==1 and cyclic['specification']['cycles']==1
ui=read(B/'named-ui.json');assert ui['model']=='barodesy-clay-2017'and urlsplit(ui['url']).fragment=='laboratory'
observed=read(P/'observations-v2.json');assert any('not a saved-state URL'in x for x in observed['known_limitations'])
# Retain and verify nature of two draft failures, rather than accepting their erroneous assumptions.
first=read(P/'initial-checker-failure.json');second=read(P/'second-checker-failure.json');assert first['exit_code']==second['exit_code']==1 and '4202'in first['stderr']and 'canvases'in second['stderr']
assert read(B/'mobile-layout.json')['canvases']==[]
assert 'Recorded agent-review status: accepted'in(B/'review-snapshot.yml').read_text()
assert 'No measurement overlays match this protocol' in (B/'named-snapshot.yml').read_text()
print(json.dumps({'passed':True,'saved_parent_assessment':json.loads(z.stdout),'package_files_verified':954,'canonical_review_identity':canonical['sha256'],'public_export_check':y.stdout.strip(),'draft_failures_retained':2,'cyclic_protocol':1,'named_import_url_is_not_saved_state':True,'reviewer_compiled_calls':0,'reviewer_browser_actions':0,'scope':'E7 local Barodesy browser/named-example integration within existing approved body2p zero-spin scope; no E4cleanrelease/E8/live/scientific expansion.'},indent=2))
