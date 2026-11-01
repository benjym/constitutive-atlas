"""Post-observation descriptive audit; saved outputs only, no new acceptance gate."""
import json
from pathlib import Path
import sys
from assess import context, read_records, csv


def diagnose(directory):
    ctx=context();records=read_records(directory);rows=[]
    for request in ctx['requests']:
        response=records[request['id']];pressure=sum(csv(request['args'][2])[:3])/3
        worst={'scaled_error':-1}
        field_max=[0.0]*25
        for sample_index,(index,reference) in enumerate(zip(request['sample_indices'],ctx['references'][request['case']]['samples'])):
            state=response['points'][index]['state']
            for component,(actual,expected) in enumerate(zip(state[:25],reference['state'])):
                error=abs(actual-float(expected))/(pressure if component<6 else 1)
                field_max[component]=max(field_max[component],error)
                if error>worst['scaled_error']:
                    worst={'scaled_error':error,'point':index,'sample':sample_index,'component':component,'actual':actual,'reference':float(expected)}
        symmetry=None
        if request['case'].startswith('extension-'):
            points=response['points']
            gap,index=max((abs(p['state'][1]-p['state'][2]),i) for i,p in enumerate(points))
            first=next((i for i,p in enumerate(points) if abs(p['state'][1]-p['state'][2])>1e-3),None)
            symmetry={'maximum_sigma_yy_zz_gap_Pa':gap,'maximum_gap_point':index,'first_gap_above_1e-3_Pa_point':first,
                      'threshold_is_descriptive_not_frozen_gate':True,'endpoint_sigma':points[-1]['state'][:6]}
        rows.append({'id':request['id'],'case':request['case'],'plastic_steps':request['plastic_steps'],'ok':response.get('ok'),
                     'points':len(response['points']),'worst':worst,'maximum_scaled_error_per_persistent_component':field_max,
                     'extension_symmetry':symmetry,'material_trials':response['material_trials'],'attempted_substeps':response['attempted_substeps']})
    refinement=[]
    for case in sorted({r['case'] for r in rows}):
        by_n={r['plastic_steps']:r['worst']['scaled_error'] for r in rows if r['case']==case}
        refinement.append({'case':case,'errors_by_steps':by_n,'512_over_256':by_n[512]/by_n[256] if by_n[256] else None,
                           '1024_over_512':by_n[1024]/by_n[512] if by_n[512] else None})
    return {'kind':'post-observation-saved-only-descriptive-audit','candidate_calls':0,'new_acceptance_gates':False,
            'all_81_paths_completed':all(r['ok'] is True for r in rows),
            'fine_paths_above_original_accuracy_gate':[r['id'] for r in rows if r['plastic_steps']==1024 and r['worst']['scaled_error']>.01],
            'rows':rows,'all_path_refinement_including_failed_accuracy':refinement,
            'interpretation':'Low-pressure extension outputs can lose yy/zz symmetry despite symmetric initial state and loading. This explains large observed component errors but does not establish whether the cause is residual transcription, continuous-law transverse instability, multiple discrete roots or Newton branch selection. No candidate changes or extra integrations.'}


if __name__=='__main__':print(json.dumps(diagnose(Path(sys.argv[1])),indent=2,allow_nan=False))
