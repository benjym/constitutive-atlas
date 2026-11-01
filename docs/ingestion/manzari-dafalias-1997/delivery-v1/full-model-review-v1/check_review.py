"""Independent saved-byte and source algebra checks; no Atlas imports or runtime calls."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
BASE = OUT.parent
checks = []

def check(name, passed, **detail):
    checks.append(dict(name=name, passed=bool(passed), **detail))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

candidate = BASE / 'manzari-dafalias-1997-constant-m-be-v1.json'
check('exact candidate', sha(candidate) == '28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064')
for relative in ['reference-v1/manifest.json', 'reference-v1/interior-lode-v1/manifest.json',
                 'resolution-study-v4/manifest.json', 'qualification-native-v5/manifest.json',
                 'qualification-wasm-v5/manifest.json', 'public-profile-v1/manifest.json']:
    path = BASE / relative
    for name, expected in json.loads(path.read_text()).items():
        if not isinstance(expected, str) or len(expected) != 64:
            continue
        target = path.parent / name
        check(relative + ':' + name, target.is_file() and sha(target) == expected)
for directory in ['native-v5-review', 'wasm-v5-review']:
    path = BASE / directory / 'manifest.json'
    data = json.loads(path.read_text())
    for name, expected in data['inputs'].items():
        target = Path(name)
        if not target.is_absolute():
            target = ROOT / target
        check(directory + ':' + name, target.is_file() and sha(target) == expected)
receipt = json.loads((BASE.parent/'source-v1/source-receipt.json').read_text())
for row in receipt['files']:
    path = ROOT / row['private_path']
    check('private source:' + path.name, path.is_file() and sha(path) == row['sha256'])

# Source Eq16: Sbar^3=tr(rho^3)/3, Jbar^2=tr(rho^2)/2.
# Cancel invariant powers independently and compare normalized-direction form.
worst = 0.0
for i in range(1, 201):
    angle = math.pi * i / 603
    eigen = [math.cos(angle + 2*k*math.pi/3) for k in range(3)]
    for amplitude in [.002, .1, 4.0]:
        rho = [amplitude*x for x in eigen]
        square = sum(x*x for x in rho)
        cube = sum(x*x*x for x in rho)
        source = 3*math.sqrt(3)/2 * (cube/3) / (square/2)**1.5
        unit = [x/math.sqrt(square) for x in rho]
        reduced = math.sqrt(6)*sum(x*x*x for x in unit)
        worst = max(worst, abs(source-reduced))
check('Eq16 invariant cancellation over 600 nondegenerate directions/scales', worst < 3e-15, maximum_error=worst)

# Fischer-Burmeister residual sqrt(gamma²+f²)-gamma+f=0 implies
# gamma>=0, f<=0 and gamma*(-f)=0. Test active/inactive branches and reject
# both wrong signs, including finite penetration (dimensionless scaled f).
for gamma, f, expected in [(0,-.5,True),(.2,0,True),(0,0,True),(-.2,0,False),(0,.2,False),(.1,-.1,False)]:
    value = math.hypot(gamma,f)-gamma+f
    check('complementarity '+str((gamma,f)), (abs(value)<1e-15)==expected)
check('initial cone has strict elastic margin', -math.sqrt(2/3)*.05*160000 < 0)
check('SI source modulus conversion', 3.14e4 * 1000 == 31400000)
result = dict(identity='md1997-full-model-review-v1-source-and-bindings',
              compiled_calls=0, production_imports=False, checks=checks,
              total=len(checks), failures=sum(not c['passed'] for c in checks))
(OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['identity','total','failures']}))
raise SystemExit(bool(result['failures']))
