"""Frozen independent actual-parent history oracle; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import hashlib,importlib.util,json,struct,sys
P=Path(__file__).parent;ROOT=P.parents[2]
def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def references(root):
    old=root/'docs/reviews/tresca-rounded-reference-v1';sp=imported('history_reference_spectral',old/'spectral_source.py')
    previous=sys.modules.get('spectral_source');sys.modules['spectral_source']=sp
    try:g=imported('history_independent_projection',old/'generate.py')
    finally:
        if previous is None:sys.modules.pop('spectral_source',None)
        else:sys.modules['spectral_source']=previous
    exact=imported('history_exact_membership',root/'docs/reviews/certified-spectral-range-v1/exact.py')
    return g,exact

def decode(bits):return [struct.unpack('>d',int(v).to_bytes(8,'big'))[0]for v in bits]
def encoded(values):return [str(int.from_bytes(struct.pack('>d',v),'big'))for v in values]
def assess(rows,inputs,root=ROOT):
    assert len(rows)==len(inputs['loading'])+1 and rows[-1]['summary']
    g,exact=references(root);failures=[];details=[];committed=encoded([float.fromhex(v)for v in inputs['initial']]);stopped=False;accepted=0;values=0;worst=D(0);crossworst=D(0)
    pars={k:D.from_float(float(v))for k,v in inputs['parameters'].items()};width=2*inputs['parameters']['k']
    def fail(step,kind,**kw):failures.append(dict(step=step,kind=kind,**kw))
    for step,row in enumerate(rows[:-1]):
        assert row['step']==step and row['parent_bits']==committed,('chain',step)
        if not row['attempted']:
            assert stopped;fail(step,'not-attempted-after-rejection');continue
        assert not stopped
        parent=decode(row['parent_bits']);out=decode(row['output_bits']);parent_in=exact.range_le(parent[:6],width);output_in=exact.range_le(out[:6],width)
        assert parent_in==exact.sturm_range_le(parent[:6],width) and output_in==exact.sturm_range_le(out[:6],width)
        assert row['parent_in']==parent_in and row['output_in']==output_in
        if not row['input_unchanged']:fail(step,'input-mutated')
        if not row['baseline_recovery']:fail(step,'baseline-recovery')
        if row['ok']:
            accepted+=1
            if not parent_in:fail(step,'accepted-source-invalid-parent')
            if not output_in:fail(step,'accepted-source-invalid-committed-state')
            if row['substeps']!=1:fail(step,'not-one-unsplit-update')
            assert row['committed_bits']==row['output_bits'];committed=row['output_bits']
        else:
            stopped=True;fail(step,'step-rejected',source_parent_admissible=parent_in)
            if not row['returned_parent']or row['output_bits']!=row['parent_bits']or row['committed_bits']!=row['parent_bits']:fail(step,'rollback-state-mismatch')
        precision_rows=[]
        for precision in (200,280):
            with localcontext()as ctx:
                ctx.prec=precision
                dv=[D.from_float(x)for x in parent];load=g.vec(inputs['loading'][step]);ref=g.evaluate(pars,dv,dv,load,[],precision)
                assert ref['certificate_error']<=D('1e-100'),(step,precision,'reference certificate')
                if row['ok']and parent_in:
                    for i,(got,target)in enumerate(zip(out,ref['returned_state'])):
                        error=abs(D.from_float(got)-target)/max(D(1),abs(target));values+=1;worst=max(worst,error)
                        if error>D('2e-9'):fail(step,'update-value-accuracy',precision=precision,component=i,error=str(error))
                vals,_,_,_=g.spectrum(g.cart([D.from_float(x)for x in out[:6]]),precision)
                precision_rows.append({'precision':precision,'returned_state':[str(v)for v in ref['returned_state']],'parent_yield_excess':str(ref['parent_yield_excess']),'output_yield_excess':str(max(vals)-min(vals)-2*pars['k']),'certificate_error':str(ref['certificate_error'])})
        with localcontext()as ctx:
            ctx.prec=300
            for x,y in zip(precision_rows[0]['returned_state'],precision_rows[1]['returned_state']):
                x,y=D(x),D(y);error=abs(x-y)/max(D(1),abs(y));assert error<D('1e-55');crossworst=max(crossworst,error)
        details.append({'step':step,'accepted':row['ok'],'parent_admissible':parent_in,'returned_state_admissible':output_in,'references':precision_rows})
    assert rows[-1]['accepted']==accepted and rows[-1]['stopped']==stopped and rows[-1]['final_bits']==committed and rows[-1]['scheduled']==12
    return {'version':'tresca-continuous-history-assessment-0.1','qualification_pass':not failures,'scheduled':12,'attempted':len(details),'accepted':accepted,'value_components':values,'maximum_normalized_update_error':str(worst),'reference_cross_precision_error':str(crossworst),'failures':failures,'steps':details}

def run(packet=P,root=ROOT):
    inputs=json.loads((packet/'inputs.json').read_text());out={}
    for backend in ('native','wasm'):out[backend]=assess([json.loads(l)for l in (packet/(backend+'-responses.jsonl')).read_text().splitlines()],inputs,root)
    out['overall_pass']=all(out[b]['qualification_pass']for b in ('native','wasm'));return out
if __name__=='__main__':
    report=run();print(json.dumps(report,indent=2))
