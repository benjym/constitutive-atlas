"""Read-only reproducible audit witnesses; no compiled execution or source edits."""
import argparse
from decimal import Decimal,localcontext
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
UNDER_REVIEW='docs/ingestion/hypoplastic-clay-2005/rate-study-v1'


def verify_inputs(repo):
    pins=json.loads((HERE/'reviewed-inputs.json').read_text())
    for name,digest in pins['repository_files'].items():
        if hashlib.sha256((repo/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('reviewed bytes changed:'+name)


def prospective_guard(values):
    # Illustrates a conservative common numerical interior, not a certified SPD test.
    n=math.hypot(*values)
    if not n:return False
    x,y,z,u,v,w=[x/n for x in values]
    minor=x*y-u*u/2
    det=x*y*z-(x*v*v+y*w*w+z*u*u)/2+u*v*w/math.sqrt(2)
    return min(x,y,z)>0 and minor>64*math.ulp(1.) and det>64*math.ulp(1.)


def run(repo):
    verify_inputs(repo)
    sys.path.insert(0,str(repo))
    from atlas.model import load,defaults,prepare_increment,evaluation_environment
    model=load(repo/UNDER_REVIEW/'model.json')
    pars=defaults(model)
    spec=importlib.util.spec_from_file_location('clay2005_audit_reference',repo/UNDER_REVIEW/'reference.py')
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    records=[]
    for name,third in [('rank-loss',0.),('negative-eigenvalue',-1e-20)]:
        z=[1.,1.,third,0.,0.,0.,.8];loading=[.001,0.,0.,0.,0.,0.]
        parent={'sigma':z[:6],'e':z[6]}
        prepared=prepare_increment(model,parent,loading,pars)
        env=evaluation_environment(model,parent,parent,loading,pars)
        try:
            oracle.rate(oracle.from_mandel(z[:6]),oracle.from_mandel(loading),z[6],**{n:pars[n]for n in oracle.SOURCE_PARAMETERS})
        except ValueError as exc:rejection=str(exc)
        else:raise ValueError('expected independent source oracle rejection missing')
        with localcontext() as ctx:
            ctx.prec=90
            d=Decimal.from_float(third)
            true_detH=d/(Decimal(2)+d)**3
        records.append({'id':name,'state7':z,'loading6':loading,'dsl_accepted':True,
                        'prepared_parent_unchanged':prepared==parent,
                        'computed_detH':env['detH'],'computed_pairH':env['pairH'],
                        'computed_Y':env['Y'],'dsl_rates7':list(env['stress_rate'].v)+[env['e_rate']],
                        'actual_diagonal_determinant_Pa3':str(d),
                        'actual_normalized_H_determinant':str(true_detH),
                        'independent_oracle_rejected':True,'independent_message':rejection,
                        'prospective_conservative_guard_accepts':prospective_guard(z[:6])})
    corpus=oracle.build_reference()
    eligible=[c['id']for c in corpus['cases']if prospective_guard(c['state'][:6])]
    s={'sigma':[1e5]*3+[0.]*3,'e':.8}
    env=evaluation_environment(model,s,s,[.001]*3+[0.]*3,pars)
    q,alpha,a,delta=[env[k]for k in ('Q','alpha','a','Delta')]
    plus=(q+2**alpha*a*math.sqrt(3))/(pars['lambda_star']*delta)
    minus=(q-2**alpha*a*math.sqrt(3))/(pars['lambda_star']*delta)
    return {'version':'clay2005-rate-independent-audit-v1','witnesses':records,
            'prospective_guard_note':'normalized Cartesian/Mandel leading minors and all3diagonals with64epsilon interior; illustrative recommendation, not installed or certifiedSPD',
            'existing_corpus_count':len(corpus['cases']),
            'existing_corpus_passing_prospective_guard_count':len(eligible),
            'eq38_source_check':{'private_pdf_sha256':'8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3',
                                'pdf_page':10,'page_size_pt':[595,842],
                                'equation_crop_top_origin_bbox_pt':[170,460,510,510],
                                'disputed_plus_glyph_bbox_pt':[326.279970,483.308020,334.070754,493.270660],
                                'visually_verified_printed_bracket':'Q + f_di*a*sqrt(3)',
                                'plus_unloading_coefficient':plus,'expected_inverse_kappa':1/pars['kappa_star'],
                                'counterfactual_minus_coefficient':minus,'expected_inverse_lambda':1/pars['lambda_star'],
                                'conclusion':'The historical minus assertion is contradicted by pinned manuscript; it is not a demonstrated source conflict.'},
            'scope':'Read-only Python/source visual audit, no compiled execution, no admission'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);p.add_argument('--output',type=Path);p.add_argument('--check',type=Path);a=p.parse_args()
    repo=a.repo or next((r for r in HERE.parents if(r/'atlas/model.py').is_file()),None)
    if repo is None:raise SystemExit('--repo required outside checkout')
    result=run(repo.resolve())
    if a.check and json.loads(a.check.read_text())!=result:raise SystemExit('audit evidence differs')
    if a.output:
        if a.output.exists():raise SystemExit('fresh output required')
        a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('2counterexamples reproduced; '+str(result['existing_corpus_passing_prospective_guard_count'])+'/41existing corpus inside prospective guard')
