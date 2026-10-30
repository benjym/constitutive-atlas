"""Serial native capture and offline verification of incremental settings."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.verify_linearization_api import verify as verify_default
from tools.verify_update_tangent import model_paths
RAW='catalogue/investigations/incremental-settings-v1/responses.json.gz'
DEFAULT_RAW='catalogue/investigations/incremental-settings-v1/default-api.json.gz'
DEFAULT=[2e-10,1e-6,45,14,20000,11]
KEYS=['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks']
def csv(v):return ','.join(format(x,'.17g') for x in v)
def specifications():
 rows=[]
 def add(name,model,strain,settings,mode='linearize',extra=()):
  args=['--mode',mode,'--model',model,'--integration-settings',settings if isinstance(settings,str) else csv(settings)]
  if mode!='run':args+=['--strain',strain]
  rows.append(dict(name=name,argv=args+list(extra)))
 rate='test-parent-reset-cutback';implicit='test-update-tangent-implicit'
 for tol in (1e-4,1e-6,1e-8):add(f'rate-{tol}',rate,'-1,0,0,0,0,0',[2e-10,tol,45,14,20000,11])
 for tol in (1e-4,2e-10,1e-12):add(f'implicit-{tol}',implicit,'.3,0,0,0,0,0',[tol,1e-6,45,14,20000,11])
 add('implicit-budget-one',implicit,'.3,0,0,0,0,0',[2e-10,1e-6,45,14,1,11])
 add('implicit-budget-two',implicit,'.3,0,0,0,0,0',[2e-10,1e-6,45,14,2,11])
 add('rate-budget-one',rate,'-1,0,0,0,0,0',[2e-10,1e-6,45,14,1,11])
 add('rate-budget-three',rate,'-1,0,0,0,0,0',[2e-10,1e-6,45,14,3,11])
 add('depth-zero',rate,'-1,0,0,0,0,0',[2e-10,1e-6,45,0,20000,11])
 add('iterations-one',implicit,'.3,0,0,0,0,0',[2e-10,1e-6,1,0,20000,11])
 add('no-backtracks',implicit,'.3,0,0,0,0,0',[2e-10,1e-6,45,14,20000,0])
 add('empty-defaults','linear-elastic','.001,0,0,0,0,0','',mode='integrate')
 add('run-defaults','linear-elastic','',DEFAULT,mode='run',extra=['--protocol','1','--target','.001','--steps','2'])
 add('run-limited','linear-elastic','',[2e-10,1e-6,1,0,20000,11],mode='run',extra=['--protocol','1','--target','.001','--steps','2'])
 invalid=['0,1e-6,45,14,20000,11','nan,1e-6,45,14,20000,11','2e-10,-1,45,14,20000,11',
          '2e-10,1e-6,0,14,20000,11','2e-10,1e-6,45,21,20000,11','2e-10,1e-6,45,14,0,11',
          '2e-10,1e-6,45,14,20000,31','2e-10,1e-6,1.5,14,20000,11','2e-10,1e-6,45,14,20000','2e-10,1e-6,45,14,20000,11,',
          '2e-10,1e-6,1001,14,20000,11','2e-10,1e-6,45,14,1000001,11','2e-10,1e-6,45,-1,20000,11']
 for i,v in enumerate(invalid):add(f'invalid-{i}','linear-elastic','.001,0,0,0,0,0',v)
 add('wrong-mode','linear-elastic','0,0,0,0,0,0',DEFAULT,mode='evaluate')
 return rows

def verify(rows):
 specs=specifications()
 if len(rows)!=len(specs):raise ValueError('incomplete settings matrix')
 reports=[];rate_errors=[];implicit_errors=[]
 failures={'implicit-budget-one':1,'rate-budget-one':0,'rate-budget-three':2,'depth-zero':0,'iterations-one':0}
 for row,spec in zip(rows,specs):
  if any(row[k]!=spec[k] for k in ('name','argv')) or row['stderr']:raise ValueError('incorrect native invocation')
  name=row['name'];d=row['response'];error=name.startswith('invalid-') or name=='wrong-mode';failed=error or name in failures or name=='run-limited'
  if d['ok'] is not (not failed) or row['returncode']!=(1 if failed else 0):raise ValueError('settings status mismatch')
  if error:
   if 'state' in d or 'integration_settings' in d:raise ValueError('invalid settings published a result')
   continue
  wire=spec['argv'][spec['argv'].index('--integration-settings')+1];settings=[float(v) for v in wire.split(',')] if wire else DEFAULT
  settings_object=dict(zip(KEYS,settings),version='incremental-settings-0.1',norm='scaled_component_max')
  if d['integration_settings']!=settings_object:raise ValueError('settings provenance mismatch')
  if 'catalogue_hash' not in d or not d['model']:raise ValueError('missing run provenance')
  if name.startswith('run-'):
   if len(d['points'])!=(1 if failed else 3):raise ValueError('protocol settings not propagated')
   continue
  if len(d['state'])!=len(d['initial']) or any(not math.isfinite(x) for x in d['state']):raise ValueError('invalid accepted state')
  diag=d['diagnostics'];n=diag['substeps']
  if n>settings[4] or n!=len(diag['increment_fractions']):raise ValueError('accepted-step budget exceeded')
  if failed:
   if d['state']!=d['initial'] or d['tangent_ok'] or d['state_tangent'] is not None or n!=failures[name]:raise ValueError('settings failure lost rollback')
   continue
  if abs(sum(diag['increment_fractions'])-1)>1e-12:raise ValueError('incomplete accepted partition')
  if name.startswith('rate-'):
   x=d['initial'][6];deriv=0.
   for f in diag['increment_fractions']:
    factor=1-f+f*f/2;deriv=deriv*factor+x*f*(1-f);x*=factor
   if not d['tangent_ok'] or abs(x-d['state'][6])>1e-14 or max(abs(v-deriv) for v in d['state_tangent'][6][:3])>1e-12:raise ValueError('configured midpoint replay mismatch')
   err=abs(x-math.exp(-1));rate_errors.append(err);reports.append(dict(name=name,substeps=n,coordinate_error=err))
  elif name.startswith('implicit-') or name=='no-backtracks':
   x=d['initial'][6];deriv=0.
   for f in diag['increment_fractions']:
    h=.3*f;y=2*x/(1+math.sqrt(1-4*h*x));deriv=(deriv+f*y*y)/(1-2*h*y);x=y
   error=abs(x-d['state'][6]);tangent_error=max(abs(v-deriv) for v in d['state_tangent'][6][:3])
   if not d['tangent_ok'] or error>100*settings[0] or tangent_error>1000*settings[0]:raise ValueError('configured implicit replay mismatch')
   if name.startswith('implicit-') and name!='implicit-budget-two':implicit_errors.append(error)
   reports.append(dict(name=name,substeps=n,root_error=error,tangent_error=tangent_error))
 if not all(b<a for a,b in zip(rate_errors,rate_errors[1:])):raise ValueError('rate accuracy does not refine')
 if not implicit_errors[-1]<implicit_errors[0]:raise ValueError('root accuracy does not improve')
 return dict(status='passed',cases=len(rows),invalid_requests=14,bounded_rollback_cases=5,rate_errors=rate_errors,implicit_root_errors=implicit_errors,refinement=reports)

def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 p=sub.add_parser('capture');p.add_argument('--solver',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p=sub.add_parser('verify');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
 args=parser.parse_args()
 if args.command=='capture':
  rows=[]
  for spec in specifications():
   run=subprocess.run([str(args.solver),*spec['argv']],capture_output=True,text=True,timeout=45)
   rows.append(dict(**spec,returncode=run.returncode,stderr=run.stderr,response=json.loads(run.stdout)))
  args.output.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(verify(rows),indent=2));return
 raw=args.raw.read_bytes();rows=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw);report=verify(rows)
 paths=['tools/verify_integration_settings.py','cpp/main.cpp','cpp/include/atlas/settings.hpp','cpp/include/atlas/solver.hpp','cpp/include/atlas/linearize.hpp','atlas/compiler.py']+[str(p.relative_to(ROOT)) for p in model_paths()]
 report.update(raw_sha256=hashlib.sha256(raw).hexdigest(),sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
