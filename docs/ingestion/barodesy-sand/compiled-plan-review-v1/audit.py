"""Read-only prospective mapping audit; no compiled execution or rate collection."""
from pathlib import Path
from fractions import Fraction
import argparse
import copy
import hashlib
import json
import math
import subprocess
import sys

PACKET=Path('docs/ingestion/barodesy-sand/rate-study-v2')
STUDY=Path('catalogue/investigations/barodesy2015-rates-v1')
ORDER=['c1','c2','c3','c4','c5','ec0','emin']
EXCLUDED=['boolean-loading','nonfinite-text','extra-parameter','missing-parameter']

def require(ok,msg):
    if not ok:raise ValueError(msg)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def same(a,b):return canonical(a)==canonical(b)
def real(x):return type(x)in(int,float)and math.isfinite(x)

def audit(repo, supplied=None, fresh=True):
    repo=Path(repo);pdir=repo/PACKET;sdir=repo/STUDY
    p=read(sdir/'protocol.json')if supplied is None else copy.deepcopy(supplied)
    model=read(pdir/'model-draft.json');policy=read(pdir/'protocol.json')
    inputs=read(pdir/'inputs.json');reference=read(pdir/'reference.json')
    freeze=read(sdir/'prospective-freeze.json')
    require(freeze['compiled_observations_at_freeze']is False,'prospective flag')
    require(type(freeze['rows_per_backend'])is int and freeze['rows_per_backend']==71,'freeze rows')
    for name,digest in freeze['files'].items():require(sha(sdir/name)==digest,'prospective pin:'+name)
    for name,digest in p['files'].items():
        require(not Path(name).is_absolute()and '..'not in Path(name).parts,'relative pin')
        require(sha(repo/name)==digest,'source pin:'+name)
    require(same(p['model_definition'],model),'model definition')
    require(p['model_file']==str(PACKET/'model-draft.json'),'model path')
    require(list(model['parameters'])==ORDER==policy['next_compiled_matrix']['parameter_order'],'parameter order')
    require([(x['name'],x['shape'])for x in model['state']]==[('sigma','sym'),('e','scalar')],'state order')
    require(model['integration']=='rate' and 'transient'not in model['state'][0],'rate state')
    valid=inputs['valid']+inputs['additional_operational_valid']
    invalid=inputs['invalid']+inputs['additional_operational_invalid']
    numeric=policy['next_compiled_matrix']['numeric_invalid_ids']
    require(len(valid)==38 and len(invalid)==20 and len(numeric)==16,'source counts')
    require(policy['next_compiled_matrix']['python_only_invalid_ids']==EXCLUDED,'type exclusions')
    require(set(numeric).isdisjoint(EXCLUDED)and set(numeric)|set(EXCLUDED)=={c['id']for c in invalid},'invalid coverage')
    require(len({c['id']for c in valid+invalid})==58,'unique source ids')
    expected={x['id']:x['oracle120']['values']for x in reference['records']}
    require(set(expected)=={c['id']for c in valid},'reference identity')
    rows=p['cases'];require(len(rows)==70 and len({x['id']for x in rows})==70,'70 unique calls')
    def args(c):
        vals=[[c['parameters'][n]for n in ORDER],c['state'],c['loading']]
        require([len(x)for x in vals]==[7,7,6],'literal dimensions')
        require(all(real(x)for xs in vals for x in xs),'finite numeric slots')
        return [model['id']]+[','.join(str(float(x))for x in xs)for xs in vals]
    for i,c in enumerate(valid):
        row=rows[i];require(row['id']=='valid:'+c['id'],'valid order')
        require(row['args']==args(c),'literal mapping:'+c['id'])
        values=expected[c['id']];require(len(values)==7 and all(real(x)for x in values),'reference channels')
        volume=-(1+Fraction.from_float(float(c['state'][6])))*sum((Fraction.from_float(float(x))for x in c['loading'][:3]),Fraction())
        require(values[6]==float(volume),'exact rational void:'+c['id'])
        if not any(c['loading']):
            require(not any(values),'zero reference');budgets=[0.]*7
        else:
            pars=c['parameters'];sn=math.hypot(*c['state'][:6]);dn=math.hypot(*c['loading'])
            scale=max((pars['c4']+pars['c5']*sn)*dn/(c['state'][6]-pars['emin']),math.hypot(*values[:6]))
            budgets=[2e-12*scale]*6+[4*math.ulp(values[6])if values[6]else 0.]
        wanted={'ok':True,'values':values,'absolute_budgets':budgets,'parity_budgets':[2*x for x in budgets]}
        require(same(row['expectation'],wanted),'reference/budget mapping:'+c['id'])
        require(set(row)=={'id','args','expectation'},'valid row shape')
    lookup={x['id']:x for x in invalid};control=rows[0]
    for j,name in enumerate(numeric):
        reject,recover=rows[38+2*j:40+2*j]
        require(same(reject,{'id':'reject:'+name,'args':args(lookup[name]),'expectation':{'ok':False}}),'numeric rejection:'+name)
        wanted=copy.deepcopy(control);wanted.update(id='recover:'+name,recovery_of=control['id'])
        require(same(recover,wanted),'same control recovery:'+name)
    mandatory={str(PACKET/name)for name in ['manifest.json','model-draft.json','inputs.json','reference.py','reference.json','support.py','protocol.json','provenance.json']}
    mandatory|={str(STUDY/'prepare.py'),'atlas/compiler.py','atlas/dsl.py','atlas/model.py','atlas/structure.py','atlas/symmetric_expm.py','atlas/scalar_math.py','schemas/model.schema.json','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp','cpp/include/atlas/expm.hpp','tests/research_rate_driver.cpp','cmake/research/CMakeLists.txt','tools/research_rate_observations.py','tools/collect_research_rates_wasm.mjs','tools/research_rate_parity.py'}
    require(mandatory<=set(p['files']),'required source coverage')
    if fresh:
        # Independent source oracle/check are Python-only. Ancestor/frozen pins and
        # complete80/120digit records, including failure diagnostics, are replayed.
        code='import check; check.checked_reference(); print("fresh source reference: PASS")'
        result=subprocess.run([sys.executable,'-B','-c',code],cwd=pdir,env={**__import__('os').environ,'PYTHONPATH':str(repo),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=60)
        require(result.returncode==0,'fresh independent replay:'+result.stderr)
    return {'version':'barodesy2015-prospective-independent-audit-v1','passed':True,'valid_calls':38,'numeric_rejection_recovery_pairs':16,'excluded_python_type_cases':EXCLUDED,'literal_calls':70,'descriptor_rows':1,'total_rows_per_backend':71,'source_pins':len(p['files']),'parameter_order':ORDER,'state_order':['xx','yy','zz','sqrt2xy','sqrt2yz','sqrt2xz','e'],'loading_order':['xx','yy','zz','sqrt2xy','sqrt2yz','sqrt2xz'],'fresh_source_reference_replayed':fresh,'compiled_execution':False,'scientific_admission':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args()
    result=audit(a.repo)
    blob=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if a.output:
        require(not a.output.exists(),'fresh output required');a.output.write_text(blob)
    print(blob,end='')
