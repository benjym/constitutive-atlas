"""Independent SLS path-only source review; no actual recovered assets read."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,runpy,sys,tempfile,copy
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parents[1]/'standard-web-delivery-plan-v2'
EXPECTED='56ee1da7d8d1c6113a8dddedff6a85169ca9e8bbde20065d21526ca7b3dedf89'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):assert v,n;checks.append(n)
ok(sha(P/'manifest.json')==EXPECTED,'exact frozen v2 manifest')
manifest=json.loads((P/'manifest.json').read_text())
for row in manifest['files']:
 q=P/row['path'];ok(not q.is_symlink()and sha(q)==row['sha256']and q.stat().st_size==row['size_bytes'],'frozen member '+row['path'])
for row in json.loads((P/'authority-pins.json').read_text()):
 q=Path(row['path']);ok(sha(q)==row['sha256']and q.stat().st_size==row['bytes'],'exact saved authority '+str(q))
write=Path.write_text;temporary=tempfile.TemporaryDirectory
def redirected_write(path,data,*args,**kwargs):
 if path==P/'check.stdout.json':path=HERE/'author-replay.json'
 return write(path,data,*args,**kwargs)
def owned_temp(*args,**kwargs):kwargs['dir']=HERE;return temporary(*args,**kwargs)
with patch.object(Path,'write_text',redirected_write),patch.object(tempfile,'TemporaryDirectory',owned_temp),contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(P/'check.py'),run_name='independent_exact_source_replay')
ok(json.loads((P/'check.stdout.json').read_text())==json.loads((HERE/'author-replay.json').read_text()),'all23 author checks exact replay')
for row in manifest['files']:ok(sha(P/row['path'])==row['sha256'],'author packet unchanged '+row['path'])
spec=importlib.util.spec_from_file_location('independent_sls_adapter',P/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
spec=importlib.util.spec_from_file_location('independent_original_recipe',a.OLD/'recipe.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
base=old.commands('/qualified/python','/qualified/node','1'*40);new=a.commands('/qualified/python','/qualified/node','1'*40)
meta=new.pop('SLS_location_successor');oldargv=next(x['argv']for x in base['operations']if x['id']=='standard-web-package');argv=next(x['argv']for x in new['operations']if x['id']=='standard-web-package');diff=[i for i,(x,y)in enumerate(zip(oldargv,argv,strict=True))if x!=y]
ok(diff==[oldargv.index('--sls-wasm-dir')+1],'exactly one literal argv field changes')
ok(argv[diff[0]]==str(a.RECOVERY)and meta['prior_directory']==oldargv[diff[0]],'only owned SLS destination selected')
argv[diff[0]]=oldargv[diff[0]];ok(new==base,'every other field/operation/prerequisite inherited exactly')
ok(new['ready_for_actual']is False and meta['coordinator_must_validate_before_finally'],'no automatic actual authority; pre/final validator mandatory')
rows=a.expected_files();ok(rows['sls.wasm']['sha256']=='62a24736aeaef9c0feec460716eeafdfd5df7a12f51eced86e84fe0ffbb49903'and rows['sls.wasm']['bytes']==5304942,'same original published SLS Wasm identity')
receipt=json.loads(a.RECEIPT.read_text());ok(a.digest(a.RECEIPT)==a.RECEIPT_SHA=='3b15e94030c1c486a33fb73026899c3fd87a10d205d378b1765be09e11144585','exact genuine saved recovery receipt')
ok(receipt['all_match']is True and receipt['no_engine_executed']is True and len(receipt['files'])==3,'receipt explicitly records three exact files and no engine run')
for row in receipt['files']:
 name=str(Path(row['path']).relative_to(a.RECOVERY));ok((row['sha256'],row['bytes'])==(rows[name]['sha256'],rows[name]['bytes']),'all three unchanged published identities '+name)
# Additional physical-boundary failures using tiny inert files, never actual assets.
with temporary(prefix='independent-recovery-',dir=HERE)as td:
 root=Path(td).resolve();a.RECOVERY=root/'recovered';a.RECOVERY.mkdir();a.RECEIPT=root/'receipt';expected={}
 for name in ('sls.js','sls.wasm','generated/models.json'):
  q=a.RECOVERY/name;q.parent.mkdir(exist_ok=True,parents=True);q.write_text('inert '+name);expected[name]={'sha256':sha(q),'bytes':q.stat().st_size}
 a.expected_files=lambda:copy.deepcopy(expected)
 d={'identity':'exact-live640-SLS-three-file-recovery-v1','all_match':True,'no_engine_executed':True,'directory':str(a.RECOVERY),'files':[{'path':str(a.RECOVERY/n),**v}for n,v in expected.items()]}
 def put():a.RECEIPT.write_text(json.dumps(d));a.RECEIPT_SHA=sha(a.RECEIPT);return a.RECEIPT_SHA
 ok(a.validate_recovery(put())['only_location_changed'],'independent inert valid physical namespace')
 d['no_engine_executed']=False
 try:a.validate_recovery(put())
 except ValueError:checks.append('false no-engine recovery authority rejects')
 else:raise AssertionError('invalid recovery accepted')
 d['no_engine_executed']=True;pin=put();saved=a.RECEIPT.read_bytes();a.RECEIPT.write_bytes(saved+b' ')
 try:a.validate_recovery(pin)
 except ValueError:checks.append('receipt bytes drift rejects independent of JSON equivalence')
 else:raise AssertionError('receipt drift accepted')
 a.RECEIPT.write_bytes(saved);target=a.RECOVERY/'generated';target.rename(root/'away');target.symlink_to(root/'away',target_is_directory=True)
 try:a.validate_recovery(pin)
 except ValueError:checks.append('nested directory symlink rejects')
 else:raise AssertionError('directory alias accepted')
ok(not list(HERE.glob('inert-recovery-*'))and not list(HERE.glob('independent-recovery-*')),'owned fixtures all removed')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','independent_checks':len(checks),'labels':checks,'exact_author_checks':23,'actual_recovered_asset_byte_reads':0,'actual_engine_or_build_browser_network_Git_calls':0,'fixtures_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','independent_checks':len(checks),'exact_author_checks':23}))
