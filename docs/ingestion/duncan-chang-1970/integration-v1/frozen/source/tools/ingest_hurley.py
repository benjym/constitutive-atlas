"""Preserve Hurley 3DXRD measurements without inventing machine-test curves."""
from __future__ import annotations

import hashlib
import io
import math
import zipfile


def read_hurley(source, raw_dir):
    from scipy.io import loadmat

    file = source['files'][0]
    raw = (raw_dir / file['filename']).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != file['sha256']:
        raise ValueError('Hurley archive checksum mismatch')
    records = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for pressure in (20, 30, 35):
            prefix = f'3dxrd_all/3dxrd_{pressure}mpa/'
            macro_name, grains_name = prefix + 'tomoToXRD_stress_all.mat', prefix + 'AllGrains.mat'
            macro_raw, grains_raw = archive.read(macro_name), archive.read(grains_name)
            macro = loadmat(io.BytesIO(macro_raw), simplify_cells=True)
            grains = loadmat(io.BytesIO(grains_raw), simplify_cells=True)['allGrainLoad']
            def record(record_id, columns, rows, member, content, kind, x, y, notes):
                provenance = {k: source[k] for k in ('source_url', 'license', 'license_url', 'attribution')}
                provenance.update(source_id=source['id'], archive=file['filename'], archive_sha256=digest,
                                  member=member, member_sha256=hashlib.sha256(content).hexdigest(),
                                  processor='tools/ingest_hurley.py:3dxrd-v1',
                                  transformations=['MATLAB arrays converted to numeric channels in source order.',
                                                   'Source signs and numeric values retained without stress/strain conversion.',
                                                   'Nonfinite cells remain missing; no stress components are rederived.'],
                                  documentation=source['documentation'])
                return dict(schema_version='0.1', kind=kind, id=record_id,
                            material=f'Hurley sand · {pressure} MPa nominal confinement', protocol='3dxrd-' + kind,
                            conventions=dict(stress='source-defined', strain='source-defined',
                                             stress_unit='per-channel', strain_unit='per-channel'),
                            initial={}, provenance=provenance, columns=columns, rows=rows,
                            source_plot=dict(x=x, y=y), warnings=[
                                'Stress units and tensor sign conventions are not explicitly specified in the enclosed data manual; values remain in native units.',
                                'These are diffraction-derived grain stresses, not load-cell stresses or a normalized model overlay.', *notes])
            names = ['strains', *sorted(k for k in macro if k.startswith('strSamp'))]
            if set(names) != {'strains', 'strSampQ', 'strSampXX', 'strSampXY', 'strSampXZ', 'strSampYY', 'strSampYZ', 'strSampZZ', *(['strSampP'] if pressure != 20 else [])}:
                raise ValueError('Unreviewed Hurley macro channels')
            lengths = {len(macro[k]) for k in names}
            if lengths != {6 if pressure == 20 else 7}:
                raise ValueError('Unaligned Hurley macro channels')
            columns = [dict(key=f'c{i+1}', name=k, unit='native; see data notes') for i, k in enumerate(names)]
            rows = [{c['key']: float(macro[name][j]) for c, name in zip(columns, names)
                     if math.isfinite(float(macro[name][j]))} for j in range(len(macro['strains']))]
            item = record(f'HURLEY-{pressure}-MACRO', columns, rows, macro_name, macro_raw,
                          'measurement-series', 'c1', columns[names.index('strSampQ')]['key'], [
                              'Sample stresses are arithmetic means of grain stress tensors; q is supplied by the authors.',
                              'Macro arrays and grain-load cells have different counts in some files; no row-to-load-step correspondence is inferred.'])
            item['provenance']['tomography_to_xrd_source_mapping'] = [a.tolist() for a in macro['tomoToXRD']]
            records.append(item)
            # Keep each load-cell population separate. Grain rows are not a time
            # history, and grain IDs must not be joined across loads implicitly.
            for step, cells in enumerate(grains, 1):
                if len(cells) != 59 or len({len(c) for c in cells}) != 1:
                    raise ValueError('Unreviewed Hurley grain-cell layout')
                labels = {1:'GrainID', 24:'Fitting confidence', 43:'RMS strain error', 44:'Phase',
                          57:'Paired grain ID', 58:'Twinned crystal flag', 59:'Twin stress difference'}
                for start, stop, label in [(2,10,'Orientation matrix'), (11,13,'Centre position'),
                        (14,19,'Lattice parameter'), (20,22,'MIDAS fit parameter'), (23,23,'Equivalent radius'),
                        (25,33,'Lattice-fit strain'), (34,42,'Scattering-vector-fit strain'),
                        (45,47,'Euler angle'), (48,56,'Sample stress tensor')]:
                    labels.update({i:f'{label} · cell {i}' for i in range(start, stop+1)})
                columns = [dict(key=f'c{i}', name=labels[i], unit='native; see data notes', source_cell=i)
                           for i in range(1,60)]
                rows = [{f'c{i+1}': float(cell[j]) for i, cell in enumerate(cells)
                         if math.isfinite(float(cell[j]))} for j in range(len(cells[0]))]
                item = record(f'HURLEY-{pressure}-GRAINS-{step:02}', columns, rows, grains_name, grains_raw,
                              'test-summary', 'c48', 'c52', [
                                  f'Independent grain population at source allGrainLoad cell {step}; each row is a grain, not a loading increment.',
                                  'Tensor channels retain their original MATLAB cell numbers because the manual component list contains indexing ambiguities.',
                                  'No joining to macro arrays or tomography mapping is performed.'])
                item['provenance']['source_load_cell'] = step
                records.append(item)
    return records
