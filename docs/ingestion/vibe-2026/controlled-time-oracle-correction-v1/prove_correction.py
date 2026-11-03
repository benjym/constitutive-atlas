"""Analytic Cartesian trace witnesses and exact semantic delta audit; no Atlas import."""
from pathlib import Path
from decimal import Decimal,localcontext
from fractions import Fraction as F
from copy import deepcopy
import json,hashlib,argparse
from generate_corpus_v2 import corrected_payload,HERE,ROOT

def prove():
 old,new=corrected_payload();actual=json.loads((HERE/'reference-corpus-v2.json').read_text());assert actual==new
 unchanged=deepcopy(new);unchanged['identity']=old['identity'];changes=[]
 for before,after,undo in zip(old['cases'],new['cases'],unchanged['cases']):
  assert before['id']==after['id'];undo['expected_state']['e']=before['expected_state']['e']
  if before['expected_state']['e']!=after['expected_state']['e']:changes.append(dict(id=before['id'],old=before['expected_state']['e'],corrected=after['expected_state']['e']))
 assert unchanged==old,'A non-e corpus field, acceptance bound, input or setting changed'
 assert {c['id'] for c in changes}=={'transport-mixed-partition1','transport-mixed-partition2','transport-mixed-partition4','transport-basis3','transport-basis4','transport-basis5'}
 # Exact rational tensor trace: six Mandel bases, including their Cartesian shear embeddings.
 witnesses=[]
 for i in range(6):
  x=[F(0)]*6;x[i]=F(7,10000)
  # Off-diagonal Mandel entries are x[3:]/sqrt(2); their diagonal is exactly zero.
  diagonal=x[:3];trace=sum(diagonal);expected=F(7,10000) if i<3 else F(0)
  assert trace==expected
  witnesses.append(dict(id='basis'+str(i),mandel=[str(v) for v in x],cartesian_diagonal=[str(v) for v in diagonal],exact_trace=str(trace),shear_only=i>=3))
 mixed=[F(1,1000),F(-3,10000),F(2,10000),F(4,10000),F(-5,10000),F(6,10000)]
 assert sum(mixed[:3])==F(9,10000) and sum(mixed)==F(14,10000)
 with localcontext() as ctx:
  ctx.prec=80;D=Decimal;good=D('1.8')*D('-.0009').exp()-1;bad=D('1.8')*D('-.0014').exp()-1
  oldcase=next(c for c in old['cases'] if c['id']=='transport-mixed-partition1');newcase=next(c for c in new['cases'] if c['id']=='transport-mixed-partition1')
  assert D(oldcase['expected_state']['e'])==bad and D(newcase['expected_state']['e'])==good
  for i in range(6):
   c=next(c for c in new['cases'] if c['id']=='transport-basis'+str(i));z=D(c['expected_state']['e']);target=D('1.8')*(D('-.0007') if i<3 else D(0)).exp()-1;assert z==target
  bound=D(str(old['acceptance']['scalar_absolute']))+D(str(old['acceptance']['scalar_relative']))*max(abs(good),abs(bad))
  assert abs(good-bad)>bound
  counterexample=dict(trace_first_three='0.0009',incorrect_sum_all_six='0.0014',corrected_e=str(good),old_e=str(bad),difference=str(abs(good-bad)),unchanged_scalar_bound=str(bound),old_oracle_rejects_exact_analytic_solution=True)
 # Fixture equation identity is read, never executed.
 fixture=ROOT/'tests/fixtures/controlled-time/transport.json';model=json.loads(fixture.read_text());assert model['equations']['e']=='-(1+e)*trace(strain_rate)'
 return dict(status='pass-source-only',method='Fraction exact trace plus Decimal80 closed-form exponent; no production interpreter imported',fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),all18_cases_preserved=True,only_allowed_changes=['top-level identity','cases[*].expected_state.e'],all_other_fields_exactly_identical=True,changed_cases=changes,basis_witnesses=witnesses,mixed_counterexample=counterexample,compiled_calls=0)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'proof-results.json');a=p.parse_args()
 with a.output.open('x') as f:json.dump(prove(),f,indent=2);f.write('\n')
 print('PASS:6basis traces +mixed exact counterexample;18cases preserved; only6 expected e fields differ;0compiledcalls')
