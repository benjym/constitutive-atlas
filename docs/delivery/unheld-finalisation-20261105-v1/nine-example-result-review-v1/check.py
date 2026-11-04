from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;N=R.parent;P=N/'nine-example-refresh-plan-v1';O=N/'nine-example-observations-v1';T=N/'nine-example-proposal-v1';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):assert v,n;checks.append(n)
def verify(pin):ck('pin '+pin['path'],sha(Path(pin['path']))==pin['sha256'] and ('bytes'not in pin or Path(pin['path']).stat().st_size==pin['bytes']))
binding=json.loads((O/'actual-binding.json').read_text())
for key in ['metadata','fresh_qualification_receipt','fresh_qualification_review','collector_manifest','collector_review']:verify(binding[key])
for pin in binding['artifacts'].values():verify(pin)
ck('genuine accepted reviews',binding['fresh_qualification_review']['sha256']=='ccadd0e9daf6c87c804567dbea0ba44af97029f08026d35fb8eb0d5d344198c1' and binding['collector_review']['sha256']=='345e1bc4232fe7be449b5307f35974f19561303912ff4052fe51016d9891d174')
q=json.loads(Path(binding['fresh_qualification_review']['path']).read_text());ck('exact qualification artifact match',q['decision']=='accepted' and all(binding['artifacts'][k]['sha256']==v['sha256']for k,v in q['artifacts'].items()))
manifest=json.loads((P/'manifest.json').read_text())
for member in manifest['files']:verify({'path':str(P/member['path']),**{k:v for k,v in member.items()if k!='path'}})
for name,expected in json.loads((P/'source-pins.json').read_text()).items():ck('source '+name,sha(Path(binding['repo'])/name)==expected)
ck('source index original preimage',(P/'original-four-index.json').read_bytes()==(Path(binding['repo'])/'catalogue/laboratory-examples.json').read_bytes())
rows=json.loads((P/'requests.json').read_text());index=json.loads((T/'catalogue/laboratory-examples.json').read_text());ck('nine entries',len(index['examples'])==9)
for row,entry in zip(rows,index['examples']):
 verify(row['old_document']);target=T/row['new_document_path'];raw=(O/'wasm'/(row['id']+'-current.json')).read_bytes()
 ck('exact proposal envelope '+row['id'],target.read_bytes()==raw and entry=={**row['entry'],'document_path':row['new_document_path'],'document_sha256':sha(target)})
ck('exclusive proposal11files',{str(x.relative_to(T))for x in T.rglob('*')if x.is_file()}=={'catalogue/laboratory-examples.json','registration.json',*[r['new_document_path']for r in rows]})
for phase in ['native','wasm','compare','assemble']:
 receipt=json.loads((O/('outer-'+phase)/'receipt.json').read_text());ck('outer passed/reaped '+phase,receipt['status']=='passed' and receipt['returncode']==receipt['reaped_returncode']==0 and receipt['mandatory_reap']is True and receipt['cleanup_errors']==[])
 for pin in [receipt['executable'],receipt['stdout'],receipt['stderr']]:verify(pin)
 ck('outer exact phase/binding '+phase,str(O/'actual-binding.json')in receipt['argv'] and receipt['elapsed_seconds']<1800 and str(P/('assemble.mjs'if phase=='assemble'else'collect.mjs'))in receipt['argv'])
# Durable complete local snapshot of every actual observation/proposal file, no copies needed.
pins=[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}for root in [O,T]for p in sorted(root.rglob('*'))if p.is_file()]
(R/'actual-evidence-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps({'status':'PASS','count':len(checks),'checks':checks,'actual_evidence_files':len(pins),'actual_compiled_calls':0},indent=2))
