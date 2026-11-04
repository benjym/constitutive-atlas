from pathlib import Path
import hashlib,json,collections
Q=Path(__file__).resolve().parent;N=Q.parents[1];P=N/'current17-runtime-actual-v1';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
def verify(r):p=Path(r['path']);ok(H(p)==r['sha256']and p.stat().st_size==r.get('bytes',r.get('size_bytes')),'exact live retained pin '+str(p))
ok(H(P/'manifest.json')=='1f6257f77404c77e8d9aa2fdfd94ba47a038b6a8d54d5c3c422d02679b9803ac','exact frozen42member actualpacket manifest')
m=json.loads((P/'manifest.json').read_text());ok(len(m['files'])==42,'all42 actual members')
for r in m['files']:
 p=P/r['path'];ok(p.is_file()and not p.is_symlink()and H(p)==r['sha256']and p.stat().st_size==r['bytes'],'exact packet member '+r['path'])
plan=json.loads((P/'plan.json').read_text());f=json.loads((P/'execution-freeze.json').read_text());ok(H(P/'execution-freeze.json')=='77c2bba425d7b03200891001c6adc816d478a09f57b209e635ce1cda99482ef3','exact prospective reuse execution freeze')
for r in plan['pins']:verify(r)
ok(H(Path(plan['observer']))=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e','original observer7328 unchanged')
ok(f['handoff_review']['sha256']=='f467e10a5436eb41d1e7af821e9b1efa7671c54a90c03688e483697d897551f7'and f['handoff']['sha256']=='78c7c2b4aeef1abd4cf6894ff66d8a70b1c4179092298c198dc9f6f3d3f11ae9','exact accepted genuine handoff/review')
ok(f['revision']=='64002531f0af5c06ad0402d0d80548102f8e6a38'and f['identity']=='baseline-five-current17-reused-execution-freeze-v1','distinct exact current17 source/artifact freeze')
last=None
for phase in ('freeze','native','wasm','pair'):
 r=json.loads((P/('outer-'+phase)/'receipt.json').read_text());ok(r['argv']==plan['commands'][phase]and r['cwd']==plan['cwd'],'exact observed launch argv/cwd '+phase)
 ok(r['returncode']==r['reaped_returncode']==0 and r['status']=='passed'and r['mandatory_reap']is True and r['cleanup_errors']==[]and r['signals_during_finalization']==[],'genuine successful observer exit/mandatory clean reap '+phase)
 for key in ('stdout','stderr','executable'):verify(r[key])
 if last is not None:ok(r['started_epoch']>=last,'genuine serial nonoverlapping phases '+phase)
 last=r['ended_epoch']
# Complete actual backend memberships, successful original oracle cases and raw-call provenance.
correction=json.loads((N/'current17-runtime-actual-count-correction-v1.json').read_text());ok(correction['original_summary_sha256']==H(P/'actual-summary.json')and correction['frozen_packet_unchanged']is True,'summary3-key count bug corrected additively without rewriting packet')
expectedstages={'describe':1,'elasticity':30,'vw96':232,'igs97':312,'mcc':296,'dp83':83,'explicit-interface':87}
for backend in ('native','wasm'):
 d=P/backend;r=json.loads((d/'receipt.json').read_text());ok(r['passed']is True and r['failures']==[]and r['started']is True,'actual original gates passed '+backend)
 ok(r['owned_transport_closed']is True and r['post_bindings_unchanged']is True and r['historical_reports_modified']is False,'actual transport closed/source-artifactpostchecks/no rewritten references '+backend)
 ok(r['embedded_catalogue_hash']=='4e31188499b5d19e52439451a709775f00e08a1f4d94570e40f43d825cd0e0a1','actual runtime catalogue4e31 '+backend)
 verify(r['freeze']);rows=json.loads((d/'raw-calls.json').read_text());ok(len(rows)==r['raw_call_count']==1041,'complete1041 rawcalls '+backend)
 ok([x['sequence']for x in rows]==list(range(1041)),'contiguous original rawcall sequence '+backend)
 ok(dict(collections.Counter(x['stage']for x in rows))==expectedstages,'all original stage request counts '+backend)
 order=[]
 for row in rows:
  if not order or order[-1]!=row['stage']:order.append(row['stage'])
  ok('post_artifact_binding_error'not in row,'no postcall artifact pin drift '+backend+' '+str(row['sequence']))
 ok(order==list(expectedstages),'exact unsplit original stage order '+backend)
 total=0
 for name,count in [('elasticity',29),('vw96',229),('igs97',303),('mcc',57)]:
  report=json.loads((d/(name+'.json')).read_text());ok(report['passed']is True and len(report['cases'])==count and all(x['passed']is True for x in report['cases']),'original exact independent '+name+'cases '+backend);total+=count
 dp=json.loads((d/'dp83-original-assessor/report.json').read_text());rawdp=json.loads((d/'dp83-raw.json').read_text());ok(dp['passed']is True and dp['count']==len(dp['cases'])==len(rawdp['calls'])==83,'all83 original DP cases actual '+backend);total+=83
 ok(total==701 and len(json.loads((d/'interface-cases.json').read_text()))==42,'all701 physical +42 interface rows '+backend)
 c=correction['backends'][backend];ok(c=={'dp_cases':83,'independent_reference_cases':701,'interface_rows':42,'interface_calls':87,'total_raw_calls':1041,'raw_dp_sha256':H(d/'dp83-raw.json')},'corrected summary bound to exact genuine DPraw '+backend)
 describe=json.loads((d/'describe.json').read_text());ok(H(d/'describe.json')=='19be5a4568830e2ac2d5e930ceb2f778a98a37c4bf31f700e6bc7ee3d41ccdac'and len(describe['models'])==17,'actual complete17 catalogue exact shipped/generated '+backend)
 for out in r['outputs'].values()if isinstance(r['outputs'],dict)else r['outputs']:verify(out)
for name in ('native-preflight.json','wasm-preflight.json'):
 x=json.loads((P/name).read_text());pathkey,activekey=('private_process_inventory','relevant_active_processes')if name=='native-preflight.json'else('private_inventory','active_material_or_build_processes');ok(H(Path(x[pathkey]))==x['sha256']and x[activekey]==[],'exact saved private process preflight '+name)
ok(json.loads((Q/'pair-replay.json').read_text())==json.loads((P/'pair.json').read_text()),'independent unchanged saved-only pair replay exact same accepted report')
(Q/'checks.json').write_text(json.dumps({'status':'PASS_SAVED_RUNTIME_RESULTS','checks':len(labels),'labels':labels,'reference_cases_per_backend':701,'interfaces':42,'interface_calls':87,'rawcalls_per_backend':1041,'original_summary_count_bug_retained':True,'reviewer_engine_calls':0},indent=2)+'\n');print(json.dumps({'status':'PASS_SAVED_RUNTIME_RESULTS','checks':len(labels)}))
