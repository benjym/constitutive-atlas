"""Saved evidence checks only; no module/browser/network execution."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent;N=R.parent;B=N/'compression-browser-v1';A=N/'experiment-compressed-transport-actual-v1';checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(name,truth=True):assert truth,name;checks.append(name)
def read(p):return json.loads(p.read_text())
ck('exact browser manifest',sha((B/'manifest.json').read_bytes())=='fa86f9badf5070a27808954726aea7f5e8c02700bcb106f2d7608cb0682d8f3f')
m=read(B/'manifest.json')
for row in m['files']:
 b=(B/row['path']).read_bytes();ck('manifest member '+row['path'],len(b)==row['bytes']and sha(b)==row['sha256'])
ck('exact seven evidence members',{p.name for p in B.iterdir()}=={'manifest.json',*[x['path']for x in m['files']]})
report=read(B/'report.json');text=(B/'compression-local-v1.js.result.txt').read_text();result=json.loads(text.split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0])
script=(B/'compression-local-v1.js').read_text()
ck('raw actual script exact',text.split('await (async (page) => {',1)[1].split('\n})(page);',1)[0].rstrip()==script.rstrip())
ck('genuine successful raw browser status',result['status']=='passed-normalized-and-largest-native-compressed-UI')
ck('raw rows normalized3600/native200000',result['normalizedRows']==3600 and result['nativeRows']==200000)
ck('native selector exact',result['nativeOption']==[{'label':'CHANG-CREEP-RAW-28-01','value':'builtin:CHANG-CREEP-RAW-28-01'}])
ck('native no-overlay status',result['nativeStatus']=='200000 rows · Source chart shown. No model overlay. See data notes.')
ck('normalized original state asserted before source selection',"if(!(await normalized.innerText()).includes('Overlay shown.'))throw Error('Normalized overlay missing');" in script)
ck('measurement hide checked',"await toggle.uncheck();" in script and "if(!(await normalized.innerText()).includes('Overlay hidden.'))throw Error('Normalized toggle failed');" in script and 'await toggle.check();' in script)
ck('native source chart actually awaited',"page.getByRole('img',{name:'Selected source measurement channels',exact:true}).waitFor({state:'visible'})" in script)
ck('no screenshot-only injected state',not any(x in script for x in ['localStorage','innerHTML','setContent','addInitScript','route.fulfill']))
ck('summary raw assets exact',report['assets_match_reviewed_package']==result['assets'])
inv={x['path']:x for x in read(A/'inventory.json')['files']}
expected={'experiments.mjs','experiments/index.json','experiments/GEOLAB-BASKARP-TRIAX-CD-1.json.gz','experiments/CHANG-CREEP-RAW-28-01.json.gz'}
ck('four exact asset identities',{x['path']for x in result['assets']}==expected)
for asset in result['assets']:
 ck('asset actual HTTP and package '+asset['path'],asset['status']==200 and asset['url']=='http://127.0.0.1:8875/constitutive-atlas/'+asset['path'] and asset['sha256']==inv[asset['path']]['sha256'] and asset['bytes']==inv[asset['path']]['bytes'])
requests=(B/'compression-requests-v1.txt').read_text()
for path in expected:ck('raw request200 '+path,'http://127.0.0.1:8875/constitutive-atlas/'+path+' => [200] OK' in requests)
ck('raw console zero', (B/'compression-console-v1.txt').read_text().strip()=='### Result\nTotal messages: 0 (Errors: 0, Warnings: 0)')
ck('report console zero',report['console_errors']==report['console_warnings']==0)
for dirname,digest in [('experiment-compressed-transport-review-v1','393aa0381ca96210b61c02cebf91ef1f08cc7d2df79357efc5599a33674d78e9'),('experiment-compressed-corpus-review-v1','7c3066faf9b4cb44de26d980cfb2d4e21cef3880f49eb81fbea5308ea6da724a')]:
 d=N/dirname/'decision.json';ck('authority accepted '+dirname,sha(d.read_bytes())==digest and read(d)['status']=='accepted')
corpus=read(N/'experiment-compressed-corpus-review-v1/decision.json')
for path,pin in corpus['binding']['files'].items():ck('corpus evidence '+path,sha((A/path).read_bytes())==pin)
records={x['id']:x for x in read(A/'report.json')['records']}
ck('normalized exact saved corpus rows',records['GEOLAB-BASKARP-TRIAX-CD-1']['rows']==3600)
ck('native exact saved corpus rows',records['CHANG-CREEP-RAW-28-01']['rows']==200000)
for id in ['GEOLAB-BASKARP-TRIAX-CD-1','CHANG-CREEP-RAW-28-01']:
 record=records[id];asset=next(x for x in result['assets']if x['path']=='experiments/'+id+'.json.gz');ck('sample corpus transport '+id,record['transport_sha256']==asset['sha256']and record['transport_bytes']==asset['bytes'])
stdout=(A/'built-assets-stdout.txt').read_text();stderr=(A/'built-assets-stderr.txt').read_bytes()
ck('all994 browser module builtassets retained', 'All 994 built experiments passed browser decoding and checksum checks.' in stdout and 'Gzip experiment transport metadata, checksums, streaming limits, cancellation and legacy compatibility passed.' in stdout and stderr==b'')
ck('actual Node terminal declared0',report['browser_module_994']['exit_code']==0 and report['browser_module_994']['terminal']=='5c7271')
ck('preview stop declared0',report['preview_stopped']=={'session':32844,'terminal':'6e3a9f','exit_code':0})
print(json.dumps({'status':'PASS_SAVED_LOCAL_COMPRESSION_BROWSER_ONLY','count':len(checks),'checks':checks,'new_browser_network_module_compiled_calls':0},indent=2))
