"""Three-candidate analytical elasticity integration check; no compilation or real data."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.calibration_recorded import run_recorded_search
from atlas.calibration_search import METHOD
from atlas.experiment_replay import parse_json

SOLVER_SHA256='960d6f8ebcc0c3296555dd6e294a3650a5ec2318108d30850216ee5a69e4f574'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    content=json.dumps(value,indent=2,allow_nan=False)+'\n'
    with Path(path).open('x') as stream:stream.write(content)
    return hashlib.sha256(content.encode()).hexdigest()

def run(solver,catalogue,output):
    output=Path(output);output.mkdir()
    experiment=parse_json((ROOT/'tests/fixtures/experiments/synthetic-drained-elastic.json').read_bytes())
    configuration=parse_json((ROOT/'protocols/drained-elastic-replay.json').read_bytes())
    model=parse_json((ROOT/'models/linear-elastic.json').read_bytes())
    configuration['parameters']['E']=2e7
    tid=experiment['id']
    reservations={'paper_reservation_version':1,'id':'synthetic-reservations',
        'experiments':[{'id':tid,'role':'development'},{'id':'synthetic-evaluation','role':'development'},
                       {'id':'synthetic-reserved','role':'reserved_final'}]}
    rh=write(output/'reservations.json',reservations)
    allocation={'schema_version':'0.1','kind':'whole-test-study-allocation','id':'synthetic-allocation',
        'phase':'development','grouping_unit':'whole_test','evaluation_claim':'previously_exposed_development',
        'calibration_packages':{'fit':[tid]},'evaluation_ids':['synthetic-evaluation'],
        'reservation_policy':{'id':'synthetic-reservations','sha256':rh},
        'limitations':['Analytical fixture only; no experimental or scientific calibration.']}
    ah=write(output/'allocation.json',allocation)
    objective={'schema_version':'0.1','kind':'study-objective','id':'synthetic-objective',
        'allocation_sha256':ah,'package':'fit','method':'piecewise-linear-residual-axial-travel-v1',
        'test_aggregation':'equal_whole_test','failure_policy':'reject_entire_candidate',
        'channels':{'q':{'unit':'Pa','scale':30000.,'weight':1.},
                    'volumetric_strain':{'unit':'1','scale':.001,'weight':1.}}}
    spec={'id':'synthetic-recorded-search','method':METHOD,'parameters':configuration['parameters'],
        'fitted':[{'name':'E','bounds':[1e7,5e7],'transform':'linear'}],
        'max_evaluations':3,'initial_step':.25,'minimum_step':.0625}
    protocol={'kind':'prospective-calibration-elastic-smoke-v1','solver_sha256':SOLVER_SHA256,
        'material_call_limit':3,'metadata_call_limit':1,
        'expected_E_sequence':[2e7,1e7,3e7],'expected_best_E':3e7,
        'maximum_best_objective':1e-12,'maximum_q_error_Pa':.002,
        'maximum_volume_error':2e-10,
        'reference':'Independent isotropic elasticity fixture, including reversal and duplicate observation; existing recorded API analytical tolerances.',
        'inputs_sha256':{p:sha(ROOT/p) for p in ['models/linear-elastic.json',
            'tests/fixtures/experiments/synthetic-drained-elastic.json','protocols/drained-elastic-replay.json',
            'atlas/calibration_recorded.py','atlas/calibration_search.py','atlas/study_objective.py',
            'atlas/experiment_replay.py','atlas/recorded.py',str(Path(__file__).relative_to(ROOT))]},
        'catalogue_file_sha256':sha(catalogue)}
    # Freeze every reference/budget before metadata or material execution.
    write(output/'protocol.json',protocol)
    result=run_recorded_search(spec,objective,allocation,reservations,model,{tid:experiment},{tid:configuration},
        allocation_sha256=ah,reservation_sha256=rh,solver=solver,solver_sha256=SOLVER_SHA256,
        catalogue=parse_json(Path(catalogue).read_bytes()),output=output/'run')
    sequence=[r['parameters']['E'] for r in result['candidates']]
    assert sequence==protocol['expected_E_sequence']
    assert result['evaluations']==3 and result['status']=='success'
    assert all(r['status']=='success' for r in result['candidates'])
    assert result['best']['parameters']['E']==protocol['expected_best_E']
    assert result['best']['objective']<=protocol['maximum_best_objective']
    response=parse_json((output/'run/candidate-00002/000-response.json').read_bytes())
    q_error=max(abs(p['state'][0]-(p['state'][1]+p['state'][2])/2-row['q'])
                for p,row in zip(response['points'],experiment['rows']))
    initial=configuration['initial_strain']
    volume_error=max(abs(sum(p['strain'][:3])-sum(initial[:3])-row['volumetric_strain'])
                     for p,row in zip(response['points'],experiment['rows']))
    assert q_error<=protocol['maximum_q_error_Pa']
    assert volume_error<=protocol['maximum_volume_error']
    assert sha(solver)==SOLVER_SHA256
    for path,h in protocol['inputs_sha256'].items():assert sha(ROOT/path)==h,path
    assessment={'kind':'calibration-elastic-smoke-assessment-v1','passed':True,
        'material_calls':3,'metadata_calls':1,'builds':0,'best_E_Pa':result['best']['parameters']['E'],
        'best_objective':result['best']['objective'],'maximum_q_error_Pa':q_error,
        'maximum_volume_error':volume_error,'scientific_admission':False}
    write(output/'assessment.json',assessment)
    write(output/'files.json',{'files':{str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*.json'))}})
    print(json.dumps(assessment,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver',type=Path,required=True)
    parser.add_argument('--catalogue',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.solver,args.catalogue,args.output)
