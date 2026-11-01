"""Reviewer diagnostics over retained evidence; never runs a compiled artifact."""
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
PACKET = ROOT / 'docs/ingestion/power-creep-itasca900'
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))
import power_creep_study as study
from atlas.model import load

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    checked = 0
    for name in ['manifest.json', 'execution-v1/manifest.json', 'verification-v1/manifest.json', 'review-v1/manifest.json']:
        path = PACKET / name
        manifest = json.loads(path.read_text())
        for relative, digest in manifest['files'].items():
            assert sha(path.parent / relative) == digest, relative
            checked += 1
        for absolute, digest in manifest.get('artifacts', {}).items():
            assert sha(Path(absolute)) == digest, absolute
            checked += 1
    retention = json.loads((ROOT/'docs/admission/power-creep-approved-v1/source-retention.json').read_text())
    source = ROOT / retention['path']
    assert sha(source) == retention['sha256']
    original = json.loads(source.read_text())
    assert isinstance(original, str) and 'Both Components Active' in original
    assert '(2)' in original and '(7)' in original and 'Sign Conventions' in original
    load(ROOT/'models/research/power-creep/power-creep-itasca900-both-active-ode.json')
    assessments = []
    execution = PACKET/'execution-v1'
    for directory, native in [(execution/'native', None), (execution/'refinement-v2/native', None), (execution/'refinement-v2/wasm', execution/'refinement-v2/native')]:
        study.PACKET = directory.parent
        with contextlib.redirect_stdout(io.StringIO()) as output:
            try:
                study.assess(directory, native)
            except SystemExit as exc:
                assert exc.code == 1
        report = json.loads(output.getvalue())
        assessments.append({'directory':str(directory.relative_to(ROOT)), 'passed':report['passed'], 'passing_requests':sum(r['passed'] for r in report['results']), 'requests':len(report['results'])})
    v = runpy.run_path(str(PACKET/'verification-v1/verify.py'))
    y = v['INITIAL'][:]
    reference = json.loads((PACKET/'verification-v1/reference.json').read_text())
    reference_error = 0
    for (duration, rate), expected in zip(v['PATH'], reference['states']):
        y = v['rk4'](y, rate, duration, 2048)
        reference_error = max(reference_error, v['err'](y, expected))
    assert reference_error == 0
    # Differentiate the source radial vector law analytically, independently of
    # the generated Jet implementation; compare centered source-RHS differences.
    z = [1300000., 800000., 900000., 200000., -100000., 300000.]
    mean = sum(z[:3])/3
    s = [a-(mean if i<3 else 0) for i,a in enumerate(z)]
    q = math.sqrt(1.5*sum(a*a for a in s))
    errors = []
    for exponent in [1., 1.5, 2.2, 3.]:
        p = [20e6, 12e6, 1e6, .002, exponent, .001, exponent, 1.]
        c = 3*p[1]*(p[3]+p[5])*q**(exponent-1)/p[2]**exponent
        worst = 0
        for j in range(6):
            plus=z[:]; minus=z[:]; plus[j]+=1.; minus[j]-=1.
            fp=study.reference_rate(plus,[0.]*6,p)[0]
            fm=study.reference_rate(minus,[0.]*6,p)[0]
            for i in range(6):
                projector = float(i==j)-(1/3 if i<3 and j<3 else 0)
                analytic = -c*projector-c*(exponent-1)*1.5*s[i]*s[j]/q**2
                worst = max(worst,abs((fp[i]-fm[i])/2-analytic))
        assert worst < 1e-8
        errors.append({'exponent':exponent,'max_jacobian_absolute_error_per_s':worst})
    return {'passed':True,'compiled_calls':0,'manifest_and_artifact_hash_checks':checked,'private_source_sha256':sha(source),'original_source_format':'private readable web-tool extracted text JSON; not origin HTML','model_validation':'pass','saved_assessments':assessments,'rk4_reference_max_error_Pa':reference_error,'source_radial_derivative_checks':errors,'origin_derivative_assessment':'For n=1: -3G*b/p_ref times deviator projector. For n>1: zero creep-vector derivative. Lazy generated select returns the corresponding finite branch; von Mises observable itself is nondifferentiable at zero and no norm-gradient or consistent FE tangent is approved.'}

if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
