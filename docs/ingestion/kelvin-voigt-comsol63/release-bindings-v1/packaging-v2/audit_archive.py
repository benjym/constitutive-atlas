"""Validate/read the complete immutable v1 audit without loose archive sidecars."""
import argparse,hashlib,json,tarfile
from pathlib import Path,PurePosixPath
B=Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()
def read_archive():
 record=json.loads((B/'ARCHIVE.json').read_text());archive=B/record['archive']
 assert sha(archive.read_bytes())==record['archive_sha256'],'archive hash mismatch'
 prefix=record['member_prefix'];payloads={}
 with tarfile.open(archive,'r:gz')as stream:
  members=stream.getmembers();assert len(members)==record['member_count']
  for member in members:
   assert member.isfile()and member.name.startswith(prefix),'unexpected archive member'
   name=member.name[len(prefix):];path=PurePosixPath(name)
   assert not path.is_absolute()and'..'not in path.parts and name not in payloads,'unsafe/duplicate member'
   assert name in record['members'],'unlisted member'
   data=stream.extractfile(member).read();assert sha(data)==record['members'][name],name
   payloads[name]=data
 assert set(payloads)==set(record['members'])
 assert sha(payloads['manifest.json'])==record['original_manifest_sha256']
 original=json.loads(payloads['manifest.json'])
 assert set(original['files'])==set(payloads)-{'manifest.json'}
 for name,h in original['files'].items():assert sha(payloads[name])==h,name
 plan=json.loads(payloads['plan.json']);own=json.loads(payloads['own-interface-plan.json'])
 for name,r in plan['sidecar_proposals'].items():assert sha(payloads['scope-v2-planned-sidecars/'+name])==r['proposed_sha256'],name
 for r in own['pairs']:assert sha(payloads['own-interface-planned-sidecars/'+r['source_archive_map']])==r['proposed_map_sha256']
 return record,payloads

def export(payloads,output):
 assert not output.exists(),'Refuse existing output directory'
 output.mkdir(parents=True)
 for name,data in payloads.items():
  p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['check','show-plan','show-own-plan','export-v1','export-proposals']);parser.add_argument('--output',type=Path);args=parser.parse_args();record,payloads=read_archive()
 if args.mode=='check':print(json.dumps({'passed':True,'archive_sha256':record['archive_sha256'],'exact_v1_members':len(payloads),'original_manifest_sha256':record['original_manifest_sha256'],'final_sidecar_proposals':16,'loose_sidecars_required_for_validation':False},indent=2))
 elif args.mode.startswith('show-'):print(payloads['plan.json'if args.mode=='show-plan'else'own-interface-plan.json'].decode(),end='')
 else:
  assert args.output is not None,'--output required'
  selected=payloads if args.mode=='export-v1'else{k:v for k,v in payloads.items()if k.startswith(('scope-v2-planned-sidecars/','own-interface-planned-sidecars/'))}
  export(selected,args.output.resolve());print(f'Exported {len(selected)} exact files to {args.output.resolve()}')
if __name__=='__main__':main()
