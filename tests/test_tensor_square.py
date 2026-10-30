"""Independent Cartesian matrix references for symmetric tensor square."""
import math
import os
from pathlib import Path
import random
import subprocess
import json
import unittest

from atlas.dsl import DIMS, Sym, Type, ValidationError, cpp, evaluate, infer, parse
from atlas.model import ROOT, load, interpret

SOLVER=Path(os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver'))


def matrix(v):
    r=math.sqrt(2)
    return [[v[0],v[3]/r,v[5]/r],[v[3]/r,v[1],v[4]/r],[v[5]/r,v[4]/r,v[2]]]


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mandel(a):
    return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]


def reference(v):
    a=matrix(v)
    return mandel(multiply(a,a))


def rotate(v,Q):
    return mandel(multiply(multiply(Q,matrix(v)),list(zip(*Q))))


class TensorSquareTests(unittest.TestCase):
    def assertVector(self,a,b):
        self.assertEqual(len(a),len(b))
        for got,want in zip(a,b):self.assertAlmostEqual(got,want,delta=1e-12*max(1,abs(want)))

    def test_cartesian_diagonal_shear_and_random_matrices(self):
        rng=random.Random(2004)
        vectors=[[0]*6,[1,2,-3,0,0,0],[0,0,0,math.sqrt(2)*2,0,0],[1,-2,3,.4,-.7,1.2]]
        vectors += [[rng.uniform(-3,3) for _ in range(6)] for _ in range(80)]
        for v in vectors:
            with self.subTest(v=v):
                got=evaluate(parse('tensor_square(A)'),{'A':Sym(tuple(v))})
                self.assertVector(got.v,reference(v))
                self.assertAlmostEqual(sum(got.v[:3]),sum(x*x for x in v),places=12)

    def test_oblique_rotation_covariance(self):
        v=[1,-2,3,.4,-.7,1.2]
        for axis,angle in enumerate((.37,-.63,1.12)):
            c,s=math.cos(angle),math.sin(angle)
            Q=([[1,0,0],[0,c,-s],[0,s,c]] if axis==0 else [[c,0,s],[0,1,0],[-s,0,c]] if axis==1 else [[c,-s,0],[s,c,0],[0,0,1]])
            got=evaluate(parse('tensor_square(A)'),{'A':Sym(tuple(rotate(v,Q)))})
            self.assertVector(got.v,rotate(reference(v),Q))

    def test_shape_units_arity_and_qualified_codegen(self):
        squared=tuple(2*x for x in DIMS['Pa'])
        self.assertEqual(infer(parse('tensor_square(A)'),{'A':Type('sym',DIMS['Pa'])}),Type('sym',squared))
        for expr in ('tensor_square(1)','tensor_square(A,A)','tensor_square()','A*A'):
            with self.subTest(expr=expr),self.assertRaises(ValidationError):infer(parse(expr),{'A':Type('sym')})
        # A pre-existing model name cannot shadow the generated function call.
        self.assertEqual(cpp(parse('tensor_square(A)')),'atlas::tensor_square(A)')
        with self.assertRaises(ValidationError):infer(parse('tensor_square(A) + A'),{'A':Type('sym',DIMS['Pa'])})

    def test_generated_fixture_matches_cartesian_reference(self):
        fixture=load(ROOT/'tests/fixtures/time/tensor-square.json')
        for v in ([0]*6,[1,2,-3,0,0,0],[0,0,0,math.sqrt(2)*2,0,0],[1,-2,3,.4,-.7,1.2]):
            expected=[x/2 for x in reference(v)]
            interpreted=interpret(fixture,{'A':v},{'A':v},[0]*6,time=0)['A']
            self.assertVector(interpreted.v,expected)
            command=[str(SOLVER),'--model',fixture['id'],'--mode','evaluate-time','--initial',','.join(map(str,v)),'--strain-rate','0,0,0,0,0,0','--start-time','0']
            actual=json.loads(subprocess.check_output(command,text=True))
            self.assertTrue(actual['ok']);self.assertVector(actual['values'],expected)


if __name__=='__main__':unittest.main()
