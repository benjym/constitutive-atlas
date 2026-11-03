"""Independent source-only audit. No Atlas imports or compiled material calls."""
from pathlib import Path
from decimal import Decimal, localcontext
import json,hashlib,sys,ast
W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
O=Path(__file__).resolve().parent
D=Decimal
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
checks=[]
oldp=W/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/reference-corpus-v1.json'
newp=Path(sys.argv[1]);old=load(oldp);new=load(newp)
check(len(old['cases'])==len(new['cases'])==18,'all 18 cases retained')
check(old['acceptance']==new['acceptance'],'acceptance bounds exact')
changed=[];basis=[]
with localcontext() as ctx:
 ctx.prec=80
 for a,b in zip(old['cases'],new['cases']):
  c=dict(a);d=dict(b);ae=c.pop('expected_state');be=d.pop('expected_state')
  check(c==d,a['id']+' all inputs/settings/fixture pins exact')
  check({k:v for k,v in ae.items() if k!='e'}=={k:v for k,v in be.items() if k!='e'},a['id']+' every non-e expected value exact')
  strain=[D(str(x)) for x in b['controls_end']['strain']]
  # Diagonal tensor entries are Mandel components 0,1,2. Off-diagonal
  # Mandel components contribute no trace, irrespective of sqrt(2) scaling.
  tr=sum(strain[:3],D(0));e0=D(str(b['state']['e']))
  expected=(1+e0)*(-tr).exp()-1
  check(D(be['e'])==expected,a['id']+' independent exact Decimal80 trace solution')
  wrong=(1+e0)*(-sum(strain,D(0))).exp()-1
  check(D(ae['e'])==wrong,a['id']+' old error reproduced')
  if ae['e']!=be['e']:changed.append(a['id'])
  if 'basis' in a['id']:basis.append({'id':a['id'],'trace':str(tr),'e':str(expected)})
check(changed==['transport-mixed-partition1','transport-mixed-partition2','transport-mixed-partition4','transport-basis3','transport-basis4','transport-basis5'],'only six shear-containing expected-e entries differ')
check(len(basis)==6,'all six Mandel basis probes retained')
for fixture in ['transport','branch','capacity-max']:
 p=W/f'tests/fixtures/controlled-time/{fixture}.json';m=load(p)
 check(m['equations']['e']=='-(1+e)*trace(strain_rate)',fixture+' production fixture uses trace')
packet=newp.parent
proof=load(packet/'runner-delta-proof.json')
for kind,rel,count in [('native','tests/test_controlled_time_native.py',2),('wasm','tools/test_controlled_time_wasm.mjs',1)]:
 original=(W/rel).read_text();snapshot=(packet/(kind+'-runner-v2.source.txt')).read_text()
 oldpath='docs/ingestion/vibe-2026/controlled-time-qualification-v1/reference-corpus-v1.json'
 newpath='docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/reference-corpus-v2.json'
 check(original.count(oldpath)==count,kind+' original path count')
 check(original.replace(oldpath,newpath)==snapshot,kind+' runner differs only exact corpus paths')
 check(snapshot.replace(newpath,oldpath)==original,kind+' reverse replacement byte identity')
 if kind=='native':ast.parse(snapshot);check(True,'native transformed source syntax')
manifest=W/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/source-manifest-v3.json'
for f in load(manifest)['files']:
 check(sha(W/f['path'])==f['sha256'],'unchanged frozen source '+f['path'])
raw=load(Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/vibe-2026/execution-v1/native-generic-results-test_independent_frozen_corpus_and_refinement.json'))
# Saved observations only; no module execution. Capture actual failure independently.
observed=[]
def walk(x):
 if isinstance(x,dict):
  if 'raw_state' in x and 'duration' in x and x['duration']==4:observed.append(x['raw_state'][7])
  for v in x.values():walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(raw)
check(bool(observed),'saved actual native endpoint found')
correct=float(new['cases'][0]['expected_state']['e']);wrong=float(old['cases'][0]['expected_state']['e'])
tol=1e-8+2e-7*abs(correct)
check(abs(observed[0]-correct)<=tol,'saved failed-call e agrees independently corrected expectation under unchanged bound')
check(abs(observed[0]-wrong)>1e-8+2e-7*abs(wrong),'saved old expectation genuinely fails unchanged bound')
report={'scope':'source-only oracle correction, no new backend execution or E4/E5 approval','checks':checks,'count':len(checks),'changed_cases':changed,'basis':basis,'saved_native_e':observed[0],'corrected_e':correct,'old_e':wrong,'unchanged_tolerance':tol,'inputs':[{'path':str(p),'sha256':sha(p)} for p in [oldp,newp]],'compiled_calls':0}
(O/'audit-results.json').write_text(json.dumps(report,indent=2)+'\n')
print('Independent audit checks:',len(checks))
