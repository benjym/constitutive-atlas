"""Descriptive contraction-disabled retained rates versus already computed HP source estimates."""
import argparse,hashlib,json
from decimal import Decimal as D,localcontext
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(x):n,d=float(x).as_integer_ratio();return D(n)/D(d)
def freeze(root,packet,path):
 assert not path.exists()
 names=['catalogue/investigations/clay2005-boundary-parity-v1/'+n for n in ['comparison.json','protocol.json','model.json']]
 p={'version':'clay2005-boundary-precision-v1-additive-contraction-comparison-freeze','original_prospective_freeze_sha256':sha(packet/'prospective-freeze.json'),'already_computed_precision_results_sha256':sha(packet/'results.json'),'files':{n:sha(root/n)for n in names},'policy':'No new highprecision evaluation, reference, numerical acceptance gate, budget or domain change. Compare retained contract-off rates to existing240digit source estimates using abs(a-b)/max(1,abs(a),abs(b)); descriptive diagnostics only.'}
 path.write_text(json.dumps(p,indent=2)+'\n')
def run(root,packet):
 f=json.loads((packet/'additive-freeze.json').read_text());assert sha(packet/'results.json')==f['already_computed_precision_results_sha256']
 for n,s in f['files'].items():assert sha(root/n)==s
 a=json.loads((root/'catalogue/investigations/clay2005-rates-v3/protocol.json').read_text());b=json.loads((root/'catalogue/investigations/clay2005-boundary-parity-v1/protocol.json').read_text());am={c['id']:c['args']for c in a['cases']};bm={c['id']:c['args']for c in b['cases']};assert am==bm,'same literal inputs required'
 c=json.loads((root/'catalogue/investigations/clay2005-boundary-parity-v1/comparison.json').read_text());rates={k:{x['id']:x['response']['values']for x in c[k]['cases']}for k in ('native','wasm')};results=json.loads((packet/'results.json').read_text());rows=[]
 with localcontext()as ctx:
  ctx.prec=260
  for r in results['cases']:
   ref=list(map(D,r['precision_results']['240']['values']));row={'id':r['id'],'backends':{}}
   for k in ('native','wasm'):
    vals=rates[k][r['id']];errors=[abs(exact(x)-y)/max(D(1),abs(exact(x)),abs(y))for x,y in zip(vals,ref)]
    row['backends'][k]={'retained_values':vals,'scaled_component_source_errors':list(map(str,errors)),'maximum_scaled_source_error':str(max(errors))}
   row['native_wasm_values_identical']=rates['native'][r['id']]==rates['wasm'][r['id']];rows.append(row)
 return {'version':'clay2005-boundary-precision-v1-additive-contraction-comparison','additive_freeze_sha256':sha(packet/'additive-freeze.json'),'script_sha256':sha(Path(__file__)),'literal_input_identity':True,'retained_study_outcome':c['outcome'],'rows':rows,'new_accuracy_gate':False,'compiled_execution':False,'new_high_precision_evaluations':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--packet',type=Path,required=True);p.add_argument('--freeze',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
 if a.freeze:freeze(a.root,a.packet,a.packet/'additive-freeze.json')
 else:
  assert a.output and not a.output.exists();r=run(a.root,a.packet);a.output.write_text(json.dumps(r,indent=2)+'\n');print('retained outcome',r['retained_study_outcome'],'descriptive cases',len(r['rows']))
