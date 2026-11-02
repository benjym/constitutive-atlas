"""Collect terminal exact-revision CI/Pages receipts and authenticated upload bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
POLICY = json.loads((HERE / 'LIVE-POLICY.json').read_text())

def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', 'repos/benjym/constitutive-atlas/' + path]))

def save(folder, name, data):
    (folder / name).write_text(json.dumps(data, indent=2) + '\n')
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = dict(passed=False, release=POLICY['release'], run=POLICY['run'])
    try:
        run = save(args.output, 'VERIFY-RUN.json', api('actions/runs/' + str(POLICY['run'])))
        assert run['head_sha'] == POLICY['release'] and run['head_branch'] == 'main'
        assert run['status'] == 'completed' and run['conclusion'] == 'success'
        jobs = save(args.output, 'VERIFY-JOBS.json', api('actions/runs/' + str(POLICY['run']) + '/jobs?per_page=100'))
        assert jobs['total_count'] == len(jobs['jobs']) == 6
        assert {j['name'] for j in jobs['jobs']} == {'native (ubuntu-latest, 3.12)', 'native (macos-26, 3.14)', 'wasm', 'wasm-linux', 'controlled-path', 'deploy'}
        assert all(j['status'] == 'completed' and j['conclusion'] == 'success' for j in jobs['jobs'])
        controlled = save(args.output, 'CONTROLLED-RUN.json', api('actions/runs/' + str(POLICY['require_controlled_run_success'])))
        assert controlled['head_sha'] == POLICY['release']
        assert controlled['status'] == 'completed' and controlled['conclusion'] == 'success'
        pages = save(args.output, 'PAGES.json', api('pages'))
        assert pages['html_url'] == POLICY['base'] and pages['build_type'] == 'workflow'
        deployments = save(args.output, 'DEPLOYMENTS.json', api('deployments?sha=' + POLICY['release'] + '&environment=github-pages&per_page=100'))
        matched = []
        for deployment in deployments:
            assert deployment['sha'] == POLICY['release'] and deployment['environment'] == 'github-pages'
            statuses = save(args.output, 'DEPLOYMENT-' + str(deployment['id']) + '-STATUSES.json', api('deployments/' + str(deployment['id']) + '/statuses?per_page=100'))
            if statuses and statuses[0]['state'] == 'success' and str(POLICY['run']) in statuses[0]['log_url']:
                matched.append(deployment['id'])
        assert matched, 'No successful exact-run Pages deployment'
        inventory = save(args.output, 'ARTIFACTS.json', api('actions/runs/' + str(POLICY['run']) + '/artifacts?per_page=100'))
        assert inventory['total_count'] == len(inventory['artifacts'])
        candidates = [x for x in inventory['artifacts'] if x['name'] == 'github-pages']
        assert len(candidates) == 1
        metadata = save(args.output, 'UPLOAD-METADATA.json', candidates[0])
        assert not metadata['expired'] and metadata['workflow_run']['head_sha'] == POLICY['release']
        archive = args.private / 'github-pages-106a9cf8.zip'
        assert not archive.exists()
        with archive.open('xb') as stream:
            subprocess.run(['gh', 'api', 'repos/benjym/constitutive-atlas/actions/artifacts/' + str(metadata['id']) + '/zip'], stdout=stream, check=True)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        assert metadata['digest'] == 'sha256:' + digest
        result.update(passed=True, all_six_jobs_success=True, controlled_success=True,
                      pages_deployments=matched, archive=str(archive), archive_sha256=digest,
                      archive_bytes=archive.stat().st_size, artifact_id=metadata['id'])
    except Exception as error:
        result['error'] = repr(error)
        raise
    finally:
        save(args.output, 'RESULT.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
