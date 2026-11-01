"""Read-only binding audit; proposal assessment is documented separately."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,re,math
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';V=C/'native-fixture-fd-analysis-v2';E=C/'native-fixture-fd-diagnostic-execution-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):
 if not v:raise RuntimeError(n)
 checks.append(n)
ck('exact v2 manifest',sha(V/'manifest.json')=='012df6fdb9799457a30c94ce2cc6e4bdfae54eedd835044e7678218ae4d4b315')
for n,v in read(V/'manifest.json')['files'].items():ck('v2 file '+n,sha(V/n)==v)
for n,v in read(V/'inputs.json').items():ck('v2 frozen input '+n,sha(Path(n))==v)
b=read(V/'binding.json');line=(E/'2/stderr').read_text().splitlines()[0];f=dict(re.findall(r'(row|level|h|ad|fd|rp|rm|direction|state|scales)=([^ ]+)',line))
for name,key in [('ad','ad'),('fd','fd'),('plus','rp'),('minus','rm')]:ck('actual numeric '+name,b[name]==float(f[key]))
for name in ['direction','state','scales']:ck('actual full '+name,b[name]==[float(x)for x in f[name].split(',')if x])
ck('actual index and h',b['native_row']==int(f['row'])==0 and b['native_column']==8 and b['level']==int(f['level'])==0 and b['h_hex']==float(f['h']).hex())
ck('error recomputed',b['error']==abs(b['ad']-b['fd']))
ck('original budget recomputed',b['original_budget']==3e-5*max(1,abs(b['ad']),abs(b['fd']))and b['error']>b['original_budget'])
a=read(C/'native-fixture-fd-analysis-v1/lattice-results.json');analytic=float(a['analytic_derivative100']);ck('analytic binding',b['analytic_source_derivative']==analytic and b['native_ad_source_difference']==abs(b['ad']-analytic) and b['native_ad_source_relative_difference']==abs(b['ad']-analytic)/abs(analytic))
ck('observed binade',all(32768<abs(b[k])<65536 for k in ['plus','minus']))
# These enforce the exact mechanically reviewed proposal identity, not an implementation or numerical pass.
p=V/'PLAN.md';ck('exact reviewed proposal',sha(p)=='5aa7e15207cd06b5d09c6282514c35e1ba2be93918da5dcb58b9589006be7949')
print(json.dumps({'identity':'independent-decimal-proposal-binding-review-v1','checks':len(checks),'check_names':checks,'v2_manifest_sha256':sha(V/'manifest.json'),'plan_sha256':sha(p),'saved_numeric_binding':'PASS','proposal_decision':'ACCEPT bounded prospective design; new implementation and independent reference review required','builds':0,'compiled_calls':0},indent=2))
