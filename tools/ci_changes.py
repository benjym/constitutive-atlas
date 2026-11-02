"""Fail closed on unknown changes; skip compiled smoke only for prose/media edits."""
import json
import os
from pathlib import Path, PurePosixPath
import subprocess


def needs_numerical(paths):
    # Evidence JSON, model definitions, study code and engine archives are not prose.
    return any(PurePosixPath(p).suffix.lower() not in
               {'.md', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.pdf'}
               or p.startswith(('cpp/', 'atlas/', 'models/', 'schemas/', 'cmake/', '.github/', 'tests/', 'tools/'))
               for p in paths)


def changed_paths(event, name):
    if name == 'pull_request':
        base, head = event['pull_request']['base']['sha'], event['pull_request']['head']['sha']
        revisions = [base + '...' + head]
    elif name == 'push' and event.get('before', '').strip('0'):
        revisions = [event['before'], event['after']]
    else:
        return None  # manual runs, new branches and unknown events run the smoke
    try:
        result = subprocess.run(['git', 'diff', '--name-only', '-z', *revisions, '--'],
                                check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return None  # missing history must never silently skip checks
    return [p for p in result.stdout.decode().split('\0') if p]


def main():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    paths = changed_paths(event, os.environ['GITHUB_EVENT_NAME'])
    numerical = paths is None or needs_numerical(paths)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write('numerical=' + str(numerical).lower() + '\n')
    print('Compiled smoke:', 'required' if numerical else 'prose/media only; skipped')


if __name__ == '__main__':
    main()
