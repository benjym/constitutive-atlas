"""Boundary for the current native CLI and scoped v0.1 replay controls.

Only this module interprets atlas model/state/solver layouts. Unsupported forms
fail explicitly instead of being coerced into the development pilot.
"""
import json
import math
import hashlib
from pathlib import Path
import shutil
import subprocess
import time

from .common import ROOT, digest, read_json


class NativeAdapter:
    def __init__(self, solver, model_ids, model_dir=None):
        self.solver = Path(solver).resolve()
        self.solver_hash = digest(self.solver)
        process = subprocess.run([str(self.solver), '--describe'], capture_output=True,
                                 text=True, timeout=30, check=True)
        catalogue = json.loads(process.stdout)
        if catalogue.get('schema_version') != '0.1':
            raise ValueError('unsupported native catalogue contract')
        self.catalogue_hash = catalogue['sha256']
        self.models = {m['id']: m for m in catalogue['models'] if m['id'] in model_ids}
        model_dir = ROOT/'models' if model_dir is None else Path(model_dir)
        self.paths = {mid: model_dir/f'{mid}.json' for mid in model_ids}
        self.source_bytes = {}
        for mid, path in self.paths.items():
            content = path.read_bytes()
            self.source_bytes[mid] = content
            model = json.loads(content)
            if mid not in self.models or model != self.models[mid]:
                raise ValueError(f'{mid}: source and compiled model differ; rebuild the solver')
            if model.get('schema_version') != '0.1':
                raise ValueError(f'{mid}: pilot only supports v0.1 rate-independent models')
            if set(f['name'] for f in model['state']) - {'sigma', 'e', 'gamma'}:
                raise ValueError(f'{mid}: explicit initialization adapter required')
        self.source_hashes = {mid: hashlib.sha256(content).hexdigest() for mid, content in self.source_bytes.items()}
        self.origin_paths = dict(self.paths)
        self.origin_solver = self.solver

    def freeze(self, directory):
        """Run from immutable local copies while the shared worktree evolves."""
        directory = Path(directory).resolve()
        (directory/'models').mkdir()
        (directory/'solver').mkdir()
        solver = directory/'solver/atlas_solver'
        shutil.copy2(self.solver, solver)
        if digest(solver) != self.solver_hash:
            raise ValueError('solver changed while snapshotting; retry into a new run directory')
        for mid, content in self.source_bytes.items():
            path = directory/'models'/f'{mid}.json'
            path.write_bytes(content)
            self.paths[mid] = path
        self.solver = solver
        self.verify_unchanged()

    def origin_drift(self):
        return {'models': {mid: not path.exists() or digest(path) != self.source_hashes[mid]
                           for mid, path in self.origin_paths.items()},
                'solver': not self.origin_solver.exists() or digest(self.origin_solver) != self.solver_hash}

    def verify_unchanged(self):
        if digest(self.solver) != self.solver_hash:
            raise ValueError('solver changed during study execution')
        for mid, path in self.paths.items():
            if digest(path) != self.source_hashes[mid]:
                raise ValueError(f'{mid}: source changed during study execution')

    def initialize(self, mid, parameters, experiment):
        model = self.models[mid]
        if experiment.get('schema_version') != '0.1' or experiment['protocol'] != 'drained-triaxial':
            raise ValueError('pilot adapter requires a v0.1 drained experiment')
        if 'void_ratio' not in experiment['initial']:
            raise ValueError('missing measured initial void ratio')
        if set(parameters) != set(model['parameters']):
            raise ValueError('all parameters must be explicitly specified')
        for name, value in parameters.items():
            bounds = model['parameters'][name]
            if not bounds['min'] <= value <= bounds['max']:
                raise ValueError(f'{name}: outside model bounds')
        z = []
        for field in model['state']:
            if field['name'] == 'sigma':
                z.extend(experiment['initial']['effective_stress'])
            elif field['name'] == 'e':
                z.append(experiment['initial']['void_ratio'])
            elif field['name'] == 'gamma' and field.get('transient'):
                z.append(0.)
            else:
                raise ValueError('initialization must be explicit')
        return z

    def simulate(self, mid, parameters, experiment, target, steps, timeout=30):
        model = self.models[mid]
        z = self.initialize(mid, parameters, experiment)
        command = [str(self.solver), '--model', mid, '--parameters',
                   ','.join(str(parameters[n]) for n in model['parameters']),
                   '--initial', ','.join(map(str, z)), '--protocol', '1',
                   '--target', repr(target), '--steps', str(steps), '--cycles', '0']
        start = time.perf_counter()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            try:
                raw = json.loads(process.stdout)
            except json.JSONDecodeError:
                return {'status': 'process_failure', 'message': process.stderr[-2000:],
                        'elapsed_seconds': time.perf_counter()-start, 'points': []}
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': f'exceeded {timeout} seconds',
                    'elapsed_seconds': time.perf_counter()-start, 'points': []}
        if raw.get('catalogue_hash') not in (None, self.catalogue_hash):
            raise ValueError('solver catalogue changed during run')
        ok = raw.get('ok') is True and process.returncode == 0
        points = [{'axial_strain': p['strain'][0], 'q': p['q_signed'],
                   'volumetric_strain': sum(p['strain'][:3])} for p in raw.get('points', [])]
        return {'status': 'success' if ok else 'integration_failure',
                'message': raw.get('message', ''), 'elapsed_seconds': time.perf_counter()-start,
                'initial_state': z, 'points': points,
                'diagnostics': {key: sum(p.get(key, 0) for p in raw.get('points', []))
                                for key in ('iterations', 'substeps', 'rejected')}}

    def replay(self, mid, parameters, experiment, coordinates, maximum_increment=.0002, timeout=120):
        """Replay acquired axial coordinates using the shared drained driver.

        Every segment starts from the preceding committed state, with native
        mixed control and integration. Coordinates are never sorted. Output
        endpoints match observations; intermediate native states are omitted.
        No physical time or hold duration is inferred from the row order.
        """
        if not math.isfinite(maximum_increment) or maximum_increment <= 0:
            raise ValueError('positive finite replay increment required')
        coordinates = list(coordinates)
        if len(coordinates) < 2 or coordinates[0] != 0 or any(not math.isfinite(x) for x in coordinates):
            raise ValueError('at least two finite acquisition coordinates beginning at zero required')
        if timeout <= 0:
            raise ValueError('positive total replay timeout required')
        z = self.initialize(mid, parameters, experiment)
        if len(z) < 6 or self.models[mid]['state'][0]['name'] != 'sigma':
            raise ValueError('replay requires stress-first state layout')
        self.verify_unchanged()
        initial = list(z)
        reference = .5*(z[1]+z[2])
        strain = [0.]*6
        start = time.perf_counter()
        calls = 0
        max_drift = 0.
        points = []
        diagnostics = {'iterations': 0, 'substeps': 0, 'rejected': 0}

        def point(index):
            return {'observation_index': index, 'axial_strain': coordinates[index],
                    'q': z[0]-.5*(z[1]+z[2]), 'volumetric_strain': sum(strain[:3]),
                    'state': list(z), 'strain': list(strain)}

        points.append(point(0))
        status, message = 'success', ''
        for index, (previous, target) in enumerate(zip(coordinates, coordinates[1:]), 1):
            increment = target-previous
            # Rate-independent repeated coordinates have no inferred evolution.
            if increment == 0:
                points.append(point(index))
                continue
            steps = max(1, math.ceil(abs(increment)/maximum_increment))
            if steps > 5000 or abs(increment) > .1:
                raise ValueError('replay segment exceeds native laboratory limits')
            command = [str(self.solver), '--model', mid, '--parameters',
                       ','.join(str(parameters[n]) for n in self.models[mid]['parameters']),
                       '--initial', ','.join(map(str, z)), '--protocol', '1',
                       '--target', repr(increment), '--steps', str(steps), '--cycles', '0']
            remaining = timeout-(time.perf_counter()-start)
            if remaining <= 0:
                status, message = 'timeout', 'total replay deadline exceeded'
                break
            try:
                process = subprocess.run(command, capture_output=True, text=True, timeout=remaining)
                calls += 1
                raw = json.loads(process.stdout)
                if raw.get('catalogue_hash') != self.catalogue_hash:
                    raise ValueError('replay solver catalogue mismatch')
                if process.returncode or raw.get('ok') is not True:
                    status, message = 'integration_failure', raw.get('message', 'native failure')
                    break
                native = raw['points']
                if not native:
                    raise ValueError('native replay returned no committed endpoint')
                final = native[-1]
                candidate = final['state']
                delta = final['strain']
                if (len(candidate) != len(z) or len(delta) != 6 or
                        any(not math.isfinite(v) for v in candidate+delta) or
                        not math.isclose(delta[0], increment, rel_tol=1e-10, abs_tol=1e-14)):
                    raise ValueError('invalid native replay endpoint')
                drift = max(abs(.5*(p['state'][1]+p['state'][2])-reference) for p in native)
                # The native driver takes the segment's initial radial stress as
                # its target. Bound accumulated roundoff against the original.
                if drift > max(1., abs(reference))*1e-6:
                    status, message = 'control_failure', 'radial stress drift exceeds replay tolerance'
                    break
                max_drift = max(max_drift, drift)
                z = candidate
                strain = [a+b for a, b in zip(strain, delta)]
                for key in diagnostics:
                    diagnostics[key] += sum(p.get(key, 0) for p in native)
                points.append(point(index))
            except subprocess.TimeoutExpired:
                status, message = 'timeout', 'total replay deadline exceeded'
                break
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                status, message = 'invalid_prediction', str(exc)
                break
        self.verify_unchanged()
        return {'status': status, 'message': message, 'points': points,
                'initial_state': initial, 'last_committed_state': list(z),
                'completed_observations': len(points), 'requested_observations': len(coordinates),
                'elapsed_seconds': time.perf_counter()-start,
                'maximum_increment': maximum_increment, 'native_calls': calls,
                'maximum_radial_stress_drift_Pa': max_drift, 'diagnostics': diagnostics,
                'control': 'recorded axial strain in acquisition order; constant radial effective stress',
                'failure_policy': 'failed native segment rolled back to preceding observation'}

    def replay_oedometer(self, mid, parameters, initial_stress, initial_void_ratio,
                        coordinates, maximum_increment=.0005, timeout=120):
        """First-loading diagnostic with explicitly supplied initial full stress.

        Coordinates are declared by the caller (engineering or log height),
        never inferred here. No measured initial-state or history claim is made.
        The adapter supports only the stress/void-ratio state, not memory models.
        """
        model = self.models[mid]
        if ([(f['name'], f['shape']) for f in model['state']] != [('sigma', 'sym'), ('e', 'scalar')]
                or model.get('schema_version') != '0.1'):
            raise ValueError('oedometer diagnostic requires a reviewed stress/void-ratio layout')
        if set(parameters) != set(model['parameters']):
            raise ValueError('all parameters must be explicitly specified')
        for name, value in parameters.items():
            bounds = model['parameters'][name]
            if not math.isfinite(value) or not bounds['min'] <= value <= bounds['max']:
                raise ValueError(f'{name}: outside model bounds')
        stress = list(initial_stress)
        if (len(stress) != 6 or any(not math.isfinite(x) for x in stress)
                or stress[0] <= 0 or min(stress[1:3]) < 0
                or stress[1] != stress[2] or any(x != 0 for x in stress[3:])
                or not math.isfinite(initial_void_ratio) or initial_void_ratio <= 0):
            raise ValueError('explicit positive axial stress, axisymmetric tensor and positive void ratio required')
        coordinates = list(coordinates)
        if (len(coordinates) < 2 or coordinates[0] != 0
                or any(not math.isfinite(x) for x in coordinates)
                or any(b < a for a, b in zip(coordinates, coordinates[1:]))
                or coordinates[-1] <= 0):
            raise ValueError('first-loading coordinates must begin at zero and increase without sorting')
        if not math.isfinite(maximum_increment) or maximum_increment <= 0 or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('positive finite increment and timeout required')
        self.verify_unchanged()
        z = stress+[initial_void_ratio]
        initial = list(z)
        strain = [0.]*6
        points = []
        start = time.perf_counter()
        calls = 0
        diagnostics = {'iterations': 0, 'substeps': 0, 'rejected': 0}

        def point(index):
            return dict(observation_index=index, imposed_axial_coordinate=coordinates[index],
                        axial_stress=z[0], radial_stress=.5*(z[1]+z[2]), void_ratio=z[6],
                        state=list(z), strain=list(strain))

        points.append(point(0))
        status, message = 'success', ''
        for index, (previous, target) in enumerate(zip(coordinates, coordinates[1:]), 1):
            increment = target-previous
            if increment == 0:
                points.append(point(index))
                continue
            steps = max(1, math.ceil(increment/maximum_increment))
            if steps > 5000 or increment > .1:
                raise ValueError('oedometer segment exceeds native laboratory limits')
            command = [str(self.solver), '--model', mid, '--parameters',
                       ','.join(str(parameters[n]) for n in model['parameters']),
                       '--initial', ','.join(map(str, z)), '--protocol', '0',
                       '--target', repr(increment), '--steps', str(steps), '--cycles', '0']
            remaining = timeout-(time.perf_counter()-start)
            if remaining <= 0:
                status, message = 'timeout', 'total replay deadline exceeded'
                break
            try:
                process = subprocess.run(command, capture_output=True, text=True, timeout=remaining)
                calls += 1
                raw = json.loads(process.stdout)
                if raw.get('catalogue_hash') != self.catalogue_hash:
                    raise ValueError('oedometer solver catalogue mismatch')
                if process.returncode or raw.get('ok') is not True:
                    status, message = 'integration_failure', raw.get('message', 'native failure')
                    break
                native = raw['points']
                if not native:
                    raise ValueError('native replay returned no committed endpoint')
                for p in native:
                    if (len(p['state']) != 7 or len(p['strain']) != 6
                            or any(not math.isfinite(x) for x in p['state']+p['strain'])
                            or any(abs(x) > 1e-14 for x in p['strain'][1:])):
                        raise ValueError('invalid oedometer state or zero-lateral-strain control')
                candidate, delta = native[-1]['state'], native[-1]['strain']
                if not math.isclose(delta[0], increment, rel_tol=1e-10, abs_tol=1e-14):
                    raise ValueError('oedometer endpoint does not match imposed coordinate')
                z = candidate
                strain = [a+b for a, b in zip(strain, delta)]
                for key in diagnostics:
                    diagnostics[key] += sum(p.get(key, 0) for p in native)
                points.append(point(index))
            except subprocess.TimeoutExpired:
                status, message = 'timeout', 'total replay deadline exceeded'
                break
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                status, message = 'invalid_prediction', str(exc)
                break
        self.verify_unchanged()
        return dict(status=status, message=message, initial_state=initial, points=points,
                    last_committed_state=list(z), completed_observations=len(points),
                    requested_observations=len(coordinates), elapsed_seconds=time.perf_counter()-start,
                    maximum_increment=maximum_increment, native_calls=calls, diagnostics=diagnostics,
                    control='declared axial coordinate; zero lateral and shear strain increments',
                    failure_policy='failed native segment rolled back to preceding observation')
