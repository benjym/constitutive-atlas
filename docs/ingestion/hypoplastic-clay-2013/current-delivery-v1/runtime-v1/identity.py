from pathlib import Path
import hashlib,json
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(value,message):
 if not value:raise ValueError(message)
def verify_inputs(study):
 s=Path(study);f=json.loads((s/'INPUT_FREEZE.json').read_text());root=Path(f['root'])
 for n,h in f['files'].items():
  p=Path(n);p=p if p.is_absolute() else root/p
  require(p.is_file() and digest(p)==h,'changed frozen input: '+n)
 return f
def verify_receipt(study,backend,receipt,journal):
 s=Path(study);f=verify_inputs(s)
 require(receipt.get('completed') is True,'incomplete '+backend)
 require(receipt['freeze_sha256']==digest(s/'INPUT_FREEZE.json'),'source freeze receipt')
 require(receipt['journal_sha256']==digest(s/backend/'journal.json'),'raw journal binding')
 expected=json.loads((s/'PLAN.json').read_text())['artifacts'][backend]
 require(receipt['artifacts']==expected,'artifact binding')
 for n,h in expected.items():require(digest(n)==h,'changed runtime artifact: '+n)
 require(receipt['builds']==0,'retained artifact reuse only')
 require(all(c['exit_code'] in (0,1) for c in receipt['commands']),'unexpected process code')
 if backend=='native':
  requests=json.loads((s/'requests.json').read_text())
  require(len(receipt['commands'])==21,'native complete commands')
  require(receipt['commands'][0]['exit_code']==0,'native descriptor status')
  for c,q in zip(receipt['commands'][1:],requests):require(c['exit_code']==(0 if q['expected_ok'] else 1),'native expected status: '+q['id'])
 else:require(len(receipt['commands'])==1 and receipt['commands'][0]['exit_code']==0,'Wasm collector status')
