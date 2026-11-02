"""Prospectively bounded algebra for exact VoR formulas; no author/compiled code."""
from fractions import Fraction as F
from decimal import Decimal as D, localcontext
import json

def check():
    n=0
    for q in [F(-1,4),F(0),F(1,10),F(1),F(17,3)]:
        for j in range(7):
            X=[[F(i+3*k+j+1,7) for i in range(3)] for k in range(3)]
            tr=sum(X[i][i] for i in range(3))
            Y=[[X[i][k]-(q*tr/(1+3*q) if i==k else 0) for k in range(3)] for i in range(3)]
            trY=sum(Y[i][i] for i in range(3))
            for i in range(3):
                for k in range(3):
                    assert Y[i][k]+(q*trY if i==k else 0)==X[i][k];n+=1
    # Exact chain cancellation: se/sen=ae+(1-ae)*aH;
    # aHdot yields sedot_hyd/se=(1-r)*sdot/s. Then Sdot_hyd=r*bareDs*sdot.
    for aH in [F(0),F(1,5),F(1,2),F(4,5),F(1)]:
        for sd in [F(-3),F(7)]:
            ae=F(9,10);s=F(10);g=ae+(1-ae)*aH
            f=aH if sd>0 else 1-aH;r=F(1,10)+F(9,10)*f**3
            ad=g*(1-r)*sd/(s*(1-ae))
            relse=(1-ae)*ad/g
            assert sd/s-relse==r*sd/s
    # Interior aH=[0,1] is invariant at endpoints for s>0,0<ae<1.
    assert all((a==0 and ad>=0) or (a==1 and ad<=0) for a in [0,1] for sd in [-1,1]
               for f in [F(a) if sd>0 else 1-F(a)]
               for r in [F(1,10)+F(9,10)*f**3]
               for ad in [(F(9,10)+F(1,10)*a)*(1-r)*sd])
    with localcontext() as c:
        c.prec=70
        s=D(10000000);se=D(2000000);lp=D('1.1');h=D('1e-10')
        def sat(v):return 1-(-(lp*(se/v).ln()).exp()).exp()
        S=sat(s);ana=(1-S)*lp*(1-S).ln()/s
        num=(sat(s+h)-sat(s-h))/(2*h)
        error=abs(ana-num);assert error<D('1e-40')
        # Eq27 uses |x+y| whereas A6/A8 use |x|+|y|.
        x=-D('0.001');y=D('0.001');combined=abs(x+y);separated=abs(x)+abs(y)
        assert combined==0 and separated==D('0.002')
        # Table1 thermal algebra currentT versus supplied oldT ordering witness.
        em0=D('.55');pm=D('1000000');hms=D('150000000');nm=D('.9');a=D('.118');b=D('-.0001');Tr=D(294)
        def micro(T):return em0*(-(nm*(pm/hms).ln()).exp()).exp()*(a+b*T)/(a+b*Tr)
        old=micro(Tr);current=micro(D(314));assert old!=current
        return {'status':'pass','exact_rank_inverse_components':n,'exact_scanning_chain_cases':10,'wrc_derivative_absolute_error':str(error),'mixed_internal_rate_witness':{'Dp_over_1_plus_em_per_Pa':'-0.00001','s_dot_Pa_per_s':'100','alpha_s_per_K':'0.00025','T_dot_K_per_s':'4','x_per_s':str(x),'y_per_s':str(y),'eq27_combined_abs_per_s':str(combined),'appendix_separate_abs_per_s':str(separated),'interpretation':'different nonlinear internal forcing for opposing simultaneous hydraulic/thermal effects; no full-material response claimed'},'current_temperature_algebra_witness':{'pm_Pa':str(pm),'Told_K':str(Tr),'Tnew_K':'314','em_oldT':str(old),'em_currentT':str(current),'difference':str(current-old)},'scope':'isolated independent algebra only; no backend, author code, full-model numerical qualification or scientific approval'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
