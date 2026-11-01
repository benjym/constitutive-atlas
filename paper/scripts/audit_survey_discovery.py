"""Audit search requests and create an unscreened publication queue."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.survey_discovery import audit_searches, validate_title_screening


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'paper/study/survey_searches.json')
    parser.add_argument('--protocol', type=Path, default=ROOT/'paper/study/survey_protocol.json')
    parser.add_argument('--screening', type=Path, default=ROOT/'paper/study/survey_screening.json')
    parser.add_argument('--discovery-only', action='store_true', help='Audit a fresh retrieval without reusing earlier title decisions')
    parser.add_argument('--output', type=Path, default=ROOT/'paper/results/survey-discovery-audit')
    args = parser.parse_args()
    report = audit_searches(args.manifest, args.protocol)
    queue = report.pop('queue')
    screened = [] if args.discovery_only else validate_title_screening(
        read_json(args.screening), read_json(args.protocol), queue, read_json(args.manifest)['batches'])
    report['screening_ledger_sha256'] = None if args.discovery_only else digest(args.screening)
    report['assisted_title_pilot'] = dict(decisions=len(screened),
        by_decision=dict(Counter(r['decision'] for r in screened)),
        remaining_without_title_decision=len(queue)-len(screened),
        qualification='Purposeful title-only pilot; no exact formulation admission or independent review.')
    by_id = {r['publication_id']: r for r in screened}
    for record in queue:
        if record['publication_id'] in by_id:
            record['stage'] = 'title_abstract'
            record['screening_decisions'] = [by_id[record['publication_id']]]
    write_json(args.output/'report.json', report)
    with (args.output/'publication-queue.jsonl').open('w') as file:
        for record in queue:
            file.write(json.dumps(record, allow_nan=False)+'\n')
    lines = ['# Bounded discovery audit', '', 'Bibliographic queue with an assisted title-only pilot; not the formulation survey.', '']
    lines += [f'- {key}: {value}' for key, value in report['counts'].items()]
    lines += ['', f"Assisted title decisions: {len(screened)}; remaining without a title decision: {len(queue)-len(screened)}."]
    lines += [f'- {key}: {value}' for key, value in report['assisted_title_pilot']['by_decision'].items()]
    lines += ['', '| Theme | Returned records | Finite descending scores |', '| --- | ---: | --- |']
    lines += [f"| {r['id']} | {r['returned_records']} | {r['finite_descending_scores']} |" for r in report['batch_checks']]
    lines += ['']+['- '+s for s in report['limits']]
    (args.output/'report.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
