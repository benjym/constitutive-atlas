"""Capture current normal compiler/database exporter output; no engine execution."""
from pathlib import Path
import hashlib,json,shutil,sqlite3,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from atlas.compiler import generate
from build_database import bundle
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
output=HERE/'baseline';output.mkdir(exist_ok=False)
generate(output);shutil.copyfile(ROOT/'catalogue/manifest.json',output/'catalogue.json');package=bundle(output)
with sqlite3.connect(output/'atlas.sqlite') as db:
 db.row_factory=sqlite3.Row
 names=sorted(row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
 tables={name:[dict(row) for row in db.execute('SELECT * FROM '+name)] for name in names}
ordinary=json.loads((output/'models.json').read_text())
record={'identity':'bingham-current-atlas-baseline-e6f06114-v3','base_commit':'e6f06114','compiled_observations':False,'ordinary_catalogue':ordinary,'ordinary_catalogue_sha256':sha(output/'models.json'),'tables':tables,'counts':{name:len(rows) for name,rows in tables.items()},'database_package':package,'source_only':True}
(HERE/'baseline-public-records.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'ordinary_models':len(ordinary['models']),'counts':record['counts'],'source_only':True,'material_calls':0},indent=2))
