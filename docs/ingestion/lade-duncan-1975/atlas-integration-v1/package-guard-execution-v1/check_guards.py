"""Exercise real qualified package guards without importing/executing material assets."""
from pathlib import Path
import hashlib,json,sys,shutil
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT))
from tools.build_implicit_path_laboratory import bundle,GATES
HERE=Path(__file__).resolve().parent
POLICY=json.loads((HERE/'POLICY.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def main(build):
 build=Path(build).resolve();out=HERE/'observations';out.mkdir(exist_ok=False);results=[]
 for case in POLICY['cases']:
  name=case['name'];stage=out/name/'build';stage.mkdir(parents=True)
  for n in POLICY['files']:
   p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((build/n).read_bytes())
  target=stage/case.get('file','implicit-path-qualification.json')
  if name in ['loader-bytes','wasm-bytes','catalogue-bytes']:target.write_bytes(target.read_bytes()+b' ')
  elif name!='positive':
   obj=json.loads(target.read_bytes())
   if name.startswith('false-gate-'):obj['gates'][name.removeprefix('false-gate-')]=False
   elif name=='extra-gate':obj['gates']['invented']=True
   elif name=='truthy-gate':obj['gates']['interpreter']=1
   elif name=='missing-gate':del obj['gates']['helpers']
   elif name=='model-hash':obj['binding']['model_sha256']='0'*64
   elif name=='runtime-hash':obj['binding']['runtime_sha256']='0'*64
   elif name=='unsafe-review-path':obj['independent_review']['path']='../build-review.json'
   elif name=='review-hash':obj['independent_review']['sha256']='0'*64
   elif name in ['same-run','review-rejected','review-false-gate']:
    if name=='same-run':obj['reviewer_run']='/root'
    elif name=='review-rejected':obj['status']='pending'
    else:obj['gates']['wasm_source']=False
    b=(json.dumps(obj,indent=2)+'\n').encode();target.write_bytes(b)
    q=stage/'implicit-path-qualification.json';v=json.loads(q.read_bytes());v['independent_review']['sha256']=sha(b);q.write_text(json.dumps(v,indent=2)+'\n');obj=None
   else:raise AssertionError(name)
   if obj is not None:target.write_text(json.dumps(obj,indent=2)+'\n')
  try:
   identity=bundle(out/name/'package',stage);actual='accepted';error=None
  except Exception as exc:actual='rejected';error=type(exc).__name__+': '+str(exc)
  row={'name':name,'expected':case['expected'],'actual':actual,'passed':actual==case['expected'],'error':error,'input_files':{n:sha((stage/n).read_bytes()) for n in POLICY['files']}}
  results.append(row);(out/'RESULTS.json').write_text(json.dumps({'passed':all(r['passed'] for r in results),'completed':len(results),'planned':len(POLICY['cases']),'checks':results,'scope':'Actual filesystem and production bundle guards; no module import/material execution'},indent=2)+'\n')
  assert row['passed'],row
 print(json.dumps({'passed':True,'checks':len(results)}))
if __name__=='__main__':main(sys.argv[1])
