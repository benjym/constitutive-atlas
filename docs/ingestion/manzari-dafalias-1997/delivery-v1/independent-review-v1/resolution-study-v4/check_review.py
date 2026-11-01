import contextlib,copy,hashlib,io,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];S=P/'resolution-study-v4';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
check('exact assigned manifest',h(S/'manifest.json')=='b82e2f9700717e6325622efb9e51be6d44b1d0a98b7f4281c93fc48b35451759')
for n in ['preflight.py','check_preparation.py']:
 stream=io.StringIO()
 with contextlib.redirect_stdout(stream):runpy.run_path(str(S/n),run_name='__main__')
 j=json.loads(stream.getvalue());(D/('reproduced-'+n+'.json')).write_text(json.dumps(j,indent=2)+'\n')
 if n=='check_preparation.py':check('all author comparisons exactly reproduced',j==json.loads((S/'comparisons.json').read_text()))
plan=json.loads((S/'requests.json').read_text());old=json.loads((P/'execution-v3/requests.json').read_text());check('request exact identity',h(S/'requests.json')=='dc02829df6c1e1b3500781bb5c3c7dc6728897a64b2cd50bd56ef60d99a89d10')
# Independently verify rotated complete increments, tensors and every checkpoint.
mod=runpy.run_path(str(S/'prepare.py'),run_name='review_import_only');rot=mod['rot'];cases={c['id']:c for c in plan['cases']};cv=cases['tensor-covariance'];base=cases[cv['compare_to']];q=cv['rotation']
check('every covariance increment exact rotated base',cv['increments']==[rot(v,q) for v in base['increments']])
check('covariance complete initial state',cv['initial']==rot(base['initial'][:6],q)+[base['initial'][6]]+rot(base['initial'][7:13],q)+[0.])
for i,(cp,bp) in enumerate(zip(cv['checkpoints'],base['checkpoints'])):
 check('covariance source checkpoint '+str(i),all(cp[k]==rot(bp[k],q) for k in ['sigma_Pa','alpha','strain']) and cp['e']==bp['e'] and cp['t']==bp['t'])
check('restart before update2048 complete fine grid',cases['restart-replay']['restart_index']==2048 and cases['restart-replay']['coordinates']==base['coordinates'])
# Synthetic partial reports isolate unchanged accuracy/refinement gate behavior; never backend evidence.
sys.path.insert(0,str(S));coarse=next(c for c in plan['cases'] if c['group']=='axis' and c['resolution']==2048);fine=cases[coarse['id'].rsplit('-',1)[0]+'-4096'];target=next(cp for cp in coarse['checkpoints'] if cp['axial_strain']!=0)['axial_strain']
def minimal(c,alpha_error):
 points=[]
 for cp in c['checkpoints']:
  z=cp['sigma_Pa']+[cp['e']]+cp['alpha']+[0.];z[7]+=alpha_error if cp['axial_strain']==target else 0
  points.append({'coordinate':cp['axial_strain'],'state':z,'strain':[cp['axial_strain'],cp['radial_strain'],cp['radial_strain'],0,0,0]})
 return {'ok':True,'points':points}
def probe(label,ec,ef):
 r={'identity':{'backend':'synthetic-only','model_sha256':plan['model_sha256'],'requests_sha256':h(S/'requests.json'),'policy_sha256':h(S/'POLICY.md'),'manifest_sha256':h(S/'manifest.json')},'cases':{coarse['id']:minimal(coarse,ec),fine['id']:minimal(fine,ef)},'special':{}}
 inp=D/(label+'-synthetic.json');inp.write_text(json.dumps(r));out=D/(label+'-checks.json')
 with patch.object(sys,'argv',[str(S/'check_reports.py'),str(inp),'--output',str(out)]),contextlib.redirect_stdout(io.StringIO()):
  try:runpy.run_path(str(S/'check_reports.py'),run_name='__main__')
  except SystemExit as ex:assert ex.code==1
 return json.loads(out.read_text())['results']
a=probe('coarse-fails-fine-exact',.003,0)
check('coarse accuracy failure remains mandatory',any(c['case']==coarse['id'] and c['channel']=='alpha-source-'+str(target) and not c['passed'] for c in a))
a=probe('flat-errors',.0001,.0001);check('unchanged refinement rejects flat above floor',any(c['case']==fine['id'] and c['channel']=='refinement-'+str(target) and not c['passed'] for c in a))
a=probe('decreasing-errors',.0001,.00005);check('unchanged refinement accepts decreasing error',any(c['case']==fine['id'] and c['channel']=='refinement-'+str(target) and c['passed'] for c in a))
# Empty report rejection reproduces missing-case handling under local v4 selectors.
empty=D/'empty-synthetic.json';empty.write_text('{}\n');out=D/'empty-parity-checks.json'
with patch.object(sys,'argv',[str(S/'check_parity.py'),str(empty),str(empty),'--output',str(out)]),contextlib.redirect_stdout(io.StringIO()):
 try:runpy.run_path(str(S/'check_parity.py'),run_name='__main__')
 except SystemExit as ex:check('empty parity rejects',ex.code==1)
(D/'checks.json').write_text(json.dumps({'reviewer_compiled_calls':0,'decision':'prospective study integrity accepted; execution conditional on independent cross-path justification','checks':checks},indent=2)+'\n')
