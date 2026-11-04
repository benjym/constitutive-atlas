from pathlib import Path
import hashlib,json,math,re
N=Path('docs/delivery/unheld-finalisation-20261105-v1');P=N/'current17-derivative-trace-actual-v1';Q=N/'shared-current17-review-v1/derivative-trace-actual-v1';A=N/'current17-derivative-trace-plan-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
ck('exact frozen actualmanifest',sha(P/'manifest.json')=='e2aed69f69ea2450f9b9a3c4773366b49e107057e6dfa6b18e3ec3a6516dae9f')
for pin in json.loads((P/'manifest.json').read_text())['files']:
 f=P/pin['path'];ck('member '+pin['path'],not f.is_symlink() and f.stat().st_size==pin['bytes'] and sha(f)==pin['sha256'])
r=json.loads((A/'recipe.json').read_text());last=0
for phase in ('configure','build','run'):
 receipt=json.loads((P/('outer-'+phase)/'receipt.json').read_text());pre=json.loads((P/(phase+'-preflight.json')).read_text())
 ck(phase+' exact argv',receipt['argv']==r[phase+'_argv'])
 ck(phase+' genuine terminal successful clean reap',receipt['status']=='passed'and receipt['returncode']==receipt['reaped_returncode']==0 and receipt['mandatory_reap']is True and receipt['cleanup_errors']==[]and receipt['signals_during_finalization']==[])
 ck(phase+' serial epoch',last<pre['epoch']<=receipt['started_epoch']<receipt['ended_epoch']);last=receipt['ended_epoch']
 ck(phase+' fresh private inventory retained',pre['active_compiled']==[] and Path(pre['process_inventory']).is_file() and pre['free_bytes']>0)
 for k in ('stdout','stderr','executable'):
  pin=receipt[k];f=Path(pin['path']);ck(phase+' '+k+' exact retained bytes',sha(f)==pin['sha256']and f.stat().st_size==pin['bytes'])
for pin in r['source_inputs']+list(r['tools'].values())+[r['parent_case'],r['case_wire']]:
 f=Path(pin['path']);ck('recipe pin '+str(f),sha(f)==pin['sha256']and f.stat().st_size==pin['bytes'])
launch=(P/'launch.py').read_text();ck('launcher verifies pins before and after observer',launch.count('verify()')==3 and launch.index('verify()\nps=')<launch.index('observer.observe(')<launch.index('verify(); print'))
B=Path('/private/tmp/atlas-current17-derivative-trace-v1/CMakeFiles/atlas_derivative_trace.dir')
for name in ('flags.make','link.txt','trace.cpp.o.d'):(Q/name).write_bytes((B/name).read_bytes())
flags=(B/'flags.make').read_text();link=(B/'link.txt').read_text();deps=(B/'trace.cpp.o.d').read_text()
ck('actual flags preserve arithmetic profile',all(v in flags for v in ('-O3','-DNDEBUG','-std=gnu++20','-ffp-contract=off','-Wall','-Wextra')))
ck('actual existing library link','/private/tmp/atlas-md1997-direct-app-v1/merged-native/libatlas_scalar_functions.a'in link)
ck('actual exact source dependencies',str(A.resolve()/'trace.cpp')in deps and str(A.resolve()/'logged-controlled-step.inc')in deps and str(Path(r['source_inputs'][0]['path']))in deps and '/private/tmp/atlas-md1997-direct-app-v1/merged-native/generated/models.hpp'in deps)
rows=[json.loads(x)for x in (P/'outer-run/stdout.raw').read_text().splitlines()];ck('exact21 JSON rows',len(rows)==21)
ck('completion faithfully retains original failure',rows[-1]=={'kind':'completion','controller_ok':False,'step':93,'parent_retained':True})
for iteration,count in ((0,2),(1,11)):
 probes=[x for x in rows if x['kind']=='probe'and x['iteration']==iteration];base=next(x for x in rows if x['kind']=='outer'and x['iteration']==iteration)
 ck('iteration'+str(iteration)+' successful finite base',base['ok']and base['finite_state'])
 ck('iteration'+str(iteration)+' exact probe count',len(probes)==count and [x['probe']for x in probes]==list(range(count)))
 previous=False;previous_slope=0
 for k,p in enumerate(probes):
  ck('probe successfinite '+str((iteration,k)),p['probe_ok']and p['probe_finite_state']and p['representable'])
  ck('probe original halving '+str((iteration,k)),p['h']==math.ldexp(max(1e-9,abs(json.loads((A/'parent-case.json').read_text())['axial'])*1e-3),-k))
  valid=p['comparable']and p['finite_slope'];stable=valid and previous and abs(p['slope']-previous_slope)<=1e-3*max(1,abs(p['slope']),abs(previous_slope))
  ck('probe displayed stability exact '+str((iteration,k)),p['stable']==stable)
  previous=valid
  if valid:previous_slope=p['slope']
 if iteration==1:
  ck('first10 partitions necessarily different',all(not p['comparable']and p['probe_fractions']!=p['base_fractions']for p in probes[:10]))
  ck('only final comparable finite slope',probes[-1]['comparable']and probes[-1]['finite_slope']and all(not p['stable']for p in probes))
  ck('original11probe ceiling exhausted',probes[-1]['probe']==10 and not next(x for x in rows if x['kind']=='derivative'and x['iteration']==1)['ok'])
  ck('residual above existing control convergence bound',next(x for x in rows if x['kind']=='residual'and x['iteration']==1)['residual']>110000*1e-8)
ck('line search lateral is alpha1',next(x for x in rows if x['kind']=='line_search')['lateral']==1)
(Q/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'compiled_calls':0},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks)}))
