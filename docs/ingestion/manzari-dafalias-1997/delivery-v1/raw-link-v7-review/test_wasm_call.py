import copy,gzip,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;A=D.parent/'raw-link-v7';sys.path.insert(0,str(A));s=importlib.util.spec_from_file_location('raw_wasm_review',A/'check_raw.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
f=D/'synthetic-full-md';checks=[]
for name in ['special.jsonl.gz','dense-cos3theta-+0-4096.jsonl.gz']:
 with gzip.open(f/name,'rt')as stream:rows=[json.loads(x)for x in stream]
 for row in rows:
  r=copy.deepcopy(row);r['argv']=None;r['returncode']=0;p=m.Replay(f,'wasm','SYNTHETIC MODULE NEVER EXECUTED');p.calls=r['call_index'];p.validate(r,row['request'])
 checks.append({'name':name+'/all synthetic Wasm calls','count':len(rows),'passed':True})
for name,change in [('logical reject wrongly exit1',lambda r:r.update(returncode=1)),('native argv in Wasm call',lambda r:r.update(argv=['bad'])),('duplicate stdout',lambda r:r.update(raw_stdout='{"ok":false,"ok":true}'))]:
 r=copy.deepcopy(rows[-1]);r['argv']=None;r['returncode']=0;change(r);p=m.Replay(f,'wasm','SYNTHETIC MODULE NEVER EXECUTED');p.calls=r['call_index']
 try:p.validate(r,rows[-1]['request'])
 except Exception as e:checks.append({'name':name,'rejected':True,'error':str(e)})
 else:raise AssertionError(name)
(D/'wasm-call-checks.json').write_text(json.dumps({'compiled_calls':0,'checks':checks},indent=2)+'\n');print(len(checks))
