"""Synthetic assessor self-tests. Fixtures are never candidate evidence."""
import copy
import math
import unittest
from assess import context, csv, inspect_path, inspect_probes, assess_records, assess_parity


def synthetic_path(request,ctx):
    # Admissible sample-and-hold history only to exercise the saved-output checker.
    # It is deliberately not asserted to solve any constitutive update.
    a=request['args'];knots=csv(a[5]);samples=ctx['references'][request['case']]['samples'];indices=request['sample_indices'];points=[];sample=0
    for i in range(request['knots_count']):
        if sample+1<len(indices) and i>=indices[sample+1]:sample+=1
        points.append({'coordinate':knots[7*i],'strain':knots[7*i+1:7*i+7],
                       'state':[float(x) for x in samples[sample]['state']]+[0.0],
                       'control_error':0.0,'diagnostics':{'iterations':0,'substeps':0,'rejected':0,'error':None,'increment_fractions':[]}})
    response={'ok':True,'api_version':'experimental-recorded-replay-0.2','catalogue_hash':ctx['catalogue_hash'],'model':a[0],'failed_knot':-1,
              'stress':{'source':'state','name':'sigma','measure':'cauchy','scope':'effective','tensor_representation':'mandel','sign':'compression_positive'},
              'points':points,'state':points[-1]['state'],'strain':points[-1]['strain'],'material_trials':0,'finite_difference_probes':0,'attempted_substeps':0}
    for key,offset in [('parameters',1),('initial',2),('initial_strain',3),('controls_wire',4),('knots_wire',5)]:response[key]=csv(a[offset])
    response['integration_settings']=dict(zip(['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'],csv(a[6])))
    response['integration_settings'].update(version='incremental-settings-0.1',norm='scaled_component_max')
    response['control_settings']=dict(zip(['control_tolerance','max_iterations','max_backtracks','max_material_trials','finite_difference_step'],csv(a[7])))
    return response


class AssessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx=context();cls.request=cls.ctx['requests'][2];cls.good=synthetic_path(cls.request,cls.ctx)

    def reject(self,mutate,gate):
        value=copy.deepcopy(self.good);mutate(value)
        with self.assertRaisesRegex(ValueError,gate):inspect_path(self.request,value,self.ctx)

    def test_positive_synthetic_path(self):
        self.assertEqual(inspect_path(self.request,self.good,self.ctx)['reference_components_checked'],450)

    def test_unsuccessful_path(self):self.reject(lambda v:v.update(ok=False),'unsuccessful')
    def test_truncated_history(self):self.reject(lambda v:v['points'].pop(),'incomplete point')
    def test_nonfinite_state(self):self.reject(lambda v:v['points'][4]['state'].__setitem__(2,math.nan),'finite numeric')
    def test_negative_gamma(self):self.reject(lambda v:v['points'][4]['state'].__setitem__(25,-1),'negative temporary')
    def test_anchor_changed(self):self.reject(lambda v:v['points'][4]['state'].__setitem__(19,1e-15),'anchor changed')
    def test_trace(self):self.reject(lambda v:v['points'][4]['state'].__setitem__(13,1e-8),'history trace')
    def test_yield(self):self.reject(lambda v:v['points'][4]['state'].__setitem__(0,1e8),'yield excess')
    def test_strain(self):self.reject(lambda v:v['points'][4]['strain'].__setitem__(0,1),'strain control')
    def test_coordinate(self):self.reject(lambda v:v['points'][4].update(coordinate=0),'coordinate')
    def test_control(self):self.reject(lambda v:v['points'][4].update(control_error=1e-5),'recorded control error')
    def test_identity(self):self.reject(lambda v:v.update(catalogue_hash='incorrect'),'identity')
    def test_parameters(self):self.reject(lambda v:v['parameters'].__setitem__(0,0),'echoed input')
    def test_settings(self):self.reject(lambda v:v['integration_settings'].update(max_iterations=450),'material policy')
    def test_entry_accuracy(self):self.reject(lambda v:v['points'][1]['state'].__setitem__(6,0.736),'first-yield accuracy')
    def test_fine_accuracy(self):self.reject(lambda v:v['points'][100]['state'].__setitem__(6,0.8),'fine trajectory accuracy')
    def test_endpoint(self):self.reject(lambda v:v.update(state=[0]*26),'endpoint mismatch')

    def test_probe_acceptance_and_rollback(self):
        records={}
        for p in self.ctx['probes']['probes']:
            records[p['id']]={'ok':False,'state':csv(p['args'][2])}
            records['recovery/'+p['id']]={'ok':True,'state':csv(self.ctx['probes']['recover_after_each']['args'][2])}
        self.assertEqual(inspect_probes(records,self.ctx),(24,[]))
        records['forced-plastic-failure']['state'][25]=0 # Must preserve nonzero incoming temporary value.
        self.assertIn('preservation',str(inspect_probes(records,self.ctx)[1]))
        records['zero-pressure']['ok']=True
        self.assertIn('probe result',str(inspect_probes(records,self.ctx)[1]))

    def test_missing_outputs_never_pass(self):
        result=assess_records({},self.ctx)
        self.assertFalse(result['research_qualification_pass']);self.assertEqual(result['successful_trajectory_checks'],0)
        self.assertTrue(any(x['gate']=='missing response' for x in result['failures']))

    def test_complete_synthetic_campaign_and_corruptions(self):
        records={r['id']:synthetic_path(r,self.ctx) for r in self.ctx['requests']}
        for p in self.ctx['probes']['probes']:
            records[p['id']]={'ok':False,'state':csv(p['args'][2])}
            records['recovery/'+p['id']]={'ok':True,'state':csv(self.ctx['probes']['recover_after_each']['args'][2])}
        parent=records['compression-e0.735-p100000/N1024']['points'][513]['state']
        for k in ['A','A-repeat','restart-A','zero']:records['transaction/'+k]={'ok':True,'state':list(parent)}
        records['transaction/B']={'ok':False,'state':list(parent)}
        result=assess_records(records,self.ctx);self.assertTrue(result['research_qualification_pass'],result['failures'])
        self.assertTrue(assess_parity(records,records,self.ctx)['pass'])
        # Corrupt zero-load persistent state and restart output separately.
        records['transaction/zero']['state'][6]+=1e-5
        records['transaction/restart-A']['state'][6]+=1e-5
        result=assess_records(records,self.ctx);self.assertFalse(result['transactions_pass'])
        records['unexpected']={'ok':True}
        self.assertTrue(any(x['gate']=='unexpected response' for x in assess_records(records,self.ctx)['failures']))
        # Force both refinement ratios above policy, while retaining fine accuracy.
        for n,error in [(256,.001),(512,.0009),(1024,.00085)]:
            r=next(r for r in self.ctx['requests'] if r['case']==self.request['case'] and r['plastic_steps']==n)
            records[r['id']]['points'][r['sample_indices'][2]]['state'][6]+=error
        self.assertTrue(any(x['gate']=='refinement ratio' for x in assess_records(records,self.ctx)['failures']))
        other=copy.deepcopy(records);other[self.request['id']]['points'][10]['state'][6]+=.01
        with self.assertRaisesRegex(ValueError,'parity'):assess_parity(records,other,self.ctx)


if __name__=='__main__':unittest.main()
