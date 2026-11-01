from pathlib import Path
import json,hashlib,tarfile,tempfile,csv
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
strip=lambda r:{k:v for k,v in r.items()if k!='elapsed_ms'}
for rel,expected in read(P/'manifest.json')['files'].items():assert sha(P/rel)==expected,rel
receipt=read(P/'package-receipt.json');assert receipt['returncode']==0 and not(P/'package.stderr').read_text()
files=read(P/'package-files.json')['files'];assert len(files)==810
for name,digest in receipt['qualified_engine'].items():assert files[name]==digest
with tempfile.TemporaryDirectory(prefix='atlas-browser-saved-') as temp:
 t=Path(temp)
 with tarfile.open(P/'observations.tar.gz')as archive:archive.extractall(t,filter='data')
 for rel,digest in read(P/'archive-files.json').items():assert sha(t/rel)==digest
 def result(name):
  lines=(t/'cli'/name).read_text().splitlines();assert lines[0]=='### Result',name;return json.loads(lines[1])
 worker=result('worker-gate.stdout');assert worker['passed'] and worker['requests']==26 and all(x['passed']for x in worker['results'])
 B=t/'fixtures-and-downloads';index=read(B/'fixture-index.json');corpus=read(B/'corpus.json')
 assert len(index['imports'])==14 and index['points']==834
 with tarfile.open(ROOT/'docs/reviews/mc-wasm-qualification-v3/observations.tar.gz')as a:
  journal=json.load(a.extractfile('observations/journal.json'));compat=json.load(a.extractfile('observations/compatibility.json'))
 saved={row['id']:json.loads(row['raw']) for row in journal if row['id']!='describe'}
 saved.update({row['id']:json.loads(row['raw'])for row in compat['rows']})
 for row,actual in zip(corpus['rows'],worker['results']):
  assert row['id']==actual['id'] and row['expected']==saved[row['id']]
  assert strip(actual['reply']['result'])==strip(row['expected'])
 for item in index['imports']:
  original=read(B/'imports'/item['file']);actual=read(B/'exports'/item['file'])
  assert sha(B/'imports'/item['file'])==item['sha256']
  assert original['result']==saved[item['id']]
  assert actual['specification']==original['specification'] and strip(actual['result'])==strip(original['result'])
  assert len(actual['result']['points'])==item['points'] and all(len(p['state'])==6 for p in actual['result']['points'])
 for name in ['protocol-1--monotonic.json','protocol-1--cyclic.json','recovered-default.json','gis-named.json']:
  actual=read(B/'roundtrip'/name)
  if name=='gis-named.json':expected=saved['GIS/named_example']
  else:expected=read(B/'imports'/('drained-default--100.json'if name=='recovered-default.json'else name))['result']
  assert strip(actual['result'])==strip(expected)
 rows=list(csv.reader((B/'roundtrip/cyclic.csv').read_text().splitlines()))
 assert len(rows)==66 and 'effective_mean_stress_Pa'in rows[0] and 'stress_scope'in rows[0]
 negative=result('roundtrip-negative.stdout');assert len(negative['invalidImports'])==3 and all(x['workerCalls']==0 for x in negative['invalidImports'])
 assert all('Stopped'in negative['parameterRecovery'][i]['status']for i in [0,2])
 assert all('up to date'in negative['parameterRecovery'][i]['status']for i in [1,3])
 disclosure=result('disclosure-reset.stdout');assert disclosure['matching']['label']=='Match available test inputs'
 assert disclosure['matching']['voidRatioInputs']==0 and disclosure['matching']['enabled']
 assert disclosure['toggle']['initiallyShowing'] and disclosure['toggle']['hidden'] and disclosure['totalStressGuard']['matchingDisabled']
 assert disclosure['reset']=={'model':'mohr-coulomb','target':'1','cycles':'0','confinement':'100','voidRatioInputs':0}
 source=result('source-gis.stdout');assert 'Stopped'in source['gisOrdinary']['status'] and 'up to date'in source['gisNamed']['status']
 assert source['catalogue']['status']=='Available to test · draft' and 'Scientific decision pending.'in source['catalogue']['text']
 assert 'Pair assessment: not assessed.'in source['catalogue']['text']
 assets=result('assets-gate.stdout');seen=set()
 for asset in assets['assets']:
  rel=asset['url'].split('/constitutive-atlas/',1)[1];assert asset['status']==200 and files[rel]==asset['sha256'];seen.add(rel)
 assert {'atlas.js','atlas.wasm','models.json','worker.js','app.js'}<=seen
 assert [x['name']for x in assets['authors']]==['Benjy Marks','François Guillard']
 assert all(x.get('status')==200 for x in assets['sources'])
 assert '100 increments'in assets['defaultDetail']
 assert 'Errors: 0, Warnings: 0'in(t/'cli/final-console.stdout').read_text()
print('PASS: all retained P01–B06 browser delivery evidence; 26 worker requests,14 UI imports/834points; no scientific admission')
