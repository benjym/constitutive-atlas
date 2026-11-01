"""Source-only dispatch tests. Every process and executable is an explicit stand-in."""
import sys
sys.dont_write_bytecode=True
import base64,copy,json,math,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import check_native_fixture_dispatch as dispatch
from tools import check_md1997_native_fixture_contract as md

ROOT=Path(__file__).resolve().parents[1]

class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name).resolve();self.calls=[]
    def fixture(self,size='16'):
        source=self.base/('source'+size);build=self.base/('build'+size)
        for name in dispatch.IDENTITIES[size]['models']:
            p=source/'models'/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'models'/(name+'.json')).read_bytes())
        for name in ['tools/check_native_fixture_contracts.py','catalogue/laboratory-package-policy.json']:
            p=source/name;p.parent.mkdir(parents=True,exist_ok=True)
            if size=='14':
                # Archived helper/policy are test inputs stored as literal bytes
                # below, not substituted implementations.
                data=base64.b64decode(ARCHIVAL[name])
            else:data=(ROOT/name).read_bytes()
            p.write_bytes(data)
        (source/'CMakeLists.txt').write_bytes((ROOT/'CMakeLists.txt').read_bytes())
        models=[json.loads((source/'models'/(name+'.json')).read_text()) for name in sorted(dispatch.IDENTITIES[size]['models'])]
        blob={'schema_version':'0.1','sha256':dispatch.sha(json.dumps(models,sort_keys=True,separators=(',',':')).encode()),'models':models}
        (build/'generated').mkdir(parents=True)
        (build/'generated/models.json').write_text(json.dumps(blob,indent=2)+'\n')
        (build/'generated/models.hpp').write_text('// synthetic, not compiled\n')
        (build/'CMakeCache.txt').write_text('CMAKE_HOME_DIRECTORY:INTERNAL='+str(source)+'\n_Python3_EXECUTABLE:INTERNAL='+str(build/'mock-python')+'\n')
        (source/'tools/test_scalar_functions.py').write_text('# Explicit nonexecuted synthetic scalar test stand-in\n')
        scalar='libatlas_scalar_probe'+('.dylib'if sys.platform=='darwin'else '.so')
        for name in [row[1]for row in dispatch.REGISTRATIONS if row[1]]+['mock-ctest','mock-python',scalar]:(build/name).write_bytes(b'NONEXECUTABLE SYNTHETIC INPUT\n')
        rows=[]
        for name,target,args in dispatch.REGISTRATIONS:
            command=[str(build/target),*args]if target else [str(build/'mock-python'),*args]if name=='atlas_python'else [str(build/'mock-python'),str(source/'tools/test_scalar_functions.py'),str(build/scalar)]
            rows.append('add_test('+ ' '.join(json.dumps(x)for x in [name,*command])+')\n')
        (build/'CTestTestfile.cmake').write_text(''.join(rows))
        return source,build
    def occ(self,source):
        m=json.loads((source/'models/original-cam-clay-sw-electronic-log-recovery-v1.json').read_text());p={k:v['default']for k,v in m['parameters'].items()}
        v=m['state'][1]['initial']/(1+1e-4);pressure=p['pref']*math.exp((p['Gamma']+p['lambda_c']-p['kappa']-v)/p['lambda_c'])
        return f"failed knot 1 residual {abs(pressure-100000)/100000:.17g} trials 1 de0 0.0001 de1 0\ndrained replay failed: original-cam-clay-sw-electronic-log-recovery-v1 singular mixed-control system; last committed knot retained\n"
    def runner(self,source,size,mutate=None):
        expected=dispatch.original_contracts(size)+(md.contracts()if size=='16' else [])
        def run(argv,env,capture_output,timeout):
            self.calls.append((argv,dict(env),timeout))
            self.assertNotEqual(env.get(md.SELECTORS[1]),'poison')
            if size!='16':
                self.assertNotIn(md.SELECTORS[0],env);self.assertNotIn(md.SELECTORS[1],env)
                rows=[]
                for x in expected:
                    rows.append({'target':x['target'],'profile':x['native_selector'],'returncode':1,'stdout':x['stdout'],'stderr':self.occ(source) if x['stderr']is None else x['stderr']})
                report={'status':'passed','model_count':int(size),'policy_id':dispatch.IDENTITIES[size]['policy_id'],'processes':rows}
                if mutate:mutate(report)
                Path(argv[-1]).write_text(json.dumps(report)+'\n')
                return subprocess.CompletedProcess(argv,0,b'Original native failure signatures and closed fixture selection verified for both test executables.\n',b'')
            x=expected[len(self.calls)-1];self.assertEqual(Path(argv[0]).name,x['target']);self.assertEqual(timeout,120)
            wanted={k:v for k,v in zip(md.SELECTORS,[x['native_selector'],x['numerical_selector']])if v is not None}
            self.assertEqual({k:env[k]for k in md.SELECTORS if k in env},wanted)
            result={'returncode':1,'stdout':x['stdout'].encode(),'stderr':(self.occ(source) if x['stderr']is None else x['stderr']).encode()}
            if mutate:mutate(result)
            return subprocess.CompletedProcess(argv,**result)
        return run
    def execute(self,source,build,runner,output='receipt.json',operation='check',suite=None):
        return dispatch.execute(operation,build/'generated/models.json',source,build,self.base/output,suite,runner,{'KEEP':'yes',md.SELECTORS[0]:'poison',md.SELECTORS[1]:'poison'})
    def test_three_exact_routes_preserve_four_or_eight_contracts(self):
        for size in ['14','15','16']:
            with self.subTest(size=size):
                self.calls=[];source,build=self.fixture(size)
                r=self.execute(source,build,self.runner(source,size),'receipt'+size+'.json')
                self.assertEqual(r['status'],'passed');self.assertEqual(len(self.calls),8 if size=='16'else 1)
                if size!='16':self.assertEqual(len(r['delegated_original_report']['processes']),4)
    def test_catalogue_corruptions_abort_before_any_process(self):
        source,build=self.fixture();p=build/'generated/models.json';old=p.read_bytes()
        transforms=[lambda b:b['models'].pop(),lambda b:b['models'].reverse(),lambda b:b['models'].append(copy.deepcopy(b['models'][0])),lambda b:b['models'][0].update(id='unknown'),lambda b:b['models'][0].update(title='changed'),lambda b:b.update(sha256='0'*64),lambda b:b.update(schema_version='0.3')]
        for i,fn in enumerate(transforms):
            b=json.loads(old);fn(b);p.write_text(json.dumps(b,indent=2)+'\n')
            with self.subTest(i=i),self.assertRaises((ValueError,KeyError,TypeError)):self.execute(source,build,self.runner(source,'16'),f'bad{i}.json')
        self.assertEqual(self.calls,[]);p.write_bytes(old)
        for i,raw in enumerate([b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1e999}']):
            with self.subTest(i=i),self.assertRaises(ValueError):dispatch.strict_json(raw)
    def test_source_helper_policy_and_build_binding_corruptions(self):
        source,build=self.fixture()
        paths=[source/'models/linear-elastic.json',source/'tools/check_native_fixture_contracts.py',source/'catalogue/laboratory-package-policy.json',build/'CMakeCache.txt']
        for i,p in enumerate(paths):
            old=p.read_bytes();p.write_bytes(old+b' ')
            if p.name=='CMakeCache.txt':p.write_text('CMAKE_HOME_DIRECTORY:INTERNAL=/wrong\n')
            with self.subTest(path=p),self.assertRaises(ValueError):self.execute(source,build,self.runner(source,'16'),f'context{i}.json')
            p.write_bytes(old)
        self.assertEqual(self.calls,[])
        extra=source/'models/unknown.json';extra.write_text('{}')
        with self.assertRaises(ValueError):self.execute(source,build,self.runner(source,'16'),'extra.json')
        self.assertEqual(self.calls,[])
    def test_every_strict_row_mutation_rejects(self):
        source,build=self.fixture()
        for index in range(8):
            for field,value in [('returncode',0),('returncode',-9),('stdout',b'wrong\n'),('stderr',b'wrong\n')]:
                self.calls=[]
                def mutate(result):
                    if len(self.calls)-1==index:result[field]=value
                name=f'bad-{index}-{field}-{value!r}.json'
                with self.subTest(index=index,field=field,value=value),self.assertRaises((ValueError,AssertionError)):self.execute(source,build,self.runner(source,'16',mutate),name)
                receipt=json.loads((self.base/name).read_text());self.assertEqual(receipt['status'],'failed');self.assertEqual(len(receipt['processes']),index+1)
    def test_partial_start_timeout_and_invalid_utf8_are_retained(self):
        source,build=self.fixture()
        for index,error in enumerate([OSError('synthetic spawn failure'),subprocess.TimeoutExpired(['stand-in'],120,output=b'partial-out',stderr=b'partial-err')]):
            def run(*args,**kwargs):raise error
            with self.assertRaises(type(error)):self.execute(source,build,run,f'exception{index}.json')
            r=json.loads((self.base/f'exception{index}.json').read_text());self.assertEqual(r['status'],'failed');self.assertEqual(r['processes'][0]['status'],'failed')
            if index:self.assertEqual(base64.b64decode(r['processes'][0]['stdout_base64']),b'partial-out')
        def bad_utf(argv,**kwargs):return subprocess.CompletedProcess(argv,1,b'\xff',b'err')
        with self.assertRaises(UnicodeDecodeError):self.execute(source,build,bad_utf,'utf.json')
        r=json.loads((self.base/'utf.json').read_text());self.assertEqual(base64.b64decode(r['processes'][0]['stdout_base64']),b'\xff')
    def test_no_overwrite_and_artifact_mutation(self):
        source,build=self.fixture();out=self.base/'existing.json';out.write_text('original')
        with self.assertRaises(FileExistsError):self.execute(source,build,self.runner(source,'16'),'existing.json')
        self.assertEqual(out.read_text(),'original');self.assertEqual(self.calls,[])
        original=self.runner(source,'16')
        def mutate(argv,**kwargs):
            result=original(argv,**kwargs)
            if len(self.calls)==8:(build/'atlas_numerical_tests').write_text('changed')
            return result
        with self.assertRaises(ValueError):self.execute(source,build,mutate,'changed-artifact.json')
    def test_delegated_corruptions(self):
        source,build=self.fixture('15')
        for i,mutation in enumerate([lambda r:r['processes'].pop(),lambda r:r.update(model_count=14),lambda r:r['processes'][0].update(stdout='models=16\n'),lambda r:r['processes'].reverse()]):
            with self.subTest(i=i),self.assertRaises(ValueError):self.execute(source,build,self.runner(source,'15',mutation),f'delegate{i}.json')
    def ctest_run(self,source,build,size,suite,*,bad=None):
        def run(argv,env,**kwargs):
            self.calls.append((argv,dict(env)))
            self.assertEqual(argv[1:],['--test-dir',str(build),'--output-on-failure',*dispatch.SUITES[suite]])
            self.assertEqual(env.get(md.SELECTORS[0]),md.NATIVE)
            self.assertEqual(env.get(md.SELECTORS[1]),md.NUMERICAL if size=='16'and suite!='recorded'else None)
            import re
            names=[n for n,_,_ in dispatch.REGISTRATIONS if (re.search(dispatch.SUITES[suite][1],n)is not None)==(dispatch.SUITES[suite][0]=='-R')]
            log='Start testing\n'+''.join(f'{i}/10 Testing: {n}\nOutput:\n----------------------------------------------------------\n'+(md.POSITIVE_STDOUT if size=='16'and n=='atlas_numerical'else 'prior fixture\n')+'<end of output>\n----------------------------------------------------------\nTest Passed.\n'for i,n in enumerate(names,1))+'End testing\n'
            if bad=='missing-numerical':log=log.replace('Testing: atlas_numerical','Testing: unknown')
            if bad=='wrong-label':log=log.replace(md.POSITIVE_STDOUT,'Explicit valid-domain/GIS-depth20 fixtures; models=16\n')
            if bad=='failed-test':log=log.replace('Test Passed.','Test Failed.',1)
            p=build/'Testing/Temporary/LastTest.log';p.parent.mkdir(parents=True,exist_ok=True)
            if bad!='missing-log':p.write_text(log)
            return subprocess.CompletedProcess(argv,1 if bad=='nonzero'else 0,b'ctest synthetic\n',b'')
        return run
    def test_all_ctest_routes_filters_environments_and_prior_log_preservation(self):
        for size in ['14','15','16']:
            source,build=self.fixture(size)
            with patch.object(dispatch.shutil,'which',return_value=str(build/'mock-ctest')):
                for suite in dispatch.SUITES:
                    with self.subTest(size=size,suite=suite):
                        r=self.execute(source,build,self.ctest_run(source,build,size,suite),size+suite+'.json','ctest',suite)
                        self.assertEqual(r['status'],'passed')
                        self.assertIn('ctest_log',r)
    def test_ctest_cannot_hide_failed_omitted_legacy_or_stale_result(self):
        source,build=self.fixture()
        with patch.object(dispatch.shutil,'which',return_value=str(build/'mock-ctest')):
            for bad in ['nonzero','missing-numerical','wrong-label','failed-test','missing-log']:
                p=build/'Testing/Temporary/LastTest.log';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('prior evidence')
                with self.subTest(bad=bad),self.assertRaises(ValueError):self.execute(source,build,self.ctest_run(source,build,'16','macos-main',bad=bad),bad+'.json','ctest','macos-main')
                r=json.loads((self.base/(bad+'.json')).read_text());self.assertEqual(base64.b64decode(r['previous_ctest_log']['base64']),b'prior evidence')
    def test_unknown_suite_rejected_without_process(self):
        source,build=self.fixture()
        with self.assertRaises(ValueError):self.execute(source,build,self.runner(source,'16'),'unknown-suite.json','ctest','skip-numerical')
        self.assertEqual(self.calls,[])
    def test_delegated_partial_report_retained_on_failure(self):
        source,build=self.fixture('15')
        def run(argv,**kwargs):
            Path(argv[-1]).write_bytes(b'{"status":"failed","processes":[]}\n')
            return subprocess.CompletedProcess(argv,1,b'partial helper output',b'helper failure')
        with self.assertRaises(ValueError):self.execute(source,build,run,'partial-delegated.json')
        report=json.loads((self.base/'partial-delegated.json').read_text())
        self.assertEqual(base64.b64decode(report['delegated_original_report_raw']['base64']),b'{"status":"failed","processes":[]}\n')
    def test_ctest_timeout_retains_partial_log_and_raw(self):
        source,build=self.fixture()
        def run(argv,**kwargs):
            log=build/'Testing/Temporary/LastTest.log';log.parent.mkdir(parents=True,exist_ok=True);log.write_text('incomplete CTest observations\n')
            raise subprocess.TimeoutExpired(argv,1800,output=b'partial ctest',stderr=b'late error')
        with patch.object(dispatch.shutil,'which',return_value=str(build/'mock-ctest')),self.assertRaises(subprocess.TimeoutExpired):self.execute(source,build,run,'ctest-timeout.json','ctest','macos-main')
        report=json.loads((self.base/'ctest-timeout.json').read_text())
        self.assertEqual(base64.b64decode(report['ctest_log']['base64']),b'incomplete CTest observations\n')
        self.assertEqual(base64.b64decode(report['processes'][0]['stdout_base64']),b'partial ctest')
    def test_full10_registry_adversaries_reject_before_all_suite_calls(self):
        source,build=self.fixture();path=build/'CTestTestfile.cmake';original=path.read_text();lines=original.splitlines(True)
        corruptions={'omitted8':''.join(lines[:2]),'extra':original+lines[-1].replace('atlas_scalar_functions','unknown_test'),'duplicate':original+lines[-1],'reordered':''.join(reversed(lines)),'wrong-command':original.replace('atlas_time_tests','atlas_capacity_tests'),'wrong-argument':original.replace('0,0,0,0,0,0','0,0,0,0,0,1'),'altered-python-suite':original.replace('"discover"','"different"'),'outcome-override':original+'set_tests_properties("atlas_numerical" PROPERTIES WILL_FAIL TRUE)\n','external-registration':original+'subdirs("hidden")\n'}
        for name,text in corruptions.items():
            path.write_text(text)
            for suite in dispatch.SUITES:
                with self.subTest(name=name,suite=suite),self.assertRaises(ValueError):self.execute(source,build,self.ctest_run(source,build,'16',suite),name+suite+'.json','ctest',suite)
        self.assertEqual(self.calls,[]);path.write_text(original)
        (source/'CMakeLists.txt').write_text((source/'CMakeLists.txt').read_text()+'# source drift\n')
        with self.assertRaises(ValueError):self.execute(source,build,self.ctest_run(source,build,'16','macos-main'),'source-cmake-drift.json','ctest','macos-main')
        self.assertEqual(self.calls,[])
    def test_ctest_selected_tool_content_and_path_drift_rejected(self):
        source,build=self.fixture()
        for mode in ['content','path']:
            original=self.ctest_run(source,build,'16','macos-main')
            def run(argv,**kwargs):
                result=original(argv,**kwargs)
                if mode=='content':(build/'mock-ctest').write_bytes(b'CHANGED SYNTHETIC CTEST\n')
                return result
            selected=[str(build/'mock-ctest'),str(build/'mock-ctest-other')]if mode=='path'else [str(build/'mock-ctest')]*2
            with patch.object(dispatch.shutil,'which',side_effect=selected),self.assertRaises(ValueError):self.execute(source,build,run,'tool-drift-'+mode+'.json','ctest','macos-main')
            report=json.loads((self.base/('tool-drift-'+mode+'.json')).read_text());self.assertEqual(report['status'],'failed');self.assertIn('ctest_postflight',report)
    def test_positive_label_exact_line_inside_output_only(self):
        source,build=self.fixture()
        for mode in ['prefix','suffix','duplicate','metadata-only','unterminated','outside-region']:
            original=self.ctest_run(source,build,'16','macos-main')
            def run(argv,**kwargs):
                result=original(argv,**kwargs);p=build/'Testing/Temporary/LastTest.log';text=p.read_text()
                if mode=='prefix':text=text.replace(md.POSITIVE_STDOUT,'WRONG-PREFIX '+md.POSITIVE_STDOUT)
                elif mode=='suffix':text=text.replace(md.POSITIVE_STDOUT,md.POSITIVE_STDOUT.rstrip('\n')+' WRONG-SUFFIX\n')
                elif mode=='duplicate':text=text.replace(md.POSITIVE_STDOUT,md.POSITIVE_STDOUT*2)
                elif mode=='unterminated':text=text.replace(md.POSITIVE_STDOUT,md.POSITIVE_STDOUT.rstrip('\n'))
                else:
                    text=text.replace(md.POSITIVE_STDOUT,'')
                    text=text.replace('Output:\n',md.POSITIVE_STDOUT+'Output:\n',1)if mode=='metadata-only'else text+md.POSITIVE_STDOUT
                p.write_text(text);return result
            with patch.object(dispatch.shutil,'which',return_value=str(build/'mock-ctest')),self.subTest(mode=mode),self.assertRaises(ValueError):self.execute(source,build,run,'bad-label-'+mode+'.json','ctest','macos-main')
    def test_combined_timeout_nonutf8_retains_timeout_identity(self):
        source,build=self.fixture()
        def run(argv,**kwargs):raise subprocess.TimeoutExpired(argv,120,output=b'\xff',stderr=b'partial-timeout')
        with self.assertRaises(subprocess.TimeoutExpired):self.execute(source,build,run,'timeout-nonutf8.json')
        report=json.loads((self.base/'timeout-nonutf8.json').read_text());row=report['processes'][0]
        self.assertEqual(report['error_type'],'TimeoutExpired');self.assertEqual(row['status'],'failed');self.assertEqual(row['error_type'],'TimeoutExpired');self.assertTrue(row['timeout_expired']);self.assertEqual(row['decode_error']['type'],'UnicodeDecodeError');self.assertEqual(base64.b64decode(row['stdout_base64']),b'\xff');self.assertEqual(base64.b64decode(row['stderr_base64']),b'partial-timeout')
    def test_ctest_symlink_resolution_is_bound_and_target_drift_rejects(self):
        source,build=self.fixture();link=build/'selected-ctest';link.symlink_to(build/'mock-ctest')
        with patch.object(dispatch.shutil,'which',return_value=str(link)):
            report=self.execute(source,build,self.ctest_run(source,build,'16','recorded'),'symlink-positive.json','ctest','recorded')
        self.assertEqual(report['ctest_executable_resolved_path'],str(build/'mock-ctest'))
        other=build/'other-ctest';other.write_bytes((build/'mock-ctest').read_bytes())
        original=self.ctest_run(source,build,'16','recorded')
        def drift(argv,**kwargs):
            result=original(argv,**kwargs);link.unlink();link.symlink_to(other);return result
        with patch.object(dispatch.shutil,'which',return_value=str(link)),self.assertRaises(ValueError):self.execute(source,build,drift,'symlink-drift.json','ctest','recorded')

ARCHIVAL={'tools/check_native_fixture_contracts.py': 'IiIiUmV0YWluIHN0cmljdCBvcmlnaW5hbCBhbmQgdW5rbm93bi1wcm9maWxlIG5hdGl2ZSBmYWlsdXJlczsgQ1Rlc3QgY2hlY2tzIHBvc2l0aXZlcy4iIiIKaW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBoYXNobGliCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgbWF0aAppbXBvcnQgcmUKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCmltcG9ydCBzdWJwcm9jZXNzCgpST09UPVBhdGgoX19maWxlX18pLnJlc29sdmUoKS5wYXJlbnRzWzFdCgoKT0NDPSdvcmlnaW5hbC1jYW0tY2xheS1zdy1lbGVjdHJvbmljLWxvZy1yZWNvdmVyeS12MScKT0NDX0hBU0g9JzYzN2JhNzIzMzVjMzQ2NGZlYzQyN2M3NzNkMjE0ZDIxZDA2ZTllMjZiYzczN2QxNTMwN2FhZTJmNjcxMTFiMzQnCkRVTkNBTj0nZHVuY2FuLWNoYW5nLTE5NzAtZW5kcG9pbnQtYXZlcmFnZScKRFVOQ0FOX0hBU0g9JzQ1MmI0OWVmNDg2NjhjMGM1ZDhhYmEyMGRmY2EzOTgyMzVmYTQ1NDMxZTg1M2VlOTIzYmUwNWExN2M3Yzg4YTAnCiMgRXhhY3QgcHJpb3IxMyBtYXBwaW5nIGZyb20gcHJlc2VydmVkIHBhY2thZ2UgcG9saWN5ODRmZTE0YzQuLi4sIG5vdCBtdXRhYmxlIGxpdmUgcG9saWN5LgpQUklPUl9USElSVEVFTj17CiAgICAiYmFyb2Rlc3ktY2xheS0yMDE3IjogIjBiZjRmZDI3ODkyNzRmMTI3MWI0MzhmZmVhNTcxNjg4NjZmN2ViZWE1NWNmY2Y4ZWY3ODY1MzI5MDNhYjM0NzciLAogICAgImJhcm9kZXN5LXNhbmQiOiAiM2E2MWI1MzczNDA0ZDY5NzNhMjk1N2JkMGZhMjE2OTJlMTBiNDllOTc0Y2RmODdlZmYwNDdkNTUzMTg1MTIzOSIsCiAgICAiZHJ1Y2tlci1wcmFnZXIiOiAiYjJhZTM0MGU5N2ZjYTQyMDllNjcxYjFmNjEwZGFjN2IxNTIwMzk0ZWVmZTMwNzA1NDhmMjk5YmQ2MDNlZTg3NyIsCiAgICAiaHlwb3BsYXN0aWMtY2xheS0yMDA1IjogIjI0N2RlMmYxNzkyY2YyMjA3NDg2NzFiNDU2M2M3ZGQyOTBjNWI5MWZjYzk1ZWRhNTk3N2FjMDNlMDFmYTZmZjUiLAogICAgImh5cG9wbGFzdGljLWNsYXktMjAxMyI6ICI2ODExNTgwY2Y5YzA2Nzg2MDViOWJiN2Q5M2E1MjQ3NDNiYmU1YjVjYjFmNTQ3YmQyMzJkMDkwYWVkYTk1MGU0IiwKICAgICJoeXBvcGxhc3RpYy1zYW5kLWlnczk3IjogIjgzNzc3NDU4ZWE0MzdhM2E3YzEzNjAxMTdkYmY0MzVmN2Q3NjM5MTNjZGEzOTkwOTllZjI5NjZlNjVhNjdlODYiLAogICAgImh5cG9wbGFzdGljLXNhbmQtdnc5NiI6ICIxZGY5NWY4MTI4YzRmMTYwNjYwMDRkZTc2MTUyODkwNzViYWZlOTZkMjE3NGUwNmU1Y2Q3NjcwNGY0NWJiZDYxIiwKICAgICJsaW5lYXItZWxhc3RpYyI6ICIzMzM4N2IyMDU4YTNmNTRlZDYxMTk0OTMxODI4OWRiMjRhYjJkNWI4ZWRkMTcyZDBhMjQ1NDA0MmM3OTc1MDQxIiwKICAgICJtb2RpZmllZC1jYW0tY2xheSI6ICJlMDc1MTE3ZTA3YTcxYTE3YTM1Y2U0N2RhYzY2MTcyYTBjYzQwMjg2MGY1YzZjZjEwNmY3ODgzZGI1NzIxYTE0IiwKICAgICJtb2hyLWNvdWxvbWIiOiAiNmEzYTEzOTIxOGZjNDEzZjA2NmFiZTViODUxYzVjN2FlZDg4OTllZTIzZWZiZDdhZTJhMmU2OGM3NjU1ZjBlNSIsCiAgICAicmVzZWFyY2gtaHAtZXh0cmFjdGVkLWFzYnMtZ2lzLTIwMjQtdjAzIjogIjQzOWI3ODVlMWRhMzA3NTIwOWM2ZDVjYTQzYTk5MWE0NDE0NjNhOTE1ZjMxZjJlOWM3N2I1YzY4MzVlMjBkYmMiLAogICAgInRyZXNjYS1hc3NvY2lhdGVkLXBlcmZlY3QtYmsyMDIydjEtYmUiOiAiMTlhY2ViZWQzN2Q1OTEyMGU0OWM1ZGZmNjk4ZTJiN2QyYTI2OTNiYmNlOWVjMzVjOGJjYmM2NTk1NDgxOWUxOCIsCiAgICAib3JpZ2luYWwtY2FtLWNsYXktc3ctZWxlY3Ryb25pYy1sb2ctcmVjb3ZlcnktdjEiOiAiNjM3YmE3MjMzNWMzNDY0ZmVjNDI3Yzc3M2QyMTRkMjFkMDZlOWUyNmJjNzM3ZDE1MzA3YWFlMmY2NzExMWIzNCIKfQpHSVNfRkFJTFVSRT0nbm9ubGluZWFyIHJlY29yZGVkIHJlcGxheSBmYWlsZWQ6IHJlc2VhcmNoLWhwLWV4dHJhY3RlZC1hc2JzLWdpcy0yMDI0LXYwMyBtYXRlcmlhbCB1cGRhdGUgZmFpbGVkIG9yIHRyaWFsIGJ1ZGdldCBleGhhdXN0ZWQ7IGxhc3QgY29tbWl0dGVkIGtub3QgcmV0YWluZWRcbicKCmRlZiBjaGVja19yZWNvcmRlZF9mYWlsdXJlKG1lc3NhZ2UsIGRlZmluaXRpb25zLCAqLCByb290PVJPT1QpOgogICAgaWYgT0NDIG5vdCBpbiBkZWZpbml0aW9uczoKICAgICAgICBhc3NlcnQgbWVzc2FnZT09R0lTX0ZBSUxVUkUKICAgICAgICByZXR1cm4gJ2hpc3RvcmljYWwtdHdlbHZlIEdJUyBmaXJzdCBmYWlsdXJlJwogICAgaWYgRFVOQ0FOIGluIGRlZmluaXRpb25zOgogICAgICAgIGFzc2VydCBkZWZpbml0aW9ucz09eyoqUFJJT1JfVEhJUlRFRU4sRFVOQ0FOOkRVTkNBTl9IQVNIfSwgJ3VucXVhbGlmaWVkIHN0cmljdCBmb3VydGVlbi1tb2RlbCBjYXRhbG9ndWUnCiAgICBlbHNlOgogICAgICAgIGFzc2VydCBsZW4oZGVmaW5pdGlvbnMpPT0xMyBhbmQgZGVmaW5pdGlvbnNbT0NDXT09T0NDX0hBU0gsICd1bnF1YWxpZmllZCBzdHJpY3QgY2F0YWxvZ3VlJwogICAgbWF0Y2g9cmUuZnVsbG1hdGNoKHInZmFpbGVkIGtub3QgMSByZXNpZHVhbCAoW14gXSspIHRyaWFscyAxIGRlMCAoW14gXSspIGRlMSAwXG5kcmFpbmVkIHJlcGxheSBmYWlsZWQ6ICcrcmUuZXNjYXBlKE9DQykrcicgc2luZ3VsYXIgbWl4ZWQtY29udHJvbCBzeXN0ZW07IGxhc3QgY29tbWl0dGVkIGtub3QgcmV0YWluZWRcbicsbWVzc2FnZSkKICAgIGFzc2VydCBtYXRjaCwgJ3N0cmljdCBPQ0MgZmFpbHVyZSBzaWduYXR1cmUgY2hhbmdlZCcKICAgIHJlc2lkdWFsLGF4aWFsPW1hcChmbG9hdCxtYXRjaC5ncm91cHMoKSkKICAgIGFzc2VydCBheGlhbD09MWUtNCBhbmQgbWF0aC5pc2Zpbml0ZShyZXNpZHVhbCkKICAgICMgSW5kZXBlbmRlbnQgY29uZSBlbmRwb2ludDogQkUgdm9sdW1lLCBzb3VyY2Ugbm9ybWFsLWNvbXByZXNzaW9uIHBhY2tpbmc7CiAgICAjIGluaXRpYWwgdHJhbnN2ZXJzZSBzdHJlc3MgaXMxMDBrUGEgYW5kIGZpeGVkIGNvbnRyb2wgc2NhbGUxMDBrUGEuCiAgICBtb2RlbD1qc29uLmxvYWRzKChyb290Lydtb2RlbHMnL2Yne09DQ30uanNvbicpLnJlYWRfdGV4dCgpKQogICAgcGFyYW1zPXtrOnZbJ2RlZmF1bHQnXSBmb3Igayx2IGluIG1vZGVsWydwYXJhbWV0ZXJzJ10uaXRlbXMoKX0KICAgIHZvbHVtZT1tb2RlbFsnc3RhdGUnXVsxXVsnaW5pdGlhbCddLygxK2F4aWFsKQogICAgcHJlc3N1cmU9cGFyYW1zWydwcmVmJ10qbWF0aC5leHAoKHBhcmFtc1snR2FtbWEnXStwYXJhbXNbJ2xhbWJkYV9jJ10tcGFyYW1zWydrYXBwYSddLXZvbHVtZSkvcGFyYW1zWydsYW1iZGFfYyddKQogICAgZXhwZWN0ZWQ9YWJzKHByZXNzdXJlLTEwMDAwMCkvMTAwMDAwCiAgICBhc3NlcnQgYWJzKHJlc2lkdWFsLWV4cGVjdGVkKTw9MmUtMTAqbWF4KDEsYWJzKGV4cGVjdGVkKSksICdzdHJpY3QgT0NDIGNvbmUgcmVzaWR1YWwgY2hhbmdlZCcKICAgIHJldHVybiAoJ2N1cnJlbnQtZm91cnRlZW4gRHVuY2FuL09DQycgaWYgRFVOQ0FOIGluIGRlZmluaXRpb25zIGVsc2UgJ2N1cnJlbnQtdGhpcnRlZW4gT0NDJykrJyBmaXJzdCBmYWlsdXJlOyBvcmlnaW5hbCByb2xsYmFjayBhc3NlcnRlZCBieSBleHBsaWNpdCBwb3NpdGl2ZSBzdWl0ZScKCmRlZiBtYWluKCk6CiAgICBwYXJzZXI9YXJncGFyc2UuQXJndW1lbnRQYXJzZXIoZGVzY3JpcHRpb249X19kb2NfXykKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoJy0tYnVpbGQnLHR5cGU9UGF0aCxkZWZhdWx0PVJPT1QvJ2J1aWxkJykKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoJy0tb3V0cHV0Jyx0eXBlPVBhdGgscmVxdWlyZWQ9VHJ1ZSkKICAgIGFyZ3M9cGFyc2VyLnBhcnNlX2FyZ3MoKQogICAgaWYgYXJncy5vdXRwdXQuZXhpc3RzKCk6cmFpc2UgVmFsdWVFcnJvcignUHJlc2VydmUgZXhpc3Rpbmcgb2JzZXJ2YXRpb25zJykKICAgIHBvbGljeT1qc29uLmxvYWRzKChST09ULydjYXRhbG9ndWUvbGFib3JhdG9yeS1wYWNrYWdlLXBvbGljeS5qc29uJykucmVhZF90ZXh0KCkpCiAgICBmb3IgbW9kZWwsZGlnZXN0IGluIHBvbGljeVsnbW9kZWxzJ10uaXRlbXMoKToKICAgICAgICBhc3NlcnQgaGFzaGxpYi5zaGEyNTYoKFJPT1QvJ21vZGVscycvZid7bW9kZWx9Lmpzb24nKS5yZWFkX2J5dGVzKCkpLmhleGRpZ2VzdCgpPT1kaWdlc3QKICAgIHJlcG9ydD17J3N0YXR1cyc6J3J1bm5pbmcnLCdwb2xpY3lfaWQnOnBvbGljeVsnaWQnXSwnbW9kZWxfY291bnQnOmxlbihwb2xpY3lbJ21vZGVscyddKSwncHJvY2Vzc2VzJzpbXX0KICAgIHNhdmU9bGFtYmRhOmFyZ3Mub3V0cHV0LndyaXRlX3RleHQoanNvbi5kdW1wcyhyZXBvcnQsaW5kZW50PTIpKydcbicpCiAgICBleHBlY3RlZD17J2F0bGFzX251bWVyaWNhbF90ZXN0cyc6J0ZEIHRlc3Qgb3V0c2lkZSBkb21haW5cbicsJ2F0bGFzX3JlY29yZGVkX3Rlc3RzJzpHSVNfRkFJTFVSRX0KICAgIHRyeToKICAgICAgICBmb3IgdGFyZ2V0LG1lc3NhZ2UgaW4gZXhwZWN0ZWQuaXRlbXMoKToKICAgICAgICAgICAgZm9yIHByb2ZpbGUgaW4gW05vbmUsJ3Vua25vd24nXToKICAgICAgICAgICAgICAgIGVudj1kaWN0KG9zLmVudmlyb24pO2Vudi5wb3AoJ0FUTEFTX05BVElWRV9GSVhUVVJFUycsTm9uZSkKICAgICAgICAgICAgICAgIGlmIHByb2ZpbGU6ZW52WydBVExBU19OQVRJVkVfRklYVFVSRVMnXT1wcm9maWxlCiAgICAgICAgICAgICAgICByZXN1bHQ9c3VicHJvY2Vzcy5ydW4oW3N0cihhcmdzLmJ1aWxkLnJlc29sdmUoKS90YXJnZXQpXSxlbnY9ZW52LGNhcHR1cmVfb3V0cHV0PVRydWUsdGV4dD1UcnVlLHRpbWVvdXQ9MTIwKQogICAgICAgICAgICAgICAgcm93PXsndGFyZ2V0Jzp0YXJnZXQsJ3Byb2ZpbGUnOnByb2ZpbGUsJ3JldHVybmNvZGUnOnJlc3VsdC5yZXR1cm5jb2RlLCdzdGRvdXQnOnJlc3VsdC5zdGRvdXQsJ3N0ZGVycic6cmVzdWx0LnN0ZGVycn07cmVwb3J0Wydwcm9jZXNzZXMnXS5hcHBlbmQocm93KTtzYXZlKCkKICAgICAgICAgICAgICAgIGFzc2VydCByZXN1bHQucmV0dXJuY29kZT09MSwodGFyZ2V0LHByb2ZpbGUscmVzdWx0LnJldHVybmNvZGUpCiAgICAgICAgICAgICAgICBpZiB0YXJnZXQ9PSdhdGxhc19yZWNvcmRlZF90ZXN0cycgYW5kIHByb2ZpbGUgaXMgTm9uZToKICAgICAgICAgICAgICAgICAgICByb3dbJ3N0cmljdF9jb250ZXh0J109Y2hlY2tfcmVjb3JkZWRfZmFpbHVyZShyZXN1bHQuc3RkZXJyLHBvbGljeVsnbW9kZWxzJ10pO3NhdmUoKQogICAgICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgICAgICBhc3NlcnQgcmVzdWx0LnN0ZGVycj09KG1lc3NhZ2UgaWYgcHJvZmlsZSBpcyBOb25lIGVsc2UgJ3Vua25vd24gbmF0aXZlIGZpeHR1cmUgcHJvZmlsZVxuJykKICAgICAgICAgICAgICAgIGFzc2VydCByZXN1bHQuc3Rkb3V0PT0oJ1N0cmljdCBvcmlnaW5hbCBkZWZhdWx0IGZpeHR1cmVzOyBtb2RlbHM9JytzdHIocmVwb3J0Wydtb2RlbF9jb3VudCddKSsnXG4nIGlmIHByb2ZpbGUgaXMgTm9uZSBlbHNlICcnKQogICAgICAgIHJlcG9ydFsnc3RhdHVzJ109J3Bhc3NlZCc7c2F2ZSgpCiAgICBleGNlcHQgQmFzZUV4Y2VwdGlvbiBhcyBleGM6CiAgICAgICAgcmVwb3J0WydzdGF0dXMnXT0nZmFpbGVkJztyZXBvcnRbJ2Vycm9yJ109c3RyKGV4Yyk7c2F2ZSgpO3JhaXNlCiAgICBwcmludCgnT3JpZ2luYWwgbmF0aXZlIGZhaWx1cmUgc2lnbmF0dXJlcyBhbmQgY2xvc2VkIGZpeHR1cmUgc2VsZWN0aW9uIHZlcmlmaWVkIGZvciBib3RoIHRlc3QgZXhlY3V0YWJsZXMuJykKCmlmIF9fbmFtZV9fPT0nX19tYWluX18nOm1haW4oKQo=', 'catalogue/laboratory-package-policy.json': 'ewogICJzY2hlbWFfdmVyc2lvbiI6ICIwLjEiLAogICJraW5kIjogInN1cHBvcnRlZC1sYWJvcmF0b3J5LXBhY2thZ2UtcG9saWN5IiwKICAiaWQiOiAic3VwcG9ydGVkLXBhY2thZ2UtZm91cnRlZW4tZHVuY2FuLXYxIiwKICAib3JkaW5hcnkiOiAiZHJhaW5lZC0xcGN0LTEwMC1jdXJyZW50LXNldHRpbmdzIiwKICAibW9kZWxzIjogewogICAgImJhcm9kZXN5LWNsYXktMjAxNyI6ICIwYmY0ZmQyNzg5Mjc0ZjEyNzFiNDM4ZmZlYTU3MTY4ODY2ZjdlYmVhNTVjZmNmOGVmNzg2NTMyOTAzYWIzNDc3IiwKICAgICJiYXJvZGVzeS1zYW5kIjogIjNhNjFiNTM3MzQwNGQ2OTczYTI5NTdiZDBmYTIxNjkyZTEwYjQ5ZTk3NGNkZjg3ZWZmMDQ3ZDU1MzE4NTEyMzkiLAogICAgImRydWNrZXItcHJhZ2VyIjogImIyYWUzNDBlOTdmY2E0MjA5ZTY3MWIxZjYxMGRhYzdiMTUyMDM5NGVlZmUzMDcwNTQ4ZjI5OWJkNjAzZWU4NzciLAogICAgImh5cG9wbGFzdGljLWNsYXktMjAwNSI6ICIyNDdkZTJmMTc5MmNmMjIwNzQ4NjcxYjQ1NjNjN2RkMjkwYzViOTFmY2M5NWVkYTU5NzdhYzAzZTAxZmE2ZmY1IiwKICAgICJoeXBvcGxhc3RpYy1jbGF5LTIwMTMiOiAiNjgxMTU4MGNmOWMwNjc4NjA1YjliYjdkOTNhNTI0NzQzYmJlNWI1Y2IxZjU0N2JkMjMyZDA5MGFlZGE5NTBlNCIsCiAgICAiaHlwb3BsYXN0aWMtc2FuZC1pZ3M5NyI6ICI4Mzc3NzQ1OGVhNDM3YTNhN2MxMzYwMTE3ZGJmNDM1ZjdkNzYzOTEzY2RhMzk5MDk5ZWYyOTY2ZTY1YTY3ZTg2IiwKICAgICJoeXBvcGxhc3RpYy1zYW5kLXZ3OTYiOiAiMWRmOTVmODEyOGM0ZjE2MDY2MDA0ZGU3NjE1Mjg5MDc1YmFmZTk2ZDIxNzRlMDZlNWNkNzY3MDRmNDViYmQ2MSIsCiAgICAibGluZWFyLWVsYXN0aWMiOiAiMzMzODdiMjA1OGEzZjU0ZWQ2MTE5NDkzMTgyODlkYjI0YWIyZDViOGVkZDE3MmQwYTI0NTQwNDJjNzk3NTA0MSIsCiAgICAibW9kaWZpZWQtY2FtLWNsYXkiOiAiZTA3NTExN2UwN2E3MWExN2EzNWNlNDdkYWM2NjE3MmEwY2M0MDI4NjBmNWM2Y2YxMDZmNzg4M2RiNTcyMWExNCIsCiAgICAibW9oci1jb3Vsb21iIjogIjZhM2ExMzkyMThmYzQxM2YwNjZhYmU1Yjg1MWM1YzdhZWQ4ODk5ZWUyM2VmYmQ3YWUyYTJlNjhjNzY1NWYwZTUiLAogICAgInJlc2VhcmNoLWhwLWV4dHJhY3RlZC1hc2JzLWdpcy0yMDI0LXYwMyI6ICI0MzliNzg1ZTFkYTMwNzUyMDljNmQ1Y2E0M2E5OTFhNDQxNDYzYTkxNWYzMWYyZTljNzdiNWM2ODM1ZTIwZGJjIiwKICAgICJ0cmVzY2EtYXNzb2NpYXRlZC1wZXJmZWN0LWJrMjAyMnYxLWJlIjogIjE5YWNlYmVkMzdkNTkxMjBlNDljNWRmZjY5OGUyYjdkMmEyNjkzYmJjZTllYzM1YzhiY2JjNjU5NTQ4MTllMTgiLAogICAgIm9yaWdpbmFsLWNhbS1jbGF5LXN3LWVsZWN0cm9uaWMtbG9nLXJlY292ZXJ5LXYxIjogIjYzN2JhNzIzMzVjMzQ2NGZlYzQyN2M3NzNkMjE0ZDIxZDA2ZTllMjZiYzczN2QxNTMwN2FhZTJmNjcxMTFiMzQiLAogICAgImR1bmNhbi1jaGFuZy0xOTcwLWVuZHBvaW50LWF2ZXJhZ2UiOiAiNDUyYjQ5ZWY0ODY2OGMwYzVkOGFiYTIwZGZjYTM5ODIzNWZhNDU0MzFlODUzZWU5MjNiZTA1YTE3YzdjODhhMCIKICB9LAogICJkZWNsYXJlZF9mYWlsdXJlcyI6IFsKICAgIHsKICAgICAgIm1vZGVsIjogInJlc2VhcmNoLWhwLWV4dHJhY3RlZC1hc2JzLWdpcy0yMDI0LXYwMyIsCiAgICAgICJvcmRpbmFyeV9zcGVjaWZpY2F0aW9uIjogewogICAgICAgICJyZXNwb25zZV9jb250cmFjdCI6ICJzdHJlc3Mtc2NvcGUtMC4xIiwKICAgICAgICAic3RyZXNzX3Njb3BlIjogImVmZmVjdGl2ZSIsCiAgICAgICAgIm1vZGVsIjogInJlc2VhcmNoLWhwLWV4dHJhY3RlZC1hc2JzLWdpcy0yMDI0LXYwMyIsCiAgICAgICAgInBhcmFtZXRlcnMiOiBbCiAgICAgICAgICAxMDAwMDAsCiAgICAgICAgICAwLjU5MzQxMTk0NTY3ODA3MjEsCiAgICAgICAgICAxMTE3NDYwMDAsCiAgICAgICAgICAxLjAyNywKICAgICAgICAgIDAuODkzLAogICAgICAgICAgMC41MiwKICAgICAgICAgIDAuMzQ2LAogICAgICAgICAgMC4xNSwKICAgICAgICAgIDIuMiwKICAgICAgICAgIDAuMDAwMSwKICAgICAgICAgIDUsCiAgICAgICAgICAyLjUsCiAgICAgICAgICAwLjEsCiAgICAgICAgICA0LAogICAgICAgICAgMS43LAogICAgICAgICAgMC44LAogICAgICAgICAgMS41LAogICAgICAgICAgNDUsCiAgICAgICAgICAxCiAgICAgICAgXSwKICAgICAgICAiaW5pdGlhbCI6IFsKICAgICAgICAgIDEwMDAwMCwKICAgICAgICAgIDEwMDAwMCwKICAgICAgICAgIDEwMDAwMCwKICAgICAgICAgIDAsCiAgICAgICAgICAwLAogICAgICAgICAgMCwKICAgICAgICAgIDAuNTk1LAogICAgICAgICAgMCwKICAgICAgICAgIDAsCiAgICAgICAgICAwLAogICAgICAgICAgMCwKICAgICAgICAgIDAsCiAgICAgICAgICAwLAogICAgICAgICAgMAogICAgICAgIF0sCiAgICAgICAgInByb3RvY29sIjogMSwKICAgICAgICAidGFyZ2V0IjogMC4wMSwKICAgICAgICAic3RlcHMiOiAxMDAsCiAgICAgICAgImN5Y2xlcyI6IDAsCiAgICAgICAgImludGVncmF0aW9uX3NldHRpbmdzIjogewogICAgICAgICAgInZlcnNpb24iOiAiaW5jcmVtZW50YWwtc2V0dGluZ3MtMC4xIiwKICAgICAgICAgICJub3JtIjogInNjYWxlZF9jb21wb25lbnRfbWF4IiwKICAgICAgICAgICJyZXNpZHVhbF90b2xlcmFuY2UiOiAyZS0xMCwKICAgICAgICAgICJyYXRlX3RvbGVyYW5jZSI6IDFlLTA2LAogICAgICAgICAgIm1heF9pdGVyYXRpb25zIjogNDUsCiAgICAgICAgICAibWF4X2RlcHRoIjogMTQsCiAgICAgICAgICAibWF4X3N1YnN0ZXBzIjogMjAwMDAsCiAgICAgICAgICAibWF4X2JhY2t0cmFja3MiOiAxMQogICAgICAgIH0sCiAgICAgICAgImxvYWRpbmciOiB7CiAgICAgICAgICAidmVyc2lvbiI6ICJsYWJvcmF0b3J5LWNvbnRyb2xzLTAuMSIsCiAgICAgICAgICAiZW5jb2RpbmciOiAiaWVlZTc1NC1iaW5hcnk2NC1oZXgiLAogICAgICAgICAgInByb2R1Y2VyIjogewogICAgICAgICAgICAidmVyc2lvbiI6ICJsYWJvcmF0b3J5LXdhdmVmb3JtLTAuMSIsCiAgICAgICAgICAgICJhbGdvcml0aG0iOiAibGluZWFyLXJuZS12MSIsCiAgICAgICAgICAgICJ0YXJnZXRfYml0cyI6ICIzZjg0N2FlMTQ3YWUxNDdiIiwKICAgICAgICAgICAgInN0ZXBzIjogMTAwLAogICAgICAgICAgICAiY3ljbGVzIjogMAogICAgICAgICAgfSwKICAgICAgICAgICJjb250cm9sc19iaXRzIjogWwogICAgICAgICAgICAiMDAwMDAwMDAwMDAwMDAwMCIsCiAgICAgICAgICAgICIzZjFhMzZlMmViMWM0MzJkIiwKICAgICAgICAgICAgIjNmMmEzNmUyZWIxYzQzMmQiLAogICAgICAgICAgICAiM2YzM2E5MmEzMDU1MzI2MSIsCiAgICAgICAgICAgICIzZjNhMzZlMmViMWM0MzJkIiwKICAgICAgICAgICAgIjNmNDA2MjRkZDJmMWE5ZmMiLAogICAgICAgICAgICAiM2Y0M2E5MmEzMDU1MzI2MSIsCiAgICAgICAgICAgICIzZjQ2ZjAwNjhkYjhiYWM4IiwKICAgICAgICAgICAgIjNmNGEzNmUyZWIxYzQzMmQiLAogICAgICAgICAgICAiM2Y0ZDdkYmY0ODdmY2I5MiIsCiAgICAgICAgICAgICIzZjUwNjI0ZGQyZjFhOWZjIiwKICAgICAgICAgICAgIjNmNTIwNWJjMDFhMzZlMmYiLAogICAgICAgICAgICAiM2Y1M2E5MmEzMDU1MzI2MSIsCiAgICAgICAgICAgICIzZjU1NGM5ODVmMDZmNjk0IiwKICAgICAgICAgICAgIjNmNTZmMDA2OGRiOGJhYzgiLAogICAgICAgICAgICAiM2Y1ODkzNzRiYzZhN2VmYSIsCiAgICAgICAgICAgICIzZjVhMzZlMmViMWM0MzJkIiwKICAgICAgICAgICAgIjNmNWJkYTUxMTljZTA3NjAiLAogICAgICAgICAgICAiM2Y1ZDdkYmY0ODdmY2I5MiIsCiAgICAgICAgICAgICIzZjVmMjEyZDc3MzE4ZmM1IiwKICAgICAgICAgICAgIjNmNjA2MjRkZDJmMWE5ZmMiLAogICAgICAgICAgICAiM2Y2MTM0MDRlYTRhOGMxNSIsCiAgICAgICAgICAgICIzZjYyMDViYzAxYTM2ZTJmIiwKICAgICAgICAgICAgIjNmNjJkNzczMThmYzUwNDgiLAogICAgICAgICAgICAiM2Y2M2E5MmEzMDU1MzI2MSIsCiAgICAgICAgICAgICIzZjY0N2FlMTQ3YWUxNDdiIiwKICAgICAgICAgICAgIjNmNjU0Yzk4NWYwNmY2OTQiLAogICAgICAgICAgICAiM2Y2NjFlNGY3NjVmZDhhZSIsCiAgICAgICAgICAgICIzZjY2ZjAwNjhkYjhiYWM4IiwKICAgICAgICAgICAgIjNmNjdjMWJkYTUxMTljZTAiLAogICAgICAgICAgICAiM2Y2ODkzNzRiYzZhN2VmYSIsCiAgICAgICAgICAgICIzZjY5NjUyYmQzYzM2MTEzIiwKICAgICAgICAgICAgIjNmNmEzNmUyZWIxYzQzMmQiLAogICAgICAgICAgICAiM2Y2YjA4OWEwMjc1MjU0NiIsCiAgICAgICAgICAgICIzZjZiZGE1MTE5Y2UwNzYwIiwKICAgICAgICAgICAgIjNmNmNhYzA4MzEyNmU5N2EiLAogICAgICAgICAgICAiM2Y2ZDdkYmY0ODdmY2I5MiIsCiAgICAgICAgICAgICIzZjZlNGY3NjVmZDhhZGFjIiwKICAgICAgICAgICAgIjNmNmYyMTJkNzczMThmYzUiLAogICAgICAgICAgICAiM2Y2ZmYyZTQ4ZThhNzFkZiIsCiAgICAgICAgICAgICIzZjcwNjI0ZGQyZjFhOWZjIiwKICAgICAgICAgICAgIjNmNzBjYjI5NWU5ZTFiMDkiLAogICAgICAgICAgICAiM2Y3MTM0MDRlYTRhOGMxNSIsCiAgICAgICAgICAgICIzZjcxOWNlMDc1ZjZmZDIyIiwKICAgICAgICAgICAgIjNmNzIwNWJjMDFhMzZlMmYiLAogICAgICAgICAgICAiM2Y3MjZlOTc4ZDRmZGYzYyIsCiAgICAgICAgICAgICIzZjcyZDc3MzE4ZmM1MDQ4IiwKICAgICAgICAgICAgIjNmNzM0MDRlYTRhOGMxNTUiLAogICAgICAgICAgICAiM2Y3M2E5MmEzMDU1MzI2MSIsCiAgICAgICAgICAgICIzZjc0MTIwNWJjMDFhMzZlIiwKICAgICAgICAgICAgIjNmNzQ3YWUxNDdhZTE0N2IiLAogICAgICAgICAgICAiM2Y3NGUzYmNkMzVhODU4OCIsCiAgICAgICAgICAgICIzZjc1NGM5ODVmMDZmNjk0IiwKICAgICAgICAgICAgIjNmNzViNTczZWFiMzY3YTEiLAogICAgICAgICAgICAiM2Y3NjFlNGY3NjVmZDhhZSIsCiAgICAgICAgICAgICIzZjc2ODcyYjAyMGM0OWJiIiwKICAgICAgICAgICAgIjNmNzZmMDA2OGRiOGJhYzgiLAogICAgICAgICAgICAiM2Y3NzU4ZTIxOTY1MmJkNCIsCiAgICAgICAgICAgICIzZjc3YzFiZGE1MTE5Y2UwIiwKICAgICAgICAgICAgIjNmNzgyYTk5MzBiZTBkZWQiLAogICAgICAgICAgICAiM2Y3ODkzNzRiYzZhN2VmYSIsCiAgICAgICAgICAgICIzZjc4ZmM1MDQ4MTZmMDA2IiwKICAgICAgICAgICAgIjNmNzk2NTJiZDNjMzYxMTMiLAogICAgICAgICAgICAiM2Y3OWNlMDc1ZjZmZDIyMCIsCiAgICAgICAgICAgICIzZjdhMzZlMmViMWM0MzJkIiwKICAgICAgICAgICAgIjNmN2E5ZmJlNzZjOGI0M2EiLAogICAgICAgICAgICAiM2Y3YjA4OWEwMjc1MjU0NiIsCiAgICAgICAgICAgICIzZjdiNzE3NThlMjE5NjUzIiwKICAgICAgICAgICAgIjNmN2JkYTUxMTljZTA3NjAiLAogICAgICAgICAgICAiM2Y3YzQzMmNhNTdhNzg2ZCIsCiAgICAgICAgICAgICIzZjdjYWMwODMxMjZlOTdhIiwKICAgICAgICAgICAgIjNmN2QxNGUzYmNkMzVhODUiLAogICAgICAgICAgICAiM2Y3ZDdkYmY0ODdmY2I5MiIsCiAgICAgICAgICAgICIzZjdkZTY5YWQ0MmMzYzlmIiwKICAgICAgICAgICAgIjNmN2U0Zjc2NWZkOGFkYWMiLAogICAgICAgICAgICAiM2Y3ZWI4NTFlYjg1MWViOCIsCiAgICAgICAgICAgICIzZjdmMjEyZDc3MzE4ZmM1IiwKICAgICAgICAgICAgIjNmN2Y4YTA5MDJkZTAwZDIiLAogICAgICAgICAgICAiM2Y3ZmYyZTQ4ZThhNzFkZiIsCiAgICAgICAgICAgICIzZjgwMmRlMDBkMWI3MTc2IiwKICAgICAgICAgICAgIjNmODA2MjRkZDJmMWE5ZmMiLAogICAgICAgICAgICAiM2Y4MDk2YmI5OGM3ZTI4MyIsCiAgICAgICAgICAgICIzZjgwY2IyOTVlOWUxYjA5IiwKICAgICAgICAgICAgIjNmODBmZjk3MjQ3NDUzOGYiLAogICAgICAgICAgICAiM2Y4MTM0MDRlYTRhOGMxNSIsCiAgICAgICAgICAgICIzZjgxNjg3MmIwMjBjNDljIiwKICAgICAgICAgICAgIjNmODE5Y2UwNzVmNmZkMjIiLAogICAgICAgICAgICAiM2Y4MWQxNGUzYmNkMzVhOCIsCiAgICAgICAgICAgICIzZjgyMDViYzAxYTM2ZTJmIiwKICAgICAgICAgICAgIjNmODIzYTI5Yzc3OWE2YjUiLAogICAgICAgICAgICAiM2Y4MjZlOTc4ZDRmZGYzYyIsCiAgICAgICAgICAgICIzZjgyYTMwNTUzMjYxN2MyIiwKICAgICAgICAgICAgIjNmODJkNzczMThmYzUwNDgiLAogICAgICAgICAgICAiM2Y4MzBiZTBkZWQyODhjZiIsCiAgICAgICAgICAgICIzZjgzNDA0ZWE0YThjMTU1IiwKICAgICAgICAgICAgIjNmODM3NGJjNmE3ZWY5ZGMiLAogICAgICAgICAgICAiM2Y4M2E5MmEzMDU1MzI2MSIsCiAgICAgICAgICAgICIzZjgzZGQ5N2Y2MmI2YWU4IiwKICAgICAgICAgICAgIjNmODQxMjA1YmMwMWEzNmUiLAogICAgICAgICAgICAiM2Y4NDQ2NzM4MWQ3ZGJmNCIsCiAgICAgICAgICAgICIzZjg0N2FlMTQ3YWUxNDdiIgogICAgICAgICAgXQogICAgICAgIH0KICAgICAgfSwKICAgICAgIm1lc3NhZ2UiOiAiY29udHJvbCBvciBjb25zdGl0dXRpdmUgc29sdmUgZmFpbGVkIGF0IHN0ZXAgMTsgbGFzdCBjb21taXR0ZWQgcG9pbnQgcmV0YWluZWQiLAogICAgICAiY29tbWl0dGVkX3BvaW50cyI6IDEsCiAgICAgICJuYW1lZF9leGFtcGxlIjogImdpczIwMjQtc21hbGwtZHJhaW5lZCIsCiAgICAgICJldmlkZW5jZSI6IHsKICAgICAgICAicGF0aCI6ICJkb2NzL3Jldmlld3MvbWMtcm9vdC1pbnRlZ3JhdGlvbi12My9zdHJpY3QtZGVmYXVsdHMuanNvbiIsCiAgICAgICAgInNoYTI1NiI6ICJiYTcxNzkxNWQ5ODA0YzMyNjFlMjdiMzRiZTBmMmRlOTU1M2Q4YjgxMjk0MmQzMGE4ZTQzNjk3MTk3MjdmYWExIgogICAgICB9CiAgICB9CiAgXSwKICAibGltaXRhdGlvbnMiOiBbCiAgICAiVGhpcyBnYXRlIHZlcmlmaWVzIG9yZGluYXJ5IHJ1bnMgYW5kIGV4cGxpY2l0bHkgcmVnaXN0ZXJlZCBzdXBwb3J0ZWQgZXhhbXBsZXMsIG5vdCBzdWNjZXNzIG9mIGV2ZXJ5IG1vZGVsIGRlZmF1bHQuIFRoZSBzZXBhcmF0ZSBzdHJpY3QgYWxsLWRlZmF1bHQgZ2F0ZSByZW1haW5zIGZhaWxlZCBmb3IgdGhlIGRlY2xhcmVkIEdJUyBjYXNlLiIsCiAgICAiTm8gbW9kZWwtc291cmNlLCBzY2llbnRpZmljIGFwcGxpY2FiaWxpdHksIHByZXBhcmF0aW9uLCBjYWxpYnJhdGlvbiBvciBleHBlcmltZW50YWwgdmFsaWRhdGlvbiBpcyBjZXJ0aWZpZWQuIE5vIG5ldyBtb2RlbCBvciBhbHRlcmVkIGRlZmluaXRpb24gaXMgYWRtaXR0ZWQgYXV0b21hdGljYWxseS4iLAogICAgIk9DQyBleGFjdCBxdWFsaWZpZWQgbm9taW5hbCBmb3JtdWxhdGlvbjsgb3JkaW5hcnkgZHJhaW5lZCBkZWZhdWx0IG11c3Qgc3VjY2VlZC4gQ3ljbGljIHN0cmVzcyB1bmxvYWRpbmcgaXMgdW5zdXBwb3J0ZWQgYW5kIHNlcGFyYXRlbHkgcmV0YWluZWQ7IG5vIHVuaWZvcm0gdGlueS1wb3NpdGl2ZS1wcmVzc3VyZSByZWxhdGl2ZSBhY2N1cmFjeS4iLAogICAgIkR1bmNhbuKAk0NoYW5nIGNvbnN0YW50LW51IGVuZHBvaW50LWF2ZXJhZ2U6IGV4YWN0IGluZGVwZW5kZW50bHkgcmV2aWV3ZWQgZGVmaW5pdGlvbjsgc291cmNlLWNvZWZmaWNpZW50IHByZXNldHMgYXJlIGlsbHVzdHJhdGl2ZSwgd2l0aCBubyBjYWxpYnJhdGlvbiwgZXhwZXJpbWVudGFsIHZhbGlkYXRpb24gb3IgRkUtaG9zdCB0YW5nZW50IGNsYWltLiBPcmRpbmFyeSBkZWZhdWx0IGlzIGFuIGFkZGl0aW9uYWwgc29mdHdhcmUgcXVhbGlmaWNhdGlvbi4iCiAgXQp9Cg=='}

if __name__=='__main__':unittest.main()
