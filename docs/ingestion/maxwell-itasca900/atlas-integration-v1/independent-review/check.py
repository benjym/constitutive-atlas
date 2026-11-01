"""Pure static/source-preservation checks; no package build or compiled execution."""
import ast,difflib,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'docs/ingestion/maxwell-itasca900/atlas-integration-v1'
sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
pins=load(BASE/'integration-bindings.json');old={};current={}
for name,h in pins['before'].items():
 p=ROOT/'catalogue/source-snapshots'/h/name;assert sha(p.read_bytes())==h;old[name]=p.read_text()
 assert checked_receipt(ROOT,str((BASE/'integration-bindings.json').relative_to(ROOT)),name,h)==p
for name,h in pins['after'].items():
 current[name]=(ROOT/name).read_text();assert sha((ROOT/name).read_bytes())==h
app=current['web/app.js'];assert app.count("import {setupMaxwellLaboratory} from './maxwell-laboratory.mjs';\n")==1
assert app.replace("import {setupMaxwellLaboratory} from './maxwell-laboratory.mjs';\n",'').replace(",setupMaxwellLaboratory({chart,cancelOrdinary:()=>cancel('')})",'')==old['web/app.js']
builder=current['tools/build_web.py'];addition="    parser.add_argument('--maxwell-wasm-dir',type=Path,default=ROOT/'build-maxwell-wasm',help='Dedicated Maxwell engine with exact accepted current-build qualification receipt')\n"
assert builder.count(addition)==1
assert builder.replace(addition,'').replace('    from build_maxwell_laboratory import bundle as bundle_maxwell\n    bundle_maxwell(dest,args.maxwell_wasm_dir)\n','')==old['tools/build_web.py']
ast.parse(builder)
subprocess.run(['node','--check',str(ROOT/'web/app.js')],check=True)
manifest=json.loads(current['catalogue/manifest.json']);prior=json.loads(old['catalogue/manifest.json']);mid='maxwell-itasca900-zero-spin-ode';new=[m for m in manifest['models'] if m['id']==mid];assert len(new)==1;entry=new[0]
manifest['models'].remove(entry);assert manifest==prior
model=load(ROOT/'models/research/maxwell'/f'{mid}.json');assert entry['catalogue_sources']==model['sources'];assert entry['status']=='reviewed' and entry['timed_laboratory']=='index.html' and entry['executable'] is False
assert (ROOT/entry['dossier']).is_file();assert sha((ROOT/'models/research/maxwell'/f'{mid}.json').read_bytes())=='dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f'
patch=''.join(''.join(difflib.unified_diff(old[n].splitlines(True),current[n].splitlines(True),fromfile='prior/'+n,tofile='current/'+n)) for n in ['web/app.js','tools/build_web.py','catalogue/manifest.json'])
assert patch==(BASE/'integration.patch').read_text()
before=load(BASE/'frozen/bindings-before.json');pres=load(BASE/'preservation.json');assert len(pres['bindings'])==7 and len(pres['changed_sidecars'])==3
for row in pres['bindings']:
 assert sha((ROOT/row['archived_path']).read_bytes())==row['sha256']
 assert checked_receipt(ROOT,row['document'],row['original_path'],row['sha256'])==ROOT/row['archived_path']
 pin=next(x['document_sha256'] for x in before['primary_references'] if x['document']==row['document']);assert sha((ROOT/row['document']).read_bytes())==pin
# Confirm no previously resolved binding is lost, across both source and sidecar references.
spec=importlib.util.spec_from_file_location('integration_scanner',BASE/'scan.py');scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner);scanner.TARGETS=set(pins['before']);now=scanner.scan(ROOT);counts={}
for group in ['primary_references','secondary_source_map_references']:
 index={(x['document'],x['original_path'],x['sha256']):x for x in now[group]};good=[x for x in before[group] if x['resolution']!='unresolved']
 for x in good:
  y=index.get((x['document'],x['original_path'],x['sha256']));assert y is not None and y['resolution']!='unresolved',(group,x)
 counts[group]=len(good)
assert counts=={'primary_references':92,'secondary_source_map_references':3943}
assert sha((ROOT/'tools/build_maxwell_laboratory.py').read_bytes())=='e712f6884290718fddc54ca00b7b7332a9d321f9d2105cc4bca84f9bfca9254c'
actual=load(ROOT/'docs/ingestion/maxwell-itasca900/atlas-build-v1/independent-review/final-v1/build-review.json');assert actual['status']=='accepted' and actual['binding']['model_sha256']==sha((ROOT/'models/research/maxwell'/f'{mid}.json').read_bytes())
print(json.dumps({'passed':True,'exact_additive_shared_files':3,'preserved_original_receipt_bindings':7,'original_sidecars_extended':3,'before_snapshot_receipt_bindings':3,'prior_resolved_primary_preserved':92,'prior_resolved_secondary_preserved':3943,'previously_resolved_bindings_lost':0,'preexisting_unresolved_primary':before['summary']['primary_unresolved'],'preexisting_unresolved_secondary':before['summary']['secondary_resolution_counts']['unresolved'],'syntax':'JS/Python passed','prior_catalogue_entries':'unchanged','source_links':'exact model sources','reviewer_builds':0,'reviewer_compiled_calls':0,'scope':'Source integration only; package/browser qualification pending'},indent=2))
