"""Run portable tests on Linux; keep exact historical replay gates on macOS.

The full unittest suite remains unchanged and runs in the required macOS job.
This separate Linux projection does not claim bit reproduction of Mac libm.
"""
import argparse
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
POLICY = ROOT / 'tools/ci_exact_replays.json'


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


class CanonicalReplay(unittest.TestCase):
    def __init__(self, original_id):
        super().__init__()
        self.original_id = original_id

    def id(self):
        return self.original_id

    def __str__(self):
        return self.original_id

    @unittest.skip('Exact archived macOS arithmetic; required macos-26 job runs the unchanged test')
    def runTest(self):
        pass


def portable_suite(suite, policy):
    tests = list(flatten(suite))
    names = {test.id() for test in tests}
    exact = set(policy['exact_test_ids'])
    if len(exact) != len(policy['exact_test_ids']) or not exact <= names:
        raise ValueError('exact-replay policy has duplicate or unknown test IDs: ' + repr(exact - names))
    if policy['canonical_runner'] != 'macos-26' or policy['canonical_python'] != '3.14':
        raise ValueError('unsupported exact-replay runtime policy')
    return unittest.TestSuite(CanonicalReplay(test.id()) if test.id() in exact else test
                              for test in tests)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portable', action='store_true', required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    policy = json.loads(POLICY.read_text())
    result = unittest.TextTestRunner(verbosity=2).run(portable_suite(suite, policy))
    raise SystemExit(not result.wasSuccessful())


if __name__ == '__main__':
    main()
