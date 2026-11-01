"""Independent binary64 expression oracle for this diagonal repeated spectrum only."""
from pathlib import Path
from fractions import Fraction as F
import json,math
P=Path(__file__).parent

def run(inputs):
 z=inputs['parent'];de=inputs['loading'];_,lam,mu,k=inputs['parameters'];width=2*k
 meanparent=math.fsum(z[:3])/3;meande=math.fsum(de[:3])/3
 devparent=[v-(meanparent if i<3 else 0.)for i,v in enumerate(z[:6])];devload=[v-(meande if i<3 else 0.)for i,v in enumerate(de)]
 trial=[a+2*mu*b for a,b in zip(devparent,devload)];assert trial[1]==trial[2] and trial[0]>trial[1] and trial[3:]==[0.]*3
 tracetrial=math.fsum(trial[:3]);mean=meanparent+(lam+2*mu/3)*math.fsum(de[:3]);gap=F.from_float(trial[0])-F.from_float(trial[1]);inside=gap<=F.from_float(width)
 if inside:branch='elastic';returned_dev=trial[:]
 else:
  if 3*trial[1]<tracetrial-width:
   branch='lower repeated corner';c=(tracetrial-width)/3;returned_dev=[c+width,c,c,0.,0.,0.]
  else:
   return {'version':'diagonal-rounded-expression-reference-0.1','trial_dev':trial,'trial_range_exact':str(gap),'trial_inside':inside,'selected_branch':'face','repeated_minimum':True,'three_vmid':3*trial[1],'trace_minus_width':tracetrial-width,'projector_min_unique':False,'raw_root':None,'conclusion':'Exact range selects plastic extension while rounded branch comparison hits equality and selects a face requiring a nonunique minimum projector.'}
 returned=[(mean if i<3 else 0.)+v for i,v in enumerate(returned_dev)];ep=[z[i+6]+(a-b)/(2*mu)for i,(a,b)in enumerate(zip(trial,returned_dev))]
 current=inputs['nearest_solution'];residual=[a-b for a,b in zip(current[:6],returned)]+[(a-b)-(t-r)/(2*mu)for a,b,t,r in zip(current[6:],z[6:],trial,returned_dev)]
 return {'version':'diagonal-rounded-expression-reference-0.1','method':'standard-library float/fraction; fsum trace rounded from exact three-term sum; independent diagonal spectrum and rank-one projector','trial_dev':trial,'trial_range_exact':str(gap),'trial_inside':inside,'branch':branch,'mean_trial':mean,'returned_dev':returned_dev,'raw_root':returned+ep,'root_range_exact':str(F.from_float(returned[0])-F.from_float(returned[1])),'nearest_physical_state_raw_residual':residual,'current_state_jacobian':'identity_12; returned terms depend only on parent, loading and parameters'}
if __name__=='__main__':
 out=run(json.loads((P/'inputs.json').read_text()));(P/'rounded-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
