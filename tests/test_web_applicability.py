"""Static applicability export and pure browser disclosure contracts."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from atlas.model import ROOT
from tools.build_applicability import bundle

class ApplicabilityWebTests(unittest.TestCase):
    def test_exact_metadata_only_package_is_deterministic(self):
        matrix=json.loads((ROOT/'catalogue/applicability/kfs-development-v1.json').read_bytes())
        pins=[matrix['dataset'][k] for k in ['allocation','reservations']]
        pins += [p for row in matrix['rows'] for p in row['evidence']]
        expected={'applicability.json'}|{'applicability-records/'+p['path'] for p in pins}
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/'constitutive-atlas';bundle(dest)
            first={str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()}
            self.assertEqual(set(first),expected)
            for p in pins:self.assertEqual(first['applicability-records/'+p['path']],(ROOT/p['path']).read_bytes())
            self.assertEqual(first['applicability.json'],(ROOT/'catalogue/applicability/kfs-development-v1.json').read_bytes())
            bundle(dest)
            self.assertEqual(first,{str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()})
            self.assertFalse(any(x.endswith(('.pdf','.wasm','.dat')) for x in first))

    def test_corrupt_metadata_stops_before_destination_writes(self):
        matrix=json.loads((ROOT/'catalogue/applicability/kfs-development-v1.json').read_bytes())
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'source';target=root/'catalogue/applicability';target.mkdir(parents=True)
            matrix['dataset']['allocation']['sha256']='0'*64
            (target/'kfs-development-v1.json').write_text(json.dumps(matrix))
            source=matrix['dataset']['allocation']['path'];p=root/source;p.parent.mkdir(parents=True);p.write_bytes((ROOT/source).read_bytes())
            dest=Path(folder)/'site';dest.mkdir();(dest/'applicability.json').write_text('previous')
            with self.assertRaisesRegex(ValueError,'identity mismatch'):bundle(dest,root=root)
            self.assertEqual((dest/'applicability.json').read_text(),'previous')
            self.assertEqual(len(list(dest.iterdir())),1)

    @unittest.skipUnless(shutil.which('node'),'Node.js required')
    def test_browser_disclosure_contracts(self):
        result=subprocess.run(['node','--test','tests/test_applicability_browser.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
