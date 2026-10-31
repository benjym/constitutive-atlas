"""Independent Decimal spherical algebra review, no Atlas/oracle/solver imports."""
from decimal import Decimal,localcontext
from pathlib import Path
import json,hashlib,argparse
D=Decimal

def run(root):
    study=root/'catalogue/investigations/clay2013-preview-v1';modelpath=study/'models/hypoplastic-clay-2013.json'
    model=json.loads(modelpath.read_text());parameters={k:D.from_float(float(v['default'])) for k,v in model['parameters'].items()}
    recorded=json.loads((study/'default-diagnostics-v1/analytical-bound.json').read_text())
    # Exact equation strings are inspected here to bind the algebra's sign/rate selection.
    expr={d['name']:d['expr'] for d in model['derived']}
    assert expr['Ad']=='fs*Ld-(sigma/lambda_star)*trace(d)'
    assert expr['stress_rate']=='fs*(de+c*trace(de)*I)+(fd/fdA)*Ad*norm(de)'
    assert expr['fdA']=='4*(1-fm)**(2/omega)'
    assert model['equations']['e']=='e_rate'
    rows=[]
    with localcontext() as ctx:
        ctx.prec=90;one=D(1);two=D(2);three=D(3);lam=parameters['lambda_star'];kap=parameters['kappa_star'];nu=parameters['nu'];N=parameters['N'];pref=parameters['p_ref'];e=D.from_float(.8)
        assert 0<kap<lam and -one<nu<one/two and 0<parameters['phi_c']<D('1.5707963267948966')
        pe=pref*((N-(one+e).ln())/lam).exp();c=nu/(one-two*nu)
        for pressure in (10000,100000):
            p=D(pressure);fs=three*p/two*(one/lam+one/kap)*(one-two*nu)/(one+nu)
            A=fs*c;B=fs*(one+two*c)
            C=(p/pe)**2*(three*p/two)*(one/kap-one/lam)/three.sqrt()
            literalC=((two*p/pe)**2)/4*(fs*(one+three*c)-three*p/lam)/three.sqrt()
            assert abs(C-literalC)<D('1e-75')
            assert abs(A-nu*B)<D('1e-75')
            r=lambda t:A+B*t-C*(one+two*t*t).sqrt()
            concavity=lambda t:-two*C/(one+two*t*t)**(D(3)/two)
            assert all(concavity(D(t))<0 for t in [-100,-1,0,1,100])
            delta=C*C-B*B/two
            row={'pressure':pressure,'pe_decimal':str(pe),'A_decimal':str(A),'B_decimal':str(B),'C_decimal':str(C),'delta_decimal':str(delta),'strict_finite_maximum_condition':bool(C>abs(B)/two.sqrt())}
            expected=next(x for x in recorded['coefficients'] if x['pressure']==pressure)
            for name,value in [('A',A),('B',B),('C',C)]:assert abs(value-D.from_float(expected[name]))<=D('1e-13')*max(one,abs(value)),name
            if delta>0:
                maxcoef=A-delta.sqrt();tstar=B/(two*delta.sqrt())
                assert abs(r(tstar)-maxcoef)<D('1e-74')
                assert abs(B-two*C*tstar/(one+two*tstar*tstar).sqrt())<D('1e-74')
                # Concavity + unique stationary point proves global maximum;
                # probes only check the independent implementation of that formula.
                assert all(r(tstar+D(k))<=maxcoef+D('1e-74') for k in [-100000,-100,-1,0,1,100,100000])
                assert maxcoef<0
                assert abs(maxcoef-D.from_float(expected['maximum_radial_rate_per_axial_rate']))<=D('1e-13')*abs(maxcoef)
                row.update(maximum_coefficient_decimal=str(maxcoef),maximizing_y_over_x_decimal=str(tstar),no_zero_radial_tangent_for_positive_x=True)
            else:
                assert B>two.sqrt()*C
                qden=B*B-two*C*C
                t=(-A*B+C*(B*B+two*A*A-two*C*C).sqrt())/qden
                assert A+B*t>0 and abs(r(t))<D('1e-74')
                row.update(unique_zero_radial_tangent_y_over_x_decimal=str(t),radial_tangent_residual_decimal=str(r(t)),no_zero_radial_tangent_for_positive_x=False)
            rows.append(row)
    return {'version':'clay2013-independent-default-control-review-v1','pass':True,'precision':90,'model_sha256':hashlib.sha256(modelpath.read_bytes()).hexdigest(),'rows':rows,'scope':'initial spherical rate specialization and concave maximization only','compiled_calls':0,'material_oracle_replays':0,'finite_endpoint_root_claim':False,'general_initial_admissibility_claim':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path);args=ap.parse_args();result=run(args.root);text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(text)
    print(text,end='')
