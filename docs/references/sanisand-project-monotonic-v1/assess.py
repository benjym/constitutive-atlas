"""Independent saved-trajectory adequacy assessor; never imports the oracle/DSL."""
from decimal import Decimal as D,localcontext
from pathlib import Path
import gzip,json
P=Path(__file__).resolve().parent
NAMES=['p50-t12','p80-t8','p80-t10','p80-t12']
def read(path):return json.loads(gzip.decompress(path.read_bytes()))
def require(ok,message):
 if not ok:raise ValueError(message)
def assess(directory=P,documents=None):
 inputs=json.loads((directory/'inputs.json').read_text());policy=json.loads((directory/'policy.json').read_text());gate=policy['gates'];ids=[x['id']for x in inputs['cases']]
 docs=documents if documents is not None else {n:read(directory/f'reference-{n}.json.gz')for n in NAMES}
 require(set(docs)==set(NAMES),'missing precision/refinement corpus')
 with localcontext()as ctx:
  ctx.prec=85;worst_precision=D(0);worst_temporal=D(0);worst_yield=D(0);rows=[];nonzero_fabric=0;plastic_samples=0
  for name,d in docs.items():
   require([x['id']for x in d['cases']]==ids,name+': case coverage/order')
   require(d['precision']==(50 if name.startswith('p50')else 80),name+': precision')
   require(D(d['local_tolerance'])==D('1e-'+name.split('t')[-1]),name+': tolerance')
   for case in d['cases']:
    require(case['status']=='generated',name+': reference failure')
    require(len(case['samples'])==18,name+': sample coverage')
    require(case['accepted']>0 and case['accepted']+case['rejected']<20000,name+': budget')
    for sample in case['samples']:
     require(len(sample['state'])==25 and len(sample['strain'])==6,name+': full state/strain')
     require(all(D(v).is_finite()for v in sample['state']+sample['strain']+list(sample['diagnostics'].values())),name+': nonfinite')
  def difference(left,right,p0):
   worst=D(0)
   for a,b in zip(left['samples'],right['samples']):
    require(D(a['parameter'])==D(b['parameter'])and a['kind']==b['kind'],'sample grid mismatch')
    scales=[p0]*6+[D(1)]*19
    worst=max(worst,max(abs(D(x)-D(y))/s for x,y,s in zip(a['state'],b['state'],scales)))
   return worst
  for i,c in enumerate(inputs['cases']):
   p0=D(c['pressure_Pa']);e=D(c['void_ratio']);k={n:D(v)for n,v in inputs['parameters'].items()};v=list(map(D,c['direction_cartesian']));fine=docs['p80-t12']['cases'][i]
   precision=difference(docs['p50-t12']['cases'][i],fine,p0);medium=difference(docs['p80-t10']['cases'][i],fine,p0);coarse=difference(docs['p80-t8']['cases'][i],docs['p80-t10']['cases'][i],p0)
   require(precision<=D(gate['arithmetic_precision_scaled_difference']),c['id']+': arithmetic adequacy')
   require(medium<=D(gate['fine_medium_scaled_difference']),c['id']+': temporal adequacy')
   ratio=medium/coarse if coarse else D(0)
   require(coarse<=D(gate['refinement_ratio_ignored_below'])or ratio<=D(gate['refinement_ratio_max']),c['id']+': nonconvergent refinement')
   G=k['G0']*k['p_at']*(D('2.97')-e)**2/(1+e)*(p0/k['p_at']).sqrt();entry=p0*(D(2)/3).sqrt()*k['m']/(2*G*sum(x*x for x in v).sqrt());max_yield=D(0)
   for j,sample in enumerate(fine['samples']):
    state=list(map(D,sample['state']));strain=list(map(D,sample['strain']));t=D(sample['parameter']);diag={n:D(x)for n,x in sample['diagnostics'].items()}
    mean=sum(state[:3])/3;dev=[x-(mean if l<3 else 0)for l,x in enumerate(state[:6])];normal=[x/mean-a for x,a in zip(dev,state[7:13])]
    yield_pa=mean*(sum(x*x for x in normal).sqrt()-(D(2)/3).sqrt()*k['m'])
    require(abs(diag['p']-mean)/p0<D('1e-28')and abs(diag['yield_Pa']-yield_pa)/p0<D('1e-28'),'inconsistent stored stress/yield diagnostics')
    require(mean>0 and diag['distance']>=0,'physical domain')
    require(state[6]==e and all(x==0 for x in state[19:]),'e/anchor carry')
    require(abs(sum(state[7:10]))<D(gate['trace_and_symmetry_scaled_error'])and abs(sum(state[13:16]))<D(gate['trace_and_symmetry_scaled_error']),'history deviatoricity')
    require(abs(diag['stress_asymmetry'])/p0<D(gate['trace_and_symmetry_scaled_error']),'stress symmetry')
    expected=[t*v[l]for l in [0,4,8]]+[t*D(2).sqrt()*v[l]for l in[1,5,2]]
    require(max(abs(x-y)for x,y in zip(strain,expected))<D('1e-28'),'strain controls')
    if j==0:require(sample['kind']=='initial'and state==[p0,p0,p0,D(0),D(0),D(0),e]+[D(0)]*18,'initial preparation')
    else:
     err=abs(yield_pa)/p0;max_yield=max(max_yield,err)
     require(err<=D(gate['yield_drift_over_initial_pressure']),c['id']+': yield drift')
    if j==1:
     require(sample['kind']=='first_yield'and abs(t-entry)<D('1e-30'),'exact entry parameter')
     expected_stress=[p0 if l in(0,4,8)else D(0)for l in range(9)];expected_stress=[x+2*G*entry*u for x,u in zip(expected_stress,v)]
     expected_mandel=[expected_stress[l]for l in[0,4,8]]+[D(2).sqrt()*expected_stress[l]for l in[1,5,2]]
     require(max(abs(x-y)/p0 for x,y in zip(state[:6],expected_mandel))<D('1e-28'),'exact elastic leg')
    if j>=2:plastic_samples+=1
   require(any(D(x)!=0 for x in fine['samples'][-1]['state'][7:13]),'no plastic backstress evolution')
   if any(D(x)!=0 for x in fine['samples'][-1]['state'][13:19]):nonzero_fabric+=1
   worst_precision=max(worst_precision,precision);worst_temporal=max(worst_temporal,medium);worst_yield=max(worst_yield,max_yield)
   rows.append({'id':c['id'],'arithmetic_scaled_difference':str(precision),'fine_medium_scaled_difference':str(medium),'medium_coarse_scaled_difference':str(coarse),'refinement_ratio':str(ratio),'maximum_scaled_yield_drift':str(max_yield)})
  return {'reference_adequacy_pass':True,'cases':27,'samples_per_case':18,'plastic_samples':plastic_samples,'nonzero_fabric_endpoints':nonzero_fabric,'maximum_arithmetic_scaled_difference':str(worst_precision),'maximum_fine_medium_scaled_difference':str(worst_temporal),'maximum_scaled_yield_drift':str(worst_yield),'rows':rows,'candidate_calls':0,'scientific_signature':None,'scope':'Project fixed-zero-memory monotonic proportional constant-volume research reference only'}
if __name__=='__main__':print(json.dumps(assess(),indent=2))
