from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3]
p=R/'tools/record_cmake_profile_build.py';s=p.read_text();start=s.index('def dependencies(');end=s.index('\ndef expand_responses',start)
new='''def dependency_identity(token, build):
    # Header aliases are permitted only as explicit, fully bound identities.
    require(token and not any(c in token for c in ['\\0','\\n','\\r','$','`']), 'Unsafe dependency token')
    require('..' not in Path(token).parts, 'Parent traversal unsupported in dependency token')
    lexical = Path(os.path.abspath(build/token))
    pending = list(lexical.parts[1:]); current = Path(lexical.anchor); chain = []
    while pending:
        current = current/pending.pop(0)
        info = current.lstat() # Missing/dangling/looping paths fail closed.
        if current.is_symlink():
            require(len(chain)<40, 'Dependency symlink chain too deep or cyclic')
            target = os.readlink(current)
            require(target and not any(c in target for c in ['\\0','\\n','\\r']), 'Unsafe dependency symlink target')
            require('..' not in Path(target).parts, 'Parent traversal unsupported in dependency symlink target')
            absolute = Path(os.path.abspath(current.parent/target))
            chain.append({'path':str(current),'target':target,'absolute_target':str(absolute)})
            pending = list(absolute.parts[1:])+pending; current = Path(absolute.anchor)
        elif pending:
            require(current.is_dir(), 'Nondirectory dependency ancestor')
    resolved = lexical.resolve(strict=True)
    require(current==resolved, 'Dependency traversal resolution differs')
    return {'token':token,'lexical_path':str(lexical),'canonical_path':str(resolved),
            'sha256':digest(resolved),'symlink_chain':chain}

def dependencies(path, build, obj, identities=None):
    text = path.read_text().replace('\\\\\\n', ' ')
    parts = re.split(r'(?<!\\\\):', text, maxsplit=1)
    require(len(parts)==2, 'Malformed dependency file')
    left = shlex.split(parts[0]); require(len(left)==1, 'Ambiguous dependency target')
    require((build/left[0]).resolve()==obj.resolve(), 'Dependency target mismatch')
    names = shlex.split(parts[1]); require(names, 'Empty dependency set')
    members = [dependency_identity(name,build) for name in names]
    require(len({m['lexical_path'] for m in members})==len(members), 'Duplicate lexical dependency member')
    paths = list(dict.fromkeys(Path(m['canonical_path']) for m in members))
    groups = {}
    for index, member in enumerate(members):groups.setdefault(member['canonical_path'],[]).append(index)
    aliases = {name:indices for name,indices in groups.items() if len(indices)>1}
    for indices in aliases.values():
        require(any(members[i]['symlink_chain'] for i in indices), 'Unexplained canonical dependency collision')
    if identities is not None:
        identities[str(path)]={'raw_depfile_sha256':digest(path),'ordered_members':members,'canonical_alias_groups':aliases}
    return paths
'''
s=s[:start]+new+s[end:];s=s.replace('units={};dep_records=set();','units={};dependency_identities={};dep_records=set();').replace("dependencies(Path(str(obj)+'.d'),build,obj)","dependencies(Path(str(obj)+'.d'),build,obj,dependency_identities)").replace("return {'files':files,","return {'dependency_identities':dependency_identities,'dependency_identity_contract':'ordered-lexical-canonical-symlink-chain-v2','files':files,")
s=s.replace('atlas-cmake-profile-build-pre-v1','atlas-cmake-profile-build-pre-v2').replace('atlas-cmake-profile-build-post-v1','atlas-cmake-profile-build-post-v2').replace('atlas-cmake-profile-build-failed-v1','atlas-cmake-profile-build-failed-v2')
s=s.replace("'files_verified':len(after['files'])","'files_verified':len(after['files']),'dependency_identity_contract':after['dependency_identity_contract'],'dependency_identities_sha256':hashlib.sha256(canonical(after['dependency_identities'])).hexdigest(),'dependency_records_verified':len(after['dependency_identities'])")
(H/'candidates/tools/record_cmake_profile_build_v2.py').write_text(s)
w=R/'.github/workflows/verify.yml';out=w.read_text().replace('tools/record_cmake_profile_build.py','tools/record_cmake_profile_build_v2.py');assert out!=w.read_text();(H/'candidates/.github/workflows/verify.yml').write_text(out)
for n in ['tools/record_cmake_profile_build.py','.github/workflows/verify.yml']:
 dst=H/'before'/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((R/n).read_bytes())

# Portable fake-file tests; subprocess/material execution blocked inside tests.
test=(H/'tests/test_build_receipts_v2.py').read_text().replace("HERE/'candidates/tools/record_cmake_profile_build_v2.py'","HERE/'tools/record_cmake_profile_build_v2.py'").replace('SOURCE_HEADER=HERE.parents[3]/TOOL.SCHEDULE','SOURCE_HEADER=HERE/TOOL.SCHEDULE')
dst=H/'candidates/tests/test_cmake_profile_build_v2.py';dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(test)
p=H/'candidates/.github/workflows/verify.yml';s=p.read_text();needle='          mkdir -p "$RUNNER_TEMP/bingham-build-receipts/time-predictor"';assert s.count(needle)==3;p.write_text(s.replace(needle,'          python -B tests/test_cmake_profile_build_v2.py\n'+needle))
