from pathlib import Path
import json,hashlib,importlib.util,tempfile,copy,ast
O=Path(__file__).resolve().parent;checks=[]
def ok(v,n):assert v,n;checks.append(n)
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('sls_source_successor',O/'adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ast.parse((O/'adapter.py').read_text());ok(True,'adapter syntax source-only')
old=m.predecessor();s=m.expected_files();ok(set(s)=={'sls.js','sls.wasm','generated/models.json'},'three exact published identities retained');ok(s['sls.wasm']['sha256']=='62a24736aeaef9c0feec460716eeafdfd5df7a12f51eced86e84fe0ffbb49903','published62a retained, not actual85ab repin')
ok(sha(m.RECEIPT)==m.RECEIPT_SHA,'genuine recoveredreceipt metadata only read; no asset bytes')
actual=json.loads(m.RECEIPT.read_text());ok(actual['all_match']and len(actual['files'])==3,'parent genuine3file recovery records');ok(sum(r['bytes']for r in actual['files'])==5405599,'parent bounded recovery bytecount')
spec=importlib.util.spec_from_file_location('v1_recipe',m.OLD/'recipe.py');v1=importlib.util.module_from_spec(spec);spec.loader.exec_module(v1);base=v1.commands('/qualified/python','/qualified/node','a'*40);new=m.commands('/qualified/python','/qualified/node','a'*40);extra=new.pop('SLS_location_successor');i=next(r for r in new['operations']if r['id']=='standard-web-package')['argv'];idx=i.index('--sls-wasm-dir')+1;ok(i[idx]==str(m.RECOVERY),'onlypathpoints to owned recoveredfixture');i[idx]=extra['prior_directory'];ok(new==base,'entire predecessor recipe exact after solelocation reversal');ok(not new['ready_for_actual'],'all v1 operationalprerequisites retained')
with tempfile.TemporaryDirectory(dir=O,prefix='inert-recovery-')as td:
 root=Path(td).resolve();m.RECOVERY=root/'sls';m.RECOVERY.mkdir();m.RECEIPT=root/'receipt.json';expected={}
 for name in ['sls.js','sls.wasm','generated/models.json']:
  q=m.RECOVERY/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(('INERT:'+name).encode());expected[name]={'sha256':sha(q),'bytes':q.stat().st_size}
 m.expected_files=lambda:copy.deepcopy(expected)
 doc={'identity':'exact-live640-SLS-three-file-recovery-v1','all_match':True,'no_engine_executed':True,'directory':str(m.RECOVERY),'files':[{'path':str(m.RECOVERY/n),**r}for n,r in expected.items()]}
 def put(d):m.RECEIPT.write_text(json.dumps(d));m.RECEIPT_SHA=sha(m.RECEIPT);return m.RECEIPT_SHA
 m.validate_recovery(put(doc));ok(True,'tiny manufactured three-file positive')
 def rejects(fn,label):
  try:fn()
  except (ValueError,FileNotFoundError):ok(True,label)
  else:raise AssertionError(label)
 rejects(lambda:m.validate_recovery('0'*64),'wrongreceiptSHA rejected')
 for name,mutate in [('unpassed',lambda x:x.update(all_match=False)),('wrongdirectory',lambda x:x.update(directory='/wrong')),('missingrecord',lambda x:x['files'].pop()),('receiptpinwrong',lambda x:x['files'][0].update(sha256='0'*64))]:
  d=copy.deepcopy(doc);mutate(d);rejects(lambda:m.validate_recovery(put(d)),'receipt rejects '+name)
 pin=put(doc)
 for name in expected:
  q=m.RECOVERY/name;b=q.read_bytes();q.write_bytes(b+b' ');rejects(lambda:m.validate_recovery(pin),'actualfile drift '+name);q.unlink();rejects(lambda:m.validate_recovery(pin),'missing actualfile '+name);q.write_bytes(b)
 extra=m.RECOVERY/'unexpected';extra.write_text('inert');rejects(lambda:m.validate_recovery(pin),'extra namespace rejected');extra.unlink()
 q=m.RECOVERY/'sls.js';b=q.read_bytes();q.unlink();q.symlink_to(m.RECEIPT);rejects(lambda:m.validate_recovery(pin),'symlink rejected');q.unlink();q.write_bytes(b)
(O/'check.stdout.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'actual_engine_browser_network_build':False,'actual_recovered_asset_byte_reads':0,'fixtures_removed':True},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
