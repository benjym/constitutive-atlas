"""Build a public, offline-replayable model download; never include source PDFs."""
from pathlib import Path
import hashlib,json,shutil,zipfile,subprocess
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'downloads';SITE=Path('/private/tmp/atlas-norsand-main-atlas-v1/site-v2')
def main():
 OUT.mkdir(exist_ok=True);packet=OUT/'norsand-1993-qualified';assert not packet.exists();packet.mkdir();(packet/'engine-path').mkdir()
 for name in ('engine.mjs','engine.wasm','catalogue.json','model.json','example.json','review.json','approval.json','qualification.json','source-receipt.json','identity.json'):
  shutil.copyfile(SITE/'engine-path'/name,packet/'engine-path'/name)
 shutil.copyfile(SITE/'path-engine.mjs',packet/'path-engine.mjs')
 shutil.copyfile(ROOT/'docs/ingestion/norsand-1993/atlas-v1/browser-default-run-v2.json',packet/'default-run.json')
 for name,source in [('SOURCE.md','docs/ingestion/norsand-1993/supplied-original-v2/README.md'),('REVIEW.md','docs/ingestion/norsand-1993/approval-v1/REPORT.md'),('crosswalk.json','docs/ingestion/norsand-1993/supplied-original-v2/crosswalk.json'),('independent-references.json','docs/ingestion/norsand-1993/e2-v3/references-v2.json')]:shutil.copyfile(ROOT/source,packet/name)
 (packet/'replay.mjs').write_text('''import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import createModule from './engine-path/engine.mjs';
import {createPathEngine} from './path-engine.mjs';
const read=async p=>readFile(new URL(p,import.meta.url)),json=async p=>JSON.parse(await read(p));
const manifest=await json('./SHA256.json');
for(const [name,hash]of Object.entries(manifest))assert.equal(createHash('sha256').update(await read('./'+name)).digest('hex'),hash,name);
const saved=await json('./default-run.json'),module=await createModule({wasmBinary:await read('./engine-path/engine.wasm')}),engine=createPathEngine(module,await json('./engine-path/catalogue.json'));
const result=engine.run(saved.model,saved.request);assert.deepEqual(result,saved.result);
console.log(JSON.stringify({result:'PASS',model:saved.model,exact_browser_replay:true,points:result.points.length,endpoint:result.points.at(-1)},null,2));
''')
 (packet/'README.txt').write_text('''NorSand1993 — exact qualified original active drained axial variant

Run offline with Node.js: node replay.mjs
This checks download hashes and exactly reproduces the complete41point run exported by the tested main-atlas browser interface.

The generated generic Wasm engine, exact model JSON, complete initial context/request/result, independent agent checklist, source receipt and source/schema crosswalk are included. No installation or network request is needed. engine-path/model.json is the reusable declarative v0.3 record. This compact Node replay download is separate from the full atlas website.

Publication: Jefferies1993, DOI10.1680/geot.1993.43.1.91.
Scope: original rigid-plastic active monotonic drained axial law; compression-positive effective stress; explicit dimensionless shear progress and C=p-Kq controls. Nine frozen parameter/state/control cases and58requests/backend qualified; arbitrary parameter combinations are exploratory. No experimental validation, elasticity, unloading/cyclic/general3D/finite-rotation claim. Exact historical staged model wording is retained; separate approval carries the bounded decision.

Raw copyrighted PDF pages and measurement arrays are excluded. The source remains privately retained and identified by SHA-256 in the receipt. Scientific approval and local browser qualification do not establish public live deployment; E8 remains open pending authorization and shared release gates.
''')
 hashes={p.relative_to(packet).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(packet.rglob('*')) if p.is_file()};(packet/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
 run=subprocess.run(['node',str(packet/'replay.mjs')],capture_output=True,text=True);assert run.returncode==0,run.stderr
 (OUT/'download-replay-result-v1.json').write_text(json.dumps({'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
 archive=OUT/'norsand-1993-qualified.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(packet.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(OUT))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None;assert not any(n.lower().endswith('.pdf') for n in z.namelist())
 receipt={'path':archive.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'files':len(hashes)+1,'offline_exact_browser_replay':'PASS','private_pdf_included':False};(OUT/'download-receipt-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
