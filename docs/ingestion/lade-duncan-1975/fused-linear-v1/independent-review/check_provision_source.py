"""Synthetic-only provisioner audit; mocked approval/package guards, no assets."""
from pathlib import Path
import gzip, hashlib, importlib.util, io, json, sys, tarfile, unittest
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent/'asset-provision-review'
OUT.mkdir(exist_ok=True)
BASE=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1'
sys.path.insert(0,str(ROOT))
checks=[]
for receipt in ['SOURCE_FREEZE.json','source-pins.json']:
    for name,pin in json.loads((BASE/receipt).read_bytes())['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,name
        checks.append({'name':'pin '+name,'passed':True})
spec=importlib.util.spec_from_file_location('provision_synthetic_tests',BASE/'test_provision.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.HERE=OUT
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(module.ProvisionTests))
(OUT/'synthetic-test-log.txt').write_text(stream.getvalue())
assert result.wasSuccessful() and result.testsRun==22
# A GNU extended-name header is consumed internally by tarfile and not yielded.
raw=io.BytesIO()
with tarfile.open(fileobj=raw,mode='w',format=tarfile.GNU_FORMAT) as tar:
    payload=b'lade-domain.mjs\0';header=tarfile.TarInfo('././@LongLink');header.type=tarfile.GNUTYPE_LONGNAME;header.size=len(payload);tar.addfile(header,io.BytesIO(payload))
    for name,data in module.DATA.items():
        info=tarfile.TarInfo('ignored-physical-name' if name=='lade-domain.mjs' else name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
witness=gzip.compress(raw.getvalue(),mtime=0)
accepted=module.p.selected_bytes(witness,module.HASHES)==module.DATA
summary={'pure_tests':result.testsRun,'pure_passed':result.wasSuccessful(),'pin_checks':checks,'GNU_longname_metadata_witness_accepted':accepted,'witness_scope':'Synthetic nonexecutable fixture; six physical nonzero tar headers, five yielded regular members. No real index/approval/archive/artifact execution.'}
(OUT/'source-check-results.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'gnu-longname-witness.tar.gz').write_bytes(witness)
print(json.dumps({k:v for k,v in summary.items() if k!='pin_checks'}))
