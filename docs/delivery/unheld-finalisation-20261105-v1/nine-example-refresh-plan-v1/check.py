from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3];BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source');OLD=ROOT/'docs/delivery/unheld-finalisation-20261102-v1/baseline-five-nine-named-observations-v2'
def sha(b):return hashlib.sha256(b).hexdigest()
checks=[]
def ok(name,value):assert value,name;checks.append(name)
rows=json.loads((P/'requests.json').read_text());ok('nine unique requests',len(rows)==9 and len({r['id'] for r in rows})==9)
ok('unchanged original policy', (P/'policy.json').read_bytes()==(OLD/'policy.json').read_bytes())
original=json.loads((P/'original-four-index.json').read_text());ok('current four index exact',(P/'original-four-index.json').read_bytes()==(BASE/'catalogue/laboratory-examples.json').read_bytes())
for i,row in enumerate(rows):
 old=(P/'references'/f"{row['id']}.json").read_bytes();doc=json.loads(old)
 ok('reference '+row['id'],sha(old)==row['old_document']['sha256'] and Path(row['old_document']['path']).read_bytes()==old)
 ok('exact request '+row['id'],row['specification']==doc['specification'])
 ok('distinct output '+row['id'],row['new_document_path']!=row['entry']['document_path'])
 if i<4:ok('exact current entry '+row['id'],row['entry']==original['examples'][i])
for f in (P/'context/web').glob('*.mjs'):ok('exact current module '+f.name,f.read_bytes()==(BASE/'web'/f.name).read_bytes())
s=(P/'collector-core.mjs').read_text();old=(OLD/'collector-core.mjs').read_text()
for name,nextname in [('withoutElapsed','parity'),('parity','envelopeNegatives'),('envelopeNegatives','journalEngine'),('journalEngine','collect')]:
 start='export function '+name;end='export function '+nextname
 ok('unchanged original '+name,s[s.index(start):s.index(end)]==old[old.index(start):old.index(end)])
run=(P/'collect.mjs').read_text();oldrun=(OLD/'collect.mjs').read_text()
start="   transport={ccall";end="\n  collect(rows"
ok('unchanged native transport',run[run.index(start):run.index(end)]==oldrun[oldrun.index(start):oldrun.index(end)])
ok('historical comparison nonblocking',"entry.historical_comparison_gate='diagnostic-only-no-budget'" in s and 'historicalDifferences(result,old.result)' in s)
ok('source/artifact guards before output',run.index('};checkPins();')<run.index('fs.mkdirSync(out)'))
ok('source/artifact guards in finally','finally{let post=null;try{checkPins();}' in run)
ok('post failure marks report failed',"status:'failed',post_input_error:post" in run)
ok('real independent authority required',"review.proposal_manifest_sha256,freeze.collector_manifest.sha256" in run and 'review.author_run!==review.reviewer_run' in run)
ok('no source install in assembler',"join(out,p)" in (P/'assemble.mjs').read_text())
(P/'source-checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'checks_passed':checks,'scope':'source metadata only; no actual engines/modules/processes'},indent=2)+'\n');print(len(checks))
