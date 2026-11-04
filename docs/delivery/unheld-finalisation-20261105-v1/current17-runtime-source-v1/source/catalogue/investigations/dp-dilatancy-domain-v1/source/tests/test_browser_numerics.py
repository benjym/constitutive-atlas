"""Prevent missing static browser controls from breaking response handling."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Ids(HTMLParser):
 def __init__(self):super().__init__();self.ids=[]
 def handle_starttag(self,tag,attrs):self.ids.extend(v for k,v in attrs if k=='id')
class BrowserNumericsMarkupTests(unittest.TestCase):
 def test_static_javascript_targets_exist(self):
  parser=Ids();parser.feed((ROOT/'web/index.html').read_text())
  self.assertEqual(len(parser.ids),len(set(parser.ids)))
  references=set(re.findall(r"\$\('([^']+)'\)",(ROOT/'web/app.js').read_text()))
  # These two lookups are explicitly optional: a navigation variant and a
  # dynamically created field present only in models with void ratio.
  self.assertEqual(references-set(parser.ids),{'breadcrumb','state-e'})
  self.assertIn('result-note',parser.ids)
if __name__=='__main__':unittest.main()
