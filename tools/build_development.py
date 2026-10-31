"""Export a scalar-only, source-bound KFS development view; no raw curves."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.strict_observation_json import loads

LOCKED=Path('docs/benchmarks/kfs-locked-initialization-sensitivity-v1')
REFINED=Path('docs/benchmarks/kfs-initialization-refinement-v1')


def summary(root=ROOT):
    root=Path(root);pins={}
    def checked(folder,name):
        manifest=loads((root/folder/'manifest.json').read_bytes())
        relative=str(folder/name);content=(root/relative).read_bytes()
        digest=hashlib.sha256(content).hexdigest()
        if manifest['files'][relative]!=digest:raise ValueError('development evidence hash mismatch: '+relative)
        pins[relative]=digest
        return loads(content)
    locked=checked(LOCKED,'results.json');policy=checked(LOCKED,'policy.json')
    refined=checked(REFINED,'results.json');refpolicy=checked(REFINED,'policy.json')
    if (locked['scientific_admission'] is not False or refined['scientific_admission'] is not False or
        locked['calibration_state_uncertainty_propagated'] is not False or
        refined['tmd13_calibration_propagated'] is not False):
        raise ValueError('unsupported scientific claim for this provisional view')
    if len(locked['panels'])!=4 or len(refined['checks'])!=16 or len(refined['initialization_shifts'])!=12:
        raise ValueError('incomplete development summary')
    pairs={(p,s) for p in ('pressure3','density3') for s in ('file_initial','original_table_disputed_e0')}
    if {(r['package'],r['scenario']) for r in locked['panels']}!=pairs or any(
        type(r['root_scaled_mse']) not in (int,float) or not math.isfinite(r['root_scaled_mse']) or r['root_scaled_mse']<0
        for r in locked['panels']):raise ValueError('invalid package score coverage')
    if {(c['coarse_case_index'],c['channel']) for c in refined['checks']}!={(i,c) for i in range(8) for c in ('q','volumetric_strain')}:
        raise ValueError('invalid refinement coverage')
    fraction=refpolicy['gate']['separation_fraction']
    floor=refpolicy['gate']['nonincrease_absolute_floor']
    for c in refined['checks']:
        separated=max(c['coarse_to_medium'],c['medium_to_fine'])<=fraction*c['coarse_initialization_signal']
        nonincrease=c['medium_to_fine']<=c['coarse_to_medium']+floor
        if (separated is not c['both_below_separation_threshold'] or nonincrease is not c['adjacent_change_nonincreasing']):
            raise ValueError('inconsistent refinement comparisons')
    passed=all(c['both_below_separation_threshold'] and c['adjacent_change_nonincreasing'] for c in refined['checks'])
    if passed!=refined['gate_passed']:raise ValueError('inconsistent refinement gate')
    maximum=max(max(c['coarse_to_medium'],c['medium_to_fine'])/c['coarse_initialization_signal'] for c in refined['checks'])
    # Construct fields individually: packet siblings, point/state arrays, requests,
    # raw observations, machine paths and per-process commands never enter export.
    result = {'kind':'kfs-development-summary','schema_version':'0.1','status':'provisional',
        'scientific_admission':False,'model_name':'Base VW96 sand hypoplasticity',
        'definition_sha256':policy['input_sha256']['paper/results/pilot-matched96/models/hypoplastic-sand-vw96.json'],
        'metric':policy['metric'],'evaluation_tests':6,'maximum_axial_strain':0.02,
        'scenarios':[{'id':'file_initial','label':'Recorded-file initialization',
                      'description':'Exact file void ratios and effective stresses; original locked development result.'},
                     {'id':'original_table_disputed_e0','label':'Original-table evaluation void ratios',
                      'description':'Change only TMD12 and TMD14 evaluation void ratios. Recorded stresses and fitted parameters stay fixed.'}],
        'scores':[{'package':r['package'],'scenario':r['scenario'],'root_scaled_mse':r['root_scaled_mse']}
                  for r in locked['panels']],
        'refinement':{'passed':passed,'limit_fraction':fraction,'maximum_fraction':maximum,
                      'levels':[0.0002,0.0001,0.00005],
                      'shifts':[{'package':r['package'],'test':r['experiment_id'],
                                 'maximum_increment':r['maximum_increment'],
                                 'q':r['normalized_rms_initialization_shift']['q'],
                                 'volume':r['normalized_rms_initialization_shift']['volumetric_strain']}
                                for r in refined['initialization_shifts']]},
        'limitations':['Previously inspected development tests; not blind validation.',
          'Four material constants fitted; four limiting-density/compression constants inherited from literature. Additional prior information remains explicit.',
          'The locked-fit panel holds calibration parameters fixed. The separate factorial panel propagates TMD13 calibration assumptions.',
          'The void-ratio source disagreement remains unresolved. Neither scenario is selected by error.',
          'Archived implementation and one material; no current-engine equivalence, cross-model ranking or scientific admission.'],
        'sources':[{'title':'Wichtmann & Triantafyllidis (2016), Table 3','url':'https://doi.org/10.1007/s11440-015-0402-z'},
          {'title':'Parameter information and inherited constants','url':'https://github.com/benjym/constitutive-atlas/tree/main/studies/kfs-development-v1/parameters-v1'},
          {'title':'Initialization scenarios and source qualifications','url':'https://github.com/benjym/constitutive-atlas/tree/main/studies/kfs-development-v1/initialization-v1'},
          {'title':'Locked-parameter sensitivity: frozen inputs and results','url':'https://github.com/benjym/constitutive-atlas/tree/main/'+str(LOCKED)},
          {'title':'Three-resolution output study','url':'https://github.com/benjym/constitutive-atlas/tree/main/'+str(REFINED)},
          {'title':'Ordered error metric definition','url':'https://github.com/benjym/constitutive-atlas/blob/main/docs/ORDERED_METRICS.md'}],
        'evidence_sha256':pins}
    from tools.build_propagation import summary as propagation_summary
    result['propagation']=propagation_summary(root,result['definition_sha256'])
    return result


def bundle(destination,root=ROOT):
    result=summary(root)  # Fail before writing public outputs.
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    for name in ('development.html','development.mjs','propagation.mjs'):
        shutil.copyfile(Path(root)/'web'/name,destination/name)
    (destination/'development.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    bundle(parser.parse_args().output)
