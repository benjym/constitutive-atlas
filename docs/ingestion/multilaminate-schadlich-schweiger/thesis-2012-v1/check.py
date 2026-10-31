"""Independent geometry/state-budget checks; no Atlas or author-code execution."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent

def quadrature_checks(doc):
    rows = doc['rows']
    if [row['i'] for row in rows] != list(range(1, 34)):
        raise ValueError('Expected all 33 ordered source rows')
    points = [([F(v) for v in row['normal']], F(row['weight'])) for row in rows]
    if any(w <= 0 or len(n) != 3 for n, w in points):
        raise ValueError('Invalid direction or weight')
    tolerance = F(doc['moment_absolute_tolerance'])
    errors = {'norm': max(abs(sum(v*v for v in n)-1) for n, w in points),
              'weight_sum': abs(2*sum(w for n, w in points)-1)}
    errors['second_moment'] = max(
        abs(2*sum(w*n[i]*n[j] for n, w in points)-F(i == j, 3))
        for i, j in product(range(3), repeat=2))
    errors['fourth_moment'] = max(
        abs(2*sum(w*n[i]*n[j]*n[k]*n[l] for n, w in points)
            -F((i == j)*(k == l)+(i == k)*(j == l)+(i == l)*(j == k), 15))
        for i, j, k, l in product(range(3), repeat=4))
    if any(error > tolerance for error in errors.values()):
        raise ValueError('Printed quadrature geometry/moments disagree: '+str(errors))
    return {key: {'exact': str(error), 'approximate': float(error)} for key, error in errors.items()}

def traction_work_check():
    # Rational orthonormal frame, independent of angle definitions or Atlas helpers.
    n = [F(1,3), F(2,3), F(2,3)]
    s = [F(2,3), F(-2,3), F(1,3)]
    t = [F(2,3), F(1,3), F(-2,3)]
    dot = lambda a,b: sum(x*y for x,y in zip(a,b))
    basis = [n,s,t]
    assert all(dot(a,b) == int(i == j) for i,a in enumerate(basis) for j,b in enumerate(basis))
    # Source Eq5: normal column has twice the off-diagonal product;
    # shear columns contain the two cross terms. Global strain uses engineering shear.
    pairs = [(0,0),(1,1),(2,2),(0,1),(1,2),(0,2)]
    transform = [[n[i]*axis[j] if i == j else n[i]*axis[j]+n[j]*axis[i]
                  for axis in basis] for i,j in pairs]
    stress = list(map(F,[11,7,5,2,3,4]))
    matrix = [[stress[0],stress[3],stress[5]],
              [stress[3],stress[1],stress[4]],
              [stress[5],stress[4],stress[2]]]
    traction = [dot(row,n) for row in matrix]
    local = [sum(transform[i][j]*stress[i] for i in range(6)) for j in range(3)]
    assert local == [dot(axis,traction) for axis in basis]
    local_strain = [F(1,7), F(-2,5), F(3,11)]
    global_engineering_strain = [dot(row,local_strain) for row in transform]
    macro_work, micro_work = dot(stress,global_engineering_strain), dot(local,local_strain)
    assert macro_work == micro_work
    return {'local_traction': list(map(str,local)), 'exact_virtual_work': str(macro_work),
            'meaning': 'One full-shear Cartesian projection/work witness, not constitutive integration'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', type=Path, help='Optionally verify the private complete source PDF')
    args = parser.parse_args()
    receipt = json.loads((HERE/'source-receipt.json').read_text())
    if args.pdf and hashlib.sha256(args.pdf.read_bytes()).hexdigest() != receipt['sha256']:
        raise ValueError('Private primary source checksum mismatch')
    doc = json.loads((HERE/'quadrature.json').read_text())
    moments = quadrature_checks(doc)
    rejected = []
    for name in ['weight_digit', 'missing_antipodal_half', 'normal_digit']:
        changed = copy.deepcopy(doc)
        if name == 'weight_digit': changed['rows'][0]['weight'] = '0.01985353993'
        elif name == 'missing_antipodal_half':
            for row in changed['rows']: row['weight'] = str(float(row['weight'])/2)
        else: changed['rows'][0]['normal'][0] = '0.99'
        try: quadrature_checks(changed)
        except ValueError: rejected.append(name)
        else: raise AssertionError('Corrupt source transcription not rejected: '+name)
    inventory = json.loads((HERE/'capability-inventory.json').read_text())
    budgets = {v['id']: v['per_plane']*33+v['global_history']
               for v in inventory['state_allocation']['variants']}
    assert budgets == {'Basic':102, 'MMSS':231, 'MMSC':264, '*_sss':396, '*_sss_lh':1056}
    assert all(n > inventory['state_allocation']['atlas_current_limit'] for n in budgets.values())
    print(json.dumps({'id':'multilaminate-thesis-2012-geometry-budget-v1',
                      'quadrature_residuals':moments, 'projection':traction_work_check(),
                      'source_history_allocations_at_numcp33':budgets,
                      'source_transcription_corruptions_rejected':rejected,
                      'private_pdf_checked':args.pdf is not None,
                      'constitutive_reference_or_admission':False,
                      'atlas_imports':0,'author_code_executions':0,'compiled_calls':0},indent=2))

if __name__ == '__main__':
    main()
