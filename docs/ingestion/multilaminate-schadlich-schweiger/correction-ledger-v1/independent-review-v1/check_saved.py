#!/usr/bin/env python3
"""Independent saved-byte/algebra audit; standard library, no Atlas imports or evaluators."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = 'docs/ingestion/multilaminate-schadlich-schweiger/correction-ledger-v1'

def need(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def near(x, y):
    need(abs(x-y) <= 1e-12 * max(1, abs(x), abs(y)), f'{x!r} != {y!r}')

def audit(root, private_pdf=None):
    manifest = json.loads((HERE/'manifest.json').read_text())
    for group in ('inputs', 'outputs'):
        for entry in manifest[group]:
            path = root/entry['path'] if group == 'inputs' else HERE/entry['path']
            need(sha(path) == entry['sha256'], f'binding changed: {path}')
    original = json.loads((root/BASE/'manifest.json').read_text())
    closure = 0
    for key, digest in original['payload'].items():
        need(sha(root/BASE/key) == digest, f'original payload changed: {key}')
        closure += 1
    for key, digest in original['inputs'].items():
        need(sha(root/key) == digest, f'original input changed: {key}')
        closure += 1
    ledger = json.loads((root/BASE/'ledger.json').read_text())
    decision = json.loads((HERE/'decision.json').read_text())
    need([p['id'] for p in ledger['patches']] == [f'PATCH-{i:02}' for i in range(1,9)], 'patch identity')
    need(all(p['status'] == 'proposed_unapproved' and p['scientific_reviewer'] is None for p in ledger['patches']), 'historical status mutated')
    need([p['id'] for p in decision['patches']] == [p['id'] for p in ledger['patches']], 'decision coverage')
    need(decision['full_model_admission'] is False and decision['executable_authorization'] is False, 'scope changed')
    need(len(decision['remaining_gates']) == 7, 'remaining gates lost')
    private = 'not_requested; source inspection receipt is hash-bound'
    if private_pdf:
        need(sha(Path(private_pdf)) == manifest['private_primary']['sha256'], 'primary PDF mismatch')
        private = 'PASS exact primary PDF identity'
    groups = []
    # 01: additive compliance, domain and preserved PLUS counterexample.
    rows = []
    for eur, expected_k in [(3000, F(75)), (1800, None), (1500, F(-150))]:
        ce, ct = (1-2*F(1,5))/eur, F(1,3000)
        cp = ct-ce
        km = 1/(100*cp) if cp else None
        kp = 1/(100*(ct+ce))
        need(km == expected_k, 'minus hardening witness')
        need(ce + 1/(100*kp) == ct+2*ce, 'PLUS failure identity')
        if km:
            need(ce+1/(100*km) == ct, 'minus additive identity')
        rows.append({'Eur':eur,'Ce':str(ce),'Ct':str(ct),'Cp':str(cp),'Kminus':str(km),'Kplus':str(kp),'Ct_plus':str(ct+2*ce)})
    need(F(3000)>3*(1-2*F(1,5))*1000, 'strict hardening domain')
    groups.append({'patch':'PATCH-01','result':'PASS conditional additive law; equality and negative compliance retained','witnesses':rows})
    # 02: shape invariant under root sign, convention selects negative root.
    sn, tau, mc = F(-60), F(48), F(3,5)
    q2 = sn*sn + tau*tau/(mc*mc)
    need(q2 == 10000, 'cap magnitude')
    for intercept in (-100,100):
        need(sn*sn/F(intercept**2)+tau*tau/(mc*mc*intercept**2)-1 == 0, 'squared cap root invariance')
    groups.append({'patch':'PATCH-02','result':'PASS Q=100, signed compressive intercept=-100; squared yield also admits +100'})
    # 03: explicit new magnitude interface, not legacy encoding inference.
    sv, pop, k0 = F(-100), F(40), F(1,2)
    pv, ph = sv-pop, k0*(sv-pop)
    need((pv,ph)==(-140,-70) and -pv == -sv+pop, 'POP magnitude conversion')
    need(sv+(-pop)==pv and sv+pop != pv, 'legacy signed increment distinguished')
    groups.append({'patch':'PATCH-03','result':'PASS explicit P>=0 mapping; signed historical POP can express a different input contract'})
    # 04: independent two-dimensional spectral reconstruction and angle ordering.
    cases = [(1.,-.2,2.), (2.,-.2,1.), (1.,0.,2.), (2.,0.,1.), (1.,.3,1.), (1.,-.3,1.)]
    max_error = 0.
    for a,b,d in cases:
        delta=math.hypot(a-d,2*b)
        lo,hi=(a+d-delta)/2,(a+d+delta)/2
        p=[[.5*(1-(a-d)/delta), -b/delta],[-b/delta,.5*(1-(d-a)/delta)]]
        h=[[a,b],[b,d]]
        for i in range(2):
            for j in range(2):
                near(sum(p[i][k]*p[k][j] for k in range(2)),p[i][j])
                v=lo*p[i][j]+hi*((1 if i==j else 0)-p[i][j])
                near(v,h[i][j]); max_error=max(max_error,abs(v-h[i][j]))
        w=math.atan2(-2*b,d-a)/2
        low=[math.cos(w),math.sin(w)]
        high=[math.cos(math.atan2(2*b,a-d)/2),math.sin(math.atan2(2*b,a-d)/2)]
        for i in range(2):
            near(sum(h[i][j]*low[j] for j in range(2)),lo*low[i])
            near(sum(h[i][j]*high[j] for j in range(2)),hi*high[i])
    # Original A2 failure in a valid positive-definite block from Eq94.
    eh,ev,nhh,nhv=20.,10.,.2,.1
    a,d,b=(1-nhh)/eh,1/ev,-math.sqrt(2)*nhv/eh
    literal=.5*math.atan((-2*math.sqrt(2)*nhv/ev)/(a+d))
    v=[math.cos(literal),math.sin(literal)]
    hv=[a*v[0]+b*v[1],b*v[0]+d*v[1]]
    need(abs(hv[0]*v[1]-hv[1]*v[0])>1e-5, 'literal A2 unexpectedly eigenvector')
    need(math.hypot(1.-1.,0.)==0., 'repeated block fixture')
    groups.append({'patch':'PATCH-04','result':'PASS six nonrepeated cases including zero coupling and equal diagonal; literal A2 fails; Delta=0 deliberately has no individual projector','max_reconstruction_error':max_error})
    # 05: raw symmetric traction needs the shear factor two.
    n=[F(-2,3),F(2,3),F(1,3)]
    need(sum(x*x for x in n)==1, 'unit normal')
    raw=2*n[0]*n[2]
    need(raw==F(-4,9) and n[0]*n[2]==F(-2,9), 'xz traction witness')
    groups.append({'patch':'PATCH-05','result':'PASS exact -4/9 raw tensor traction versus literal -2/9'})
    # 06: global work identity and traction maps; similarity is not local Euclidean work.
    sig=[1.,2.,3.,4.,5.,6.]; eng=[.1,.2,.3,.4,.5,.6]
    m=[1.,1.,1.,math.sqrt(2),math.sqrt(2),math.sqrt(2)]
    sk=[m[i]*sig[i] for i in range(6)]; ek=[eng[i]/m[i] for i in range(6)]
    near(sum(sig[i]*eng[i] for i in range(6)),sum(sk[i]*ek[i] for i in range(6)))
    pr=[float(n[0]**2),float(n[1]**2),float(n[2]**2),float(2*n[0]*n[1]),float(2*n[1]*n[2]),float(2*n[0]*n[2])]
    near(sum(pr[i]*sig[i] for i in range(6)),sum(pr[i]/m[i]*sk[i] for i in range(6)))
    # P=diag(2,1), C=diag(1,3), sigma=(1,1): both vectors transformed by P.
    need(2*2+1*3==7 and 1+3==4 and F(1,4)*2*2+1*3==4, 'nonorthogonal work metric witness')
    # A non-axis coordinate-plane direction still gives a zero t-normal-stress row.
    normal=[F(3,5),F(4,5),F(0)]; tangent=[F(0),F(0),F(1)]
    need(all(normal[i]*tangent[i]==0 for i in range(3)), 'singular projection witness')
    groups.append({'patch':'PATCH-06','result':'PASS global Kelvin work and traction maps; nonorthogonal similarity needs a metric (Euclidean work 7 vs global 4); coordinate-plane singularity retained'})
    # 07: explicitly distinct reciprocal interpolation choices.
    z=F(1,2); eh=20*(1-z)+5*z; ev=10*(1-z)+5*z
    nhv=F(1,10)*(1-z)+F(1,5)*z
    listing=nhv*ev/eh
    figure=F(1,20)*(1-z)+F(1,5)*z
    need(listing==F(9,100) and figure==F(1,8) and listing != figure, 'Poisson lineage difference')
    need(nhv/eh==listing/ev, 'reciprocity')
    groups.append({'patch':'PATCH-07','result':'PASS reciprocal listing nu_vh=9/100 versus figure nu_vh=1/8 at same midpoint; no pathwise positivity certification'})
    # 08: local intersection, positive ratio and degenerate branch.
    p,qe,tcs=F(60),F(80),F(4,5)
    bc=p*tcs/qe
    need(bc==F(3,5) and (p*tcs)/(-qe)==-bc and (-p)*tcs/(-qe)==bc, 'C5 signed ratios')
    for te in (F(0),F(1,2),tcs,F(1)):
        f=p*tcs-p*te-bc*(1-te/tcs)*qe
        factor=(tcs-te)*(p-bc*qe/tcs)
        need(f==factor==0, 'Hvorslev local factorization')
    need(p*tcs-p*tcs-999*(1-tcs/tcs)*qe==0, 'B cancels at equal angles')
    # Equivalent pressure with s=1/2, A=1/2, Q=100, p=64: qe=81.
    q,p2,a,s=100.,64.,.5,.5
    qeq=(q**s+a*(p2**s-q**s))**(1/s)
    near(qeq,81.)
    groups.append({'patch':'PATCH-08','result':'PASS exact nondegenerate factorization and sign; te=tcs leaves B undetermined; equivalent-pressure power witness qe=81'})
    return {'task':'REVIEW-multilaminate-patches-v1','status':'PASS','input_bindings':len(manifest['inputs']),'output_bindings':len(manifest['outputs']),'original_closure_bindings':closure,'private_primary':private,'algebra_groups':groups,'execution':{'Atlas_imports':0,'model_calls':0,'author_code_calls':0,'compiled_calls':0,'builds':0},'scope':'eight conditional patches only; no full-model admission'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=None)
    parser.add_argument('--private-pdf',type=Path)
    args=parser.parse_args()
    print(json.dumps(audit(args.root if args.root is not None else HERE.parents[4],args.private_pdf),indent=2,ensure_ascii=False))
