"""Offline native/Wasm recorded evidence checks and browser target integrity."""
import copy
import gzip
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'catalogue/investigations/recorded-browser-v1'


def verify(report):
    if report.get('ok') is not True or len(report['pairs'])!=16:raise ValueError('incomplete parity capture')
    def compare(a,b):
        if type(b) in (float,int):
            if type(a) not in (float,int) or not math.isfinite(a) or abs(a-b)>1e-9*max(1,abs(b)):raise ValueError('numerical parity mismatch')
        elif isinstance(b,list):
            if not isinstance(a,list) or len(a)!=len(b):raise ValueError('shape mismatch')
            for x,y in zip(a,b):compare(x,y)
        elif isinstance(b,dict):
            if not isinstance(a,dict) or set(a)!=set(b):raise ValueError('metadata mismatch')
            for key in b:compare(a[key],b[key])
        elif type(a)!=type(b) or a!=b:raise ValueError('value mismatch')
    for row in report['pairs']:
        compare(row['wasm'],row['native'])
        for key in ['failed_knot','material_trials','attempted_substeps','finite_difference_probes']:
            if row['wasm'][key]!=row['native'][key]:raise ValueError('work/status counters differ')
    return len(report['pairs'])


class RecordedBrowserTests(unittest.TestCase):
    def report(self):return json.loads(gzip.decompress((EVIDENCE/'parity.json.gz').read_bytes()))
    def test_saved_native_wasm_parity(self):self.assertEqual(verify(self.report()),16)
    def test_corrupt_value_or_status_rejected(self):
        for key in ('state','strain'):
            r=self.report();r['pairs'][0]['wasm'][key][0]+=.01
            with self.assertRaises(ValueError):verify(r)
        r=self.report();r['pairs'][0]['wasm']['material_trials']+=1
        with self.assertRaises(ValueError):verify(r)
    def test_browser_export_retains_failure_prefix(self):
        d=json.loads((EVIDENCE/'browser-export.json').read_text());r=d['result']
        self.assertFalse(r['ok']);self.assertEqual(r['failed_knot'],2);self.assertEqual(len(r['points']),2)
        self.assertEqual(r['state'],r['points'][-1]['state']);self.assertEqual(r['strain'],r['points'][-1]['strain'])
        self.assertEqual(d['specification']['control_settings']['max_material_trials'],1)
    def test_static_recorded_targets_and_packaging(self):
        class Ids(HTMLParser):
            def __init__(self):super().__init__();self.ids=[]
            def handle_starttag(self,tag,attrs):self.ids.extend(v for k,v in attrs if k=='id')
        p=Ids();p.feed((ROOT/'web/index.html').read_text());self.assertEqual(len(p.ids),len(set(p.ids)))
        refs=set(re.findall(r"\$\('([^']+)'\)",(ROOT/'web/recorded-view.mjs').read_text()))
        self.assertFalse(refs-set(p.ids))
        builder=(ROOT/'tools/build_web.py').read_text()
        for name in ['recorded.mjs','recorded-view.mjs','recorded-example.json']:self.assertIn(name,builder)


if __name__=='__main__':unittest.main()
