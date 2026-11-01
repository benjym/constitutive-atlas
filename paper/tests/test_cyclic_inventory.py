import copy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, read_json
from analysis.cyclic_inventory import build_inventory, validate_assignments


class CyclicInventoryTests(unittest.TestCase):
    def setUp(self):
        self.inventory = read_json(ROOT/'paper/study/ottawa_cyclic_inventory.json')

    def test_workbook_phases_and_summaries_share_blocks(self):
        rows = [r for r in self.inventory['records'] if r['id'].startswith('LEAP-2018-TOR-DR50-0P10-')]
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({r['file_block'] for r in rows}), 1)
        assignments = {rows[0]['id']: 'development', rows[-1]['id']: 'reserved_final'}
        with self.assertRaisesRegex(ValueError, 'cross development/final'):
            validate_assignments(self.inventory, assignments)

    def test_raw_and_processed_records_cannot_leak_across_split(self):
        assignments = {'LEAP-2018-TOR-DR50-0P10-LOADING': 'development',
                       'LEAP-2018-TOR-RAW-F051-LOADING': 'reserved_final'}
        with self.assertRaisesRegex(ValueError, 'cross development/final'):
            validate_assignments(self.inventory, assignments)
        assignments = {key: 'development' for key in assignments}
        validate_assignments(self.inventory, assignments)

    def test_changed_source_bytes_and_duplicate_record_ids_are_rejected(self):
        registry = read_json(ROOT/'data/public_sources.json')
        report = {'records': [dict(r, archive_sha256=r['source_file_sha256'])
                              for r in self.inventory['records']]}
        bad = copy.deepcopy(report)
        bad['records'][0]['archive_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'source identity'):
            build_inventory(bad, registry)
        report['records'].append(report['records'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate cyclic record'):
            build_inventory(report, registry)


if __name__ == '__main__':
    unittest.main()
