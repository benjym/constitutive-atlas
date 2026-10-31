"""Verify the saved publication/refinement result without measurements or solver calls.
This checks evidence consistency, not independent scientific admission.
"""
import bisect,hashlib,json,pathlib,struct,tarfile

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=pathlib.Path(__file__).resolve().parent
 read=lambda f:json.loads((p/f).read_text())
 for name,h in read('inputs/freeze.json')['files'].items():assert sha((p/'inputs'/name).read_bytes())==h,name
 manifest=read('source-manifest.json')
 with tarfile.open(p/'source.tar.gz') as archive:
  for name,h in manifest.items():assert sha(archive.extractfile('source/'+name).read())==h,name
 pins=read('inputs/source-pins.json');assert sha((p/'generated-models.json').read_bytes())==pins['metadata']['sha256']
 assert sha((p/'source-manifest.json').read_bytes())==pins['source_manifest_sha256']
 ref=read('inputs/reference.json')['channels'];summary=read('results/summary.json');paths=[]
 def interp(x,y,t):
  assert x[0]<=t<=x[-1];i=min(max(1,bisect.bisect_right(x,t)),len(x)-1)
  return y[i-1]+(y[i]-y[i-1])*(t-x[i-1])/(x[i]-x[i-1])
 for request,row in zip(read('inputs/requests.json'),summary['paths'],strict=True):
  d='observations/'+request['id']+'/';z=read(d+'stdout.json');receipt=read(d+'receipt.json')
  assert receipt['returncode']==0 and receipt['artifact_sha256']==pins['artifact']['sha256']
  assert receipt['freeze_sha256']==sha((p/'inputs/freeze.json').read_bytes())
  for name in ['stdout.json','stderr.txt']:assert sha((p/d/name).read_bytes())==receipt[name.split('.')[0]+'_sha256']
  for key in ['model','parameters','initial','protocol','steps','integration_settings']:assert z[key]==request[key]
  assert z['catalogue_hash']==pins['metadata']['catalogue_hash'] and z['ok'] is True
  assert z['research_scope']=={'version':'quarter-strain-operational-0.1','maximum_strain_amplitude':.25,'finite_kinematics_verified':False}
  assert z['loading']['controls_bits']==request['controls_bits']
  x=[v['control'] for v in z['points']]
  assert [struct.pack('>d',v).hex() for v in x]==request['controls_bits']
  assert all(a<b for a,b in zip(x,x[1:])) and x[-1]==.25 and len(x)==request['steps']+1
  ys={'q':[v['q_signed'] for v in z['points']],'volumetric_strain':[sum(v['strain'][:3]) for v in z['points']]}
  assert row['id']==request['id'] and row['complete'] and row['ok']
  for k,c in ref.items():
   assert all(v['lower']<=interp(x,ys[k],v['axial_coordinate'])<=v['upper'] for v in c['rows'])
   assert row['source'][k]=={'pass':True,'failures':[]}
  paths.append((x,ys))
 for left,right,expected in zip(paths,paths[1:],summary['refinement']):
  for k,c in ref.items():
   maximum=max(abs(interp(left[0],left[1][k],v['axial_coordinate'])-interp(right[0],right[1][k],v['axial_coordinate'])) for v in c['rows'])
   assert maximum==expected['channels'][k]['maximum_difference'] and maximum<=c['refinement_limit']
 assert len(paths)==3 and len(summary['refinement'])==2 and summary['source_pass'] and summary['refinement_pass'] and not summary['scientific_admission']
 print('PASS: frozen inputs, archived sources, three native receipts, six source envelopes and four refinement checks. No solver calls or private data required. Experimental errors require separate private-data assessment.')
if __name__=='__main__':main()
