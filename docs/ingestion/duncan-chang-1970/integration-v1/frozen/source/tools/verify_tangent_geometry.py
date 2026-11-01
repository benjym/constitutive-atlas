"""Capture serial native tangent probes or verify retained geometry evidence offline."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.dsl import evaluate,parse
from atlas.model import defaults,load
from tools.verify_update_tangent import RAW as BASE_RAW,model_paths

RAW='catalogue/investigations/tangent-geometry-v1/responses.json.gz'
INDICES=(0,1,2,3,4,9,10)
STEPS=(2e-7,1e-7,5e-8)
DIRECTION=tuple(x/math.sqrt(35) for x in (2,-1,3,4,-2,1))
# Rodrigues rotation, axis (1,2,3), angle 0.61 radians.
a=[x/math.sqrt(14) for x in (1,2,3)];c=math.cos(.61);s=math.sin(.61)
K=[[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]]
ROTATION=[[c*(i==j)+(1-c)*a[i]*a[j]+s*K[i][j] for j in range(3)] for i in range(3)]

def rotate(v):
 q=math.sqrt(2);A=[[v[0],v[3]/q,v[5]/q],[v[3]/q,v[1],v[4]/q],[v[5]/q,v[4]/q,v[2]]]
 B=[[sum(ROTATION[i][k]*A[k][l]*ROTATION[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
 return [B[0][0],B[1][1],B[2][2],q*B[0][1],q*B[1][2],q*B[0][2]]

Q=list(map(list,zip(*[rotate([float(i==j) for i in range(6)]) for j in range(6)])))

def reference():return json.loads(gzip.decompress((ROOT/BASE_RAW).read_bytes()))
def models():return {m['id']:m for m in map(load,model_paths())}
def rotate_state(values,model):
 result=[];offset=0
 for f in model['state']:
  n=6 if f['shape']=='sym' else 1
  result.extend(rotate(values[offset:offset+n]) if n==6 else values[offset:offset+n]);offset+=n
 return result

def specifications():
 result=[];ms=models()
 for index in INDICES:
  r=reference()[index];parent=r['parent'];de=r['increment'];model=ms[r['model']]
  def add(name,p,d,mode):
   csv=lambda v:','.join(format(x,'.17g') for x in v)
   result.append(dict(name=f'{index}/{name}',argv=['--mode',mode,'--model',r['model'],'--initial',csv(p),'--strain',csv(d)]))
  add('rotated',rotate_state(parent,model),rotate(de),'linearize')
  for h in STEPS:
   for sign in (-1,1):add(f'direction/{h}/{sign}',parent,[x+sign*h*v for x,v in zip(de,DIRECTION)],'integrate')
 return result

def verify(rows):
 specs=specifications();base=reference();ms=models();worst_fd=0;worst_fine=0;worst_rotation=0;entries=0;rotations=[];sequences=[]
 if len(rows)!=len(specs):raise ValueError('incomplete geometry matrix')
 for row,spec in zip(rows,specs):
  if any(row[k]!=spec[k] for k in ('name','argv')) or row['returncode']!=0 or row['stderr']:
   raise ValueError('incorrect native invocation')
  d=row['response']
  index=int(row['name'].split('/')[0]);n=len(base[index]['state'])
  if d.get('ok') is not True or len(d['state'])!=n or any(not math.isfinite(x) for x in d['state']):raise ValueError('failed/nonfinite update')
 by_name={r['name']:r['response'] for r in rows}
 for index in INDICES:
  r=base[index];model=ms[r['model']];p=defaults(model)
  scales=[evaluate(parse(f['scale']),p) for f in model['state'] for _ in range(6 if f['shape']=='sym' else 1)]
  errors=[]
  for h in STEPS:
   minus=by_name[f'{index}/direction/{h}/-1'];plus=by_name[f'{index}/direction/{h}/1']
   if minus['diagnostics']['increment_fractions']!=r['fractions'] or plus['diagnostics']['increment_fractions']!=r['fractions']:
    raise ValueError('directional comparison changed accepted partition')
   fd=[(x-y)/(2*h) for x,y in zip(plus['state'],minus['state'])]
   want=[sum(x*v for x,v in zip(row,DIRECTION)) for row in r['tangent']]
   error=max(abs(x-y)/max(scale,abs(y)) for x,y,scale in zip(want,fd,scales))
   errors.append(error);worst_fd=max(worst_fd,error);entries+=len(fd)
  if errors[-1]>1e-5:raise ValueError('refined directional derivative mismatch')
  for coarse,fine in zip(errors,errors[1:]):
   if coarse>1e-5 and fine>coarse/2:raise ValueError('directional discrepancy does not refine')
  worst_fine=max(worst_fine,errors[-1]);sequences.append(dict(index=index,model=r['model'],normalized_errors=errors))
  d=by_name[f'{index}/rotated']
  if not d.get('tangent_ok'):raise ValueError('rotated tangent unavailable')
  if len(d['state_tangent'])!=len(scales) or any(len(v)!=6 or any(not math.isfinite(x) for x in v) for v in d['state_tangent']):
   raise ValueError('rotated tangent malformed')
  # First transform each state-valued tangent column, then right-multiply Q^T.
  transformed=list(map(list,zip(*[rotate_state([row[j] for row in r['tangent']],model) for j in range(6)])))
  expected=[[sum(row[k]*Q[j][k] for k in range(6)) for j in range(6)] for row in transformed]
  state_expected=rotate_state(r['state'],model)
  state_error=max(abs(x-y)/scale for x,y,scale in zip(d['state'],state_expected,scales))
  tangent_error=max(abs(x-y)/max(scale,abs(y)) for row,want,scale in zip(d['state_tangent'],expected,scales) for x,y in zip(row,want))
  same=d['diagnostics']['increment_fractions']==r['fractions']
  # Same-partition covariance is a strict algebra/discrete-update check. Different
  # partitions are retained as diagnostics, not counted as passing that check.
  if index!=4 and not same:raise ValueError('required rotation changed accepted partition')
  if same and (state_error>1e-7 or tangent_error>1e-7):raise ValueError('fixed-partition rotational covariance mismatch')
  rotations.append(dict(index=index,model=r['model'],same_partition=same,state_scaled_error=state_error,tangent_normalized_error=tangent_error))
  if same:worst_rotation=max(worst_rotation,tangent_error)
 return dict(status='passed',native_requests=len(rows),directional_cases=len(INDICES)*len(STEPS),directional_entries=entries,
             direction=list(DIRECTION),steps=list(STEPS),refined_fd_tolerance=1e-5,largest_directional_error=worst_fd,
             largest_finest_directional_error=worst_fine,directional_sequences=sequences,
             individual_steps_above_tolerance=sum(e>1e-5 for seq in sequences for e in seq['normalized_errors']),
             rotation=ROTATION,rotation_tolerance=1e-7,rotations=rotations,
             same_partition_rotation_cases=sum(x['same_partition'] for x in rotations),largest_fixed_partition_rotation_error=worst_rotation)

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
 raw=args.raw.read_bytes();rows=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw)
 report=verify(rows);paths=['tools/verify_tangent_geometry.py',BASE_RAW,'cpp/main.cpp','cpp/include/atlas/linearize.hpp','cpp/include/atlas/solver.hpp']+[str(p.relative_to(ROOT)) for p in model_paths()]
 report.update(raw_sha256=hashlib.sha256(raw).hexdigest(),sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
