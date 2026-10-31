"""Additive source-only naive binary64 Cartesian determinant diagnostic, not a solver/reference."""
import argparse,hashlib,json,math
from decimal import Decimal as D,localcontext
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(x):n,d=x.as_integer_ratio();return D(n)/D(d)
def run(packet):
 freeze=json.loads((packet/'cofactor-freeze.json').read_text());assert sha(packet/'results.json')==freeze['precision_results_sha256'];assert sha(packet/'prospective-freeze.json')==freeze['input_freeze_sha256'];inputs=json.loads((packet/'prospective-freeze.json').read_text());rates=json.loads((packet/'results.json').read_text());rows=[]
 for case,reference in zip(inputs['cases'],rates['cases']):
  assert case['id']==reference['id'];v=[float(x['literal'])for x in case['exact_binary64']['state'][:6]];q=math.sqrt(2.);x,y,z,u,w,t=v;a=[[x,u/q,t/q],[u/q,y,w/q],[t/q,w/q,z]]
  # Scale prior to scalar cofactors to avoid the scaled1e50 determinant overflowing.
  scale=max(map(abs,v));b=[[x/scale for x in row]for row in a]
  naive=b[0][0]*(b[1][1]*b[2][2]-b[1][2]*b[2][1])-b[0][1]*(b[1][0]*b[2][2]-b[1][2]*b[2][0])+b[0][2]*(b[1][0]*b[2][1]-b[1][1]*b[2][0])
  with localcontext()as ctx:
   ctx.prec=260;actual=D(reference['precision_results']['240']['diagnostics']['det_sigma'])/(exact(scale)**3);value=exact(naive);relative=abs(value-actual)/abs(actual)
  rows.append({'id':case['id'],'binary64_scaled_cartesian_determinant':naive,'binary64_scale':scale,'relative_det_error_against_actual_input_cartesian_source':str(relative)})
 return {'version':'clay2005-boundary-precision-v1-additive-naive-cofactor-diagnostic','freeze_sha256':sha(packet/'cofactor-freeze.json'),'script_sha256':sha(Path(__file__)),'rows':rows,'limitations':['Python scalar binary64 arithmetic, math.sqrt(2) and normalization; not compiled C++/Wasm, contraction test or complete source-rate kernel','Includes representation and normalization error plus arithmetic cancellation; does not isolate one operation or prove a component error bound','No new highprecision source evaluations or acceptance gate'], 'compiled_calls':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--freeze',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
 if a.freeze:
  target=a.packet/'cofactor-freeze.json';assert not target.exists();target.write_text(json.dumps({'version':'clay2005-boundary-precision-v1-additive-naive-cofactor-freeze','input_freeze_sha256':sha(a.packet/'prospective-freeze.json'),'precision_results_sha256':sha(a.packet/'results.json'),'policy':'Descriptive scaled direct Cartesian 3x3 cofactor in Python binary64 for exact retained Mandel inputs mapped using math.sqrt(2). Compare determinant against already computed240digit actual-input Cartesian determinant with same exact scale cubed. No source-rate re-evaluation, gate or domain modification.'},indent=2)+'\n')
 else:
  assert a.output and not a.output.exists();a.output.write_text(json.dumps(run(a.packet),indent=2)+'\n')
