"""One current-engine KFS development replay; saved-only reconstruction.

run NEW_ABSOLUTE_DIRECTORY executes the current engine only.
audit DIRECTORY reconstructs both predictions without native execution.
Raw measurements, trajectories and native process outputs remain private.
"""
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

R=module('current_tmd7_old_run',HERE.parent/'kfs-tmd13-evaluation-propagation-v1/run_case.py')
A=module('current_tmd7_saved',HERE.parent/'kfs-tmd13-evaluation-propagation-v1/assess.py')
OLD=R.OLD


def sha(path):return OLD.digest(path.read_bytes())
def read(path):return OLD.loads(path.read_bytes())

def inputs():
    freeze=read(HERE/'freeze.json');policy=read(HERE/'policy.json')
    OLD.require(sha(HERE/'policy.json')==freeze['policy_sha256'],'policy changed')
    OLD.require(sha(Path(__file__))==freeze['runner_assessor_sha256'],'runner/assessor changed')
    for name,digest in policy['input_sha256'].items():
        OLD.require(sha(ROOT/name)==digest,'input changed: '+name)
    oldpolicy,_,report,states=R.inputs()
    record=oldpolicy['cases'][policy['baseline_case_index']]
    OLD.require(record==policy['record'],'baseline case differs')
    experiment,rows,saved=R.prepare(record,oldpolicy,report,states)
    OLD.require(len(rows)==policy['observations'],'observation window differs')
    OLD.require(oldpolicy['maximum_increment']==policy['maximum_increment'],'caller ceiling differs')
    OLD.require(oldpolicy['selected'][record['calibration_scenario']]['parameters']==policy['parameters'],'vector differs')
    return policy,freeze,experiment,rows


def verify_baseline(policy):
    directory=Path(policy['baseline_directory'])
    for name,digest in policy['baseline_files'].items():
        OLD.require(sha(directory/name)==digest,'baseline changed: '+name)
    return directory


def setup(tracker,policy,engine):
    entry=policy['engines'][engine]
    adapter=OLD.adapter_class(tracker)(Path(entry['path']),[R.MODEL],ROOT/entry['model_directory'])
    OLD.require(adapter.solver_hash==entry['artifact_sha256'] and adapter.catalogue_hash==entry['catalogue_hash'],'engine identity changed')
    return adapter


def predict(adapter,policy,experiment,rows):
    result=adapter.replay(R.MODEL,policy['parameters'],experiment,[r['axial_strain'] for r in rows],
                          policy['maximum_increment'],policy['timeout_seconds'])
    OLD.require(result['status']=='success' and result['completed_observations']==len(rows),'failed or partial replay')
    OLD.require(result['native_calls']==policy['segments'],'segment coverage differs')
    return result


def saved_prediction(directory,summary,policy,engine,experiment,rows):
    ledger=read(directory/'processes.json')
    OLD.require(all(type(r['returncode']) is int and r['returncode']==0 for r in ledger),'unsuccessful integer process code')
    tracker=A.SavedProcesses(directory,summary,policy['engines'][engine]['catalogue_hash'])
    prediction=predict(setup(tracker,policy,engine),policy,experiment,rows);tracker.finish()
    content=(directory/'prediction.json').read_bytes()
    OLD.require(OLD.digest(content)==summary['prediction_sha256'],'prediction checksum differs')
    OLD.require(A.without_elapsed(prediction)==A.without_elapsed(OLD.loads(content)),'full native prediction reconstruction differs')
    return prediction,ledger


def validate_native(directory,ledger,policy):
    diagnostics={'substeps':0,'rejected':0,'iterations':0};points=0
    for receipt in ledger[1:]:
        command=receipt['command'];options=dict(zip(command[1::2],command[2::2]));raw=read(directory/receipt['stdout'])
        state=list(map(float,options['--initial'].split(',')));target=float(options['--target']);steps=int(options['--steps'])
        OLD.require(raw['model']==R.MODEL and raw['protocol']==1 and raw['cycles']==0,'native protocol differs')
        OLD.require(raw['initial']==state and raw['parameters']==list(policy['parameters'][n] for n in policy['parameter_names']),'native vector/initial echo differs')
        OLD.require(raw['target']==target and raw['steps']==steps and len(raw['points'])==steps+1,'native target/count differs')
        OLD.require(raw['points'][0]['state']==state,'native segment initial differs')
        for i,p in enumerate(raw['points']):
            OLD.require(len(p['state'])==7 and len(p['strain'])==6,'native layout differs')
            OLD.require(all(type(x) in (int,float) and math.isfinite(x) for x in p['state']+p['strain']),'invalid native state')
            OLD.require(abs(p['strain'][0]-target*i/steps)<=1e-13,'native caller coordinate differs')
            OLD.require(abs(p['state'][1]-p['state'][2])<=1e-6,'native axisymmetry differs')
            OLD.require(max(abs(p['state'][k]-state[k]) for k in (1,2))<=policy['radial_stress_tolerance_pa'],'native radial control differs')
            OLD.require(abs(p['q_signed']-(p['state'][0]-.5*(p['state'][1]+p['state'][2])))<=1e-7,'native q binding differs')
            for key in diagnostics:
                OLD.require(type(p[key]) is int and p[key]>=0,'invalid native counters');diagnostics[key]+=p[key]
        points+=steps
    return {'caller_increments':points,'diagnostics':diagnostics}


def comparison(current,baseline,policy,rows):
    maxima={'stress_pa':0.,'void_ratio':0.,'strain':0.,'q_pa':0.,'volumetric_strain':0.}
    for a,b in zip(current['points'],baseline['points']):
        OLD.require(a['observation_index']==b['observation_index'] and a['axial_strain']==b['axial_strain'],'acquisition knot/order differs')
        maxima['stress_pa']=max(maxima['stress_pa'],max(abs(x-y) for x,y in zip(a['state'][:6],b['state'][:6])))
        maxima['void_ratio']=max(maxima['void_ratio'],abs(a['state'][6]-b['state'][6]))
        maxima['strain']=max(maxima['strain'],max(abs(x-y) for x,y in zip(a['strain'],b['strain'])))
        maxima['q_pa']=max(maxima['q_pa'],abs(a['q']-b['q']))
        maxima['volumetric_strain']=max(maxima['volumetric_strain'],abs(a['volumetric_strain']-b['volumetric_strain']))
    scales=policy['channel_scales']
    changes={c:OLD.compare_acquisition_linear(baseline['points'],current,c,scales[c]) for c in scales}
    errors={engine:{c:OLD.compare_acquisition_linear(rows,prediction,c,scales[c]) for c in scales}
            for engine,prediction in [('archived',baseline),('current',current)]}
    gates={key:value<=policy['maximum_difference_limits'][key] for key,value in maxima.items()}
    for channel in scales:
        gates[channel+'_scaled_rms']=math.sqrt(changes[channel]['scaled_mse'])<=policy['scaled_rms_limits'][channel]
    return {'maximum_differences':maxima,'response_change':changes,'experimental_errors':errors,'gates':gates,
            'overall_compatibility_pass':all(gates.values())}


def audit(directory):
    policy,freeze,experiment,rows=inputs();baseline_dir=verify_baseline(policy)
    baseline,oldledger=saved_prediction(baseline_dir,read(baseline_dir/'summary.json'),policy,'archived',experiment,rows)
    OLD.require(read(directory/'execution-freeze.json')=={'freeze_sha256':sha(HERE/'freeze.json'),'policy_sha256':sha(HERE/'policy.json')},'execution freeze differs')
    summary=read(directory/'summary.json')
    OLD.require(summary['status']=='success' and summary['policy_sha256']==freeze['policy_sha256'],'run incomplete or changed')
    current,newledger=saved_prediction(directory,summary,policy,'current',experiment,rows)
    # Each engine chains its own committed state; all other segment inputs must
    # remain byte-identical to the archived request. Full replay above verifies
    # the independently chained --initial values against actual native receipts.
    for old,new in zip(oldledger[1:],newledger[1:]):
        def controls(row):
            args=row['command'];return {k:v for k,v in zip(args[1::2],args[2::2]) if k!='--initial'}
        OLD.require(controls(old)==controls(new),'segment request overlay differs')
    details={engine:validate_native(path,ledger,policy) for engine,path,ledger in
             [('archived',baseline_dir,oldledger),('current',directory,newledger)]}
    OLD.require(details['archived']['caller_increments']==details['current']['caller_increments']==policy['caller_increments'],'caller increment coverage differs')
    result={'id':policy['id'],'policy_sha256':sha(HERE/'policy.json'),'experiment_id':policy['record']['experiment_id'],
            'scope':'existing development window only; previously inspected, not blind',
            'observations':len(rows),'segments':policy['segments'],'current_processes':len(newledger),
            'baseline_receipts_reconstructed':len(oldledger),'diagnostics':details,
            'maximum_radial_stress_drift_pa':{engine:pred['maximum_radial_stress_drift_Pa'] for engine,pred in [('archived',baseline),('current',current)]},
            'current_artifact_sha256':policy['engines']['current']['artifact_sha256'],
            'current_source_commit':policy['engines']['current']['source_commit'],
            'fits':0,'builds':0,'scientific_admission':False,'limits':policy['limits']}
    result.update(comparison(current,baseline,policy,rows));return result


def run(directory):
    policy,freeze,experiment,rows=inputs();baseline_dir=verify_baseline(policy)
    # Validate and reconstruct the archived control BEFORE current observations.
    saved_prediction(baseline_dir,read(baseline_dir/'summary.json'),policy,'archived',experiment,rows)
    OLD.require(directory.is_absolute() and not directory.exists() and ROOT not in directory.parents,'new absolute output outside repository required')
    directory.mkdir(parents=True)
    OLD.write(directory/'execution-freeze.json',{'freeze_sha256':sha(HERE/'freeze.json'),'policy_sha256':sha(HERE/'policy.json')})
    tracker=OLD.RecordedProcesses(directory,policy['engines']['current']['catalogue_hash'])
    summary={'status':'failed','policy_sha256':freeze['policy_sha256']}
    OLD.write(directory/'summary.json',summary)
    try:
        adapter=setup(tracker,policy,'current');prediction=predict(adapter,policy,experiment,rows)
        OLD.write(directory/'prediction.json',prediction)
        summary.update(status='success',native_calls=prediction['native_calls'],prediction_sha256=sha(directory/'prediction.json'))
    except Exception as exc:
        summary['error']=str(exc);raise
    finally:
        summary.update(processes=len(tracker.records),process_receipts_sha256=sha(directory/'processes.json') if tracker.records else None)
        OLD.write(directory/'summary.json',summary)
    result=audit(directory);OLD.write(directory/'results.json',result)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':
    OLD.require(len(sys.argv)==3 and sys.argv[1] in ['run','audit'],'usage: replay.py run|audit DIRECTORY')
    if sys.argv[1]=='run':run(Path(sys.argv[2]))
    else:print(json.dumps(audit(Path(sys.argv[2])),indent=2,allow_nan=False))
