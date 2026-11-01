"""AI review: stdlib algebra and saved-data assessment only; no engine imports/calls."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads((ROOT/p).read_text())

def assess():
 out={"kind":"AI technical review checks", "compiled_calls":0,"author_code_executed":False}
 inv=json.loads((HERE/'inputs.json').read_text())
 bad=[r['path'] for r in inv['files'] if sha(ROOT/r['path'])!=r['sha256']]
 private=[r['path'] for r in inv['private_sources']+inv.get('external_instructions',[]) if sha(r['path'])!=r['sha256']]
 assert set(bad)<= {'IMPLEMENTATION_PLAN.md'} and not private,(bad,private)
 # Retain the original pin; board changes during coordination do not rebind science inputs.
 drift=[{'path':p,'observed_sha256':sha(ROOT/p),'classification':'concurrent live board drift; not scientific evidence'} for p in bad]
 out['input_hashes']={'public':len(inv['files']),'private':len(inv['private_sources']),'mismatches':drift,'strict_integrity_gate':'failed_live_board_drift' if drift else 'passed'}
 sanpins=load('docs/ingestion/sanisand-2004/production-closure-v1/inputs.json')['files']
 assert all(sha(ROOT/r['path'])==r['sha256'] for r in sanpins)
 out['sanisand_original_package_pins_verified']=len(sanpins)
 expected_private={'/private/tmp/atlas-mcc-source-review-v3/ModifiedCamClay_report.pdf':'a03df6d05d777bfc4d484e6e12a2aecdebcbbf16bfca3b6601e699178620e9ce','/private/tmp/atlas-clay-barodesy-source-20261031-v1/private/medicus-fellin-2017-publisher.pdf':'bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15',str(Path.home()/'Downloads/dafalias-manzari-2004-simple-plasticity-sand-model-accounting-for-fabric-change-effects.pdf'):'b6e0f6ccfd018729a9bbd8492745af649c7682a8a1e929348ae25a728917e023'}
 assert all(sha(p)==h for p,h in expected_private.items())
 out['private_primary_pdf_receipt_hashes_verified']=len(expected_private)
 # The published/native elasticity requests admit an independent Cartesian calculation.
 el=load('catalogue/evidence/reports/linear-elastic-analytical-v1.json')
 worst=0
 for r in el['cases']:
  a=r['arguments']; pref,E,nu=map(float,a[a.index('--parameters')+1].split(','))
  de=r['total_strain']; s=r['initial']; tr=sum(de[:3]); lam=E*nu/((1+nu)*(1-2*nu)); G=E/(2*(1+nu))
  ref=[s[i]+2*G*de[i]+(lam*tr if i<3 else 0) for i in range(6)]+[(1+s[6])*math.exp(-tr)-1]
  ratios=[abs(x-y)/((1e-4 if i<6 else 1e-10)+1e-10*abs(y)) for i,(x,y) in enumerate(zip(r['actual'],ref))]
  assert max(ratios)<=1,(r['id'],max(ratios))
  worst=max(worst,max(ratios))
 out['elasticity_independent_saved_endpoint_check']={'cases':len(el['cases']),'maximum_original_budget_fraction':worst,'nu_tested':[-.2,.25,.49]}
 # Closed-form scalar DP return is independently rederived here, without DSL/oracle imports.
 cases=load('catalogue/investigations/dp-dilatancy-domain-v1/cases.json')['cases']
 raw=load('catalogue/investigations/dp-dilatancy-domain-v1/results/raw.json')['calls']
 assert len(cases)==len(raw)==83
 worst=0; failures=0; successful=0
 for r,w in zip(cases,raw):
  assert r['id']==w['id']; response=json.loads(w['stdout']); a=r['arguments']
  pref,E,nu,M,Md,c=map(float,a[a.index('--parameters')+1].split(',')); s=r['initial']
  if r['expected_failure']:
   assert w['returncode']!=0 and response['ok'] is False and response['state']==s
   failures+=1;continue
  de=list(map(float,a[a.index('--strain')+1].split(',')));tr=sum(de[:3]);G=E/(2*(1+nu));K=E/(3*(1-2*nu))
  pn=sum(s[:3])/3;pt=pn+K*tr
  st=[s[i]-(pn if i<3 else 0)+2*G*(de[i]-(tr/3 if i<3 else 0)) for i in range(6)]
  qt=math.sqrt(1.5*sum(x*x for x in st));ft=qt-M*pt-c
  gam=0 if ft<=0 else ft/(3*G+M*K*Md)
  if qt-3*G*gam<0:
   assert M>0 and Md>0
   gam=(-c/M-pt)/(K*Md)
  fac=max(0,1-3*G*gam/qt) if qt else 0
  ref=[pt+K*Md*gam+fac*st[i] if i<3 else fac*st[i] for i in range(6)]+[(1+s[6])*math.exp(-tr)-1,gam]
  ratios=[abs(x-y)/((1e-4 if i<6 else 1e-9)+1e-9*abs(y)) for i,(x,y) in enumerate(zip(response['state'],ref))]
  assert w['returncode']==0 and response['ok'] is True and max(ratios)<=1,(r['id'],max(ratios))
  successful+=1;worst=max(worst,max(ratios))
 out['dp_independent_saved_check']={'requests':83,'successful':successful,'expected_failures_exact_rollback':failures,'maximum_original_budget_fraction':worst}
 # Exact witnesses; these are limitations, not newly run model failures.
 oldwork=F(1,1000)*((F(6,5)-2)*100000+10000);assert oldwork==-70
 out['dp_negative_work_witness_old_definition_Pa']=float(oldwork)
 out['zero_load_tolerance_caveat']={'accepted_scaled_yield':5e-9,'unchanged_gamma0_FB_residual':1e-8,'meaning':'Slightly exterior tolerance-admitted parents do not have an exact unchanged root. No runtime observation or failure claim.'}
 # MCC report assessment: actual accepted partition and separate continuum gates.
 mcc=load('catalogue/evidence/reports/modified-cam-clay-scalar-v2.json');assert len(mcc['cases'])==57
 refs=[]
 for r in mcc['cases']:
  assert r['passed']
  if r.get('expected_failure'):assert not r['solver_ok'] and r['returncode']!=0 and r['actual']==r['initial']
  if r.get('max_tolerance_ratio') is not None:assert r['max_tolerance_ratio']<=1
  if 'levels'in r:
   errors=[abs(sum(t['final_state'][:3])/3-r['expected_pressure'])/abs(r['expected_pressure']) for t in r['levels']]
   orders=[math.log(a/b,2)for a,b in zip(errors,errors[1:])]
   assert min(orders)>.8 and errors[-1]<5e-4
   refs.append({'id':r['id'],'final_relative_error':errors[-1],'minimum_order':min(orders)})
 cross=next(r for r in mcc['cases']if r['id']=='overconsolidated-yield-crossing')
 assert cross['diagnostics']['increment_fractions']==[.5,.5] and not cross['unpartitioned_reference']['passed'] and not cross['unpartitioned_reference']['applicable']
 phi=F(1,3);volume_rate=F(1,100)
 printed_porosity=(1+phi)*volume_rate; selected_porosity=(1-phi)*volume_rate
 assert printed_porosity/selected_porosity==2
 M=F(6,5);pc=F(200000);p=pc/2;q=M*pc/2
 assert q*q+M*M*p*(p-pc)==0
 out['mcc_report_assessment']={'cases':57,'refinement':refs,'yield_crossing_partition':[.5,.5],'unpartitioned_pressure_gap_Pa':cross['unpartitioned_reference']['expected'][0]-cross['actual'][0], 'selected_M_squared_yield_witness':0,'printed_single_M_witness_Pa2':float(q*q+M*p*(p-pc)),'printed_porosity_rate_ratio':float(printed_porosity/selected_porosity)}
 # Endpoint elastic stiffness itself imposes an incremental limitation.
 V=.03;denom=1-(1+.7)*math.exp(-V)*V/.04
 out['mcc_counterexample_elastic_trial']={'e_n':.7,'kappa':.04,'volumetric_increment':V,'elastic_trial_denominator':denom,'meaning':'No positive full-step elastic trial at this increment. A plastic/subdivided solution may exist; not an observed engine failure.'}
 assert denom<0
 # Barodesy NCL distinguishes source choices for all complete published soils.
 soils=[('London',22.6,.11,.016),('Dresden',35,.038,.008),('Weald',24,.059,.018)]
 b=[]
 for name,deg,la,ka in soils:
  s=math.sin(math.radians(deg));c5=(1+s)/(1-s);c3=(-math.sqrt(3)/la+math.sqrt(3)/ka)/(2**(c5*la)+(1/500)**(c5*la)-2)
  beta=-1/(c3*la)+(2**(c5*la)-1)/math.sqrt(3)
  body=c3/math.sqrt(3)*(2**(c5*la)-1-math.sqrt(3)*beta)
  appendix=c3/math.sqrt(3)*(6**(c5*la)-1-math.sqrt(3)*beta)
  assert math.isclose(body,1/la,rel_tol=1e-13) and not math.isclose(appendix,1/la,rel_tol=.001)
  b.append({'soil':name,'body_dlogp_dv':body,'NCL_1_over_lambda':1/la,'appendix_dlogp_dv':appendix})
 out['barodesy_independent_NCL']=b
 # Inspect numerical channel errors, not merely assessment status.
 tc=load('catalogue/investigations/terracotta-preparation-hold-refinement-v2/assessment.json')
 policy=load('catalogue/investigations/terracotta-preparation-hold-v1/policy.json')['fine_bounds'];tcworst=0
 for backend in tc['backends'].values():
  assert not backend['failures']
  for row in backend['metrics']:
   for phase in row['errors'].values():
    for channel,errors in phase.items():
     bound=policy[channel];bound=bound if isinstance(bound,list)else[bound]*len(errors)
     for e,g in zip(errors,bound):assert e<=g;tcworst=max(tcworst,e/g)
 out['terracotta_saved_component_check']={'backends':2,'paths_per_backend':3,'phases_per_path':2,'maximum_original_limit_fraction':tcworst,'old_outcome':load('catalogue/investigations/terracotta-preparation-hold-v1/assessment.json')['status']}
 # SAN independent first-yield scalar derivation and finite-product limit.
 plan=load('docs/ingestion/sanisand-2004/production-closure-v1/reference-plan.json');rows=[]
 g=plan['first_yield_grid']
 for es in g['void_ratios']:
  for ps in g['pressures_pa']:
   e=float(es);p=float(ps);G=float(g['G0'])*float(g['p_at'])*(2.97-e)**2/(1+e)*math.sqrt(p/float(g['p_at']))
   axial=p*float(g['m'])/(3*G)
   assert math.isclose(2*G*math.sqrt(1.5)*axial,math.sqrt(2/3)*p*float(g['m']),rel_tol=1e-14)
   rows.append({'e':e,'p_Pa':p,'axial_yield_magnitude':axial})
 out['sanisand_first_yield']=rows
 A=F(7);Hb=F(11);El=F(13);b0=F(17)
 limit=b0*A/Hb; seq=[]
 for d in [F(1,10**n)for n in [1,3,6,12]]:
  L=d*A/(Hb+d*El);product=L*b0/d;seq.append(float(abs(product-limit)))
 assert all(a>b for a,b in zip(seq,seq[1:]))
 out['sanisand_finite_product_limit']={'limit':float(limit),'absolute_errors':seq,'naive_L0_times_h_disallowed':True}
 out['skipped']=['No compiled execution/build','No complete journal Terra Cotta source','No Dafalias1986 original','No full plastic SANISAND trajectory oracle','No current release or hosted qualification']
 return out
if __name__=='__main__':
 result=assess()
 print(json.dumps(result,indent=2))
 # Never convert a stale pin to a pass. Independent unaffected algebra may still complete.
 sys.exit(2 if result['input_hashes']['mismatches'] else 0)
