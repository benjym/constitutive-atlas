from pathlib import Path
import json,hashlib,shlex,re,os,collections,importlib.util
O=Path(__file__).resolve().parent;R=O.parents[3];B=Path('/private/tmp/atlas-time-profile-v2/build-time-v2');p=next((B/'CMakeFiles/atlas_schedule_predictor_tests.dir').rglob('*.o.d'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
text=p.read_text().replace('\\\n',' ');left,right=re.split(r'(?<!\\):',text,maxsplit=1);tokens=shlex.split(right);groups=collections.defaultdict(list)
for t in tokens:groups[str((B/t).resolve())].append(t)
aliases=[]
for canonical,members in groups.items():
 if len(members)>1:
  chains=[]
  for token in members:
   path=B/token;links=[]
   for part in [path,*path.parents]:
    if part.is_symlink():links.append({'path':str(part),'target':os.readlink(part)})
   chains.append({'token':token,'symlinks':links})
  aliases.append({'canonical_path':canonical,'sha256':sha(Path(canonical)),'ordered_tokens':members,'chains':chains})
spec=importlib.util.spec_from_file_location('oldrecorder',R/'tools/record_cmake_profile_build.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:m.dependencies(p,B,Path(str(p)[:-2]));old={'unexpected_pass':True}
except Exception as e:old={'rejected':str(e)}
x={'saved_local_depfile':str(p),'raw_sha256':sha(p),'tokens':len(tokens),'canonical_alias_groups':aliases,'old_recorder':old,'scope':'Actual saved local .d source-only observation. CI raw log reports same error class but CI .d was not uploaded; this is not proof of exact CI dependency tokens.'};(O/'SAVED-DEPFILE-CHECK.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
