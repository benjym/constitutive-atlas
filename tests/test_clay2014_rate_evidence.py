"""Portable replay of the original retained rate assertions; no binary."""
import json
from pathlib import Path
import unittest
from atlas.source_replay import registered
ROOT=Path(__file__).resolve().parents[1]
class RetainedRates(unittest.TestCase):
 def test_retained_source_raw_and_numerical_evidence(self):
  result=registered(ROOT,'catalogue/source-replays/clay2014-rate-v1/registry.json','clay2014-rate',timeout=120)
  report=json.loads(result['stdout'])
  self.assertEqual(report['original_groups'],1)
  self.assertTrue(report['original_assertions_passed'])
  self.assertTrue(report['original_wasm_audit_negative_retained'])
  self.assertFalse(report['compiled_execution'])
