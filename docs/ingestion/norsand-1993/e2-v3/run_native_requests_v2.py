"""Execute frozen flat C ABI requests, retaining failure sentinels and inputs."""
from pathlib import Path
import ctypes as C,json,sys,hashlib

def run(library,request_file,output_file):
 lib=C.CDLL(str(Path(library).resolve()));fn=lib.path_advance;P=C.POINTER(C.c_double)
 fn.argtypes=[C.c_int,P,C.c_int,C.c_double,P,C.c_int,P,C.c_int,C.c_double,P,P,P,C.c_int,P,P,P,C.c_int];fn.restype=C.c_int
 requests=json.loads(Path(request_file).read_text());rows=[];committed={}
 def array(values):return (C.c_double*len(values))(*[float(x) for x in values])
 for req in requests['requests']:
  ns=len(req['state']);np=len(req['parameters']);nc=len(req['current_controls']);no=req['observable_count']
  state=array(committed[req['state_from']]['state'] if 'state_from' in req else req['state']);params=array(req['parameters']);current=array(req['current_controls']);start=array(req['start_controls']);end=array(req['end_controls']);settings=array(req['settings'])
  original=[list(v) for v in [state,params,current,start,end,settings]]
  output=array([-1234567.]*ns);coordinate=C.c_double(-7654321.);obs=array([-1234567.]*no)
  status=fn(req['model'],state,ns,float(req['coordinate']),params,np,current,nc,float(req['progress']),start,end,settings,len(req['settings']),output,C.byref(coordinate),obs,no)
  def equal(a,b):return all(x==y or x!=x and y!=y for x,y in zip(a,b)) and len(a)==len(b)
  assert all(equal(list(v),old) for v,old in zip([state,params,current,start,end,settings],original)),('input mutated',req['id'])
  if status==0:assert list(output)==[-1234567.]*ns and coordinate.value==-7654321. and list(obs)==[-1234567.]*no,('failed-call output mutated',req['id'])
  row=dict(id=req['id'],status=status,state=list(output),coordinate=coordinate.value,observables=list(obs));rows.append(row)
  if status:committed[req['id']]=row
 result=dict(library_sha256=hashlib.sha256(Path(library).read_bytes()).hexdigest(),request_sha256=hashlib.sha256(Path(request_file).read_bytes()).hexdigest(),rows=rows)
 Path(output_file).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':run(*sys.argv[1:])
