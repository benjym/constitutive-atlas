"""Independent actual saved Wasm/native evidence review; no artifact calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import contextlib,gzip,hashlib,io,json,runpy,subprocess,tarfile,gc
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parent;ROOT=P.parents[3]
OUTPUT=Path(sys.argv[1]) if len(sys.argv)>1 else D/'checks.json'
assert not OUTPUT.exists(),'Preserve reviewer observations; provide a fresh output path'
B=P/'qualification-wasm-v5';W=Path('/private/tmp/atlas-control-partition-v1/md-wasm-v5');O=W.parent/'ordinary-wasm-v7';N=W.parent/'md-native-v5'
SCRATCH=W.parent/'independent-md-wasm-v5-checks-v1';SCRATCH.mkdir(exist_ok=True)
load=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();h=lambda p:sha(p.read_bytes())
checks=[]
def check(name,value):
    checks.append({'name':name,'passed':bool(value)});assert value,name
def closure(folder,expected=None):
    if expected:check(str(folder.name)+'/manifest identity',h(folder/'manifest.json')==expected)
    manifest=load(folder/'manifest.json')
    if 'identity' in manifest:
        for n,v in manifest.get('inputs',{}).items():check(folder.name+'/input/'+n,h(Path(n))==v)
        manifest=manifest['review_files']
    for n,v in manifest.items():check(folder.name+'/'+n,h(folder/n)==v)
closure(B,'f292df48d6e5ddbd2fd381570ab6afddbd9c69f5a1f3890f5af0fc7e4e364e59')
freeze=load(B/'freeze.json')
check('qualification preobservation inputs exact',all(h(ROOT/n)==v for n,v in freeze['inputs'].items()))
for folder in ['build-wasm-v2','raw-link-v7','resolution-study-v4','ordinary-regression-v7','native-v5-review','qualification-native-v5']:closure(P/folder)
source=load(ROOT/'docs/investigations/control-partition-derivative-v1/implementation-v1/source-freeze.json')
check('all582 runtime sources exact',len(source['source_files'])==582 and all(h(Path(source['source_directory'])/n)==v for n,v in source['source_files'].items()))
br=load(P/'build-wasm-v2/build-receipt.json');bf=load(P/'build-wasm-v2/freeze.json')
check('build allpreobservation inputs exact',all(h(ROOT/n)==v for n,v in bf['inputs'].items()))
check('JS payload and generated catalogue exact',all(h(Path(br[n]))==br[k] for n,k in [('artifact_path','artifact_sha256'),('wasm_path','wasm_sha256'),('catalogue_path','generated_catalogue_sha256')]))
check('build sourcefreeze exact',br['source_freeze_sha256']==freeze['source_freeze_sha256']==h(ROOT/'docs/investigations/control-partition-derivative-v1/implementation-v1/source-freeze.json'))
check('build freeze/log identity',h(P/'build-wasm-v2/freeze.json')==br['freeze_sha256'] and h(Path(br['build_log_path']))==br['build_log_sha256'])
check('serial explicit Release wasm build',br['build_type']=='Release' and br['target']=='atlas_solver' and br['parallel']==1 and br['EMCC_CORES']=='1' and bf['build_command'][-4:]==['--target','atlas_solver','--parallel','1'])
for n in ['configure','build']:
    check(n+' process success',load(P/'build-wasm-v2'/(n+'-process.json'))['returncode']==0)
check('native reviewer accepted exactmanifest',h(P/'native-v5-review/manifest.json')=='25cd86c9b3982c5babc1441f6429b5798817c90f695ffa05e5e24f278fd4697c')
check('candidate unchanged',h(P/'manzari-dafalias-1997-constant-m-be-v1.json')=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064')
retention=load(B/'retention-receipt.json');archive=B/retention['archive']
check('durable archive SHA and size',h(archive)==retention['sha256'] and archive.stat().st_size==36875386)
with tarfile.open(archive,'r:gz')as t:
    members=t.getmembers();files={m.name:m for m in members}
    check('exact63 regular unique archive members',len(files)==len(members)==63 and all(m.isfile() for m in members) and set(files)=={r['path']for r in retention['files']})
    for row in retention['files']:
        raw=t.extractfile(files[row['path']]).read()
        check('archive and working/'+row['path'],len(raw)==row['size'] and sha(raw)==row['sha256'] and (W.parent/row['path']).read_bytes()==raw)
pr=load(B/'parity-retention-receipt.json');gz=B/pr['compressed_path']
check('parity compressed hash',h(gz)==pr['compressed_sha256'])
digest=hashlib.sha256();size=0
with gzip.open(gz,'rb')as f:
    while block:=f.read(1048576):digest.update(block);size+=len(block)
check('parity lossless original bytes',digest.hexdigest()==pr['uncompressed_sha256']==h(Path(pr['private_original_path'])) and size==pr['uncompressed_size']==202813847)
for prefix in ['collect','ordinary']:
    check(prefix+' parent success',load(B/(prefix+'-process.json'))['returncode']==0)
    command=load(B/(prefix+'-start.json'))['command']
    check(prefix+' full v7 collection',any(str(v).endswith('/raw-link-v7/run_bound.py')for v in command) and '--case'not in command and '--wasm-engine'in command)
for folder,calls in [(W,45143),(O,16)]:
    transport=load(folder/'transport.json');binding=load(folder/'runtime-binding.json')
    check(folder.name+' worker lifecycle',transport['closed']is True and transport['call_count']==calls and transport['worker']['exit_code']==0 and transport['worker']['ready_wire']=='{"ready":true}\n' and (folder/'worker-stderr.txt').read_bytes()==b'')
    check(folder.name+' exact receipt/report/runtime linkage',binding['coordinator_build_receipt_sha256']==h(P/'build-wasm-v2/build-receipt.json') and binding['delegate_returncode']==0 and binding['report_sha256']==h(folder/'report.json') and binding['artifact_sha256']==br['artifact_sha256'] and binding['wasm_sha256']==br['wasm_sha256'] and binding['source_freeze_sha256']==br['source_freeze_sha256'])
def forbidden(*a,**k):raise AssertionError('No live processes permitted during saved checkers')
checker_receipts=[]
for label,script,args,saved,output in [
 ('MD raw',P/'raw-link-v7/check_raw.py',[str(W),'--study','md'],B/'raw-checks.json',SCRATCH/'raw.json'),
 ('ordinary raw',P/'raw-link-v7/check_raw.py',[str(O),'--study','ordinary'],B/'ordinary-raw-checks.json',SCRATCH/'ordinary-raw.json'),
 ('source',P/'resolution-study-v4/check_reports.py',[str(W/'report.json')],B/'source-checks.json',SCRATCH/'source.json'),
 ('paired',P/'resolution-study-v4/check_parity.py',[str(N/'report.json'),str(W/'report.json')],Path(pr['private_original_path']),SCRATCH/'parity.json')]:
    if not output.exists():
        with patch.object(sys,'argv',[str(script),*args,'--output',str(output)]),patch.object(sys,'path',[str(script.parent),*sys.path]),patch.object(subprocess,'run',forbidden),patch.object(subprocess,'Popen',forbidden),contextlib.redirect_stdout(io.StringIO()):
            try:runpy.run_path(str(script),run_name='__main__')
            except SystemExit as exc:check(label+' checker exit zero',exc.code==0)
    check(label+' saved check exact bytes',h(output)==h(saved))
    checker_receipts.append({'label':label,'script':str(script.relative_to(ROOT)),'script_sha256':h(script),'output':str(output),'output_sha256':h(output),'output_size':output.stat().st_size,'saved_sha256':h(saved)})
    gc.collect()
report=load(W/'report.json');ordinary=load(O/'report.json');plan=load(P/'resolution-study-v4/requests.json');policy=load(P/'ordinary-regression-v7/policy.json')
check('35cases24special45143 calls',list(report['cases'])==[c['id']for c in plan['cases']] and len(report['cases'])==35 and len(report['special'])==24 and report['call_count']==45143)
check('all35 operational cases passed',all(c['ok']is True for c in report['cases'].values()))
check('ordinary all16 expected outcomes',ordinary['passed']is True and len(ordinary['cases'])==16 and [c['model']for c in ordinary['cases']]==[c['model']for c in policy['cases']] and all(c['passed']is True for c in ordinary['cases']))
check('ordinary declared15 success oneGISrejection',sum(c['response']['ok']is True for c in ordinary['cases'])==15 and [c['model']for c in ordinary['cases']if c['response']['ok']is False]==['research-hp-extracted-asbs-gis-2024-v03'])
check('96943 source gates zero failure',load(SCRATCH/'source.json')['checks']==96943 and all(c['passed'] for c in load(SCRATCH/'source.json')['results']))
count=0;failed=0
with (SCRATCH/'parity.json').open()as f:
    for line in f:
        count+=line.startswith('      "name": ')
        failed+='"passed": false' in line
check('2204769 paired gates zero failure',count==2204769 and failed==0)
check('parent manifest unchanged at end',h(B/'manifest.json')=='f292df48d6e5ddbd2fd381570ab6afddbd9c69f5a1f3890f5af0fc7e4e364e59')
OUTPUT.write_text(json.dumps({'decision':'accepted bounded Wasm resolution-study-v4 and paired native/Wasm plus ordinary-v7 only','compiled_calls':0,'builds':0,'checks':checks,'count':len(checks),'saved_checker_reproduction':checker_receipts,'source_checks':96943,'paired_checks':count,'source_failures':0,'paired_failures':failed},indent=2)+'\n')
print(json.dumps({'status':'passed','independent_checks':len(checks),'source_checks':96943,'paired_checks':count,'compiled_calls':0}))
