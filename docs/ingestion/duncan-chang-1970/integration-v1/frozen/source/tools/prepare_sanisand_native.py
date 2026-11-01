"""Prepare one standalone C++/AD check; never compile or execute native code.

Run with an output directory, then compile and run the emitted fixture separately.
Derivatives cover strain columns at fixed admissible on-cone state and branch;
they are not a finite-step constitutive tangent.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.dsl import Sym, cpp, parse
from tools.inspect_sanisand_limit import load_fragment, evaluate_fragment


def state(direction, distance, sign):
    length = sum(v*v for v in direction)**.5
    n = [v/length for v in direction]
    radius = (2/3)**.5*.01
    alpha = [.15*v for v in n]
    return dict(sigma=Sym(tuple(1e5*(alpha[i]+radius*n[i]+(1 if i<3 else 0)) for i in range(6))),
                alpha=Sym(tuple(alpha)), alpha_in=Sym(tuple(a-distance*v for a,v in zip(alpha,n))),
                z=Sym(tuple(-.4*v for v in n)), e=.7,
                d_epsilon=Sym(tuple(sign*(1e-4*v+(1e-5 if i<3 else 0)) for i,v in enumerate(n))))


def flatten(result, fragment):
    return [v for term in fragment['terms'] for v in
            (result[term['name']].v if term['shape']=='sym' else (result[term['name']],))]


def prepare(output):
    fragment = load_fragment()
    lines = ['#include "atlas/tensor.hpp"', '#include <iostream>',
             '#include <stdexcept>', 'using namespace atlas;',
             'template<class T> std::vector<T> evaluate(const std::vector<T>& x) {',
             'const auto I=identity<T>();']
    offset = 0
    for name, spec in fragment['inputs'].items():
        if spec['shape']=='sym':
            lines.append(f'const auto {name}=tensor_from(x,{offset});')
            offset += 6
        else:
            lines.append(f'const T {name}=x.at({offset});')
            offset += 1
    for term in fragment['terms']:
        lines.append(f"const auto {term['name']}={cpp(parse(term['expression']))};")
    lines.append('std::vector<T> out;')
    for term in fragment['terms']:
        name = term['name']
        lines.append(f'for(const auto& v:{name}.v) out.push_back(v);' if term['shape']=='sym' else f'out.push_back({name});')
    lines += ['return out;}',
              'void near(double got,double expected,double atol,double rtol) {',
              'if(!std::isfinite(got)||std::abs(got-expected)>atol+rtol*std::abs(expected))',
              'throw std::runtime_error("value or strain derivative mismatch");}',
              'int main(){try{std::size_t values=0,derivatives=0;']
    count = 0
    for direction in ([2,-1,-1,0,0,0], [-2,1,1,0,0,0], [.4,-.1,-.3,.7,-.2,.1]):
        for distance in (0., .03):
            for sign in (-1,1):
                supplied = state(direction, distance, sign)
                result = evaluate_fragment(fragment, **supplied)
                expected = flatten(result, fragment)
                deriv = []
                # The dependence on strain is piecewise linear. These perturbations
                # preserve the state and loading/dilatancy branches for every case.
                for j in range(6):
                    variants = []
                    for delta in (-1e-8, 1e-8):
                        strain = list(supplied['d_epsilon'].v)
                        strain[j] += delta
                        modified = dict(supplied, d_epsilon=Sym(tuple(strain)))
                        other = evaluate_fragment(fragment, **modified)
                        assert (other['scaled_loading_index']>0)==(result['scaled_loading_index']>0)
                        assert (other['D']>0)==(result['D']>0)
                        variants.append(flatten(other, fragment))
                    deriv.append([(b-a)/2e-8 for a,b in zip(*variants)])
                inputs = [v for name,spec in fragment['inputs'].items() for v in
                          (supplied[name].v if spec['shape']=='sym' else (supplied.get(name,spec.get('default')),))]
                strain_offset = 0
                for name,spec in fragment['inputs'].items():
                    if name=='d_epsilon': break
                    strain_offset += 6 if spec['shape']=='sym' else 1
                array = lambda xs: '{'+','.join(repr(float(v)) for v in xs)+'}'
                lines += ['{', 'const std::vector<double> x='+array(inputs)+';',
                          'const std::vector<double> expected='+array(expected)+';',
                          'const std::vector<double> fd='+array([v for column in deriv for v in column])+';',
                          'const auto actual=evaluate(x); std::vector<Jet> seed;',
                          'for(double v:x) seed.emplace_back(v);',
                          f'for(int j=0;j<6;++j) seed[{strain_offset}+j].d[j]=1.;',
                          'const auto ad=evaluate(seed);',
                          'for(std::size_t k=0;k<actual.size();++k){',
                          'near(actual[k],expected[k],1e-8,2e-10);',
                          'near(ad[k].v,expected[k],1e-8,2e-10); values+=2;',
                          'for(int j=0;j<6;++j){near(ad[k].d[j],fd[j*actual.size()+k],1e-7,2e-7);++derivatives;}}', '}']
                count += 1
    lines += [f'std::cout<<"{count} cases: "<<values<<" values and "<<derivatives<<" strain derivatives passed\\n";',
              'return 0;}catch(const std::exception& e){std::cerr<<e.what()<<"\\n";return 1;}}']
    output.mkdir(parents=True, exist_ok=True)
    fixture = output/'sanisand_algebra.cpp'
    fixture.write_text('\n'.join(lines)+'\n')
    paths = ['catalogue/source-audits/sanisand-2004-hardening-limit.json',
             'catalogue/source-audits/sanisand-2004-original-equations.json',
             'tools/inspect_sanisand_limit.py', 'tools/inspect_sanisand_original.py',
             'tools/prepare_sanisand_native.py', 'atlas/dsl.py', 'cpp/include/atlas/tensor.hpp']
    manifest = dict(kind='prepared-native-algebra-check', cases=count,
                    scope='On-cone algebra and six strain columns at fixed state; no finite integration or state tangent.',
                    sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                    fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest())
    (output/'preparation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Prepared {fixture}; no compilation or native execution performed.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    prepare(parser.parse_args().output)
