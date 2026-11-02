"""Coordinator qualification of the exact tested-upload ordinary Wasm; original gates."""
from pathlib import Path
import sys,subprocess,json,hashlib,struct
HERE=Path(__file__).resolve().parent; PARENT=HERE.parent
site=Path(sys.argv[1]).resolve();out=HERE/'upload-engine';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
local=json.loads((PARENT/'release-v3/package-manifest.json').read_text())
identities={n:{'upload':sha(site/n),'accepted_local':local[n]} for n in ['atlas.js','atlas.wasm','models.json']}
if all(x['upload']==x['accepted_local'] for x in identities.values()):
 (out/'assessment.json').write_text(json.dumps({'pass':True,'exact_accepted_artifact_reuse':True,'identities':identities,'qualification':'Original accepted672requests/backend and independent reference/parity gates apply to exact identical upload engine bytes.'},indent=2)+'\n');print('Exact accepted upload engine; no fresh numerical replay required');sys.exit(0)
p=subprocess.run([sys.executable,'-B',str(PARENT/'qualify.py'),'wasm',str(site/'atlas.js'),str(out/'wasm-results')],capture_output=True,text=True)
(out/'qualification.log').write_text(p.stdout+p.stderr);assert p.returncode==0
native=json.loads((PARENT/'release-v3/native-results/journal.json').read_text());wasm=json.loads((out/'wasm-results/journal.json').read_text());assert len(native)==len(wasm)==668
count=0;maximum=0.
def compare(a,b):
 global count,maximum
 if isinstance(a,dict):
  assert a.keys()==b.keys();return [compare(a[k],b[k]) for k in a]
 if isinstance(a,list):
  assert len(a)==len(b);return [compare(x,y) for x,y in zip(a,b)]
 if isinstance(a,(int,float)) and not isinstance(a,bool):
  delta=abs(a-b)/max(1.,abs(a),abs(b));assert delta<=1e-10,(a,b,delta);count+=1;maximum=max(maximum,delta)
 else:assert a==b,(a,b)
for a,b in zip(native,wasm):
 assert a['id']==b['id'] and a['request']==b['request'];compare(json.loads(a['raw']),json.loads(b['raw']))
original=json.loads((PARENT/'transaction-supplement-v1/native-journal.json').read_text());current_native=json.loads((PARENT/'release-v3/native-supplement.json').read_text());assert [r['request'] for r in original]==[r['request'] for r in current_native];proc=subprocess.Popen(['node',str(PARENT/'wasm-transport.mjs'),str(site/'atlas.js')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);rows=[]
for row,expected in zip(original,current_native):
 proc.stdin.write(json.dumps(row['request'])+'\n');proc.stdin.flush();raw=json.loads(proc.stdout.readline())['raw'];rows.append({'id':row['id'],'request':row['request'],'raw':raw});(out/'wasm-supplement.json').write_text(json.dumps(rows,indent=2)+'\n');compare(json.loads(expected['raw']),json.loads(raw))
proc.stdin.close();proc.wait()
a,f,b,z=[json.loads(r['raw']) for r in rows];bits=lambda xs:b''.join(struct.pack('d',v) for v in xs);parent=[100000.,100000.,100000.,0.,0.,0.,.75]
assert a['ok'] and b['ok'] and z['ok'] and not f['ok'];assert bits(a['state'])==bits(b['state']) and bits(z['state'])==bits(parent) and bits(f['state'])==bits(parent);assert f['diagnostics']['attempted_substeps']>0 and f['diagnostics']['discarded_substeps']==f['diagnostics']['attempted_substeps']
(out/'assessment.json').write_text(json.dumps({'pass':True,'exact_accepted_artifact_reuse':False,'identities':identities,'calls':672,'numeric_comparisons':count,'maximum_scaled_error':maximum,'gate':1e-10,'independent_reference_assessment':json.loads((out/'wasm-results/assessment.json').read_text()),'literal_partial_failure_rollback_recovery_zero':True},indent=2)+'\n');print('Actual uploaded engine672calls/reference/parity/transaction PASS')
