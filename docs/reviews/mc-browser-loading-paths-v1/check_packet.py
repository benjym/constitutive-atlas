"""Input/reference binding, exact producer fixtures and corruption checks only."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import copy,hashlib,json,math,struct,tempfile
from prepare_inputs import generate,controls,difference,float_bits
from waveform_oracle import bits,decode,hex_
P=Path(__file__).resolve().parent
checks=0

def require(ok,label):
 global checks
 checks+=1
 if not ok:raise AssertionError(label)
def validate(data,refs=()):
 require(data==generate(),'independent requested input regeneration')
 digest=hashlib.sha256((P/'source-input.json').read_bytes()).hexdigest()
 for ref in refs:
  require(ref['identity']=='mc-browser-loading-source-reference-v1','new reference identity')
  require(ref['source_input_sha256']==digest,'reference binds exact stored input')
  require([x['id']for x in ref['paths']]==[x['id']for x in data['paths']],'reference path order')
  for path,out in zip(data['paths'],ref['paths']):
   require(len(out['points'])==len(path['controls_bits']),'full reference path length')
   require(out['protocol']==path['protocol'],'reference protocol binding')
   for i,point in enumerate(out['points']):
    require(F(D(point['control']))==decode(int(path['controls_bits'][i],16)),'reference exact displayed control')

def main():
 data=json.loads((P/'source-input.json').read_bytes());refs=[json.loads((P/f'reference-p{n}.json').read_bytes())for n in(280,360)]
 freeze=json.loads((P/'prospective-freeze.json').read_bytes())
 for name,digest in freeze['files'].items():require(hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,'frozen source/input '+name)
 validate(data,refs)
 changed=[]
 old=json.loads((P/'source/original-source-input.json').read_bytes())
 for path,prior in zip(data['paths'],old['paths']):
  raw=list(map(lambda x:int(x,16),path['controls_bits']));require(raw[0]==0,'initial canonical+0')
  for i,(a,b)in enumerate(zip(raw[1:],raw)):
   require(difference(a,b)==int(path['control_delta_bits'][i],16),'exact oracle delta')
   # Independent host subtraction sanity check, not definition of Fraction oracle.
   af=struct.unpack('>d',a.to_bytes(8,'big'))[0];bf=struct.unpack('>d',b.to_bytes(8,'big'))[0]
   require(float_bits(af-bf)==difference(a,b),'binary64 subtraction sanity')
   require(hex_(a)==path['control_targets'][i],'hex/bit consistency')
  count=sum(a!=b for a,b in zip(path['control_targets'],prior['control_targets']));changed.append({'id':path['id'],'changed_controls':count,'total':len(raw)-1,'producer':path['producer']})
 # Independent source contract examples, endpoint/sign semantics and invalid types.
 require(controls(.01,100,0)[-1]==float_bits(.01),'linear exact endpoint')
 require(all(v==0 for v in controls(-0.,32,0)),'zero amplitude canonicalzero')
 for n,cyc in[(32,1),(64,1),(5000,100),(63,7)]:
  seq=controls(-.01,n,cyc)
  for i,b in enumerate(seq):
   if (2*cyc*i)%n==0:require(b==0,'exact whole/halfperiodzero')
 for n in(3,7,100,200):
  seq=controls(.01,n,0)
  for i,b in enumerate(seq[1:-1],1):require(b==float_bits((.01*i)/n),'linear two RNE operations')
 tiny=controls(-float.fromhex('0x0.0000000000001p-1022'),64,1)
 require(any(v==1<<63 for v in tiny),'nonzero amplitude negative underflow sign retained')
 require(difference(1<<63,0)==1<<63,'negativezero subtract positivezero')
 # Each mutation is tested against an otherwise valid packet, not candidate results.
 probes=[]
 def reject(label,mutate):
  dat,rs=copy.deepcopy(data),copy.deepcopy(refs);mutate(dat,rs)
  try:validate(dat,rs)
  except AssertionError:probes.append(label)
  else:raise AssertionError('corruption accepted '+label)
 reject('control_column',lambda d,r:d['paths'][0]['controls_bits'].__setitem__(1,'0000000000000000'))
 reject('delta_column',lambda d,r:d['paths'][0]['control_delta_bits'].__setitem__(0,'0000000000000000'))
 reject('producer_identity',lambda d,r:d['paths'][0].__setitem__('producer','legacy-sine'))
 reject('request_steps',lambda d,r:d['paths'][0].__setitem__('steps',31))
 reject('initial',lambda d,r:d['initial'].__setitem__(0,'0x0.0p+0'))
 reject('parameter',lambda d,r:d['parameters'].__setitem__('c','0x1.0p+0'))
 reject('reference_source_binding',lambda d,r:r[0].__setitem__('source_input_sha256','0'*64))
 reject('reference_identity',lambda d,r:r[0].__setitem__('identity','mc-axisymmetric-source-reference-v1'))
 reject('reference_path_missing',lambda d,r:r[0]['paths'].pop())
 reject('reference_point_missing',lambda d,r:r[0]['paths'][0]['points'].pop())
 reject('reference_control',lambda d,r:r[0]['paths'][0]['points'][1].__setitem__('control','0'))
 reject('reference_protocol',lambda d,r:r[0]['paths'][0].__setitem__('protocol',4))
 report={'identity':'mc-browser-loading-binding-check-v1','passed':True,'checks':checks,'corruption_probes':probes,'changed_from_old_loading':changed,'candidate_calls':0,'compiled_observations':0}
 (P/'binding-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'passed':True,'checks':checks,'corruption_probes':len(probes)}))
if __name__=='__main__':main()
