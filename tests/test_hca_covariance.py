"""Finite-set HCA covariance with separated farthest pairs; no general tie claim.

Cartesian Q T Q^T independently induces the orthonormal Mandel matrix M.
This tests an arithmetic diagnostic, not frame evolution or an HCA material.
"""
import math
import unittest
from tools.hca_diagnostics import convert_mandel, sampled_amplitude


def transpose(a):return [list(x) for x in zip(*a)]
def multiply(a,b):return [[math.fsum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def rotation():
    a,b,c=.37,-.51,.23
    ca,sa,cb,sb,cc,sc=math.cos(a),math.sin(a),math.cos(b),math.sin(b),math.cos(c),math.sin(c)
    x=[[1,0,0],[0,ca,-sa],[0,sa,ca]]
    y=[[cb,0,sb],[0,1,0],[-sb,0,cb]]
    z=[[cc,-sc,0],[sc,cc,0],[0,0,1]]
    return multiply(z,multiply(y,x))
def tensor(v):
    # Atlas Mandel order: xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz.
    a,b,c,d,e,f=v;r=math.sqrt(2)
    return [[a,d/r,f/r],[d/r,b,e/r],[f/r,e/r,c]]
def mandel(t):
    r=math.sqrt(2)
    return [t[0][0],t[1][1],t[2][2],r*t[0][1],r*t[1][2],r*t[0][2]]
def rotate(v,q):return mandel(multiply(multiply(q,tensor(v)),transpose(q)))
def induced(q):
    columns=[rotate([float(i==j) for i in range(6)],q) for j in range(6)]
    return transpose(columns)
def eigenvalues(a):
    # Independent symmetric Jacobi diagonalization; no diagnostic radii used.
    a=[r[:] for r in a]
    for _ in range(200):
        p,q=max(((i,j) for i in range(6) for j in range(i+1,6)),key=lambda ij:abs(a[ij[0]][ij[1]]))
        if abs(a[p][q])<=1e-18:break
        angle=.5*math.atan2(2*a[p][q],a[q][q]-a[p][p]);co,si=math.cos(angle),math.sin(angle)
        j=[[float(i==k) for k in range(6)] for i in range(6)]
        j[p][p]=j[q][q]=co;j[p][q]=si;j[q][p]=-si
        a=multiply(transpose(j),multiply(a,j))
    else:raise AssertionError('Jacobi eigensolver failed to converge')
    return sorted(a[i][i] for i in range(6))
def fixture():
    # Three orthonormal deviatoric Mandel axes, including Cartesian shear.
    axes=[[1/math.sqrt(2),-1/math.sqrt(2),0,0,0,0],
          [0,0,0,1,0,0],
          [1/math.sqrt(6),1/math.sqrt(6),-2/math.sqrt(6),0,0,0]]
    radii=[3e-4,1.3e-4,.4e-4]
    points=[]
    for r,d in zip(radii,axes):
        points.extend([[-r*v for v in d],[r*v for v in d]])
    # Interior points retain a nonharmonic sampled path without moving extrema.
    points.append([sum(.1*r*d[k] for r,d in zip(radii,axes)) for k in range(6)])
    return points,radii


class HCACovarianceTests(unittest.TestCase):
    def close(self,a,b,atol=2e-17):
        if isinstance(a,(list,tuple)):
            self.assertEqual(len(a),len(b))
            for x,y in zip(a,b):self.close(x,y,atol)
        else:self.assertLessEqual(abs(a-b),atol)
    def test_cartesian_rotation_induces_orthonormal_mandel_map(self):
        q=rotation();m=induced(q)
        self.close(multiply(q,transpose(q)),[[float(i==j) for j in range(3)] for i in range(3)],1e-14)
        self.close(multiply(m,transpose(m)),[[float(i==j) for j in range(6)] for i in range(6)],1e-14)
        v=[.3,-.2,.7,.4,-.6,.8]
        self.close(rotate(v,q),[r[0] for r in multiply(m,[[x] for x in v])],1e-14)
    def test_oblique_finite_set_operator_spectrum_and_norm_covariance(self):
        points,radii=fixture();q=rotation();m=induced(q)
        base=sampled_amplitude(points);turned=sampled_amplitude([rotate(p,q) for p in points])
        self.assertEqual(base['sampled_rank'],3);self.assertEqual(turned['sampled_rank'],3)
        # Unique antipodal extrema avoid an algorithmic choice between spans.
        for result in [base,turned]:
            self.close(result['radii'],radii)
            self.assertEqual([len(s['exact_tied_pairs']) for s in result['stages']],[1,1,1])
            self.assertEqual([s['selected_pair'] for s in result['stages']],[[0,1],[2,3],[4,5]])
            self.assertLess(result['discarded_radius_bound'],1e-15)
        expected=multiply(m,multiply(base['amplitude_operator'],transpose(m)))
        self.close(turned['amplitude_operator'],expected)
        spectrum=sorted([0.,0.,0.,*radii])
        self.close(eigenvalues(base['amplitude_operator']),spectrum)
        self.close(eigenvalues(turned['amplitude_operator']),spectrum)
        norm=math.hypot(*radii)
        for result in [base,turned]:
            self.close(result['epsilon_ampl'],norm)
            self.close(math.sqrt(sum(v*v for row in result['amplitude_operator'] for v in row)),norm)
    def test_rotated_source_basis_matches_atlas_operator(self):
        points,_=fixture();turned=[rotate(p,rotation()) for p in points]
        # Explicit source order xx,yy,zz,sqrt(2)xy,sqrt(2)xz,sqrt(2)yz.
        source=[p[:4]+[p[5],p[4]] for p in turned]
        for a,s in zip(turned,source):self.close(convert_mandel(s,source='source_mandel',target='atlas_mandel'),a)
        a=sampled_amplitude(turned);s=sampled_amplitude(source,basis='source_mandel')
        self.close(a['amplitude_operator'],s['amplitude_operator'])
        self.close(a['epsilon_ampl'],s['epsilon_ampl'])

if __name__=='__main__':unittest.main()
