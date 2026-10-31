"""Executable-location rebinding tests; no private evidence or processes."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('tmd7_recovery', HERE / 'recover.py')
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class Saved:
    def __init__(self, expected):
        self.expected = expected
        self.calls = []

    def run(self, command, **kwargs):
        if command != self.expected:
            raise ValueError('native command/order differs')
        self.calls.append((command, kwargs))
        return 'saved response only'


class Rebinding(unittest.TestCase):
    def test_only_executable_location_is_rebound_and_request_is_not_mutated(self):
        saved = Saved(['/original/solver', '--parameters', '1,2', '--initial', '3,4'])
        counts = []
        rebound = R.ReboundRequests(saved, Path('/snapshot/solver'), '/original/solver', counts)
        request = ['/snapshot/solver', '--parameters', '1,2', '--initial', '3,4']
        self.assertEqual(rebound.run(request, check=True), 'saved response only')
        self.assertEqual(request[0], '/snapshot/solver')
        self.assertEqual(saved.calls, [(saved.expected, {'check': True})])
        self.assertEqual(counts, [1])

    def test_unexpected_physical_executable_cannot_select_another_receipt(self):
        saved = Saved(['/original/solver', '--describe'])
        counts = []
        rebound = R.ReboundRequests(saved, '/snapshot/solver', '/original/solver', counts)
        with self.assertRaisesRegex(ValueError, 'unexpected physical executable'):
            rebound.run(['/different/solver', '--describe'])
        self.assertEqual(saved.calls, [])
        self.assertEqual(counts, [])

    def test_changed_nonlocation_argument_is_still_rejected_by_saved_tracker(self):
        saved = Saved(['/original/solver', '--parameters', '1,2'])
        counts = []
        rebound = R.ReboundRequests(saved, '/snapshot/solver', '/original/solver', counts)
        with self.assertRaisesRegex(ValueError, 'native command/order differs'):
            rebound.run(['/snapshot/solver', '--parameters', '1,3'])
        self.assertEqual(counts, [])


if __name__ == '__main__':
    unittest.main()
