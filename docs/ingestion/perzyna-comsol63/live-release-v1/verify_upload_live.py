from pathlib import Path, PurePosixPath
import argparse, collections, concurrent.futures, hashlib, json, sqlite3
import tarfile, time, urllib.parse, urllib.request, zipfile

HERE = Path(__file__).resolve().parent
POLICY = json.loads((HERE / 'LIVE-POLICY.json').read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def verify(archive, metadata, output):
    output.mkdir(parents=True, exist_ok=False)
    result = {'passed': False, 'release': POLICY['release'], 'run': POLICY['run']}
    try:
        assert metadata['name'] == 'github-pages' and not metadata['expired']
        assert metadata['workflow_run']['head_sha'] == POLICY['release']
        assert metadata['digest'] == 'sha256:' + sha(archive.read_bytes())
        assert sha((HERE / 'PRIOR-DATABASE-ROW-BAGS.json').read_bytes()) == POLICY['prior_database_bags_sha256']
        files, kept = {}, {}
        keep = set(POLICY['critical_local_hashes']) | {'engine-perzyna/identity.json', 'atlas.sqlite', 'atlas-database.json'}
        with zipfile.ZipFile(archive) as zipped:
            members = [x for x in zipped.infolist() if not x.is_dir()]
            assert len(members) == 1 and members[0].filename == 'artifact.tar'
            with zipped.open(members[0]) as stream, tarfile.open(fileobj=stream, mode='r|*') as tar:
                for member in tar:
                    path = PurePosixPath(member.name)
                    assert not path.is_absolute() and '..' not in path.parts
                    if member.isdir():
                        continue
                    assert member.isfile(), member.name
                    name = path.as_posix()
                    assert name not in files, name
                    data = tar.extractfile(member).read()
                    files[name] = {'sha256': sha(data), 'bytes': len(data)}
                    if name in keep:
                        kept[name] = data
        (output / 'UPLOAD-MANIFEST.json').write_text(json.dumps({'artifact': metadata, 'files': files}, indent=2) + '\n')
        assert sha((HERE.parent / 'package-v2/PACKAGE-MANIFEST.json').read_bytes()) == POLICY['local_package_manifest_sha256']
        local = json.loads((HERE.parent / 'package-v2/PACKAGE-MANIFEST.json').read_text())['files']
        def public(name):
            return not any(p.startswith('.') for p in PurePosixPath(name).parts) and not name.startswith('implicit-path-package-checks/')
        assert {n for n in files if public(n)} == {n for n in local if public(n)}
        for name, expected in POLICY['critical_local_hashes'].items():
            assert files[name]['sha256'] == expected, 'Changed tested input: ' + name
        identity = json.loads(kept['engine-perzyna/identity.json'])
        assert identity['release_revision'] == POLICY['release']
        assert identity['model'] == 'perzyna-comsol63-mises-perfect-zero-spin-ode'
        assert identity['model_sha256'] == '7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac'
        manifest = json.loads(kept['atlas-database.json'])
        assert manifest['counts'] == POLICY['expected_database_counts']
        assert sha(kept['atlas.sqlite']) == manifest['database']['sha256']
        database = output / 'upload-atlas.sqlite'
        database.write_bytes(kept['atlas.sqlite'])
        previous = json.loads((HERE / 'PRIOR-DATABASE-ROW-BAGS.json').read_text())['tables']
        connection = sqlite3.connect('file:' + str(database.resolve()) + '?mode=ro', uri=True)
        assert connection.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
        assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
        preserved = {}
        for table, before in previous.items():
            quoted = '"' + table.replace('"', '""') + '"'
            columns = [x[1] for x in connection.execute('PRAGMA table_info(' + quoted + ')')]
            assert columns == before['columns']
            rows = list(connection.execute('SELECT * FROM ' + quoted))
            hashes = collections.Counter(sha(json.dumps(row, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode()) for row in rows)
            assert not (collections.Counter(before['hash_counts']) - hashes), table
            preserved[table] = {'prior_rows': before['row_count'], 'current_rows': len(rows), 'all_prior_rows_preserved': True}
        connection.close()
        result.update(upload_files=len(files), critical_tested_inputs=len(POLICY['critical_local_hashes']), database_counts=manifest['counts'], prior_table_bags=preserved)

        selected = {name: item for name, item in files.items()
                    if public(name) and (not name.startswith('experiments/') or name == 'experiments/manifest.json')}
        def check(item):
            name, expected = item
            attempts = []
            for attempt in range(POLICY['http_attempts']):
                record = {'attempt': attempt + 1}
                try:
                    request = urllib.request.Request(POLICY['base'] + urllib.parse.quote(name, safe='/') + '?release=' + POLICY['release'], headers={'Cache-Control': 'no-cache', 'User-Agent': 'Constitutive-Atlas-delivery-verification'})
                    with urllib.request.urlopen(request, timeout=POLICY['http_timeout_seconds']) as response:
                        data = response.read()
                        record.update(status=response.status, sha256=sha(data), bytes=len(data))
                    record['matches'] = record['status'] == 200 and record['sha256'] == expected['sha256'] and record['bytes'] == expected['bytes']
                except Exception as error:
                    record.update(matches=False, error=repr(error))
                attempts.append(record)
                if record['matches']:
                    break
                time.sleep(0.5 * (attempt + 1))
            return name, {'expected': expected, 'attempts': attempts, 'matches': attempts[-1]['matches']}
        with concurrent.futures.ThreadPoolExecutor(max_workers=POLICY['http_concurrency']) as pool:
            checked = dict(pool.map(check, sorted(selected.items())))
        (output / 'HTTP-ASSETS.json').write_text(json.dumps(checked, indent=2) + '\n')
        result.update(http_assets=len(checked), http_all_exact=all(x['matches'] for x in checked.values()))
        assert result['http_all_exact']
        result['passed'] = True
    except Exception as error:
        result['error'] = repr(error)
        raise
    finally:
        (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--metadata', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, json.loads(args.metadata.read_text()), args.output), indent=2))
