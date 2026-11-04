"""Verify exact saved actual evidence and source only. No production engine calls."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys,tempfile
O=Path(__file__).resolve().parent;P=O.parent;B=P.parent;R=P.parents[3];E=B/'baseline-qualification-execution-v5';A=B/'baseline-qualification-plan-v5'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
checks=[]
def ck(n,b):assert b,n;checks.append(n)
expected={'execution-freeze-v1.json':'3af647ab632b40081a06f4e61b92cdccaacf01c216d32603ddc5f488ca380d7d','native-v1/receipt.json':'c8552c064c90e3c98d3b75d7c1491245b0fb92d49fb0d1a85d79b0142ddf5f74','wasm-v1/receipt.json':'7c2a0f86294a95bb65a1eb199d240a973678ed7589d2593f232bb0077902336a','pair-v1.json':'db96c97ad115b155d62c74376eb39e8386109ee3fad746c8d8a6c6b18b76b414'}
for n,s in expected.items():ck('actual pin '+n,h(E/n)==s)
ck('accepted exact collector',h(A/'collector.py')=='d5829f3f43ec132f429a0c6fcb07316e4152b4bd68ccb105565d0159f1d7df6e')
spec=importlib.util.spec_from_file_location('review_saved_pair',A/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# This collector action is saved-source replay only: its only child is the unchanged DP Python --replay assessor.
with tempfile.TemporaryDirectory(prefix='baseline-e5-pair-') as temp:
 q=Path(temp)/'pair.json';m.assess_pair(argparse.Namespace(native=E/'native-v1',wasm=E/'wasm-v1',output=q))
 ck('full saved oracle/interface replay exact parent pair',read(q)==read(E/'pair-v1.json'))
 ck('retained reviewer replay exact',read(q)==read(O/'pair-replay.json'))
f=read(E/'execution-freeze-v1.json');m.validate_execution_freeze(f);ck('real complete execution provenance validator',True)
commit=read(E/'local-source-commit-v1.json');ck('genuine isolated commit',commit['commit']=='8c29746893dfb2f63386c26544aef4c356c9ae19' and commit['base']=='28d4af2b1d4d6b9c1a58038a8ef9a99ec3279d8c' and len(commit['paths'])==10 and not commit['remote_push'])
repo=Path(commit['repo']);actual=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip();ck('actual isolated HEAD matches receipt',actual==commit['commit'])
changed=subprocess.run(['git','diff-tree','--no-commit-id','--name-only','-r',commit['commit']],cwd=repo,capture_output=True,text=True,check=True).stdout.splitlines();ck('exact ten committed paths',sorted(changed)==sorted(commit['paths']))
for mid,pin in f['candidates'].items():
 ck('exact candidate proposal '+mid,h(Path(pin['path']))==h(B/'baseline-migration/proposals'/f'{mid}.json')==f['policy']['candidate_sha256'][mid])
 blob=subprocess.run(['git','show',commit['commit']+':models/'+mid+'.json'],cwd=repo,capture_output=True,check=True).stdout
 ck('committed exact candidate '+mid,hashlib.sha256(blob).hexdigest()==pin['sha256'])
metadata=B/'baseline-build-metadata-recovery-review-v1/actual-completion-v1/decision.json';d=read(metadata)
ck('genuine independent build decision',h(metadata)=='b2945ee52dbcf50567ae9ac4e94225babc43e5338ead855499cc3fa2376e79d2')
ck('actual build decision accepted scope',d['decision']=='accepted-bounded-actual-build-metadata-provenance' and d['remaining_blocking_findings']==[] and d['actual_children']==8 and d['new_version_only_children']==2 and d['original_parent_exit_code']==1)
for key in ['completed_receipt','original_failed_receipt','checks','prospective','accepted_plan_decision']:m.verify(d[key]);ck('metadata binding '+key,True)
ck('completed actual build bound by E4 freeze',f['build_receipt']==d['completed_receipt'])
for row in read(P/'source-pins.json'):ck('private original still exact '+row['path'],h(R/row['path'])==row['sha256'])
ck('source phase manifest still exact',h(P/'source-phase-manifest.json')=='f9b677e89163c990d8deb9251bec2767ebce94f6bde5238496fd8660386f0ec3')
for r in read(P/'source-phase-manifest.json')['files']:ck('immutable source phase '+r['path'],h(P/r['path'])==r['sha256'])
summaries={}
for backend in ['native','wasm']:
 p=E/(backend+'-v1');receipt=read(p/'receipt.json');ck(backend+'1041saved requests',receipt['raw_call_count']==1041)
 counts={};metrics={}
 for gate in ['elasticity','vw96','igs97','mcc']:
  report=read(p/(gate+'.json'));counts[gate]=len(report['cases']);ck(backend+' every '+gate,report['passed']and all(x['passed']for x in report['cases']))
  metrics[gate]={'tolerances':report['tolerances'],'maximum_saved_tolerance_ratio':max((x.get('max_tolerance_ratio')or 0)for x in report['cases'])}
 report=read(p/'dp83-original-assessor/report.json');counts['dp83']=report['count'];ck(backend+'all83DP',report['passed']and all(x['passed']for x in report['cases']))
 ck(backend+'complete701',counts=={'elasticity':29,'vw96':229,'igs97':303,'mcc':57,'dp83':83}and sum(counts.values())==701)
 interface=read(p/'interface-cases.json');ck(backend+'42interface rows',len(interface)==42 and all(x['passed']for x in interface))
 raw=read(p/'raw-calls.json');ck(backend+'87interface requests',sum(x['stage']=='explicit-interface'for x in raw)==87)
 ck(backend+'transport closed nofailures',receipt['owned_transport_closed']and receipt['post_bindings_unchanged']and receipt['failures']==[])
 summaries[backend]={'counts':counts,'raw_requests':1041,'interface_rows':42,'interface_calls':87,'metrics':metrics}
result={'identity':'baseline-five-v03-independent-saved-evidence-review-v1','status':'PASS_EXACT_SAVED_EVIDENCE','check_count':len(checks),'checks':checks,'summaries':summaries,'source_commit':commit['commit'],'build_metadata_decision':m.pin(metadata),'full_saved_pair_replay':True,'new_tolerance_or_old_approval_transfer':False,'actual_model_module_calls_by_reviewer':0,'source_only_children':'unchanged DP Python --replay and git read-only identity checks only','temporary_replay_removed':True}
m.write(O/'saved-checks.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['checks','summaries']}))
