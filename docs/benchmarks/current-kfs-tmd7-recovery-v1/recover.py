"""Read-only relocation harness for the preserved TMD7 saved audit.

The frozen source and receipts remain byte-identical. Only physical lookup
locations and the saved request's executable-location identity are rebound.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class ReboundRequests:
    """Preserve original command identity for the unchanged saved tracker."""
    def __init__(self, saved, physical, logical, counts):
        self.saved, self.physical, self.logical, self.counts = saved, str(physical), logical, counts

    def run(self, command, **kwargs):
        require(command and command[0] == self.physical, 'unexpected physical executable')
        original = [self.logical, *command[1:]]
        result = self.saved.run(original, **kwargs)
        self.counts.append(1)
        return result


def recover(bundle):
    policy = json.loads((HERE / 'policy.json').read_text())
    freeze = json.loads((HERE / 'freeze.json').read_text())
    require(sha(HERE / 'policy.json') == freeze['policy_sha256'] and
            sha(Path(__file__)) == freeze['runner_sha256'], 'recovery policy/source changed')
    preserver = ROOT / policy['preserver_path']
    require(sha(preserver) == policy['preserver_sha256'], 'preservation verifier changed')
    P = module('tmd7_preservation_verifier', preserver)
    bundle = Path(bundle).resolve()
    inventory = P.verify(bundle, policy['inventory_sha256'])
    source = bundle / 'payload/repository'
    packet = source / 'docs/benchmarks/current-kfs-tmd7-v1'
    original_policy = json.loads((packet / 'policy.json').read_text())
    original_index = json.loads((packet / 'private-evidence-index.json').read_text())
    require(sha(packet / 'results.json') == policy['expected_scalar_sha256'], 'original scalar identity differs')
    denied = [Path(inventory['source_root']).resolve(), Path(original_index['directory']).resolve(),
              Path(original_policy['baseline_directory']).resolve(),
              Path(original_policy['engines']['current']['path']).resolve()]
    require(all(not bundle.is_relative_to(old) for old in denied), 'snapshot overlaps original study locations')
    active = False
    probe = False
    probes = 0
    original_attempts = 0
    reads = set()

    def hook(event, args):
        nonlocal probes, original_attempts
        if not active:
            return
        require(event not in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'os.fork'),
                'process execution forbidden during saved recovery')
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if any(path == old or path.is_relative_to(old) for old in denied):
            if probe:
                probes += 1
            else:
                original_attempts += 1
            raise ValueError('original study content read forbidden')
        mode, flags = args[1:3]
        require(not (isinstance(mode, str) and any(c in mode for c in 'wax+')) and
                not (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)),
                'write-open forbidden during saved recovery')
        if path.is_relative_to(bundle):
            reads.add(str(path.relative_to(bundle)))

    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(bundle.parent / '.unused-tmd7-recovery-cache')
    sys.addaudithook(hook)
    translations = []
    try:
        active = True
        probe = True
        for old in denied:
            try:
                old.read_bytes()
            except ValueError as error:
                require(str(error) == 'original study content read forbidden', 'unexpected probe rejection')
            else:
                raise ValueError('original-location read guard did not reject')
        probe = False
        R = module('relocated_current_tmd7_audit', packet / 'replay.py')

        def baseline_lookup(frozen_policy):
            directory = bundle / 'payload/baseline'
            for name, expected in frozen_policy['baseline_files'].items():
                require(sha(directory / name) == expected, 'relocated baseline differs')
            return directory

        def engine_lookup(tracker, frozen_policy, engine):
            entry = frozen_policy['engines'][engine]
            physical = (bundle / 'payload/artifacts/current-atlas_solver' if engine == 'current'
                        else source / 'paper/results/pilot-matched96/solver/atlas_solver')
            translated = ReboundRequests(tracker, physical, entry['path'], translations)
            adapter = R.OLD.adapter_class(translated)(physical, [R.R.MODEL], source / entry['model_directory'])
            require(adapter.solver_hash == entry['artifact_sha256'] and
                    adapter.catalogue_hash == entry['catalogue_hash'], 'relocated engine identity differs')
            return adapter

        # Two explicit I/O substitutions. Do not alter law, policy or audit math.
        R.verify_baseline = baseline_lookup
        R.setup = engine_lookup
        result = R.audit(bundle / 'payload/current')
        require(result == R.read(packet / 'results.json'), 'recovered public scalar result differs')
        require(len(translations) == 88, 'saved request coverage differs')
    finally:
        active = False
    require(original_attempts == 0 and probes == 4, 'original-location guard coverage differs')
    P.verify(bundle, policy['inventory_sha256'])
    return {'id': policy['id'], 'result': 'pass', 'scalar_result_exact': True,
            'original_scalar_sha256': policy['expected_scalar_sha256'],
            'inventory_sha256': policy['inventory_sha256'], 'snapshot_files_verified': len(inventory['files']),
            'snapshot_files_read_during_reconstruction': len(reads),
            'saved_requests_verified': len(translations), 'location_guard_probes_rejected': probes,
            'original_study_content_read_attempts_during_audit': original_attempts,
            'snapshot_unchanged': True, 'new_native_calls': 0, 'new_builds': 0,
            'scientific_admission': False, 'scope': policy['limits']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    print(json.dumps(recover(args.bundle), indent=2, allow_nan=False))
