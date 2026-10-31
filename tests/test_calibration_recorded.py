"""Synthetic durable runner tests with analytical native-API doubles; no processes."""
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from atlas.calibration_recorded import run_recorded_search
from atlas.calibration_search import METHOD
from atlas.experiment_replay import digest
from atlas.model import ROOT, load
from tests.test_experiment_replay import synthetic


class RecordedCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name);self.output=self.folder/'run'
        self.solver=self.folder/'fake-solver';self.solver.write_bytes(b'not executable; API doubles only')
        self.sh=hashlib.sha256(self.solver.read_bytes()).hexdigest()
        self.model=load(ROOT/'models/linear-elastic.json')
        self.catalogue={'schema_version':'0.1','sha256':digest([self.model]),'models':[copy.deepcopy(self.model)]}
        exp,config=synthetic();config['parameters']['E']=2e7
        self.tid=exp['id'];self.experiments={self.tid:exp};self.configs={self.tid:config}
        self.reserve={'paper_reservation_version':1,'id':'synthetic-reservations',
            'experiments':[{'id':self.tid,'role':'development'},{'id':'E','role':'development'},
                           {'id':'R','role':'reserved_final'}]}
        self.rh=hashlib.sha256(json.dumps(self.reserve).encode()).hexdigest()
        self.allocation={'schema_version':'0.1','kind':'whole-test-study-allocation','id':'synthetic-allocation',
            'phase':'development','grouping_unit':'whole_test','evaluation_claim':'previously_exposed_development',
            'calibration_packages':{'fit':[self.tid]},'evaluation_ids':['E'],
            'reservation_policy':{'id':'synthetic-reservations','sha256':self.rh},'limitations':['Synthetic only.']}
        self.ah=hashlib.sha256(json.dumps(self.allocation).encode()).hexdigest()
        self.objective={'schema_version':'0.1','kind':'study-objective','id':'synthetic-objective',
            'allocation_sha256':self.ah,'package':'fit','method':'piecewise-linear-residual-axial-travel-v1',
            'test_aggregation':'equal_whole_test','failure_policy':'reject_entire_candidate',
            'channels':{'q':{'unit':'Pa','scale':30000.,'weight':1.},
                        'volumetric_strain':{'unit':'1','scale':.001,'weight':1.}}}
        self.spec={'id':'synthetic-recorded-search','method':METHOD,
            'parameters':copy.deepcopy(config['parameters']),
            'fitted':[{'name':'E','bounds':[1e7,5e7],'transform':'linear'}],
            'max_evaluations':3,'initial_step':.25,'minimum_step':.0625}

    def response(self,request,solver,timeout):
        params=dict(zip(self.model['parameters'],request['parameters']))
        E,nu=params['E'],params['nu'];initial=request['initial'];origin=request['path']['initial_strain']
        points=[]
        for knot in request['path']['knots']:
            axial=knot['targets'][0]-origin[0];radial=knot['targets'][1]
            stress=initial[0]+E*axial+2*nu*(radial-initial[1])
            lateral=-nu*axial+(1+nu)*(1-2*nu)*(radial-initial[1])/E
            strain=[origin[0]+axial,origin[1]+lateral,origin[2]+lateral,0,0,0]
            volume=axial+2*lateral
            state=[stress,radial,radial,0,0,0,(1+initial[6])*math.exp(-volume)-1]
            points.append({'coordinate':knot['coordinate'],'state':state,'strain':strain,'control_error':0.})
        return {'ok':True,'api_version':'experimental-recorded-replay-0.1','catalogue_hash':self.catalogue['sha256'],
                'model':request['model'],'parameters':request['parameters'],'initial':initial,'points':points,
                'state':points[-1]['state'],'strain':points[-1]['strain']}

    def run_case(self,executor=None):
        metadata=subprocess.CompletedProcess([],0,json.dumps(self.catalogue),'')
        with patch('atlas.calibration_recorded.subprocess.run',return_value=metadata) as describe,\
             patch('atlas.calibration_recorded.execute_recorded',side_effect=executor or self.response) as execute:
            result=run_recorded_search(self.spec,self.objective,self.allocation,self.reserve,self.model,
                self.experiments,self.configs,allocation_sha256=self.ah,reservation_sha256=self.rh,
                solver=self.solver,solver_sha256=self.sh,catalogue=self.catalogue,output=self.output)
        return result,describe,execute

    def test_complete_serial_run_best_persistent_receipts_and_input_isolation(self):
        before=copy.deepcopy((self.experiments,self.configs,self.spec))
        result,describe,execute=self.run_case()
        self.assertEqual(describe.call_count,1);self.assertEqual(execute.call_count,3)
        self.assertEqual(result['best']['parameters']['E'],3e7)
        self.assertLess(result['best']['objective'],1e-22)
        self.assertEqual(before,(self.experiments,self.configs,self.spec))
        requests=[]
        for i in range(3):
            directory=self.output/f'candidate-{i:05d}'
            request=json.loads((directory/'000-request.json').read_text())['request'];requests.append(request)
            self.assertEqual(json.loads((directory/'assessment.json').read_text()),result['candidates'][i])
            self.assertTrue((directory/'000-response.json').is_file())
        self.assertEqual([r['parameters'][1] for r in requests],[2e7,1e7,3e7])
        self.assertTrue(all(r['initial']==requests[0]['initial'] for r in requests))
        manifest=json.loads((self.output/'manifest.json').read_text())
        for path,h in manifest['files'].items():
            self.assertEqual(hashlib.sha256((self.output/path).read_bytes()).hexdigest(),h)
        self.assertFalse(manifest['scientific_admission'])
        with self.assertRaisesRegex(ValueError,'already exists'):self.run_case()

    def test_each_whole_test_has_its_own_fresh_preparation(self):
        tid='synthetic-second'
        self.experiments[tid]=copy.deepcopy(self.experiments[self.tid]);self.experiments[tid]['id']=tid
        self.configs[tid]=copy.deepcopy(self.configs[self.tid]);self.configs[tid]['initial_history']['e']=.9
        self.reserve['experiments'].append({'id':tid,'role':'development'})
        self.rh=hashlib.sha256(json.dumps(self.reserve).encode()).hexdigest()
        self.allocation['reservation_policy']['sha256']=self.rh
        self.allocation['calibration_packages']['fit'].append(tid)
        self.ah=hashlib.sha256(json.dumps(self.allocation).encode()).hexdigest()
        self.objective['allocation_sha256']=self.ah
        result,_,execute=self.run_case()
        self.assertEqual(result['status'],'success');self.assertEqual(execute.call_count,6)
        for i in range(3):
            directory=self.output/f'candidate-{i:05d}'
            states=[json.loads((directory/f'{j:03d}-request.json').read_text())['request']['initial'] for j in range(2)]
            self.assertEqual([z[6] for z in states],[.7,.9])
            self.assertEqual(states[0][:6],states[1][:6])

    def test_native_descriptor_mismatch_stops_before_material_and_output(self):
        with patch('atlas.calibration_recorded.subprocess.run',return_value=subprocess.CompletedProcess([],0,'{}','')) as metadata,patch('atlas.calibration_recorded.execute_recorded') as execute:
            with self.assertRaisesRegex(ValueError,'descriptor'):
                run_recorded_search(self.spec,self.objective,self.allocation,self.reserve,self.model,
                    self.experiments,self.configs,allocation_sha256=self.ah,reservation_sha256=self.rh,
                    solver=self.solver,solver_sha256=self.sh,catalogue=self.catalogue,output=self.output)
            self.assertEqual(metadata.call_count,1);execute.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_failed_prefix_is_saved_and_entire_candidate_rejected(self):
        def fail(request,solver,timeout):
            response=self.response(request,solver,timeout)
            response.update(ok=False,message='synthetic nonconvergence',points=response['points'][:2])
            return response
        result,_,execute=self.run_case(fail)
        self.assertEqual(execute.call_count,3);self.assertEqual(result['status'],'no_feasible_candidate')
        self.assertTrue(all(r['objective'] is None for r in result['candidates']))
        saved=json.loads((self.output/'candidate-00000/000-response.json').read_text())
        self.assertEqual(len(saved['points']),2)

    def test_transport_exception_is_persisted_fatal_and_not_retried(self):
        def broken(*args,**kwargs):raise RuntimeError('exit/status mismatch')
        result,_,execute=self.run_case(broken)
        self.assertEqual(execute.call_count,1);self.assertEqual(result['status'],'error')
        self.assertEqual(result['stop_reason'],'evaluator_error')
        self.assertTrue((self.output/'candidate-00000/000-execution-error.json').is_file())
        self.assertTrue((self.output/'candidate-00000/assessment.json').is_file())

    def test_response_identity_order_and_completion_corruption_is_fatal(self):
        for defect in ['parameters','initial','catalogue','order','truncated','control','final']:
            self.output=self.folder/defect
            def corrupted(request,solver,timeout):
                r=copy.deepcopy(self.response(request,solver,timeout))
                if defect=='parameters':r['parameters'][1]=9.
                if defect=='initial':r['initial'][0]=0.
                if defect=='catalogue':r['catalogue_hash']='0'*64
                if defect=='order':r['points'][1]['coordinate']=9
                if defect=='truncated':r['points'].pop()
                if defect=='control':r['points'][1]['control_error']=1.
                if defect=='final':r['state']=[0.]*7
                return r
            with self.subTest(defect=defect):
                result,_,execute=self.run_case(corrupted)
                self.assertEqual(result['status'],'error');self.assertEqual(execute.call_count,1)
                self.assertTrue((self.output/'candidate-00000/000-response.json').is_file())

    def test_wrong_dataset_model_or_executable_never_calls_native(self):
        variants=['reserved','seed','bounds','binary','order','volume']
        for defect in variants:
            with self.subTest(defect=defect):
                old=copy.deepcopy((self.experiments,self.configs,self.spec,self.catalogue,self.sh))
                if defect=='reserved':self.experiments['R']=self.experiments[self.tid]
                if defect=='seed':self.configs[self.tid]['parameters']['E']=4e7
                if defect=='bounds':self.spec['fitted'][0]['bounds'][1]=1e15
                if defect=='binary':self.sh='0'*64
                if defect=='order':self.catalogue['models'][0]['parameters']=dict(reversed(list(self.model['parameters'].items())))
                if defect=='volume':self.experiments[self.tid]['rows'][0]['volumetric_strain']=.1
                with patch('atlas.calibration_recorded.subprocess.run') as metadata,patch('atlas.calibration_recorded.execute_recorded') as execute:
                    with self.assertRaises(ValueError):
                        run_recorded_search(self.spec,self.objective,self.allocation,self.reserve,self.model,
                            self.experiments,self.configs,allocation_sha256=self.ah,reservation_sha256=self.rh,
                            solver=self.solver,solver_sha256=self.sh,catalogue=self.catalogue,output=self.output)
                    metadata.assert_not_called();execute.assert_not_called()
                self.experiments,self.configs,self.spec,self.catalogue,self.sh=old
                self.assertFalse(self.output.exists())

    def test_assessment_write_failure_leaves_incomplete_run_and_no_next_call(self):
        from atlas import calibration_recorded as runner
        write=runner._write
        def fail(path,value):
            if Path(path).name=='assessment.json':raise OSError('synthetic disk full')
            return write(path,value)
        with patch.object(runner,'_write',side_effect=fail):
            with self.assertRaisesRegex(OSError,'disk full'):self.run_case()
        self.assertTrue((self.output/'candidate-00000/000-response.json').is_file())
        self.assertFalse((self.output/'candidate-00001').exists())
        self.assertFalse((self.output/'result.json').exists())
        self.assertFalse((self.output/'manifest.json').exists())


if __name__=='__main__':unittest.main()
