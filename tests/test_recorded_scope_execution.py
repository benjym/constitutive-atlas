"""Strict scoped adapters: saved native responses, corruptions, and no fallback."""
import copy,json,subprocess,unittest
from unittest.mock import patch
from atlas.dsl import ValidationError
from atlas.model import ROOT
from atlas.recorded_scope_execution import execute_scoped_recorded,verify_scoped_recorded_response
from tests.scoped_recorded_execution_cases import retained


def response_corpus():
    catalogue,rows=retained();assert len(rows)==16
    for row in rows:row['accepted']=True
    good=next(r for r in rows if r['label']=='total-mixed');failure=next(r for r in rows if r['label']=='scope-failed-1')
    for change in ['version','scope','descriptor-extra','catalogue','model','wire','knots','initial-strain','initial','parameters','settings','settings-extra','boolean','control-extra','restart','restart-extra','restart-count','trials','coordinate','partial','final','point-state','point-strain','failure-prefix','empty-failure']:
        row=copy.deepcopy(failure if change in ['failure-prefix','empty-failure'] else good);r=row['response'];row['accepted']=False;row['label']=change
        if change=='version':r['api_version']='experimental-recorded-replay-0.1'
        elif change=='scope':r['stress']['scope']='effective'
        elif change=='descriptor-extra':r['stress']['extra']=True
        elif change=='catalogue':r['catalogue_hash']='0'*64
        elif change=='model':r['model']='another'
        elif change=='wire':r['controls_wire'][0]+=1
        elif change=='knots':r['knots_wire'][0]+=1
        elif change=='initial-strain':r['initial_strain'][0]+=1
        elif change=='initial':r['initial'][0]+=1
        elif change=='parameters':r['parameters'][0]+=1
        elif change=='settings':r['integration_settings']['max_iterations']+=1
        elif change=='settings-extra':r['integration_settings']['extra']=1
        elif change=='boolean':r['control_settings']['max_backtracks']=True
        elif change=='control-extra':r['control_settings']['extra']=1
        elif change=='restart':r['restart_settings']['max_restarts']=0
        elif change=='restart-extra':r['restart_settings']['extra']=1
        elif change=='restart-count':r['restart_diagnostics']['accepted']=1
        elif change=='trials':r['material_trials']=-1
        elif change=='coordinate':r['points'][1]['coordinate']+=1
        elif change=='partial':r['points'].pop()
        elif change=='final':r['state'][0]+=1
        elif change=='point-state':r['points'][1]['state'].pop()
        elif change=='point-strain':r['points'][1]['strain'][0]='bad'
        elif change=='failure-prefix':r['failed_knot']=1
        elif change=='empty-failure':r['points']=[]
        rows.append(row)
    return catalogue,rows

class ScopedRecordedExecutionTests(unittest.TestCase):
    def test_response_checks_and_browser_parity(self):
        catalogue,rows=response_corpus();before=copy.deepcopy((catalogue,rows))
        for row in rows:
            if row['accepted']:self.assertIs(verify_scoped_recorded_response(row['response'],row['request'],catalogue),row['response'])
            else:
                with self.subTest(row=row['label']),self.assertRaises((RuntimeError,ValidationError)):verify_scoped_recorded_response(row['response'],row['request'],catalogue)
        result=subprocess.run(['node','tests/test_recorded_scope_execution_browser.mjs'],cwd=ROOT,input=json.dumps(dict(catalogue=catalogue,rows=rows),allow_nan=False),capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertEqual(json.loads(result.stdout),[r['accepted'] for r in rows]);self.assertEqual((catalogue,rows),before)

    def test_native_routing_and_failed_prefix(self):
        catalogue,rows=retained()
        for row in rows:
            with patch('subprocess.run',side_effect=[subprocess.CompletedProcess([],0,json.dumps(catalogue),''),subprocess.CompletedProcess([],row['returncode'],json.dumps(row['response']),'')]) as run:
                self.assertEqual(execute_scoped_recorded(row['request'],catalogue,'unused'),row['response'])
                self.assertEqual(run.call_count,2);args=run.call_args_list[1].args[0];self.assertEqual(args[args.index('--recorded-stress-scope')+1],row['request']['stress_scope']);self.assertEqual('--recorded-restarts' in args,'restart_settings' in row['request'])

    def test_preflight_scope_descriptor_order_and_exit_rejection(self):
        catalogue,rows=retained();row=rows[0]
        wrong=copy.deepcopy(row['request']);wrong['stress_scope']='total'
        with patch('subprocess.run') as run:
            with self.assertRaises(ValidationError):execute_scoped_recorded(wrong,catalogue,'unused')
            run.assert_not_called()
        for change in ['descriptor','order']:
            described=copy.deepcopy(catalogue)
            if change=='descriptor':described['sha256']='0'*64
            else:described['models'][0]['parameters']=dict(reversed(list(described['models'][0]['parameters'].items())))
            with patch('subprocess.run',return_value=subprocess.CompletedProcess([],0,json.dumps(described),'')) as run:
                with self.assertRaises(RuntimeError):execute_scoped_recorded(row['request'],catalogue,'unused')
                self.assertEqual(run.call_count,1)
        for bad in [subprocess.CompletedProcess([],1,json.dumps(row['response']),''),subprocess.CompletedProcess([],1,json.dumps(dict(ok=False,message='missing scoped export')),'')]:
            with patch('subprocess.run',side_effect=[subprocess.CompletedProcess([],0,json.dumps(catalogue),''),bad]) as run:
                with self.assertRaises(RuntimeError):execute_scoped_recorded(row['request'],catalogue,'unused')
                self.assertEqual(run.call_count,2)

if __name__=='__main__':unittest.main()
