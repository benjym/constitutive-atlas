"""Supplemental immutable-input integrity and independent accumulated-law checks."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import json,math,hashlib,collections
from prepare_inputs import controls
from waveform_oracle import hex_
P=Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_bytes())
data,reqs,ref,policy=map(load,('source-input.json','requests.json','reference-p360.json','reference-policy.json'));failures=[];count=0;reports=[]
def check(ok,label,**kw):
 global count
 count+=1
 if not ok:failures.append(dict(reason=label,**kw))
def frac(s):return F.from_float(float.fromhex(s))
def dec(f):return D(f.numerator)/D(f.denominator)
with localcontext()as ctx:
 ctx.prec=220;tol=D(policy['maximum_normalized_source_check']);params=ref['parameters'];K,E,s,d,h=map(D,[params[k]for k in('K','E','s','d','h')]);initial=list(map(frac,data['initial']));a0,r0=dec(initial[0]),dec(initial[1]);p0=(a0+2*r0)/3
 check(len(reqs)==len(data['paths'])==len(ref['paths'])==14,'fourteen-corresponding-paths')
 maxima=(F(0),'',0)
 for req,path,out in zip(reqs,data['paths'],ref['paths']):
  rid=req['id'];check(rid==path['id']==out['id'],'id-correspondence',id=rid);check(type(req['protocol'])is int and req['protocol']==path['protocol']==out['protocol'],'protocol-correspondence',id=rid)
  check(len(path['control_targets'])==len(path['control_deltas'])==req['steps']==len(out['points'])-1,'control-and-point-length',id=rid)
  par_order=('p_ref','E','nu','c','phi','psi');check([float(x).hex()for x in req['parameters'].split(',')]==[data['parameters'][n]for n in par_order],'literal-parameter-correspondence',id=rid)
  check([float(x).hex()for x in req['initial'].split(',')]==data['initial'],'literal-initial-correspondence',id=rid)
  check(req['mode']=='run'and req['expected_ok']is True,'literal-request-mode',id=rid)
  expected_controls=controls(req['target'],req['steps'],req['cycles']);previous=0.;acc=F(0);branch_counts=collections.Counter();max_control=F(0);max_q=D(0);max_global=D(0);max_mean_drop=D(0);lastmean=p0
  for i,(target,delta,point)in enumerate(zip(path['control_targets'],path['control_deltas'],out['points'][1:]),1):
   t,dv=float.fromhex(target),float.fromhex(delta);check(math.isfinite(t)and math.isfinite(dv),'finite-controls',id=rid,step=i)
   check((t-previous).hex()==delta,'binary64-subtraction-exact-literal',id=rid,step=i)
   intended=hex_(expected_controls[i])
   check(intended==target,'specified-fraction-rne-target-bits',id=rid,step=i)
   acc+=frac(delta);err=abs(acc-frac(target));max_control=max(max_control,err)
   if err>maxima[0]:maxima=(err,rid,i)
   a,r=map(D,point['state'][:2]);ea,er=map(D,point['strain'][:2]);mean=D(point['mean_stress']);pv=D(point['accumulated_plastic_volumetric_strain']);scale=max(D(1),abs(a),abs(r));branch_counts[point['branch']]+=1
   globalerr=abs((ea+2*er)-(mean-p0)/K-pv);max_global=max(max_global,globalerr);check(globalerr<=tol*max(D(1),abs(ea),abs(er),abs(pv)),'cumulative-elastic-plastic-volume',id=rid,step=i)
   if req['protocol']==3:
    qerr=abs((a-r)-(a0-r0)-dec(acc));max_q=max(max_q,qerr);check(qerr<=tol*scale,'protocol3-cumulative-q',id=rid,step=i)
   if req['protocol']in(2,3):
    max_mean_drop=max(max_mean_drop,lastmean-mean);check(mean>=lastmean-tol*scale,'constantvolume-plastic-mean-nondecrease',id=rid,step=i)
   if req['protocol']==1:
    hi=((1-s)*r0-h)/(1+s)if point['branch']=='extension'else((1+s)*r0+h)/(1-s)
    if point['branch']in('compression','extension'):check(abs(a-hi)<=tol*scale,'drained-source-plateau',id=rid,step=i)
   if req['protocol']==4:check(a>=D(params['apex'])-tol*scale,'hydrostatic-tensile-apex-bound',id=rid,step=i)
   previous=t;lastmean=mean
  reports.append({'id':rid,'protocol':req['protocol'],'updates':req['steps'],'branch_counts':dict(branch_counts),'maximum_cumulative_delta_minus_displayed_control_exact':str(max_control),'maximum_cumulative_delta_minus_displayed_control_decimal':str(dec(max_control)),'maximum_cumulative_q_error':str(max_q),'maximum_global_volume_error':str(max_global),'maximum_constantvolume_mean_drop':str(max_mean_drop)})
 byid={x['id']:x for x in ref['paths']};x,y=[byid['drained-default/'+str(n)]['points'][-1]for n in(100,200)]
 endpoint={}
 for channel in('state','strain'):
  differences=[abs(D(a)-D(b))for a,b in zip(x[channel],y[channel])];endpoint[channel+'_maximum_difference']=str(max(differences));check(max(differences)<=tol*max(D(1),*map(lambda z:abs(D(z)),x[channel]+y[channel])),'drained100-200-'+channel+'-endpoint')
 for p in reports:
  if p['id']in('protocol-1/cyclic','protocol-2/cyclic','protocol-3/cyclic'):check(p['branch_counts'].get('compression',0)>0 and p['branch_counts'].get('extension',0)>0,'cyclic-both-plastic-sides',id=p['id'])
 check(any(p['branch_counts'].get('apex',0)>0 for p in reports if p['protocol']==4),'isotropic-apex-exercised')
 result={'identity':'mc-browser-loading-input-and-adequacy-check-v1','checks':count,'passed':not failures,'failures':failures,'source_input_sha256':hashlib.sha256((P/'source-input.json').read_bytes()).hexdigest(),'maximum_exact_cumulative_delta_vs_displayed_control':{'fraction':str(maxima[0]),'decimal':str(dec(maxima[0])),'path':maxima[1],'step':maxima[2],'interpretation':'not an error; intended stored deltas are consumed independently of displayed control'},'drained100_200_endpoint':endpoint,'paths':reports,'candidate_calls':0,'compiled_observations':0}
(P/'adequacy-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'passed':result['passed'],'checks':count,'failures':failures,'maximum_control_discrepancy':result['maximum_exact_cumulative_delta_vs_displayed_control'],'default_endpoint':endpoint},indent=2));raise SystemExit(0 if result['passed']else 1)
