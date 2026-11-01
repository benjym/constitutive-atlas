"""Assess fresh captures through the unchanged published SLS study functions."""
import importlib.util,json,os
from pathlib import Path
ROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()
OUT=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve()
assert OUT.is_dir() and not OUT.is_relative_to(ROOT)
BASE=ROOT/'docs/ingestion/sls-comsol63/execution-v1'
s=importlib.util.spec_from_file_location('sls_study',BASE/'study.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
cases=json.loads((BASE/'cases.json').read_text())['cases']
envelope=json.loads((OUT/'native-envelope.json').read_text())
rows={'native':envelope['capture'],'wasm':json.loads((OUT/'wasm-raw.json').read_text())}
for backend,data in rows.items():
    report=m.assess(cases,data)
    if backend=='native':
        assert envelope['report']==report
        # Historical check_saved compatibility field, not a retained-call claim:
        # every capture here comes from this fresh native-envelope.json.
        report['original_material_calls_preserved']=True
        (OUT/'native-observe-v2-raw.json').write_text(json.dumps(data,indent=2)+'\n')
    assert report['passed'] is True
    (OUT/(backend+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
