"""Pure fixed-current dependency guard tests. No real bundler or module calls."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
from tools import check_current_dependency_assets as guard


class CurrentDependencyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='current-dependency-pure-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.original_engines = dict(guard.ENGINES)
        self.root_patch = patch.object(guard, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.sources_patch = patch.object(guard, 'source_snapshot', return_value={'pure-fixture':'unchanged'})
        self.source_mock = self.sources_patch.start()
        self.addCleanup(self.sources_patch.stop)
        self.calls = []
        for key,name in guard.ENGINES.items():
            for member in guard.REQUIRED[key]:
                path = self.root/name/member
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fake bytes; no numerical artifact\n')
        def make(key):
            def action(destination, build):
                self.calls.append((key,destination,build))
                self.assertEqual(build, self.root/guard.ENGINES[key])
                self.assertFalse(destination.exists())
                destination.mkdir(parents=True)
                (destination/'mock-package.json').write_text(json.dumps({'mock':key}))
                return {'mock_identity':key}
            return action
        self.actions = {key:make(key) for key in guard.ENGINES}
        self.actions_patch = patch.object(guard, 'bundlers', return_value=self.actions)
        self.actions_patch.start()
        self.addCleanup(self.actions_patch.stop)
        self.output = self.root/'reports'

    def report(self):
        return json.loads((self.output/'report.json').read_text())

    def test_exact_fixed_current_paths(self):
        self.assertEqual(guard.ENGINES, {
            'norsand':'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine',
            'interface2016':'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine',
            'maxwell':'docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine'})

    def test_three_guards_and_temporary_cleanup(self):
        before=guard.engine_snapshot()
        result=guard.check(self.output)
        self.assertEqual(list(result['packages']), list(guard.ENGINES))
        self.assertEqual(result['compiled_calls'], 0)
        self.assertEqual(result['before'],result['after'])
        self.assertEqual(before,guard.engine_snapshot())
        self.assertEqual(len(self.calls),3)
        self.assertTrue(all(not dest.exists() for _,dest,_ in self.calls))
        self.assertEqual(guard.ENGINES,self.original_engines)

    def test_missing_current_qualification_cannot_fallback(self):
        for key,filename in [('norsand','refresh-qualification.json'),('interface2016','refresh-qualification.json'),('maxwell','maxwell-qualification.json')]:
            with self.subTest(key=key):
                p=self.root/guard.ENGINES[key]/filename
                data=p.read_bytes();p.unlink()
                output=self.root/('missing-'+key)
                with self.assertRaisesRegex(ValueError,'Required current'):
                    guard.check(output)
                self.assertEqual(json.loads((output/'report.json').read_text())['status'],'failed')
                p.write_bytes(data)
        self.assertEqual(self.calls,[])

    def test_missing_engine_retains_failure(self):
        path=self.root/guard.ENGINES['maxwell']
        path.rename(path.with_name('unavailable'))
        with self.assertRaises(ValueError):guard.check(self.output)
        self.assertEqual(self.report()['status'],'failed')
        self.assertEqual(self.calls,[])

    def test_stale_guard_retains_partial_report_and_inputs(self):
        before=guard.engine_snapshot()
        def stale(*args):raise ValueError('stale exact accepted binding')
        self.actions['maxwell']=stale
        with self.assertRaisesRegex(ValueError,'stale exact'):guard.check(self.output)
        self.assertEqual(set(self.report()['packages']),{'norsand','interface2016'})
        self.assertEqual(guard.engine_snapshot(),before)
        self.assertTrue(all(not dest.exists() for _,dest,_ in self.calls))

    def test_engine_mutation_rejected(self):
        original=self.actions['norsand']
        def mutate(dest,build):
            result=original(dest,build)
            (build/'atlas_path_capability.wasm').write_text('changed fake bytes')
            return result
        self.actions['norsand']=mutate
        with self.assertRaisesRegex(ValueError,'changed during'):guard.check(self.output)
        self.assertNotEqual(self.report()['before']['engines'],self.report()['after']['engines'])

    def test_source_mutation_rejected(self):
        self.source_mock.side_effect=[{'source':'before'},{'source':'after'},{'source':'after'}]
        with self.assertRaisesRegex(ValueError,'changed during'):guard.check(self.output)
        self.assertEqual(self.report()['status'],'failed')

    def test_symlink_engine_root_rejected_and_reported(self):
        path=self.root/guard.ENGINES['maxwell'];target=path.with_name('actual');path.rename(target);path.symlink_to(target,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'Symlink'):guard.check(self.output)
        self.assertEqual(self.report()['status'],'failed')
        self.assertEqual(self.calls,[])

    def test_symlink_member_rejected(self):
        path=self.root/guard.ENGINES['maxwell']/'maxwell.js';path.unlink();target=self.root/'outside';target.write_text('fake');path.symlink_to(target)
        with self.assertRaisesRegex(ValueError,'Nonregular'):guard.check(self.output)
        self.assertEqual(self.report()['status'],'failed')

    def test_traversal_absolute_and_parent_symlink_rejected(self):
        for name in ('../outside','/outside'):
            with self.subTest(name=name),self.assertRaises(ValueError):guard.repo_path(name)
        parent=self.root/'linked';parent.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):guard.repo_path('linked/a')

    def test_existing_output_preserved(self):
        self.output.mkdir();marker=self.output/'preserve';marker.write_text('original')
        with self.assertRaises(ValueError):guard.check(self.output)
        self.assertEqual(marker.read_text(),'original')
        self.assertFalse((self.output/'report.json').exists())
        self.assertEqual(self.calls,[])

    def test_output_inside_engine_rejected(self):
        before=guard.engine_snapshot()
        with self.assertRaises(ValueError):guard.check(self.root/guard.ENGINES['maxwell']/'report-output')
        self.assertEqual(before,guard.engine_snapshot())

    def test_symlink_output_parent_rejected(self):
        path=self.root/'link';path.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):guard.check(path/'reports')
        self.assertEqual(self.calls,[])

    def test_all_three_actions_required(self):
        del self.actions['maxwell']
        with self.assertRaisesRegex(ValueError,'All three'):guard.check(self.output)
        self.assertEqual(self.report()['status'],'failed')
        self.assertEqual(self.calls,[])


if __name__=='__main__':unittest.main()
