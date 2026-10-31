#!/usr/bin/env python3
"""Independent exact arithmetic for Wu/Bauer Eq21 versus Appendix I.
No Atlas imports, numerical integration, compilation, or corrected source adoption.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import random

PAIRS=((0,0),(1,1),(2,2),(0,1),(0,2),(1,2))
WEIGHTS=(1,1,1,2,2,2)

def matrix(v):
    out=[[F(0) for _ in range(3)] for _ in range(3)]
    for x,(i,j) in zip(v,PAIRS):
        out[i][j]=out[j][i]=F(x)
    return out

def vec(a):
    return [a[i][j] for i,j in PAIRS]

def product(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def eq21_linear(s,d,c1,c2):
    a,b=matrix(s),matrix(d)
    p=sum(a[i][i] for i in range(3))
    contraction=sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
    return vec([[c1*p*b[i][j]+c2*contraction*a[i][j]/p for j in range(3)] for i in range(3)])

def eq21_nonlinear_coefficient(s,c3,c4):
    a=matrix(s)
    p=sum(a[i][i] for i in range(3))
    dev=[[a[i][j]-(p/3 if i==j else 0) for j in range(3)] for i in range(3)]
    aa,dd=product(a,a),product(dev,dev)
    return vec([[(c3*aa[i][j]+c4*dd[i][j])/p for j in range(3)] for i in range(3)])

def appendix_n_over_norm(s,c3,c4):
    # Literal six printed N formulas (PDF28,p860), factored by norm(D).
    a,b,c,d,e,f=map(F,s)
    p=a+b+c
    x,y,z=a-p/3,b-p/3,c-p/3
    return [-(c3*(a*a+d*d+e*e)+c4*(d*d+e*e+x*x))/p,
            -(c3*(d*d+b*b+f*f)+c4*(d*d+f*f+y*y))/p,
            -(c3*(e*e+f*f+c*c)+c4*(e*e+f*f+z*z))/p,
            -(c3*(a*d+d*b+e*f)+c4*(e*f+d*x+d*y))/p,
            -(c3*(a*e+d*f+e*c)+c4*(d*f+e*x+e*z))/p,
            -(c3*(d*e+b*f+f*c)+c4*(d*e+f*y+f*z))/p]

def appendix_upper(s,c1,c2):
    # Literal 21 expressions, including apparent errors; tensor shear order12,13,23.
    a,b,c,d,e,f=map(F,s)
    p=a+b+c
    return {(0,0):c2*a*a/p+c1*p,(0,1):c2*a*b/p,(0,2):c2*a*c/p,
            (0,3):2*c2*a*d/p,(0,4):2*c2*a*f/p,(0,5):2*c2*a*f/p,
            (1,1):c2*b*b/p+c1*p,(1,2):c2*b*c/p,(1,3):2*c2*d*b/p,
            (1,4):2*c2*e*b/p,(1,5):2*c2*b*f/p,
            (2,2):c2*c*c/p+c1*p,(2,3):2*c2*d*c/p,(2,4):2*c2*e*c/p,(2,5):2*c2*f*c/p,
            (3,3):2*c2*d*d/p+c1*p,(3,4):2*c2*d*e/p,(3,5):2*c2*d*f/p,
            (4,4):2*c2*e*a/p+c1*p,(4,5):2*c2*e*f/p,(5,5):2*c2*f*f/p+c1*p}

def raw_derived(s,c1,c2):
    s=list(map(F,s)); p=sum(s[:3])
    return [[(c1*p if i==j else 0)+c2*s[i]*s[j]*WEIGHTS[j]/p for j in range(6)] for i in range(6)]

def tag(i,j): return f'L{i+1}{j+1}'

def serial(v):
    if isinstance(v,F): return str(v)
    if isinstance(v,dict): return {str(k):serial(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [serial(x) for x in v]
    return v

def run():
    rng=random.Random(199412)
    counts={'cases':0,'raw_linear_basis_components':0,'nonlinear_components':0,'metric_symmetry_entries':0,'norm_metric_cases':0}
    expected_errors={'L15','L55'}
    for _ in range(200):
        s=[F(rng.randint(-50,50)) for _ in range(6)]
        if sum(s[:3])==0: s[0]+=1
        c1,c2,c3,c4=map(F,(-2,-3,-5,7))
        derived=raw_derived(s,c1,c2)
        literal=appendix_upper(s,c1,c2)
        unexpected=[tag(i,j) for (i,j),v in literal.items() if v!=derived[i][j] and tag(i,j) not in expected_errors]
        assert not unexpected, unexpected
        for j in range(6):
            d=[F(int(k==j)) for k in range(6)]
            assert eq21_linear(s,d,c1,c2)==[derived[i][j] for i in range(6)]
            counts['raw_linear_basis_components']+=6
        n=appendix_n_over_norm(s,c3,c4)
        assert [-x for x in n]==eq21_nonlinear_coefficient(s,c3,c4)
        counts['nonlinear_components']+=6
        for i in range(6):
            for j in range(6):
                assert WEIGHTS[i]*derived[i][j]==WEIGHTS[j]*derived[j][i]
                counts['metric_symmetry_entries']+=1
        d=[F(rng.randint(-9,9)) for _ in range(6)]
        dm=matrix(d)
        assert sum(x*x*w for x,w in zip(d,WEIGHTS))==sum(dm[i][j]**2 for i in range(3) for j in range(3))
        counts['norm_metric_cases']+=1
        counts['cases']+=1
    s=list(map(F,(11,7,5,2,3,4)))
    derived=raw_derived(s,F(-2),F(-3)); printed=appendix_upper(s,F(-2),F(-3))
    witnesses={tag(i,j):{'printed':v,'eq21':derived[i][j]} for (i,j),v in printed.items() if v!=derived[i][j]}
    assert set(witnesses)==expected_errors
    # Normal/shear symmetry counterexample, independent of the two entry defects.
    assert printed[(0,3)]==2*derived[3][0] and printed[(0,3)]!=derived[3][0]
    # Exact specialization vi=vf=0,Rf=3,Ei/sigma3=3 of printed Eqs25--29.
    c2,c3=F(25,8),F(-25,8)
    c4=-9*(25+(3-1)*3*(-3)*c2)/(1*(3-1)**2*(3**2-4))
    mat=[[F(3),F(1,3),F(-1,3),F(0)],
         [F(0),F(-1),F(1),F(0)],
         [F(-25),F(-9),F(9),F(16,9)],
         [F(0),F(-3),F(1),F(4,9)]]
    rhs=[F(3),F(0),F(0),F(0)]
    literal_coeff=[F(1),c2,c3,c4]
    residual=[sum(a*b for a,b in zip(row,literal_coeff))-r for row,r in zip(mat,rhs)]
    assert residual==[F(25,12),F(-25,4),F(-225,4),F(-25,4)]
    # This candidate only solves the printed matrix; it is not an adopted converter.
    matrix_solution=[F(1),F(25,8),F(25,8),F(225,16)]
    assert [sum(a*b for a,b in zip(row,matrix_solution))-r for row,r in zip(mat,rhs)]==[0]*4
    friction=[]
    for ratio in (2,3,5,10):
        literal=F(ratio+1,ratio-1)
        geometric=F(ratio-1,ratio+1)
        assert literal>1 and 0<geometric<1 and literal*geometric==1
        friction.append({'Rf':ratio,'printed_arcsin_argument':literal,'mohr_circle_candidate_argument':geometric})
    return serial({'version':'wu-bauer-1994-appendix-I-exact-v1','status':'bounded-diagnostics-pass-with-retained-source-conflicts',
      'arithmetic':'stdlib fractions.Fraction; no Atlas imports', 'counts':counts,
      'upper_entries':21,'upper_agreement_for_generic_witness':19,
      'retained_entry_conflicts':witnesses,
      'raw_symmetry_witness':{'L14':derived[0][3],'L41':derived[3][0]},
      'calibration':{'vi':0,'vf':0,'Rf':3,'Ei_over_sigma3':3,'printed_coefficients':literal_coeff,
                     'printed_eq25_residual':residual,'printed_matrix_solution_candidate':matrix_solution,
                     'candidate_adopted':False},
      'friction_argument_witnesses':friction,
      'scientific_admission':False,'compiled_or_executed_cpp':False,
      'scope_exclusions':['canonical signs','corrected implementation selection','finite integration','source figure reproduction','experimental validation','independent scientific review']})

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
