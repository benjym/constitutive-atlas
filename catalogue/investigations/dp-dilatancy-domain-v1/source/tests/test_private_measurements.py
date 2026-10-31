"""Permission-held preparation preserves values without inventing missing units."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.prepare_private_measurements import prepare_table


class PrivateMeasurementTests(unittest.TestCase):
    def prepare(self, text, headers, count, columns):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name); raw = text.encode()
        with zipfile.ZipFile(root/'held.zip','w') as z: z.writestr('measurement.dat',raw)
        package=dict(source_id='fixture',filename='held.zip',sha256=hashlib.sha256((root/'held.zip').read_bytes()).hexdigest())
        table=dict(member='measurement.dat',sha256=hashlib.sha256(raw).hexdigest(),header_lines=headers,
                   numeric_rows=count,numeric_column_counts=columns)
        return root,package,table

    def test_explicit_units_comments_and_missing_unit_map(self):
        root,package,table=self.prepare('strain pressure\n[%] [kPa]\n0 2\n-1,5 3\n#4 5\n',
                                       ['strain pressure','[%] [kPa]','#4 5'],2,{'2':2})
        result=prepare_table(package,table,root,root)
        with gzip.open(root/result['path'],'rt') as f:rows=[json.loads(line) for line in f]
        meta=rows[0]['metadata'];self.assertFalse(meta['public_hosting'])
        self.assertEqual(meta['units'],['1','Pa'])
        numeric=[r for r in rows[1:] if 'native' in r]
        self.assertEqual(numeric[1],dict(source_line=4,native=[-1.5,3],values=[-.015,3000]))
        self.assertEqual(rows[-1],dict(source_line=5,source_text='#4 5'))
        # One unit for a two-channel table is ambiguous; preserve native values.
        table['header_lines']=['[kPa]']
        result=prepare_table(package,table,root,root)
        with gzip.open(root/result['path'],'rt') as f:rows=[json.loads(line) for line in f]
        self.assertEqual(rows[0]['metadata']['source_units'],[])
        self.assertTrue(all('values' not in r for r in rows[1:]))

    def test_changed_source_cannot_pass_review_counts_and_digest(self):
        root,package,table=self.prepare('x y\n1 2\n3 4\n',['x y'],2,{'2':2})
        table['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'differs from reviewed source'):
            prepare_table(package,table,root,root)
