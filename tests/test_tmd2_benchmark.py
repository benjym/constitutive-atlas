"""Input identity checks for the bounded TMD2 command; no native execution."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.benchmark_tmd2 import normalize, semantic_hash, SEMANTIC_SHA

class Tmd2InputIdentity(unittest.TestCase):
    def test_timestamp_only_is_excluded_from_content_identity(self):
        data={'provenance':{'normalized_at':'old','member_sha256':'abc'},'rows':[{'q':1}]}
        changed=json.loads(json.dumps(data));changed['provenance']['normalized_at']='new'
        self.assertEqual(semantic_hash(data),semantic_hash(changed))
        changed['rows'][0]['q']=2
        self.assertNotEqual(semantic_hash(data),semantic_hash(changed))
        changed=json.loads(json.dumps(data));changed['provenance']['member_sha256']='def'
        self.assertNotEqual(semantic_hash(data),semantic_hash(changed))

    def test_archive_mismatch_is_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'changed.zip';path.write_bytes(b'changed original archive')
            with patch('tools.benchmark_tmd2.zipfile.ZipFile') as reader:
                with self.assertRaisesRegex(ValueError,'checksum mismatch'):normalize(path)
                reader.assert_not_called()

    def test_pinned_local_original_reconstructs_content(self):
        source=Path(__file__).resolve().parents[1]/'data/raw/KFS-TMD1-5.zip'
        if not source.exists():self.skipTest('private original source archive unavailable')
        record=normalize(source)
        self.assertEqual(semantic_hash(record),SEMANTIC_SHA)
        self.assertEqual(record['id'],'KFS-TMD2')
        self.assertEqual(record['rows'][0]['q'],-153.04999999999998)
        self.assertEqual(record['provenance']['redistribution'],'not-reviewed; local research copy only')

if __name__=='__main__':unittest.main()
