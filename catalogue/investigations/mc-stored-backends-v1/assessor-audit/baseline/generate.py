"""Prospective source/literal request preparation. No candidate execution."""
from pathlib import Path
import sys,shutil,json,gzip,copy,hashlib,difflib,math
from fractions import Fraction
R=Path(sys.argv[1]).resolve();P=Path(sys.argv[2]).resolve();P.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R))
from atlas.compiler import generate
from atlas.evidence_sources import selected_files
model='models/research/mohr-coulomb-sysala-cermak-h0-gap-classifier-v2.json'
def save(name,x):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
for folder,suffixes in [('atlas',{'.py'}),('schemas',{'.json'}),('cpp/include',{'.hpp'})]:
 for src in selected_files(R/folder,suffixes):
  dest=P/'frozen'/src.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
dest=P/'frozen'/model;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/model,dest)
ref=R/'docs/reviews/mc-stored-reference-v1'
if not (P/'reference').exists():shutil.copytree(ref,P/'reference')
generate(P/'generated-original',[R/model])
s=(P/'generated-original/models.hpp').read_text();original=s
s=s.replace('namespace atlas {','namespace atlas {\ninline thread_local int study_selected_branch=-1;\ninline thread_local int study_failure_line=-1;\ninline thread_local std::array<double,24> study_values{};',1)
# Report the branch actually consumed by this exact emitted model, not a second classifier.
trace_names=['K','G','sf','sd','cf','h','aa','ds','dl','dr','da','v1','v2','v3','ftrial','gsl','gsr','gla','gra','class_ga','class_gs','face_gamma','left_gamma','right_gamma']
save('trace-fields.json',trace_names)
lines=s.splitlines();out=[];branch=0
for n,line in enumerate(lines,1):
 # All fail exits remain fail exits, with a write-only diagnostic; no arithmetic or control change.
 if 'return false;' in line:line=line.replace('return false;',f'{{ study_failure_line={n}; return false; }}')
 out.append(line)
 for index,name in enumerate(trace_names):
  if line.startswith('const auto '+name+' = '):out.append(f'study_values[{index}]=atlas::value({name});')
 if line.startswith('const auto branch = '):
  out.append('study_selected_branch=int(atlas::value(branch));');branch+=1
assert branch==1,branch
traced='\n'.join(out)+'\n';(P/'generated').mkdir(exist_ok=True);(P/'generated/models.hpp').write_text(traced)
(P/'generated/instrumentation.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),traced.splitlines(True),fromfile='generated-original/models.hpp',tofile='generated/models.hpp')))
data=json.loads((ref/'corpus/inputs.json').read_bytes());cases=data['cases'];requests=[]
def add(rid,c,kind='jet',mode='eval',family='reference',**kw):
 r=dict(id=rid,case=c['id'],kind=kind,mode=mode,family=family,current=c['current'].copy(),parent=c['parent'].copy(),loading=c['loading'].copy(),parameters=copy.deepcopy(c['parameters']),seeds=copy.deepcopy(data['seeds']),check_initial=False,max_iterations=45,max_depth=0,**kw);requests.append(r);return r
for c in cases:
 for kind in ('double','jet'):add(c['id']+'/'+kind,c,kind)
 # Off-parent value checks are algebraic current shifts, exact binary64 differences assessed with Fraction.
 off=add(c['id']+'/off-parent',c,'jet',family='off-parent')
 off['current']=[(float.fromhex(v)+math.ldexp(float.fromhex(c['parameters']['c']),-4)*(i-2)).hex() for i,v in enumerate(c['current'])]
 if c['id'].startswith('mixed-scale-middle/'):
  for k in (1,3,4,5):off['current'][k]='0x0.0p+0'
 # Keep the tiny middle directly observable; subtracting two huge current/residual values cannot recover it.
supplement=json.loads((P/'supplemental-reference/inputs.json').read_bytes())
for c in supplement['cases']:
 for kind in ('double','jet'):add(c['id']+'/'+kind,c,kind,family='finite-resolution')
# Finite material-domain edge values; these are recognized rejection expectations, not source references.
base=next(c for c in cases if c['id']=='certificate/face/diagonal')
zero=copy.deepcopy(base);zero['id']='analytic-zero-trial';zero['current']=zero['parent']=zero['loading']=['0x0.0p+0']*6
add('initial/valid-zero',zero,'jet',family='initial-valid')['check_initial']=True
bad=add('initial/inadmissible-current',zero,'jet',family='initial-reject');bad['check_initial']=True;bad['current']=[(-100*float.fromhex(base['parameters']['c'])).hex()]*3+['0x0.0p+0']*3
unchecked=copy.deepcopy(bad);unchecked.update(id='initial/off-parent-unchecked',check_initial=False,family='initial-unchecked');requests.append(unchecked)
badparent=add('solver/inadmissible-parent',zero,'double','solve',family='solver-initial-reject');badparent['parent']=bad['current'].copy();badparent['current']=bad['current'].copy()
for c in supplement['cases']:add(c['id']+'/recovery',base,'jet',family='recovery')
for name,value in [('E',0.),('c',0.),('nu',-1.),('nu',.5),('phi',0.),('psi',0.),('phi',math.pi/2),('psi',math.pi/2),('p_ref',0.)]:
 r=add('invalid/'+name+'/'+value.hex(),base,'jet',family='invalid-parameter');r['parameters'][name]=value.hex()
 add(r['id']+'/recovery',base,'jet',family='recovery')
for field in ('current','parent','loading'):
 for k in range(6):
  for token in ('nan','inf','-inf'):
   r=add('nonfinite/'+field+'/'+str(k)+'/'+token,base,'jet',family='nonfinite');r[field][k]=token
   add(r['id']+'/recovery',base,'jet',family='recovery')
for name in base['parameters']:
 for token in ('nan','inf','-inf'):
  r=add('nonfinite/parameter/'+name+'/'+token,base,'jet',family='nonfinite');r['parameters'][name]=token
  add(r['id']+'/recovery',base,'jet',family='recovery')
for col in range(38):
 for field in ('current','parent','loading'):
  r=add('nonfinite/seed/'+str(col)+'/'+field,base,'jet',family='nonfinite');r['seeds'][col][field][col%6]='nan' if col%2 else 'inf'
  add(r['id']+'/recovery',base,'jet',family='recovery')
# Successful host calls are limited to independently admissible source certificate parents.
for c in cases:
 if not c['id'].startswith('certificate/') or c['id'].endswith('/hold'):continue
 add('solver/'+c['id'],c,'double','solve',family='solver-source')
# Failure after one actual Newton iteration; recovery uses original loading with normal settings.
r=add('solver/iteration-budget',base,'double','transaction',family='solver-rollback');r['max_iterations']=1
# Explicit invalid loading and parameters exercise early rollback separately.
r=add('solver/nonfinite-loading',base,'double','transaction',family='solver-early-rollback');r['loading'][0]='nan'
r=add('solver/invalid-parameter',base,'double','transaction',family='solver-early-rollback');r['parameters']['E']='0x0.0p+0'
save('requests.json',requests)
parameter_names=list(json.loads((R/model).read_text())['parameters'])
save('wire.json',{'fields':['id','mode','kind','check_initial','max_iterations','max_depth','parameters in model order','current6','parent6','loading6','38 x current6 parent6 loading6'], 'parameters':parameter_names,'columns':38,'literal_hex':True,'compiled_observations':0})
wire=[]
for r in requests:
 words=[r['id'],r['mode'],r['kind'],str(int(r['check_initial'])),str(r['max_iterations']),str(r['max_depth'])]
 words += [r['parameters'][n] for n in parameter_names]+r['current']+r['parent']+r['loading']
 words += [v for seed in r['seeds'] for f in ('current','parent','loading') for v in seed[f]]
 wire.append(' '.join(words))
(P/'requests.txt.gz').write_bytes(gzip.compress(('\n'.join(wire)+'\n').encode(),mtime=0))
save('generation-results.json',{'requests':len(requests),'reference_inputs':len(cases),'instrumentation_branch_sites':branch,'candidate_calls':0,'compiled_observations':0,'parameter_names':parameter_names,'model_sha256':hashlib.sha256((R/model).read_bytes()).hexdigest()})
print(json.dumps({'requests':len(requests),'candidate_calls':0,'compiled_observations':0}))
