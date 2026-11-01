"""Recorded JSON contract tests; opt-in serial native API/CLI checks.

ATLAS_RECORDED_SOLVER selects an existing binary; tests never compile it.
ATLAS_RECORDED_CAPTURE optionally retains all native responses as gzip JSON.
"""
import copy
import gzip
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from atlas.dsl import ValidationError
from atlas.model import ROOT, all_models
from atlas.stress import stress_scope
from atlas.recorded_scope_execution import execute_scoped_recorded
from atlas.recorded import (CONTROL_DEFAULTS, MATERIAL_DEFAULTS, execute_recorded,
                            recorded_wire, validate_recorded_run)


def specimen():
    path=json.loads((ROOT/'protocols/recorded-drained-reversal.json').read_text())
    return dict(version='experimental-recorded-run-0.1', model='linear-elastic', path=path)


class RecordedRunContractTests(unittest.TestCase):
    def test_roundtrip_no_mutation(self):
        spec=specimen();before=copy.deepcopy(spec)
        self.assertIs(validate_recorded_run(spec),spec)
        c,k=recorded_wire(spec)
        self.assertEqual(len(c),42);self.assertEqual(len(k),7*len(spec['path']['knots']))
        self.assertEqual(k[::7],[r['coordinate'] for r in spec['path']['knots']])
        self.assertEqual(spec,before)

    def test_closed_request_and_settings(self):
        for field,value in [('extra',1),('initial',[]),('parameters',[]),('initial',[2**53+1]*7),('model',4),
                            ('integration_settings',{'max_depth':21}),
                            ('integration_settings',{'max_iterations':True}),
                            ('control_settings',{'max_material_trials':0}),
                            ('control_settings',{'finite_difference_step':float('nan')}),
                            ('control_settings',{'extra':1})]:
            with self.subTest(field=field,value=value):
                s=specimen();s[field]=value
                with self.assertRaises(ValidationError):validate_recorded_run(s)

    def test_invalid_document_never_executes(self):
        s=specimen();s['path']['knots'].reverse()
        with patch('subprocess.run') as run:
            with self.assertRaises(ValidationError):execute_recorded(s,'unused')
            run.assert_not_called()

    def test_invalid_solver_output(self):
        for stdout,code in [('not-json',1),('[]',0),('{"ok":true}',0),('{"ok":true}',1),('{"ok":false}',0)]:
            with self.subTest(stdout=stdout,code=code), patch('subprocess.run',return_value=subprocess.CompletedProcess([],code,stdout,'')):
                with self.assertRaises(RuntimeError):execute_recorded(specimen(),'unused')


@unittest.skipUnless(os.environ.get('ATLAS_RECORDED_SOLVER'),'set ATLAS_RECORDED_SOLVER to an existing binary')
class RecordedNativeAPITests(unittest.TestCase):
    records=[]
    @classmethod
    def tearDownClass(cls):
        target=os.environ.get('ATLAS_RECORDED_CAPTURE')
        if target:Path(target).write_bytes(gzip.compress(json.dumps(cls.records,allow_nan=False).encode(),mtime=0))

    def run_spec(self,spec):
        solver=os.environ['ATLAS_RECORDED_SOLVER']
        if spec['version']=='experimental-recorded-run-0.2':
            catalogue=json.loads(subprocess.check_output([solver,'--describe'],text=True))
            self.assertEqual(catalogue['models'],all_models())
            result=execute_scoped_recorded(spec,catalogue,solver)
        else:
            result=execute_recorded(spec,solver)
        self.records.append(dict(request=copy.deepcopy(spec),response=copy.deepcopy(result)))
        json.dumps(result,allow_nan=False)
        if spec['version']=='experimental-recorded-run-0.2':
            self.assertEqual(result['stress']['scope'],spec['stress_scope'])
            return result
        self.assertEqual(result['specification'],spec)
        self.assertEqual(len(result['request_sha256']),64)
        return result

    def test_drained_analytical_reversal_and_duplicates(self):
        s=specimen();s['path']['knots'].insert(2,copy.deepcopy(s['path']['knots'][1]))
        for i,k in enumerate(s['path']['knots']):k['coordinate']=i
        r=self.run_spec(s);self.assertTrue(r['ok'],r['message'])
        self.assertEqual(r['integration_settings']|MATERIAL_DEFAULTS,r['integration_settings'])
        for key,value in MATERIAL_DEFAULTS.items():self.assertEqual(r['integration_settings'][key],value)
        self.assertEqual(r['control_settings'],CONTROL_DEFAULTS)
        for k,pt in zip(s['path']['knots'],r['points']):
            axial=k['targets'][0]
            expected=[axial,-.25*axial,-.25*axial,0,0,0]
            for a,b in zip(pt['strain'],expected):self.assertAlmostEqual(a,b,delta=2e-11)
            self.assertAlmostEqual(pt['state'][0],100000+30000000*axial,delta=.002)
            self.assertAlmostEqual(pt['state'][6],1.7*math.exp(-.5*axial)-1,delta=2e-10)
        self.assertEqual(r['points'][1]['state'],r['points'][2]['state'])
        self.assertEqual(r['points'][2]['diagnostics']['substeps'],0)

    def test_all_stress_shears_and_oblique_rows(self):
        s=specimen();p=s['path'];p['initial_strain']=[.001,-.002,.003,.004,-.005,.006]
        p['controls']=[{'kind':'stress','coefficients':[int(i==j) for j in range(6)]} for i in range(6)]
        # Invertible oblique normal row; other five remain independent.
        p['controls'][0]['coefficients']=[1,.2,-.4,.3,0,0]
        stress0=[100000,100000,100000,0,0,0];p['knots']=[]
        strains=[[0]*6,[.0001,-.0002,.0003,.0004,-.0005,.0006],[-.0002,.0001,0,-.0001,.0002,-.0003]]
        for k,de in enumerate(strains):
            sigma=[stress0[j]+24000000*de[j]+(12000000*sum(de[:3]) if j<3 else 0) for j in range(6)]
            p['knots'].append({'coordinate':k*7-3,'targets':[sum(a*b for a,b in zip(c['coefficients'],sigma)) for c in p['controls']]})
        r=self.run_spec(s);self.assertTrue(r['ok'],r['message'])
        for pt,de in zip(r['points'],strains):
            for j in range(6):self.assertAlmostEqual(pt['strain'][j],p['initial_strain'][j]+de[j],delta=2e-11)

    def test_all_strain_each_public_model_and_restart(self):
        ids=subprocess.check_output([os.environ['ATLAS_RECORDED_SOLVER'],'--list'],text=True).splitlines()
        self.assertEqual(ids, [m['id'] for m in all_models()])
        for model in ids:
            with self.subTest(model=model):
                s=specimen();s['model']=model;p=s['path']
                definition=next(m for m in all_models() if m['id']==model)
                # Supply illustrative state explicitly, as v0.3 requires.
                s['initial']=[value for field in definition['state'] for value in
                              (field['initial'] if field.get('shape')=='sym' else [field['initial']])]
                for i,c in enumerate(p['controls']):c['kind']='strain';c['coefficients']=[int(i==j) for j in range(6)]
                p['knots']=[{'coordinate':k,'targets':[x,0,0,0,0,0]} for k,x in enumerate([0,.0001,-.0001,.0002])]
                is_gis=model=='research-hp-extracted-asbs-gis-2024-v03'
                if is_gis or stress_scope(definition)=='total':
                    original=self.run_spec(copy.deepcopy(s))
                    self.assertFalse(original['ok'])
                    if is_gis:
                        self.assertEqual(original['state'],s['initial'])
                        self.assertEqual(original['failed_knot'],1)
                        self.assertEqual(len(original['points']),1)
                    else:
                        self.assertIn('requires effective stress',original['message'])
                        self.assertNotIn('state',original)
                s['version']='experimental-recorded-run-0.2'
                s['stress_scope']=stress_scope(definition)
                if is_gis:s['integration_settings']={'max_depth':20}
                r=self.run_spec(s);self.assertTrue(r['ok'],r['message'])
                parent=r['initial']
                for i,pt in enumerate(r['points'][1:],1):
                    de=[pt['strain'][j]-r['points'][i-1]['strain'][j] for j in range(6)]
                    command=[os.environ['ATLAS_RECORDED_SOLVER'],'--mode','integrate','--model',model,'--initial',','.join(map(str,parent)),'--strain',','.join(map(str,de))]
                    if is_gis:
                        settings=MATERIAL_DEFAULTS|s['integration_settings']
                        command+=['--integration-settings',','.join(map(str,settings.values()))]
                    direct=json.loads(subprocess.check_output(command,text=True));self.assertTrue(direct['ok']);self.assertEqual(direct['state'],pt['state']);parent=pt['state']
                restart=copy.deepcopy(s);restart['initial']=r['points'][2]['state'];restart['path']['initial_strain']=r['points'][2]['strain'];restart['path']['knots']=p['knots'][2:]
                again=self.run_spec(restart);self.assertTrue(again['ok']);self.assertEqual(again['state'],r['state'])

    def test_failure_prefix_and_custom_budget(self):
        s=specimen();s['control_settings']={'max_material_trials':1}
        r=self.run_spec(s);self.assertFalse(r['ok']);self.assertEqual(r['failed_knot'],1)
        self.assertEqual(len(r['points']),1);self.assertEqual(r['state'],r['initial'])
        self.assertEqual(r['strain'],s['path']['initial_strain']);self.assertEqual(r['material_trials'],1)
        # An all-strain record consumes one trial, then the same budget fails
        # at the next record while preserving a nonempty advanced prefix.
        for i,row in enumerate(s['path']['controls']):
            row['kind']='strain';row['coefficients']=[int(i==j) for j in range(6)]
        s['path']['knots']=[{'coordinate':i,'targets':[x,0,0,0,0,0]} for i,x in enumerate([0,.001,-.001])]
        r=self.run_spec(s);self.assertFalse(r['ok']);self.assertEqual(r['failed_knot'],2)
        self.assertEqual(len(r['points']),2);self.assertEqual(r['state'],r['points'][-1]['state'])
        self.assertEqual(r['strain'],r['points'][-1]['strain']);self.assertNotEqual(r['state'],r['initial'])

    def test_first_knot_mismatch_has_no_prefix(self):
        s=specimen();s['path']['knots'][0]['targets'][0]=.01
        r=self.run_spec(s);self.assertFalse(r['ok']);self.assertEqual(r['points'],[])
        self.assertEqual(r['state'],r['initial']);self.assertEqual(r['material_trials'],0)

    def test_5001_observations_no_argument_limit(self):
        s=specimen();k=s['path']['knots'][0];s['path']['knots']=[dict(coordinate=i/3,targets=k['targets']) for i in range(5001)]
        r=self.run_spec(s);self.assertTrue(r['ok']);self.assertEqual(len(r['points']),5001);self.assertEqual(r['material_trials'],0)

    def test_json_cli_writes_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'request.json';out=Path(tmp)/'result.json'
            for good in (True,False):
                s=specimen()
                if not good:s['model']='unknown'
                source.write_text(json.dumps(s))
                process=subprocess.run([sys.executable,'-m','atlas.cli','replay',str(source),'--solver',os.environ['ATLAS_RECORDED_SOLVER'],'--output',str(out)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(process.returncode,0 if good else 1,process.stderr)
                self.assertEqual(json.loads(out.read_text())['ok'],good)

    def test_native_wire_rejection_and_mode_separation(self):
        c,k=recorded_wire(specimen())
        with tempfile.TemporaryDirectory() as tmp:
            cf,kf=Path(tmp)/'c.csv',Path(tmp)/'k.csv'
            base=[os.environ['ATLAS_RECORDED_SOLVER'],'--mode','recorded','--model','linear-elastic','--initial-strain','0,0,0,0,0,0','--recorded-controls-file',str(cf),'--recorded-knots-file',str(kf)]
            for changed,wire in [('tag',[2]+c[1:]),('length',c[:-1]),('nan',[float('nan')]+c[1:])]:
                cf.write_text(','.join(map(str,wire)));kf.write_text(','.join(map(str,k)))
                result=subprocess.run(base,capture_output=True,text=True);self.assertEqual(result.returncode,1);self.assertFalse(json.loads(result.stdout)['ok'])
            cf.write_text(','.join(map(str,c)));kf.write_text(','.join(map(str,k)))
            for extra in [['--target','.01'],['--recorded-settings','1e-10,1.5,10,20,1e-7'],['--integration-settings','1e-10,1e-6,45,21,100,10']]:
                result=subprocess.run(base+extra,capture_output=True,text=True);self.assertEqual(result.returncode,1);self.assertFalse(json.loads(result.stdout)['ok'])
            result=subprocess.run([os.environ['ATLAS_RECORDED_SOLVER'],'--mode','integrate','--model','linear-elastic','--recorded-knots-file',str(kf)],capture_output=True,text=True)
            self.assertEqual(result.returncode,1);self.assertFalse(json.loads(result.stdout)['ok'])



class RetainedRecordedAPITests(unittest.TestCase):
    def rows(self):
        path=ROOT/'catalogue/investigations/recorded-replay-api-v1/responses.json.gz'
        return json.loads(gzip.decompress(path.read_bytes()))

    def test_retained_endpoint_and_request_consistency(self):
        from tools.verify_recorded_replay import verify
        self.assertEqual(verify(self.rows())['cases'],16)

    def test_corrupt_endpoint_and_prefix_rejected(self):
        from tools.verify_recorded_replay import verify
        rows=self.rows();rows[0]['response']['points'][1]['strain'][0]+=.01
        with self.assertRaises(ValueError):verify(rows)
        rows=self.rows();r=next(row['response'] for row in rows if not row['response']['ok'] and row['response']['points'])
        r['state'][0]+=1
        with self.assertRaises(ValueError):verify(rows)

    def test_existing_commands_unchanged(self):
        path=ROOT/'catalogue/investigations/recorded-replay-api-v1/compatibility.json.gz'
        rows=json.loads(gzip.decompress(path.read_bytes()))
        self.assertEqual(len(rows),46)
        for row in rows:self.assertEqual(row['prior'],row['current'])

    def test_corrupt_provenance_rejected(self):
        from tools.verify_recorded_replay import verify
        for field in ('knots_wire','controls_wire'):
            rows=self.rows();rows[0]['response'][field][0]+=1
            with self.assertRaises(ValueError):verify(rows)
        rows=self.rows();rows[0]['response']['request_sha256']='0'*64
        with self.assertRaises(ValueError):verify(rows)


if __name__=='__main__':unittest.main()
