"""Freeze exact binary64 inputs and a prospective diagnostic policy; no source rates evaluated."""
import argparse,hashlib,json,math
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(root):
 study=root/'catalogue/investigations/clay2005-rates-v3';protocol=json.loads((study/'protocol.json').read_text());comparison=json.loads((study/'comparison.json').read_text())
 failed=list(dict.fromkeys(f['case'] for f in comparison['parity']['failures']))
 assert len(failed)==5
 controls=['accuracy/nonisotropic-0-mixed','accuracy/sphere-100000-load','accuracy/rotated-mixed','finite_only/safe','finite_only/oblique-safe','finite_only/shear-near-positive-interior']
 selected=failed+controls;rows=[]
 for name in selected:
  case=next(c for c in protocol['cases'] if c['id']==name)
  arrays=[]
  for field in case['args'][1:]:
   values=[]
   for token in field.split(','):
    x=float(token);assert math.isfinite(x);n,d=x.as_integer_ratio();values.append({'literal':token,'hex':x.hex(),'numerator':str(n),'denominator':str(d)})
   arrays.append(values)
  rows.append({'id':name,'selection':'retained-parity-failure' if name in failed else 'predeclared-control','args':case['args'],'exact_binary64':dict(zip(('parameters','state','increment'),arrays))})
 paths=['catalogue/investigations/clay2005-rates-v3/'+n for n in ['protocol.json','model.json','comparison.json','native-observation.transport.json','wasm-observation.transport.json']]+['docs/ingestion/hypoplastic-clay-2005/rate-study-v2/reference.py','docs/ingestion/hypoplastic-clay-2005/rate-study-v2/reference.json','docs/ingestion/hypoplastic-clay-2005/rate-study-v2/SOURCE_CORRECTION.md','docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3/corpus.json']
 return {'version':'clay2005-actual-binary64-boundary-precision-v1','frozen_before_high_precision_evaluation':True,'files':{p:sha(root/p)for p in paths},'source':{'title':'A hypoplastic constitutive model for clays','author':'David Mašín','year':2005,'doi':'https://doi.org/10.1002/nag.416','url':'https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf','version':'accepted author manuscript; final publisher equivalence unverified','sha256':'8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3','locators':['p10Eq38PLUS,40,41','pp24–25AppendixC73–85'],'private_pdf':'/private/tmp/atlas-ingest-clay2005-20261031/private/masin-2005-author.pdf'},'policy':{'decimal_precisions':[80,160,240],'construction':'each literal first parsed to binary64, then exact integer ratio at every precision; Cartesian off-diagonals divide exact Mandel values by high-precision sqrt(2)','source_route':'Cartesian AppendixC; T=-sigma,D=-E; zero spin; Eq38 PLUS agrees with40/84; no ideal eigenvalues or Atlas evaluation','trigonometry':'stdlib Decimal Taylor sin/cos on exact binary64 phi; stop when term abs<10^(-precision-5)','convergence':[{'pair':[80,160],'scaled_rate_tolerance':'1e-50','relative_detH_tolerance':'1e-50'},{'pair':[160,240],'scaled_rate_tolerance':'1e-120','relative_detH_tolerance':'1e-120'}],'scaled_rate_norm':'max_i abs(a_i-b_i)/max(1,abs(a_i),abs(b_i))','conditioning':'determinant relative Frobenius derivative amplification ||sigma||F ||adj(sigma)||F / abs(det sigma); determinant cancellation sum(abs(cofactor-expansion terms))/abs(det); adjacent-binary64 perturb each nonzero one of6Mandel stress entries up/down at240digits, record SPD and source-rate changes','perturbation_qualification':'adjacent stored inputs only, not evaluation error certificate; no ideal-spectrum perturbations; no domain changes','backend_diagnostic':'compare retained backend rates to converged240digit source estimates componentwise; descriptive only, no new retroactive accuracy gate','failure_policy':'retain source/convergence/domain failures; do not relax tolerances, rescale ideal input, rewrite references or change support'},'cases':rows,'claims':{'new_source_accuracy_gate':False,'scientific_admission':False,'compiled_execution':False}}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);v=a.parse_args();assert not v.output.exists();d=build(v.root);v.output.write_text(json.dumps(d,indent=2)+'\n');print(sha(v.output))
