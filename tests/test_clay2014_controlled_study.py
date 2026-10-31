"""Assessor/transport corruption tests with synthetic analytical responses only."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import clay2014_controlled_study as study


class ControlledStudy(unittest.TestCase):
    def fixture(self, folder, backend='native', perturb=0., fractions=None):
        protocol,_=study.frozen_inputs()
        historical=study.read(study.ROOT/study.reference.HISTORICAL)
        template=historical['records'][0]['calls'][0]['response']
        rows=[]
        def append(request,response,descriptor=False):
            raw=json.dumps(response,allow_nan=False)
            if backend=='native':
                rows.append({'backend':backend,'mode':'persistent_stream','request_line':study.transport.stream_line(request),'request':request,'stdout':raw+'\n'})
            else:
                args=[] if descriptor else [request['model']]+[study.transport.csv(request[k]) for k in ('parameters','initial','strain','settings')]
                rows.append({'backend':backend,'name':'atlas_describe' if descriptor else 'atlas_integrate_with_settings',
                             'types':[] if descriptor else ['string']*5,'args':args,'request':request,'raw':raw})
        append({'mode':'describe'},historical['runtime_descriptor'],True)
        for group in protocol['groups']:
            parent=protocol['input']['initial'].copy()
            for point in group['points']:
                request=study.request(protocol,point,parent)
                response=copy.deepcopy(template)
                response.update({k:copy.deepcopy(request[k]) for k in ('model','parameters','initial','strain')})
                response['integration_settings']=study.transport.settings(request)
                response['state']=point['target'].copy()
                response['state'][:3]=[x+perturb for x in response['state'][:3]]
                fs=[.5,.5] if fractions is None else fractions
                response['diagnostics']={'iterations':0,'substeps':len(fs),'rejected':0,'increment_fractions':fs}
                response['catalogue_hash']=historical['catalogue_hash']
                append(request,response);parent=response['state'].copy()
        path=Path(folder)/f'{backend}.jsonl'
        path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        receipt={'version':study.VERSION,'backend':backend,'protocol_sha256':study.sha(study.ROOT/study.PROTOCOL),
                 'collection_freeze_sha256':study.sha(study.ROOT/study.FREEZE),
                 'artifacts':{p:pin for p,pin in study.ARTIFACTS.items() if (p.startswith('build-wasm/') if backend=='wasm' else p.startswith('build/'))},
                 'completed':True,'calls':315,'exit_status':0,'stderr':'','trailing_stdout':'','transport_sha256':study.sha(path)}
        return receipt,path,rows

    def test_exact_analytical_synthetic_matrix_and_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            n,p,_=self.fixture(tmp);native=study.audit(n,p)
            w,q,_=self.fixture(tmp,'wasm');wasm=study.audit(w,q)
            self.assertEqual(native['outcome'],'passed');self.assertEqual(wasm['outcome'],'passed')
            self.assertEqual(len(native['endpoint_comparisons']),18)
            self.assertEqual(study.parity(native,wasm)['maximum_state_and_parent_scaled_difference'],0.)

    def test_numerical_failure_is_retained_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt,path,_=self.fixture(tmp,perturb=100.)
            result=study.audit(receipt,path)
            self.assertEqual(result['outcome'],'failed')
            self.assertTrue(any('accuracy' in f for f in result['failures']))
            self.assertTrue(any('contraction' in f for f in result['failures']))
            self.assertTrue(all(x is False for x in result['claims'].values()))

    def test_wrong_effective_mesh_is_retained_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt,path,_=self.fixture(tmp,fractions=[.25]*4)
            result=study.audit(receipt,path)
            self.assertEqual(result['outcome'],'failed')
            self.assertEqual(len(result['failures']),315)

    def test_rebound_raw_corruption_is_rejected(self):
        for kind in ('parent','control','missing','duplicate','boolean','descriptor','echo'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                receipt,path,rows=self.fixture(tmp)
                if kind=='parent':rows[2]['request']['initial'][0]+=1
                if kind=='control':rows[1]['request']['strain'][0]*=2
                if kind=='missing':rows.pop()
                if kind=='duplicate':rows[2]=copy.deepcopy(rows[1])
                if kind=='boolean':rows[1]['request']['settings'][2]=True
                if kind in ('descriptor','echo'):
                    i=0 if kind=='descriptor' else 1
                    response=json.loads(rows[i]['stdout'])
                    if kind=='descriptor':response['sha256']='0'*64
                    else:response['initial'][0]+=1
                    rows[i]['stdout']=json.dumps(response)
                path.write_text(''.join(json.dumps(row)+'\n' for row in rows));receipt['transport_sha256']=study.sha(path)
                with self.assertRaises(ValueError):study.audit(receipt,path)

    def test_receipt_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt,path,_=self.fixture(tmp)
            for key,value in [('calls',True),('calls',314),('completed',1),('exit_status',False),('transport_sha256','0'*64),('protocol_sha256','0'*64),('collection_freeze_sha256','0'*64),('artifacts',{})]:
                with self.subTest(key=key,value=value):
                    r=copy.deepcopy(receipt);r[key]=value
                    with self.assertRaises(ValueError):study.audit(r,path)


if __name__=='__main__':unittest.main()
