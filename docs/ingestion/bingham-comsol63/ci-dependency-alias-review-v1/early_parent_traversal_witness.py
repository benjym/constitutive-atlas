from pathlib import Path
import importlib.util,json,hashlib
O=Path(__file__).resolve().parent;P=O.parent/'ci-dependency-alias-v1/candidates/tools/record_cmake_profile_build_v2.py'
spec=importlib.util.spec_from_file_location('candidate',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=O/'parent-traversal-fixture';(f/'links').mkdir(parents=True);(f/'else/deep').mkdir(parents=True)
(f/'links/header.h').write_text('wrong lexical collapse\n');(f/'else/header.h').write_text('actual referenced header\n');(f/'links/dir').symlink_to('../else/deep',target_is_directory=True)
token='links/dir/../header.h';actual=(f/token).resolve(strict=True)
try:observed=m.dependency_identity(token,f)
except Exception as e:observed={'rejected':str(e)}
x={'candidate_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'token':token,'actual_filesystem_resolution':str(actual),'observed':observed,'correct_identity_or_rejection':observed.get('canonical_path')==str(actual) or 'rejected' in observed}
(O/'EARLY-PARENT-TRAVERSAL-WITNESS.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
