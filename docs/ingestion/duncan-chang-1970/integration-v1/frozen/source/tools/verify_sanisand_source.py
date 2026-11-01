"""Execute pinned, locally supplied SANISAND functions against Cartesian algebra.

No OpenSees code is downloaded, vendored or linked into Atlas. The temporary
harness substitutes vector storage and class context; it is not full OpenSees.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('Macauley', 'g', 'GetTrace', 'GetDevPart', 'SingleDot',
           'DoubleDot2_2_Contr', 'DoubleDot2_2_Cov', 'DoubleDot2_2_Mixed',
           'GetNorm_Contr', 'GetNorm_Cov', 'ToContraviant', 'ToCovariant',
           'GetF', 'GetPSI', 'GetLodeAngle', 'GetElasticModuli',
           'GetNormalToYield', 'GetStateDependent')
PARAMETERS = ('G0', 'nu', 'e_init', 'Mc', 'c', 'lambda_c', 'e0', 'ksi',
              'P_atm', 'm', 'h0', 'ch', 'nb', 'A0', 'nd', 'z_max', 'cz')
SCALARS = ('K', 'G', 'F', 'psi', 'cos3', 'h', 'aB', 'aD', 'b0', 'A', 'D', 'B', 'C')
NAMES = (list(SCALARS) + [f'{name}[{i}]' for name in ('n', 'b', 'd', 'R', 'sym_product') for i in range(6)]
         + ['norm_contr', 'norm_cov', 'dot_contr', 'dot_cov', 'dot_mixed']
         + [f'{name}[{i}]' for name in ('covariant', 'contravariant') for i in range(6)])
# Fixed before running the source comparison. Large near-singular h values are
# assessed relatively; each scalar/component is retained in the report.
RTOL, ATOL = 2e-9, 2e-10


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_methods(source):
    # Preserve exact selected text, including comments. Mask lexical tokens only
    # for brace counting so braces inside comments/strings cannot end a method.
    result = []
    for name in METHODS:
        pattern = rf'(double|Vector|void)\s+ManzariDafalias::{name}\s*\(([^)]*)\)'
        matches = []
        for match in re.finditer(pattern, source):
            if name == 'GetElasticModuli' and len(match[2].split(',')) != 4:
                continue
            # Start at this signature: unrelated commented-out source may contain
            # malformed literals or nested comment markers before the method.
            masked = source[:match.end()] + re.sub(
                r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',
                lambda m: re.sub(r'[^\n]', ' ', m.group()), source[match.end():])
            brace = masked.find('{', match.end())
            depth, end = 1, brace+1
            while depth and end < len(source):
                depth += (masked[end] == '{') - (masked[end] == '}')
                end += 1
            if depth or brace < 0:
                raise ValueError(f'Unclosed method: {name}')
            matches.append(dict(name=name, declaration=f'{match[1]} {name}({match[2]});',
                                text=source[match.start():end],
                                first_line=source.count('\n', 0, match.start())+1,
                                last_line=source.count('\n', 0, end)+1))
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one selected method: {name}, found {len(matches)}')
        result.extend(matches)
    return result


# Original adapter code. Source methods and complete notices are inserted only
# into a private temporary translation unit, never into the repository.
HARNESS = r'''
#include <cmath>
#include <iostream>
#include <iomanip>
#include <vector>
#define opserr std::cerr
#define endln std::endl
class Vector {
    std::vector<double> data;
public:
    explicit Vector(int n):data(n,0.){}
    int Size()const{return int(data.size());}
    double& operator()(int i){return data.at(i);}
    double operator()(int i)const{return data.at(i);}
    void Zero(){for(auto& x:data)x=0;}
    Vector& operator+=(const Vector& v){for(int i=0;i<Size();++i)data[i]+=v(i);return *this;}
    Vector& operator-=(const Vector& v){for(int i=0;i<Size();++i)data[i]-=v(i);return *this;}
    Vector& operator*=(double x){for(auto& v:data)v*=x;return *this;}
    Vector& operator/=(double x){for(auto& v:data)v/=x;return *this;}
};
Vector operator+(Vector a,const Vector& b){return a+=b;}
Vector operator-(Vector a,const Vector& b){return a-=b;}
Vector operator*(Vector a,double x){return a*=x;}
Vector operator*(double x,Vector a){return a*=x;}
Vector operator/(Vector a,double x){return a/=x;}
class ManzariDafalias {
public:
    double one3=1./3.,two3=2./3.,root23=std::sqrt(2./3.),small=1e-10;
    double m_Pmin,m_Presidual;
    int mElastFlag=1;
    Vector mI1{6};
    {{FIELDS}}
    {{DECLARATIONS}}
};
{{DEFINITIONS}}
int main(){
    ManzariDafalias m;
    {{READ_PARAMETERS}}
    m.m_Pmin=1e-4*m.m_P_atm; m.m_Presidual=.01*m.m_P_atm;
    for(int i=0;i<3;++i)m.mI1(i)=1.;
    Vector stress(6),alpha(6),fabric(6),anchor(6);
    for(auto* v:{&stress,&alpha,&fabric,&anchor})for(int i=0;i<6;++i)std::cin>>(*v)(i);
    double e;std::cin>>e>>m.mElastFlag;
    if(!std::cin)return 2;
    double K,G,cos3,h,psi,aB,aD,b0,A,D,B,C;
    Vector n(6),d(6),b(6),R(6);
    m.GetElasticModuli(stress,e,K,G);
    m.GetStateDependent(stress,alpha,fabric,e,anchor,n,d,b,cos3,h,psi,aB,aD,b0,A,D,B,C,R);
    std::cout<<std::setprecision(17);
    for(double x:{K,G,m.GetF(stress,alpha),psi,cos3,h,aB,aD,b0,A,D,B,C})std::cout<<x<<' ';
    Vector product=m.SingleDot(alpha,fabric);
    for(auto* v:{&n,&b,&d,&R,&product})for(int i=0;i<6;++i)std::cout<<(*v)(i)<<' ';
    for(double x:{m.GetNorm_Contr(alpha),m.GetNorm_Cov(alpha),
                  m.DoubleDot2_2_Contr(alpha,fabric),m.DoubleDot2_2_Cov(alpha,fabric),
                  m.DoubleDot2_2_Mixed(alpha,fabric)})std::cout<<x<<' ';
    Vector cov=m.ToCovariant(alpha),contr=m.ToContraviant(alpha);
    for(auto* v:{&cov,&contr})for(int i=0;i<6;++i)std::cout<<(*v)(i)<<' ';
    std::cout<<'\n';
}
'''


def translation_unit(source, notice, methods):
    header = source[:source.index('#include')]
    generated = HARNESS.replace('{{FIELDS}}', '\n'.join(f'double m_{p};' for p in PARAMETERS))
    generated = generated.replace('{{DECLARATIONS}}', '\n'.join(m['declaration'] for m in methods))
    generated = generated.replace('{{DEFINITIONS}}', '\n\n'.join(m['text'] for m in methods))
    generated = generated.replace('{{READ_PARAMETERS}}', '\n'.join(f'std::cin>>m.m_{p};' for p in PARAMETERS))
    return '/*\n'+notice+'\n*/\n'+header+'\n'+generated


# Cartesian oracle: no Atlas DSL/tensor operations and no selected source bodies.
def matrix(v):
    return [[v[0], v[3], v[5]], [v[3], v[1], v[4]], [v[5], v[4], v[2]]]


def vector(a):
    return [a[0][0], a[1][1], a[2][2], a[0][1], a[1][2], a[0][2]]


def linear(a, b, x=1., y=1.):
    return [[x*a[i][j]+y*b[i][j] for j in range(3)] for i in range(3)]


def scale(a, x):
    return [[x*v for v in row] for row in a]


def trace(a):
    return sum(a[i][i] for i in range(3))


def dot(a, b):
    return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))


def product(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


I = [[float(i == j) for j in range(3)] for i in range(3)]


def oracle(case):
    pset = case['parameters']
    G0, nu, ei, Mc, c, lam, e0, ksi, patm, m, h0, ch, nb, A0, nd, _, _ = pset
    stress, alpha, fabric, anchor = (matrix(case[k]) for k in ('stress', 'alpha', 'fabric', 'anchor'))
    e = case['e']
    mean = trace(stress)/3
    raw_p = mean+.01*patm
    p = max(raw_p, 1e-10)
    deviator = linear(stress, I, 1, -mean)
    shifted = linear(deviator, alpha, 1, -raw_p)
    norm = math.sqrt(dot(shifted, shifted))
    n = scale(shifted, 0 if abs(raw_p) < 1e-10 else 1/(norm if norm >= 1e-10 else 1))
    n2 = product(n, n)
    cos3 = max(-1., min(1., math.sqrt(6)*trace(product(n, n2))))
    lode = 2*c/((1+c)-(1-c)*cos3)
    psi = e-e0+lam*(p/patm)**ksi
    aB = lode*Mc*math.exp(-nb*psi)-m
    aD = lode*Mc*math.exp(nd*psi)-m
    b = linear(n, alpha, math.sqrt(2/3)*aB, -1)
    d = linear(n, alpha, math.sqrt(2/3)*aD, -1)
    b0 = G0*h0*(1-ch*e)/math.sqrt(p/patm)
    dist = dot(linear(alpha, anchor, 1, -1), n)
    h = 1e10 if abs(dist) < 1e-10 else b0/dist
    A = A0*(1+max(0, dot(fabric, n)))
    # Stable logistic evaluation. Selected source uses exp directly.
    x = 7.6349-7.2713*p
    factor = (math.exp(-x)/(1+math.exp(-x)) if x >= 0 else 1/(1+math.exp(x))) if p < .05*patm else 1.
    D = A*dot(d, n)*factor
    B = 1+1.5*(1-c)/c*lode*cos3
    C = 3*math.sqrt(1.5)*(1-c)/c*lode
    R = linear(linear(n, linear(n2, I, 1, -1/3), B, -C), I, 1, D/3)
    G = G0*patm*(2.97-ei)**2/(1+ei)
    if case['elastic_flag']:
        G *= math.sqrt(max(mean, 1e-4*patm)/patm)
    K = 2/3*(1+nu)/(1-2*nu)*G
    sym_product = scale(linear(product(alpha, fabric), product(fabric, alpha)), .5)
    alpha_cov_matrix = matrix([x if i < 3 else x/2 for i, x in enumerate(case['alpha'])])
    fabric_cov_matrix = matrix([x if i < 3 else x/2 for i, x in enumerate(case['fabric'])])
    result = [K, G, norm-math.sqrt(2/3)*m*raw_p, psi, cos3, h, aB, aD, b0, A, D, B, C]
    for tensor in (n, b, d, R, sym_product):
        result.extend(vector(tensor))
    result.extend([math.sqrt(dot(alpha, alpha)), math.sqrt(dot(alpha_cov_matrix, alpha_cov_matrix)),
                   dot(alpha, fabric), dot(alpha_cov_matrix, fabric_cov_matrix),
                   sum(a*b for a, b in zip(case['alpha'], case['fabric']))])
    result.extend(x if i < 3 else 2*x for i, x in enumerate(case['alpha']))
    result.extend(x if i < 3 else x/2 for i, x in enumerate(case['alpha']))
    return result


def cases():
    # Verification example from the official documentation; no calibration claim.
    base = dict(parameters=[125., .05, .8, 1.25, .712, .019, .934, .7, 100., .01,
                            7.05, .968, 1.1, .704, 3.5, 4., 600.],
                stress=[140., 80., 80., 9., -6., 3.], alpha=[.04, -.02, -.02, .01, .02, -.03],
                fabric=[.3, -.2, -.1, -.1, .2, .15], anchor=[0.]*6, e=.75, elastic_flag=1)
    result = []

    def add(name, **changes):
        c = {**base, **changes, 'id': name}
        result.append(c)
        return c

    add('sheared-reference')
    params_pa = list(base['parameters']); params_pa[8] *= 1000
    add('sheared-reference-pa', parameters=params_pa, stress=[1000*x for x in base['stress']])
    add('axisymmetric-compression', stress=[160., 70., 70., 0., 0., 0.], alpha=[0.]*6)
    add('axisymmetric-extension', stress=[40., 130., 130., 0., 0., 0.], alpha=[0.]*6)
    add('isotropic-zero-direction', stress=[100., 100., 100., 0., 0., 0.], alpha=[0.]*6)
    add('singular-memory-distance', anchor=base['alpha'])
    add('signed-hardening-distance', anchor=[2*x for x in base['alpha']])
    add('near-zero-direction', stress=[100., 100., 100., 0., 0., 0.], alpha=[0., 0., 0., 1e-15, 0., 0.])
    add('zero-raw-pressure', stress=[-1., -1., -1., 1., -.5, .2])
    add('negative-raw-pressure', stress=[-2., -2., -2., 1., -.5, .2])
    add('current-void-ratio-change', e=.9)
    add('elastic-stage', elastic_flag=0)
    for mean in (.2, 3.999999, 4., 4.000001):
        a = add(f'pressure-{mean:.9g}-kpa', stress=[mean]*3+[.1, -.05, .02])
        params = list(a['parameters']); params[8] *= 1000
        add(a['id'].removesuffix('kpa')+'pa', parameters=params, stress=[x*1000 for x in a['stress']])
    rng = random.Random(2004)
    for i in range(64):
        def deviatoric(size):
            v = [rng.uniform(-size, size) for _ in range(6)]
            mean = sum(v[:3])/3
            return [x-mean if j < 3 else x for j, x in enumerate(v)]
        stress = deviatoric(30)
        stress[:3] = [x+rng.uniform(80, 200) for x in stress[:3]]
        add(f'random-sheared-{i:02}', stress=stress, alpha=deviatoric(.15),
            fabric=deviatoric(.5), anchor=deviatoric(.1), e=rng.uniform(.5, .95))
    for i, angle in enumerate((.17, .53, 1.2)):
        co, si = math.cos(angle), math.sin(angle)
        q = [[co, -si, 0], [si, co, 0], [0, 0, 1]]
        qt = [list(row) for row in zip(*q)]
        add(f'rotated-reference-{i}', **{k: vector(product(product(q, matrix(base[k])), qt))
                                         for k in ('stress', 'alpha', 'fabric', 'anchor')})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cxx', default='c++')
    args = parser.parse_args()
    audit = json.loads((ROOT/'catalogue/source-audits/sanisand-2004-opensees.json').read_text())
    checked = []
    for item in audit['sources']:
        if 'github.com' not in item['url']:
            continue
        path = args.reference_directory/item['url'].split('/')[-1]
        if sha(path) != item['sha256']:
            raise ValueError(f'Reference source hash mismatch: {path.name}')
        checked.append(dict(name=path.name, sha256=sha(path)))
    source = (args.reference_directory/'ManzariDafalias.cpp').read_text()
    methods = extract_methods(source)
    compiler = shutil.which(args.cxx)
    if compiler is None:
        raise ValueError('C++ compiler unavailable')
    runs = []
    with tempfile.TemporaryDirectory(prefix='atlas-sanisand-') as directory:
        unit = translation_unit(source, (args.reference_directory/'COPYRIGHT').read_text(), methods)
        path = Path(directory)/'kernel.cpp'; path.write_text(unit)
        exe = Path(directory)/'kernel'
        build = subprocess.run([compiler, '-std=c++20', '-O2', str(path), '-o', str(exe)], capture_output=True, text=True)
        if build.returncode:
            raise RuntimeError('Private reference harness compilation failed:\n'+build.stderr)
        unit_hash = sha(path)
        executable_hash = sha(exe)
        for case in cases():
            inputs = case['parameters']+sum((case[k] for k in ('stress', 'alpha', 'fabric', 'anchor')), [])+[case['e'], case['elastic_flag']]
            run = subprocess.run([str(exe)], input=' '.join(map(repr, inputs))+'\n', text=True, capture_output=True, check=True)
            actual = [float(x) for x in run.stdout.split()]
            expected = oracle(case)
            if len(actual) != len(NAMES) or len(expected) != len(NAMES):
                raise ValueError('Unexpected source/oracle result layout')
            failures = [name for name, a, b in zip(NAMES, actual, expected)
                        if not math.isfinite(a) or not math.isfinite(b) or abs(a-b) > ATOL+RTOL*abs(b)]
            runs.append(dict(case=case, source=dict(zip(NAMES, actual)), oracle=dict(zip(NAMES, expected)),
                             passed=not failures, failed_components=failures, stderr=run.stderr))
    by_id = {r['case']['id']: r for r in runs}
    low = by_id['pressure-0.2-kpa']['source']['D']
    low_pa = by_id['pressure-0.2-pa']['source']['D']
    findings = dict(low_pressure_dilatancy=dict(D_numeric_kpa=low, D_numeric_pa=low_pa,
                        difference=low-low_pa, unit_invariant=abs(low-low_pa) <= ATOL+RTOL*abs(low_pa),
                        interpretation='Observed source variant: raw numeric pressure in logistic exponent; this is not a physically unit-invariant correction.'),
                    current_void_ratio_ignored_by_elasticity=all(by_id['sheared-reference']['source'][k] == by_id['current-void-ratio-change']['source'][k] for k in ('K', 'G')),
                    signed_hardening=by_id['signed-hardening-distance']['source']['h'],
                    singular_hardening=by_id['singular-memory-distance']['source']['h'])
    regular = by_id['sheared-reference']['source']
    regular_pa = by_id['sheared-reference-pa']['source']
    high_pressure_unit_check = all(abs(regular[k]*(1000 if k in ('K', 'G', 'F') else 1)-regular_pa[k])
                                   <= ATOL+RTOL*abs(regular_pa[k]) for k in SCALARS)
    assertions = dict(high_pressure_unit_covariance=high_pressure_unit_check,
                      low_pressure_unit_difference_observed=abs(low-low_pa) > 1e-4,
                      elasticity_uses_initial_void_ratio=findings['current_void_ratio_ignored_by_elasticity'],
                      negative_signed_hardening_observed=findings['signed_hardening'] < 0,
                      singular_hardening_replacement=findings['singular_hardening'] == 1e10)
    passed = all(r['passed'] for r in runs) and all(assertions.values())
    files = ['tools/verify_sanisand_source.py', 'atlas/opensees.py', 'tests/test_opensees.py',
             'tests/test_sanisand_source.py', 'docs/models/sanisand-2004-conventions.md',
             'catalogue/source-audits/sanisand-2004-opensees.json']
    report = dict(schema_version='0.1', kind='selected-source-function-verification', model_id='sanisand-2004',
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  reference_commit=audit['reference_commit'], created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  scope='Selected unchanged state/tensor functions compiled with original Atlas vector adapter and substitute class context. No full OpenSees integration, canonical Atlas SANISAND execution, original-paper review, independent human review or model admission.',
                  source_files=[dict(path=p, sha256=sha(ROOT/p)) for p in files],
                  reference_files=checked, temporary_translation_unit_sha256=unit_hash,
                  temporary_executable_sha256=executable_hash,
                  selected_methods=[{k:v for k,v in m.items() if k not in ('text', 'declaration')} |
                                    dict(normalized_text_sha256=hashlib.sha256(m['text'].encode()).hexdigest()) for m in methods],
                  compiler_version=subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
                  build_flags=['-std=c++20', '-O2'], tolerances=dict(relative=RTOL, absolute=ATOL),
                  case_count=len(runs), passed=passed, assertions=assertions, findings=findings, runs=runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(f'Selected SANISAND functions: {sum(r["passed"] for r in runs)}/{len(runs)} cases; {args.output}')
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
