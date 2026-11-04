from pathlib import Path
import hashlib,json,runpy,contextlib,io
R=Path(__file__).resolve().parent;P=R.parent/'nine-example-refresh-plan-v1';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,b):assert b,n;checks.append(n)
ck('manifest',sha(P/'manifest.json')=='22437c460a1bd435e03fa63936e6e95774883931afb97f4f1d18faad9002c79d')
m=json.loads((P/'manifest.json').read_text());ck('106 unique members',len(m['files'])==106 and len({r['path']for r in m['files']})==106)
for r in m['files']:ck(r['path'],sha(P/r['path'])==r['sha256'] and (P/r['path']).stat().st_size==r['bytes'])
original=Path.write_text
writes=[]
def owned(self,*a,**kw):
 assert self==P/'source-checks.json','unexpected author write '+str(self)
 writes.append(str(self));return original(R/'author-source-checks.json',*a,**kw)
Path.write_text=owned;s=io.StringIO()
try:
 with contextlib.redirect_stdout(s):runpy.run_path(str(P/'check.py'),run_name='__main__')
finally:Path.write_text=original
(R/'author-source.stdout.txt').write_text(s.getvalue());ck('strict120 author source replay',len(writes)==1 and (R/'author-source-checks.json').read_bytes()==(P/'source-checks.json').read_bytes())
rows=json.loads((P/'requests.json').read_text());ck('nine unique distinct safe candidate document targets',len({r['new_document_path']for r in rows})==9 and all(r['new_document_path'].startswith('protocols/') and '..'not in r['new_document_path'].split('/') for r in rows))
ck('four preserved original metadata',all(rows[i]['entry']==json.loads((P/'original-four-index.json').read_text())['examples'][i] for i in range(4)))
run=(P/'collect.mjs').read_text();assembly=(P/'assemble.mjs').read_text();core=(P/'collector-core.mjs').read_text()
ck('actual authority required',all(x in run for x in ["review.decision,'accepted'","review.author_run!==review.reviewer_run","review.unresolved_blockers,[]","freeze.fresh_qualification_receipt"]))
ck('output distinct physical parent and absent',"fs.realpathSync(dirname(out)),dirname(out)"in run and "!fs.existsSync(out)"in run)
ck('assembly passed backends and compare',"['native','wasm','compare']"in assembly and "report.status,'passed'"in assembly)
ck('assembly exact imported same requests and old four metadata',"parseLaboratoryDocument(raw.toString(),catalogue),row.specification"in assembly and "assert.deepEqual(a,b"in assembly)
ck('finite every result number',"finite(result)"in core and "Number.isFinite(value)"in core)
ck('history diagnostic only',"diagnostic-only-no-budget"in core)
print(json.dumps({'status':'PASS','count':len(checks),'checks':checks,'actual_material_or_generated_module_calls':0},indent=2))
