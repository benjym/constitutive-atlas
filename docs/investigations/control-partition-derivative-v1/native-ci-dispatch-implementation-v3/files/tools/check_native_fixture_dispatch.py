"""Closed catalogue dispatch around unchanged archival/published native contracts."""
import sys
sys.dont_write_bytecode=True
import argparse,base64,hashlib,importlib.util,json,os,re,shutil,subprocess,time
from pathlib import Path
try:
    from tools import check_md1997_native_fixture_contract as md
except ModuleNotFoundError:
    import check_md1997_native_fixture_contract as md

ROOT=Path(__file__).resolve().parents[1]
TIMEOUT=120
CTEST_TIMEOUT=1800
SUITES={'macos-main':['-E','^atlas_recorded$'],'linux-main':['-E','^(atlas_python|atlas_recorded)$'],'recorded':['-R','^atlas_recorded$']}
NATIVE_CMAKE_SHA256='61f7fb538fcb1f2d03259ed4eda531fc9f41bc6119ffed56f3ea49dd8c762a0d'
REGISTRATIONS=[('atlas_numerical','atlas_numerical_tests',[]),('atlas_recorded','atlas_recorded_tests',[]),('atlas_tensor_square','atlas_tensor_square_tests',[]),('atlas_python',None,['-m','unittest','discover','-s','tests','-v']),('atlas_time','atlas_time_tests',[]),('atlas_capacity','atlas_capacity_tests',[]),('atlas_recorded_fixture','atlas_recorded_fixture_tests',[]),('atlas_expm_context','atlas_expm_probe',['0,0,0,0,0,0','1']),('atlas_log1p_context','atlas_log1p_probe',['0']),('atlas_scalar_functions',None,[])]
IDENTITIES={'14': {'models': {'barodesy-clay-2017': '0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477', 'barodesy-sand': '3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239', 'drucker-prager': 'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877', 'hypoplastic-clay-2005': '247de2f1792cf220748671b4563c7dd290c5b91fcc95eda5977ac03e01fa6ff5', 'hypoplastic-clay-2013': '6811580cf9c0678605b9bb7d93a524743bbe5b5cb1f547bd232d090aeda950e4', 'hypoplastic-sand-igs97': '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86', 'hypoplastic-sand-vw96': '1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61', 'linear-elastic': '33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041', 'modified-cam-clay': 'e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14', 'mohr-coulomb': '6a3a139218fc413f066abe5b851c5c7aed8899ee23efbd7ae2a2e68c7655f0e5', 'research-hp-extracted-asbs-gis-2024-v03': '439b785e1da3075209c6d5ca43a991a441463a915f31f2e9c77b5c6835e20dbc', 'tresca-associated-perfect-bk2022v1-be': '19acebed37d59120e49c5dff698e2b7d2a2693bbce9ec35c8bcbc65954819e18', 'original-cam-clay-sw-electronic-log-recovery-v1': '637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34', 'duncan-chang-1970-endpoint-average': '452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'}, 'catalogue_embedded_sha256': '38f03e0099cfee9c89deaa59e729ac43563d4d39b17d321721a199e58d3b77d4', 'catalogue_file_sha256': '77e85070a62ada86d47af3890817f57d6ce0194e646a396dbf7ff75c75f9834a', 'policy_id': 'supported-package-fourteen-duncan-v1'}, '15': {'models': {'barodesy-clay-2017': '0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477', 'barodesy-sand': '3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239', 'drucker-prager': 'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877', 'hypoplastic-clay-2005': '247de2f1792cf220748671b4563c7dd290c5b91fcc95eda5977ac03e01fa6ff5', 'hypoplastic-clay-2013': '6811580cf9c0678605b9bb7d93a524743bbe5b5cb1f547bd232d090aeda950e4', 'hypoplastic-sand-igs97': '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86', 'hypoplastic-sand-vw96': '1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61', 'linear-elastic': '33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041', 'modified-cam-clay': 'e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14', 'mohr-coulomb': '6a3a139218fc413f066abe5b851c5c7aed8899ee23efbd7ae2a2e68c7655f0e5', 'research-hp-extracted-asbs-gis-2024-v03': '439b785e1da3075209c6d5ca43a991a441463a915f31f2e9c77b5c6835e20dbc', 'tresca-associated-perfect-bk2022v1-be': '19acebed37d59120e49c5dff698e2b7d2a2693bbce9ec35c8bcbc65954819e18', 'original-cam-clay-sw-electronic-log-recovery-v1': '637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34', 'duncan-chang-1970-endpoint-average': '452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0', 'ramberg-osgood-ansys242': 'c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2'}, 'catalogue_embedded_sha256': '29c12dec5d2ec9ce1ea84b8991757e4f03af1122a92095689c5b6f81b64c342f', 'catalogue_file_sha256': 'e07f3a21927b28aad8865085216f17d7152dc6f6a67c3663cabbe97c78b606ee', 'policy_id': 'supported-package-fifteen-ramberg-v1'}, '16': {'models': {'barodesy-clay-2017': '0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477', 'barodesy-sand': '3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239', 'drucker-prager': 'b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877', 'hypoplastic-clay-2005': '247de2f1792cf220748671b4563c7dd290c5b91fcc95eda5977ac03e01fa6ff5', 'hypoplastic-clay-2013': '6811580cf9c0678605b9bb7d93a524743bbe5b5cb1f547bd232d090aeda950e4', 'hypoplastic-sand-igs97': '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86', 'hypoplastic-sand-vw96': '1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61', 'linear-elastic': '33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041', 'modified-cam-clay': 'e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14', 'mohr-coulomb': '6a3a139218fc413f066abe5b851c5c7aed8899ee23efbd7ae2a2e68c7655f0e5', 'research-hp-extracted-asbs-gis-2024-v03': '439b785e1da3075209c6d5ca43a991a441463a915f31f2e9c77b5c6835e20dbc', 'tresca-associated-perfect-bk2022v1-be': '19acebed37d59120e49c5dff698e2b7d2a2693bbce9ec35c8bcbc65954819e18', 'original-cam-clay-sw-electronic-log-recovery-v1': '637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34', 'duncan-chang-1970-endpoint-average': '452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0', 'ramberg-osgood-ansys242': 'c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2', 'manzari-dafalias-1997-constant-m-be-v1': '28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'}, 'catalogue_embedded_sha256': 'bedc53e3186a253e9f1e1545a7e46a5fc8fd9f76dce4f5b9721edc21347e9e7c', 'catalogue_file_sha256': 'f38da28fd2857e03e1def0c2ed70dc2a5b999984ef087360b324c933a2da3a99', 'policy_id': 'prospective16qualification-map; no scientific admission/policy16 fabricated'}}
HELPERS={'14':'2ec42239c58d823d7d0575f57918b07451186fc4f46ef44aacf4d9338fa34609','15':'37db9c734030735d2290e6e4e0935ed714a8b2e5d349678a881e6d69afb35a7a','16':'37db9c734030735d2290e6e4e0935ed714a8b2e5d349678a881e6d69afb35a7a'}
POLICIES={'14':'f0e242cfd9592ab3bf94ab1af16517a347a4bfcdded6fde24d84c73656297094','15':'915a91d2c6ee5ce7fba70f484a50beba313f4f4dc340283af0e2c4a823983029','16':'915a91d2c6ee5ce7fba70f484a50beba313f4f4dc340283af0e2c4a823983029'}

def require(condition,message):
    if not condition:raise ValueError(message)

def sha(data):return hashlib.sha256(data).hexdigest()

def unique(pairs):
    obj={}
    for key,value in pairs:
        require(key not in obj,'duplicate JSON key: '+key);obj[key]=value
    return obj

def strict_json(raw):
    def bad(value):raise ValueError('nonfinite JSON: '+value)
    obj=json.loads(raw,object_pairs_hook=unique,parse_constant=bad)
    json.dumps(obj,allow_nan=False) # reject exponent overflow too
    return obj

def digest_file(path):
    require(path.is_file() and not path.is_symlink(),'missing/symlink file: '+str(path))
    return sha(path.read_bytes())

def classify(raw,source):
    blob=strict_json(raw)
    require(set(blob)=={'schema_version','sha256','models'} and blob['schema_version']=='0.1','unknown generated schema')
    models=blob['models'];require(type(models) is list,'models must be list')
    ids=[m['id'] for m in models]
    require(all(type(x) is str for x in ids) and ids==sorted(set(ids)),'duplicate/reordered/invalid IDs')
    require(any(set(ids)==set(f['models']) for f in IDENTITIES.values()),'unknown model set')
    mapping={name:digest_file(source/'models'/(name+'.json')) for name in ids}
    matches=[size for size,frozen in IDENTITIES.items() if frozen['models']==mapping]
    require(len(matches)==1,'unknown exact catalogue mapping')
    size=matches[0];frozen=IDENTITIES[size]
    require(sha(raw)==frozen['catalogue_file_sha256'],'generated file identity mismatch')
    require(blob['sha256']==frozen['catalogue_embedded_sha256'],'embedded catalogue identity mismatch')
    require(models==[strict_json((source/'models'/(name+'.json')).read_bytes()) for name in ids],'generated objects differ from exact source objects')
    require(sha(json.dumps(models,sort_keys=True,separators=(',',':'),allow_nan=False).encode())==blob['sha256'],'computed catalogue digest mismatch')
    # Do not silently drop an unrecognised source model from catalogue input.
    require({p.stem for p in (source/'models').glob('*.json')}==set(ids),'source catalogue has missing/extra model files')
    return size,blob,mapping

def load_helper(source,size):
    path=source/'tools/check_native_fixture_contracts.py'
    require(digest_file(path)==HELPERS[size],'wrong original helper context')
    spec=importlib.util.spec_from_file_location('_unchanged_native_contract_'+size,path)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    return helper

def canonical_ctest_text(source,build,registrations):
    """Exact CMake4.4.3 serialization of the pinned native registration source.

    Fail closed on every byte outside this source-derived grammar. In particular
    comments, backtrace fields and property syntax are not execution loopholes.
    A generator/source format change needs a separately reviewed identity.
    """
    cmake=(source/'CMakeLists.txt').read_text()
    require(digest_file(source/'CMakeLists.txt')==NATIVE_CMAKE_SHA256,'unqualified native CMake source identity')
    for value in [str(source),str(build),*(token for row in registrations for token in row)]:
        require(not any(c in value for c in ['\n','\r','\\','$',';','\x00']),'unsupported interpolating/escaped CTest path or token')
    matches=list(re.finditer(r'(?m)^[ \t]*add_test\(NAME ([^ ]+) COMMAND',cmake))
    source_lines={m.group(1):cmake.count('\n',0,m.start())+1 for m in matches}
    require(list(source_lines)==[r[0]for r in registrations],'source registration metadata mismatch')
    env_source=re.findall(r'(ATLAS_[A-Z0-9_]+)=\$<TARGET_FILE:([^>]+)>',cmake)
    require([k for k,_ in env_source]==['ATLAS_SOLVER','ATLAS_TIME_SOLVER','ATLAS_RESEARCH_SOLVER','ATLAS_HISTORY_SOLVER','ATLAS_CLAY2013_SOLVER','ATLAS_GIS2024_SOLVER'],'source Python environment binding mismatch')
    environment=';'.join(k+'='+str(build/target)for k,target in env_source)
    require('WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" ENVIRONMENT' in cmake,'source Python working directory mismatch')
    quote=lambda text:json.dumps(text,ensure_ascii=False)
    text='# CMake generated Testfile for \n# Source directory: '+str(source)+'\n# Build directory: '+str(build)+'\n# \n# This file includes the relevant testing commands required for \n# testing this directory and lists subdirectories to be tested as well.\n'
    for row in registrations:
        name=row[0]
        text+='add_test('+' '.join(quote(token)for token in row)+')\n'
        backtrace=str(source/'CMakeLists.txt')+';'+str(source_lines[name])+';add_test;'+str(source/'CMakeLists.txt')+';0;'
        properties=('_BACKTRACE_TRIPLES '+quote(backtrace))if name!='atlas_python'else ('ENVIRONMENT '+quote(environment)+' WORKING_DIRECTORY '+quote(str(source))+' _BACKTRACE_TRIPLES '+quote(backtrace))
        text+='set_tests_properties('+quote(name)+' PROPERTIES  '+properties+')\n'
    return text

def validate_registrations(source,build,cache):
    require(digest_file(source/'CMakeLists.txt')==NATIVE_CMAKE_SHA256,'unqualified native CMake source identity')
    source_rows=re.findall(r'add_test\(NAME ([^ ]+) COMMAND', (source/'CMakeLists.txt').read_text())
    require(source_rows==[r[0]for r in REGISTRATIONS],'source native registration inventory changed')
    python_entries=[line.split('=',1)[1]for line in cache.splitlines()if line.startswith(('_Python3_EXECUTABLE:INTERNAL=','Python3_EXECUTABLE:FILEPATH='))]
    require(python_entries and len({str(Path(p).resolve())for p in python_entries})==1,'missing/ambiguous CMake Python executable')
    python=Path(python_entries[0])
    require(python.is_absolute(),'CMake Python executable must be absolute')
    suffix='.dylib'if sys.platform=='darwin'else '.so'if sys.platform.startswith('linux')else None
    require(suffix is not None,'unqualified native platform')
    scalar=build/('libatlas_scalar_probe'+suffix)
    expected=[]
    for name,target,args in REGISTRATIONS:
        if name=='atlas_scalar_functions':command=[str(python),str(source/'tools/test_scalar_functions.py'),str(scalar)]
        elif target is None:command=[str(python),*args]
        else:command=[str(build/target),*args]
        expected.append([name,*command])
    text=(build/'CTestTestfile.cmake').read_text();observed=[]
    for line in text.splitlines():
        line=line.strip()
        require(not re.match(r'(?:subdirs|include)\s*\(',line,re.I),'unexpected external CTest registration')
        if re.match(r'add_test\b',line,re.I):
            match=re.fullmatch(r'add_test\(((?:"(?:[^"\\]|\\.)*"\s*)+)\)',line)
            require(match is not None,'unqualified CTest registration syntax')
            observed.append([json.loads(token)for token in re.findall(r'"(?:[^"\\]|\\.)*"',match.group(1))])
    require(observed==expected,'generated native registration identity/order/command mismatch')
    require(text==canonical_ctest_text(source,build,expected),'generated CTest properties/full-file grammar differ from pinned source')
    # Bind every registration's executable and the scalar test's script/library,
    # not only the two strict-contract executables.
    artifacts={str(Path(row[1])):digest_file(Path(row[1]))for row in expected}
    for path in [source/'tools/test_scalar_functions.py',scalar]:artifacts[str(path)]=digest_file(path)
    return expected,artifacts

def context(catalogue,source,build):
    require(__debug__,'original analytical helper requires Python assertions enabled')
    source=source.resolve();build=build.resolve();catalogue=catalogue.resolve()
    require(catalogue==build/'generated/models.json','catalogue is not this build generated catalogue')
    raw=catalogue.read_bytes();size,blob,mapping=classify(raw,source)
    helper=load_helper(source,size)
    policy=source/'catalogue/laboratory-package-policy.json'
    require(digest_file(policy)==POLICIES[size],'wrong original policy context')
    policy_obj=strict_json(policy.read_bytes())
    require(policy_obj['models']==IDENTITIES['14' if size=='14' else '15']['models'],'policy mapping mismatch')
    cache=(build/'CMakeCache.txt').read_text()
    entries=[line.split('=',1)[1] for line in cache.splitlines() if line.startswith('CMAKE_HOME_DIRECTORY:INTERNAL=')]
    require(len(entries)==1 and Path(entries[0]).resolve()==source,'CMake build source binding mismatch')
    registrations,registered_artifacts=validate_registrations(source,build,cache)
    bindings={str(p.relative_to(source)):digest_file(p) for folder in ['models','cpp','atlas','schemas','tests','tools','cmake','catalogue','.github'] for p in sorted((source/folder).rglob('*')) if p.is_file() and p.suffix not in ['.pyc'] and '__pycache__' not in p.parts}
    bindings['CMakeLists.txt']=digest_file(source/'CMakeLists.txt')
    artifacts={name:digest_file(build/name) for name in ['atlas_numerical_tests','atlas_recorded_tests','generated/models.json','generated/models.hpp','CTestTestfile.cmake','CMakeCache.txt']}
    meta={'route':size,'catalogue_path':str(catalogue),'catalogue_file_sha256':sha(raw),'catalogue_embedded_sha256':blob['sha256'],'model_definitions':mapping,'source_root':str(source),'build':str(build),'source_files':bindings,'original_helper_sha256':digest_file(source/'tools/check_native_fixture_contracts.py'),'policy_sha256':digest_file(policy),'policy_id':policy_obj['id'],'artifacts':artifacts,'registrations':registrations,'registered_artifacts':registered_artifacts,'dispatcher_sha256':digest_file(Path(__file__)),'md_contract_helper_sha256':digest_file(Path(md.__file__))}
    return meta,helper

def original_contracts(size):
    rows=[]
    for target in ['atlas_numerical_tests','atlas_recorded_tests']:
        for profile in [None,'unknown']:
            rows.append(dict(id=target+('-default' if profile is None else '-unknown-native'),target=target,native_selector=profile,numerical_selector=None,returncode=1,stdout='' if profile else 'Strict original default fixtures; models='+size+'\n',stderr='unknown native fixture profile\n' if profile else ('FD test outside domain\n' if target=='atlas_numerical_tests' else None)))
    return rows

def recorded(message,meta,helper):
    mapping=meta['model_definitions']
    # Full route validation is a precondition, never infer sixteen from a subset.
    require(mapping==IDENTITIES[meta['route']]['models'],'recorded caller mapping not qualified')
    if meta['route']=='16':
        mapping=dict(mapping);del mapping['manzari-dafalias-1997-constant-m-be-v1']
        require(mapping==IDENTITIES['15']['models'],'MD projection differs from published fifteen')
    return helper.check_recorded_failure(message,mapping,root=Path(meta['source_root']))

class Receipt:
    def __init__(self,output,operation):
        self.output=Path(output)
        self.output.parent.mkdir(parents=True,exist_ok=True)
        # Exclusive creation occurs before any observation, and never overwrites.
        with self.output.open('x') as handle:handle.write('{}\n')
        self.value={'identity':'native-fixture-closed-dispatch-v3','operation':operation,'status':'running','processes':[]}
        self.save()
    def save(self):
        self.output.write_text(json.dumps(self.value,indent=2,allow_nan=False)+'\n')
    def process(self,argv,env,timeout,runner=subprocess.run):
        selectors={k:env[k] for k in md.SELECTORS if k in env}
        row={'argv':list(map(str,argv)),'timeout_seconds':timeout,'requested_selectors':selectors,'effective_selectors':selectors,'status':'started'}
        self.value['processes'].append(row);self.save()
        try:
            result=runner(row['argv'],env=env,capture_output=True,timeout=timeout)
            row['returncode']=result.returncode
            self.raw(row,result.stdout,result.stderr)
            row['status']='completed';self.save();return row
        except BaseException as exc:
            row.update(status='failed',error_type=type(exc).__name__,error=str(exc));self.save()
            if isinstance(exc,subprocess.TimeoutExpired):
                row['timeout_expired']=True;row['timeout_command']=list(map(str,exc.cmd))if isinstance(exc.cmd,(list,tuple))else str(exc.cmd);row['timeout_elapsed_limit']=exc.timeout;self.save()
                try:self.raw(row,exc.stdout or b'',exc.stderr or b'')
                except UnicodeDecodeError as decode:
                    row['decode_error']={'type':type(decode).__name__,'message':str(decode)};self.save()
            raise
    def raw(self,row,stdout,stderr):
        for key,data in [('stdout',stdout),('stderr',stderr)]:
            require(type(data) is bytes,'transport must return raw bytes')
            row[key+'_base64']=base64.b64encode(data).decode('ascii')
            row[key+'_sha256']=sha(data)
            # Retain bytes even when decoding fails.
        self.save()
        for key,data in [('stdout',stdout),('stderr',stderr)]:row[key]=data.decode('utf-8',errors='strict')
        self.save()

def verify_original(row,expected,meta,helper):
    require(row.get('status')=='completed','original process incomplete')
    for field in ['returncode','stdout']:
        require(type(row.get(field)) is type(expected[field]) and row[field]==expected[field],'strict original mismatch: '+field)
    require(row['effective_selectors']==({md.SELECTORS[0]:'unknown'} if expected['native_selector'] else {}),'strict selector mismatch')
    if expected['stderr'] is None:row['strict_context']=recorded(row['stderr'],meta,helper)
    else:require(row['stderr']==expected['stderr'],'strict original stderr mismatch')

def check_contracts(meta,helper,receipt,base_env,runner=subprocess.run):
    source=Path(meta['source_root']);build=Path(meta['build']);size=meta['route']
    if size in ['14','15']:
        # Delegate exact helper main in its matching source context. Its four
        # strict subprocesses remain unchanged; inspect complete saved rows too.
        delegated=receipt.output.with_name(receipt.output.stem+'-original-helper.json')
        require(not delegated.exists(),'preserve delegated original observations')
        receipt.value['delegated_original_report_path']=str(delegated);receipt.save()
        env=md.selector_env(base_env)
        require(not env.get('PYTHONOPTIMIZE'),'original helper assertions must not be disabled')
        try:
            row=receipt.process([sys.executable,'-B',str(source/'tools/check_native_fixture_contracts.py'),'--build',str(build),'--output',str(delegated)],env,TIMEOUT*4+30,runner)
        finally:
            if delegated.is_file():
                raw=delegated.read_bytes();receipt.value['delegated_original_report_raw']={'sha256':sha(raw),'base64':base64.b64encode(raw).decode('ascii')};receipt.save()
        require(row['returncode']==0 and row['stderr']=='','unchanged original helper failed')
        report=strict_json(delegated.read_bytes());receipt.value['delegated_original_report']=report
        receipt.value['delegated_original_report_sha256']=digest_file(delegated);receipt.save()
        require(report['status']=='passed' and report['model_count']==int(size) and report['policy_id']==meta['policy_id'],'wrong delegated report identity')
        require(len(report['processes'])==4,'wrong delegated process count')
        for observed,expected in zip(report['processes'],original_contracts(size)):
            require(observed['target']==expected['target'] and observed['profile']==expected['native_selector'],'wrong delegated strict call order')
            normalized=dict(observed,status='completed',effective_selectors={md.SELECTORS[0]:'unknown'} if observed['profile'] else {})
            verify_original(normalized,expected,meta,helper)
        return
    for expected in original_contracts(size)+md.contracts():
        env=md.selector_env(base_env,expected['native_selector'],expected['numerical_selector'])
        row=receipt.process([str(build/expected['target'])],env,TIMEOUT,runner)
        row['id']=expected['id'];row['requested_selectors']={k:env[k] for k in md.SELECTORS if k in env};receipt.save()
        if expected['id'].startswith('atlas_'):verify_original(row,expected,meta,helper)
        else:md.verify(row,expected)
        receipt.save()

def ctest(meta,suite,receipt,base_env,runner=subprocess.run):
    require(suite in SUITES,'unknown CTest suite')
    env=md.selector_env(base_env,md.NATIVE,md.NUMERICAL if meta['route']=='16' and suite!='recorded' else None)
    ctest_executable=shutil.which('ctest')
    require(ctest_executable is not None,'ctest executable not found')
    resolved_ctest=Path(ctest_executable).resolve()
    receipt.value['ctest_executable_sha256']=digest_file(resolved_ctest)
    receipt.value['ctest_executable_path']=ctest_executable;receipt.value['ctest_executable_resolved_path']=str(resolved_ctest);receipt.save()
    log=Path(meta['build'])/'Testing/Temporary/LastTest.log'
    if log.is_file():
        raw=log.read_bytes();receipt.value['previous_ctest_log']={'path':str(log),'sha256':sha(raw),'base64':base64.b64encode(raw).decode('ascii')};receipt.save()
        # Preserve exact prior log in this immutable observation receipt before
        # clearing the mutable CTest location, so stale success cannot qualify.
        log.unlink()
    try:
        row=receipt.process([ctest_executable,'--test-dir',meta['build'],'--output-on-failure',*SUITES[suite]],env,CTEST_TIMEOUT,runner)
    finally:
        if log.is_file():
            raw=log.read_bytes();receipt.value['ctest_log']={'path':str(log),'sha256':sha(raw),'base64':base64.b64encode(raw).decode('ascii')};receipt.save()
    selected_after=shutil.which('ctest')
    receipt.value['ctest_postflight']={'selected_path':selected_after,'same_path':selected_after==ctest_executable}
    if selected_after==ctest_executable:
        resolved_after=Path(selected_after).resolve()
        receipt.value['ctest_postflight']['resolved_path']=str(resolved_after)
        receipt.value['ctest_postflight']['sha256']=digest_file(resolved_after)
    receipt.save()
    require(selected_after==ctest_executable and receipt.value['ctest_postflight'].get('resolved_path')==str(resolved_ctest) and receipt.value['ctest_postflight'].get('sha256')==receipt.value['ctest_executable_sha256'],'CTest executable path/content changed during observation')
    require(type(row['returncode']) is int and row['returncode']==0,'positive CTest suite failed')
    require(log.is_file(),'missing positive CTest log')
    names=[row[0]for row in meta['registrations']]
    expected=[n for n in names if (re.search(SUITES[suite][1],n) is not None)==(SUITES[suite][0]=='-R')]
    observed=re.findall(r'^\d+/\d+ Testing: ([^\n]+)$',raw.decode('utf-8',errors='strict'),re.M)
    require(expected and observed==expected,'CTest log coverage/order differs from full selected suite')
    sections=re.split(r'(?m)(?=^\d+/\d+ Testing: )',raw.decode('utf-8',errors='strict'))[1:]
    require(len(sections)==len(expected) and all(s.count('Test Passed.')==1 and 'Test Failed.' not in s for s in sections),'CTest did not pass every selected test')
    if meta['route']=='16' and suite!='recorded':md.verify_positive_log(raw.decode('utf-8',errors='strict'))

def execute(operation,catalogue,source,build,output,suite=None,runner=subprocess.run,base_env=None):
    receipt=Receipt(output,operation)
    receipt.value['requested_context']={'catalogue':str(catalogue),'source_root':str(source),'build':str(build),'suite':suite};receipt.save()
    try:
        meta,helper=context(Path(catalogue),Path(source),Path(build));receipt.value['context']=meta;receipt.save()
        if operation=='check':check_contracts(meta,helper,receipt,os.environ if base_env is None else base_env,runner)
        elif operation=='ctest':ctest(meta,suite,receipt,os.environ if base_env is None else base_env,runner)
        else:raise ValueError('unknown operation')
        after,_=context(Path(catalogue),Path(source),Path(build))
        require(meta==after,'source/build/artifact identity changed during observations')
        receipt.value['status']='passed';receipt.save();return receipt.value
    except BaseException as exc:
        receipt.value.update(status='failed',error_type=type(exc).__name__,error=str(exc));receipt.save();raise

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['check','ctest'])
    for name in ['catalogue','source-root','build','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--suite',choices=sorted(SUITES));a=p.parse_args()
    if (a.operation=='ctest')!=(a.suite is not None):p.error('--suite required only with ctest')
    execute(a.operation,a.catalogue,a.source_root,a.build,a.output,a.suite)

if __name__=='__main__':main()
