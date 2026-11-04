"""Apply only coordinator-authorized candidate packaging-tool additions."""
from pathlib import Path
import shutil,difflib
P=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
(P/'before').mkdir(exist_ok=True);(P/'proposed').mkdir(exist_ok=True)
def edit(name,changes):
 p=S/'tools'/name;old=p.read_text();(P/'before'/name).write_text(old);new=old
 for a,b in changes:
  assert new.count(a)==1,(name,a,new.count(a));new=new.replace(a,b)
 (P/'proposed'/name).write_text(new);p.write_text(new)
 (P/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+name,tofile='after/'+name)))
edit('build_controlled_path_web.py',[
("    refresh = validate_refresh(build, MODEL)","    from profile_source_compatibility import validate as compatible_source, copy_evidence\n    compatibility = compatible_source(ROOT, build, 'norsand')\n    refresh = None if compatibility is not None else validate_refresh(build, MODEL)"),
("    if refresh is not None:\n        qualification_path", "    if compatibility is not None:\n        qualification_path = build/'controlled-path-qualification.json'\n        qualification = compatibility['qualification']\n        qualification_bytes = compatibility['qualification_bytes']\n        sources = compatibility['sources']\n        accepted_review_bytes = compatibility['review_bytes']\n        qualified_artifact_bytes = {name:(build/name).read_bytes() for name in ('atlas_path_capability.mjs', 'atlas_path_capability.wasm')}\n    elif refresh is not None:\n        qualification_path"),
("    identity = {'profile':'controlled-path-ode-v1'", "    copy_evidence(compatibility, engine)\n    identity = {'profile':'controlled-path-ode-v1'")])
edit('build_maxwell_laboratory.py',[
("    before = source_manifest()", "    before = source_manifest()\n    from profile_source_compatibility import validate as compatible_source\n    compatibility = compatible_source(ROOT, build, 'maxwell')"),
("    if qualification.get('schema_version')", "    expected_binding = dict(binding, source_manifest_sha256=qualification['binding']['source_manifest_sha256']) if compatibility is not None else binding\n    if qualification.get('schema_version')"),
("qualification.get('binding') != binding", "qualification.get('binding') != expected_binding"),
("accepted.get('binding') != binding", "accepted.get('binding') != expected_binding"),
("    files.update(components)","    if compatibility is not None:\n        files['engine-maxwell/source-compatibility.json'] = compatibility['compatibility_bytes']\n        files['engine-maxwell/source-compatibility-review.json'] = compatibility['decision_bytes']\n    files.update(components)")])
edit('build_interface2016_web.py',[
("    refresh = validate_refresh(build, MODEL)","    from profile_source_compatibility import validate as compatible_source, copy_evidence\n    compatibility = compatible_source(ROOT, build, 'interface2016')\n    refresh = dict(qualification=compatibility['qualification'], qualification_bytes=compatibility['qualification_bytes'], review_bytes=compatibility['review_bytes']) if compatibility is not None else validate_refresh(build, MODEL)"),
("        closure = qualification['binding']['source_closure']", "        closure = compatibility['sources'] if compatibility is not None else qualification['binding']['source_closure']"),
("    identity = dict(profile='controlled-path-ode-v1'", "    copy_evidence(compatibility, engine)\n    identity = dict(profile='controlled-path-ode-v1'")])
shutil.copyfile(P/'profile_source_compatibility.py',S/'tools/profile_source_compatibility.py')
print('Applied three additive optional branches plus one new helper; no engine execution')
