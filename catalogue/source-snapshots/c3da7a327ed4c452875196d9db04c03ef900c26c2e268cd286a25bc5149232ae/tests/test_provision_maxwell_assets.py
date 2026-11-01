import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from tools import provision_maxwell_assets as p


class ProvisionTests(unittest.TestCase):
    def archive(self, directory, entries):
        path = Path(directory)/'closure.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            for name, data, kind in entries:
                info = tarfile.TarInfo(name)
                info.type = kind
                info.size = len(data) if kind == tarfile.REGTYPE else 0
                info.linkname = '/tmp/unwanted' if kind == tarfile.SYMTYPE else ''
                archive.addfile(info, io.BytesIO(data) if info.size else None)
        return path

    def test_selective_no_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries=[(name,b'asset',tarfile.REGTYPE) for name in p.MEMBERS]
            entries.append(('../../unwanted',b'ignored',tarfile.REGTYPE))
            archive=self.archive(tmp,entries)
            binding={key:p.digest(b'asset') for _,key in p.MEMBERS.values()}
            with patch.object(p,'ARCHIVE_SHA256',p.digest(archive.read_bytes())):
                result=p.selected_bytes(archive,binding)
            self.assertEqual(set(result),{v[0] for v in p.MEMBERS.values()})
            self.assertEqual(list(Path(tmp).iterdir()),[archive])

    def test_archive_and_member_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=self.archive(tmp,[(n,b'asset',tarfile.REGTYPE) for n in p.MEMBERS])
            binding={key:p.digest(b'other') for _,key in p.MEMBERS.values()}
            with self.assertRaisesRegex(ValueError,'archive'):
                p.selected_bytes(archive,binding)
            with patch.object(p,'ARCHIVE_SHA256',p.digest(archive.read_bytes())):
                with self.assertRaisesRegex(ValueError,'artifact'):
                    p.selected_bytes(archive,binding)

    def test_duplicate_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            name=next(iter(p.MEMBERS))
            for entries, message in [
                ([(name,b'',tarfile.REGTYPE)]*2,'Duplicate'),
                ([(name,b'',tarfile.SYMTYPE)],'Invalid selected'),
            ]:
                archive=self.archive(tmp,entries)
                with patch.object(p,'ARCHIVE_SHA256',p.digest(archive.read_bytes())):
                    with self.assertRaisesRegex(ValueError,message):
                        p.selected_bytes(archive,{})

    def test_existing_destination_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'existing';target.mkdir()
            marker=target/'keep';marker.write_text('unchanged')
            with self.assertRaisesRegex(ValueError,'existing'):
                p.provision(target)
            self.assertEqual(marker.read_text(),'unchanged')


if __name__ == '__main__':
    unittest.main()
