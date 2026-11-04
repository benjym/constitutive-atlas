"""Delegate unchanged continuous-reference analysis to its exact historical MCC."""
import hashlib, importlib.util, json
from pathlib import Path
from atlas.evidence import checked_receipt
ROOT=Path(__file__).resolve().parents[1]
def _original(report):
    context=json.loads((ROOT/'docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2/historical-routing-v1.json').read_text())
    name='tools/analyze_mcc_continuous.py'
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==context['pins'][name],name
    case=next(c for c in report['cases'] if c['id']=='mcc-plastic-isotropic-strain')
    model=checked_receipt(ROOT,'catalogue/investigations/recorded-refinement-v1/manifest.json',
                          'models/modified-cam-clay.json',case['model_sha256'])
    spec=importlib.util.spec_from_file_location('_original_mcc_continuous',ROOT/name)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=model.parents[1]
    return module
def analyze(report):return _original(report).analyze(report)
def analyze_followups(report,followup):return _original(report).analyze_followups(report,followup)
