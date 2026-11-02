"""Pin built files and require explicit versioned schedule selection before execution."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 build=(ROOT/sys.argv[1]).resolve();target=sys.argv[2];output=pathlib.Path(sys.argv[3]);required=sys.argv[4]=='require-schedule'
 assert build.is_relative_to(ROOT) and not output.exists()
 obj=build/'CMakeFiles'/(target+'.dir');deps=list(obj.rglob('*.o.d'));assert deps
 headers=set()
 for dep in deps:
  for word in dep.read_text().replace('\\\n',' ').split():
   if word.endswith('/atlas/schedule.hpp'):headers.add(str(pathlib.Path(word).resolve()))
 expected=ROOT/'runtimes/physical-time-v2/include/atlas/schedule.hpp'
 assert not required or headers=={str(expected)},headers
 assert str(ROOT/'cpp/include/atlas/schedule.hpp') not in headers
 paths=[build/target,build/'CMakeCache.txt']+[p for p in obj.rglob('*') if p.is_file()]
 for name in ['generated','time-generated']:
  if (build/name).is_dir():paths.extend(p for p in (build/name).rglob('*') if p.is_file())
 assert (build/target).is_file()
 data={'phase':'built and pinned before material/test observation','schedule_required':required,'actual_schedule_headers':sorted(headers),'versioned_schedule_sha256':sha(expected),'files':{str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}}
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'pinned_files':len(data['files']),'selected_schedule_headers':data['actual_schedule_headers']}))
if __name__=='__main__':main()
