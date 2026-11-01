"""Check the public implicit-path route, exact assets and database without material calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

MODEL = 'lade-duncan-1975-midpoint-elastic-eq19-gap-v4'
MODEL_SHA = '120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
WITNESSES = {'lade-duncan-1975-local-eq19-gap-be-v2', 'hypoplastic-sand-vw96', 'linear-elastic'}
COMPONENTS = {f'implicit-path-{name}.mjs' for name in ('contract', 'engine', 'runner', 'worker', 'laboratory')}
GATES = {'interpreter', 'helpers', 'native_triaxial', 'native_fixed', 'native_domain',
         'native_lifecycle', 'native_legacy', 'native_supplement', 'wasm_parity', 'wasm_chains', 'wasm_source'}


def check(directory):
    directory = Path(directory).resolve()
    checks = []

    def require(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise ValueError(name)

    def read(name):
        path = (directory / name).resolve()
        require('safe existing package path: ' + name,
                not Path(name).is_absolute() and '..' not in Path(name).parts
                and path.is_relative_to(directory) and path.is_file())
        return path.read_bytes()

    def data(name):
        return json.loads(read(name))

    def digest(value):
        return hashlib.sha256(value).hexdigest()

    prefix = 'engine-implicit-path/'
    manifest = data(prefix + 'package-manifest.json')
    require('main-atlas manifest kind', manifest.get('kind') == 'implicit-path-main-atlas-1')
    expected = COMPONENTS | {prefix + name for name in (
        'lade-domain.mjs', 'lade-domain.wasm', 'models.json', MODEL + '.json', 'approval.json',
        'review.json', 'review.html', 'qualification.json', 'build-review.json',
        'interface-review.json', 'source-manifest.json', 'identity.json')}
    require('complete exact profile asset set', set(manifest['files']) == expected)
    for name, pin in manifest['files'].items():
        require('exact packaged hash: ' + name, digest(read(name)) == pin)
    actual = {p.relative_to(directory).as_posix() for p in (directory / prefix).rglob('*') if p.is_file()}
    require('no stale profile assets', actual == (expected - COMPONENTS) | {prefix + 'package-manifest.json'})
    identity = data(prefix + 'identity.json')
    definition = data(prefix + MODEL + '.json')
    catalogue = data(prefix + 'models.json')
    require('exact public model and profile', identity['model'] == MODEL and identity['profile'] == 'implicit-path-v1'
            and identity['model_sha256'] == MODEL_SHA and identity['public_models'] == [MODEL]
            and definition['id'] == MODEL and digest(read(prefix + MODEL + '.json')) == MODEL_SHA)
    require('complete internal regression catalogue', [m['id'] for m in catalogue['models']] ==
            [MODEL, 'lade-duncan-1975-local-eq19-gap-be-v2', 'hypoplastic-sand-vw96', 'linear-elastic']
            and catalogue['models'][0] == definition and catalogue['sha256'] == identity['catalogue_hash'])
    for field, filename in [('catalogue_file_sha256', 'models.json'), ('module_sha256', 'lade-domain.mjs'),
                            ('wasm_sha256', 'lade-domain.wasm'), ('approval_sha256', 'approval.json'),
                            ('review_sha256', 'review.json'), ('review_html_sha256', 'review.html'),
                            ('qualification_sha256', 'qualification.json'), ('build_review_sha256', 'build-review.json'),
                            ('interface_review_sha256', 'interface-review.json')]:
        require('identity bound asset: ' + field, identity[field] == digest(read(prefix + filename)))
    require('complete component pins', set(identity['component_sha256']) == COMPONENTS)
    for name in COMPONENTS:
        require('identity component: ' + name, identity['component_sha256'][name] == digest(read(name)))
    qualification = data(prefix + 'qualification.json')
    accepted = data(prefix + 'build-review.json')
    require('all eleven qualified gates', qualification['status'] == 'passed' and set(qualification['gates']) == GATES
            and all(v is True for v in qualification['gates'].values()))
    require('actual separate accepted numerical reviewer', accepted['status'] == 'accepted'
            and accepted['gates'] == qualification['gates'] and accepted['binding'] == qualification['binding']
            and bool(accepted['reviewer_run']) and accepted['reviewer_run'] != qualification['implementation_run'])
    require('runtime source binding', data(prefix + 'source-manifest.json')['sha256'] == identity['runtime_sha256']
            == qualification['binding']['runtime_sha256'])
    review, approval = data(prefix + 'review.json'), data(prefix + 'approval.json')
    require('exact scientific approval', review['status'] == 'accepted' and review['model']['id'] == MODEL
            and review['model']['sha256'] == MODEL_SHA and approval['status'] == 'approved'
            and approval['model_id'] == MODEL and approval['definition']['sha256'] == MODEL_SHA
            and approval['review']['sha256'] == identity['review_sha256'])
    require('all nine scientific decisions', len(review['checklist']) == 9
            and all(c['outcome'] in ('pass', 'not-applicable') for c in review['checklist'])
            and review['blocking_findings'] == [])
    ordinary = data('models.json')['models']
    require('special model absent ordinary engine', MODEL not in {m['id'] for m in ordinary})
    discovery = data('catalogue.json')['models']
    entries = [m for m in discovery if m['id'] == MODEL]
    require('exact discoverable special route', len(entries) == 1 and entries[0].get('implicit_path_laboratory') == 'index.html'
            and entries[0].get('executable') is False)
    require('historical witness not public', not any(m['id'] == 'lade-duncan-1975-local-eq19-gap-be-v2' for m in discovery))
    app = read('app.js').decode()
    require('main application imports and registers controller', "from './implicit-path-laboratory.mjs'" in app
            and 'setupImplicitPathLaboratory({chart,' in app)
    dossier = entries[0]['dossier']
    require('source dossier packaged', bool(read(dossier)) and bool(read(dossier + '.html')))
    with sqlite3.connect('file:' + str(directory / 'atlas.sqlite') + '?mode=ro', uri=True) as database:
        row = database.execute('SELECT executable,definition_json FROM models WHERE id=?', (MODEL,)).fetchone()
        require('database exact research definition', row is not None and row[0] == 0 and json.loads(row[1]) == definition)
        row = database.execute('SELECT definition_sha256,record_json FROM model_approvals WHERE model_id=?', (MODEL,)).fetchone()
        require('database exact approval', row is not None and row[0] == MODEL_SHA and json.loads(row[1]) == approval)
        row = database.execute('SELECT sha256,record_json FROM agent_reviews WHERE model_id=?', (MODEL,)).fetchone()
        require('database exact independent review', row is not None and row[0] == identity['review_sha256'] and json.loads(row[1]) == review)
        require('database original source identity', database.execute(
            'SELECT count(*) FROM sources WHERE model_id=? AND url=?',
            (MODEL, 'https://doi.org/10.1061/AJGEB6.0000204')).fetchone()[0] > 0)
        require('database original publication mapping', database.execute(
            'SELECT count(*) FROM publication_models WHERE model_id=? AND publication_id=?',
            (MODEL, 'doi:10.1061/ajgeb6.0000204')).fetchone()[0] == 1)
    return {'status': 'passed', 'checks': checks,
            'scope': 'Packaged byte, discovery, main-route wiring and database checks; no material or actual browser execution'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Refusing to overwrite package evidence')
    try:
        report = check(args.directory)
    except Exception as failure:
        args.output.write_text(json.dumps({'status': 'failed', 'error': str(failure)}, indent=2) + '\n')
        raise
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS:', len(report['checks']), 'implicit-path package checks')
