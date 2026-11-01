from pathlib import Path
import json,hashlib,re,time
root=Path('/Users/bmar5496/code/constitutive-atlas');p=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1');targets={'catalogue/investigations/solver-rollback-v1/'+x+'source-archive-map.json' for x in ['', 'native/','wasm/']};files=set()
for x in p.glob('reverse-*-files.txt'):files.update(x.read_text().splitlines())
hex=re.compile(r'[0-9a-f]{64}\Z');rows=[];pins=[];errors=[]
def walk(node,loc=''):
 if isinstance(node,dict):
  for k,v in node.items():
   if k in targets and isinstance(v,str) and hex.fullmatch(v):yield k,v,loc+'/'+k,'direct-map'
  for pk in ['path','original_path']:
   if node.get(pk) in targets if isinstance(node.get(pk),str) else False:
    for hk in ['sha256','hash']:
     if isinstance(node.get(hk),str) and hex.fullmatch(node[hk]):yield node[pk],node[hk],loc+'/'+hk,pk+'-object'
  for k,v in node.items():
   if isinstance(v,(dict,list)):yield from walk(v,loc+'/'+str(k))
 elif isinstance(node,list):
  for i,v in enumerate(node):
   if isinstance(v,(dict,list)):yield from walk(v,loc+'/'+str(i))
for rel in sorted(files):
 raw=(root/rel).read_bytes();pins.append({'document':rel,'digest':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
 try:x=json.loads(raw)
 except Exception as e:errors.append({'document':rel,'error':str(e)});continue
 for path,h,loc,shape in walk(x):rows.append({'document':rel,'document_digest':hashlib.sha256(raw).hexdigest(),'target_path':path,'expected_digest':h,'pointer':loc,'shape':shape})
result={'scope':'Targeted literal-path reverse inventory of three existing solver-rollback sidecars, JSON files in catalogue/docs/tools/schemas/tests excluding source-snapshots/frozen; does not claim complete escaped/encoded path search or recursive full-repository closure. No maps modified.','targets':sorted(targets),'candidate_documents':len(files),'input_bytes':sum(x['bytes'] for x in pins),'input_pins':pins,'references':rows,'parse_errors':errors,'completed_at_unix':time.time()};(p/'TARGETED_REVERSE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'documents':len(files),'references':len(rows),'parse_errors':len(errors),'sidecar_documents':len({r['document'] for r in rows if r['document'].endswith('/source-archive-map.json')})}))
