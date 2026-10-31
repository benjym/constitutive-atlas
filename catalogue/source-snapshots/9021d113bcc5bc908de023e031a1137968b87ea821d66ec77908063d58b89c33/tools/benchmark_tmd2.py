"""Reproduce the fixed TMD2 research benchmark; no parameter fitting.

Measurements are local research inputs, not public deployment assets. The source
archive, raw member, normalized semantic content and frozen gates are checked.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.data import normalize_member

PACKET = ROOT / 'docs/benchmarks/kfs-tmd2-research-range-v1'
ARCHIVE_URL = 'https://www.torsten-wichtmann.de/KFSDB/TMD/TMD1-5/TMD1-5.zip'
ARCHIVE_SHA = 'c83098bca222dbcbb67b7cb4fa4e57c300d22cad2d71211e6393c85c3a74c712'
MEMBER_SHA = 'dbd60b1aab4608766e5d002f513ae31e8cda7898a4babe32afea89f997229667'
SEMANTIC_SHA = '11e6ecfb2d77f4db92ab1a167ead4b0d13de7a89031f72bbe05cab1df1bd90dc'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def semantic_hash(record):
    value = json.loads(json.dumps(record))
    value['provenance'].pop('normalized_at', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def normalize(archive):
    if sha(archive) != ARCHIVE_SHA:
        raise ValueError('Original TMD1-5 archive checksum mismatch; no solver execution')
    with zipfile.ZipFile(archive) as source:
        matches = [i for i in source.infolist() if i.filename == 'TMD2.dat']
        if len(matches) != 1 or matches[0].file_size > 5_000_000:
            raise ValueError('Expected one bounded TMD2.dat member')
        content = source.read(matches[0])
    if hashlib.sha256(content).hexdigest() != MEMBER_SHA:
        raise ValueError('TMD2 member checksum mismatch')
    record = normalize_member(content, 'TMD2.dat', ARCHIVE_SHA, MEMBER_SHA)
    if semantic_hash(record) != SEMANTIC_SHA:
        raise ValueError('Normalized TMD2 content changed; create a separately reviewed data version')
    return record


def command(args, directory, stem):
    """Journal commands and exact output before interpreting status."""
    receipt = {'command': list(map(str, args)), 'started': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    write(directory / (stem + '.json'), receipt)
    with (directory / (stem + '.stdout')).open('wb') as out, (directory / (stem + '.stderr')).open('wb') as err:
        result = subprocess.run(args, stdout=out, stderr=err, check=False)
    receipt.update(returncode=result.returncode, stdout_sha256=sha(directory / (stem + '.stdout')), stderr_sha256=sha(directory / (stem + '.stderr')))
    write(directory / (stem + '.json'), receipt)
    if result.returncode:
        raise RuntimeError(f'{stem} failed ({result.returncode}); see retained stdout/stderr')


def unpack_source(archive, output):
    """Write only the hash-verified Atlas regular files, never archive links."""
    with tarfile.open(archive) as source:
        for member in source:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'source':
                raise ValueError('Unexpected source archive path')
            dest = output / relative
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(source.extractfile(member).read())
            else:
                raise ValueError('Source archive contains a non-regular entry')


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    # Preserve failures and inputs in this new output; never overwrite an old run.
    status = {'kind': 'local-research-tmd2-reproduction', 'public_measurement_release': False, 'completed': False}
    write(out / 'run.json', status)
    try:
        import matplotlib  # Required before any build or material execution.
        manifest = json.loads((PACKET / 'packet-manifest.json').read_text())
        for name, digest in manifest.items():
            if sha(PACKET / name) != digest:
                raise ValueError('Frozen packet checksum mismatch: ' + name)
        archive = args.archive.resolve() if args.archive else out / 'KFS-TMD1-5.zip'
        if not args.archive:
            with urllib.request.urlopen(ARCHIVE_URL, timeout=30) as response:
                data = response.read(1_000_001)
            if len(data) > 1_000_000:
                raise ValueError('Source download exceeds expected bounded archive size')
            archive.write_bytes(data)
        normalized = out / 'KFS-TMD2.json'
        write(normalized, normalize(archive))
        status['data'] = {'archive_url': ARCHIVE_URL, 'archive_sha256': sha(archive), 'member_sha256': MEMBER_SHA, 'normalized_sha256': sha(normalized), 'normalized_semantic_sha256': SEMANTIC_SHA, 'timestamp_excluded_from_semantic_hash': 'provenance.normalized_at only'}
        # Reuse requires the exact already-built Atlas artifact, not arbitrary author binaries.
        if args.solver:
            solver = args.solver.resolve()
            previous = json.loads((PACKET / 'build-receipt.json').read_text())
            if sha(solver) != previous['artifact']['sha256']:
                raise ValueError('--solver must match the recorded Atlas artifact; omit it to build the frozen source')
        else:
            unpack_source(PACKET / 'source.tar.gz', out)
            expected = json.loads((PACKET / 'source-manifest.json').read_text())
            for name, digest in expected.items():
                if sha(out / 'source' / name) != digest:
                    raise ValueError('Unpacked source checksum mismatch: ' + name)
            command(['cmake', '-S', str(out / 'source'), '-B', str(out / 'build'), '-DCMAKE_BUILD_TYPE=Release'], out, 'configure')
            command(['cmake', '--build', str(out / 'build'), '--target', 'atlas_solver', '--parallel', '1'], out, 'build')
            solver = out / 'build/atlas_solver'
        metadata = (PACKET / 'generated-models.json') if args.solver else out / 'build/generated/models.json'
        if sha(metadata) != sha(PACKET / 'generated-models.json'):
            raise ValueError('Compiled model catalogue differs from the frozen benchmark')
        inputs = out / 'inputs'
        shutil.copytree(PACKET / 'inputs', inputs)
        (inputs / 'freeze.json').unlink()
        pins = json.loads((inputs / 'source-pins.json').read_text())
        pins['metadata']['path'] = str(metadata)
        pins['metadata']['sha256'] = sha(metadata)
        pins['artifact'] = {'path': str(solver), 'sha256': sha(solver)}
        pins['data'] = {'path': str(normalized), 'sha256': sha(normalized), 'semantic_sha256': SEMANTIC_SHA}
        pins['portable_source_packet_manifest_sha256'] = sha(PACKET / 'packet-manifest.json')
        write(inputs / 'source-pins.json', pins)
        write(inputs / 'portable-command.json', {'script_sha256': sha(Path(__file__)), 'source_archive_sha256': sha(PACKET / 'source.tar.gz'), 'data': status['data'], 'maximum_material_calls': 3})
        write(inputs / 'freeze.json', {'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'compiled_tmd2_calls_at_freeze': 0, 'maximum_tmd2_calls': 3, 'files': {f.name: sha(f) for f in sorted(inputs.iterdir()) if f.is_file()}})
        # Original reference, requests, settings and acceptance script remain exact.
        for name in ['reference.json', 'requests.json', 'protocol.json', 'assess.py', 'run_study.py']:
            if sha(inputs / name) != sha(PACKET / 'inputs' / name):
                raise ValueError('Frozen study input changed: ' + name)
        write(out / 'run.json', status)
        print('Inputs verified and frozen; executing exactly three serial TMD2 paths.', flush=True)
        command([sys.executable, str(inputs / 'run_study.py'), '--output', str(out / 'observations')], out, 'execute')
        command([sys.executable, str(inputs / 'assess.py'), '--observations', str(out / 'observations'), '--data', str(normalized), '--output', str(out / 'results')], out, 'assess')
        summary = json.loads((out / 'results/summary.json').read_text())
        lines = ['# TMD2 local reproduction', '', 'Source-informed operational reconstruction; historical strain conversion and independent scientific admission remain open.', '', 'Experimental errors are descriptive calibration-campaign errors, not held-out validation. Measured volume is fractional volume change; finite-kinematic equivalence is not verified.', '', '![Source/model reproduction](results/reproduction.png)', '', '| Path | Source envelope | q RMSE (kPa) | Volume RMSE (percentage points) |', '| --- | --- | ---: | ---: |']
        for row in summary['paths']:
            errors = row.get('experimental_errors', {})
            q = errors.get('q', {}).get('rmse')
            volume = errors.get('volumetric_strain', {}).get('rmse')
            passed = row.get('complete', False) and all(c['pass'] for c in row.get('source', {}).values())
            lines.append(f"| {row['id']} | {passed} | {q/1000 if q is not None else 'unavailable'} | {volume*100 if volume is not None else 'unavailable'} |")
        lines += ['', '| Adjacent paths | Max q change (Pa) | Max volume change | Pass |', '| --- | ---: | ---: | --- |']
        for pair in summary['refinement']:
            q, volume = pair['channels']['q'], pair['channels']['volumetric_strain']
            lines.append(f"| {' → '.join(pair['paths'])} | {q['maximum_difference']} | {volume['maximum_difference']} | {q['pass'] and volume['pass']} |")
        lines += ['', 'Sources: [2016 database](https://doi.org/10.1007/s11440-015-0402-z), [2019 model comparison](https://doi.org/10.1016/j.soildyn.2019.05.001).', '', 'See results/summary.json for every source gate and all error metrics. Raw/normalized measurements remain local research files; no public redistribution grant is inferred.', '']
        (out / 'report.md').write_text('\n'.join(lines))
        status.update(completed=True, source_pass=summary['source_pass'], refinement_pass=summary['refinement_pass'], solver_sha256=sha(solver), scientific_admission=False)
        write(out / 'run.json', status)
        print(f"Report: {out / 'results/summary.json'}; source={status['source_pass']}, refinement={status['refinement_pass']}")
        return 0 if status['source_pass'] and status['refinement_pass'] else 1
    except Exception as exc:
        status['failure'] = str(exc)
        write(out / 'run.json', status)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Fresh local research directory (contains private measurements)')
    parser.add_argument('--archive', type=Path, help='Use pinned original TMD1-5 ZIP offline; otherwise fetch from the author')
    parser.add_argument('--solver', type=Path, help='Reuse exact recorded native Atlas artifact; otherwise build frozen source serially')
    args = parser.parse_args()
    try:
        return run(args)
    except Exception as exc:
        print(f'TMD2 benchmark failed: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
