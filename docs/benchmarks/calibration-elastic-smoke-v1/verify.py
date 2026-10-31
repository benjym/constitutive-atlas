"""Audit the saved synthetic calibration and replay its search without native calls."""
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.calibration_search import calibrate
from atlas.experiment_replay import digest


def verify(folder):
    folder=Path(folder)
    read=lambda name:json.loads((folder/name).read_text())
    files=read('files.json')['files']
    for path,h in files.items():assert hashlib.sha256((folder/path).read_bytes()).hexdigest()==h,path
    protocol=read('protocol.json');freeze=read('run/freeze.json');saved=read('run/result.json')
    for path,h in protocol['inputs_sha256'].items():
        source=ROOT/path
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=h:
            source=ROOT/'catalogue/source-snapshots'/h/path
        assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()==h,path
    for name,h in freeze['value_sha256'].items():assert digest(freeze[name])==h,name
    assert freeze['solver_sha256']==protocol['solver_sha256']
    metadata=read('run/metadata.json')
    assert metadata['returncode']==0 and json.loads(metadata['stdout'])==freeze['catalogue']
    assert freeze['catalogue']['sha256']==digest(freeze['catalogue']['models'])
    allocation_bytes=(folder/'allocation.json').read_bytes()
    reservation_bytes=(folder/'reservations.json').read_bytes()
    assert hashlib.sha256(allocation_bytes).hexdigest()==freeze['allocation_sha256']
    assert hashlib.sha256(reservation_bytes).hexdigest()==freeze['reservation_sha256']
    observations={tid:{'units':{k:v['unit'] for k,v in freeze['objective']['channels'].items()},
                       'rows':exp['rows']} for tid,exp in freeze['experiments'].items()}
    index=0
    def saved_prediction(parameters):
        nonlocal index
        directory=f'run/candidate-{index:05d}'
        assessment=read(directory+'/assessment.json');assert assessment==saved['candidates'][index]
        assert assessment['parameters']==parameters
        predictions={}
        for i,tid in enumerate(freeze['allocation']['calibration_packages'][freeze['objective']['package']]):
            prepared=read(directory+f'/{i:03d}-request.json');request=prepared['request']
            assert prepared['test_id']==tid
            assert prepared['provenance']['request_sha256']==digest(request)
            assert request['parameters']==[parameters[n] for n in freeze['model']['parameters']]
            # The identical fixed first-observation preparation is required for all candidates.
            first=read(f'run/candidate-00000/{i:03d}-request.json')['request']
            assert request['initial']==first['initial'] and request['path']==first['path']
            response=read(directory+f'/{i:03d}-response.json')
            assert response['ok'] is True and response['catalogue_hash']==freeze['catalogue']['sha256']
            assert response['parameters']==request['parameters'] and response['initial']==request['initial']
            assert response['specification']==request and response['request_sha256']==digest(request)
            rows=observations[tid]['rows'];assert len(response['points'])==len(rows)
            points=[]
            for j,(point,row) in enumerate(zip(response['points'],rows)):
                assert point['coordinate']==j
                stress,strain=point['state'],point['strain']
                volume=math.fsum(strain[:3])-math.fsum(request['path']['initial_strain'][:3])
                values={'q':stress[0]-(stress[1]+stress[2])/2,'p':sum(stress[:3])/3,'volumetric_strain':volume}
                points.append(dict(observation_index=j,axial_strain=row['axial_strain'],
                    **{name:values[name] for name in observations[tid]['units']}))
            predictions[tid]={'units':observations[tid]['units'],'status':'success','points':points}
        index+=1
        return predictions
    replay=calibrate(freeze['search'],saved_prediction,freeze['objective'],freeze['allocation'],
        freeze['reservations'],observations,allocation_sha256=freeze['allocation_sha256'],
        reservation_sha256=freeze['reservation_sha256'])
    assert index==3 and replay==saved
    assert [r['parameters']['E'] for r in saved['candidates']]==protocol['expected_E_sequence']
    assert saved['best']['parameters']['E']==protocol['expected_best_E']
    assert saved['best']['objective']<=protocol['maximum_best_objective']
    result={'passed':True,'saved_candidates_replayed':3,'native_calls':0,'builds':0,
            'all_file_hashes_match':True,'search_result_exact':True,'scientific_admission':False}
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',nargs='?',type=Path,default=Path(__file__).parent/'evidence')
    verify(parser.parse_args().folder)
