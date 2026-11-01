"""Independent saved-evidence review; never builds or executes material code."""
import argparse, contextlib, hashlib, io, json, math, pathlib, runpy, subprocess, sys
P=pathlib.Path
HERE=P(__file__).resolve().parent

def read(p): return json.loads(p.read_text())
def require(x,m):
    if not x: raise AssertionError(m)
def close(a,b,m):require(math.isclose(a,b,rel_tol=2e-13,abs_tol=1e-16),m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=P,default=HERE.parents[2] if len(HERE.parents)>2 else P.cwd());ap.add_argument('--output',type=P,required=True);args=ap.parse_args();root=args.repo.resolve();b=root/'docs/benchmarks'
 checks=[]
 def mark(name,detail):checks.append({'id':name,'result':'pass','detail':detail})
 # These identities do not import Atlas or evaluate a material trajectory.
 H=[.6,.25,.15,.04,-.02,.01]; D=[.004,-.001,-.0003,.002,.0007,-.0004];dev=[H[i]-1/3 if i<3 else H[i] for i in range(6)]
 dot=lambda a,c:sum(x*y for x,y in zip(a,c));n=math.sqrt(dot(D,D));F=.8;a=2.1;fd=.4
 source=[F*F*(-D[i])+a*a*dot(H,[-v for v in D])*H[i]+fd*a*F*(H[i]+dev[i])*n for i in range(6)]
 converted=[F*F*D[i]+a*a*dot(H,D)*H[i]-fd*a*F*(H[i]+dev[i])*n for i in range(6)]
 for x,y in zip(source,converted):close(-x,y,'Eq40 double sign conversion')
 require(math.sqrt(2/2)==1,'isotropic F');mark('law_sign_and_isotropy','Eq40 stress/stretching sign reversal gives negative nonlinear term; Eq42 F(0)=1; scalar algebra only')
 A=[[2,.3,-.4],[.3,-1,.7],[-.4,.7,4]];v=[2,-1,4,math.sqrt(2)*.3,math.sqrt(2)*-.4,math.sqrt(2)*.7]
 close(dot(v,v),sum(x*x for row in A for x in row),'Mandel contraction');mark('mandel_contraction','Frobenius and sqrt(2)-weighted six-vector norms agree for nonzero shear witness')
 allocation=read(root/'studies/kfs-development-v1/allocation.json');require(allocation['calibration_packages']['density3']==['KFS-TMD3','KFS-TMD8','KFS-TMD13'],'density3');require(not set(allocation['calibration_packages']['density3'])&set(allocation['evaluation_ids']),'whole test overlap')
 params=next(m['parameters'] for m in read(root/'studies/kfs-development-v1/parameters-v1/parameter-policy.json')['models'] if m['id']=='hypoplastic-sand-vw96')
 require({n for n,p in params.items() if p['role']=='fitted'}=={'phi','hs','alpha','beta'},'four fitted');require({n for n,p in params.items() if p['role']=='fixed' and p['category']=='material'}=={'n','ed0','ec0','ei0'},'four inherited');mark('information_partition','whole-test separation; four fitted/four inherited material constants; p_ref numerical')
 cal=read(b/'kfs-tmd13-calibration-sensitivity-v1/results.json')
 for scenario,chosen in cal['selected'].items():
  fits=[f for f in cal['fits'] if f['record']['scenario']==scenario and f['fit_status']=='success'];best=min(fits,key=lambda f:f['best_objective']);require(best['record']['seed']==chosen['seed']==0,'selection');require(best['best_parameters']==chosen['parameters'],'selected vector');require(all(f['evaluation_count']==96 and f['termination']=='budget_limit' for f in fits),'budget')
 delta=[k for k in cal['selected']['file_initial']['parameters'] if cal['selected']['file_initial']['parameters'][k]!=cal['selected']['original_table_disputed_e0']['parameters'][k]];require(delta==['alpha'],'only alpha');mark('calibration_selection','both calibration-only seed0; all six budget96; only selected alpha differs')
 states=read(root/'studies/kfs-development-v1/initialization-v1/states.json')['records']; changed=[]
 for s in states:
  require(s['file_initial']['sigma']==s['original_table_disputed_e0']['sigma'],'hybrid stresses');
  if s['file_initial']['e']!=s['original_table_disputed_e0']['e']:changed.append(s['experiment_id'])
 require(set(changed)=={'KFS-TMD12','KFS-TMD13','KFS-TMD14'},'changed specimen');mark('hybrid_states','only disputed e0 changes; all stress components retained')
 study=read(b/'kfs-tmd13-evaluation-propagation-v1/results.json'); recalculated={}
 for case in study['cases']:
  rec=case['record'];eid=rec['experiment_id'];experiment=read(root/'paper/results/pilot-matched96/experiments'/f'{eid}.json');rows=[]
  for row in experiment['rows']:
   if row['axial_strain']>.02:break
   rows.append(row)
  prediction=read(P('/private/tmp/atlas-kfs-tmd13-evaluation-v1')/f"case-{rec['index']:02d}"/'prediction.json');points=prediction['points'];require(len(rows)==len(points),'complete points');require(prediction['status']=='success','failed prediction')
  scores={}
  for ch in ['q','volumetric_strain']:
   r=[p[ch]-o[ch] for p,o in zip(points,rows)];w=[abs(y['axial_strain']-x['axial_strain']) for x,y in zip(rows,rows[1:])]
   require(all(p['observation_index']==i and p['axial_strain']==rows[i]['axial_strain'] for i,p in enumerate(points)),'order')
   scale=sum(experiment['initial']['effective_stress'][:3])/3 if ch=='q' else .01
   mse=math.fsum(z*(x*x+x*y+y*y)/3 for z,x,y in zip(w,r,r[1:]))/math.fsum(w)/(scale*scale);close(mse,case['metrics'][ch]['scaled_mse'],'independent segment integral');scores[ch]=mse
  recalculated[rec['index']]=scores
 panels=[]
 for panel in study['panels']:
  ids=panel['case_indices'];require(len(ids)==len(set(ids))==6,'panel coverage');require({study['cases'][i]['record']['experiment_id'] for i in ids}==set(allocation['evaluation_ids']),'six tests');score=math.sqrt(math.fsum(recalculated[i][ch] for i in ids for ch in ['q','volumetric_strain'])/12);close(score,panel['root_scaled_mse'],'panel score');panels.append(score)
 require(len(set(i for p in study['panels'] for i in p['case_indices']))==16,'16 unique cases');mark('independent_factorial_metrics',{'sixteen_private_predictions':'complete ordered residual integrals recomputed independently without Atlas metrics','four_scores':panels,'twelve_equal_channel_weights':True})
 outcomes={}
 for packet,expected,count in [('kfs-propagation-refinement-v1',False,32),('kfs-nested-partitions-v1',True,8)]:
  x=read(b/packet/'results.json');require(len(x['checks'])==count,'gate coverage');bad=[]
  for c in x['checks']:
   sep=max(c['coarse_to_medium'],c['medium_to_fine'])<=.01*c['coarse_calibration_response_shift'];non=c['medium_to_fine']<=c['coarse_to_medium']+1e-12
   require(sep==c['both_below_separation_threshold'] and non==c['adjacent_change_nonincreasing'],'predicate arithmetic')
   if not(sep and non):bad.append({'test':c['coarse_case']['experiment_id'],'vector':c['coarse_case']['calibration_scenario'],'channel':c['channel']})
  require((not bad)==expected==x['gate_passed'],'gate verdict');outcomes[packet]={'gate':expected,'failed':bad}
 require(len(outcomes['kfs-propagation-refinement-v1']['failed'])==4,'four retained failures');mark('independent_gate_predicates',outcomes)
 # Run only the already-inspected saved-data entry points. A process launch is fatal.
 commands=[['current-source-build-v1/verify.py'],['current-archived-vw96-v1/check_saved.py'],['current-kfs-tmd7-v1/check_saved.py','--private-dir','/private/tmp/atlas-current-kfs-tmd7-v1']]
 extra=[('kfs-tmd13-calibration-sensitivity-v1',['--private-dir','/private/tmp/atlas-kfs-tmd13-calibration-v1']),('kfs-tmd13-evaluation-propagation-v1',['--private-dir','/private/tmp/atlas-kfs-tmd13-evaluation-v1','--prior-dir','/private/tmp/atlas-kfs-locked-initialization-v1']),('kfs-propagation-refinement-v1',['--private-dir','/private/tmp/atlas-kfs-propagation-refinement-v1','--coarse-dir','/private/tmp/atlas-kfs-tmd13-evaluation-v1','--prior-dir','/private/tmp/atlas-kfs-locked-initialization-v1']),('kfs-nested-partitions-v1',['--private-dir','/private/tmp/atlas-kfs-nested-partitions-v1','--fine-dir','/private/tmp/atlas-kfs-propagation-refinement-v1','--coarse-dir','/private/tmp/atlas-kfs-tmd13-evaluation-v1','--prior-dir','/private/tmp/atlas-kfs-locked-initialization-v1'])]
 import tempfile
 logs=[];old=subprocess.Popen
 def forbidden(*a,**kw):raise AssertionError('Review forbids subprocess/native/build launch')
 subprocess.Popen=forbidden
 try:
  with tempfile.TemporaryDirectory(prefix='kfs-agent-audit-') as d:
   for packet,options in extra:commands.append([packet+'/check_saved.py',*options,'--output',str(P(d)/(packet+'.json'))])
   commands.append(['kfs-private-retention-v1/verify.py'])
   for command in commands:
    stdout=io.StringIO();stderr=io.StringIO();previous=sys.argv;sys.argv=[str(b/command[0]),*command[1:]]
    try:
     with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
      try:runpy.run_path(str(b/command[0]),run_name='__main__')
      except SystemExit as exc:require(exc.code in (None,0),'saved auditor failed')
    finally:sys.argv=previous
    logs.append({'script':command[0],'result':'pass','stdout':stdout.getvalue(),'stderr':stderr.getvalue()})
 finally:subprocess.Popen=old
 mark('saved_auditors',{'passed':len(logs),'process_launch_guard':True})
 result={'review_id':'kfs-development-agent-v1','new_native_calls':0,'new_builds':0,'new_fits':0,'independent_checks':checks,'saved_auditors':logs}
 args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(f'PASS: {len(checks)} independent check groups; {len(logs)} saved auditors; no compiled calls')
if __name__=='__main__':main()
