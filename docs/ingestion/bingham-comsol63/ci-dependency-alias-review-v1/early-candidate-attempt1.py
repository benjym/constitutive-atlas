"""Record/verify an existing Unix-Makefiles physical-time profile build.

No compiler, material engine, subprocess or shell is executed here. This is an
integrity/provenance receipt, not numerical qualification or binary attestation.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys

SCHEDULE = 'runtimes/physical-time-v2/include/atlas/schedule.hpp'
SCHEDULE_SHA = 'fd05b08d422468802fb788386a2f19463dec65ca66e3cf2153f837a5db0d2702'
LEGACY = 'cpp/include/atlas/schedule.hpp'

def require(condition, message):
    if not condition: raise ValueError(message)

def digest(path):
    require(path.is_file() and path.stat().st_size > 0, 'Missing/empty required file: '+str(path))
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''): value.update(block)
    return value.hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def parse_json(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, 'Duplicate JSON key: '+key); out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def local(root, name):
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts and str(relative) not in {'.',''}, 'Unsafe relative input')
    current = root
    for part in relative.parts:
        current = current/part; require(not current.is_symlink(), 'Symlink in local input: '+str(current))
    require(current.resolve().is_relative_to(root), 'Local path escapes root')
    return current

def cache_values(path):
    out={}
    for line in path.read_text().splitlines():
        match=re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*):[^=]*=(.*)',line)
        if match:
            require(match[1] not in out, 'Duplicate CMake cache key');out[match[1]]=match[2]
    return out

def dependency_identity(token, build):
    # Header aliases are permitted only as explicit, fully bound identities.
    require(token and not any(c in token for c in ['\0','\n','\r','$','`']), 'Unsafe dependency token')
    lexical = Path(os.path.abspath(build/token))
    pending = list(lexical.parts[1:]); current = Path(lexical.anchor); chain = []
    while pending:
        current = current/pending.pop(0)
        info = current.lstat() # Missing/dangling/looping paths fail closed.
        if current.is_symlink():
            require(len(chain)<40, 'Dependency symlink chain too deep or cyclic')
            target = os.readlink(current)
            require(target and not any(c in target for c in ['\0','\n','\r']), 'Unsafe dependency symlink target')
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
    text = path.read_text().replace('\\\n', ' ')
    parts = re.split(r'(?<!\\):', text, maxsplit=1)
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

def expand_responses(tokens, build, records, depth=0):
    require(depth < 8, 'Response nesting too deep')
    output = []
    for token in tokens:
        require(not re.search(r'[;$`|&<>\n\r]',token), 'Unsafe shell/expansion syntax in response arguments')
        if token.startswith('@'):
            unresolved = Path(token[1:])
            if not unresolved.is_absolute(): unresolved = build/unresolved
            require(unresolved.is_relative_to(build), 'Response file escapes build')
            local(build,unresolved.relative_to(build))
            path = unresolved.resolve();records.add(path);digest(path)
            output.extend(expand_responses(shlex.split(path.read_text()), build, records, depth+1))
        else: output.append(token)
    return output

def archive_members(path):
    data=path.read_bytes();require(data.startswith(b'!<arch>\n'), 'Invalid scalar archive format')
    offset=8;table=b'';members={}
    while offset<len(data):
        header=data[offset:offset+60];require(len(header)==60 and header[58:]==b'`\n', 'Malformed archive header')
        raw=header[:16].decode('ascii').strip();size=int(header[48:58]);offset+=60
        content=data[offset:offset+size];require(len(content)==size, 'Truncated archive member');offset+=size+(size%2)
        if raw=='//':table=content;continue
        if raw in {'/','/SYM64/'}:continue
        if raw.startswith('#1/'):
            length=int(raw[3:]);require(length<=len(content), 'Invalid BSD archive member')
            name=content[:length].rstrip(b'\0').decode();content=content[length:]
        elif raw.startswith('/') and raw[1:].isdigit():
            start=int(raw[1:]);require(start<len(table), 'Missing archive name table');name=table[start:].split(b'/\n',1)[0].decode()
        else:name=raw.rstrip('/')
        if name.startswith('__.SYMDEF'):continue
        require(name and '/' not in name and name not in members, 'Unsafe/duplicate scalar archive member')
        members[name]=hashlib.sha256(content).hexdigest()
    require(offset==len(data), 'Trailing malformed archive data')
    return members

def snapshot(request):
    require(set(request)=={'root','build','target','entrypoint','recipe','models','schedule','kind','artifacts','consumer_tools','consumer_sources'}, 'Unexpected request fields')
    root = Path(request['root']).resolve(); require(root.is_dir(), 'Source root absent')
    build = local(root, request['build']); require(build.is_dir(), 'Build absent')
    target = request['target']; require(bool(re.fullmatch(r'[A-Za-z0-9_]+',target)), 'Unsafe target')
    require(target!='atlas_scalar_functions', 'Scalar archive is not a material target')
    require(request['schedule'] in {'required','absent'} and request['kind'] in {'native','wasm'}, 'Unsupported profile mode')
    entry = local(root,request['entrypoint']); recipe = local(root,request['recipe']); models = local(root,request['models'])
    require(models.is_dir(), 'Model directory absent')
    model_paths = sorted(models.glob('*.json')); require(model_paths, 'No model inputs')
    required = {Path(__file__).resolve(), entry, recipe, root/'cmake/AtlasScalarFunctions.cmake'}
    # Exact current release identities are recorded. No historical source hash is substituted.
    sources = set(required) | set(model_paths)
    for directory, suffixes in [('atlas',{'.py'}),('cpp',{'.cpp','.hpp','.c','.h'}),('schemas',{'.json'}),('runtimes/physical-time-v2',None)]:
        folder = local(root,directory); require(folder.is_dir(), 'Source directory absent: '+directory)
        found = [p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and (suffixes is None or p.suffix in suffixes)]
        require(found, 'Source enumeration empty: '+directory)
        for p in found: local(root,p.relative_to(root)); sources.add(p)
    for name in request['consumer_sources']:
        p=local(root,name); require(p.is_file(), 'Consumer source absent'); sources.add(p)
    for p in (root/'cpp/scalar-functions').rglob('*'):
        if p.is_file():local(root,p.relative_to(root));sources.add(p)
    for p in sources:
        if p.is_relative_to(root):local(root,p.relative_to(root))
        digest(p)
    schedule = local(root,SCHEDULE); legacy = local(root,LEGACY)
    require(digest(schedule)==SCHEDULE_SHA, 'Versioned schedule hash differs')
    records = {build/'CMakeCache.txt', build/'compile_commands.json'}
    for p in records: local(build,p.relative_to(build));digest(p)
    cache = cache_values(build/'CMakeCache.txt')
    require(cache.get('CMAKE_GENERATOR')=='Unix Makefiles', 'Unix Makefiles required for exact .o.d audit')
    require(cache.get('CMAKE_EXPORT_COMPILE_COMMANDS') in {'ON','TRUE','1'}, 'Compile command export required')
    require(Path(cache.get('CMAKE_HOME_DIRECTORY','')).resolve()==recipe.parent, 'CMake recipe/source directory mismatch')
    # Emscripten legitimately keeps compiler/ar/ranlib identities in generated
    # Compiler.cmake records rather than cache entries. Read only literal quoted
    # values; never evaluate CMake, variables or a toolchain program.
    compiler_versions={}; compiler_tools={}
    for lang in ['C','CXX']:
        matches=list((build/'CMakeFiles').glob('*/CMake'+lang+'Compiler.cmake'))
        require(len(matches)==1, 'Exactly one actual '+lang+' compiler record required')
        info=matches[0];local(build,info.relative_to(build));records.add(info);text=info.read_text()
        version=re.findall(r'^set\(CMAKE_'+lang+r'_COMPILER_VERSION "([^"\n]+)"\)$',text,re.M)
        require(len(version)==1, 'Compiler version missing/ambiguous: '+lang);compiler_versions[lang]=version[0]
        for key in ['CMAKE_'+lang+'_COMPILER','CMAKE_AR','CMAKE_RANLIB','CMAKE_LINKER']:
            values=re.findall(r'^set\('+key+r' "([^"\n]+)"\)$',text,re.M)
            require(len(values)<=1, 'Ambiguous compiler tool record: '+key)
            if values:
                require(not re.search(r'[;$`\n\r]',values[0]), 'Nonliteral compiler tool record')
                if key in compiler_tools:require(compiler_tools[key]==values[0], 'Conflicting compiler tool records')
                compiler_tools[key]=values[0]
    tool_keys = ['CMAKE_C_COMPILER','CMAKE_CXX_COMPILER','CMAKE_AR','CMAKE_RANLIB','CMAKE_LINKER','CMAKE_COMMAND','CMAKE_MAKE_PROGRAM']
    tools = {}
    for key in tool_keys:
        values=[mapping[key] for mapping in [cache,compiler_tools] if mapping.get(key)]
        require(values, 'Missing tool record: '+key)
        require(len(set(str(Path(value).resolve()) for value in values))==1, 'Cache/compiler tool disagreement: '+key)
        p = Path(values[0]); require(p.is_absolute() and os.access(p,os.X_OK), 'Tool is not an executable absolute path: '+key)
        p=p.resolve();digest(p);tools[key]=str(p);records.add(p)
    require(request['consumer_tools'], 'Consumer tool records required')
    for name in request['consumer_tools']:
        require(bool(re.fullmatch(r'[A-Za-z0-9_.+-]+',name)), 'Unsafe consumer tool')
        found=shutil.which(name);require(found, 'Consumer tool absent: '+name)
        p=Path(found).resolve();digest(p);records.add(p);tools['consumer:'+name]=str(p)
    if request['kind']=='wasm':
        require(cache.get('CMAKE_TOOLCHAIN_FILE'), 'Wasm toolchain file required')
        toolchain=Path(cache['CMAKE_TOOLCHAIN_FILE']).resolve();records.add(toolchain);digest(toolchain)
        require('emscripten' in str(toolchain).lower(), 'Expected Emscripten toolchain')
    generator_python=[cache[key] for key in ['Python3_EXECUTABLE','_Python3_EXECUTABLE'] if cache.get(key)]
    require(generator_python and len({str(Path(value).resolve()) for value in generator_python})==1, 'Missing/conflicting actual generator Python')
    generator=Path(generator_python[0]);require(generator.is_absolute() and os.access(generator,os.X_OK), 'Generator Python is not executable')
    generator=generator.resolve();records.add(generator);tools['generator:Python3']=str(generator)
    generator_commands=[]
    for makefile in (build/'CMakeFiles').glob('*.dir/build.make'):
        for line in makefile.read_text().splitlines():
            if line.startswith('\t') and '-m atlas.compiler ' in line:
                local(build,makefile.relative_to(build));records.add(makefile)
                words=shlex.split(line.strip())
                require(len(words)==9 and words[0]=='cd' and Path(words[1]).resolve()==root and words[2]=='&&' and Path(words[3]).resolve()==generator and words[4:7]==['-B','-m','atlas.compiler'] and Path(words[7]).resolve()==build/'generated' and Path(words[8]).resolve()==models, 'Actual model generator command differs')
                generator_commands.append(words)
    require(len(generator_commands)==1, 'Exactly one recorded normal model generator command required')
    generated={build/'generated/models.hpp',build/'generated/models.json'}
    for p in generated:local(build,p.relative_to(build));digest(p)
    metadata=parse_json(build/'generated/models.json');raw_models=[parse_json(p) for p in model_paths]
    require(metadata.get('schema_version')=='0.1' and metadata.get('models')==raw_models, 'Generated catalogue differs from exact model inputs')
    catalogue_hash=hashlib.sha256(canonical(raw_models)).hexdigest()
    require(metadata.get('sha256')==catalogue_hash, 'Generated catalogue digest mismatch')
    header=(build/'generated/models.hpp').read_text()
    require(header.startswith('// Generated by atlas.compiler;') and catalogue_hash in header, 'Generated header/compiler/catalogue binding missing')
    commands=parse_json(build/'compile_commands.json');require(isinstance(commands,list) and commands, 'No compiler command records')
    units={};dependency_identities={};dep_records=set();actual_dependencies=set();object_records=set();ordered_commands={};includes={}
    expected_scalar=set(re.findall(r'\$\{ATLAS_SCALAR_ROOT\}/([^"\n]+\.c)',(root/'cmake/AtlasScalarFunctions.cmake').read_text()))
    require(expected_scalar, 'Scalar source recipe empty')
    for group in [target,'atlas_scalar_functions']:
        directory=build/'CMakeFiles'/(group+'.dir');require(directory.is_dir() and not directory.is_symlink(), 'Target record absent')
        for name in ['flags.make','build.make','link.txt','DependInfo.cmake']:
            p=directory/name;local(build,p.relative_to(build));digest(p);records.add(p)
        for line in (directory/'flags.make').read_text().splitlines():
            if re.match(r'^(?:C|CXX)_[A-Z_]+\s*=',line):
                expand_responses(shlex.split(line.split('=',1)[1]),build,records)
        objects=set(directory.rglob('*.o'));deps=set(directory.rglob('*.o.d'))
        for p in objects|deps:local(build,p.relative_to(build))
        require(objects and len(objects)==len(deps), 'Missing/extra object or .o.d')
        require({Path(str(p)+'.d') for p in objects}==deps, 'Object/dependency enumeration differs')
        expected_sources={entry.resolve()} if group==target else {(root/n).resolve() for n in expected_scalar}
        selected=[]
        for command in commands:
            require(isinstance(command,dict) and isinstance(command.get('file'),str), 'Invalid compile command')
            cwd=Path(command.get('directory','')).resolve()
            raw_tokens=command.get('arguments') or shlex.split(command.get('command',''))
            require(isinstance(raw_tokens,list) and all(isinstance(x,str) for x in raw_tokens), 'Invalid raw compiler arguments')
            tokens=expand_responses(raw_tokens,build,records)
            require(isinstance(tokens,list) and all(isinstance(x,str) for x in tokens), 'Invalid ordered compiler arguments')
            if '-o' not in tokens:continue
            offset=tokens.index('-o');require(offset+1<len(tokens), 'Missing object output')
            obj=(cwd/tokens[offset+1]).resolve()
            if not obj.is_relative_to(directory.resolve()):continue
            require(cwd==build.resolve(), 'Compiler working directory mismatch')
            require(obj in {p.resolve() for p in objects}, 'Command output object absent')
            source=(cwd/command['file']).resolve();require(source in expected_sources, 'Unexpected compiled source')
            require('-c' in tokens and (cwd/tokens[tokens.index('-c')+1]).resolve()==source, 'Compile source argument mismatch')
            require(Path(tokens[0]).resolve()==Path(tools['CMAKE_CXX_COMPILER' if source.suffix!='.c' else 'CMAKE_C_COMPILER']), 'Actual compiler differs from cache')
            require('-ffp-contract=off' in tokens, 'Scalar rounding flag absent')
            require(str(obj) not in ordered_commands, 'Duplicate compiler object')
            ordered_commands[str(obj)]={'raw':raw_tokens,'expanded':tokens};selected.append((source,obj))
            depset=dependencies(Path(str(obj)+'.d'),build,obj,dependency_identities)
            require(source in depset, 'Source absent from .o.d')
            actual_dependencies.update(depset);dep_records.add(Path(str(obj)+'.d'));object_records.add(obj)
            if group==target:
                require(build/'generated/models.hpp' in depset, 'Actual generated header absent from dependencies')
                schedule_headers={p for p in depset if p.name=='schedule.hpp' and p.parent.name=='atlas'}
                if request['schedule']=='required':require(schedule_headers=={schedule}, 'Actual schedule selection/exclusion failed')
                else:require(not schedule_headers, 'Time-only target cannot claim schedule selection')
                inc=[];i=0
                while i<len(tokens):
                    if tokens[i]=='-I':i+=1;inc.append((cwd/tokens[i]).resolve())
                    elif tokens[i].startswith('-I'):inc.append((cwd/tokens[i][2:]).resolve())
                    i+=1
                expected=[root/'runtimes/physical-time-v2/include',root/'cpp/include',build/'generated']
                require(all(p in inc for p in expected) and [inc.index(p) for p in expected]==sorted(inc.index(p) for p in expected), 'Ordered actual include roots differ')
                includes[str(obj)]=[str(p) for p in inc]
        require({s for s,o in selected}==expected_sources and len(selected)==len(expected_sources), 'Compiled source records incomplete')
        require({o for s,o in selected}=={p.resolve() for p in objects}, 'Unrecorded target objects')
        units[group]=[(str(s),str(o)) for s,o in selected]
    require(legacy not in actual_dependencies, 'Legacy common schedule included')
    archive=local(build,'libatlas_scalar_functions.a');digest(archive);records.add(archive)
    scalar_objects={Path(o).name:digest(Path(o)) for source,o in units['atlas_scalar_functions']}
    require(archive_members(archive)==scalar_objects, 'Scalar archive members differ from exact object set/bytes')
    for group in [target,'atlas_scalar_functions']:
        link_lines=[line for line in (build/'CMakeFiles'/(group+'.dir')/'link.txt').read_text().splitlines() if line.strip()]
        require(len(link_lines)==(1 if group==target else 2), 'Unexpected target/archive link command count')
        words=expand_responses(shlex.split(link_lines[0]),build,records)
        if group=='atlas_scalar_functions':
            ranlib=expand_responses(shlex.split(link_lines[1]),build,records)
            require(len(ranlib)==2 and Path(ranlib[0]).resolve()==Path(tools['CMAKE_RANLIB']) and (build/ranlib[1]).resolve()==archive, 'Actual ranlib command differs')
        require(Path(words[0]).resolve()==Path(tools['CMAKE_CXX_COMPILER' if group==target else 'CMAKE_AR']), 'Actual linker/archive tool differs from recorded tool')
        paths={(build/word).resolve() for word in words if not word.startswith('-')}
        require(archive.resolve() in paths, 'Scalar archive absent from actual link/archive command')
        if group==target:
            require(words.count('-o')==1 and words.index('-o')+1<len(words), 'Actual target link output absent')
            linked_output=(build/words[words.index('-o')+1]).resolve()
        required_objects={Path(o) for s,o in units[group]}
        require(required_objects.issubset(paths), 'Object missing from actual link/archive command')
    artifacts=[local(build,n) for n in request['artifacts']]
    require(len(artifacts)==len(set(artifacts)), 'Duplicate artifacts')
    if request['kind']=='native':
        require(request['artifacts']==[target], 'Native artifact must be exact target executable')
        require(os.access(artifacts[0],os.X_OK), 'Native artifact is not executable')
    else:
        require(len(artifacts)==3 and {p.suffix for p in artifacts}=={'.js','.mjs','.wasm'} and len({p.stem for p in artifacts})==1, 'Wasm originalJS/module/Wasm trio required')
        original=next(p for p in artifacts if p.suffix=='.js');alias=next(p for p in artifacts if p.suffix=='.mjs')
        require(digest(original)==digest(alias), 'Copied module differs from original JS')
    for p in artifacts: digest(p)
    require(linked_output==next((p for p in artifacts if p.suffix=='.js'),artifacts[0]), 'Actual link output differs from captured artifact')
    records |= generated | dep_records | object_records | actual_dependencies | set(artifacts) | sources
    files={str(p.resolve()):digest(p) for p in sorted(records)}
    return {'dependency_identities':dependency_identities,'dependency_identity_contract':'ordered-lexical-canonical-symlink-chain-v2','files':files,'source_files':[str(p.resolve()) for p in sorted(sources)],'objects':sorted(str(p) for p in object_records),'dependency_records':sorted(str(p) for p in dep_records),'ordered_compile_commands':ordered_commands,'ordered_include_roots':includes,'tool_paths':tools,'compiler_versions':compiler_versions,'generator_command':generator_commands[0],'catalogue_hash':catalogue_hash,'schedule_mode':request['schedule'],'actual_schedule_headers':sorted(str(p) for p in actual_dependencies if p.name=='schedule.hpp' and p.parent.name=='atlas'),'artifacts':{str(p):digest(p) for p in artifacts},'current_release_source_not_historical_substitution':True,'scope':'Pre/post integrity of existing build records; no execution, binary attestation, numerical approval or general toolchain reproducibility claim'}

def fresh(path,data):
    require(not path.exists() and not path.is_symlink(), 'Receipt/output already exists')
    require(path.parent.is_dir(), 'Receipt parent must already exist')
    require(not any(p.is_symlink() for p in [path.parent,*path.parent.parents]), 'Symlink in receipt parent')
    with path.open('xb') as stream:stream.write(data)

def capture(request,receipt):
    require(receipt.is_absolute() and receipt.parent.is_dir(), 'Absolute receipt with existing parent required')
    require(not any(p.is_symlink() for p in [receipt.parent,*receipt.parent.parents]), 'Symlink in receipt parent')
    require(not receipt.exists() and not Path(str(receipt)+'.sha256').exists(), 'Fresh receipt and seal required')
    before=snapshot(request)
    evidence=Path(str(receipt)+'.evidence');require(not evidence.exists() and not evidence.is_symlink(), 'Fresh evidence directory required')
    evidence.mkdir()
    build=(Path(request['root'])/request['build']).resolve();copied={}
    for name,expected in before['files'].items():
        source=Path(name)
        if not source.is_relative_to(build):continue
        relative=source.relative_to(build);target=evidence/relative;target.parent.mkdir(parents=True,exist_ok=True)
        with source.open('rb') as source_stream, target.open('xb') as target_stream:shutil.copyfileobj(source_stream,target_stream)
        require(digest(target)==expected, 'Build record changed during evidence copy');copied[relative.as_posix()]=expected
    require(copied and snapshot(request)==before, 'Build/source changed during capture')
    value={'kind':'atlas-cmake-profile-build-pre-v2','captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':request,'snapshot':before,'retained_build_records':{'directory':str(evidence.resolve()),'files':copied}}
    data=json.dumps(value,indent=2,allow_nan=False).encode()+b'\n';fresh(receipt,data)
    fresh(Path(str(receipt)+'.sha256'),(hashlib.sha256(data).hexdigest()+'\n').encode())
    return value

def verify(receipt,expected,output):
    require(bool(re.fullmatch('[0-9a-f]{64}',expected)), 'Expected pre-receipt SHA256 required')
    require(digest(receipt)==expected, 'Pre-receipt changed')
    value=parse_json(receipt);require(set(value)=={'kind','captured_utc','request','snapshot','retained_build_records'} and value['kind']=='atlas-cmake-profile-build-pre-v2', 'Unexpected pre-receipt')
    retained=value['retained_build_records'];directory=Path(retained['directory'])
    require(directory==Path(str(receipt)+'.evidence').resolve() and not directory.is_symlink(), 'Evidence directory differs')
    actual={}
    for p in directory.rglob('*'):
        if p.is_file():local(directory,p.relative_to(directory));actual[p.relative_to(directory).as_posix()]=digest(p)
    require(actual==retained['files'], 'Retained build records changed or incomplete')
    after=snapshot(value['request']);require(after==value['snapshot'], 'Source/build/tool/artifact identity or enumeration changed after call')
    fresh(output,json.dumps({'kind':'atlas-cmake-profile-build-post-v2','pre_receipt_sha256':expected,'all_records_unchanged':True,'material_call_result':'Caller reached this command after successful consumer; helper does not execute or attest consumer','files_verified':len(after['files'])},indent=2).encode()+b'\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    pre=sub.add_parser('capture')
    for name in ['root','build','target','entrypoint','recipe','models','schedule','kind','receipt']:pre.add_argument('--'+name,required=True)
    pre.add_argument('--artifact',action='append',required=True);pre.add_argument('--consumer-tool',action='append',required=True);pre.add_argument('--consumer-source',action='append',default=[])
    post=sub.add_parser('verify');post.add_argument('--receipt',type=Path,required=True);post.add_argument('--receipt-sha256',required=True);post.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.action=='verify':verify(args.receipt,args.receipt_sha256,args.output);print('PASS: pre-call source/build/tool/artifact identities unchanged');return
    request={k:getattr(args,k) for k in ['root','build','target','entrypoint','recipe','models','schedule','kind']}
    request['root']=str(Path(request['root']).resolve());request.update(artifacts=args.artifact,consumer_tools=args.consumer_tool,consumer_sources=args.consumer_source)
    try:
        value=capture(request,Path(args.receipt));print(json.dumps({'files':len(value['snapshot']['files']),'schedule_headers':value['snapshot']['actual_schedule_headers'],'pre_receipt_sha256':digest(Path(args.receipt))}))
    except Exception as error:
        failed=Path(args.receipt+'.failure.json')
        if failed.parent.is_dir() and not failed.exists():fresh(failed,json.dumps({'kind':'atlas-cmake-profile-build-failed-v2','request':request,'error_type':type(error).__name__,'error':str(error),'compiled_or_material_calls':0},indent=2).encode()+b'\n')
        raise
if __name__=='__main__':main()
