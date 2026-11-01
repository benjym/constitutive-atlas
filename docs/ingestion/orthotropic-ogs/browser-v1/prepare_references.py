"""Prospective independent source-only Fraction references; no compiled calls."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
p=ROOT/'docs/ingestion/orthotropic-ogs/source-v1/verify.py';spec=importlib.util.spec_from_file_location('orthotropic_source_oracle',p);oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
keys=['E1','E2','E3','G12','G23','G13','nu12','nu23','nu13']
fixtures={
 'default':{'parameters':[30e6,45e6,60e6,12e6,18e6,15e6,.2,.25,.15],'initial':[0]*6,'increments':[[.001,-.0002,.0003,.0004,-.0005,.0006],[-.001,.0002,-.0003,-.0004,.0005,-.0006],[0]*6]},
 'custom':{'parameters':[40e6,55e6,70e6,13e6,19e6,16e6,.18,.22,.12],'initial':[120000,-230000,340000,45000,-56000,67000],'increments':[[.0007,-.0004,.0002,-.0003,.0006,-.0005],[-.0002,.0003,-.0001,.0004,-.0002,.0006],[0]*6]}}
for f in fixtures.values():
 s=oracle.compliance(dict(zip(keys,f['parameters'])));assert oracle.spd(s);c=oracle.inverse(s);state=list(map(lambda x:Q(str(x)),f['initial']));strain=[Q(0)]*6;points=[{'step':0,'state':list(map(float,state)),'strain':[0]*6}]
 for i,row in enumerate(f['increments'],1):
  de=list(map(lambda x:Q(str(x)),row));state=[a+b for a,b in zip(state,oracle.matvec(c,de))];strain=[a+b for a,b in zip(strain,de)];points.append({'step':i,'state':list(map(float,state)),'strain':list(map(float,strain)),'exact_state':list(map(str,state))})
 f['points']=points
(HERE/'references.json').write_text(json.dumps({'origin':'Exact rational inversion of pinned source compliance via source-v1/verify.py, no production expressions','stressAbsoluteTolerancePa':1e-6,'strainAbsoluteTolerance':1e-15,'fixtures':fixtures},indent=2)+'\n')
