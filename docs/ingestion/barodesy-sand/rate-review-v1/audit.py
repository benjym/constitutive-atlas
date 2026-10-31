"""Read-only, portable audit of frozen sand2015 rate v1; no compiled calls."""
import argparse,copy,hashlib,importlib,json,math,sys
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def modules(repo):
    pins=json.loads((HERE/'reviewed-inputs.json').read_text())
    for relative,digest in pins['repository_files'].items():
        if sha(repo/relative)!=digest:raise ValueError('reviewed input changed: '+relative)
    packet=repo/'docs/ingestion/barodesy-sand/rate-study-v1'
    sys.path.insert(0,str(repo));sys.path.insert(0,str(packet))
    reference=importlib.import_module('reference');check=importlib.import_module('check')
    if Path(reference.__file__).resolve()!=packet/'reference.py' or Path(check.__file__).resolve()!=packet/'check.py':raise ValueError('wrong imported packet modules')
    return reference,check


def exact_void(c):
    return float(-(1+Fraction.from_float(float(c['state'][6])))*sum((Fraction.from_float(float(x))for x in c['loading'][:3]),Fraction(0)))


def source_diagonal(c):
    # Source2015 p54Eq9,p56Eq31, tension-positive T,D, scalar diagonal exponentials.
    p=c['parameters'];sig=c['state'][:3];d=[-x for x in c['loading'][:3]];e=c['state'][6]
    sn=math.hypot(*sig);dn=math.hypot(*d);u=[x/dn for x in d];delta=math.fsum(u)
    R=[-math.exp(p['c1']*math.exp(p['c2']*delta)*x)for x in u];rn=math.hypot(*R)
    B=(p['ec0']-p['emin'])/(p['ec0']+1)*math.exp(-(1+p['emin'])/p['c5']*math.log1p(p['c5']*sn/p['c4']))
    ec=(p['emin']+B)/(1-B);h=-(p['c4']+p['c5']*sn)/(e-p['emin'])
    td=[h*((delta+p['c3']*ec)*x/rn-p['c3']*e*(-s/sn))*dn for x,s in zip(R,sig)]
    return [-x for x in td]+[0.]*3+[exact_void(c)]


def run(repo):
    reference,check=modules(repo)
    rows=reference.read_inputs();frozen=check.checked_reference();result=check.run()
    by={r['id']:r for r in frozen['records']}
    void=[]
    for c in rows['valid']:
        want=exact_void(c);got=by[c['id']]['oracle120']['values'][6]
        ulp=0. if got==want else abs(got-want)/math.ulp(want)
        void.append({'id':c['id'],'exact_fraction_rounded_void':want,'oracle120_void':got,'ulp_error':ulp})
    if any(x['ulp_error']>0 for x in void):raise ValueError('frozen corpus void exact-rounding discrepancy')
    base=copy.deepcopy(rows['valid'][0]);diagonal=[]
    for i,E in enumerate(([.002,-.0007,.0001],[-.001,.0003,.0004],[0.,.001,-.001])):
        c=copy.deepcopy(base);c['id']='review-diagonal-'+str(i);c['state']=[1e5,1.6e5,7e4,0.,0.,0.,.75];c['loading']=list(E)+[0.]*3
        want=source_diagonal(c);actual=check.draft_rate(c)
        scale=(c['parameters']['c4']+c['parameters']['c5']*math.hypot(*c['state'][:6]))*math.hypot(*c['loading'])/(c['state'][6]-c['parameters']['emin'])
        error=max(abs(a-b)for a,b in zip(actual[:6],want[:6]))/scale
        if error>2e-12:raise ValueError('independent diagonal sign check failed')
        diagonal.append({'input':c,'source_diagonal':want,'dsl':actual,'stress_scaled_error':error})
    cancel=copy.deepcopy(base);cancel['id']='review-trace-cancellation';cancel['loading']=[500.,1e-130,-500.,0.,0.,0.]
    values={str(p):reference.evaluate(cancel,p)['values']for p in (80,120,200)}
    exact=exact_void(cancel);actual=check.draft_rate(cancel)
    try:check.assess_values(cancel,actual,values['120'])
    except ValueError as exc:assessor={'rejected':True,'message':str(exc)}
    else:assessor={'rejected':False}
    if not(values['80'][6]==values['120'][6]==0 and exact==values['200'][6]==actual[6] and exact!=0 and assessor['rejected']):raise ValueError('cancellation finding not reproduced')
    density=copy.deepcopy(base);density['id']='review-rounded-critical-density';density['parameters']['c5']=.1;density['state']=[465000*1e9/math.sqrt(3)]*3+[0.]*3+[.75]
    oracle=reference.evaluate(density,120)
    try:check.draft_rate(density)
    except ValueError as exc:dsl={'rejected':True,'message':str(exc)}
    else:dsl={'rejected':False}
    if not(oracle['ec']==density['parameters']['emin'] and dsl['rejected']):raise ValueError('rounded density finding not reproduced')
    bound=2*math.exp(1.5*math.sqrt(3))
    return {'version':'barodesy2015-rate-independent-review-0.1','compiled_execution':False,'frozen_corpus':{'valid':len(result['records']),'invalid':len(result['invalid']),'fresh_exact_reference_replay':True,'maximum_stress_scaled_error':max(x['stress_scaled_error']for x in result['records']),'exact_fraction_void_checks':void},'source_diagonal_sign_witnesses':diagonal,'expm_bound':{'proof':'abs(c1)*exp(-c2*v)<=2*exp(1.5*sqrt(3)) for ||U||=1,|trU|<=sqrt3','maximum':bound,'generic_limit':64,'within_limit':bound<64},'findings':[{'id':'F1-trace-cancellation','severity':'P2','scope':'wider accepted input envelope; frozen37 unchanged','input':cancel,'oracle_values':values,'exact_fraction_rounded_void':exact,'dsl_values':actual,'assessor':assessor,'action':'Use exact sum of actual binary64 diagonal values (Fraction or dynamically sufficient precision), then exact scalar multiplication before final rounding; do not label fixed120digit result correctly rounded across unrestricted cancellation. Revise as separate packet preserving v1.'},{'id':'F2-critical-density-domain','severity':'P2','scope':'wider source-oracle vs operational DSL acceptance contract','input':density,'oracle_ec_binary64':oracle['ec'],'oracle120_values':oracle['values'],'dsl':dsl,'action':'Separate ideal source-domain calculation from binary64 model domain; explicitly check/report rounded ec>emin for paired operational oracle or declare nonmatching support. Preserve this negative witness.'}], 'assessment':'No source/sign/expm blocker found for frozen37-case instantaneous proposal. Wider-envelope oracle/correct-rounding and domain-equivalence claims need revision. No general support certification, finite integration, objectivity or scientific admission.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    repo=a.repo or next((x for x in HERE.parents if(x/'atlas/model.py').is_file()),None)
    if repo is None:raise ValueError('supply --repo Atlas checkout')
    if a.output.exists():raise ValueError('fresh output required')
    a.output.write_text(json.dumps(run(repo),indent=2,allow_nan=False)+'\n')
