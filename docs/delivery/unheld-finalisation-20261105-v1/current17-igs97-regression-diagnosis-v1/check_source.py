"""Source reversal and isolated algebra only; no model/kernel/executable invocation."""
from pathlib import Path
import json,hashlib,math
P=Path(__file__).resolve().parent
policy=json.loads((P/'GATES.json').read_text());checks=[]
def check(name,value):assert value,name;checks.append(name)
for label,pin in policy['inputs'].items():
 p=Path(pin['path']);check('input pin '+label,p.stat().st_size==pin['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'])
s=Path(policy['inputs']['current_solver']['path']).read_text();old=Path(policy['inputs']['old_solver']['path']).read_text()
a=(P/'proposed/cpp/include/atlas/solver.hpp').read_text();helper=(P/'rate-control-partition.hpp.txt').read_text()
plain='[&](const Sym<double>&increment){return integrate(model,zn,increment,p,settings);}'
fixed='[&](const Sym<double>&increment){return models()[model].rate?integrate_rate_control_partition(model,zn,increment,de,trial,p,settings):integrate(model,zn,increment,p,settings);}'
check('candidate A reverses exactly to640',a.replace(helper+'\n','').replace(fixed,plain)==s)
q=P/'original-rate-profile-v1';b=(q/'proposed/cpp/include/atlas/solver.hpp').read_text();before=(q/'current-block.txt').read_text();after=(q/'replacement-block.txt').read_text()
check('candidate B reverses exactly to640',b.count(after)==1 and b.replace(after,before)==s)
rate='''double h=std::max(1e-9,std::abs(axial)*1e-3);auto dd=de;dd.v[1]=dd.v[2]=lateral+h;auto pert=integrate(model,zn,dd,p,settings);
            if(!pert.ok)return false;double derivative=(.5*(pert.state[1]+pert.state[2])-.5*(trial.state[1]+trial.state[2]))/h;'''
check('original702 rate arithmetic exact',rate in old)
check('candidateB rate arithmetic exact',rate.replace('\n            ','\n                ').replace('double derivative=','derivative=') in after)
nonrate=after.split('            }else{\n',1)[1].rsplit('            }\n',1)[0]
normalized='\n'.join(line[4:] for line in nonrate.splitlines())+'\n'
check('candidateB nonrate retains640 body',normalized.replace('if(!slope.ok)return false;derivative=slope.value;','if(!slope.ok)return false;const double derivative=slope.value;')==before)
check('generic equationform only','if(models()[model].rate)' in after and 'igs97' not in after and 'manzari' not in after)
check('candidateA unchanged rate threshold','if(!(error<settings.rate_tolerance))return result;' in helper)
for term in ['std::abs(full[j]-two[j])/scales[j]','std::abs(half_defect[j])/scales[j]','std::abs(two_defect[j])/scales[j]']:
 check('candidateA same rate defect '+term,term.replace('[j]','[i]') in s and term in helper)
# Algebraic illustration only: an adaptive tree changes although the observable
# is exactly linear. This proves possible source-path rejection, not IGS cause.
def tree(x):return [.5,.5] if x==0 else [.25]*4
def value(x):return 4*x+2
base=tree(0);previous=False;accepted=False
for k in range(11):
 h=math.ldexp(1e-7,-k);valid=tree(h)==base;slope=(value(h)-value(0))/h
 stable=valid and previous and abs(slope-previous_slope)<=1e-3*max(1,abs(slope),abs(previous_slope))
 accepted=accepted or stable;previous=valid;previous_slope=slope
check('manufactured smooth observable rejects changed adaptive tree',not accepted)
h=1e-7;directional=(value(h)-value(0))/h
check('original directional algebra finite',math.isfinite(directional) and abs(directional-4)<1e-8)
cur=json.loads(Path(policy['inputs']['current_result']['path']).read_text());prior=json.loads(Path(policy['inputs']['old_result']['path']).read_text())
check('exact saved request unchanged',cur['specification']==prior['specification'])
check('saved old success101',prior['result']['ok'] is True and len(prior['result']['points'])==101)
check('saved current failure93',cur['result']['ok'] is False and len(cur['result']['points'])==93)
for d in [cur,prior]:check('same original controls101',len(d['specification']['loading']['controls_bits'])==101)
(P/'source-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'count':len(checks),'actual_model_or_compiled_calls':0},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'actual_model_or_compiled_calls':0}))
