"""Saved-only full-state native/Wasm comparison after separate backend audits."""
import json,math,sys
from pathlib import Path
from assess import load,FROZEN,require,vector

def compare(native,wasm,rows,bound):
 require(native['backend']=='native'and wasm['backend']=='wasm','backend pair identity');require(len(native['rows'])==len(wasm['rows'])==len(rows),'parity row coverage');worst=0.;points=0
 def pair(a,b,params):
  nonlocal worst,points
  for key in ['model','parameters','settings','strain']:require(a['request'][key]==b['request'][key],'parity literal loading/settings')
  require(a['response']['ok']is b['response']['ok'],'parity status')
  if 'state'not in a['response']or'state'not in b['response']:require('state'not in a['response']and'state'not in b['response'],'parity state envelope');return
  scales=[params['p_scale']]*6+[1.]+[params['R']]*6+[1.]
  for key in ['initial','state']:
   aa=a['request']['initial']if key=='initial'else a['response']['state'];bb=b['request']['initial']if key=='initial'else b['response']['state'];require(vector(aa,14)and vector(bb,14),'parity finite layout');error=max(abs(x-y)/s for x,y,s in zip(aa,bb,scales));worst=max(worst,error);require(error<=bound,'native/Wasm state parity')
  points+=1
 for a,b,row in zip(native['rows'],wasm['rows'],rows):
  require(a['id']==b['id']==row['id'],'parity trajectory identity');model=load(FROZEN/'model.json');params=dict(zip(model['parameters'],row['parameters']))
  for key in ['calls','restart_same','restart_fresh']:
   require(len(a[key])==len(b[key]),'parity call coverage')
   for x,y in zip(a[key],b[key]):pair(x,y,params)
 params=dict(zip(load(FROZEN/'model.json')['parameters'],native['control']['request']['parameters']));pair(native['control'],wasm['control'],params);require(len(native['probes'])==len(wasm['probes'])==9,'parity probe coverage')
 for a,b in zip(native['probes'],wasm['probes']):
  require(a['id']==b['id'],'parity probe identity')
  for key in ['call','recovery']:pair(a[key],b[key],params)
 return {'native_wasm_parity_pass':True,'points':points,'maximum_scaled_full_state_difference':worst,'frozen_bound':bound,'scientific_admission':False}
if __name__=='__main__':
 n,w=map(Path,sys.argv[1:3]);require(load(n/'assessment.json')['backend_qualification_pass']is True and load(w/'assessment.json')['backend_qualification_pass']is True,'separate backend qualification');print(json.dumps(compare(load(n/'result.json'),load(w/'result.json'),load(FROZEN/'trajectory-requests.json.gz'),load(FROZEN/'policy.json')['native_wasm_scaled_parity_max']),indent=2))
