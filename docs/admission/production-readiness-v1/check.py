"""Read-only admission packet preflight; integrity success never supplies admission."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result

    def finite(token):
        value = float(token)
        if not math.isfinite(value):
            raise ValueError('nonfinite JSON number')
        return value

    def reject(token):
        raise ValueError('invalid JSON constant: ' + token)

    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_float=finite, parse_constant=reject)


def within(root, name):
    path = Path(name)
    resolved = (root / path).resolve()
    if path.is_absolute() or '..' in path.parts or not resolved.is_relative_to(root.resolve()):
        raise ValueError('unsafe packet input path: ' + name)
    return resolved


def require(condition, message):
    if not condition:
        raise ValueError(message)


def assess(root, work, decisions):
    root = Path(root).resolve()
    require(work['version'] == 'production-readiness-work-packages-v1', 'wrong packet version')
    require(work['kind'] == 'unsigned_admission_work_packages', 'wrong packet kind')
    require(work['compiled_execution_authorized_by_this_packet'] is False, 'packet cannot authorize execution')
    require(work['status_promotion_authorized_by_this_packet'] is False, 'packet cannot authorize promotion')
    require(decisions['kind'] == 'unsigned_decision_template_not_a_canonical_review', 'wrong decision kind')
    for field in ('reviewer', 'reviewed_at', 'independence_statement'):
        require(decisions[field] is None, 'frozen unsigned template was signed in place')
    for name, expected in work['inputs'].items():
        actual = hashlib.sha256(within(root, name).read_bytes()).hexdigest()
        require(actual == expected, 'pinned input changed: ' + name)

    summaries = []
    seen = set()
    all_decisions = set()
    for package in work['models']:
        mid = package['model_id']
        require(mid not in seen, 'duplicate model package')
        seen.add(mid)
        definition = package['definition']
        model = read_json(within(root, definition['path']))
        require(definition['path'] in work['inputs'], 'definition not pinned')
        require(work['inputs'][definition['path']] == definition['sha256'], 'inconsistent definition hash')
        require(model['id'] == mid and model['status'] == definition['status'], 'model status/id changed')
        require(model['schema_version'] == definition['schema_version'], 'model schema changed')
        review_ref = package['pending_review']
        review = read_json(within(root, review_ref['path']))
        require(work['inputs'].get(review_ref['path']) == review_ref['sha256'], 'review not pinned')
        require(review['model'] == {'id': mid, 'definition_sha256': definition['sha256']}, 'stale review binding')
        require(review['status'] == 'pending' and review['independent'] is False and review['unresolved'],
                'pending review was promoted or emptied in place')
        require(package['scientific_reviewer'] is None and package['scientific_review_complete'] is False,
                'unsigned work package claims scientific acceptance')
        require(package['release_attestation'] is None, 'release attestation must be a separately reviewed output')
        scope = package['proposed_scope']
        for field in ('experimental_validation', 'finite_element_host_qualification', 'universal_convergence'):
            require(scope[field] is False, 'unsupported scope promotion: ' + field)
        for ref in package['evidence']:
            require(ref['path'] in work['inputs'], 'evidence not pinned')
            evidence = read_json(within(root, ref['path']))
            require(evidence['model'] == review['model'], 'evidence is not current-definition evidence')
            require(evidence['id'] == ref['id'] and evidence['outcome'] == ref['outcome'], 'evidence identity changed')
            for artifact in evidence['artifacts']:
                require(work['inputs'].get(artifact['path']) == artifact['sha256'], 'artifact not bound to original evidence')
        answers = decisions['answers'][mid]
        ids = [a['id'] for a in answers]
        require(ids == package['decision_ids'] and len(ids) == len(set(ids)), 'decision list changed/duplicated')
        require(not all_decisions.intersection(ids), 'duplicate decision across models')
        all_decisions.update(ids)
        for answer in answers:
            for field in ('decision', 'rationale', 'reviewer', 'reviewed_at'):
                require(answer[field] is None, 'unsigned decision template changed in place')
            for name in answer['evidence']:
                require(name in work['inputs'], 'decision evidence missing from pins')
        summaries.append({'model_id': mid, 'definition_sha256': definition['sha256'],
                          'review_binding': 'exact_current_definition',
                          'unsigned_decisions': ids, 'scientific_review': 'pending_unassigned',
                          'release_attestation': 'absent', 'admission': 'blocked'})

    require(seen == set(decisions['answers']), 'extra/missing decision sheet')
    # The DP source crosswalk names the preserved pre-guard definition. Verify
    # its exact supersession instead of changing the historical crosswalk hash.
    packet = 'catalogue/investigations/dp-dilatancy-domain-v1/'
    before_path, after_path = packet + 'previous-definition.json', packet + 'candidate-definition.json'
    before, after = read_json(within(root, before_path)), read_json(within(root, after_path))
    current = read_json(root / 'models/drucker-prager.json')
    crosswalk = read_json(root / 'docs/ingestion/drucker-prager/formulation-crosswalk.json')
    require(crosswalk['root_definition_sha256'] == work['inputs'][before_path], 'DP source crosswalk lost prior identity')
    require(current == after, 'current DP is not the exact approved candidate')
    require(after['domain'] == before['domain'] + ['Md <= M'], 'unexpected DP domain correction')
    require({k: v for k, v in before.items() if k != 'domain'} ==
            {k: v for k, v in after.items() if k != 'domain'}, 'DP correction changed constitutive equations')
    return {'version': 'production-readiness-preflight-v1', 'packet_integrity': 'passed',
            'pinned_input_count': len(work['inputs']), 'unsigned_decision_count': len(all_decisions),
            'dp_historical_crosswalk_supersession': 'verified_exact_guard_only',
            'models': summaries, 'scientific_admission': 'blocked',
            'compiled_calls': 0, 'model_or_review_writes': 0,
            'next_action': 'Agree an independent reviewer and answer the exact-definition decision sheets; then freeze a new reviewed release qualification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--require-admitted', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = assess(args.repo, read_json(HERE / 'work-packages.json'),
                    read_json(HERE / 'decisions-template.json'))
    output = json.dumps(result, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(output)
    else:
        print(output, end='')
    return 2 if args.require_admitted and result['scientific_admission'] != 'admitted' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print('Admission packet preflight failed: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
