"""Strict saved-data comparison. Never runs a compiler/native process or makes references."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
from decimal import Decimal,localcontext
import json,hashlib,re,argparse
from decimal_dsl import context,Rejected
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HASH=re.compile(r'[0-9a-f]{64}\Z');HEX=re.compile(r'-?0x[0-9a-f]+(?:\.[0-9a-f]*)?p[+-][0-9]+\Z')
def pairs(xs):
 d={}
 for k,v in xs:
  if k in d:raise Rejected('duplicate key '+k)
  d[k]=v
 return d
def jsonfloat(s):
 x=float(s)
 require(x==x and abs(x)!=float('inf'),'nonfinite JSON number')
 return x
def read(p):return json.loads(Path(p).read_text(),object_pairs_hook=pairs,parse_float=jsonfloat,parse_constant=lambda x:(_ for _ in()).throw(Rejected('nonfinite JSON')))
def keys(d,names):
 if type(d)is not dict or set(d)!=set(names):raise Rejected('exact object keys required '+str(names))
def require(cond,msg):
 if not cond:raise Rejected(msg)
def hexfloat(s):
 require(type(s)is str and HEX.fullmatch(s),'finite hex string required')
 x=float.fromhex(s);require(x==x and abs(x)!=float('inf'),'nonfinite hex');return x

def same_metadata(a,b):
 if type(b)is dict:
  keys(a,b)
  for k in b:same_metadata(a[k],b[k])
 elif type(b)is list:
  require(type(a)is list and len(a)==len(b),'metadata list shape')
  for x,y in zip(a,b):same_metadata(x,y)
 elif type(b)is str and HEX.fullmatch(b):require(hexfloat(a).hex()==hexfloat(b).hex(),'binary64 metadata bits')
 else:require(type(a)is type(b)and a==b,'metadata literal')
def file_binding(row):
 keys(row,['path','sha256']);require(type(row['path'])is str and HASH.fullmatch(row['sha256']),'raw binding type');p=Path(row['path']);require(sha(p)==row['sha256'],'raw file hash');return p.read_bytes()

def transport(process,binding):
 selectors={'ATLAS_NATIVE_FIXTURES':'explicit-gis20-occ-restart-duncan-v5','ATLAS_NUMERICAL_FIXTURES':'md1997-decimal-fd-reference-v1','PYTHONOPTIMIZE':'0'}
 require(process.get('selectors')==selectors,'selectors');require(process.get('executable_sha256')==binding['executable_sha256'],'executable binding');require(sha(binding['executable_path'])==binding['executable_sha256'],'actual executable bytes')
 require(process.get('purpose')==binding['purpose'],'purpose')
 if process.get('identity')=='md1997-decimal-direct-process-v1':
  keys(process,['identity','purpose','argv','cwd','returncode','stdout','stderr','selectors','executable_sha256'])
  require(process['argv']==[binding['executable_path']],'native argv');require(type(process['returncode'])is int and process['returncode']==0,'native returncode')
  require(process['cwd']==binding['working_directory'],'native cwd')
  out=file_binding(process['stdout']);require(file_binding(process['stderr'])==b'','direct stderr must be empty');return out,'separate stdout/stderr directly observed'
 if process.get('identity')=='md1997-decimal-ctest-child-v1':
  keys(process,['identity','purpose','child_name','child_command','child_directory','child_status','last_test_log','combined_output','parent','selectors','executable_sha256'])
  parent=process['parent'];keys(parent,['argv','cwd','returncode','stdout','stderr'])
  require(type(parent['cwd'])is str and Path(parent['cwd']).is_absolute(),'parent cwd type')
  require(type(parent['argv'])is list and len(parent['argv'])>=2 and all(type(x)is str for x in parent['argv'])and '--test-dir'in parent['argv'],'CTest argv');require(type(parent['returncode'])is int and parent['returncode']==0,'CTest parent returncode')
  file_binding(parent['stdout']);file_binding(parent['stderr']);log=file_binding(process['last_test_log']);out=file_binding(process['combined_output'])
  require(process['child_directory']==binding['working_directory'],'child cwd')
  require(process['child_name']=='atlas_numerical'and process['child_status']=='Test Passed.'and process['child_command']==[binding['executable_path']],'child identity')
  # Parse complete LastTest section, not a caller-provided offset or a second direct run.
  text=log.decode('utf-8');matches=list(re.finditer(r'(?m)^([0-9]+)/([0-9]+) Testing: atlas_numerical\r?\n',text));require(len(matches)==1,'unique numerical LastTest section')
  start=matches[0].end();next_test=re.search(r'(?m)^[0-9]+/[0-9]+ Testing: ',text[start:]);end=start+next_test.start()if next_test else len(text);section=text[start:end]
  marker='Output:\n----------------------------------------------------------\n';require(section.count(marker)==1 and section.count('<end of output>')==1,'LastTest output markers');before,rest=section.split(marker);combined,after=rest.split('<end of output>')
  commands=re.findall(r'(?m)^Command: (.*)$',before);directories=re.findall(r'(?m)^Directory: (.*)$',before)
  require(commands==['"'+binding['executable_path']+'"']and directories==[process['child_directory']],'anchored unique actual LastTest command/directory')
  require(re.findall(r'(?m)^([0-9]+/[0-9]+) Test: atlas_numerical$',before)==[matches[0].group(1)+'/'+matches[0].group(2)],'LastTest test header')
  require(combined.encode()==out,'actual CTest combined output linkage')
  require(re.search(r'(?m)^Test Passed\.\r?$',after)is not None and 'Test Failed.'not in after,'actual child success marker')
  return out,'CTest merged child stdout/stderr; no separate child stderr or numeric exit code inferred'
 raise Rejected('unknown process provenance')

def assess(request_path,reference_path,process_path,binding_path,binding_hash):
 if not __debug__:raise RuntimeError('Unoptimized Python required')
 require(HASH.fullmatch(binding_hash)and sha(binding_path)==binding_hash,'independently pinned expected build-binding hash')
 D=Path(__file__).resolve().parent
 require(sha(request_path)==sha(D/'requests.json')and sha(reference_path)==sha(D/'reference.json'),'frozen request/reference bytes')
 q=read(request_path);r=read(reference_path);p=read(process_path);b=read(binding_path)
 require(r['evaluator_sha256']==sha(D/'decimal_dsl.py')and r['policy_sha256']==sha(D/'POLICY.md'),'evaluator/policy binding')
 keys(b,['identity','purpose','source_freeze_sha256','fixture_sha256','generated_catalogue_sha256','executable_sha256','executable_path','working_directory','model_sha256'])
 require(b['identity']=='md1997-decimal-native-build-binding-v1'and b['purpose']in ['actual','synthetic-test-only'],'build identity')
 for k in ['source_freeze_sha256','fixture_sha256','generated_catalogue_sha256','executable_sha256','model_sha256']:require(type(b[k])is str and HASH.fullmatch(b[k]),'build hash')
 require(type(b['executable_path'])is str and Path(b['executable_path']).is_absolute()and type(b['working_directory'])is str and Path(b['working_directory']).is_absolute(),'build paths')
 require(b['model_sha256']==q['model_sha256'],'current model binding')
 require(r['request_sha256']==sha(request_path),'reference request binding')
 raw,channel=transport(p,b)
 env=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_float=jsonfloat,parse_constant=lambda x:(_ for _ in()).throw(Rejected('nonfinite JSON')))
 keys(env,['identity','selector','status','models','bindings','base','endpoints','ad_hex','cpp_checks'])
 require(env['identity']=='md1997-decimal-ad-export-v1'and env['selector']=='md1997-decimal-fd-reference-v1'and env['status']=='exported-unassessed','export identity');require(type(env['models'])is int and env['models']==16,'model count')
 wanted={k:r[k]for k in ['evaluator_sha256','policy_sha256','base_source_freeze_sha256','model_sha256']};wanted.update(request_sha256=sha(request_path),reference_sha256=sha(reference_path),build_binding_sha256=binding_hash)
 same_metadata(env['bindings'],wanted)
 base={k:q[k]for k in ['layout','state_hex','previous_hex','loading_hex','parameters_hex','scales_hex']};same_metadata(env['base'],base)
 require(type(env['endpoints'])is list and len(env['endpoints'])==56,'endpoint coverage')
 for observed,expected in zip(env['endpoints'],q['endpoints']):
  same_metadata(observed,{**expected,'domain':True,'branch':True})
 same_metadata(env['cpp_checks'],{'rank13':True,'rotation':True,'other_models':True})
 ad=env['ad_hex'];require(type(ad)is list and len(ad)==14 and all(type(row)is list and len(row)==14 for row in ad),'AD14x14 shape')
 ad=[[Decimal.from_float(hexfloat(x))for x in row]for row in ad]
 failures=[];comparisons=0;results=[]
 with context(120):
  secants=r['data']['120']['secants'];require(len(secants)==28 and all(len(x)==14 for x in secants),'reference shape')
  for col in range(14):
   for level in [0,1]:
    for row in range(14):
     fd=Decimal(secants[2*col+level][row]);a=ad[row][col];require(fd.is_finite(),'reference finite');err=abs(fd-a);budget=Decimal('3e-5')*max(1,abs(fd),abs(a));comparisons+=1
     record=dict(gate='AD/FD',column=col,level=level,row=row,fd=str(fd),ad=str(a),error=str(err),budget=str(budget),passed=err<budget);results.append(record)
     if not err<budget:failures.append(record)
   for row in range(14):
    x,y=[Decimal(secants[2*col+l][row])for l in [0,1]];err=abs(x-y);budget=Decimal('1.5e-5')*max(1,abs(x),abs(y));comparisons+=1
    record=dict(gate='h/h2',column=col,row=row,fd_h=str(x),fd_hhalf=str(y),error=str(err),budget=str(budget),passed=err<budget);results.append(record)
    if not err<budget:failures.append(record)
 return dict(identity='md1997-decimal-saved-assessment-v1',passed=not failures,purpose=b['purpose'],channel_scope=channel,comparisons=comparisons,results=results,failures=failures,request_sha256=sha(request_path),reference_sha256=sha(reference_path),process_sha256=sha(process_path),build_binding_sha256=binding_hash,raw_output_sha256=hashlib.sha256(raw).hexdigest(),compiled_calls=0)

def main():
 ap=argparse.ArgumentParser()
 for k in ['requests','reference','process','build-binding','build-binding-sha256','output']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();out=Path(a.output);require(not out.exists(),'fresh assessment output')
 try:report=assess(a.requests,a.reference,a.process,a.build_binding,a.build_binding_sha256)
 except Exception as exc:report=dict(identity='md1997-decimal-saved-assessment-v1',passed=False,error=str(exc),compiled_calls=0)
 with out.open('x')as stream:stream.write(json.dumps(report,indent=2)+'\n')
 if report['passed']is not True:raise SystemExit(1)
if __name__=='__main__':main()
