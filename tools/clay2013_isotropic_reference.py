import hashlib,json
from pathlib import Path
from decimal import Decimal,localcontext
from tools.reference_clay2013_isotropic import path,state
ROOT=Path(__file__).resolve().parents[1]
P=dict(lambda_star='.12',kappa_star='.025',N='1.1')
def encode(v):
 if isinstance(v,Decimal):return str(v)
 raise TypeError(type(v).__name__)
def generate():
 with localcontext() as c:
  c.prec=90
  cases=[]
  for p in ('10','10000','1000000'):
   for name,x in [('compression',['.01','.02','.03']),('unloading',['-.01','-.02','-.03']),('reversal',['.02','-.03','.01'])]:
    cases.append(dict(name=f'{name}-p{p}',initial=dict(p=p,e='.8'),parameters=P,increments=x,states=path(p,'.8',x,**P)))
  return dict(contract='clay2013-isotropic-closed-form-v1',precision=90,compression_positive=True,oracle_sha256=hashlib.sha256((ROOT/'tools/reference_clay2013_isotropic.py').read_bytes()).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,scope='analytic isotropic ODE only; no production/native evaluation or scientific admission')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args();args.output.write_text(json.dumps(generate(),default=encode,indent=2)+'\n')
