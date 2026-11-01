"""Saved failing numerical gate is immutable and sensitive to new regressions."""
from tests.historical_generation import generate as historical_generate
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,tempfile,unittest
from atlas.model import ROOT
from atlas.compiler import generate
P=ROOT/'catalogue/investigations/tresca-rounded-backends-v1'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class TrescaBackendEvidenceTests(unittest.TestCase):
    def test_saved_gate_reproduces_failures_without_execution(self):
        result=module('tresca_verify',P/'verify.py').verify(P,ROOT)
        self.assertFalse(result['overall_pass'])
        for b in ('native','wasm'):
            self.assertEqual(len(result[b]['failures']),5);self.assertEqual(len(result[b]['coverage_gaps']),2)
            self.assertEqual(result[b]['requests'],219)
    def test_assessor_catches_additional_corruption(self):
        m=module('tresca_assess',P/'assess.py');requests=json.loads((P/'requests.json').read_text())['requests'];ref=json.loads(gzip.decompress((ROOT/'docs/reviews/tresca-rounded-reference-v1/reference-p280.json.gz').read_bytes()));policy=json.loads((P/'policy.json').read_text());base=[json.loads(v)for v in (P/'native-responses.jsonl').read_text().splitlines()]
        for kind in ('value','derivative','rollback','recovery'):
            rows=copy.deepcopy(base)
            if kind=='value':rows[0]['values'][0]+=1;expected='value-accuracy'
            elif kind=='derivative':rows[1]['derivatives'][0][37]+=1;expected='derivative-accuracy'
            elif kind=='rollback':next(v for v in rows if v['mode']=='transaction')['returned_parent']=False;expected='tentative-rollback-transaction'
            else:rows[0]['baseline_recovery']=False;expected='same-instance-recovery'
            with self.subTest(kind=kind):
                result=m.assess(rows,requests,ref,policy);self.assertGreater(len(result['failures']),5);self.assertIn(expected,[v['kind']for v in result['failures']])
    def test_normal_generation_and_instrumentation_only(self):
        with tempfile.TemporaryDirectory()as d:
            historical_generate(d,[P/'frozen/model.json'],'tresca-rounded-backends-v1')
            for n in ('models.hpp','models.json'):self.assertEqual((Path(d)/n).read_bytes(),(P/'generated-original'/n).read_bytes())
        modified=(P/'generated/models.hpp').read_text();self.assertEqual(modified.replace('\ninline int study_branch=-1;','').replace('study_branch=int(value(branch));\n',''),(P/'generated-original/models.hpp').read_text())
        original=json.loads((ROOT/'docs/reviews/tresca-declarative-v1/model.json').read_text());self.assertEqual(original,json.loads((P/'frozen/model.json').read_text()))
        self.assertFalse((ROOT/'models'/('tresca-associated-perfect-bk2022v1-be-research.json')).exists())
    def test_transport_tail_has_exact_frozen_remaining_requests(self):
        wire=gzip.decompress((P/'requests.txt.gz').read_bytes()).splitlines(True);freeze=json.loads((P/'wasm-transport-resume-freeze.json').read_text());tail=b''.join(wire[64:]);self.assertEqual(hashlib.sha256(tail).hexdigest(),freeze['remaining_input_sha256']);self.assertEqual(len(wire),219)
        a=[json.loads(v)['id']for v in (P/'wasm-prefix-responses.jsonl').read_text().splitlines()];b=[json.loads(v)['id']for v in (P/'wasm-tail-responses.jsonl').read_text().splitlines()];self.assertEqual(len(set(a+b)),219)
