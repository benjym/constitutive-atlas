#!/usr/bin/env python3
"""Parent-executed orchestration of unchanged generic integrate API only."""
import argparse,json,math,subprocess,gzip,hashlib,copy
from pathlib import Path
P=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--artifact',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
 out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
 fixture=P.parent/'frozen-probes-v1.json';req=json.loads(fixture.read_text())['probes'][0]['request'];a=req['strain'][0];reference=160000.
 report={'identity':'md1997-exact-protocol1-control-trace-v1','artifact_sha256':hashlib.sha256(Path(args.artifact).read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'iterations':[],'calls':0,'ok':False}
 raw=gzip.open(out/'calls.jsonl.gz','wt')
 def call(b,label):
  r=copy.deepcopy(req);r['strain']=[a,b,b,0,0,0]
  argv=[args.artifact,'--mode','integrate','--model',r['model'],'--parameters',','.join(map(str,r['parameters'])),'--initial',','.join(map(str,r['initial'])),'--integration-settings',','.join(map(str,r['settings'])),'--strain',','.join(map(str,r['strain']))]
  process=subprocess.run(argv,capture_output=True,text=True);response=None
  try:response=json.loads(process.stdout)
  except Exception:pass
  report['calls']+=1;index=report['calls']
  raw.write(json.dumps({'index':index,'label':label,'request':r,'argv':argv,'returncode':process.returncode,'raw_stdout':process.stdout,'stderr':process.stderr,'response':response})+'\n');raw.flush()
  item={'call':index,'radial_increment':b,'ok':bool(response and response.get('ok'))}
  if response:
   item['diagnostics']=response.get('diagnostics');item['message']=response.get('message')
   if item['ok']:item['residual_Pa']=(response['state'][1]+response['state'][2])/2-reference
  return item
 try:
  b=-.2*a
  for it in range(30):
   row={'iteration':it};report['iterations'].append(row);trial=call(b,f'{it}-trial');row['trial']=trial
   if not trial['ok']:report['reason']='constitutive trial failed';break
   residual=trial['residual_Pa']
   if abs(residual)<max(1.,abs(reference))*1e-8:report['ok']=True;report['reason']='radial tolerance reached';break
   h=max(1e-9,abs(a)*1e-3);pert=call(b+h,f'{it}-FD');row['perturbation']=pert
   if not pert['ok']:report['reason']='constitutive perturbation failed';break
   derivative=(pert['residual_Pa']-residual)/h;row['derivative_Pa_per_strain']=derivative
   if not math.isfinite(derivative) or abs(derivative)<1e-6:report['reason']='invalid control derivative';break
   correction=-residual/derivative;row['correction']=correction;row['backtracks']=[];accepted=False
   for k in range(11):
    factor=2.**-k;test=call(b+factor*correction,f'{it}-backtrack-{k}');test['factor']=factor;row['backtracks'].append(test)
    if test['ok'] and abs(test['residual_Pa'])<abs(residual):b+=factor*correction;accepted=True;break
   if not accepted:report['reason']='no strict residual descent among prescribed backtracks';break
  else:report['reason']='outer iteration limit'
 finally:
  raw.close();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
  (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir()) if f.is_file()},indent=2)+'\n')
 print(json.dumps({'ok':report['ok'],'reason':report.get('reason'),'calls':report['calls'],'iterations':len(report['iterations'])},indent=2))
if __name__=='__main__':main()
