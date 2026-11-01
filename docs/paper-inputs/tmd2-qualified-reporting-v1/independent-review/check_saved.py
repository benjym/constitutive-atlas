"""Read-only independent paper projection audit; no rendering/imports/process calls."""
import hashlib
import json
import math
from pathlib import Path
HERE = Path(__file__).resolve().parent
PACKET = HERE.parent
ROOT = HERE.parents[3]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    own = read(HERE/'manifest.json')
    for name,digest in own['inputs'].items():
        require(sha(ROOT/name) == digest, 'changed input '+name)
    for name,digest in own['outputs'].items():
        require(sha(HERE/name) == digest, 'changed review output '+name)
    pins = read(PACKET/'inputs.json')
    require(len(pins) == 7, 'seven fixed public inputs')
    for name,digest in pins.items():
        require(sha(ROOT/name) == digest, 'changed accepted input '+name)
    decision = read(ROOT/'docs/benchmarks/kfs-tmd2-reporting-agent-v1/decision.json')
    accepted = read(ROOT/'docs/benchmarks/kfs-tmd2-reporting-agent-v1/manifest.json')
    summary_path = 'docs/benchmarks/kfs-tmd2-portable-v1/results/summary.json'
    summary = read(ROOT/summary_path)
    require(decision['verdict'] == 'accept-qualified-reporting' and not decision['blocking_findings_for_stated_scope'], 'accepted scope')
    require(decision['summary_sha256'] == pins[summary_path] == accepted['public_inputs'][summary_path], 'review-summary chain')
    product = read(PACKET/'generated/reporting.json')
    require(product['input_sha256'] == pins, 'input identities not projected exactly')
    require(product['model_sha256'] == decision['model_sha256'], 'definition identity')
    require(product['mandatory_qualifications'] == decision['remaining_qualifications'] and len(product['mandatory_qualifications']) == 7, 'seven qualifications')
    require(all(product[k] is False for k in ['model_admission','held_out_validation','measurement_redistribution_permission','fresh_engine_qualification']), 'ungranted authority')
    require(len(product['error_rows']) == len(summary['paths']) == 3, 'three paths')
    metrics = ['rmse','mae','maximum_absolute_error']
    table_lines = (PACKET/'generated/tables.md').read_text().splitlines()
    latex = (PACKET/'generated/errors-tabular.tex').read_text()
    count = 0
    for source,row in zip(summary['paths'],product['error_rows'],strict=True):
        require(row['id'] == source['id'] and row['saved_points'] == source['points'], 'path identity/count')
        require(row['caller_intervals']+1 == row['saved_points'] and row['target_accumulated_axial_fraction'] == .25, 'caller intervals/target')
        require(row['errors_SI'] == source['experimental_errors'], 'all full-precision SI scalars')
        require(row['experimental_overlap_accumulated_axial_fraction'] == source['experimental_overlap'], 'overlap')
        display = []
        for channel,target,conversion in [('q','q_kPa',lambda v:v/1000),('volumetric_strain','trace_volume_percentage_points',lambda v:v*100)]:
            for metric in metrics:
                value = source['experimental_errors'][channel][metric]
                require(math.isfinite(value) and value >= 0, 'finite SI scalar')
                converted = conversion(value)
                require(row['display_errors'][target][metric] == converted, 'unit conversion')
                display.append(format(converted,'.6g'));count += 1
        cells = [str(row['caller_intervals']),str(row['saved_points'])]+display
        require('| '+' | '.join(cells)+' |' in table_lines, 'rounded Markdown errors')
        require(' & '.join(cells) in latex, 'rounded LaTeX errors')
    expected = [(pair,name,values) for pair in summary['refinement'] for name,values in pair['channels'].items()]
    require(len(expected) == len(product['refinement_rows']) == 4, 'four refinements')
    ratios = []
    for (pair,channel,values),row in zip(expected,product['refinement_rows'],strict=True):
        require(row['paths'] == pair['paths'] and row['channel'] == channel, 'pair allocation')
        require(row['maximum_difference_SI'] == values['maximum_difference'] and row['frozen_limit_SI'] == values['limit'], 'refinement SI values')
        factor = .001 if channel == 'q' else 100
        require(row['display_maximum_difference'] == values['maximum_difference']*factor and row['display_frozen_limit'] == values['limit']*factor, 'refinement units')
        ratio = values['maximum_difference']/values['limit']
        require(row['difference_to_limit_ratio'] == ratio and 0 < ratio < 1, 'ratio')
        ratios.append({'paths':row['paths'],'channel':channel,'ratio':ratio})
    rejected = read(ROOT/'docs/benchmarks/kfs-tmd2-reference-v1/rejection-assessment.json')['requests']
    require(product['historical_original_api_rejections'] == rejected and len(rejected) == 3, 'retained rejections')
    require(all(row['completed_points'] == 0 and row['returncode'] == 1 for row in rejected), 'empty API failures')
    witness = read(ROOT/'docs/reviews/tmd2-process-status-v1/witness.json')
    guard = read(ROOT/'docs/reviews/tmd2-process-status-v1/guard-results.json')
    require(product['process_status_witness'] == witness and witness['altered_returncode'] == 23 and witness['old_assessor_exit'] == 0, 'exit23 old false pass')
    require(product['corrected_process_guard'] == guard and guard['exit23_rejected'] is True, 'corrected rejection')
    md = '\n'.join(table_lines)
    require(all('- '+q in table_lines for q in decision['remaining_qualifications']), 'display qualifiers')
    require('not physical integration-error bounds' in md, 'refinement interpretation')
    caption = (PACKET/'generated/CAPTION.txt').read_text()
    require('without a new fit or material execution' in caption and 'finite-deformation output conversion remain unverified' in caption, 'caption scope')
    required = {'tables.md','errors-tabular.tex','refinement.png','refinement.svg','CAPTION.txt','reporting.json','render-runtime.json'}
    require({p.name for p in (PACKET/'generated').iterdir()} == required, 'seven public artifacts only')
    runtime = read(PACKET/'generated/render-runtime.json')
    require(runtime['backend'] == 'Agg' and runtime['new_solver_calls'] == runtime['new_fits'] == 0, 'render identity')
    return {'status':'PASS','input_bindings':len(own['inputs']),'output_bindings':len(own['outputs']),'frozen_public_sources':7,'full_precision_SI_errors':count,'paths':3,'refinement_checks':4,'ratios':ratios,'mandatory_qualifications':7,'original_empty_API_rejections':3,'exit23_false_pass_and_corrected_rejection':True,'artifacts':7,'material_calls':0,'private_inputs':0,'paper_tree_edits':0}

if __name__ == '__main__':
    print(json.dumps(main(),indent=2,allow_nan=False))
