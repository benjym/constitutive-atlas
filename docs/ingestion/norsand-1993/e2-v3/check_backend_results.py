from pathlib import Path
import json,sys,hashlib

def main(request_file,*result_files):
 reqs=json.loads(Path(request_file).read_text());reports=[];allrows=[]
 for file in result_files:
  data=json.loads(Path(file).read_text());assert data['request_sha256']==hashlib.sha256(Path(request_file).read_bytes()).hexdigest();assert len(data['rows'])==len(reqs['requests']);errors=[]
  for req,row in zip(reqs['requests'],data['rows']):
   assert req['id']==row['id'];assert row['status']==req['expected_status'],(req['id'],'status',row['status'])
   if not row['status']:continue
   gate=2e-7 if req.get('analytical') else 2e-11
   error=max(abs(a-b) for a,b in zip(row['state'],req['expected_state']))
   if 'expected_observables' in req:error=max(error,max(abs(a-b)/s for a,b,s in zip(row['observables'],req['expected_observables'],req['observable_scales'])))
   assert error<=gate,(req['id'],error,gate)
   assert row['coordinate']==float(req['coordinate'])+float(req['progress'])
   if req['progress']==0:assert row['state']==req['state']
   errors.append(error)
  reports.append(dict(file=file,count=len(data['rows']),max_error=max(errors)));allrows.append(data['rows'])
 if len(allrows)==2:
  for req,a,b in zip(reqs['requests'],*allrows):
   assert a['id']==b['id'] and a['status']==b['status']
   if not a['status']:continue
   error=max(abs(x-y) for x,y in zip(a['state'],b['state']))
   error=max(error,max(abs(x-y)/s for x,y,s in zip(a['observables'],b['observables'],req['observable_scales'])))
   assert error<=2e-11,(a['id'],'native/Wasm parity',error)
 print(json.dumps(dict(result='PASS',reports=reports),indent=2))
if __name__=='__main__':main(*sys.argv[1:])
