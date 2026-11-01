#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('native',type=Path);p.add_argument('wasm',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();n=json.loads(a.native.read_text());w=json.loads(a.wasm.read_text());errors=[]
if n['status']!='passed' or w['status']!='passed':errors.append('backend fixture gate failed')
if n['request_sha256']!=w['request_sha256'] or len(n['rows'])!=len(w['rows']):errors.append('request/report identity mismatch')
for i,(x,y) in enumerate(zip(n['rows'],w['rows'])):
 if x['request']['id']!=y['request']['id']:errors.append([i,'case order mismatch']);continue
 rx,ry=x.get('response',{}),y.get('response',{})
 if rx.get('ok')!=ry.get('ok'):errors.append([i,'outcome mismatch'])
 zx,zy=rx.get('state',[]),ry.get('state',[])
 if len(zx)!=8 or len(zy)!=8 or any(not math.isfinite(v) for v in zx+zy) or any(abs(v-t)>1e-10 for v,t in zip(zx,zy)):errors.append([i,'full-state parity mismatch'])
r={'status':'failed' if errors else 'passed','absolute_state_parity_budget':1e-10,'errors':errors};a.output.write_text(json.dumps(r,indent=2)+'\n');raise SystemExit(1 if errors else 0)
