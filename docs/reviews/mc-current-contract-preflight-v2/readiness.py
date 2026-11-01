"""Admission-to-build gate, separate from reproducing a saved failed study."""
from pathlib import Path
import json,sys
r=json.loads((Path(__file__).resolve().parent/'consumer-results.json').read_text())
if not r['passed']:
    print(f"NOT READY: {len(r['false_passes'])} document-parser false passes; no compiled observation authorized by this preflight.")
    sys.exit(1)
print('Document preflight passed; independent final source/collector/freeze audit still required before a build.')
