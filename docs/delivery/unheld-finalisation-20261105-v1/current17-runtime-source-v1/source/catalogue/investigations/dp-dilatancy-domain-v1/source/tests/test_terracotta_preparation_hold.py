"""Schedule and evidence-rejection contracts; synthetic responses are not solver evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from atlas.schedule import DEFAULTS,validate_schedule
ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'catalogue/investigations/terracotta-preparation-hold-v1'
REFERENCE=ROOT/'docs/ingestion/terracotta-2024/preparation-hold-reference-v1/refinement-v2/references.json'

def module(name):
 spec=importlib.util.spec_from_file_location(name,STUDY/(name+'.py'));result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
assemble=module('assemble')
# The retained assessor imports only its adjacent request assembler.
previous=sys.modules.get('assemble');sys.modules['assemble']=assemble
try:assessor=module('assess')
finally:
 if previous is None:sys.modules.pop('assemble',None)
 else:sys.modules['assemble']=previous

class PreparationHoldContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.reference=json.loads(REFERENCE.read_text());cls.model=json.loads((ROOT/'models/research/terracotta-2024-fig1.json').read_text());cls.policy=json.loads((STUDY/'policy.json').read_text())
 def records(self):
  records=assemble.requests(self.reference,self.model)
  for record in records:
   case=next(c for c in self.reference['cases'] if c['id']==record['case']);points=[]
   for source in case['points']:
    p,q=source['pressure'],source['signed_q'];segment=1 if source['phase']=='hold' else (0 if source['time']>0 else -1)
    point={'time':source['time'],'segment':segment,'side':'right' if source['side']=='right' else 'left',
     'state':source['state'][:],'strain':source['strain'][:],'strain_rate':source['rate'][:],
     'observables':[p+2*q/3,p-q/3,p-q/3,0,0,0,p,q,source['elastic_pressure'],source['elastic_q'],0,0,0],
     'iterations':0,'substeps':0,'rejected':0,'temporal_error_norm':0,'nonlinear_residual_norm':0}
    if segment==1 and point['side']=='right':point['strain_rate']=[None,None,None,0,0,0]
    points.append(point)
   entry=copy.deepcopy(points[0]);entry.update(segment=0,side='right');points.insert(1,entry)
   record['response']={**copy.deepcopy(record['request']),'ok':True,'catalogue_hash':'a'*64,'points':points,'solver':{**DEFAULTS,**record['request']['solver'],'maximum_depth':40}}
  return records
 def check(self,records):return assessor.assess(records,self.reference,self.model,self.policy,'a'*64)
 def test_requests_are_one_full_schedule_and_validate(self):
  records=assemble.requests(self.reference,self.model);self.assertEqual(len(records),9)
  for row in records:
   request=row['request'];validate_schedule(request)
   self.assertEqual(request['parameters'],[p['default'] for p in self.model['parameters'].values()])
   self.assertEqual([s['duration'] for s in request['segments']],[10,20])
   self.assertEqual(request['segments'][1]['controls'][:3],[{'quantity':'stress','kind':'hold'}]*3)
 def test_perfect_reference_transport_is_accepted(self):self.assertEqual(len(self.check(self.records())),9)
 def test_replacing_hold_entry_state_is_rejected(self):
  records=self.records();records[0]['response']['points'][12]['state'][0]+=1e-10
  with self.assertRaises(AssertionError):self.check(records)
 def test_resetting_hold_clock_is_rejected(self):
  records=self.records();records[0]['response']['points'][12]['time']=0
  with self.assertRaises(AssertionError):self.check(records)
 def test_moving_capture_target_is_rejected(self):
  records=self.records();records[0]['response']['points'][12]['observables'][6]+=1
  with self.assertRaises(AssertionError):self.check(records)
 def test_missing_phase_or_request_is_rejected(self):
  records=self.records();records.pop()
  with self.assertRaises(AssertionError):self.check(records)

if __name__=='__main__':unittest.main()
