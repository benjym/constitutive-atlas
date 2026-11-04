from pathlib import Path
import json,hashlib,re
N=Path('docs/delivery/unheld-finalisation-20261105-v1');Q=N/'shared-current17-review-v1/control-dispatch-design-v2';S=N/'current17-runtime-source-v1/source';catfile=N/'current17-browser-plan-v1/catalogue17.json';header=Path('/private/tmp/atlas-md1997-direct-app-v1/merged-native/generated/models.hpp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
ck('exact17 metadata',sha(catfile)=='19be5a4568830e2ac2d5e930ceb2f778a98a37c4bf31f700e6bc7ee3d41ccdac')
ck('exact generated header',sha(header)=='dbe5c22a4b5c6767a2292c8071f3d6621e6f432a26700506cabda2700599b8dc')
compiler=(S/'atlas/compiler.py').read_text();model=(S/'atlas/model.py').read_text()
ck('generated bool exactly semantic role',"str(state_role(f) == 'plastic_multiplier').lower()"in compiler)
ck('legacy multiplier compatibility mapping',"'plastic_multiplier' if field.get('multiplier')"in model)
ck('validated dimensionless scalar residualonly',"if role == 'plastic_multiplier' and (typ!=Type()"in model and "integration_kind(model)!='residual'"in model)
ck('temporary roles require zero initial',"if role != 'persistent' and (integration_kind(model) != 'residual' or any(v != 0 for v in initial))"in model)
rows=[];text=header.read_text()
for m in json.loads(catfile.read_text())['models']:
 roles=[f.get('semantics',{}).get('role','plastic_multiplier'if f.get('multiplier')else'increment_unknown'if f.get('transient')else'persistent')for f in m['state']]
 selected='plastic_multiplier'in roles;form=m['formulation']['equation_form'];line=next(x for x in text.splitlines()if x.startswith('{'+json.dumps(m['id'])+','));fields=line.split(',{{',1)[1].split('}},{{',1)[0]
 ck('generated classification '+m['id'],bool(re.search(r', true, true\}',fields+'}'))==selected)
 ck('declared multiplier residualonly '+m['id'],not selected or form=='incremental_residual')
 rows.append({'id':m['id'],'equation_form':form,'multiplier_fields':[f['name']for f,r in zip(m['state'],roles)if r=='plastic_multiplier'],'proposed_class':'unchanged640 audited derivative'if selected else'historical702 directional FD','plasticity_inference':'none; field role is algorithmic capability'})
ck('four declared predictor class',[x['id']for x in rows if x['multiplier_fields']]==['drucker-prager','manzari-dafalias-1997-constant-m-be-v1','modified-cam-clay','s-clay1'])
ck('known implicit plastic counterexamples excluded',all(next(x for x in rows if x['id']==id)['multiplier_fields']==[]for id in ['mohr-coulomb','original-cam-clay-sw-electronic-log-recovery-v1','tresca-associated-perfect-bk2022v1-be']))
(Q/'classification.json').write_text(json.dumps(rows,indent=2)+'\n')
(Q/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'compiled_calls':0},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks)}))
