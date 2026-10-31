"""Assemble prospective full schedules; no compiled execution."""
import argparse,hashlib,json
from pathlib import Path

def requests(reference,model):
 aliases={'Kmod':'K','Gmod':'G','Mcrit':'M','pOne':'p1'}
 output=[]
 for case in reference['cases']:
  for tolerance in (1e-4,1e-6,1e-8):
   rate=case['initial_rate']
   request={'schema_version':'0.2','units':'SI','model':model['id'],'start_time':0,
    'parameters':[reference['parameters'][aliases.get(name,name)] for name in model['parameters']],
    'initial':case['initial_state'],'initial_strain':case['initial_strain'],'initial_strain_rate':rate,
    'segments':[{'id':'preparation','duration':10,'samples':10,
      'controls':[{'quantity':'strain','kind':'rate','value':v} for v in rate]},
     {'id':'hold','duration':20,'samples':10,
      'controls':[{'quantity':'stress','kind':'hold'} for _ in range(3)]+[{'quantity':'strain','kind':'hold'} for _ in range(3)]}],
    'solver':{'method':'backward-euler-step-doubling','relative_tolerance':tolerance,
      'absolute_scale_fraction':1e-11,'maximum_substeps':100000}}
   output.append({'case':case['id'],'relative_tolerance':tolerance,'request':request})
 return output

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--reference',type=Path,required=True);parser.add_argument('--model',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 reference=json.loads(args.reference.read_bytes());model=json.loads(args.model.read_bytes())
 data=requests(reference,model)
 assert len(data)==9
 args.output.write_text(json.dumps({'identity':'terracotta-preparation-hold-v1','compiled_observations':0,'reference_sha256':hashlib.sha256(args.reference.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(args.model.read_bytes()).hexdigest(),'records':data},indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
