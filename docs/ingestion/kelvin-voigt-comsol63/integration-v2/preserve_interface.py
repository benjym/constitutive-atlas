"""Coordinator-authorized isolated interface-v3 installation and prior receipt preservation."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];SOURCE=Path('/Users/bmar5496/code/constitutive-atlas');D=Path('docs/ingestion/kelvin-voigt-comsol63');B=R/D/'integration-v2'
def digest(data):return hashlib.sha256(data).hexdigest()
def put(name,data):
 p=R/name
 if p.exists():assert p.read_bytes()==data,('Refuse conflicting existing file',str(name))
 else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 return digest(data)
def archive(original,data):
 h=digest(data);name=Path('catalogue/source-snapshots')/h/original;put(name,data);return {'original_path':str(original),'sha256':h,'archived_path':str(name)}
def write_map(name,m):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(m,indent=2)+'\n');return digest(p.read_bytes())
def new_map(folder,entries):
 p=R/folder/'source-archive-map.json';assert not p.exists(),p
 docs={str(z.relative_to(R)):digest(z.read_bytes())for z in sorted((R/folder).glob('*.json'))}
 m={'version':'immutable-source-archive-map-0.1','documents':docs,'entries':entries};return write_map(folder/'source-archive-map.json',m)
def main():
 assert not(B/'installation.json').exists(),'Create-only installation receipt'
 names=[D/'interface-v1/freeze.json',D/'interface-v2/freeze.json',D/'integration-v1/archive-installation.json',D/'interface-v1/runtime-tests/manifest.json']
 original_receipts={str(p):digest((R/p).read_bytes())for p in names}
 v3=json.loads((SOURCE/D/'interface-v3/freeze.json').read_text());newfiles=v3['files'];archives=[];changed_map=D/'interface-v1/source-archive-map.json';oldmap=(R/changed_map).read_bytes();oldmaprow=archive(changed_map,oldmap);archives.append(oldmaprow)
 m=json.loads(oldmap);oldentries=list(m['entries']);olddocs=dict(m['documents']);entries=[]
 for name in['web/kelvin-voigt-contract.mjs','tests/test_kelvin_voigt_contract.mjs']:
  old=(SOURCE/D/'interface-v3/prior'/name).read_bytes();h=digest(old)
  assert all(json.loads((R/D/version/'freeze.json').read_text())['files'][name]==h for version in['interface-v1','interface-v2'])
  assert digest((R/name).read_bytes())==h,('Unexpected isolated live source before installation',name)
  row=archive(Path(name),old);archives.append(row);entries.append(row)
  assert not any(z['original_path']==name and z['sha256']==h for z in m['entries']);m['entries'].append(row)
 assert all(e in m['entries']for e in oldentries)and all(m['documents'][k]==v for k,v in olddocs.items())
 maps={str(changed_map):write_map(changed_map,m),str(D/'interface-v2/source-archive-map.json'):new_map(D/'interface-v2',entries),str(D/'integration-v1/source-archive-map.json'):new_map(D/'integration-v1',[oldmaprow])}
 # Preserve exact v3 evidence alongside the six current source/test files.
 for p in sorted((SOURCE/D/'interface-v3').rglob('*')):
  if p.is_file():put(D/'interface-v3'/p.relative_to(SOURCE/D/'interface-v3'),p.read_bytes())
 for name,h in newfiles.items():
  data=(SOURCE/name).read_bytes();assert digest(data)==h,name;(R/name).write_bytes(data)
 assert original_receipts=={str(p):digest((R/p).read_bytes())for p in names},'Historical receipt changed'
 report={'identity':'kelvin-interface-v3-isolated-installation-v2','scope':'Only isolated release source; no root shared changes/builds/compiled calls','historical_receipts_unchanged':original_receipts,'canonical_prior_archives':archives,'changed_or_new_maps':maps,'installed_six_files':newfiles,'interface_v3_freeze_sha256':digest((R/D/'interface-v3/freeze.json').read_bytes()),'source_v3_evidence_mirrored_exactly':True,'files':{**{z['archived_path']:z['sha256']for z in archives},**maps,**newfiles}};(B/'installation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'prior_snapshots':len(archives),'map_changes':len(maps),'current_files':len(newfiles),'old_receipts_unchanged':len(original_receipts)},indent=2))
if __name__=='__main__':main()
