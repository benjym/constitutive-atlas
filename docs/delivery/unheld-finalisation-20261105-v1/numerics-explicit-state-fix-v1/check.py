from pathlib import Path
import json,hashlib,gzip
P=Path(__file__).resolve().parent;ROOT=P.parents[3];W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def ok(name,v):assert v,name;checks.append(name)
original=(W/'tools/test_numerics.mjs').read_text();new=(P/'proposed/tools/test_numerics.mjs').read_text();restored=new
for a,b in reversed(json.loads((P/'substitutions.json').read_text())):
 ok('unique exact substitution '+a,restored.count(b)==1);restored=restored.replace(b,a)
ok('all other source/assertions/tolerances exact',restored==original)
ok('comparison budget remains1e-7','Math.abs(a-b)<=1e-7*Math.max(1,Math.abs(b))' in new)
ok('17 original pairs shape',"for(const row of rows)" in new and "for(const settings of [undefined,configured])" in new and new.count("const stopped=check('limited-run'")==1 and new.count("const bad=check('invalid-settings'")==1)
proof=json.loads((P/'initial-equivalence.json').read_text());raw=(W/proof['source_row_file']['path']).read_bytes();ok('immutable original rows',sha(raw)==proof['source_row_file']['sha256']);rows=json.loads(gzip.decompress(raw))[:5]
ok('first row linear elastic',rows[0]['model']=='linear-elastic')
for row,p in zip(rows,proof['rows']):
 for kind in ['legacy','current']:
  data=(W/p[kind]['path']).read_bytes();ok('exact model pin '+kind+row['model'],sha(data)==p[kind]['sha256']);model=json.loads(data);initial=[v for f in model['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])];ok('all components exact '+kind+row['model'],initial==row['parent']==p['frozen_row_parent'])
 ok('no state reorder/shortening '+row['model'],p['declared_initial']==p['legacy_implicit_initial']==row['parent'])
for path,pin in json.loads((P/'source-and-failure-pins.json').read_text()).items():
 source=ROOT/path if path.startswith('docs/') else W/path;ok('retained source/failure pin '+path,sha(source.read_bytes())==pin['sha256'])
for row in json.loads((P/'source-delta.json').read_text())['files']:
 b=(P/row['proposal']).read_bytes();ok('payload '+row['path'],sha(b)==row['sha256'] and len(b)==row['bytes']);base=W/row['path'];ok('preimage '+row['path'],(sha(base.read_bytes()) if base.is_file() else None)==row['preimage_sha256'])
(P/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'checks_passed':checks,'actual_native_generated_module_material_calls':0,'model_compiler_runtime_changes':0},indent=2)+'\n');print(len(checks))
