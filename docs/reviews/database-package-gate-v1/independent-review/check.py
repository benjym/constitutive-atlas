"""Verify exact reviewed bytes and unchanged structural checks, without engine execution."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def main():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for name, digest in manifest['inputs'].items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError('Changed review input: ' + name)
    for name, digest in manifest['outputs'].items():
        if sha((HERE / name).read_bytes()) != digest:
            raise ValueError('Changed review output: ' + name)
    before = json.loads((HERE.parent / 'before.json').read_text())
    for name, receipt in before.items():
        if sha((ROOT / receipt['archive']).read_bytes()) != receipt['sha256']:
            raise ValueError('Changed original: ' + name)
    name = 'tools/test_web_package.mjs'
    original = (ROOT / before[name]['archive']).read_text()
    candidate = (ROOT / name).read_text()
    additions = ["import {validateDatabasePackage} from './validate_database_package.mjs';\n", ' validateDatabasePackage(directory);\n']
    for line in additions:
        if candidate.count(line) != 1:
            raise ValueError('Missing/duplicate hook')
        candidate = candidate.replace(line, '')
    if candidate != original:
        raise ValueError('Unrelated structural gate changes')
    strict = (ROOT / name).read_text()
    if strict.index('const metadata=validatePackage(directory);') > strict.index('const createAtlas='):
        raise ValueError('Static gate after engine import')
    supported = (ROOT / 'tools/test_supported_package.mjs').read_text()
    if supported.index('catalogue=validatePackage(directory)') > supported.index('const createAtlas='):
        raise ValueError('Supported static gate after engine import')
    delta = json.loads((HERE.parent / 'workflow-delta.json').read_text())
    receipt = json.loads((HERE.parent / 'workflow-before.json').read_text())
    base = subprocess.check_output(['git', 'show', delta['base_revision'] + ':' + delta['path']], cwd=ROOT)
    proposed = (HERE.parent / 'proposed-verify.yml').read_bytes()
    if sha(base) != delta['base_sha256'] or base.count(delta['before'].encode()) != 2:
        raise ValueError('Changed workflow projection base')
    if proposed != base.replace(delta['before'].encode(), delta['after'].encode()) or sha(proposed) != delta['proposed_sha256']:
        raise ValueError('Extra workflow projection changes')
    if sha((ROOT / receipt['archive']).read_bytes()) != receipt['sha256']:
        raise ValueError('Changed workflow before archive')
    return {'status':'PASS', 'input_bindings':len(manifest['inputs']), 'output_bindings':len(manifest['outputs']), 'before_archives':3, 'exact_workflow_command_insertions':2, 'exact_additive_gate_lines':2, 'compiled_calls':0}

if __name__ == '__main__':
    print(json.dumps(main(),sort_keys=True))
