"""Opt-in bounded restart contract, retained regression and serial native checks."""
import copy
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from atlas.dsl import ValidationError
from atlas.model import ROOT, all_models
from atlas.refinement import validate_study
from atlas.recorded import execute_recorded,validate_recorded_run,recorded_wire,RESTART_DEFAULTS
from tools.diagnose_dp_recorded_apex import scalar_return
from tests.test_recorded_api import specimen


def source_levels():
    with gzip.open(ROOT/'catalogue/investigations/recorded-refinement-v1/plastic-report.json.gz','rt') as f:report=json.load(f)
    return next(c['levels'] for c in report['cases'] if c['model']=='drucker-prager')


def verify_dp_response(s,r):
    if r['restart_settings']!=RESTART_DEFAULTS|s['restart_settings']:raise ValueError('restart policy changed')
    d=r['restart_diagnostics']
    if not 0<=d['accepted']<=d['searches'] or not 0<=d['material_trials']<=r['material_trials']:raise ValueError('restart accounting')
    if not r['ok']:
        if len(r['points'])!=r['failed_knot'] or r['state']!=r['points'][-1]['state'] or r['strain']!=r['points'][-1]['strain']:raise ValueError('failed prefix')
    elif len(r['points'])!=len(s['path']['knots']):raise ValueError('incomplete success')
    _,E,nu,M,Md,c=r['parameters'];K=E/(3*(1-2*nu));G=E/(2*(1+nu))
    for i,(pt,knot) in enumerate(zip(r['points'],s['path']['knots'])):
        if pt['coordinate']!=knot['coordinate']:raise ValueError('order changed')
        if len(pt['state'])!=8 or len(pt['strain'])!=6 or any(not math.isfinite(v) for v in pt['state']+pt['strain']):raise ValueError('nonfinite/malformed state')
        for row,target in zip(s['path']['controls'],knot['targets']):
            scale=max(map(abs,row['coefficients']));v=pt['state'][:6] if row['kind']=='stress' else pt['strain']
            err=abs(sum(a/scale*b for a,b in zip(row['coefficients'],v))-target/scale)
            if err>(1e-4 if row['kind']=='stress' else 1e-10):raise ValueError('control violation')
        if i:
            old=r['points'][i-1]
            if knot['targets']==s['path']['knots'][i-1]['targets']:
                if pt['state']!=old['state']:raise ValueError('duplicate mutated history')
                continue
            de=[a-b for a,b in zip(pt['strain'],old['strain'])]
            expected=scalar_return(old['state'],de,K,G,M,Md,c)
            if max(abs(a-b) for a,b in zip(expected['stress'],pt['state']))>1e-4:raise ValueError('independent scalar return disagrees')
            if abs(pt['state'][6]-((1+old['state'][6])*math.exp(-sum(de[:3]))-1))>1e-10:raise ValueError('density/history leak')
    return True


class RestartContractTests(unittest.TestCase):
    def test_explicit_optional_settings_preserved(self):
        s=specimen();s['restart_settings']={};before=copy.deepcopy(s)
        self.assertIs(validate_recorded_run(s),s);self.assertEqual(s,before)
        s['restart_settings']={'max_restarts':0};validate_recorded_run(s)
        study=json.loads((ROOT/'benchmarks/recorded-plastic-path-density.json').read_text())
        study['cases'][0]['specification']['restart_settings']={}
        self.assertIs(validate_study(study),study)

    def test_closed_numeric_bounds(self):
        for value in [None,[],{'unknown':1},{'max_restarts':-1},{'max_restarts':17},{'max_restarts':1.5},
                      {'restart_levels':0},{'restart_levels':17},{'restart_step':0},{'restart_step':.02},{'restart_step':float('nan')}]:
            s=specimen();s['restart_settings']=value
            with self.assertRaises(ValidationError):validate_recorded_run(s)

    def test_response_policy_and_accounting_rejected(self):
        with gzip.open(ROOT/'catalogue/investigations/recorded-restarts-v1/responses.json.gz','rt') as f:rows=json.load(f)
        enabled=next(row for row in rows if 'restart_settings' in row['request'] and row['response']['ok'])
        disabled=next(row for row in rows if row['request'].get('restart_settings',{}).get('max_restarts')==0)
        legacy=next(row for row in rows if 'restart_settings' not in row['request'])
        corrupt=[]
        row=copy.deepcopy(disabled);row['response']['restart_diagnostics']['searches']=1;corrupt.append(row)
        row=copy.deepcopy(legacy);row['response']['restart_diagnostics']=dict(searches=0,material_trials=0,accepted=0);corrupt.append(row)
        row=copy.deepcopy(enabled);del row['response']['material_trials'];corrupt.append(row)
        row=copy.deepcopy(enabled);row['response']['material_trials']=float('nan');corrupt.append(row)
        for row in corrupt:
            proc=subprocess.CompletedProcess([],0 if row['response']['ok'] else 1,json.dumps(row['response']),'')
            with patch('subprocess.run',return_value=proc),self.assertRaises(RuntimeError):execute_recorded(row['request'],'unused')



@unittest.skipUnless(os.environ.get('ATLAS_RECORDED_SOLVER'),'set ATLAS_RECORDED_SOLVER to existing binary')
class RestartNativeTests(unittest.TestCase):
    records=[]
    @classmethod
    def tearDownClass(cls):
        if path:=os.environ.get('ATLAS_RESTART_CAPTURE'):
            Path(path).write_bytes(gzip.compress(json.dumps(cls.records,allow_nan=False).encode(),mtime=0))

    def run_spec(self,s):
        r=execute_recorded(s,os.environ['ATLAS_RECORDED_SOLVER'])
        self.records.append(dict(request=copy.deepcopy(s),response=copy.deepcopy(r)))
        return r

    def assert_legacy(self,actual,expected):
        if os.environ.get('ATLAS_EXACT_RECORDED_BASELINE')=='1':self.assertEqual(actual,expected);return
        # Work partitions/iteration counts can depend on compiler floating point.
        # Retained local evidence below additionally proves bitwise JSON equality.
        a,b=copy.deepcopy(actual),copy.deepcopy(expected)
        # A catalogue addition changes its identity, not the legacy response law.
        # Validate the current identity independently before comparing old behavior.
        current_models=all_models()
        current_hash=hashlib.sha256(json.dumps(current_models,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(a.pop('catalogue_hash'),current_hash)
        self.assertEqual(len(b.pop('catalogue_hash')),64)
        for r in (a,b):
            for key in ('material_trials','attempted_substeps','finite_difference_probes'):r.pop(key)
            for point in r['points']:point.pop('diagnostics')
        def compare(x,y):
            if type(x) is float or type(y) is float:
                self.assertIn(type(x),(int,float));self.assertIn(type(y),(int,float))
                self.assertTrue(math.isfinite(x));self.assertLessEqual(abs(x-y),1e-9*max(1,abs(y)))
            elif isinstance(y,list):
                self.assertEqual(len(x),len(y))
                for v,w in zip(x,y):compare(v,w)
            elif isinstance(y,dict):
                self.assertEqual(set(x),set(y))
                for key in y:compare(x[key],y[key])
            else:self.assertEqual(x,y)
        compare(a,b)

    def test_disabled_legacy_responses_exact(self):
        with gzip.open(ROOT/'catalogue/investigations/recorded-replay-api-v1/responses.json.gz','rt') as f:retained=json.load(f)
        for row in retained:self.assert_legacy(self.run_spec(row['request']),row['response'])
        for level in source_levels()[:3]:
            old=level['response'];s=copy.deepcopy(old['specification'])
            r=self.run_spec(s);self.assert_legacy(r,old)
            s['restart_settings']={'max_restarts':0};disabled=self.run_spec(s)
            self.assertFalse(disabled['ok']);self.assertEqual(disabled['state'],r['state'])
            self.assertEqual(disabled['material_trials'],r['material_trials'])
            self.assertEqual(disabled['restart_diagnostics'],dict(searches=0,material_trials=0,accepted=0))

    def test_three_coarse_paths_and_independent_scalar_return(self):
        for level in source_levels()[:3]:
            s=copy.deepcopy(level['response']['specification']);s['restart_settings']={}
            r=self.run_spec(s);self.assertTrue(r['ok'],r['message']);self.assertTrue(verify_dp_response(s,r))
            self.assertGreater(r['restart_diagnostics']['accepted'],0)
            for point in r['points']:self.assertLess(abs(point['strain'][1]-point['strain'][2]),1e-10)

    def test_search_budget_and_late_prefix(self):
        s=copy.deepcopy(source_levels()[0]['response']['specification']);s['restart_settings']={'restart_levels':1}
        failed=self.run_spec(s);self.assertFalse(failed['ok']);self.assertEqual(failed['failed_knot'],2)
        self.assertEqual(failed['restart_diagnostics'],dict(searches=1,material_trials=6,accepted=0))
        self.assertTrue(verify_dp_response(s,failed))
        s['restart_settings']={};s['control_settings']={'max_material_trials':failed['material_trials']-4}
        capped=self.run_spec(s);self.assertFalse(capped['ok']);self.assertEqual(capped['material_trials'],s['control_settings']['max_material_trials'])
        self.assertEqual(capped['state'],failed['state']);self.assertEqual(capped['strain'],failed['strain'])
        self.assertTrue(verify_dp_response(s,capped))

    def test_control_rows_scaling_and_permutation(self):
        s=copy.deepcopy(source_levels()[0]['response']['specification']);s['restart_settings']={}
        expected=self.run_spec(s)
        order=[2,4,0,1,5,3];scales=[-1e-3,1e3,2.,-3.,.125,4.]
        s['path']['controls']=[dict(kind=s['path']['controls'][i]['kind'],coefficients=[v*scale for v in s['path']['controls'][i]['coefficients']]) for i,scale in zip(order,scales)]
        for knot in s['path']['knots']:knot['targets']=[knot['targets'][i]*scale for i,scale in zip(order,scales)]
        actual=self.run_spec(s);self.assertTrue(actual['ok']);self.assertTrue(verify_dp_response(s,actual))
        for a,b in zip(actual['points'],expected['points']):
            for x,y in zip(a['state'],b['state']):self.assertAlmostEqual(x,y,places=7)
            for x,y in zip(a['strain'],b['strain']):self.assertAlmostEqual(x,y,places=12)

    def test_invalid_wire_and_mode(self):
        solver=os.environ['ATLAS_RECORDED_SOLVER']
        for args in [['--mode','integrate','--model','linear-elastic','--strain','0,0,0,0,0,0','--recorded-restarts','1,.001,8']]:
            p=subprocess.run([solver,*args],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,1);self.assertFalse(json.loads(p.stdout)['ok'])
        with tempfile.TemporaryDirectory() as directory:
            controls,knots=recorded_wire(specimen());c=Path(directory)/'controls';k=Path(directory)/'knots'
            c.write_text(','.join(map(str,controls)));k.write_text(','.join(map(str,knots)))
            base=[solver,'--mode','recorded','--model','linear-elastic','--initial-strain','0,0,0,0,0,0','--recorded-controls-file',str(c),'--recorded-knots-file',str(k)]
            for wire in ['', '1', '1,0,8', '1,.001,1.5', '17,.001,8', '1,nan,8']:
                proc=subprocess.run([*base,'--recorded-restarts',wire],capture_output=True,text=True,timeout=10)
                self.assertEqual(proc.returncode,1);self.assertFalse(json.loads(proc.stdout)['ok'])


class RetainedRestartTests(unittest.TestCase):
    def test_retained_provenance_and_scalar_checks(self):
        import hashlib
        with gzip.open(ROOT/'catalogue/investigations/recorded-restarts-v1/responses.json.gz','rt') as f:rows=json.load(f)
        self.assertEqual(len(rows),29)
        with gzip.open(ROOT/'catalogue/investigations/recorded-replay-api-v1/responses.json.gz','rt') as f:legacy=json.load(f)
        by_hash={row['response']['request_sha256']:row for row in rows}
        for row in legacy:self.assertEqual(by_hash[row['response']['request_sha256']],row)
        enabled=[]
        for row in rows:
            s,r=row['request'],row['response'];validate_recorded_run(s)
            canonical=json.dumps(s,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
            self.assertEqual(r['specification'],s);self.assertEqual(r['request_sha256'],hashlib.sha256(canonical).hexdigest())
            c,k=recorded_wire(s);self.assertEqual(r['controls_wire'],c);self.assertEqual(r['knots_wire'],k)
            if 'restart_settings' in s:enabled.append(row);self.assertTrue(verify_dp_response(s,r))
        self.assertEqual(len(enabled),10);self.assertEqual(sum(row['response']['ok'] for row in enabled),5)
        changed=copy.deepcopy(next(row for row in enabled if row['response']['ok']))
        changed['response']['points'][1]['state'][6]+=.1
        with self.assertRaises(ValueError):verify_dp_response(changed['request'],changed['response'])

if __name__=='__main__':unittest.main()
