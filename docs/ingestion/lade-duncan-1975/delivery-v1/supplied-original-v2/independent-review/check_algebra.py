"""Independent exact polynomial/conjugacy checks; no Atlas imports/compiled calls.

Source: supplied original1975, pp1043 (7-9),1046-47 (14-19).
Stress magnitudes here use one arbitrary consistent unit. These are algebraic
witnesses, not a stress-update oracle or experimental/numerical qualification.
"""
from fractions import Fraction as F
import json
from pathlib import Path


def tr(a): return sum(a[i][i] for i in range(3))
def det(a):
    return sum(a[0][j] * (a[1][(j+1)%3]*a[2][(j+2)%3]-a[1][(j+2)%3]*a[2][(j+1)%3]) for j in range(3))
def cof(a):
    out=[]
    for i in range(3):
        row=[]
        for j in range(3):
            ii=[k for k in range(3) if k!=i]; jj=[k for k in range(3) if k!=j]
            row.append((-1)**(i+j)*(a[ii[0]][jj[0]]*a[ii[1]][jj[1]]-a[ii[0]][jj[1]]*a[ii[1]][jj[0]]))
        out.append(row)
    return out

def mul(a,b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def trans(a): return list(map(list,zip(*a)))
def rotate(a,q): return mul(mul(q,a),trans(q))
def dot(a,b): return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def tensor_normal(a,k):
    c=cof(a); t=tr(a)
    return [[3*t*t*(i==j)-k*c[i][j] for j in range(3)] for i in range(3)]
def g(a,k): return tr(a)**3-k*det(a)
def source_stress6(a): return [a[0][0],a[1][1],a[2][2],a[1][2],a[2][0],a[0][1]]
def from_stress6(s): return [[s[0],s[5],s[4]],[s[5],s[1],s[3]],[s[4],s[3],s[2]]]
def source_flow6(a,k):
    # Direct transcription of printed Eq9, separate from cofactor implementation.
    x,y,z,yz,zx,xy=source_stress6(a); t=x+y+z
    return [3*t*t-k*y*z+k*yz*yz,3*t*t-k*z*x+k*zx*zx,3*t*t-k*x*y+k*xy*xy,
            2*k*(x*yz-xy*zx),2*k*(y*zx-xy*yz),2*k*(z*xy-yz*zx)]
def tensor_from_engineering(s):
    return [[s[0],s[5]/2,s[4]/2],[s[5]/2,s[1],s[3]/2],[s[4]/2,s[3]/2,s[2]]]
def exact_derivative(a,k,index):
    # Five-point derivative is exact for this cubic, with independent determinant evaluation.
    s=source_stress6(a)
    def at(j):
        x=s[:]; x[index]+=F(j,8)
        return g(from_stress6(x),k)
    return (at(-2)-8*at(-1)+8*at(1)-at(2))/(12*F(1,8))

q=[[F(3,5),F(-4,5),F(0)],[F(4,5),F(3,5),F(0)],[F(0),F(0),F(1)]]
a=[[F(5),F(1,2),F(1,3)],[F(1,2),F(3),F(1,4)],[F(1,3),F(1,4),F(2)]]
A=F(11,25); f=tr(a)**3/det(a); k=A*f+27*(1-A)
sf=source_flow6(a,k); n=tensor_normal(a,k); t=tensor_from_engineering(sf)
assert t==n
assert all(exact_derivative(a,k,i)==sf[i] for i in range(6))
assert sum(x*y for x,y in zip(source_stress6(a),sf))==3*g(a,k)==dot(a,t)
assert tensor_normal(rotate(a,q),k)==rotate(n,q)
wrong=from_stress6(sf)
wrong_rotated=from_stress6(source_flow6(rotate(a,q),k))
assert dot(a,wrong)!=3*g(a,k)
assert wrong_rotated!=rotate(wrong,q)
# Composing k(f) first gives g_comp=(1-A)*(I1^3-27I3), which
# has the same scalar value but a different direction from the frozen-k rule.
composed=[[(1-A)*(3*tr(a)**2*(i==j)-27*cof(a)[i][j]) for j in range(3)] for i in range(3)]
assert (1-A)*(tr(a)**3-27*det(a))==g(a,k)
assert composed!=n
assert any(composed[i][j]*n[0][0]!=n[i][j]*composed[0][0] for i in range(3) for j in range(3))
# Exact fixed-pressure inversion/derivative of Eq16.
x=F(15); aa=F(3,100); d=F(957,1000)/F(63)
W=aa*x/(1-d*x)
assert W/(aa+d*W)==x
# Differentiate W(x)=a*x/(1-d*x) algebraically via quotient rule.
assert (aa*(1-d*x)+aa*x*d)/(1-d*x)**2==aa/(1-d*x)**2
# Vary a at fixed x: algebraic W changes, while printed Eq19's df=0 gives0.
da=F(1,1000); deltaW=(aa+da)*x/(1-d*x)-W
assert deltaW==x/(1-d*x)*da and deltaW!=0
result={
 'kind':'independent-exact-algebra-witnesses-not-model-qualification',
 'source_equations':'7-9,14-19; printed pp1043,1046-1047',
 'checks':{'six_independent_stress_derivatives_match_eq9':'pass, exact five-point cubic derivative',
 'engineering_shear_mapping_to_tensor_gradient':'pass, exact rational equality',
 'source_vector_work_equals_tensor_work_equals_3g':'pass, exact rational equality',
 'mapped_flow_rotation_covariance':'pass, rational orthogonal rotation',
 'unmapped_shear_as_tensor_counterexample':'retained: fails work and rotation covariance',
 'substitute_kappa_before_derivative_counterexample':'retained: same g value, different nonparallel flow',
 'fixed_a_hyperbola_inversion_derivative':'pass, exact rational equality',
 'variable_a_constant_f_counterexample':'retained: algebraic W changes while Eq19 gives zero'},
 'witness':{'stress6_order':'xx,yy,zz,yz,zx,xy','stress6':[str(v) for v in source_stress6(a)],
 'A':str(A),'f':str(f),'kappa2':str(k),'correct_work':str(dot(a,t)),
 'incorrect_tensor_shear_work':str(dot(a,wrong)),'fixed_f_da':str(da),'algebraic_W_change':str(deltaW),'eq19_W_change':'0'},
 'limitations':['No Atlas functions imported','No production candidate tested','No compiled execution','Not a frozen finite-path reference','No experimental comparison']}
if __name__=='__main__':
    output=Path(__file__).with_name('algebra-results.json')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
