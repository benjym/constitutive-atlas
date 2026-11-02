#!/usr/bin/env python3
"""Independent Cartesian matrix host + fixed-step RK4. No Atlas/model import."""
import json, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def contraction(a,b):return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def rhs(y,d,p):
 sn,sp,tx,tz,e=y
 # Compute original extension-positive source action, then reverse stress.
 T=[[-sn,-tx,-tz],[-tx,-sp,0],[-tz,0,-sp]]
 D=[[-d[2],-d[0]/2,-d[1]/2],[-d[0]/2,0,0],[-d[1]/2,0,0]]
 tr=sum(T[i][i] for i in range(3))
 H=[[v/tr for v in row] for row in T]
 Z=[[H[i][j]-(1/3 if i==j else 0) for j in range(3)] for i in range(3)]
 j=contraction(Z,Z);u=math.sqrt(3*j)
 if j==0:F=1.
 else:
  C=mm(mm(Z,Z),Z);c=-math.sqrt(6)*sum(C[i][i] for i in range(3))/j**1.5
  F=math.sqrt(u*u/8+(2-u*u)/(2+math.sqrt(2)*u*c))-u/(2*math.sqrt(2))
 a=math.sqrt(3)*(3-math.sin(p['phi_c']))/(2*math.sqrt(2)*math.sin(p['phi_c']))
 rho=math.exp(-(-tr/p['hs'])**p['n']);ed=p['ed0']*rho;ec=p['ec0']*rho;ei=p['ei0']*rho
 fd=((e-ed)/(ec-ed))**p['alpha'];fe=(ec/e)**p['beta']
 B=3+a*a-math.sqrt(3)*a*((p['ei0']-p['ed0'])/(p['ec0']-p['ed0']))**p['alpha']
 fb=p['hs']/p['n']*(1+ei)/ei*(p['ei0']/p['ec0'])**p['beta']*(-tr/p['hs'])**(1-p['n'])/B
 factor=fb*fe/contraction(H,H);hd=contraction(H,D);dn=math.sqrt(contraction(D,D))
 R=[[factor*(F*F*D[i][j]+a*a*hd*H[i][j]+fd*a*F*(H[i][j]+Z[i][j])*dn) for j in range(3)] for i in range(3)]
 return [-R[0][0],-R[1][1],-R[0][1],-R[0][2],(1+e)*sum(D[i][i] for i in range(3))]

def rk4(y,d,p,n,progress):
 h=progress/n
 for _ in range(n):
  a=rhs(y,d,p);b=rhs([v+h*k/2 for v,k in zip(y,a)],d,p);c=rhs([v+h*k/2 for v,k in zip(y,b)],d,p);z=rhs([v+h*k for v,k in zip(y,c)],d,p)
  y=[v+h*(aa+2*bb+2*cc+zz)/6 for v,aa,bb,cc,zz in zip(y,a,b,c,z)]
 return y

def stress(y):return [y[0],y[1],y[1],math.sqrt(2)*y[2],0.,math.sqrt(2)*y[3]]
def main():
 policy=json.loads((ROOT/'policy.json').read_text());rows=[];passed=True
 for c in policy['cases']:
  versions=[]
  for n in policy['reference']['steps_per_segment']:
   y=c['initial'][:];start=c['start_controls'];ends=[]
   for seg in c['segments']:
    end=seg['end_controls'];d=[(end[k]-start[k])/seg['progress'] for k in ['gamma_x','gamma_z','normal_strain']]
    y=rk4(y,d,policy['parameters'],n,seg['progress']);ends.append({'state':y[:],'stress':stress(y)});start=end
   versions.append({'steps':n,'endpoints':ends})
  delta=max(abs(a-b)/s for aa,bb in zip(versions[-2]['endpoints'],versions[-1]['endpoints']) for a,b,s in zip(aa['state'],bb['state'],policy['reference']['scale']))
  ok=delta<=policy['reference']['convergence_scaled_absolute'];passed &=ok
  rows.append({'case':c['name'],'converged':ok,'last_refinement_scaled_difference':delta,'refinements':versions})
 report={'identity':'interface2016-Cartesian-RK4-reference-v1','policy_sha256':hashlib.sha256((ROOT/'policy.json').read_bytes()).hexdigest(),'reference_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'all_converged':passed,'rows':rows,'compiled_calls':0}
 (ROOT/'references.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'all_converged':passed,'cases':len(rows),'max_refinement_difference':max(x['last_refinement_scaled_difference'] for x in rows)}))
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
