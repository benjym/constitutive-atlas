from pathlib import Path
import gzip,json,hashlib,sys
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;P=R/'docs/ingestion/vibe-2026/full-python-contracts-v1';sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ret=read(P/'raw-inventory-durable-retention-v1.json');data=json.loads(gzip.decompress(Path(ret['durable_root_path']).read_bytes()));v2=read(P/'preservation-plan-v2.json');maps={m['path']:m for m in v2['maps']};eligible=[];unsupported=[];preexisting=[]
def contains(n,p,h):
 if isinstance(n,dict):return n.get(p)==h or n.get('path')==p and any(n.get(k)==h for k in ['sha256','hash']) or any(contains(v,p,h) for v in n.values())
 return isinstance(n,list) and any(contains(v,p,h) for v in n)
for row in data['secondary_source_map_references']:
 path=row['original_path'];doc=row['document'];h=row['sha256']
 if path not in maps or maps[path]['before_sha256']!=h or doc.endswith('/source-archive-map.json'):continue
 if not contains(read(R/doc),path,h):unsupported.append({'document':doc,'original_path':path,'sha256':h});continue
 side=str(Path(doc).parent/'source-archive-map.json')
 if side in maps:old=read(R/maps[side]['before_archive']) if maps[side]['before_sha256'] else None
 else:old=read(R/side) if (R/side).exists() else None
 if old and old['documents'].get(doc)!=sha(R/doc):preexisting.append({'document':doc,'original_path':path,'reason':'preexisting document identity mismatch'});continue
 target=checked_receipt(R,doc,path,h);assert sha(target)==h;eligible.append({'document':doc,'original_path':path,'selected':str(target.relative_to(R))})
report={'scope':'Independent full original indexed reverse-map inventory reassessment; no inference from author true flags','genuine_previously_eligible_resolved':len(eligible),'unsupported_path_shape_provenance':len(unsupported),'preexisting_docpin_invalid':len(preexisting),'eligible':eligible,'unsupported':unsupported,'preexisting':preexisting,'compiled_calls':0};(O/'reverse-closure-results.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['eligible','unsupported','preexisting']})
