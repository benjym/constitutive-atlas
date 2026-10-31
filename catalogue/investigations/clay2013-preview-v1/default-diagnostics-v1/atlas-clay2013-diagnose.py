import sys,json,subprocess,hashlib,pathlib
root=pathlib.Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root))
from atlas.model import load,evaluation_environment
s=root/'catalogue/investigations/clay2013-preview-v1';req=json.load(open(s/'requests.json'))[10];m=load(s/'models/hypoplastic-clay-2013.json');exe='/private/tmp/atlas-clay2013-preview-native-v1/atlas_laboratory_preview'
out=pathlib.Path('/private/tmp/atlas-clay2013-default-diagnostics-v1');out.mkdir(exist_ok=False)
rows=[]
for pressure in (10000.,100000.):
 state={'sigma':[pressure]*3+[0.]*3,'e':.8}
 for radial in (-.2,-.20001,0.,-.5, .2, .5,1.):
  de=[1e-4,radial*1e-4,radial*1e-4,0,0,0]
  args=[exe,'--mode','integrate','--model',req['model'],'--parameters',req['parameters'],'--initial',','.join(format(x,'.17g')for x in state['sigma']+[.8]),'--strain',','.join(format(x,'.17g')for x in de),'--integration-settings',req['integration_settings']]
  p=subprocess.run(args,capture_output=True,text=True,timeout=30)
  env=evaluation_environment(m,state,state,de)
  row={'pressure':pressure,'radial_axial_ratio':radial,'argv':args,'returncode':p.returncode,'raw':p.stdout,'stderr':p.stderr,'derived':{k:(v.v if hasattr(v,'v')else v)for k,v in env.items()if k in('fm','omega','pe','fd','fdA','fs','cos3theta','d','Ad','stress_rate')}}
  rows.append(row);(out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
  r=json.loads(p.stdout);print(pressure,radial,r['ok'],r.get('diagnostics'),flush=True)
(out/'identity.json').write_text(json.dumps({'executable':exe,'sha256':hashlib.sha256(pathlib.Path(exe).read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'original_manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest()},indent=2)+'\n')
