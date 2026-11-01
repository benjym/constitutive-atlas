"""Full14-state parity after both independently pass their route audit."""
from assess import require,vector,read,BASE

def compare(native,wasm):
 require(native['backend']=='native'and wasm['backend']=='wasm','parity backend pair');params=dict(zip(read(BASE.parents[2]/'docs/reviews/gis2024-v03-research-freeze-v1/model.json')['parameters'],native['clean']['request']['args'][1].split(',')));scales=[float(params['p_scale'])]*6+[1.]+[float(params['R'])]*6+[1.];worst=0.;points=0
 def pair(a,b):
  nonlocal worst,points
  aa=a['response'];bb=b['response'];require(aa['ok']is bb['ok'],'parity outcome');require(len(aa.get('points',[]))==len(bb.get('points',[])),'parity prefix')
  for x,y in zip(aa.get('points',[]),bb.get('points',[])):
   require(vector(x['state'],14)and vector(y['state'],14),'parity layout');error=max(abs(i-j)/s for i,j,s in zip(x['state'],y['state'],scales));worst=max(worst,error);require(error<=1e-7,'full14 native/Wasm parity');points+=1
 for a,b in zip(native['laboratory'],wasm['laboratory']):require(a['id']==b['id'],'parity case');pair(a['call'],b['call'])
 pair(native['clean'],wasm['clean'])
 for a,b in zip(native['guards'],wasm['guards']):require(a['id']==b['id'],'parity guard');pair(a['call'],b['call']);pair(a['recovery'],b['recovery'])
 for key in ['call','recovery']:pair(native['failure'][key],wasm['failure'][key])
 return {'parity_pass':True,'points':points,'maximum_scaled_full14_difference':worst,'bound':1e-7,'scientific_admission':False}
