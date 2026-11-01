"""Produce auditable closed-form evidence without evaluating the model DSL.

The oracle uses Cartesian Lamé coefficients and engineering shear conversion.
It never calls expression evaluation or constitutive code generation.
"""
import argparse
import datetime
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.evidence import sha256, validate_record

STRESS_ATOL = 1e-4  # Pa; fixed before executing the cases
REL_TOL = 1e-10
VOID_ATOL = 1e-10


def csv(values):
    return ','.join(format(v, '.17g') for v in values)


def expected_state(initial, strain, E, nu):
    # Cartesian Hooke law, not the model's K/dev residual expression.
    lame = E * nu / ((1 + nu) * (1 - 2 * nu))
    shear = E / (2 * (1 + nu))
    volume = sum(strain[:3])
    stress = [initial[i] + lame * volume + 2 * shear * strain[i] for i in range(3)]
    # Mandel e_xy = gamma_xy/sqrt(2), sigma_xy^M = sqrt(2)*tau_xy.
    for i in range(3, 6):
        engineering_shear = math.sqrt(2) * strain[i]
        stress.append(initial[i] + math.sqrt(2) * shear * engineering_shear)
    # Project bookkeeping convention, not a claim about the OGS material state.
    return stress + [(1 + initial[6]) * math.exp(-volume) - 1]


def compare(actual, expected):
    if len(actual) != len(expected) or not all(math.isfinite(v) for v in actual):
        return False, None
    errors = [abs(a-b) for a,b in zip(actual, expected)]
    limits = [(STRESS_ATOL if i < 6 else VOID_ATOL) + REL_TOL*abs(b) for i,b in enumerate(expected)]
    return all(e <= t for e,t in zip(errors, limits)), max(e/t for e,t in zip(errors, limits))


def execute(solver):
    definitions = json.loads(subprocess.check_output([str(solver), '--describe'], text=True))
    local = json.loads((ROOT / 'models/linear-elastic.json').read_text())
    embedded = next(m for m in definitions['models'] if m['id'] == 'linear-elastic')
    if local != embedded:
        raise ValueError('Solver embeds a different elasticity definition; rebuild first')
    cases = []
    def run_case(ident, arguments, initial, strain, E, nu):
        command = [str(solver), '--model', 'linear-elastic', '--parameters', csv([1e5,E,nu]), '--initial', csv(initial)] + arguments
        process = subprocess.run(command, text=True, capture_output=True, timeout=30)
        result = json.loads(process.stdout)
        expected = expected_state(initial, strain, E, nu)
        actual = result.get('state', [])
        if 'points' in result and result['points']:
            actual = result['points'][-1]['state']
        passed, ratio = compare(actual, expected)
        cases.append(dict(id=ident, arguments=command[1:], initial=initial, total_strain=strain,
            expected=expected, actual=actual, max_tolerance_ratio=ratio,
            solver_ok=result.get('ok',False), returncode=process.returncode,
            passed=passed and process.returncode==0 and result.get('ok',False),
            message=result.get('message','')))

    initial = [110000,90000,125000,1400,-900,650,0.7]
    paths = dict(hydrostatic=[.0002]*3+[0]*3,
        deviatoric=[.0006,-.0003,-.0003,0,0,0],
        shear_xy=[0,0,0,.0004,0,0], shear_yz=[0,0,0,0,-.0005,0],
        shear_xz=[0,0,0,0,0,.0007],
        mixed=[.00031,-.00012,.00007,.00009,-.00005,.00011],
        unloading=[-.00031,.00012,-.00007,-.00009,.00005,-.00011], zero=[0]*6)
    for label,E,nu in [('standard',3e7,.25),('auxetic',1.7e7,-.2),('near-incompressible',3e7,.49)]:
        for name,strain in paths.items():
            run_case(label+'-'+name, ['--mode','integrate','--strain',csv(strain)], initial,strain,E,nu)
    # These cases also check mixed-control solutions, not only prescribed strain.
    initial = [1e5]*3+[0,0,0,.7]
    E,nu,x = 3e7,.25,.001
    for name,protocol,strain in [
        ('drained',1,[x,-nu*x,-nu*x,0,0,0]),
        ('undrained',2,[x,-x/2,-x/2,0,0,0]),
        ('oedometer',0,[x,0,0,0,0,0]),
        ('isotropic',4,[x,x,x,0,0,0])]:
        run_case(name,['--protocol',str(protocol),'--target',str(x),'--steps','16','--cycles','0'],initial,strain,E,nu)
    # Undrained cyclic paths return to the initial state and check e bookkeeping.
    run_case('undrained-reversal-cycle',['--protocol','2','--target',str(x),'--steps','64','--cycles','2'],initial,[0]*6,E,nu)
    return dict(kind='analytical-elasticity-report',model='linear-elastic',
        catalogue_hash=definitions['sha256'],
        oracle='Cartesian Lame law and engineering-shear conversion; no DSL evaluation',
        tolerances=dict(stress_absolute_Pa=STRESS_ATOL,void_absolute=VOID_ATOL,relative=REL_TOL),
        state_order=['sigma_xx','sigma_yy','sigma_zz','sqrt(2)*sigma_xy','sqrt(2)*sigma_yz','sqrt(2)*sigma_xz','e'],
        runtime=dict(python=platform.python_version(),platform=platform.platform(),solver_sha256=sha256(solver)),
        cases=cases,passed=all(c['passed'] for c in cases))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver',type=Path,default=ROOT/'build/atlas_solver')
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/elasticity-evidence.json')
    parser.add_argument('--record',type=Path,help='Write an integrity envelope; output must be inside the repository')
    args=parser.parse_args()
    report=execute(args.solver.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    if args.record:
        # Pin exactly the source files used for this automated check. Other work
        # in the shared checkout is neither included nor claimed as tested.
        paths=sorted({p.relative_to(ROOT).as_posix()
            for directory,pattern in [('atlas','*.py'),('cpp','**/*'),('models','*.json'),('schemas','*.json')]
            for p in (ROOT/directory).glob(pattern) if p.is_file()}
            | {'tools/verify_elasticity.py','CMakeLists.txt'})
        subprocess.check_call(['git','ls-files','--error-unmatch','--',*paths],cwd=ROOT,stdout=subprocess.DEVNULL)
        changed=subprocess.check_output(['git','diff','HEAD','--',*paths],cwd=ROOT,text=True)
        if changed:
            raise ValueError('Commit the evidence checker and definition before recording a revision')
        record=dict(schema_version='0.1',kind='numerical-evidence',id='linear-elastic-analytical-v1',
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            model=dict(id='linear-elastic',definition_sha256=sha256(ROOT/'models/linear-elastic.json')),
            executor=dict(name='Constitutive Atlas automated checker',automated=True,method='analytical-closed-form',independent_review=False),
            scope='29 native closed-form cases: Cartesian tensor stress, all shear planes, three elastic parameter regimes and axisymmetric controls. Void ratio is separately checked as project bookkeeping.',
            limitations=['No independent human equation/numerical review.','Analytical oracle was authored in this project; independent mathematical formulation is not independent authorship.','No experimental validation, finite-rotation objectivity or nearly incompressible limit guarantee.','This record does not certify that every engine source matches the binary; solver binary hash and embedded definition are recorded.'],
            outcome='passed' if report['passed'] else 'failed',
            artifacts=[dict(path=args.output.resolve().relative_to(ROOT).as_posix(),sha256=sha256(args.output))],
            source_files=[dict(path=p,sha256=sha256(ROOT/p)) for p in paths],
            reproduction_command='cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 2 && python3 tools/verify_elasticity.py --output artifacts/elasticity-evidence.json')
        args.record.parent.mkdir(parents=True,exist_ok=True)
        args.record.write_text(json.dumps(record,indent=2)+'\n')
        validate_record(args.record,current=True)
    print(f"{sum(c['passed'] for c in report['cases'])}/{len(report['cases'])} closed-form cases passed; {args.output}")
    if not report['passed']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
