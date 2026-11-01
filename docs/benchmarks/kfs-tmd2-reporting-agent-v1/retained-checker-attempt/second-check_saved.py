"""Independent saved TMD2 arithmetic/identity audit. No Atlas imports or execution.
Default needs public saved evidence only. --private additionally verifies locally
available primary PDFs/driver/data and recomputes aggregate experimental errors.
It never downloads, evaluates a constitutive law, builds, fits, or launches a process.
"""
import argparse
import bisect
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import struct
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B = ROOT / 'docs/benchmarks'
STUDY = B / 'kfs-tmd2-research-range-v1'
PORTABLE = B / 'kfs-tmd2-portable-v1'
REFERENCE = B / 'kfs-tmd2-reference-v1'

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))

def interpolate(x, y, t):
    require(x[0] <= t <= x[-1], 'extrapolation forbidden')
    i = max(0, min(len(x)-2, bisect.bisect_right(x, t)-1))
    return y[i] + (y[i+1]-y[i]) * ((t-x[i])/(x[i+1]-x[i]))

def close(a, b):
    return math.isclose(a, b, rel_tol=3e-13, abs_tol=1e-12)

def main(private=False):
    manifest = read(HERE/'manifest.json')
    for relative, digest in manifest['public_inputs'].items():
        require(sha(ROOT/relative) == digest, 'changed input: '+relative)
    for relative, digest in manifest['outputs'].items():
        require(sha(HERE/relative) == digest, 'changed review output: '+relative)
    source_manifest = read(STUDY/'source-manifest.json')
    with tarfile.open(STUDY/'source.tar.gz') as archive:
        for name, digest in source_manifest.items():
            require(hashlib.sha256(archive.extractfile('source/'+name).read()).hexdigest() == digest,
                    'archived source changed: '+name)
        raw_model = archive.extractfile('source/models/hypoplastic-sand-igs97.json').read()
    require(hashlib.sha256(raw_model).hexdigest() == '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86', 'model identity')
    model = json.loads(raw_model)
    params = read(STUDY/'inputs/parameter-set.json')
    values = params['parameters']
    literal = dict(p_ref=100000., phi=math.radians(33.1), hs=4000000000., n=.27,
                   ed0=.677, ec0=1.054, ei0=1.212, alpha=.14, beta=2.5, R=.0001,
                   mR=2.2, mT=1.1, beta_r=.1, chi=5.5)
    require(values == literal and params['material_parameter_count'] == 13,
            'primary table constants')
    require(params['numerical_scale_parameters'] == ['p_ref'], 'project scale')
    require(list(model['parameters']) == list(values), 'positional parameter allocation')
    with localcontext() as context:
        context.prec = 100
        h = float(Decimal('.0001')/Decimal(3).sqrt())
    initial = [100000.]*3+[0.]*3+[.975]+[h]*3+[0.]*3
    require(3*Fraction(h)**2/Fraction(values['R'])**2 < 1, 'initial rounded history')
    case = read(STUDY/'inputs/case.json')
    require(case['initial']['flat_state'] == initial, 'nominal source state')
    require(case['initial']['measured_initial_state_separate']['void_ratio'] != initial[6], 'measured initialization substituted')
    require(next(m for m in read(STUDY/'generated-models.json')['models'] if m['id'] == model['id']) == model, 'generated definition identity')
    reference = read(STUDY/'inputs/reference.json')
    channels = reference['channels']
    for name, channel in channels.items():
        left, right, top, bottom = channel['frame_pdf_points']
        require(close(channel['horizontal_half_width'], 2*reference['stroke_width_pdf_points']*.25/(right-left)), 'horizontal width')
        require(close(channel['vertical_half_width'], 2*reference['stroke_width_pdf_points']*(500000 if name == 'q' else .14)/(bottom-top)), 'vertical width')
        require(channel['refinement_limit'] == channel['vertical_half_width']/10, 'prospective refinement ratio')
        require([r['axial_coordinate'] for r in channel['rows']] == [.25*i/100 for i in range(101)], 'source grid')
    for name in ['reference.json','protocol.json','requests.json','parameter-set.json','case.json']:
        require((STUDY/'inputs'/name).read_bytes() == (REFERENCE/'inputs'/name).read_bytes(), 'preceding frozen input changed')
    requests = read(STUDY/'inputs/requests.json')
    require([r['steps'] for r in requests] == [400,800,1600], 'three allocations')
    pins = read(STUDY/'inputs/source-pins.json')
    summary = read(STUDY/'results/summary.json')
    paths = []
    for request, expected in zip(requests, summary['paths'], strict=True):
        require(request['parameters'] == list(values.values()) and request['initial'] == initial, 'request values')
        directory = STUDY/'observations'/request['id']
        receipt, response = read(directory/'receipt.json'), read(directory/'stdout.json')
        require(type(receipt['returncode']) is int and receipt['returncode'] == 0, 'nonzero/noninteger process')
        require(receipt['artifact_sha256'] == pins['artifact']['sha256'], 'artifact receipt')
        require(receipt['freeze_sha256'] == sha(STUDY/'inputs/freeze.json'), 'freeze receipt')
        for name in ['stdout','stderr']:
            require(sha(directory/(name+('.json' if name == 'stdout' else '.txt'))) == receipt[name+'_sha256'], 'observation bytes')
        require(response['ok'] is True and response['research_scope']['finite_kinematics_verified'] is False, 'response scope')
        for field in ['model','parameters','initial','protocol','steps','integration_settings']:
            require(response[field] == request[field], 'response/request '+field)
        points = response['points']
        x = [point['control'] for point in points]
        require(len(x) == request['steps']+1 and x[0] == 0 and x[-1] == .25, 'completed controls')
        require(all(a < b for a,b in zip(x,x[1:])), 'control monotonicity')
        require([struct.pack('>d',v).hex() for v in x] == request['controls_bits'], 'control bits')
        y = {'q':[point['q_signed'] for point in points],
             'volumetric_strain':[sum(point['strain'][:3]) for point in points]}
        for channel, c in channels.items():
            require(all(row['lower'] <= interpolate(x,y[channel],row['axial_coordinate']) <= row['upper'] for row in c['rows']), 'source envelope')
            require(expected['source'][channel] == {'pass':True,'failures':[]}, 'summary source gate')
        paths.append((request['id'],x,y))
    differences = []
    for left,right,expected in zip(paths[:-1],paths[1:],summary['refinement'],strict=True):
        row = {'paths':[left[0],right[0]],'channels':{}}
        for name,c in channels.items():
            maximum = max(abs(interpolate(left[1],left[2][name],r['axial_coordinate'])-interpolate(right[1],right[2][name],r['axial_coordinate'])) for r in c['rows'])
            require(close(maximum,expected['channels'][name]['maximum_difference']) and maximum <= c['refinement_limit'], 'refinement arithmetic')
            row['channels'][name] = maximum
        differences.append(row)
    require(summary['source_pass'] is True and summary['refinement_pass'] is True and summary['scientific_admission'] is False, 'qualified gates')
    require((STUDY/'results/summary.json').read_bytes() == (PORTABLE/'results/summary.json').read_bytes(), 'portable summary changed')
    for request in requests:
        original = read(REFERENCE/'observations'/request['id']/'receipt.json')
        rejected = read(REFERENCE/'observations'/request['id']/'stdout.json')
        require(original['returncode'] == 1 and rejected['points'] == [] and rejected['message'] == 'control amplitude exceeds laboratory limit', 'original failure lost')
        portable = read(PORTABLE/'native-receipts'/(request['id']+'.json'))
        require(portable['returncode'] == 0 and portable['freeze_sha256'] == sha(PORTABLE/'inputs/freeze.json'), 'portable receipt')
    for directory in [REFERENCE,STUDY,PORTABLE]:
        for name,digest in read(directory/'inputs/freeze.json')['files'].items():
            target = directory/'inputs'/name
            if not target.exists():
                target = STUDY/'inputs'/name
            require(sha(target) == digest, 'frozen file '+str(target))
    witness = read(ROOT/'docs/reviews/tmd2-process-status-v1/witness.json')
    require(witness['old_assessor_exit'] == 0 and witness['altered_returncode'] == 23 and witness['source_pass'] is True, 'preserved process false pass')
    private_result = {'status':'NOT REQUESTED', 'measurements_or_documents_emitted':False}
    if private:
        receipts = read(HERE/'private-inputs.json')['files']
        for entry in receipts:
            require(sha(Path(entry['path'])) == entry['sha256'], 'private input changed: '+entry['id'])
        data_path = next(Path(entry['path']) for entry in receipts if entry['id'] == 'normalized-tmd2')
        clean = []
        for row in read(data_path)['rows']:
            if not 0 <= row['axial_strain'] <= .25:
                continue
            if clean and row['axial_strain'] == clean[-1]['axial_strain']:
                clean[-1] = row
            else:
                require(not clean or row['axial_strain'] > clean[-1]['axial_strain'], 'measurement reversal')
                clean.append(row)
        aggregates = []
        for name,x,y in paths:
            lo,hi = max(x[0],clean[0]['axial_strain']),min(x[-1],clean[-1]['axial_strain'])
            grid = [lo+(hi-lo)*i/100 for i in range(101)]
            expected = next(row for row in summary['paths'] if row['id'] == name)
            metrics = {}
            for channel in channels:
                errors = [interpolate(x,y[channel],t)-interpolate([r['axial_strain'] for r in clean],[r[channel] for r in clean],t) for t in grid]
                actual = {'rmse':math.sqrt(sum(e*e for e in errors)/len(errors)), 'mae':sum(abs(e) for e in errors)/len(errors),'maximum_absolute_error':max(abs(e) for e in errors)}
                require(all(close(value,expected['experimental_errors'][channel][key]) for key,value in actual.items()), 'experimental aggregate arithmetic')
                metrics[channel] = actual
            aggregates.append({'id':name,'metrics':metrics})
        private_result = {'status':'PASS','verified_files':len(receipts),'aggregates':aggregates,'measurements_or_documents_emitted':False}
    return {'status':'PASS','public_bindings':len(manifest['public_inputs']),'review_output_bindings':len(manifest['outputs']), 'source_envelope_checks':6,'refinement_checks':4,'original_empty_rejections':3,'portable_summary_byte_identical':True,'refinement_maxima':differences,'private':private_result,'material_calls':0,'compiled_calls':0,'new_fits':0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private', action='store_true')
    print(json.dumps(main(parser.parse_args().private),indent=2,allow_nan=False))
