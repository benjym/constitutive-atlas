from pathlib import Path
from fractions import Fraction as F
import json,sys,struct
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).parent;sys.path.insert(0,str(s/'reference'))
from reference import passes_exact_accuracy
rows=json.loads(Path(sys.argv[1]).read_text());refs=json.loads((s/'reference/references.json').read_text())['cases'];assert len(rows)==len(refs)==35
for row,ref in zip(rows,refs):
 assert row['id']==ref['id']and row['wire']==','.join(ref['input_bits'])
 value=json.loads(row['raw'],parse_int=float);assert value['ok']is True
 q=value['q'];assert type(q)in(int,float)and struct.pack('>d',q).hex()==value['q_bits']
 qsq=F(int(ref['q_squared_numerator']),int(ref['q_squared_denominator']))
 assert passes_exact_accuracy(q,qsq),row['id']
print(json.dumps({'passed':True,'reference_cases':35,'exact_isotropic_zeros':sum(r['exact_isotropic_zero']for r in refs),'source_accuracy':'32u*q+8minsub, unchanged','candidate_calls':0},indent=2))
