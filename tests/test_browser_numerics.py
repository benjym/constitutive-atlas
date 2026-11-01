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
  # These lookups are optional: a navigation variant, a model-dependent
  # void-ratio field, and the dynamically created public-profile link.
  self.assertEqual(references-set(parser.ids),{'breadcrumb','state-e','model-profile-link'})
  self.assertIn('result-note',parser.ids)
 def test_dynamic_profile_link_is_created_and_lookups_are_optional(self):
  source=(ROOT/'web/app.js').read_text()
  self.assertRegex(source,r"link\.id='model-profile-link';link\.href=catalogueModelHash\(")
  lookups=re.findall(r"\$\('model-profile-link'\)([^;]*);",source)
  self.assertTrue(lookups)
  self.assertTrue(all(tail=='?.remove()' for tail in lookups))
if __name__=='__main__':unittest.main()
