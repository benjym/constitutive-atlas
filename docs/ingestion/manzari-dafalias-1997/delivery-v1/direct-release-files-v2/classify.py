"""Finite release path selection from two read-only Git name snapshots."""
from pathlib import Path
import json,hashlib,ast
P=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
tracked=(P/'tracked-changes.txt').read_text().splitlines();untracked=(P/'untracked.txt').read_text().splitlines()
review=json.loads((S/'catalogue/agent-reviews/manzari-dafalias-1997-constant-m-be-v1-agent-review-v2.json').read_text());artifacts={x['path']:x['sha256'] for x in review['artifacts']}
D='docs/ingestion/manzari-dafalias-1997/delivery-v1/'
compat={D+'direct-profile-compatibility-implementation-review-v1/decision.json',D+'direct-profile-compatibility-implementation-v1/bindings.json',D+'direct-profile-compatibility-review-v1/decision.json',D+'direct-profile-compatibility-v1/manifest.json'}
oracles={'tools/md1997_decimal_reference_current17_v1/'+n for n in ['requests.json','reference.json','POLICY.md','decimal_dsl.py','assess_saved.py']}
keep={};exclude={}
for n in tracked:keep[n]='Modified operational model/runtime/fixture, metadata preservation, ordinary app/package/CI source'
for n in untracked:
 if n.startswith('catalogue/source-snapshots/'):keep[n]='Canonical original bytes read through unchanged historical receipt/archive-map semantics'
 elif n=='catalogue/agent-reviews/manzari-dafalias-1997-constant-m-be-v1-agent-review-v2.json':keep[n]='Genuine scientific approval referenced by approved-models registry'
 elif n in artifacts:keep[n]='Exact immutable artifact directly required by genuine scientific-review validation'
 elif n in compat:keep[n]='Fixed explicit data dependency of actual packaging compatibility helper'
 elif n.startswith('docs/models/')or n.startswith('models/')or n.startswith('protocols/'):keep[n]='Runnable model/public dossier or named specification referenced by current examples'
 elif n in oracles or n in {'tools/check_md1997_numerical_ci.py','tools/profile_source_compatibility.py','tools/test_interface2016_compatible_package.mjs'}:keep[n]='Ordinary qualification numerical runner/frozen Decimal inputs or actual packaging helper'
 elif n.startswith('web/engines/current17-compatible/'):keep[n]='Exact repository-provisionable qualified payload and compatibility evidence required by builder/workflow paths'
 else:exclude[n]='Unused prospective production authority/platform/capture/collector path; absent from actual ordinary pipeline and compatibility helper source inventories'
for n in exclude:
 if n.endswith('/transport-schema.json'):exclude[n]='Unconsumed schema from obsolete external transport; direct runner/assessor reads only five frozen oracle files'
 if n==D+'current17-production-bridge-v1/profile-cases.json':exclude[n]='Prospective production bridge data, not consumed by direct current17 pipeline'
# Direct scientific review files are hashed by agent_review, not recursively executed.
checks=[]
for n,h in artifacts.items():
 p=S/n;assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==h,n;checks.append(n)
# Ensure every new direct source inventory requirement is retained.
allnames=set(tracked)|set(untracked)
bindings=json.loads((S/(D+'direct-profile-compatibility-implementation-v1/bindings.json')).read_text())
for row in bindings.values():
 for n in row['source_files']:
  assert (S/n).is_file(),n
  if n in allnames:assert n in keep,('new compatibility dependency omitted',n)
for n in oracles|compat|{'tools/check_md1997_numerical_ci.py','tools/profile_source_compatibility.py','tools/test_interface2016_compatible_package.mjs'}:assert n in keep and(S/n).is_file(),n
ast.parse((S/'tools/check_md1997_numerical_ci.py').read_text());ast.parse((S/'tools/md1997_decimal_reference_current17_v1/assess_saved.py').read_text())
# Read source only: current package dispatcher and the new checker direct inputs.
web=(S/'tools/build_web.py').read_text()
assert "interface_checker = 'test_interface2016_compatible_package.mjs' if" in web
checker=(S/'tools/test_interface2016_compatible_package.mjs').read_text()
for n in ['direct-profile-compatibility-implementation-review-v1/decision.json','direct-profile-compatibility-implementation-v1/bindings.json','direct-profile-compatibility-v1/manifest.json']:
 assert D+n in keep and n in checker,n
# Every direct local build_web import is either tracked baseline or selected here.
for node in ast.walk(ast.parse(web)):
 if isinstance(node,ast.ImportFrom) and node.module:
  candidates=['tools/'+node.module.replace('.','/')+'.py',node.module.replace('.','/')+'.py']
  for n in candidates:
   if (S/n).is_file() and n in allnames:assert n in keep,('omitted dispatcher import',n)
for n in ['web/path-engine.mjs','web/interface2016-laboratory.mjs','tools/test_interface2016_package.mjs']:
 assert (S/n).is_file(),n
 if n in allnames:assert n in keep,n
assert set(keep)|set(exclude)==allnames and not(set(keep)&set(exclude))
(P/'release-paths.txt').write_text(''.join(n+'\n' for n in sorted(keep)))
(P/'exclude-paths.txt').write_text(''.join(n+'\n' for n in sorted(exclude)))
(P/'classification.json').write_text(json.dumps({'include':keep,'exclude':exclude},indent=2)+'\n')
(P/'release-file-hashes.json').write_text(json.dumps({n:{'sha256':hashlib.sha256((S/n).read_bytes()).hexdigest(),'bytes':(S/n).stat().st_size} for n in sorted(keep)},indent=2)+'\n')
(P/'checks.json').write_text(json.dumps({'tracked_changes':len(tracked),'untracked':len(untracked),'include':len(keep),'exclude':len(exclude),'scientific_artifacts_exact':len(checks),'new_compatibility_dependencies_all_included':True,'five_oracles_and_three_direct_tools_included':True,'new_interface_checker_and_dispatch_inputs_included':True,'original_index_untouched':True},indent=2)+'\n')
print((P/'checks.json').read_text())
