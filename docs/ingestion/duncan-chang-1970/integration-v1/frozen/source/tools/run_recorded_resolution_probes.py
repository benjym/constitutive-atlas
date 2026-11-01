"""Five serial native follow-up calls; no compilation or change to model defaults."""
import argparse,gzip,json,sys,subprocess,hashlib,time
from pathlib import Path
repo=Path(__file__).resolve().parents[1];sys.path.insert(0,str(repo))
from atlas.recorded import execute_recorded
from atlas.refinement import refine_recorded
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--solver',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
out=args.output_dir;out.mkdir(parents=True,exist_ok=True);binary=args.solver.resolve()
probes=json.loads((repo/'catalogue/investigations/recorded-resolution-diagnosis-v1/original-igs-material-probes.json').read_text())
results=[]
for probe,depth in zip(probes,[15,20,19]):
 argv=probe['argv'].copy();settings=argv[argv.index('--integration-settings')+1].split(',');settings[3]=str(depth)
 argv[argv.index('--integration-settings')+1]=','.join(settings)
 start=time.monotonic();p=subprocess.run([str(binary),*argv],text=True,capture_output=True,timeout=45)
 response=json.loads(p.stdout)
 results.append(dict(case=probe['case'],factor=probe['factor'],argv=argv,returncode=p.returncode,elapsed_seconds=time.monotonic()-start,response=response))
 print(json.dumps(dict(case=probe['case'],factor=probe['factor'],depth=depth,ok=response['ok'],substeps=response['diagnostics']['substeps'],rejected=response['diagnostics']['rejected'])),flush=True)
(out/'igs-native-depth-probes.json').write_text(json.dumps(dict(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),runs=results),indent=2)+'\n')
with gzip.open(repo/'catalogue/investigations/recorded-refinement-v1/plastic-report.json.gz','rt') as f:report=json.load(f)
source=next(c['specification'] for c in report['study']['cases'] if c['id']=='mcc-plastic-isotropic-strain')
results=[]
for factor,residual in [(64,None),(32,1e-12)]:
 spec,indices=refine_recorded(source,factor)
 if residual is not None:spec.setdefault('integration_settings',{})['residual_tolerance']=residual
 start=time.monotonic();response=execute_recorded(spec,binary,timeout=45)
 results.append(dict(factor=factor,residual_override=residual,original_indices=indices,elapsed_seconds=time.monotonic()-start,response=response))
 print(json.dumps(dict(factor=factor,residual=residual,ok=response['ok'],points=len(response['points']))),flush=True)
with gzip.GzipFile(filename=str(out/'mcc-native-followup.json.gz'),mode='wb',mtime=0) as f:f.write((json.dumps(dict(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),runs=results),indent=2)+'\n').encode())
