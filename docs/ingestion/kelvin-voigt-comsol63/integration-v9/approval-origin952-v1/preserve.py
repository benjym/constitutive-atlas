"""Registry-only archival preservation and six explicitly whitelisted receipts."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];W=Path('/Users/bmar5496/code/constitutive-atlas');D=Path('docs/ingestion/kelvin-voigt-comsol63');sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 assert not(B/'receipt.json').exists(),'Create-only preservation'
 source='catalogue/approved-models.json';data=(R/source).read_bytes();h=sha(data);assert h=='080f74d1ff6628f7877049084910ae37d2e48737f24d15e87c672b82763cb754';archive='catalogue/source-snapshots/'+h+'/'+source
 docs=[str(D/x)for x in ['package-v4/freeze.json','integration-v8/current37d-merge-v1/merge-receipt.json']];originals={};maps={};restored={};scalar_map='docs/reviews/common-scalar-functions-v1/source-archive-map.json';guard=json.loads((R/scalar_map).read_text());guard_sha=sha((R/scalar_map).read_bytes())
 for doc in docs:
  original=(R/doc).read_bytes();node=json.loads(original);assert node['source_sha256'][source]==h;originals[doc]=sha(original);name=str(Path(doc).parent/'source-archive-map.json');assert not(R/name).exists(),name
  m={'version':'immutable-source-archive-map-0.1','documents':{str(p.relative_to(R)):sha(p.read_bytes())for p in(R/doc).parent.glob('*.json')},'entries':[{'original_path':source,'sha256':h,'archived_path':archive}]};maps[name]=(json.dumps(m,indent=2)+'\n').encode()
 for suffix in ['addendum-freeze-v1','freeze-v1','freeze-v2','freeze-v3','freeze-v4','freeze-v5']:
  path='docs/reviews/common-scalar-functions-v1/package-controls-'+suffix+'.json';bytes_=(W/path).read_bytes();expected=guard['documents'][path];assert sha(bytes_)==expected,(path,expected)
  if(R/path).exists():assert(R/path).read_bytes()==bytes_,path
  else:restored[path]=bytes_
 target=R/archive;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==data
 else:target.write_bytes(data)
 for path,bytes_ in restored.items():(R/path).write_bytes(bytes_)
 for path,bytes_ in maps.items():(R/path).write_bytes(bytes_)
 assert(R/source).read_bytes()==data;assert sha((R/scalar_map).read_bytes())==guard_sha
 sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
 for doc in docs:assert sha((R/doc).read_bytes())==originals[doc];assert checked_receipt(R,doc,source,h)==target
 receipt={'identity':'kelvin-approval-origin952-preservation-v1','incoming_origin':'95210701c73718500ca41d0eb70a8281c585b1a3','preserved_registry_sha256':h,'scope':'Preserve exact priorregistry and two existing source receipts before parent data-only approval merge; restore only six coordinator-whitelisted scalar-control receipt JSONs from root exactbytes','original_receipts':originals,'files':{archive:h}|{p:sha(v)for p,v in maps.items()}|{p:sha(v)for p,v in restored.items()},'restored_scalar_receipts':{p:sha(v)for p,v in restored.items()},'existing_scalar_guard':{'path':scalar_map,'sha256':guard_sha},'context_reason':'Six pre-existing scalar map document guards named absent original receipt files; exact source-workspace bytes matched all existing guards and were copied under explicit coordinator whitelist. No sidecar expectations or original document hashes changed.','bindings':[{'document':doc,'original_path':source,'sha256':h,'archived_path':archive}for doc in docs],'registry_unchanged_during_preservation':True,'passed':True};(B/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Preserved registry;2sidecars;',len(restored),'exact missing scalar receipt files restored')
if __name__=='__main__':main()
