"""Unchanged original saved-data assessors only. Never call a material engine."""
from pathlib import Path
import argparse,importlib.util,json
N=Path('docs/delivery/unheld-finalisation-20261105-v1').resolve();P=N/'rate-restoration-qualification-plan-v3';A=N/'rate-restoration-qualification-actual-v3';Q=N/'shared-current17-review-v1/C-runtime-actual-v3'
spec=importlib.util.spec_from_file_location('_review_C_actual_collector',P/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Original assess_pair uses Replay for all original requests, and the unchanged
# DP --replay saved-data assessor in a removed TemporaryDirectory. No Transport.
m.M.assess_pair(argparse.Namespace(native=A/'native',wasm=A/'wasm',output=Q/'original-pair-replay.json'))
assert json.loads((Q/'original-pair-replay.json').read_text())==json.loads((A/'pair.json').read_text())
print('Original saved-data701/interface/DP/pair reassessment exact PASS; no material calls')
