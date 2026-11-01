"""Frozen saved-response gate; no candidate or compiled execution."""
from pathlib import Path
import argparse,gzip,json,math,hashlib
P=Path(__file__).parent
BRANCH={0:'elastic',1:'upper',2:'lower',3:'face'}
def assess(rows,requests,reference,policy):
    assert len(rows)==len(requests)==policy['requests'];refs={r['id']:r['reference']for r in reference['cases']};hist={str(r['step']):r['reference']for r in reference['history']}
    failures=[];gaps=[];checked=0;derivatives=0;worst_value=0.;worst_derivative=0.;rejects=0;accepted=0
    def fail(row,kind,**extra):failures.append(dict(id=row['id'],kind=kind,**extra))
    def numbers(row,actual,expected,tolerance,kind):
        nonlocal checked,derivatives,worst_value,worst_derivative
        if len(actual)!=len(expected):fail(row,kind+'-shape');return
        for i,(a,e)in enumerate(zip(actual,expected)):
            e=float(e)
            if type(a)not in (int,float)or not math.isfinite(a):fail(row,kind+'-nonfinite',component=i);continue
            error=abs(a-e)/max(1.,abs(e))
            if kind=='derivative':derivatives+=1;worst_derivative=max(worst_derivative,error)
            else:checked+=1;worst_value=max(worst_value,error)
            if error>tolerance:fail(row,kind+'-accuracy',component=i,error=error,actual=a,expected=e)
    for row,request in zip(rows,requests):
        assert row['id']==request['id'] and row['mode']==request['mode']
        if not row['input_unchanged']:fail(row,'input-mutated')
        if not row['baseline_recovery']:fail(row,'same-instance-recovery')
        if row['ok']:accepted+=1
        else:rejects+=1
        group=request['group']
        if group=='negative':
            if row['ok']:fail(row,'required-rejection-accepted')
            if request['mode']=='solve'and row['shape']and not row['ok']and not row['returned_parent']:fail(row,'failed-state-not-parent')
            continue
        if group=='transaction':
            if row['ok']or row['tentative_ok']or not row['tentative_changed']or not row['returned_parent']:fail(row,'tentative-rollback-transaction')
            continue
        ref=hist[request['case_id']]if group=='history-restart'else refs[request['case_id']]
        if group=='history-restart'and not ref['parent_admissible']:
            if row['ok']:fail(row,'source-invalid-rounded-parent-accepted',yield_excess=ref['parent_yield_excess'])
            elif not row['returned_parent']:fail(row,'source-invalid-parent-rollback')
            continue
        if not row['ok']:fail(row,'source-valid-case-rejected');continue
        expected=ref['returned_state']if request['mode']=='solve'else ref['residual']
        numbers(row,row['values'],expected,2e-9,'value')
        actual_branch=BRANCH.get(row['branch']);source_branch=ref['branch'];scale=max(1.,*(abs(float(x))for x in ref['eigenvalues']),2*request['input']['parameters']['k']);distances=list(map(float,ref['boundary_distances']));near=[abs(x)<=1e-10*scale for x in distances]
        allowed={source_branch}
        if near[0]:allowed|={'elastic','face'}
        if near[1]:allowed|={'face','upper'}
        if near[2]:allowed|={'face','lower'}
        if actual_branch not in allowed:fail(row,'unsupported-branch',source_branch=source_branch,actual_branch=actual_branch)
        if request['mode']=='jet':
            if actual_branch!=source_branch:
                gaps.append(dict(id=row['id'],kind='adjacent-selected-derivative-not-qualified',source_branch=source_branch,actual_branch=actual_branch));continue
            if len(row['derivatives'])!=12 or any(len(v)!=38 for v in row['derivatives']):fail(row,'derivative-matrix-shape');continue
            for j in range(38):numbers(row,[v[j]for v in row['derivatives']],ref['directions'][j]['residual'],2e-8,'derivative')
    return dict(version='tresca-pressure-split-v2-assessment-0.1',qualification_pass=not failures and not gaps,requests=len(rows),accepted=accepted,rejected=rejects,value_components=checked,derivative_components=derivatives,maximum_normalized_value_error=worst_value,maximum_normalized_derivative_error=worst_derivative,failures=failures,coverage_gaps=gaps)
def run(packet,root):
    global P
    P=packet;requests=json.loads((P/'requests.json').read_text())['requests'];reference=json.loads(gzip.decompress((root/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes()));policy=json.loads((P/'policy.json').read_text());out={}
    for backend in ('native','wasm'):
        rows=[json.loads(line)for line in (P/(backend+'-responses.jsonl')).read_text().splitlines()];out[backend]=assess(rows,requests,reference,policy)
    out['overall_pass']=all(out[b]['qualification_pass']for b in ('native','wasm'));return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();out=run(P,a.root)
    if a.output:
        assert not a.output.exists();a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({b:{k:v for k,v in out[b].items()if k not in ('failures','coverage_gaps')}|dict(failures=len(out[b]['failures']),coverage_gaps=len(out[b]['coverage_gaps']))for b in ('native','wasm')}));print('overall_pass',out['overall_pass'])
