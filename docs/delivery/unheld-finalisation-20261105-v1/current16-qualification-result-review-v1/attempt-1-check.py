from pathlib import Path
import json,hashlib,importlib.util,sys,tempfile,subprocess,types
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;P=R.parent/'current16-qualification-plan-v1';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):assert v,n;checks.append(n)
def verify(pin):
 p=Path(pin['path']);ck('pin '+str(p),sha(p)==pin['sha256'] and ('bytes'not in pin or p.stat().st_size==pin['bytes']))
summary=R.parent/'qualification-observations-v1.json';ck('exact summary',sha(summary)=='0e27d8da45dbfe287564b2ce9c67853933b1567088e980dc68b41e8444227da4');s=json.loads(summary.read_text())
for pin in [s['source_freeze'],s['execution_freeze'],s['build_receipt'],*s['backend_receipts'],s['pair'],*s['artifacts'].values()]:verify(pin)
collector=P.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5/collector.py'
ck('exact unchanged collector',sha(collector)=='d5829f3f43ec132f429a0c6fcb07316e4152b4bd68ccb105565d0159f1d7df6e')
spec=importlib.util.spec_from_file_location('original_saved_collector',collector);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=tempfile.TemporaryDirectory
class OwnedTemporary(original):
 def __init__(self,*a,**kw):kw['dir']=R;super().__init__(*a,**kw)
tempfile.TemporaryDirectory=OwnedTemporary
originalrun=subprocess.run;commands=[]
def saved_only(argv,**kw):
 assert len(argv)==6 and argv[1].endswith('/run_study.py') and argv[2]=='--replay' and argv[4]=='--output',argv
 assert Path(argv[3]).is_relative_to(P) and Path(argv[5]).is_relative_to(R)
 commands.append(argv)
 return originalrun(argv,**kw)
subprocess.run=saved_only
try:m.assess_pair(types.SimpleNamespace(native=P/'native-v1',wasm=P/'wasm-v1',output=R/'pair-replay.json'))
finally:subprocess.run=originalrun;tempfile.TemporaryDirectory=original
ck('saved pair exactly replayed',json.loads((R/'pair-replay.json').read_text())==json.loads((P/'pair-v1.json').read_text()) and len(commands)==2)
(R/'pure-replay-argv.json').write_text(json.dumps(commands,indent=2)+'\n')
build=json.loads((P/'actual-build-v1/receipt.json').read_text());ck('8 successful serial configure/build/version children',len(build['commands'])==8 and all(x['returncode']==0 and x['source_post_unchanged']is True for x in build['commands']))
ck('four compiler metadata and versions',len(build['compiler_metadata'])==4 and len(build['all_resolved_compilers'])==4 and len(build['compiler_version_logs'])==4)
for pin in [*build['compiler_metadata'].values(),*build['all_resolved_compilers'].values(),*build['generated_files']]:verify(pin)
pre=json.loads((P/'source-freeze-v1.json').read_text());ck('796 source inventory',len(pre['source_inventory'])==796)
for backend in ['native','wasm']:
 described=json.loads((P/backend.__add__('-v1')/'describe.json').read_text());ck('exact16 '+backend,described['sha256']==s['catalogue_hash'] and len(described['models'])==16 and [x['id']for x in described['models']]==s['models'])
 generated=next(x for x in build['generated_files'] if backend+'/generated/models.json'in x['path']);ck('generated describe exact '+backend,json.loads(Path(generated['path']).read_text())==described)
for phase in ['build','freeze','native','wasm','pair']:
 folder=P/('outer-'+phase+'-v1');receipt=json.loads((folder/'receipt.json').read_text());ck('outer passed/reaped '+phase,receipt['status']=='passed' and receipt['returncode']==0 and receipt['reaped_returncode']==0 and receipt['mandatory_reap']is True and receipt['cleanup_errors']==[])
 for pin in [receipt['executable'],receipt['stdout'],receipt['stderr']]:verify(pin)
 ck('outer1800 bounded '+phase,receipt['elapsed_seconds']<1800)
ck('no owned temporary contexts remain',not any(p.is_dir()for p in R.iterdir()))
print(json.dumps({'status':'PASS','count':len(checks),'checks':checks,'saved_replay_subprocesses':2,'actual_compiled_module_material_calls':0,'scope':'Original unchanged full saved pair assessor replay, source/build/artifact pins and16 inventory; no new scientific scope'},indent=2))
