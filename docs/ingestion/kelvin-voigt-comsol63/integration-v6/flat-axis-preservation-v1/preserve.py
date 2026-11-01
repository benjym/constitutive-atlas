"""One-time source-only preservation before coordinator's axis-range edit."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];D=Path('docs/ingestion/kelvin-voigt-comsol63');sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 assert not(B/'receipt.json').exists();source='web/app.js';data=(R/source).read_bytes();h=sha(data);assert h=='a989a23c5cdc19c4d02a9b28c5f051ee77795e6983d246e0627068acd0f48ab7'
 archive='catalogue/source-snapshots/'+h+'/'+source;docs=[str(D/x)for x in ['package-v3/freeze.json','integration-v5/merge-receipt.json']];maps={};originals={}
 for doc in docs:
  original=(R/doc).read_bytes();assert h in original.decode()and source in original.decode();originals[doc]=sha(original);name=str(Path(doc).parent/'source-archive-map.json');assert not(R/name).exists(),name
  mapping={'version':'immutable-source-archive-map-0.1','documents':{str(p.relative_to(R)):sha(p.read_bytes())for p in(R/doc).parent.glob('*.json')},'entries':[{'original_path':source,'sha256':h,'archived_path':archive}]};maps[name]=(json.dumps(mapping,indent=2)+'\n').encode()
 target=R/archive;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==data
 else:target.write_bytes(data)
 for name,bytes_ in maps.items():(R/name).write_bytes(bytes_)
 sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
 for doc in docs:assert sha((R/doc).read_bytes())==originals[doc];assert checked_receipt(R,doc,source,h)==target
 assert(R/source).read_bytes()==data
 receipt={'identity':'kelvin-flat-axis-app-preservation-v1','scope':'Exact current merged app archived before parent presentation-only axis-range change; no numerical values, controls, model, source receipts or app bytes changed by preservation','preserved_app_sha256':h,'original_documents':originals,'files':{archive:h}|{name:sha(bytes_)for name,bytes_ in maps.items()},'bindings':[{'document':doc,'original_path':source,'sha256':h,'archived_path':archive}for doc in docs],'passed':True}
 (B/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Preserved',h,'and installed2document-bound sidecars')
if __name__=='__main__':main()
