"""Coordinator's optimistic, narrowly scoped main-atlas integration."""
from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 baseline=json.loads((OUT/'concurrent-refresh-v2/frozen/bindings-before.json').read_text())
 for p in baseline['live_source_identities']:assert sha(ROOT/p['original_path'])==p['sha256'],p['original_path']
 model='norsand-jefferies-1993-active-axial';review=ROOT/'catalogue/agent-reviews/norsand-1993-agent-v1.json'
 assert not review.exists()
 validate_review(ROOT/'docs/ingestion/norsand-1993/approval-v1/agent-review-v1.json',for_approval=True)
 for name in ('path-engine.mjs','path-worker.mjs','path-laboratory.mjs'):assert not (ROOT/'web'/name).exists()
 app=(ROOT/'web/app.js').read_text()
 app=replace(app,"import {setupSlsLaboratory} from './sls-laboratory.mjs';","import {setupSlsLaboratory} from './sls-laboratory.mjs';\nimport {setupPathLaboratory} from './path-laboratory.mjs';")
 app=replace(app,"setupSlsLaboratory({chart,cancelOrdinary:()=>cancel('')})]);","setupSlsLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupPathLaboratory({chart,cancelOrdinary:()=>cancel('')})]);")
 assert app.count("timedView?.supports(entry.id)&&entry.timed_laboratory==='index.html'")==2
 app=app.replace("timedView?.supports(entry.id)&&entry.timed_laboratory==='index.html'","timedView?.supports(entry.id)&&(entry.timed_laboratory==='index.html'||entry.path_laboratory==='index.html')")
 app=replace(app,"timedView?.supports(entry.id)?'Approved bounded scope · physical-time laboratory'","timedView?.supports(entry.id)?(entry.path_laboratory?'Approved bounded scope · controlled-path laboratory':'Approved bounded scope · physical-time laboratory')")
 app=replace(app,"}else if(timedRoute){const section=element('section');","}else if(entry.path_laboratory&&timedView?.supports(entry.id)){body.append(element('p','The main laboratory exposes dimensionless shear progress, complete initial history and linearly changing stress controls for the original drained active axial law. Experimental comparison is unavailable.'));}else if(timedRoute){const section=element('section');")
 builder=(ROOT/'tools/build_web.py').read_text()
 builder=replace(builder,"    parser.add_argument('--output',type=Path,help='Explicit local output directory')","    parser.add_argument('--controlled-path-wasm-dir',type=Path,default=ROOT/'docs/ingestion/norsand-1993/shared-integration-v1/wasm-v2',help='Exact retained qualified controlled-path engine; generated source and runtime hashes are checked')\n    parser.add_argument('--output',type=Path,help='Explicit local output directory')")
 builder=replace(builder,"    (dest/'.nojekyll').touch()","    from build_controlled_path_web import bundle as bundle_controlled_path\n    bundle_controlled_path(dest,args.controlled_path_wasm_dir)\n    (dest/'.nojekyll').touch()")
 shutil.copyfile(ROOT/'docs/ingestion/norsand-1993/approval-v1/agent-review-v1.json',review)
 validate_review(review,for_approval=True);entry=approval_entry(review);write(OUT/'approval.json',entry)
 registry=ROOT/'catalogue/approved-models.json';data=json.loads(registry.read_text());assert not any(a['model_id']==model for a in data['models']);data['models'].append(entry);write(registry,data)
 manifest=ROOT/'catalogue/manifest.json';data=json.loads(manifest.read_text());family=next(a for a in data['models'] if a['id']=='norsand-1993')
 family.update(status='reviewed',note='Original1993 source verified from all13pages. Family discovery identity retained; the separately listed active axial variant has bounded independent agent approval. Later revisions remain separate.',capability_gap='Family discovery is not a general3D implementation. Only the separately identified original active drained axial formulation is admitted within its reviewed numerical scope.')
 family['research_sources'].append({'url':'https://github.com/benjym/constitutive-atlas/blob/main/docs/ingestion/norsand-1993/supplied-original-v2/README.md','role':'Verified original-source packet','locator':'Original13pages, printed91–103; equations5–12; private PDF hash in public receipt'})
 data['models'].append({'id':model,'name':'NorSand 1993 · original drained active axial law','family':'critical-state plasticity','status':'reviewed','executable':False,'path_laboratory':'index.html','dossier':'docs/models/norsand-1993-active-axial-v1.md','discovery_url':'https://doi.org/10.1680/geot.1993.43.1.91','note':'Independent agent approval for the exact original rigid-plastic active axial variant and frozen numerical examples. Main-atlas controlled-path interface; browser qualification recorded separately. No experimental validation or general3D claim.','catalogue_sources':[{'url':'https://doi.org/10.1680/geot.1993.43.1.91','role':'Original publication · Jefferies1993','locator':'Géotechnique43(1),91–103; equations5–12 and original image-pressure closure'}]});write(manifest,data)
 pub=ROOT/'catalogue/publications.json';data=json.loads(pub.read_text());node=next(a for a in data['publications'] if a.get('doi')=='10.1680/geot.1993.43.1.91');node['model_ids'].append(model)
 receipt='docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json'
 node['evidence'].append({'url':'https://doi.org/10.1680/geot.1993.43.1.91','path':receipt,'sha256':sha(ROOT/receipt),'accessed_on':'2026-11-01','locator':'User-supplied original13pages, printed91–103; exact private PDF identity and equation locators'})
 node['unresolved']=['Deposited title contains the typo “simle”; raw metadata and title are preserved.','Exact active axial variant independently approved within its frozen numerical scope; experimental validation, later variants and general3D continuation remain unsupported.'];write(pub,data)
 for name in ('path-engine.mjs','path-worker.mjs','path-laboratory.mjs'):shutil.copyfile(ROOT/'docs/ingestion/norsand-1993/browser-v1/proposed'/name,ROOT/'web'/name)
 (ROOT/'web/app.js').write_text(app);(ROOT/'tools/build_web.py').write_text(builder)
 dossier=ROOT/'docs/models/norsand-1993-active-axial-v1.md';assert not dossier.exists()
 dossier.write_text('''# NorSand 1993 — original active drained axial formulation

Jefferies, M.G. (1993), *Nor-Sand: a simple critical state model for sand*, Géotechnique43(1),91–103. [Original publication](https://doi.org/10.1680/geot.1993.43.1.91). The privately retained supplied PDF has SHA-256 fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9; all13pages were visually inspected. Raw copyrighted pages are not redistributed.

The admitted variant is `norsand-jefferies-1993-active-axial`, definition SHA-25667ff78f8cd56fd8812ba42f4456105b6e7ae217090dbcf40d8f8d5f839995d2c. Its original rigid-plastic equations5–12 use effective compression-positive stress, fixed axial Mandel components and dimensionless shear progress. C=p−Kq controls stress: K=1/3 means constant cell pressure; K=0 means constant mean pressure. A run carries the complete state, coordinate, parameters and current controls. Trial failure rolls back the entire requested advance.

Independent scientific approval covers the exact definition, nine frozen original-equation reference cases and58requests per native/Wasm backend. The numerical corpus uses M1.2,h280,λ.0135,Γ.82,pref1000Pa and N0/.2/.39 with specified initial state/control combinations through progress.16. These sampled cases do not validate the full declared parameter box. The current-volume void-ratio reconstruction and adaptive midpoint solver are explicit Atlas choices.

[Accepted agent checklist](../../catalogue/agent-reviews/norsand-1993-agent-v1.json), [source receipt](../ingestion/norsand-1993/supplied-original-v2/source-receipt.json), [review report](../ingestion/norsand-1993/approval-v1/REPORT.md), and [delivery ledger](../ingestion/norsand-1993/DELIVERY.md) record exact evidence and interface status. The main laboratory offers complete state/stress controls, plots and full-context export/import/replay. Experimental measurement comparison is unavailable: no compatible licensed calibrated dataset is supplied.

Elasticity, inactive/interior unloading, cyclic response, later NorSand revisions, general3D/Lode continuation, finite rotations, FE/MPM and analytic tangents are excluded. The unchanged exact definition retains historical staged/draft metadata; the separate approval registry supplies the bounded admission decision. Actual browser and live deployment status must be read separately in the delivery ledger.
''')
 for p in ('docs/STATUS.md','ROADMAP.md'):
  with (ROOT/p).open('a') as f:f.write('\n\nNorSand1993: the separately identified original active drained axial variant now has exact-byte independent agent approval and58/58 native/Wasm qualification. Main-atlas controlled-path integration is in progress; experimental/general3D/live claims remain excluded. See [delivery ledger]('+('ingestion/norsand-1993/DELIVERY.md' if p.startswith('docs/') else 'docs/ingestion/norsand-1993/DELIVERY.md')+').\n')
 write(OUT/'integration-result-v1.json',{'result':'PASS','model':model,'approval_path':str(review.relative_to(ROOT)),'prior_model_entries_preserved':len(json.loads(manifest.read_text())['models'])-1,'shared_files':{x['original_path']:sha(ROOT/x['original_path']) for x in baseline['live_source_identities']}})
 print('Integrated exact review, approval, source lineage and main-atlas controlled-path hooks.')
if __name__=='__main__':main()
