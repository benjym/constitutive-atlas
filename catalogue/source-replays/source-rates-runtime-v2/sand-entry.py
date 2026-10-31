"""New numerical replay identity; original runtime metadata remains historical."""
import hashlib,json,sys,unittest
from pathlib import Path


def compare_reports(actual, expected):
    # Only runtime provenance is classified separately. All other fields and
    # numerical values retain the original exact-equality requirement.
    a,b=actual.copy(),expected.copy()
    runtime=a.pop('python_version')
    original_runtime=b.pop('python_version')
    if runtime!=sys.version or not isinstance(original_runtime,str) or not original_runtime:
        raise ValueError('invalid report runtime provenance')
    if a!=b:
        raise ValueError('original numerical source report changed')
    return {'current_python':runtime,'original_python':original_runtime,
            'runtime_metadata_equal':runtime==original_runtime}


def main():
    from atlas.model import ROOT
    folder=ROOT/'docs/ingestion/barodesy-sand/rate-study-v2'
    sys.path.insert(0,str(folder))
    import check
    actual=check.run()
    expected=json.loads((folder/'python-report.json').read_text())
    compare_reports(actual,expected)
    suite=unittest.defaultTestLoader.discover(str(folder),pattern='test_*.py')
    result=unittest.TestResult();suite.run(result)
    if result.errors or result.failures:raise ValueError(repr(result.errors+result.failures))
    if result.testsRun!=11:raise ValueError('original test group completeness')
    print(json.dumps({'id':'sand','original_report_sha256':hashlib.sha256((folder/'python-report.json').read_bytes()).hexdigest(),
        'original_numerical_report_exact':True,'runtime_metadata_separate':True,
        'original_python_groups':result.testsRun,'compiled_execution':False,'admission':False},sort_keys=True))


if __name__=='__main__':main()
