"""Read-only Python-core adversarial probes against independent Cartesian certified references."""
import argparse,hashlib,importlib.util,json,math,types
from fractions import Fraction as F
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(root,reference_packet):
 core=module(root/'atlas/numerics/determinant.py','isolated_determinant_core_review');ind=module(reference_packet/'reference.py','independent_cartesian_reference');refs=json.loads((reference_packet/'references.json').read_text());rows=[]
 def check(name,fn,expected):
  try:value=fn();observed=value.hex()if isinstance(value,float)else value
  except ValueError:observed='reject'
  except Exception as e:observed={'exception':type(e).__name__,'message':str(e)}
  rows.append({'name':name,'expected':expected,'observed':observed,'passed':observed==expected})
 # Primal primitive on allfrozeninputs; derivative-only and seed failure are not primal failures.
 for case in refs['cases']:
  vals=list(map(float,case['values']))
  if 'nonfinite-input'in case['tags']:expected='reject'
  else:
   certificate=case['rounding_certificates'][0]if 'rounding_certificates'in case else ind.certified(ind.exact_cartesian(vals,[[0.]*38 for _ in range(6)])[0]);assert certificate['certified'];expected='reject'if certificate['overflow']else certificate['hex']
  check('primal/'+case['id'],lambda vals=vals:core.determinant(vals),expected)
 # Shared rounding/sign core on every independently certified exact cofactor direction.
 for case in refs['cases']:
  for i,(pair,certificate)in enumerate(zip(case.get('exact_cartesian_algebraic_components',[]),case.get('rounding_certificates',[]))):
   a=F(*map(int,pair['rational']));b=F(*map(int,pair['sqrt2_coefficient']));expected='reject'if certificate['overflow']else certificate['hex'];check('round-component/'+case['id']+'/'+str(i),lambda a=a,b=b:core.rounded(a,b),expected)
 # Rational and irrational probes straddling rounding midpoints far closer than guide accuracy.
 floats=[0.,math.ulp(0.),math.nextafter(2.**-1022,0.),2.**-1022,1.,math.nextafter(1.,math.inf),2.,float.fromhex('0x1.fffffffffffffp+1023')]
 low_sqrt=F(math.isqrt(2*(2**400)**2),2**400);high_sqrt=low_sqrt+F(1,2**400)
 for i,x in enumerate(floats):
  upper=math.nextafter(x,math.inf);mid=(F(x)+(F(2)**1024 if math.isinf(upper)else F(upper)))/2;exponent=-1074 if x==0 else math.frexp(x)[1]-1;b=F(2)**(exponent-100)
  for label,a,bb in [('rational-mid',mid,F(0)),('irr-above',mid-b*low_sqrt,b),('irr-below',mid-b*high_sqrt,b)]:
   for direction in (-1,1):
    q=ind.Q(direction*a,direction*bb);certificate=ind.certified(q);assert certificate['certified'];expected='reject'if certificate['overflow']else certificate['hex'];check('midpoint/'+str(i)+'/'+label+'/'+str(direction),lambda q=q:core.rounded(q.a,q.b),expected)
 # Fast candidate must never be necessary: force guide to NaN and gross wrong finite values.
 original=core.math
 for mode,guide in [('nan',float('nan')),('wrong-finite',1e300)]:
  core.math=types.SimpleNamespace(**{k:getattr(math,k)for k in dir(math)if not k.startswith('__')});core.math.sqrt=lambda _,guide=guide:guide
  for case in refs['cases']:
   if case['expectation']['ok']is not True:continue
   check('untrusted-guide/'+mode+'/'+case['id'],lambda case=case:core.determinant(list(map(float,case['values']))),case['expectation']['value_hex'])
 core.math=original
 for name,values in [('bool',[True]*6),('None',[None]*6),('complex',[1j]*6),('string',['1']*6),('oversized-integer',[2**2000]*6),('short',[1]*5),('long',[1]*7),('empty',[])]:check('invalid-type/'+name,lambda values=values:core.determinant(values),'reject')
 return {'version':'symmetric-determinant-core-v1-source-only-probes','source_hashes':{n:sha(root/n)for n in ['cpp/include/atlas/numerics/determinant.hpp','atlas/numerics/determinant.py']},'independent_reference_hashes':{n:sha(reference_packet/n)for n in ['prospective-freeze.json','reference.py','references.json','rounding-checks.json']},'count':len(rows),'passed':sum(r['passed']for r in rows),'all_passed':all(r['passed']for r in rows),'unexpected':[r for r in rows if not r['passed']],'rows':rows,'compiled_calls':0,'material_calls':0,'atlas_interpreter_calls':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--reference-packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.root,a.reference_packet);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(r['passed'],'/',r['count'],'allpass',r['all_passed'])
