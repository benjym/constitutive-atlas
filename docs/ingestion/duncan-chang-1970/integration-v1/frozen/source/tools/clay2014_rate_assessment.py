"""Additive replay assessment for original v1 reports; no report/source-pin rewriting.

Wasm serializes integral floats as integers. Use the original strict numeric
identity rule for raw parsed JSON, preserving boolean rejection. Numerical gates
and original source receipts remain unchanged.
"""
import argparse,json,math
from pathlib import Path
from tools import clay2014_rate_study as rates

def verify_transport(report,path):
    if report['backend']=='native':return rates.verify_transport(report,path)
    rates.require(rates.sha(path)==report.get('transport_sha256'),'transport file binding')
    raw=rates.read(path);calls=report['calls'];expected=[report['descriptor']]+[c['response']for c in calls]
    rates.require(type(raw)is list and len(raw)==len(expected),'Wasm raw row count')
    for i,(row,want)in enumerate(zip(raw,expected)):
        rates.require(type(row)is dict and row.get('name')==('atlas_describe'if i==0 else 'atlas_research_rate'),'C ABI function')
        rates.require(row.get('types')==([]if i==0 else ['string']*4),'C ABI types')
        args=row.get('args');rates.require(type(args)is list and len(args)==(0 if i==0 else 4),'C ABI arguments')
        if i:
            r=calls[i-1]['request'];rates.require(args[0]==r['model'],'C ABI model')
            for value,key in zip(args[1:],('parameters','state','increment')):
                rates.require(type(value)is str,'C ABI CSV');parsed=[float(x)for x in value.split(',')]
                rates.require(all(rates.finite(x)for x in parsed)and parsed==r[key],'C ABI CSV/request')
        rates.require(type(row.get('raw'))is str,'Wasm raw response string')
        parsed=json.loads(row['raw'],parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite JSON')))
        rates.require(rates.same(parsed,want),'Wasm raw response binding')
    return len(expected)

def compare(wasm,native,native_path,wasm_transport,native_transport):
    rates.verify(wasm);rates.verify(native);rates.require(rates.same(rates.read(native_path),native),'native parsed report/file mismatch')
    rates.require(wasm['backend']=='wasm'and native['backend']=='native','parity backends')
    rates.require(wasm['native_report_sha256']==rates.sha(native_path),'native report file binding')
    verify_transport(wasm,wasm_transport);verify_transport(native,native_transport)
    ref,_=rates.checked_reference();targets={c['id']:c for c in ref['cases']};maximum=0.
    for a,b in zip(wasm['calls'],native['calls']):
        rates.require(rates.same(a['request'],b['request']),'backend request mismatch')
        if a['request']['role']=='invalid':continue
        c=targets[a['request']['id']];x=a['response']['values'];y=b['response']['values']
        stress=math.hypot(*(u-v for u,v in zip(x[:6],y[:6])));void=abs(x[6]-y[6]);policy=rates.PARITY_POLICY
        sl=policy['stress_scaled_bound']*c['stress_scale']+policy['stress_absolute_floor_Pa']
        vl=policy['void_scaled_bound']*c['void_scale']+policy['void_absolute_floor']
        rates.require(stress<=sl and void<=vl,'native/Wasm parity budget');maximum=max(maximum,stress/sl,void/vl)
    return maximum

def assess(wasm_path,native_path,wasm_transport,native_transport,artifact=None):
    inputs=[('native_report',native_path),('wasm_report',wasm_path),('native_transport',native_transport),('wasm_transport',wasm_transport)]
    before={k:rates.sha(p)for k,p in inputs};own_before=rates.sha(__file__);original_before=rates.sha(rates.__file__)
    wasm=rates.read(wasm_path);native=rates.read(native_path)
    w=rates.verify(wasm);n=rates.verify(native)
    rows=dict(native=verify_transport(native,native_transport),wasm=verify_transport(wasm,wasm_transport))
    maximum=compare(wasm,native,native_path,wasm_transport,native_transport)
    if artifact is not None:rates.verify_artifacts(wasm,artifact)
    rates.require(all(rates.sha(p)==before[k]for k,p in inputs),'assessment inputs changed during replay')
    rates.require(rates.sha(__file__)==own_before and rates.sha(rates.__file__)==original_before,'assessment source changed during replay')
    return dict(version='clay2014-additive-raw-identity-assessment-v1',raw_identity='Finite int/float equality; booleans remain distinct. Original v1 reports and source pins unchanged.',change_scope="Only raw parsed-JSON numeric identity; original numerical acceptance gates unchanged.",native=n,wasm=w,transport_rows=rows,maximum_parity_budget_fraction=maximum,policy=rates.PARITY_POLICY,input_sha256=before,assessor_sha256=own_before,original_assessor_sha256=original_before,claims=wasm['claims'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('wasm-report','native-report','wasm-transport','native-transport','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--artifact',type=Path);a=p.parse_args()
    result=assess(a.wasm_report,a.native_report,a.wasm_transport,a.native_transport,a.artifact)
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k]for k in ('transport_rows','maximum_parity_budget_fraction')},sort_keys=True))
if __name__=='__main__':main()
