"""One original finite audit replay per test process; no compiled execution."""
from functools import lru_cache
import json
from pathlib import Path
from atlas.source_replay import registered
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def original_families():
    result=registered(ROOT,'catalogue/source-replays/finite-tensor-v1/registry.json','finite-tensor',timeout=600)
    summary=json.loads(result['stdout'])
    if summary['clay_original_outcome']!='failed' or summary['clay_controlled_outcome']!='passed' or summary['original_failed_study_replaced']:
        raise AssertionError('original finite outcomes relabelled')
    if summary['compiled_execution'] or summary['admission']:
        raise AssertionError('replay scope changed')
    return {row['family']:row for row in summary['families']}
