"""Independent smooth reference analytic derivative audit; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import runpy,json,hashlib
B=Path(__file__).resolve().parents[2]
A=runpy.run_path(str(B/'independent-review/audit_reference.py'))
def main():
    source=json.loads((B/'smooth-v2.json').read_text());out=[]
    with localcontext()as c:
        c.prec=160
        for case in source['derivatives']:
            exact=A['analytic_columns'](case);errors=[]
            for sweep in case['sweeps']:
                errors.append(max(abs(D(v)-e)/max(D(1),abs(e))for col,ec in zip(sweep['columns'],exact)for v,e in zip(col,ec)))
            assert all(e<D('2e-5')for e in errors)
            old=A['eigen'](case['previous'][:6]);margin=D.from_float(case['previous'][6])-(old[-1]-old[0]);assert margin>D(1000)
            out.append({'id':case['id'],'domain_previous_history_margin':str(margin),'analytic_vs_source_fd_errors':list(map(str,errors))})
    return {'pass':True,'compiled_calls':0,'material_updates':0,'results':out,'smooth_sha256':hashlib.sha256((B/'smooth-v2.json').read_bytes()).hexdigest()}
if __name__=='__main__':print(json.dumps(main(),indent=2))
