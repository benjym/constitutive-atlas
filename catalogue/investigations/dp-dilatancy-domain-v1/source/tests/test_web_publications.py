"""Static evidence assets must retain canonical records without a solver build."""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

from atlas.model import ROOT
from tools.build_publications import bundle


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and 'src' in attrs:
            self.files.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.files.append(attrs['href'])


class PublicationAssetTests(unittest.TestCase):
    def test_project_path_bundle_preserves_sources_and_loads_no_solver(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / 'constitutive-atlas'
            bundle(destination)
            before = {str(p.relative_to(destination)): p.read_bytes() for p in destination.rglob('*') if p.is_file()}
            bundle(destination)
            after = {str(p.relative_to(destination)): p.read_bytes() for p in destination.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            for source, target in [('catalogue/publications.json', 'publications.json'),
                                   ('catalogue/manifest.json', 'catalogue.json'),
                                   ('schemas/publications.schema.json', 'schemas/publications.schema.json')]:
                self.assertEqual((ROOT / source).read_bytes(), (destination / target).read_bytes())
            parser = Assets()
            parser.feed((destination / 'publications.html').read_text())
            self.assertCountEqual(parser.files, ['style.css', 'publications.mjs'])
            for path in parser.files:
                self.assertFalse(path.startswith('/'))
                self.assertTrue((destination / path).is_file())
            self.assertEqual(set(before), {'publications.html', 'publications.mjs', 'style.css',
                                           'publications.json', 'catalogue.json', 'schemas/publications.schema.json'})
