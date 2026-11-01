"""Independently verify Chang MAT numeric blocks and published boundary units.

Uses SciPy's subsystem matrix reader separately from the ingestion decoder.
Pass --curated after ingestion to compare every retained numeric cell and row.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.ingest_chang_mat import decode_table


def verify(raw_dir, *, curated=False):
    import numpy as np
    import openpyxl
    from scipy.io import loadmat
    from scipy.io.matlab._mio5 import MatFile5Reader

    registry = json.loads((ROOT/'data/public_sources.json').read_text())['sources']
    config = next(s for s in registry if s['id'] == 'chang-creep-raw')
    summary_config = next(s for s in registry if s['id'] == 'chang-creep-summary')['files'][0]
    raw_summary = (raw_dir/summary_config['filename']).read_bytes()
    assert hashlib.sha256(raw_summary).hexdigest() == summary_config['sha256']
    workbook = openpyxl.load_workbook(io.BytesIO(raw_summary), read_only=True, data_only=True)
    summary = list(workbook.active.values)
    workbook.close()
    assert '(s)' in summary[1][6] and '(s)' in summary[1][7]
    assert '(mm)' in summary[1][8] and '(mm)' in summary[1][9]
    entries = json.loads((ROOT/'data/curated/index.json').read_text())['records'] if curated else []
    checks = []
    tolerance = 1e-8  # Frozen in the pre-ingestion source-boundary audit.
    for file in config['files']:
        path = raw_dir/file['filename']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == file['sha256']
        source = loadmat(path)
        stream = io.BytesIO(source['__function_workspace__'].tobytes())
        assert stream.read(8) == b'\x00\x01IM\x00\x00\x00\x00'
        reader = MatFile5Reader(stream, byte_order='<')
        reader.initialize_read()
        header, _ = reader.read_var_header()
        subsystem = reader.read_var_array(header, False)
        wrapper = subsystem['MCOS'][0, 0]
        assert wrapper['s2'][0] == b'FileWrapper__'
        slots = wrapper['arr'][0].ravel()
        assert len(slots) == 12
        arrays = slots[2].ravel()
        names = [str(v.item()) for v in slots[7].ravel()]
        decoded_names, decoded_arrays, _, _, _ = decode_table(path)
        assert decoded_names == names == file['columns']
        assert len(arrays) == len(decoded_arrays)
        for a, b in zip(arrays, decoded_arrays):
            assert np.array_equal(a.ravel(), b, equal_nan=True)
        rows = int(slots[4].item())
        assert rows == file['expected_observations']
        assert all(a.shape == (rows, 1) for a in arrays)
        number = file['experiment_number']
        sr = summary[number+1]
        assert sr[0] == '#'+str(number)
        metadata = source['iExpEntry']
        time = arrays[0].ravel()
        slip = arrays[file['slip_column']-1].ravel()
        anchors = []
        for tk, sk, ti, si in [('TimeStart', 'PreShearedDspl', 6, 8), ('TimeEnd', 'FailureDspl', 7, 9)]:
            target = float(metadata[tk][0, 0].item())
            target_slip = float(metadata[sk][0, 0].item())
            near = int(np.argmin(abs(time-target)))
            errt, errs = float(time[near]-target), float(slip[near]-target_slip)
            assert abs(errt) <= tolerance and abs(errs) <= tolerance
            assert abs(target-sr[ti]) <= tolerance and abs(target_slip-sr[si]) <= tolerance
            anchors.append(dict(time_field=tk, slip_field=sk, matlab_row=near+1,
                                time_error_s=errt, slip_error_mm=errs))
        record_count = 0
        if curated:
            matching = sorted([e for e in entries if e['id'].startswith('CHANG-CREEP-RAW-'+str(number).zfill(2)+'-')], key=lambda e:e['id'])
            offset = 0
            for entry in matching:
                packed = (ROOT/'data/curated'/entry['path']).read_bytes()
                assert hashlib.sha256(packed).hexdigest() == entry['sha256']
                record = json.loads(gzip.decompress(packed))
                n = len(record['rows'])
                assert record['kind'] == 'measurement-series'
                assert record['provenance']['source_rows'] == list(range(offset+1, offset+n+1))
                assert record['provenance']['archive_sha256'] == file['sha256']
                for i, array in enumerate(arrays, 1):
                    actual = np.array([r.get('c'+str(i), np.nan) for r in record['rows']])
                    native = np.array([np.nan if r[i] is None else r[i] for r in record['source_table']['values']])
                    expected = array.ravel()[offset:offset+n]
                    assert np.array_equal(actual, expected, equal_nan=True)
                    assert np.array_equal(native, expected, equal_nan=True)
                offset += n
                record_count += 1
            assert offset == rows
        checks.append(dict(experiment=number, filename=file['filename'], sha256=file['sha256'],
                           observations=rows, channels=len(names), numeric_cells_compared=rows*len(names),
                           curated_records_checked=record_count, anchors=anchors, result='pass'))
        print('Verified experiment', number, file=sys.stderr, flush=True)
    assert len(checks) == 40 and {c['experiment'] for c in checks} == set(range(1, 41))
    return dict(format='atlas-chang-source-verification-v1', anchor_tolerance_s_and_mm=tolerance,
                curated_checked=curated, checks=checks, result='pass')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', required=True, type=Path)
    parser.add_argument('--curated', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = verify(args.raw_dir, curated=args.curated)
    data = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    if args.output:
        args.output.write_text(data)
    else:
        print(data)


if __name__ == '__main__':
    main()
