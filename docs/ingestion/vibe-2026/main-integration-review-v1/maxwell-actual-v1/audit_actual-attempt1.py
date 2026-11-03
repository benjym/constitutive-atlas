from pathlib import Path
import json,hashlib,sys,importlib.util,datetime,tempfile
R=Path(__file__).resolve().parents[5];O=Path(__file__).parent;sys.path.insert(0,str(R));P=R/'docs/ingestion/vibe-2026/maxwell-refresh-v1';E=P/'execution-v1'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[];inputs={}
def check(ok,label):
 assert ok,label
 checks.append(label)
def pin(p):inputs[str(p.relative_to(R))]=h(p)
spec=importlib.util.spec_from_file_location('independent_maxwell_source',R/'tools/qualify_maxwell_refresh.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
plan,m,tx=c.guard(P/'plan.json');check(h(P/'plan.json')=='23cdeeb999b2e0dffb8736348de0024e5522cbd9ae94e60e9528316291815e9b','accepted exact prospective plan');pin(P/'plan.json');pin(R/'tools/qualify_maxwell_refresh.py')
result=read(P/'results.json');check(result['status']=='passed-pending-independent-build-review','actual pending identity');check(result['gates']=={g:True for g in c.GATES},'five original gates exact');check(result['implementation_run']==plan['implementation_run'],'actual distinct implementation identity')
for f in plan['files']:pin(R/f['path'])
for path in plan['source_manifest']['files']:pin(R/path)
previous=None
for backend in ['native','wasm']:
 for i,phase in enumerate(['configure','build']):
  p=E/f'{backend}-{phase}.json';r=read(p);pin(p);pin(p.with_suffix('.log'));check(r['returncode']==0 and r['command']==plan['serial_build_commands'][backend][i],backend+phase+' frozen exact successful terminal');check(h(p.with_suffix('.log'))==r['log_sha256'],backend+phase+' exact raw log')
  started=datetime.datetime.fromisoformat(r['started_utc']);check(previous is None or started>=previous,backend+phase+' serial nonoverlap');previous=started+datetime.timedelta(seconds=r['elapsed_seconds'])
  if phase=='build':
   text=p.with_suffix('.log').read_text();check('Building CXX object' in text and '[100%] Built target atlas_maxwell_solver' in text,backend+' genuine compile and link observed')
artifactdir=E/'build-artifacts';manifest=read(artifactdir/'manifest.json');pin(artifactdir/'manifest.json')
for path,expected in manifest['files'].items():check(h(artifactdir/path)==expected==h(R/'.local/maxwell-refresh-v1'/path),'durable and original actual artifact '+path);pin(artifactdir/path)
statistics={};cases=read(R/c.BASE/'reference-cases.json')['cases']
for backend in ['native','wasm']:
 folder=E/backend;summary=read(folder/'summary.json');check(h(folder/'summary.json')==result[backend+'_summary']['sha256'],'result exact '+backend+' summary');check(summary['bindings']['plan_sha256']==h(P/'plan.json'),'summary exact plan '+backend);c.check_saved(folder,summary)
 for path in folder.iterdir():
  if path.is_file():pin(path)
 check(summary['bindings']['artifacts']==c.artifacts(R/plan['builds'][backend],backend),backend+' live actual artifact exact')
 rows=read(folder/'reference-raw.json');errs=m.assess_rows(cases,rows);tc=tx.cases_for(folder/'reference-raw.json');check(tc==read(folder/'transaction-cases.json')['cases'],backend+' exact original recovery and endpoint restart requests');tr=read(folder/'transaction-raw.json');te=tx.assess(tc,tr);check(len(rows)==24 and len(tc)==len(tr)==14,backend+' complete24+14 twice')
 for q,row in zip(cases+tc,rows+tr):check(len(row['calls'])==2,backend+' two calls '+q['id'])
 # Complete append-only command pair sequence; no exceptions or missing terminals.
 events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()];check(events[0]['kind']=='bindings-before-material',backend+' pre-material binding');pairs=events[1:];check(len(pairs)%2==0,backend+' even terminal pairs')
 for a,b in zip(pairs[::2],pairs[1::2]):check(a['kind']=='before-command' and b['kind']=='after-command' and a['label']==b['label'] and b['returncode'] in [0,1],backend+' durable genuine command pair '+a['label'])
 if backend=='native':
  for q,row in zip(cases+tc,rows+tr):
   for repeat,raw in enumerate(row['calls']):
    a=next(x for x in pairs if x['kind']=='before-command' and x['label']==q['id']+'-'+str(repeat));b=next(x for x in pairs if x['kind']=='after-command' and x['label']==q['id']+'-'+str(repeat));check(a['argv'][1:]==q['argv'] and all(b[k]==raw[k] for k in ['stdout','stderr','returncode']),'native original argv and exact journal raw '+q['id']+str(repeat))
  for name,cid in c.PRESETS.items():m.assess(next(q for q in cases if q['id']==cid),read(folder/f'preset-{name}.json'))
  check(read(folder/'creep-replay.json')==read(folder/'preset-creep.json'),'native actual creep CLI replay exact');refuse=next(x for x in pairs if x['kind']=='after-command' and x['label']=='untimed-refusal');check(refuse['returncode']==1 and json.loads(refuse['stdout'])['ok'] is False,'native actual untimed refusal')
 else:
  check(summary['bindings']['native_peer_summary_sha256']==h(E/'native/summary.json'),'Wasm exact successful native peer')
  presets=read(folder/'presets.json');check([p['name'] for p in presets]==list(c.PRESETS),'all four public presets')
  for row in presets:
   source=read(R/'examples/maxwell'/f"{row['name']}.json");check(row['controls']=={**source,'solver':row['controls']['solver']} and all(row['controls']['solver'].get(k)==v for k,v in source['solver'].items()),row['name']+' original complete source controls');check(row['result']==row['replayed_result'],row['name']+' public complete export import replay');m.assess(next(q for q in cases if q['id']==c.PRESETS[row['name']]),row['result'])
 statistics[backend]={'reference_cases':len(rows),'transaction_cases':len(tc),'original_errors_Pa':errs,'transaction_errors_Pa':te}
 entries=read(artifactdir/backend/'compile_commands.json');api=[x for x in entries if x['file'].endswith('main.cpp')];check(bool(api),backend+' actual solver translation unit');check(all('-fno-fast-math' in x['command'] and '-ffp-contract=off' in x['command'] for x in api),backend+' strict scalar float flags')
from atlas.compiler import generate
with tempfile.TemporaryDirectory(prefix='source-generation-',dir=O) as t:
 generate(t,[R/c.DEFINITION])
 for name in ['models.hpp','models.json']:check(h(Path(t)/name)==h(artifactdir/'native/generated'/name)==h(artifactdir/'wasm/generated'/name),'fresh compiler exact native/Wasm generated '+name)
parity=c.assess_parity(E/'native',E/'wasm');check(parity==result['parity'] and parity['numeric_comparisons']==5962,'original full parity reassessment')
build=R/plan['builds']['wasm'];binding={'model_sha256':h(R/c.DEFINITION),'catalogue_file_sha256':h(build/'generated/models.json'),'module_sha256':h(build/'maxwell.js'),'wasm_sha256':h(build/'maxwell.wasm'),'source_manifest_sha256':plan['source_manifest']['sha256'],'reference_policy_sha256':h(R/c.BASE/'reference-cases.json')};check(binding==result['binding'],'all six actual package bindings exact');pin(P/'results.json')
report={'checks':checks,'count':len(checks),'statistics':statistics,'parity':parity,'inputs':inputs,'compiled_calls':0,'cleanup':'One source-only generation temporary directory automatically removed; no processes/builds/material/modules executed.'};(O/'actual-results.json').write_text(json.dumps(report,indent=2)+'\n')
review={'status':'accepted','reviewer_run':'/root/vibe_oracle_review:maxwell-current-build-v1','binding':binding,'gates':result['gates'],'results_sha256':h(P/'results.json'),'blocking_findings':[],'evidence':{'path':str((O/'actual-results.json').relative_to(R)),'sha256':h(O/'actual-results.json')},'scope':plan['limits'],'independence':'Separate agent that authored neither current collector nor original scientific runtime/assessors; reviewed fresh coordinator saved build terminals and raw results without executing compiled artifacts.'};(O/'build-review.json').write_text(json.dumps(review,indent=2)+'\n')
manifest={'files':[{'path':str(p.relative_to(R)),'sha256':h(p)} for p in O.iterdir() if p.is_file()]};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('checks',len(checks),'parity',parity);print('review',h(O/'build-review.json'));print('manifest',h(O/'manifest.json'))
