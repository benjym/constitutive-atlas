"""Describe retained caller/adaptive partition diagnostics; never launch a solver."""
import argparse
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SPEC=importlib.util.spec_from_file_location('partition_refinement_assessor',HERE.parent/'kfs-propagation-refinement-v1/assess.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)
OLD=A.OLD


def segment_stats(directory,maximum_increment):
    ledger=OLD.loads((directory/'processes.json').read_bytes());segments=[];hist=Counter()
    totals={'caller_steps':0,'reported_substeps':0,'reported_rejected':0,'counter_relation_checks':0}
    for receipt in ledger[1:]:
        command=receipt['command'];raw=OLD.loads((directory/receipt['stdout']).read_bytes())
        target=float(command[command.index('--target')+1]);steps=int(command[command.index('--steps')+1])
        OLD.require(raw['target']==target and raw['steps']==steps==max(1,math.ceil(abs(target)/maximum_increment)),
                    'caller step count differs from ceiling policy')
        OLD.require(len(raw['points'])==steps+1,'native caller points incomplete')
        substeps=rejected=0
        for point in raw['points'][1:]:
            count=point['substeps'];reject=point['rejected']
            OLD.require(type(count) is int and type(reject) is int and count>0 and reject>=0,
                        'invalid diagnostic counters')
            OLD.require(count==2*(reject+1),'diagnostics do not match full binary rejection tree counts')
            totals['counter_relation_checks']+=1
            hist[(count,reject)]+=1;substeps+=count;rejected+=reject
        segments.append({'steps':steps,'substeps':substeps,'rejected':rejected,
                         'mean_axial_travel_per_reported_substep':abs(target)/substeps})
        totals['caller_steps']+=steps;totals['reported_substeps']+=substeps;totals['reported_rejected']+=rejected
    prediction=OLD.loads((directory/'prediction.json').read_bytes())
    OLD.require(totals['reported_substeps']==prediction['diagnostics']['substeps'] and
                totals['reported_rejected']==prediction['diagnostics']['rejected'],'aggregate counters differ')
    return segments,{'maximum_increment':maximum_increment,'native_segments':len(segments),**totals,
                     'counter_histogram':[{'substeps':s,'rejected':r,'caller_points':n} for (s,r),n in sorted(hist.items())]}


def interval_localization(reference,prediction,scale):
    """Exact integral of squared linear difference; acquisition index locators only."""
    OLD.require(len(reference)==len(prediction) and len(reference)>=2,'unequal curves')
    for a,b in zip(reference,prediction):OLD.require(a['axial_strain']==b['axial_strain'],'coordinates differ')
    areas=[]
    for i,(a,b) in enumerate(zip(reference,reference[1:]),1):
        width=b['axial_strain']-a['axial_strain'];OLD.require(width>=0,'decreasing coordinate unsupported in this diagnostic')
        left=(prediction[i-1]['q']-a['q'])/scale;right=(prediction[i]['q']-b['q'])/scale
        areas.append(width*(left*left+left*right+right*right)/3)
    total=math.fsum(areas);travel=reference[-1]['axial_strain']-reference[0]['axial_strain']
    OLD.require(travel>0 and total>0,'no nonzero diagnostic difference')
    top=sorted(enumerate(areas,1),key=lambda item:item[1],reverse=True)[:3]
    return {'normalized_rms':math.sqrt(total/travel),
            'largest_interval_contributions':[{'ending_observation_index':i,'squared_difference_share':area/total} for i,area in top],
            'top_three_squared_difference_share':math.fsum(area for _,area in top)/total}


def analyze(fine,coarse,prior):
    policy=OLD.loads((HERE/'policy.json').read_bytes())
    for path,sha in policy['input_sha256'].items():OLD.require(OLD.digest((ROOT/path).read_bytes())==sha,'input changed: '+path)
    source=OLD.loads((HERE/'source-receipt.json').read_bytes())
    OLD.require(OLD.digest((HERE/'source/solver-at-report-commit.hpp').read_bytes())==source['sha256'],'interpretive source changed')
    verified=A.assess(fine,coarse,prior)
    OLD.require(verified==OLD.loads((ROOT/'docs/benchmarks/kfs-propagation-refinement-v1/results.json').read_bytes()),
                'failed result not exactly reproduced')
    failures=[c for c in verified['checks'] if not c['adjacent_change_nonincreasing']]
    OLD.require([c['coarse_case']['index'] for c in failures]==policy['coarse_case_indices'],'failure selection changed')
    cases=[]
    for failed in failures:
        case=failed['coarse_case'];index=case['index'];levels=[];segments=[];curves=[]
        for step,path in zip(policy['levels'],(coarse/f'case-{index:02d}',fine/f'case-{index*2:02d}',fine/f'case-{index*2+1:02d}')):
            segment,stats=segment_stats(path,step);segments.append(segment);levels.append(stats)
            curves.append(OLD.loads((path/'prediction.json').read_bytes())['points'])
        OLD.require(len({len(s) for s in segments})==1,'different segment alignment')
        inverted=[i for i,(a,b) in enumerate(zip(segments[0],segments[1]),1)
                  if a['mean_axial_travel_per_reported_substep']<b['mean_axial_travel_per_reported_substep']]
        scale=next(r['metrics']['q']['scale'] for r in verified['cases'] if r['record']['coarse_case_index']==index)
        cm=interval_localization(curves[0],curves[1],scale);mf=interval_localization(curves[1],curves[2],scale)
        for actual,expected in [(cm['normalized_rms'],failed['coarse_to_medium']),(mf['normalized_rms'],failed['medium_to_fine'])]:
            OLD.require(math.isclose(actual,expected,rel_tol=2e-14,abs_tol=1e-20),'localization integral differs')
        cases.append({'case':case,'levels':levels,
                      'coarse_lower_mean_travel_per_reported_substep_than_medium_segments':len(inverted),
                      'first_five_inverted_segment_ending_observation_indices':inverted[:5],
                      'maximum_medium_to_coarse_mean_travel_per_reported_substep_ratio':max(b['mean_axial_travel_per_reported_substep']/a['mean_axial_travel_per_reported_substep'] for a,b in zip(segments[0],segments[1])),
                      'coarse_to_medium_q_difference':cm,'medium_to_fine_q_difference':mf})
    return {'id':policy['id'],'cases':cases,'failed_refinement_gate_preserved':verified['gate_passed'] is False,
            'native_process_receipts_reconstructed':verified['new_native_process_receipts']+verified['coarse_native_process_receipts_reconstructed'],
            'new_native_calls':0,'builds':0,'scientific_admission':False,
            'interpretation':'Nominal increment refinement is not monotone in the saved mean axial-travel/reported-substep proxy. This supports a partition-change explanation but cannot establish causality or recover complete accepted-step trees.',
            'binary_to_interpretive_source_build_receipt_available':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fine-dir',type=Path,required=True);parser.add_argument('--coarse-dir',type=Path,required=True)
    parser.add_argument('--prior-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=analyze(args.fine_dir,args.coarse_dir,args.prior_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
