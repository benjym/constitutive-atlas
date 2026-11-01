"""Synthetic archives/mocked E5/package guards only; never load executable artifacts."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
from tools import provision_implicit_path_assets as p

DATA={name:('fixture-only: '+name).encode() for name in p.MEMBERS}
HASHES={name:p.digest(data) for name,data in DATA.items()}
def archive(extra=None, omit=None, duplicate=None, kind=None, oversize=False):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w',format=tarfile.USTAR_FORMAT) as tar:
        rows=[(name,data) for name,data in DATA.items() if name!=omit]
        if duplicate: rows.append((duplicate,DATA[duplicate]))
        if extra: rows.append((extra,b'extra fixture'))
        for name,data in rows:
            info=tarfile.TarInfo(name);info.size=len(data)
            if name==kind:
                info.type=tarfile.SYMTYPE;info.linkname='outside';info.size=0
            tar.addfile(info,io.BytesIO(data) if info.isreg() else None)
    raw=stream.getvalue()
    if oversize:
        # Header only: reject declared oversize before any huge payload allocation.
        info=tarfile.TarInfo('lade-domain.mjs');info.size=p.MAX_MEMBER+1
        raw=info.tobuf(format=tarfile.USTAR_FORMAT)+b'\0'*1024
    return gzip.compress(raw,mtime=0)

class ProvisionTests(unittest.TestCase):
    def test_five_regular_members(self):
        self.assertEqual(p.selected_bytes(archive(),HASHES),DATA)
    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):p.selected_bytes(archive(duplicate='lade-domain.mjs'),HASHES)
    def test_extra(self):
        with self.assertRaisesRegex(ValueError,'Unexpected'):p.selected_bytes(archive(extra='extra'),HASHES)
    def test_traversal(self):
        with self.assertRaisesRegex(ValueError,'unsafe'):p.selected_bytes(archive(extra='../escape'),HASHES)
    def test_absolute(self):
        with self.assertRaisesRegex(ValueError,'unsafe'):p.selected_bytes(archive(extra='/escape'),HASHES)
    def test_symlink(self):
        with self.assertRaisesRegex(ValueError,'regular'):p.selected_bytes(archive(kind='lade-domain.mjs'),HASHES)
    def test_hardlink(self):
        out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w') as tar:
            m=tarfile.TarInfo('lade-domain.mjs');m.type=tarfile.LNKTYPE;m.linkname='lade-domain.wasm';tar.addfile(m)
        with self.assertRaisesRegex(ValueError,'regular'):p.selected_bytes(gzip.compress(out.getvalue()),HASHES)
    def test_oversize(self):
        with self.assertRaisesRegex(ValueError,'16 MiB'):p.selected_bytes(archive(oversize=True),HASHES)
    def test_hash(self):
        bad={**HASHES,'lade-domain.mjs':'0'*64}
        with self.assertRaisesRegex(ValueError,'Changed'):p.selected_bytes(archive(),bad)
    def test_missing(self):
        with self.assertRaisesRegex(ValueError,'Missing'):p.selected_bytes(archive(omit='lade-domain.mjs'),HASHES)
    def test_exact_hash_fields(self):
        with self.assertRaisesRegex(ValueError,'exact five'):p.selected_bytes(archive(),{**HASHES,'extra':'0'*64})
    def test_concatenated_tar_extra(self):
        raw=gzip.decompress(archive())
        extra=io.BytesIO()
        with tarfile.open(fileobj=extra,mode='w') as tar:
            m=tarfile.TarInfo('extra');m.size=1;tar.addfile(m,io.BytesIO(b'x'))
        with self.assertRaisesRegex(ValueError,'Unexpected'):p.selected_bytes(gzip.compress(raw+extra.getvalue()),HASHES)
    def test_bounded_decompression(self):
        with patch.object(p,'MAX_ARCHIVE',1024):
            with self.assertRaisesRegex(ValueError,'decompressed'):p.selected_bytes(archive(),HASHES)
    def test_existing_destination_no_approval_read(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary,patch.object(p,'authorized_index') as guard:
            with self.assertRaisesRegex(ValueError,'existing'):p.provision(temporary)
            guard.assert_not_called()
    def test_dangling_destination_symlink(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary,patch.object(p,'authorized_index') as guard:
            dest=Path(temporary)/'dest';dest.symlink_to(Path(temporary)/'absent')
            with self.assertRaisesRegex(ValueError,'existing'):p.provision(dest)
            guard.assert_not_called()
    def test_missing_e5_before_archive(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary,patch.object(p,'validate_review',side_effect=FileNotFoundError('fixture missing E5')) as review,patch.object(p,'selected_bytes') as select:
            dest=Path(temporary)/'dest'
            with self.assertRaises(FileNotFoundError):p.provision(dest)
            review.assert_called_once();select.assert_not_called();self.assertFalse(dest.exists())
    def fixture(self,root):
        archive_bytes=archive();path=root/p.ARCHIVE;path.parent.mkdir(parents=True);path.write_bytes(archive_bytes)
        index={'status':'passed','model':p.MODEL,'archive':{'path':p.ARCHIVE,'sha256':p.digest(archive_bytes)},'files':HASHES}
        (root/p.INDEX).write_text(json.dumps(index))
        expected={'id':'synthetic-only','model_id':p.MODEL,'status':'approved'}
        registry=root/'catalogue/approved-models.json';registry.parent.mkdir(parents=True,exist_ok=True);registry.write_text(json.dumps({'models':[expected]}))
        record={'model':{'id':p.MODEL},'artifacts':[{'path':name,'sha256':p.digest((root/name).read_bytes())} for name in [p.INDEX,p.ARCHIVE]]}
        return index,expected,record
    def test_mocked_authorization_explicit_pins(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root=Path(temporary);index,expected,record=self.fixture(root)
            with patch.object(p,'ROOT',root),patch.object(p,'validate_review',return_value=record),patch.object(p,'approval_entry',return_value=expected):
                self.assertEqual(p.authorized_index()[0],index)
                record['artifacts'].pop()
                with self.assertRaisesRegex(ValueError,'explicitly pin'):p.authorized_index()
    def test_registry_mismatch(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root=Path(temporary);_,expected,record=self.fixture(root)
            with patch.object(p,'ROOT',root),patch.object(p,'validate_review',return_value=record),patch.object(p,'approval_entry',return_value={**expected,'id':'wrong'}):
                with self.assertRaisesRegex(ValueError,'registry'):p.authorized_index()
    def test_index_archive_path_mismatch(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root=Path(temporary);index,expected,record=self.fixture(root);index['archive']['path']='other.tar.gz';(root/p.INDEX).write_text(json.dumps(index));record['artifacts'][0]['sha256']=p.digest((root/p.INDEX).read_bytes())
            with patch.object(p,'ROOT',root),patch.object(p,'validate_review',return_value=record),patch.object(p,'approval_entry',return_value=expected):
                with self.assertRaisesRegex(ValueError,'Invalid or unbound'):p.authorized_index()
    def test_mocked_stage_guard_before_rename(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root=Path(temporary);index,expected,record=self.fixture(root);dest=root/'installed';seen=[]
            def guard(package,build):
                self.assertFalse(dest.exists());self.assertEqual({str(x.relative_to(build)) for x in build.rglob('*') if x.is_file()},p.MEMBERS)
                self.assertEqual({name:(build/name).read_bytes() for name in p.MEMBERS},DATA);seen.append(True);return {'fixture':'no executable artifact'}
            with patch.object(p,'ROOT',root),patch.object(p,'validate_review',return_value=record),patch.object(p,'approval_entry',return_value=expected),patch.object(p,'bundle',side_effect=guard):
                result=p.provision(dest)
                self.assertEqual(result['files'],HASHES);self.assertTrue(dest.exists());self.assertEqual(seen,[True])
    def test_guard_failure_does_not_install(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            root=Path(temporary);index,expected,record=self.fixture(root);dest=root/'installed'
            with patch.object(p,'ROOT',root),patch.object(p,'validate_review',return_value=record),patch.object(p,'approval_entry',return_value=expected),patch.object(p,'bundle',side_effect=ValueError('fixture guard rejected')):
                with self.assertRaisesRegex(ValueError,'guard rejected'):p.provision(dest)
                self.assertFalse(dest.exists());self.assertEqual(list(root.glob('.implicit-path-provision-*')),[])
    def test_duplicate_json(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):p.parse_json(b'{"a":1,"a":2}')

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ProvisionTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (HERE/'pure-results.json').write_text(json.dumps({'scope':'synthetic tar/mock E5/package guard only; no executable module/material/build calls','tests':result.testsRun,'passed':result.wasSuccessful(),'failures':[str(x) for x in result.failures],'errors':[str(x) for x in result.errors]},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
