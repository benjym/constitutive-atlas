"""Classic publication identities and exported provenance, without material runs."""
from contextlib import closing
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from atlas.model import ROOT
from atlas.research import load_publications, export_database
from tools.build_publications import bundle

HERE = ROOT/'docs/ingestion/classic-publications-v1'

class ClassicPublicationTests(unittest.TestCase):
    def test_additions_preserve_exact_previous_graph_records(self):
        receipt=json.loads((HERE/'receipt.json').read_bytes())
        source=receipt['previous_graph']; content=(ROOT/source['path']).read_bytes()
        self.assertEqual(hashlib.sha256(content).hexdigest(),source['sha256'])
        old=json.loads(content); graph=load_publications()
        self.assertEqual(graph['publications'][:len(old['publications'])],old['publications'])
        self.assertEqual(graph['relations'][:len(old['relations'])],old['relations'])
        # Later independently sourced additions must not invalidate this historical prefix.
        self.assertGreaterEqual(len(graph['publications']),len(old['publications'])+3)
        self.assertGreaterEqual(len(graph['relations']),len(old['relations'])+1)
        self.assertEqual(graph['independent_review'],'pending')
        m=json.loads((HERE/'manifest.json').read_bytes())
        for group in ['files','dependencies']:
            for f,h in m[group].items():self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h)

    def test_correction_identity_content_limit_and_model_bindings(self):
        graph=load_publications();nodes={n['id']:n for n in graph['publications']}
        original=nodes['doi:10.1061/jsfeaq.0001458'];correction=nodes['doi:10.1061/jsfeaq.0001706']
        lade=nodes['doi:10.1061/ajgeb6.0000204']
        self.assertEqual(original['publication_date_parts'],[1970,9])
        self.assertEqual(correction['publication_date_parts'],[1971,11])
        self.assertEqual(correction['version_role'],'correction')
        self.assertIn('Erratum for',correction['title'])
        self.assertEqual(original['model_ids'],['duncan-chang-1970'])
        self.assertEqual(correction['model_ids'],original['model_ids'])
        self.assertEqual(lade['model_ids'],['lade-duncan-1975', 'lade-duncan-1975-midpoint-elastic-eq19-gap-v4'])
        self.assertNotIn('doi:10.1061/ajgeb6.0000208',nodes)
        edge=next(e for e in graph['relations'] if e['source']==correction['id'])
        self.assertEqual((edge['target'],edge['relation']),(original['id'],'corrects'))
        self.assertIn('not verified',edge['summary'])
        self.assertEqual(edge['independent_review'],'pending')
        for node in [original,correction,lade]:
            ev=node['evidence'][0];data=json.loads((ROOT/ev['path']).read_bytes())['message']
            self.assertEqual(node['title'],data['title'][0])
            self.assertEqual(node['doi'],data['DOI'].lower())
            self.assertEqual(node['authors'],[(a.get('given','')+' '+a['family']).strip() for a in data['author']])

    def test_sqlite_and_static_package_retain_new_records(self):
        graph=load_publications();expected={n['id']:n for n in graph['publications']}
        ids=['doi:10.1061/jsfeaq.0001458','doi:10.1061/jsfeaq.0001706','doi:10.1061/ajgeb6.0000204']
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);dbpath=root/'atlas.sqlite';export_database(dbpath)
            with closing(sqlite3.connect(dbpath)) as db:
                self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
                for ident in ids:
                    row=db.execute('SELECT record_json FROM publications WHERE id=?',(ident,)).fetchone()
                    self.assertEqual(json.loads(row[0]),expected[ident])
                    bindings=db.execute('SELECT model_id FROM publication_models WHERE publication_id=?',(ident,)).fetchall()
                    self.assertCountEqual(bindings,[(model,) for model in expected[ident]['model_ids']])
                for mid in ['duncan-chang-1970','lade-duncan-1975']:
                    self.assertEqual(db.execute('SELECT executable,definition_json FROM models WHERE id=?',(mid,)).fetchone(),(0,None))
            package=root/'web';bundle(package)
            self.assertEqual((package/'publications.json').read_bytes(),(ROOT/'catalogue/publications.json').read_bytes())
            self.assertEqual((package/'catalogue.json').read_bytes(),(ROOT/'catalogue/manifest.json').read_bytes())

if __name__=='__main__': unittest.main()
