"""Prospective test-only arithmetic context; never changes the frozen tool/module."""
import ast
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
TOOL=ROOT/'tools/check_ramberg_osgood.py'

def make_with_arithmetic(*, half_integer=True, other_power=pow):
    def reference_power(base, exponent):
        # Fixed source exponents: n=1.5 or2.5 gives n-1=.5 or1.5.
        # Specify these as elementary binary64 operations, avoiding libm pow.
        if half_integer and exponent==0.5:
            return math.sqrt(base)
        if half_integer and exponent==1.5:
            return base*math.sqrt(base)
        return other_power(base,exponent)
    class ExplicitPower(ast.NodeTransformer):
        def visit_BinOp(self,node):
            self.generic_visit(node)
            if isinstance(node.op,ast.Pow):
                return ast.copy_location(ast.Call(func=ast.Name(id='_reference_power',ctx=ast.Load()),args=[node.left,node.right],keywords=[]),node)
            return node
    tree=ast.fix_missing_locations(ExplicitPower().visit(ast.parse(TOOL.read_text())))
    context={'__name__':'ramberg_test_arithmetic_context','__file__':str(TOOL),
             'sum':math.fsum,'_reference_power':reference_power}
    exec(compile(tree,str(TOOL),'exec'),context)
    return context['make_requests']()
