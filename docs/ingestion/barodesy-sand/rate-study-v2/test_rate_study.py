import copy,json,math,os,unittest
from fractions import Fraction
from pathlib import Path
import check,reference,support
HERE=Path(__file__).resolve().parent


def repository():
    configured=os.environ.get('ATLAS_REVIEW_REPO')
    return Path(configured)if configured else next((p for p in HERE.parents if(p/'atlas/model.py').is_file()),None)


class RevisedRates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.inputs=reference.read_inputs();cls.fresh=reference.build_reference();cls.by={r['id']:r for r in cls.fresh['records']}

    def test_full_fresh_replay_and_corruption(self):
        self.assertEqual(check.checked_reference(),self.fresh)
        for f in ('number','precision','domain','bool'):
            c=copy.deepcopy(self.fresh)
            if f=='number':c['records'][0]['oracle120']['values'][0]+=1
            if f=='precision':c['records'][0]['oracle80']['decimal_values'][0]='0'
            if f=='domain':c['invalid'][-1]['ideal_source']['accepted']=False
            if f=='bool':c['invalid'][0]['operational_rejected']=1
            with self.assertRaises(ValueError):check.checked_reference(c)

    def test_frozen_v1_requests_and_equations_preserved(self):
        repo=repository();self.assertIsNotNone(repo,'set ATLAS_REVIEW_REPO for staged replay')
        old=repo/'docs/ingestion/barodesy-sand/rate-study-v1'
        prior=json.loads((old/'inputs.json').read_text())
        for key in ('valid','invalid','rotations','calibration','source_pdf_sha256'):self.assertEqual(self.inputs[key],prior[key])
        a=json.loads((old/'model-draft.json').read_text());b=json.loads((HERE/'model-draft.json').read_text())
        for key in ('parameters','state','derived','equations','domain','sources','integration'):self.assertEqual(a[key],b[key])
        oldref={c['id']:c for c in json.loads((old/'reference.json').read_text())['records']}
        for c in prior['valid']:self.assertEqual(self.by[c['id']]['oracle120']['values'],oldref[c['id']]['oracle120']['values'])

    def test_exact_void_all38_actual_binary64(self):
        for c in self.inputs['valid']+self.inputs['additional_operational_valid']:
            _,q=reference.exact_volume(c);want=float(q);got=self.by[c['id']]['oracle120']
            self.assertEqual(got['values'][6],want)
            self.assertEqual(Fraction(int(got['void_exact_fraction']['numerator']),int(got['void_exact_fraction']['denominator'])),q)
            self.assertEqual(Fraction(reference.exact_decimal(q)),q)

    def test_cancellation_counterexample_resolved_not_relabelled_zero(self):
        c=self.inputs['additional_operational_valid'][0];z=self.by[c['id']]
        support.validate(c)
        self.assertEqual(z['oracle80']['values'][6],-1.7500000000000002e-130);self.assertEqual(z['oracle120']['values'][6],z['oracle80']['values'][6])
        self.assertEqual(reference.ideal_source_rate(c,200)['values'][6],z['oracle120']['values'][6])
        actual=check.draft_rate(c);self.assertEqual(actual[6],z['oracle120']['values'][6]);check.assess_values(c,actual,z['oracle120']['values'])
        bad=list(actual);bad[6]=0
        with self.assertRaises(ValueError):check.assess_values(c,bad,z['oracle120']['values'])

    def test_exact_volume_extreme_cancellation_and_ties(self):
        c=copy.deepcopy(self.inputs['valid'][0])
        for v in (1e-300,math.ulp(0.),-1e-300):
            c['loading']=[500.,v,-500.,0.,0.,0.];_,q=reference.exact_volume(c)
            self.assertEqual(q,-Fraction(7,4)*Fraction.from_float(v))
            self.assertEqual(Fraction(reference.exact_decimal(q)),q)
        c['state'][-1]=.5;c['loading']=[500.,math.ulp(0.),-500.,0.,0.,0.]
        self.assertEqual(float(reference.exact_volume(c)[1]),-2*math.ulp(0.))  # -1.5subnormal tie -> even
        c['loading']=[1.,-1.,0.,0.,0.,0.];self.assertEqual(reference.exact_volume(c)[1],0)

    def test_ideal_only_density_witness_is_operational_rejection(self):
        c=self.inputs['additional_operational_invalid'][0];ideal=reference.ideal_source_rate(c,120)
        self.assertGreater(__import__('decimal').Decimal(ideal['ideal_ec_gap_decimal']),0)
        self.assertEqual(ideal['ec'],c['parameters']['emin'])
        with self.assertRaises(ValueError):support.validate(c)
        with self.assertRaises(ValueError):check.draft_rate(c)

    def test_numerical_invalids_are_not_physical_source_rejections(self):
        by={r['id']:r for r in self.fresh['invalid']}
        for name in ('tiny-stress','tiny-loading','above-density','excessive-loading','audit-rounded-critical-density'):
            self.assertTrue(by[name]['operational_rejected']);self.assertTrue(by[name]['ideal_source']['accepted'])
        self.assertEqual(len(self.fresh['invalid']),20)

    def test_all38_rates_and20_operational_rejections(self):
        result=check.run();self.assertEqual(len(result['records']),38);self.assertEqual(len(result['invalid']),20)
        self.assertFalse(result['compiled_execution']);self.assertFalse(result['admission'])

    def test_strict_types_domains_and_nonmutation(self):
        good=copy.deepcopy(self.inputs['valid'][0]);saved=copy.deepcopy(good)
        check.draft_rate(good);self.assertEqual(good,saved)
        for bad in self.inputs['invalid']+self.inputs['additional_operational_invalid']:
            keep=copy.deepcopy(bad)
            with self.assertRaises((ValueError,ArithmeticError)):support.validate(bad)
            with self.assertRaises((ValueError,ArithmeticError)):check.draft_rate(bad)
            self.assertEqual(bad,keep)

    def test_source_diagonal_action_and_rotation(self):
        # Independent scalar source Eq9/Eq31 evaluation; no matrix expm algorithm.
        c=copy.deepcopy(self.inputs['valid'][0]);c['state']=[120000.,90000.,70000.,0,0,0,.75];c['loading']=[.001,-.0003,.0002,0,0,0]
        p=c['parameters'];sig=c['state'][:3];d=[-x for x in c['loading'][:3]];dn=math.hypot(*d);sn=math.hypot(*sig);u=[x/dn for x in d];delta=math.fsum(u)
        R=[-math.exp(p['c1']*math.exp(p['c2']*delta)*x)for x in u];rn=math.hypot(*R)
        B=(p['ec0']-p['emin'])/(p['ec0']+1)*math.exp(-(1+p['emin'])/p['c5']*math.log1p(p['c5']*sn/p['c4']));ec=(p['emin']+B)/(1-B);h=-(p['c4']+p['c5']*sn)/(.75-p['emin'])
        want=[-h*((delta+p['c3']*ec)*x/rn-p['c3']*.75*(-y/sn))*dn for x,y in zip(R,sig)]
        got=check.draft_rate(c);self.assertLess(max(abs(x-y)for x,y in zip(got[:3],want))/math.hypot(*want),2e-12)
        from atlas.model import load
        model=load(HERE/'model-draft.json');self.assertEqual(model['integration'],'rate');self.assertNotIn('increment_reset',model)
        # Frozen rotations remain independently checked through all38 source comparisons.
        for name in self.inputs['rotations']:self.assertIn(name,self.by)

    def test_expm_and_compiled_proposal_counts(self):
        self.assertLess(2*math.exp(1.5*math.sqrt(3)),64)
        p=json.loads((HERE/'protocol.json').read_text());m=p['next_compiled_matrix']
        self.assertEqual(m['persistent_raw_rows_per_backend'],1+38+16*2)
        self.assertEqual(len(m['numeric_invalid_ids']),16);self.assertEqual(len(m['python_only_invalid_ids']),4)


if __name__=='__main__':unittest.main()
