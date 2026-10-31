"""Independent exact-binary64 caller inputs, never production JS or model code."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,struct,sys
from waveform_oracle import bits,decode,waveform,hex_
P=Path(__file__).resolve().parent

def float_bits(x):return int.from_bytes(struct.pack('>d',x),'big')
def difference(a,b):
 x=decode(a)-decode(b)
 # IEEE RNE exact cancellation gives +0; -0 minus +0 gives -0.
 return bits(x) if x else (1<<63 if a==(1<<63) and b==0 else 0)
def controls(target,steps,cycles):
 if type(steps)is not int or not 1<=steps<=5000:raise ValueError('steps')
 if type(cycles)is not int or not 0<=cycles<=100:raise ValueError('cycles')
 amp=F.from_float(target);ab=float_bits(target);out=[0]
 for i in range(1,steps+1):
  if not amp:b=0
  elif not cycles:
   b=ab if i==steps else bits(decode(bits(amp*i))/steps)
  else:
   w,_=waveform(steps,cycles,i);b=0 if not w else bits(amp*w)
  out.append(b)
 return out

def generate():
 original=json.loads((P/'source/original-source-input.json').read_bytes());requests=json.loads((P/'requests.json').read_bytes())
 if len(requests)!=14 or [r['id']for r in requests]!=[p['id']for p in original['paths']]:raise ValueError('original14request correspondence')
 data={k:v for k,v in original.items() if k!='paths'}
 data.update(identity='mc-browser-loading-input-v1',control_semantics='Exact binary64 caller controls from independent Fraction RNE linear-rne-v1/cyclic-sine-rne12-v1; initial+0; exact linear endpoint; cyclic integer-phase zero nodes+0; deltasRN(control_i-control_previous), no libm sine.',original_source_input_sha256=hashlib.sha256((P/'source/original-source-input.json').read_bytes()).hexdigest(),requests_sha256=hashlib.sha256((P/'requests.json').read_bytes()).hexdigest(),paths=[])
 for req,old in zip(requests,original['paths']):
  raw=controls(req['target'],req['steps'],req['cycles']);ds=[difference(a,b)for a,b in zip(raw[1:],raw)]
  row={k:v for k,v in old.items()if k not in('control_targets','control_deltas')}
  row.update(producer='cyclic-sine-rne12-v1'if req['cycles']else'linear-rne-v1',target_bits=f"{float_bits(req['target']):016x}",steps=req['steps'],cycles=req['cycles'],controls_bits=[f'{v:016x}'for v in raw],control_delta_bits=[f'{v:016x}'for v in ds],control_targets=[hex_(v)for v in raw[1:]],control_deltas=[hex_(v)for v in ds])
  data['paths'].append(row)
 return data
if __name__=='__main__':
 target=P/'source-input.json'
 if target.exists():raise RuntimeError('preserve existing source input; replay in copied clean stage')
 data=generate();target.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n');print(json.dumps({'identity':data['identity'],'paths':len(data['paths']),'points':sum(len(p['controls_bits'])for p in data['paths']),'source_input_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'candidate_calls':0}))
