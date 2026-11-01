"""Independent endpoint invariants of retained reference results; no runtime."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'references-v2.json'
# Freeze tolerances before first run. Endpoint checks do not verify trajectories.
ALGEBRA_GATE=D('1e-35')
KINEMATICS_GATE=D('1e-10')
data=json.loads(SOURCE.read_text())
rows=[]
with localcontext() as ctx:
    ctx.prec=70
    for case in data['cases']:
        r=case['reference'];o=r['outputs'];N=D(case['N']);M=D('1.2')
        p=D(o['mean_pressure']);q=D(o['deviatoric_stress']);pi=D(o['image_pressure'])
        eta=D(o['eta']);e=D(o['e']);ev=D(o['ev']);eq=D(o['eq'])
        C=D(r['controls_end']['pressure_control']);K=D(r['controls_end']['stress_ratio_control'])
        eta_yield=M/N*(1+(N-1)*((p/pi).ln()*N/(1-N)).exp()) if N else M*(1+(pi/p).ln())
        algebra=max(abs(eta-eta_yield),abs(q-p*eta)/D(130000),abs(p-K*q-C)/D(130000),abs(eq-D('.16')))
        kinematics=abs((1+e)*ev.exp()/(1+D(r['initial_state']['e']))-1)
        assert algebra<ALGEBRA_GATE,(case['id'],algebra)
        assert kinematics<KINEMATICS_GATE,(case['id'],kinematics)
        rows.append(dict(id=case['id'],algebra_error=str(algebra),kinematic_invariant_relative=str(kinematics)))
result=dict(scope='retained independent reference endpoint algebra and kinematics only',passed=True,cases=len(rows),algebra_gate=str(ALGEBRA_GATE),kinematics_gate=str(KINEMATICS_GATE),reference_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows)
(HERE/'reference-endpoint-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,cases=len(rows),max_algebra_error=max(float(r['algebra_error']) for r in rows),max_kinematic_invariant=max(float(r['kinematic_invariant_relative']) for r in rows)),indent=2))
