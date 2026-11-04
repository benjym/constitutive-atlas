"""Current source-rate behavior, separately from exact historical capsule replay."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CurrentSourceRates(unittest.TestCase):
    def check_current(self, folder, module, call, filename, historical_keys):
        # A fresh process avoids colliding packet-local reference/support modules.
        program = """
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]);folder=root/sys.argv[2]
sys.path.insert(0,str(folder))
module=__import__(sys.argv[3])
actual=module.run() if sys.argv[4]=='run' else module.assess(root)
expected=json.loads((folder/sys.argv[5]).read_text())
for key in json.loads(sys.argv[6]):
    if actual[key]!=expected[key]:raise ValueError('current numerical behavior changed: '+key)
for name,pin in actual.get('runtime_pins',{}).items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=pin:raise ValueError('current runtime pin mismatch')
print(json.dumps({'current_runtime_checked':True,'compiled_execution':False,'admission':False}))
"""
        result = subprocess.run([sys.executable, '-B', '-c', program, str(ROOT), folder,
                                 module, call, filename, json.dumps(historical_keys)],
                                cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['current_runtime_checked'])

    def test_sand_all_current_rates_and_rejections(self):
        self.check_current('docs/ingestion/barodesy-sand/rate-study-v2', 'check',
                           'run', 'python-report.json', ['records', 'invalid'])

    def test_clay_current_rates_rejections_and_spd_support(self):
        self.check_current('docs/ingestion/hypoplastic-clay-2005/rate-study-v2', 'check_study',
                           'assess', 'checks.json',
                           ['rate_cases', 'historical_invalids', 'support_cases'])


if __name__ == '__main__':
    unittest.main()
