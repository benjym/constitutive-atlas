"""Reconstruct qualified sources in an isolated clone; never change shared files."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('/Users/bmar5496/code/constitutive-atlas');D=Path('/private/tmp/atlas-lade-release-v1');H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest();records={};missing=[];conflicts=[]
def safe(n):
 p=Path(n);assert not p.is_absolute() and '..' not in p.parts and not p.is_symlink();return p
def copy(n,h,why,donor=None):
 p=safe(n);src=Path(donor) if donor else R/p
 if not src.is_file() or sha(src.read_bytes())!=h:src=R/'catalogue/source-snapshots'/h/p
 if not src.is_file() or sha(src.read_bytes())!=h:
  missing.append({'path':n,'sha256':h,'why':why});return
 if n in records and records[n]['sha256']!=h:conflicts.append({'path':n,'prior':records[n],'replacement':h,'reason':why})
 data=src.read_bytes();dest=D/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);records[n]={'sha256':h,'donor':str(src),'reason':why,'bytes':len(data)}
# Complete owned project-authored evidence, excluding local website output archives.
for p in sorted((R/'docs/ingestion/lade-duncan-1975').rglob('*')):
 if not p.is_file() or p.is_relative_to(H) or p.name=='website.tar.gz' or '__pycache__' in p.parts:continue
 assert p.suffix.lower() not in ('.pdf','.dll','.dylib'),p
 copy(p.relative_to(R).as_posix(),sha(p.read_bytes()),'Owned ingestion/source/numerical/acceptance evidence')
runtime=json.loads((R/'docs/reviews/common-scalar-functions-v1/actual-root-v1/source-freeze.json').read_text())['files']
for n,h in runtime.items():
 if n=='.github/workflows/verify.yml':continue
 copy(n,h,'Accepted actual-root common numerical implementation baseline')
freeze=json.loads((R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/actual-package-v2/EXECUTION_SOURCE_FREEZE.json').read_text())['files']
for n,h in freeze.items():
 if Path(n).is_absolute():continue
 copy(n,h,'Exact accepted v2 package source; supersedes historical noncompiled provenance')
# Current qualification source guards are exact, not inferred from broad freeze membership.
for typ,p in [('norsand',Path('/private/tmp/atlas-duncan-integration-v2/current-inputs/norsand/controlled-path-qualification.json')),('maxwell',R/'.local/lade-main-atlas-v1/maxwell/maxwell-qualification.json')]:
 x=json.loads(p.read_text());pins=x['binding'].get('sources',{})
 if isinstance(pins,dict):
  for n,h in pins.items():copy(n,h,typ+' exact qualified source closure')
# Bound scientific review artifacts (including archived receipt resolution context).
registry=json.loads((D/'catalogue/approved-models.json').read_text())['models']
for row in registry:
 review=row.get('review',{}).get('path')
 if not review or not review.endswith('.json'):continue
 rec=json.loads((D/review).read_text())
 for item in rec.get('artifacts',[]):
  n,h=item['path'],item['sha256'];live=R/n
  if live.is_file() and sha(live.read_bytes())==h:copy(n,h,'Canonical approval supporting artifact')
  else:
   canonical=R/'catalogue/source-snapshots'/h/n
   if canonical.is_file():copy('catalogue/source-snapshots/'+h+'/'+n,h,'Canonical historical approval artifact',canonical)
   else:missing.append({'path':n,'sha256':h,'why':'Approval artifact needs official receipt resolution'})
# Source renderer dossiers are project-owned text and required normal package inputs.
for p in sorted((R/'docs/models').glob('*.md')):copy(p.relative_to(R).as_posix(),sha(p.read_bytes()),'Required normal catalogue dossier')
# Root CI fixture policy/tests are required for the integrated ordinary engine.
for folder in ['tests','protocols']:
 for p in sorted((R/folder).rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.mjs','.cpp','.json','.hpp'):
   copy(p.relative_to(R).as_posix(),sha(p.read_bytes()),'Integrated CI test/protocol dependency; separately reviewed effective delta')
for n in ['.nvmrc','pyproject.toml','cmake/AtlasScalarFunctions.cmake']:
 p=R/n;copy(n,sha(p.read_bytes()),'CI toolchain/build configuration')
# Transport exact qualified controlled-path bytes; no recompilation/review invention.
folder=Path('/private/tmp/atlas-duncan-integration-v2/current-inputs/norsand')
for p in sorted(folder.rglob('*')):
 if p.is_file():copy('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand/'+p.relative_to(folder).as_posix(),sha(p.read_bytes()),'Exact accepted controlled-path CI transport',p)
result={'base':'b04b0519398bad9e4b9bf854b2d6e8d4719b7f7b','files':records,'conflicts':conflicts,'unresolved':missing,'scope':'Exact qualified reconstruction in isolated clone; excluded local-only website archives/private originals/unrelated paper'}
(H/'OVERLAY-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'files':len(records),'conflicts':len(conflicts),'unresolved':len(missing)}))
