"""Own-state driver. Raw process responses are saved before JSON parsing/assessment."""
import argparse,copy,gzip,hashlib,json,select,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];FREEZE=ROOT/'docs/reviews/gis2024-v03-research-freeze-v1'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def csv(xs):return ','.join(format(x,'.17g')for x in xs)
def dump(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
class Transport:
 def __init__(self,command,recorder,context):
  self.command=command;self.context=context;self.recorder=recorder;self.stderr=(recorder.directory/f'context-{recorder.counter:04d}.stderr').open('w');self.p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
 def send(self,line):
  self.p.stdin.write(line+'\n');self.p.stdin.flush()
  if not select.select([self.p.stdout],[],[],30)[0]:raise TimeoutError('backend response timeout')
  raw=self.p.stdout.readline();index=self.recorder.counter;self.recorder.counter+=1
  receipt={'index':index,'context':self.context,'pid':self.p.pid,'command':self.command,'line':line,'stdout':raw,'process_poll':self.p.poll()}
  dump(self.recorder.directory/f'{index:04d}.json',receipt)
  if not raw:raise RuntimeError('backend closed output')
  return json.loads(raw),index
 def describe(self):return self.send('D')
 def call(self,r):
  response,index=self.send('\t'.join(['I',r['model'],csv(r['parameters']),csv(r['initial']),csv(r['strain']),csv(r['settings'])]))
  return {'request':copy.deepcopy(r),'response':response,'receipt':index,'context':self.context}
 def close(self):
  self.p.stdin.close()
  try:self.p.wait(timeout=5)
  except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
  self.stderr.close();self.p.stdout.close()
class Recorder:
 def __init__(self,directory):self.directory=directory;directory.mkdir();self.counter=0

def execute(command,destination,backend):
 for path,expected in read(HERE/'execution-freeze.json')['files'].items():
  assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
 destination.mkdir(parents=True,exist_ok=False);recorder=Recorder(destination/'receipts');rows=read(FREEZE/'trajectory-requests.json.gz');probes=read(FREEZE/'probes.json');data={'backend':backend,'rows':[],'probes':[],'descriptors':[],'transport_error':None,'artifact_sha256':{str(Path(x).resolve()):hashlib.sha256(Path(x).read_bytes()).hexdigest()for x in command if Path(x).is_file()}};main=Transport(command,recorder,'main')
 def descriptor(t):
  d,i=t.describe();data['descriptors'].append({'context':t.context,'descriptor':d,'receipt':i})
 try:
  descriptor(main)
  for row in rows:
   result={'id':row['id'],'calls':[],'restart_same':[],'restart_fresh':[]};data['rows'].append(result);state=row['initial'][:]
   for strain in row['increments']:
    r={k:row[k]for k in ['model','parameters','settings']};r.update(initial=state[:],strain=strain[:]);item=main.call(r);result['calls'].append(item)
    if item['response'].get('ok')is not True:break
    state=item['response']['state'][:]
   if len(result['calls'])==len(row['increments'])and all(x['response'].get('ok')is True for x in result['calls']):
    checkpoint=result['calls'][row['partitions']-1]['response']['state'][:]
    fresh=Transport(command,recorder,'fresh:'+row['id'])
    try:
     descriptor(fresh)
     for name,transport in [('restart_same',main),('restart_fresh',fresh)]:
      state=checkpoint[:]
      for strain in row['increments'][row['partitions']:]:
       r={k:row[k]for k in ['model','parameters','settings']};r.update(initial=state[:],strain=strain[:]);item=transport.call(r);result[name].append(item)
       if item['response'].get('ok')is not True:break
       state=item['response']['state'][:]
    finally:fresh.close()
   dump(destination/'partial.json',data);print(row['id'],len(result['calls']),flush=True)
  data['control']=main.call(probes['control'])
  for p in probes['probes']:
   data['probes'].append({'id':p['id'],'call':main.call(p['request']),'recovery':main.call(probes['control'])})
 except Exception as exc:data['transport_error']=repr(exc)
 finally:main.close();dump(destination/'result.json',data)
 return 0 if data['transport_error']is None else 2
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('backend',choices=['native','wasm']);p.add_argument('executable');p.add_argument('destination',type=Path);a=p.parse_args();cmd=[a.executable]if a.backend=='native'else['node',str(HERE/'wasm_line.mjs'),a.executable];raise SystemExit(execute(cmd,a.destination,a.backend))
