"""Separate post-observation diagnostic; never changes the qualification gate."""
from pathlib import Path
import hashlib,json,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2]
def run():
    freeze=json.loads((P/'rounding-diagnostic-freeze.json').read_text())
    assert hashlib.sha256((P/'rounding_diagnostic.py').read_bytes()).hexdigest()==freeze['script_sha256']
    assert hashlib.sha256((P/'assessment.json').read_bytes()).hexdigest()==freeze['assessment_sha256']
    spec=importlib.util.spec_from_file_location('history_saved_assessment',P/'assess.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);g,exact=a.references(ROOT)
    inputs=json.loads((P/'inputs.json').read_text());width=2*inputs['parameters']['k'];report=json.loads((P/'assessment.json').read_text());out={}
    for backend in ('native','wasm'):
        raw={row['step']:row for row in map(json.loads,(P/(backend+'-responses.jsonl')).read_text().splitlines())if 'step'in row};details=[]
        for row in report[backend]['steps']:
            if not row['accepted']:continue
            rounded=[a.encoded([float(x)for x in ref['returned_state']])for ref in row['references']];assert rounded[0]==rounded[1]
            actual=raw[row['step']]['output_bits'];values=a.decode(rounded[0]);inside=exact.range_le(values[:6],width);assert inside==exact.sturm_range_le(values[:6],width)
            details.append({'step':row['step'],'independently_nearest_rounded_state_bits':rounded[0],'rounded_independent_stress_admissible':inside,'actual_stress_matches_nearest_rounding':actual[:6]==rounded[0][:6],'actual_full_state_matches_nearest_rounding':actual==rounded[0],'different_components':[i for i,(x,y)in enumerate(zip(actual,rounded[0]))if x!=y]})
        out[backend]=details
    return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
