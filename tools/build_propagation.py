"""Explicit scalar projection of calibration propagation and both refinement outcomes."""
import hashlib
import math
from pathlib import Path
from tools.strict_observation_json import loads

CAL=Path('docs/benchmarks/kfs-tmd13-calibration-sensitivity-v1')
PROP=Path('docs/benchmarks/kfs-tmd13-evaluation-propagation-v1')
REF=Path('docs/benchmarks/kfs-propagation-refinement-v1')
NEST=Path('docs/benchmarks/kfs-nested-partitions-v1')
FOLDERS=(CAL,PROP,REF,NEST)
REPLAY=Path('docs/benchmarks/current-kfs-tmd7-v1')
BUILD=Path('docs/benchmarks/current-source-build-v1')
CURRENT_FOLDERS=(REPLAY,BUILD)
FILE='file_initial';ALT='original_table_disputed_e0';SCENARIOS=(FILE,ALT)
CHANNELS=('q','volumetric_strain')


def require(condition,message):
    if not condition:raise ValueError(message)


def number(value):
    require(type(value) in (int,float) and math.isfinite(value) and value>=0,'invalid scalar evidence')
    return value


def gates(result,policy,expected):
    checks=result['checks']
    keys=[(c['coarse_case']['index'],c['channel']) for c in checks]
    require(len(keys)==len(expected) and set(keys)==expected,'incomplete refinement coverage')
    maximum=0;failed=[]
    for c in checks:
        first=number(c['coarse_to_medium']);second=number(c['medium_to_fine'])
        signal=number(c['coarse_calibration_response_shift']);require(signal>0,'zero refinement signal')
        if 'calibration_signals' in policy:
            require(signal==policy['calibration_signals'][str(c['coarse_case']['index'])][c['channel']],'nested calibration signal differs')
        threshold=policy['gate']['separation_fraction']*signal
        separated=max(first,second)<=threshold
        nonincrease=second<=first+policy['gate']['nonincrease_absolute_floor']
        require(c['threshold']==threshold and c['both_below_separation_threshold'] is separated and
                c['adjacent_change_nonincreasing'] is nonincrease,'inconsistent refinement predicates')
        maximum=max(maximum,max(first,second)/signal)
        if not nonincrease:failed.append({'test':c['coarse_case']['experiment_id'],
             'calibration_scenario':c['coarse_case']['calibration_scenario'],'channel':c['channel'],
             'first_change':first,'second_change':second})
    return {'numerical_passed':all(c['both_below_separation_threshold'] and c['adjacent_change_nonincreasing'] for c in checks),
            'case_channel_checks':len(checks),'separation_passes':sum(c['both_below_separation_threshold'] for c in checks),
            'nonincrease_failures':len(failed),'maximum_fraction':maximum,
            'limit_fraction':policy['gate']['separation_fraction'],'failed':failed}


def current_replay(root,archived_definition,propagation):
    """Project public scalars only; never read experimental/native private files."""
    pins={}
    def checked(folder,name):
        content=(root/folder/name).read_bytes();digest=hashlib.sha256(content).hexdigest()
        manifest=loads((root/folder/'manifest.json').read_bytes())
        require(manifest['files'][name]==digest,'current replay evidence hash mismatch: '+str(folder/name))
        pins[str(folder/name)]=digest;return loads(content)
    policy=checked(REPLAY,'policy.json');result=checked(REPLAY,'results.json')
    verification=checked(REPLAY,'verification.json')
    build=checked(BUILD,'evidence/result.json');source=checked(BUILD,'source-manifest.json')
    require(result['policy_sha256']==pins[str(REPLAY/'policy.json')],'current replay policy binding differs')
    require(result['scientific_admission'] is False and result['fits']==0 and result['builds']==0,'unsupported current replay promotion')
    require(verification['full_saved_prediction_reconstruction']=='exact excluding elapsed_seconds only' and
            verification['public_scalar_reconstruction']=='exact' and verification['software_checks_passed']==6 and
            verification['software_checks_skipped']==0 and verification['new_native_calls_in_audit']==0 and
            verification['raw_arrays_published'] is False,'current replay audit incomplete')
    current=policy['engines']['current'];archived=policy['engines']['archived']
    require(result['current_artifact_sha256']==current['artifact_sha256']==build['artifact_sha256'] and
            result['current_source_commit']==current['source_commit']==build['source_commit']==source['source_commit'],
            'current replay build identity differs')
    require(policy['input_sha256'][str(BUILD/'evidence/result.json')]==pins[str(BUILD/'evidence/result.json')] and
            policy['input_sha256'][str(BUILD/'source-manifest.json')]==pins[str(BUILD/'source-manifest.json')],
            'current build dependency differs')
    model='models/hypoplastic-sand-vw96.json'
    require(source['files'][model]==policy['input_sha256'][model],'current built model identity differs')
    old='paper/results/pilot-matched96/models/hypoplastic-sand-vw96.json'
    require(policy['input_sha256'][old]==archived_definition,'archived replay definition differs')
    baseline=propagation['cases'][2]
    require(policy['record']==baseline['record'] and policy['record']['experiment_id']=='KFS-TMD7' and
            policy['baseline_files']['prediction.json']==baseline['prediction_sha256'],'archived replay control differs')
    require(policy['maximum_axial_strain']==.02 and policy['maximum_increment']==.0002 and
            result['observations']==policy['observations']==44 and result['segments']==policy['segments']==43 and
            result['current_processes']==policy['current_process_budget']==44 and result['baseline_receipts_reconstructed']==44,
            'current replay scope differs')
    expected={'stress_pa','void_ratio','strain','q_pa','volumetric_strain'}
    require(set(result['maximum_differences'])==set(policy['maximum_difference_limits'])==expected,'current replay state coverage differs')
    rows=[];gates={}
    for key in ('stress_pa','q_pa','void_ratio','strain','volumetric_strain'):
        value=number(result['maximum_differences'][key]);limit=number(policy['maximum_difference_limits'][key])
        gates[key]=value<=limit;rows.append({'quantity':key,'maximum_difference':value,'limit':limit,'passed':gates[key]})
    for channel in CHANNELS:
        rms=math.sqrt(number(result['response_change'][channel]['scaled_mse']));limit=number(policy['scaled_rms_limits'][channel])
        gates[channel+'_scaled_rms']=rms<=limit
        rows.append({'quantity':channel+'_scaled_rms','maximum_difference':rms,'limit':limit,'passed':gates[channel+'_scaled_rms']})
    require(result['gates']==gates and result['overall_compatibility_pass'] is all(gates.values()),'current replay gate differs')
    counts={}
    for engine in ('archived','current'):
        detail=result['diagnostics'][engine];d=detail['diagnostics']
        require(detail['caller_increments']==policy['caller_increments']==125 and
                all(type(d[k]) is int and d[k]>=0 for k in ('substeps','rejected','iterations')),'current replay diagnostics differ')
        counts[engine]={'caller_increments':detail['caller_increments'],'substeps':d['substeps'],'rejected':d['rejected']}
    errors=[{'channel':c,'rmse':number(result['experimental_errors']['current'][c]['rmse'])} for c in CHANNELS]
    return {'kind':'current-kfs-replay-summary','status':'provisional','scientific_admission':False,
       'test':'KFS-TMD7','observations':44,'segments':43,'current_processes':44,
       'maximum_axial_strain':.02,'maximum_increment':.0002,'passed':result['overall_compatibility_pass'],
       'rows':rows,'diagnostics':counts,'experimental_errors':errors,
       'source_commit':current['source_commit'],'artifact_sha256':current['artifact_sha256'],
       'current_definition_sha256':policy['input_sha256'][model],'archived_definition_sha256':archived_definition,
       'sources':[{'title':'Current-source TMD7 replay: fixed inputs, results and audit','url':'https://github.com/benjym/constitutive-atlas/tree/main/'+str(REPLAY)},
                  {'title':'Current native source and build receipt','url':'https://github.com/benjym/constitutive-atlas/tree/main/'+str(BUILD)}],
       'limitations':['One fixed density3 vector and recorded-file initialization; complete existing development window, not the full acquired test or blind evaluation.',
          'Compatibility with an archived prediction does not establish agreement with measurements, general engine equivalence or model admission.',
          'The historical executable still lacks an exact source/build receipt; the current executable has its own provenance.',
          'The six-test panels above remain archived results. The website Wasm engine is a separate artifact, not this native executable.',
          'The original refinement sequence remains failed. Raw curve redistribution rights and scientific admission remain open.'],
       'evidence_sha256':pins}


def summary(root,definition_sha256):
    root=Path(root);pins={}
    def checked(folder,name):
        manifest=loads((root/folder/'manifest.json').read_bytes());path=str(folder/name)
        content=(root/path).read_bytes();sha=hashlib.sha256(content).hexdigest()
        require(manifest['files'][path]==sha,'propagation evidence hash mismatch: '+path)
        pins[path]=sha;return loads(content)
    packets={f:(checked(f,'policy.json'),checked(f,'results.json')) for f in FOLDERS}
    for folder,(policy,result) in packets.items():
        require(result['scientific_admission'] is False,'unsupported scientific promotion')
        require(result['policy_sha256']==pins[str(folder/'policy.json')],'policy/result binding differs')
    cp,cal=packets[CAL];pp,prop=packets[PROP];rp,ref=packets[REF];np,nest=packets[NEST]
    require(pp['selected']==cal['selected'] and pp['input_sha256'][str(CAL/'results.json')]==pins[str(CAL/'results.json')],
            'calibration selection binding differs')
    model='paper/results/pilot-matched96/models/hypoplastic-sand-vw96.json'
    require(pp['input_sha256'][model]==definition_sha256,'archived definition differs')
    require(rp['input_sha256'][str(PROP/'results.json')]==pins[str(PROP/'results.json')] and
            np['input_sha256'][str(REF/'results.json')]==pins[str(REF/'results.json')],'refinement dependency differs')
    require(pp['evaluation_ids']==['KFS-TMD1','KFS-TMD5','KFS-TMD7','KFS-TMD9','KFS-TMD12','KFS-TMD14'],'evaluation coverage differs')
    require(len(cal['fits'])==6 and cp['optimizer']['seeds']==[0,17,41] and cp['optimizer']['max_evaluations']==96,
            'unsupported calibration budget')
    selections=[]
    for scenario in SCENARIOS:
        fits=[r for r in cal['fits'] if r['record']['scenario']==scenario]
        require(len(fits)==3 and [f['record']['seed'] for f in fits]==[0,17,41] and
                all(f['fit_status']=='success' and f['termination']=='budget_limit' and f['evaluation_count']==96 for f in fits),
                'incomplete budget-limited starts')
        chosen=min(fits,key=lambda f:number(f['best_objective']))
        require(cal['selected'][scenario]['parameters']==chosen['best_parameters'] and
                cal['selected'][scenario]['seed']==chosen['record']['seed'],'calibration-only selection differs')
        selections.append({'scenario':scenario,'seed':chosen['record']['seed'],'alpha':chosen['best_parameters']['alpha']})
    require(len(prop['cases'])==16 and [r['record'] for r in prop['cases']]==pp['cases'],'propagation cases differ')
    pairs={(c,e) for c in SCENARIOS for e in SCENARIOS}
    require(len(prop['panels'])==4 and {(r['calibration_scenario'],r['evaluation_scenario']) for r in prop['panels']}==pairs,
            'factorial panel coverage differs')
    panels=[]
    for panel in prop['panels']:
        indices=[];values=[]
        for eid in pp['evaluation_ids']:
            evaluation=panel['evaluation_scenario'] if eid in pp['disputed_evaluation_ids'] else FILE
            rows=[r for r in prop['cases'] if r['record']['calibration_scenario']==panel['calibration_scenario'] and
                  r['record']['evaluation_scenario']==evaluation and r['record']['experiment_id']==eid]
            require(len(rows)==1,'missing factorial panel member');indices.append(rows[0]['record']['index'])
            values.extend(number(rows[0]['metrics'][c]['scaled_mse']) for c in CHANNELS)
        score=math.sqrt(math.fsum(values)/len(values))
        require(panel['case_indices']==indices and panel['root_scaled_mse']==score and panel['tests']==6 and panel['channel_scores']==12,
                'factorial panel score differs')
        panels.append({'calibration_scenario':panel['calibration_scenario'],'evaluation_scenario':panel['evaluation_scenario'],
                       'root_scaled_mse':score})
    original=gates(ref,rp,{(i,c) for i in range(16) for c in CHANNELS})
    require(ref['gate_passed'] is original['numerical_passed'],'original gate differs')
    original['passed']=ref['gate_passed']
    nested=gates(nest,np,{(i,c) for i in (2,3,10,11) for c in CHANNELS})
    require(len(nest['cases'])==8 and [r['record'] for r in nest['cases']]==np['cases'],'nested case coverage differs')
    rejection_free=True;caller_points=0
    for row in nest['cases']:
        d=row['diagnostics'];count=d['caller_points']
        require(type(count) is int and count>0,'invalid caller count')
        require(type(d['reported_rejected']) is int and type(d['reported_substeps']) is int,'invalid diagnostic counters')
        expected=d['reported_rejected']==0 and d['reported_substeps']==2*count
        require(d['rejection_free_two_substep_gate'] is expected,'nested diagnostics differ')
        rejection_free &= expected;caller_points+=count
    passed=nested['numerical_passed'] and rejection_free
    require(nest['numerical_gate_passed'] is nested['numerical_passed'] and nest['rejection_free_gate_passed'] is rejection_free and
            nest['gate_passed'] is passed and nest['original_refinement_gate_remains_failed'] is (not original['passed']),
            'nested regime/original gate conflated')
    require(all(number(c['coarse_to_medium'])>0 for c in nest['checks']),'undefined refinement ratio')
    ratios=[number(c['medium_to_fine'])/number(c['coarse_to_medium']) for c in nest['checks']]
    nested.update(passed=passed,rejection_free=rejection_free,caller_points=caller_points,
                  ratio_min=min(ratios),ratio_max=max(ratios),
                  rows=[{'test':c['coarse_case']['experiment_id'],'calibration_scenario':c['coarse_case']['calibration_scenario'],
                         'channel':c['channel'],'first_change':c['coarse_to_medium'],'second_change':c['medium_to_fine']}
                        for c in nest['checks']])
    links=[{'title':'von Wolffersdorff (1996): original model publication',
            'url':'https://doi.org/10.1002/(SICI)1099-1484(199607)1:3<251::AID-CFM13>3.0.CO;2-3'}]
    for title,folder in [('Calibration-only selection and budgets',CAL),('Four-panel evaluation propagation',PROP),
                         ('Original failed refinement study',REF),('Separate nested caller regime',NEST)]:
        links.append({'title':title,'url':'https://github.com/benjym/constitutive-atlas/tree/main/'+str(folder)})
    replay=current_replay(root,definition_sha256,prop)
    require(loads((root/REPLAY/'policy.json').read_bytes())['parameters']==cal['selected'][FILE]['parameters'],'current replay calibration selection differs')
    return {'current_replay':replay,'kind':'kfs-propagation-summary','schema_version':'0.1','status':'provisional','scientific_admission':False,
            'definition_sha256':definition_sha256,'evaluation_tests':6,'panels':panels,'selections':selections,
            'calibration':{'starts_per_scenario':3,'candidate_budget_per_start':96,'selection':'calibration_only','all_budget_limited':True},
            'original_refinement':original,'nested':nested,
            'limitations':['Previously exposed development data; no blind validation or tuning on these evaluation scores.',
             'Source void ratios remain disputed; neither scenario is selected as physically correct by its error.',
             'Both calibration selections exhaust their search budgets; unique parameters and a global optimum are not established.',
             'The original refinement sequence remains failed. The nested result covers four cases in a different caller regime, not a new six-test panel or proof of cause/convergence order.',
             'Archived executable lacks an exact source-to-build receipt; current-engine equivalence and model admission remain open.'],
            'sources':links,'evidence_sha256':pins}
