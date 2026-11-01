"""Compare retained MCC isotropic refinement with an exact continuous reduction."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from atlas.isotropic_reference import cam_clay_isotropic
from atlas.model import load
from atlas.refinement import refine_recorded
from atlas.recorded import recorded_wire,MATERIAL_DEFAULTS,CONTROL_DEFAULTS
from tools.analyze_recorded_refinement import summarize


def validate_point(point):
    for key,length in [('state',9),('strain',6)]:
        vector=point[key]
        if not isinstance(vector,list) or len(vector)!=length or any(type(x) not in (int,float) or not math.isfinite(x) for x in vector):
            raise ValueError('nonfinite or malformed MCC observation '+key)
    if type(point['coordinate']) not in (int,float) or not math.isfinite(point['coordinate']):
        raise ValueError('nonfinite or malformed MCC coordinate')


def analyze(report):
    summarize(report)  # Check requests, hashes, grids, controls and stored metrics first.
    case=next(c for c in report['cases'] if c['id']=='mcc-plastic-isotropic-strain')
    source=next(c['specification'] for c in report['study']['cases'] if c['id']==case['id'])
    model=load(ROOT/'models/modified-cam-clay.json')
    model_hash=hashlib.sha256((ROOT/'models/modified-cam-clay.json').read_bytes()).hexdigest()
    if case['model_sha256']!=model_hash:raise ValueError('retained MCC model differs from analytical reference')
    if source['model']!=model['id']:raise ValueError('reference model mismatch')
    controls=source['path']['controls']
    for i,row in enumerate(controls):
        if row['kind']!='strain' or row['coefficients']!=[int(i==j) for j in range(6)]:
            raise ValueError('reference requires componentwise strain controls')
    if source['path']['initial_strain']!=[0]*6:raise ValueError('reference requires zero strain origin')
    response=case['levels'][0]['response'];initial=response['initial']
    if initial[:3]!=[initial[0]]*3 or initial[3:6]!=[0]*3 or len(initial)!=9:
        raise ValueError('reference requires isotropic MCC initial state')
    parameters=dict(zip(model['parameters'],response['parameters'],strict=True))
    strains=[]
    for knot in source['path']['knots']:
        t=knot['targets']
        if t[:3]!=[t[0]]*3 or t[3:]!=[0]*3:raise ValueError('reference requires isotropic path')
        strains.append(sum(t[:3]))
    reference=cam_clay_isotropic(initial[0],initial[7],initial[6],parameters['kappa'],parameters['lambda_c'],strains)
    for ref,knot in zip(reference,source['path']['knots']):ref['coordinate']=knot['coordinate']
    levels=[]
    for level in case['levels']:
        response=level['response']
        if not response['ok']:raise ValueError('cannot compare incomplete MCC level')
        for point in response['points']:validate_point(point)
        points=[response['points'][i] for i in level['original_indices']]
        errors=[]
        for pt,ref in zip(points,reference,strict=True):
            if max(abs(x-pt['state'][0]) for x in pt['state'][:3])>1e-4 or max(map(abs,pt['state'][3:6]))>1e-4:
                raise ValueError('computed path is not isotropic')
            errors.append(dict(coordinate=pt['coordinate'],p_error=pt['state'][0]-ref['p'],
                               pc_error=pt['state'][7]-ref['pc'],e_error=pt['state'][6]-ref['e']))
        error=max(abs(row[key]) for row in errors for key in ('p_error','pc_error'))
        levels.append(dict(factor=level['factor'],max_pressure_pc_error_Pa=error,errors=errors))
    orders=[dict(factor=b['factor'],order=math.log(a['max_pressure_pc_error_Pa']/b['max_pressure_pc_error_Pa'])/
                 math.log(b['factor']/a['factor'])) for a,b in zip(levels,levels[1:])]
    return dict(scope='Continuous limit of declared Atlas MCC equations under isotropic monotone segments; not source, external-code or experimental validation',
                model_sha256=hashlib.sha256((ROOT/'models/modified-cam-clay.json').read_bytes()).hexdigest(),
                initial=initial,parameters=parameters,reference=reference,levels=levels,orders=orders)


def analyze_followups(report,followup):
    result=analyze(report)
    source=next(c['specification'] for c in report['study']['cases'] if c['id']=='mcc-plastic-isotropic-strain')
    rows=[]
    if [(run['factor'],run['residual_override']) for run in followup['runs']]!=[(64,None),(32,1e-12)]:raise ValueError('follow-up matrix differs')
    if followup['binary_sha256']!=report['solver_sha256']:raise ValueError('follow-up binary differs')
    for run in followup['runs']:
        spec,indices=refine_recorded(source,run['factor'])
        if run['residual_override'] is not None:spec.setdefault('integration_settings',{})['residual_tolerance']=run['residual_override']
        r=run['response'];controls,knots=recorded_wire(spec)
        canonical=json.dumps(spec,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if (r['specification']!=spec or r['request_sha256']!=hashlib.sha256(canonical).hexdigest() or
            run['original_indices']!=indices or r['controls_wire']!=controls or r['knots_wire']!=knots or
            r['catalogue_hash']!=report['catalogue_hash'] or r['initial']!=result['initial'] or
            r['parameters']!=list(result['parameters'].values())):raise ValueError('follow-up request/input changed')
        if not r['ok'] or r['failed_knot']!=-1 or len(r['points'])!=len(spec['path']['knots']):raise ValueError('incomplete follow-up')
        if r['state']!=r['points'][-1]['state'] or r['strain']!=r['points'][-1]['strain']:raise ValueError('follow-up committed endpoint differs')
        if any(r['integration_settings'][key]!=v for key,v in (MATERIAL_DEFAULTS|spec.get('integration_settings',{})).items()):raise ValueError('follow-up settings differ')
        if r['control_settings']!=CONTROL_DEFAULTS|spec.get('control_settings',{}):raise ValueError('follow-up controls differ')
        for point,knot in zip(r['points'],spec['path']['knots']):
            validate_point(point)
            if point['coordinate']!=knot['coordinate'] or max(abs(a-b) for a,b in zip(point['strain'],knot['targets']))>r['control_settings']['control_tolerance']:
                raise ValueError('follow-up observation or strain differs')
            if max(abs(x-point['state'][0]) for x in point['state'][:3])+max(map(abs,point['state'][3:6]))>1e-4:
                raise ValueError('follow-up is not isotropic')
        errors=[]
        for i,ref in zip(indices,result['reference']):
            pt=r['points'][i]
            errors.append(dict(coordinate=pt['coordinate'],p_error=pt['state'][0]-ref['p'],pc_error=pt['state'][7]-ref['pc'],e_error=pt['state'][6]-ref['e']))
        baseline=next(level for case in report['cases'] if case['id']=='mcc-plastic-isotropic-strain' for level in case['levels'] if level['factor']==32)
        bp=[baseline['response']['points'][i] for i in baseline['original_indices']]
        difference=max(abs(r['points'][i]['state'][j]-p['state'][j]) for i,p in zip(indices,bp) for j in (0,1,2,7))
        error=max(abs(row[key]) for row in errors for key in ('p_error','pc_error'))
        rows.append(dict(factor=run['factor'],residual_override=run['residual_override'],max_pressure_pc_error_Pa=error,
                         max_difference_from_default_factor32_Pa=difference,errors=errors))
    result['followups']=rows
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--followup',type=Path)
    args=parser.parse_args()
    with gzip.open(args.report,'rt') if args.report.suffix=='.gz' else args.report.open() as f:report=json.load(f)
    if args.followup:
        with gzip.open(args.followup,'rt') as f:followup=json.load(f)
        result=analyze_followups(report,followup)
        result['followup_sha256']=hashlib.sha256(args.followup.read_bytes()).hexdigest()
    else:result=analyze(report)
    result['report_sha256']=hashlib.sha256(args.report.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(levels=len(result['levels']),finest_error_Pa=result['levels'][-1]['max_pressure_pc_error_Pa'],
                          finest_order=result['orders'][-1]['order'])))
if __name__=='__main__':main()
