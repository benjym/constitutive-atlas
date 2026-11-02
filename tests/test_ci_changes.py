"""Ensure dependency changes cannot disappear behind the documentation shortcut."""
import subprocess
import unittest
from unittest.mock import patch
from tools.ci_changes import changed_paths, needs_numerical


class ChangeSelectionTests(unittest.TestCase):
    def test_prose_only_and_mixed_changes(self):
        self.assertFalse(needs_numerical(['README.md', 'docs/STATUS.md', 'docs/plot.png']))
        for path in ['CMakeLists.txt', 'cpp/include/atlas.hpp', 'atlas/compiler.py', 'models/new.json',
                     'docs/ingestion/example/cases.json', 'docs/ingestion/example/engine.zip',
                     'docs/ingestion/example/study.py', '.github/workflows/verify.yml',
                     'tools/ci_fast.py', 'web/app.js', 'unknown.config']:
            with self.subTest(path=path):
                self.assertTrue(needs_numerical(['README.md', path]))

    def test_unknown_event_or_history_runs_checks(self):
        self.assertIsNone(changed_paths({}, 'workflow_dispatch'))
        self.assertIsNone(changed_paths({'before':'0'*40}, 'push'))
        with patch('tools.ci_changes.subprocess.run', side_effect=subprocess.CalledProcessError(1,['git'])):
            self.assertIsNone(changed_paths({'before':'a'*40,'after':'b'*40}, 'push'))

    def test_pull_request_uses_merge_base_and_handles_spaces(self):
        event={'pull_request':{'base':{'sha':'a'*40},'head':{'sha':'b'*40}}}
        with patch('tools.ci_changes.subprocess.run', return_value=subprocess.CompletedProcess([],0,b'docs/a b.md\0web/app.js\0')) as call:
            self.assertEqual(changed_paths(event,'pull_request'),['docs/a b.md','web/app.js'])
            self.assertIn('a'*40+'...'+'b'*40,call.call_args.args[0])
