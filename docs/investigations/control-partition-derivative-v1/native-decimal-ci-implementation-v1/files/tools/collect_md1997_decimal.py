"""Closed Decimal fixture transport. No reference generation or material law."""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Unoptimized Python required')
import base64,hashlib,importlib.util,json,os,re,shutil,subprocess
from pathlib import Path
NATIVE='explicit-gis20-occ-restart-duncan-v5'
NUMERICAL='md1997-decimal-fd-reference-v1'
BUILD_ENV='ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256'
HASH=re.compile(r'[0-9a-f]{64}\Z')
MAX_OUTPUT=4*1024*1024
SUPPORT=Path(__file__).resolve().parent/'md1997_decimal_reference'
SUPPORT_HASHES={'assess_saved.py': '494555791f207a158d890c4b614526f605373d7b8ba945b09461025e5874b052', 'decimal_dsl.py': 'c0d7c733db1432f67370d832c6f4a9dc6db5b94ba2ddfa0955cec39aadf91668', 'POLICY.md': '79152e516054320064d67b9dc333be0945d6738362b4ab17b968ffaaf84f087c', 'requests.json': 'ee4158da6cc5f8f9bec55bb56183fd465e8ba1f710d83d1fa0f08d631e3bc098', 'reference.json': '74ae57a2b70b7042ef8e8408b589911d8fce723f8c27aac62accb34f4299e299', 'transport-schema.json': '6c164920db387dfd9768dc08d9aa0df8bdd4d5338782d46a86ec4ee9c51f064e'}
def require(ok,message):
 if not ok:raise ValueError(message)
def digest(p):
 p=Path(p);require(p.is_file()and not p.is_symlink(),'missing/symlink input '+str(p));return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(rows):
 out={}
 for k,v in rows:require(k not in out,'duplicate JSON key');out[k]=v
 return out
def read(p):
 v=json.loads(Path(p).read_bytes(),object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in()).throw(ValueError(x)))
 json.dumps(v,allow_nan=False);return v
def keys(v,names):require(type(v)is dict and set(v)==set(names),'closed keys required')
def raw_binding(p):return {'path':str(p),'sha256':digest(p)}
def write(p,data):
 p=Path(p)
 with p.open('xb')as f:f.write(data)
 return raw_binding(p)
def write_json(p,data):return write(p,(json.dumps(data,indent=2,allow_nan=False)+'\n').encode())
def env(base,native=None,numerical=None,binding=None):
 out=dict(base)
 for k in ['ATLAS_NATIVE_FIXTURES','ATLAS_NUMERICAL_FIXTURES',BUILD_ENV]:out.pop(k,None)
 if native is not None:out['ATLAS_NATIVE_FIXTURES']=native
 if numerical is not None:out['ATLAS_NUMERICAL_FIXTURES']=numerical
 if binding is not None:out[BUILD_ENV]=binding
 return out
def contracts():
 return [dict(id='md-binary64-v1-required-failure',target='atlas_numerical_tests',native_selector=NATIVE,numerical_selector='md1997-source-admissible-v1',returncode=1,stdout='Source-admissible MD1997 numerical fixtures; inherited explicit-gis20-occ-restart-duncan-v5; models=16\n',stderr='MD AD/FD residual Jacobian mismatch\n'),*[dict(id='decimal-'+label,target='atlas_numerical_tests',native_selector=profile,numerical_selector=NUMERICAL,returncode=1,stdout='',stderr='MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5\n')for label,profile in [('missing-native',None),('incompatible-native','explicit-gis20-occ-restart-v4')]]]

class Frozen:
 def __init__(self,path,expected,meta,output,allow_synthetic=False):
  self.path=Path(path).resolve();self.expected=expected;self.meta=meta
  require(type(expected)is str and HASH.fullmatch(expected),'external freeze pin required')
  require(digest(self.path)==expected,'external freeze hash mismatch')
  self.spec=read(self.path);keys(self.spec,['identity','purpose','source_directory','source_freeze','build_binding','build_receipt','toolchain','inputs'])
  require(self.spec['identity']=='md1997-decimal-ci-execution-freeze-v1','execution freeze identity')
  purpose=self.spec['purpose'];require(purpose=='actual'or(allow_synthetic and purpose=='synthetic-test-only'),'actual execution cannot use synthetic freeze')
  self.purpose=purpose;self.output=Path(output).resolve();self.source=Path(meta['source_root']);self.build=Path(meta['build'])
  require(meta['route']=='16'and self.spec['source_directory']==str(self.source),'Decimal exact16 source binding')
  for folder in [self.source,self.build,self.output.parent]:require(not self.path.is_relative_to(folder),'execution freeze must be independently outside source/build/output')
  self.verify()
 def verify(self):
  require(__debug__ and digest(self.path)==self.expected,'execution freeze changed')
  for key in ['source_freeze','build_binding','build_receipt','toolchain']:
   row=self.spec[key];keys(row,['path','sha256']);require(type(row['sha256'])is str and HASH.fullmatch(row['sha256'])and digest(row['path'])==row['sha256'],'frozen '+key+' changed')
   p=Path(row['path']).resolve();require(not p.is_relative_to(self.source)and not p.is_relative_to(self.build)and not p.is_relative_to(self.output.parent),'external receipt placed inside mutable source/build/output')
  for n,row in self.spec['inputs'].items():
   keys(row,['sha256','realpath']);p=Path(n);require(p.is_absolute()and str(p.resolve())==row['realpath']and digest(p)==row['sha256'],'pinned build input changed '+n)
  sf=read(self.spec['source_freeze']['path']);keys(sf,['identity','directory','files'])
  require(sf['directory']==str(self.source)and sf['files'],'source freeze directory/inventory')
  require(not any(p.is_symlink()or p.name=='__pycache__'or p.suffix=='.pyc'for p in self.source.rglob('*')),'source symlink/bytecode artifacts forbidden')
  actual={str(p.relative_to(self.source))for p in self.source.rglob('*')if p.is_file()}
  require(actual==set(sf['files']),'source inventory differs from independently frozen source')
  if self.purpose=='actual':
   require(len(actual)==601,'actual Decimal source requires exact601-file composition')
   require(SUPPORT.parent.parent==self.source,'collector/oracle module must belong to bound source')
  for n,h in sf['files'].items():require(digest(self.source/n)==h,'source changed '+n)
  require(digest(self.source/'tests/test_solver.cpp')==read(self.spec['build_binding']['path'])['fixture_sha256'],'fixture binding')
  for n,h in SUPPORT_HASHES.items():require(digest(SUPPORT/n)==h,'accepted oracle support changed '+n)
  require({p.name for p in SUPPORT.iterdir()}==set(SUPPORT_HASHES),'oracle support inventory')
  tools=read(self.spec['toolchain']['path']);require(type(tools.get('files'))is dict and tools['files'],'toolchain file map')
  for n,row in tools['files'].items():require(Path(n).is_absolute()and digest(Path(n).resolve())==row['sha256']and str(Path(n).resolve())==row['realpath'],'tool changed '+n)
  for selected in [sys.executable,shutil.which('ctest')]:
   require(selected is not None,'required tool missing');resolved=str(Path(selected).resolve());require(any(row['realpath']==resolved and row['sha256']==digest(Path(selected).resolve())for row in tools['files'].values()),'selected Python/CTest not frozen')
  b=read(self.spec['build_binding']['path']);keys(b,['identity','purpose','source_freeze_sha256','fixture_sha256','generated_catalogue_sha256','executable_sha256','executable_path','working_directory','model_sha256'])
  require(b['identity']=='md1997-decimal-native-build-binding-v1'and b['purpose']==self.purpose,'actual build binding identity/purpose')
  require(b['source_freeze_sha256']==self.spec['source_freeze']['sha256']and b['executable_path']==str(self.build/'atlas_numerical_tests')and b['working_directory']==str(self.build),'build/source/path correspondence')
  require(b['executable_sha256']==digest(b['executable_path'])and b['generated_catalogue_sha256']==digest(self.build/'generated/models.json')and b['model_sha256']==self.meta['model_definitions']['manzari-dafalias-1997-constant-m-be-v1'],'generated/artifact/model binding')
  # Actual build correspondence is a separately reviewed trust prerequisite,
  # never inferred from the export stamp or a hash-shaped caller object.
  receipt=read(self.spec['build_receipt']['path']);keys(receipt,['identity','passed','source_freeze_sha256','build_binding_sha256','artifacts','evidence'])
  require(receipt['identity']=='md1997-decimal-reviewed-build-binding-v1'and receipt['passed']is True and receipt['source_freeze_sha256']==self.spec['source_freeze']['sha256']and receipt['build_binding_sha256']==self.spec['build_binding']['sha256'],'reviewed build receipt linkage')
  require(type(receipt['evidence'])is dict and receipt['evidence'],'complete external build evidence pins required')
  for n,h in {**receipt['artifacts'],**receipt['evidence']}.items():require(Path(n).is_absolute()and digest(n)==h,'actual build evidence changed '+n)
  required={str(self.build/n):self.meta['artifacts'][n]for n in self.meta['artifacts']}
  required.update(self.meta['registered_artifacts'])
  require(all(receipt['artifacts'].get(n)==h for n,h in required.items()),'build receipt must bind every generated/registered artifact')
  self.binding=b;self.binding_hash=self.spec['build_binding']['sha256']

def selectors():return {'ATLAS_NATIVE_FIXTURES':NATIVE,'ATLAS_NUMERICAL_FIXTURES':NUMERICAL,'PYTHONOPTIMIZE':'0'}
def checked_raw(folder,row,channel):
 require(row.get('status')=='completed','incomplete process')
 raw=base64.b64decode(row[channel+'_base64'],validate=True)
 require(hashlib.sha256(raw).hexdigest()==row[channel+'_sha256']and len(raw)<=MAX_OUTPUT,'raw hash/capture size mismatch')
 return write(folder/channel,raw)
def envelope(raw):
 require(type(raw)is bytes and raw.endswith(b'\n')and raw.count(b'\n')==1,'one complete JSON envelope line required')
 require(raw.startswith(b'{')and raw.endswith(b'}\n'),'no envelope prefix/suffix permitted')

def oracle():
 # Avoid ambient modules shadowing the independently frozen evaluator import.
 if 'decimal_dsl'in sys.modules:require(digest(sys.modules['decimal_dsl'].__file__)==SUPPORT_HASHES['decimal_dsl.py'],'ambient Decimal module differs')
 else:
  s=importlib.util.spec_from_file_location('decimal_dsl',SUPPORT/'decimal_dsl.py');m=importlib.util.module_from_spec(s);sys.modules['decimal_dsl']=m;s.loader.exec_module(m)
 s=importlib.util.spec_from_file_location('md1997_saved_oracle',SUPPORT/'assess_saved.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def assess(frozen,receipt,folder,process,runner,recheck):
 frozen.verify();recheck();process_path=folder/'typed-process.json';write_json(process_path,process)
 report=folder/'assessment.json'
 argv=[sys.executable,'-B',str(SUPPORT/'assess_saved.py'),'--requests',str(SUPPORT/'requests.json'),'--reference',str(SUPPORT/'reference.json'),'--process',str(process_path),'--build-binding',frozen.spec['build_binding']['path'],'--build-binding-sha256',frozen.binding_hash,'--output',str(report)]
 environment=env(os.environ);environment.update(PYTHONOPTIMIZE='0',PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(SUPPORT));environment.pop('PYTHONHOME',None)
 try:
  row=receipt.process(argv,environment,120,runner,cwd=str(frozen.build));row['role']='external-Decimal-assessor';receipt.save()
 finally:
  retained={'process':raw_binding(process_path),'report':raw_binding(report)if report.is_file()and not report.is_symlink()else None,'purpose':frozen.purpose,'status':'assessment-attempt-retained'}
  receipt.value.setdefault('decimal_assessment_attempts',[]).append(retained);receipt.save()
 frozen.verify();recheck();require(type(row['returncode'])is int and row['returncode']==0 and row['stdout']==''and row['stderr']=='','external assessor process failed or emitted unexpected output')
 actual=read(report);expected=oracle().assess(SUPPORT/'requests.json',SUPPORT/'reference.json',process_path,Path(frozen.spec['build_binding']['path']),frozen.binding_hash)
 require(actual==expected,'external assessment report does not reproduce frozen oracle')
 require(actual['passed']is True and actual['purpose']==frozen.purpose and actual['comparisons']==588 and type(actual['comparisons'])is int and len(actual['results'])==588 and actual['failures']==[]and all(x['passed']is True for x in actual['results']),'all588 external comparisons required')
 receipt.value.setdefault('decimal_assessments',[]).append({'process':raw_binding(process_path),'report':raw_binding(report),'raw_output_sha256':actual['raw_output_sha256'],'purpose':actual['purpose'],'comparisons':588,'passed':True});receipt.save()
 frozen.verify();recheck()

def folder_for(receipt):
 folder=receipt.output.with_name(receipt.output.stem+'-decimal');folder.mkdir(exist_ok=False);return folder
def direct(frozen,receipt,base_env,runner,recheck):
 folder=folder_for(receipt);frozen.verify();recheck()
 environment=env(base_env,NATIVE,NUMERICAL,frozen.binding_hash);environment.update(PYTHONOPTIMIZE='0',PYTHONDONTWRITEBYTECODE='1')
 row=receipt.process([frozen.binding['executable_path']],environment,120,runner,cwd=str(frozen.build));row['role']='Decimal-export-unassessed';receipt.value['status']='cpp-complete-awaiting-external';receipt.save()
 frozen.verify();recheck();require(type(row['returncode'])is int and row['returncode']==0,'native Decimal export failed')
 envelope(base64.b64decode(row['stdout_base64'],validate=True))
 process={'identity':'md1997-decimal-direct-process-v1','purpose':frozen.purpose,'argv':row['argv'],'cwd':str(frozen.build),'returncode':row['returncode'],'stdout':checked_raw(folder,row,'stdout'),'stderr':checked_raw(folder,row,'stderr'),'selectors':selectors(),'executable_sha256':frozen.binding['executable_sha256']}
 assess(frozen,receipt,folder,process,runner,recheck)

def ctest_output(frozen,receipt,row,raw,runner,recheck):
 folder=folder_for(receipt);require(len(raw)<=MAX_OUTPUT,'CTest output exceeds frozen capture limit')
 text=raw.decode('utf-8');matches=list(re.finditer(r'(?m)^([0-9]+)/([0-9]+) Testing: atlas_numerical\n',text));require(len(matches)==1,'unique numerical section required')
 tail=text[matches[0].end():];next_test=re.search(r'(?m)^[0-9]+/[0-9]+ Testing: ',tail);section=tail[:next_test.start()]if next_test else tail
 marker='Output:\n----------------------------------------------------------\n';require(section.count(marker)==1 and section.count('<end of output>')==1,'unambiguous numerical output')
 before,rest=section.split(marker);output,after=rest.split('<end of output>')
 require(re.findall(r'(?m)^Test Passed\.$',after)==['Test Passed.']and 'Test Failed.'not in after,'one genuine child success')
 require(re.findall(r'(?m)^Command: (.*)$',before)==['"'+frozen.binding['executable_path']+'"']and re.findall(r'(?m)^Directory: (.*)$',before)==[str(frozen.build)]and re.findall(r'(?m)^([0-9]+/[0-9]+) Test: atlas_numerical$',before)==[matches[0].group(1)+'/'+matches[0].group(2)],'exact CTest child headers')
 envelope(output.encode())
 process={'identity':'md1997-decimal-ctest-child-v1','purpose':frozen.purpose,'child_name':'atlas_numerical','child_command':[frozen.binding['executable_path']],'child_directory':str(frozen.build),'child_status':'Test Passed.','last_test_log':write(folder/'LastTest.log',raw),'combined_output':write(folder/'combined_output',output.encode()),'parent':{'argv':row['argv'],'cwd':row['cwd'],'returncode':row['returncode'],'stdout':checked_raw(folder,row,'stdout'),'stderr':checked_raw(folder,row,'stderr')},'selectors':selectors(),'executable_sha256':frozen.binding['executable_sha256']}
 receipt.value['status']='cpp-complete-awaiting-external';receipt.save();assess(frozen,receipt,folder,process,runner,recheck)
