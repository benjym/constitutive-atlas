"""Recover exact existing bytes into OWN packet/private context only."""
from pathlib import Path
import gzip,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3];C=Path('/private/tmp/atlas-bingham-clean-checkout-evidence-v1/tracked-context');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
missing=json.loads((H/'OBSERVED-MISSING.json').read_text());assert len(missing)==7;rows={}
for n,h in missing.items():
 assert n.startswith('catalogue/source-snapshots/'+h+'/') and sha(R/n)==h;assert not (C/n).exists() or sha(C/n)==h
 payload=H/'candidate-bytes'/(h+Path(n).suffix);payload.parent.mkdir(parents=True,exist_ok=True);payload.write_bytes((R/n).read_bytes())
 p=C/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/n).read_bytes())
 rows[n]={'sha256':h,'before_local_sha256':h,'tracked_in_baseline':False,'candidate':'candidate-bytes/'+h+Path(n).suffix,'provenance':str(R/n),'action':'Track existing exact hash-pinned archive member; no source/map/pin changes','ignore_cause':'.gitignore line1 build*/ matches nested build-v1/build-v2 component'}
(H/'INSTALLATION.json').write_text(json.dumps({'baseline_commit':'28d4af2b1d4d6b9c1a58038a8ef9a99ec3279d8c','installed':False,'files':rows,'old_file_changes':0,'requires_independent_review':True,'coordinator_note':'Paths already exist locally but are ignored/untracked. Stage exact approved members explicitly with git add -f; no broad ignore rule change needed. Packet payload files are flat and nonignored; only canonical historical members require explicit force-stage.'},indent=2)+'\n')
