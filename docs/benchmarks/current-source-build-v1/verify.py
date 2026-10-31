"""Audit saved build evidence without building or executing the solver."""
from pathlib import Path
import hashlib
import json
import sys

PACKET = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(packet=PACKET):
    evidence = packet/'evidence'
    policy = json.loads((packet/'protocol.json').read_text())
    manifest = json.loads((packet/'source-manifest.json').read_text())
    result = json.loads((evidence/'result.json').read_text())
    freeze = json.loads((evidence/'freeze.json').read_text())
    assert sha(packet/'protocol.json') == freeze['protocol_sha256']
    assert sha(packet/'source-manifest.json') == policy['source_manifest_sha256'] == freeze['source_manifest_sha256']
    assert sha(packet/'reproduce.py') == freeze['runner_sha256']
    assert sha(evidence/'freeze.json') == result['freeze_sha256']
    assert result['source_commit'] == manifest['source_commit'] == policy['source_commit']
    assert result['source_files_checked'] == len(manifest['files']) == 351
    for name,digest in result['evidence_files'].items():
        assert sha(evidence/name) == digest, name
    for name,digest in result['build_files'].items():
        assert sha(evidence/name) == digest, name
    for stem in ['01-expected','02-cmake-version','03-configure','04-compiler-version','05-build','06-describe']:
        receipt = json.loads((evidence/(stem+'.json')).read_text())
        assert type(receipt['returncode']) is int and receipt['returncode'] == 0, stem
        assert receipt['stdout_sha256'] == sha(evidence/(stem+'.stdout')), stem
        assert receipt['stderr_sha256'] == sha(evidence/(stem+'.stderr')), stem
    build = json.loads((evidence/'05-build.json').read_text())['command']
    describe = json.loads((evidence/'06-describe.json').read_text())['command']
    assert build == ['cmake','--build',str(Path(result['artifact_path']).parent),'--target','atlas_solver','--parallel','1']
    assert describe == [result['artifact_path'],'--describe']
    catalogue = json.loads((evidence/'06-describe.stdout').read_text())
    assert catalogue['sha256'] == result['catalogue_identity'] == freeze['catalogue_identity'] == '0d2e46841e859ca94bd69fff91020a4516b24f2c50c139f61ece5748b00b3fe7'
    assert len(catalogue['models']) == freeze['model_count'] == result['model_count'] == 9
    assert result['status'] == 'pass' and result['material_calls'] == 0 and result['native_metadata_calls'] == 1
    return result

if __name__ == '__main__':
    result = audit(Path(sys.argv[1]) if len(sys.argv)>1 else PACKET)
    print(f"PASS: {result['source_files_checked']} source pins; six successful command receipts; nine-model catalogue; metadata only")
