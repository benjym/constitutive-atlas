import json,hashlib
from pathlib import Path
out=Path(__file__).parent
assert not (out/'freeze.json').exists()
src=out.parent/'floating-contraction-v1/browser-loading.json'
r=json.loads(src.read_text())['pairs'][-1]
assert r['name']=='legacy/duncan-chang-1970-endpoint-average/3'
cases=[]
for i in range(1,13):
 for prev_backend in ['native','wasm']:
  prev=r[prev_backend]['points'][i-1]
  for strain_backend in ['native','wasm']:
   cur=r[strain_backend]['points'][i]
   de=[a-b for a,b in zip(cur['strain'],r[strain_backend]['points'][i-1]['strain'])]
   for current_backend in ['native','wasm','previous']:
    z=prev['state'] if current_backend=='previous' else r[current_backend]['points'][i]['state']
    cases.append(dict(id=f'point{i}/prev-{prev_backend}/strain-{strain_backend}/current-{current_backend}',model=r['specification']['model'],parameters=r['specification']['parameters'],previous=prev['state'],current=z,strain=de))
# Finite differences are common-input probes, not an AD/Jacobian accuracy test.
base=[c for c in cases if c['id'].startswith(('point9/','point10/')) and '/prev-native/strain-native/current-native' in c['id']]
for c in base:
 for field in ['current','previous','strain']:
  for k in range(len(c[field])):
   step=1e-8 if field=='strain' else 1e-2
   for sign in [-1,1]:
    d=json.loads(json.dumps(c));d['id']+=f'/{field}{k}/{sign}';d[field][k]+=sign*step;cases.append(d)
requests={'scope':'Identical-input full residual probes at saved accepted endpoints, previous-state guesses and fixed perturbations. These are not actual internal Newton trial traces, AD verification, scientific validation or release acceptance. Compare baseline and contraction-off native to unchanged Wasm. Invalid probes retained; no filtering.','cases':cases}
(out/'requests.json').write_text(json.dumps(requests,indent=2)+'\n')
(out/'POLICY.md').write_text('''# Common-input residual diagnostic\n\nFreeze identical model/parameter/current/previous/strain inputs before any calls. Use all first12saved cyclic endpoints, each native/Wasm previous and strain increment, and native/Wasm endpoint or previous-state guesses. At points9/10 add fixed signed perturbations to each current/previous/strain component. These are reconstructed probes, not observed Newton trials.\n\nRecord every raw response from baseline native, contraction-off native and baseline Wasm evaluate APIs. Report domain rejection agreement and all exact residual differences; do not skip invalid cases or convert a negative diagnostic to a release pass. No shared source, build, tolerance, input or scientific gate change. The original browser-wire gate remains failed.\n''')
paths=[Path(__file__),src,out/'requests.json',out/'POLICY.md',out.parent/'freeze.json',out.parent/'floating-contraction-v1/object-audit-v2.json']
(out/'freeze.json').write_text(json.dumps({'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'cases':len(cases)},indent=2)+'\n')
print(len(cases),'probes frozen')
