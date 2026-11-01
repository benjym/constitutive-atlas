"""Source-compliance residual checks; no compiled observations or material solver."""
from pathlib import Path
import sys,json,hashlib,math
B=Path(__file__).resolve().parent;R=B.parents[3];sys.path.insert(0,str(R))
from atlas.model import load,interpret,check_solution_state,evaluation_environment
from atlas.compiler import generate
m=load(B/'candidate.json');refs=json.loads((B/'references.json').read_text());results=[]
for case in refs['cases']:
    def state(v):return {'sigma':v[:6],'h':v[6]}
    try:
        got=interpret(m,state(case['target']),state(case['initial']),case['de'],case['parameters']);r=list(got['sigma'].v)+[got['h']]
        expect=list(map(float,case['wire_residual']));error=max(abs(x-y)/1e5 for x,y in zip(r,expect));assert error<2e-10,(case['id'],error)
        env=evaluation_environment(m,state(case['target']),state(case['initial']),case['de'],case['parameters']);branch='unload_reload' if env['D']<case['initial'][6] else 'primary' if env['Sbar']<1 else 'postfailure'
        assert branch==case['branch'],(case['id'],'branch mismatch')
        assert check_solution_state(m,state(case['target']),case['parameters']),(case['id'],'endpoint constraint')
        results.append(dict(id=case['id'],pass_=True,residual_error=error,source_branch=case['branch'],binary_branch=branch,solution_constraints=check_solution_state(m,state(case['target']),case['parameters'])))
    except (ValueError,ArithmeticError) as e:results.append(dict(id=case['id'],pass_=False,error=str(e)))
generate(B/'generated',[B/'candidate.json'])
out=dict(identity='duncan-material-interpreter-v1',checks=results,all_residuals_pass=all(x['pass_'] for x in results),candidate_sha256=hashlib.sha256((B/'candidate.json').read_bytes()).hexdigest(),material_updates=0,compiled_calls=0)
(B/'interpreter-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}));print('constraint failures:',[x['id'] for x in results if not x.get('solution_constraints',False)]);print('branch discrepancies:',[x['id'] for x in results if x.get('source_branch')!=x.get('binary_branch')]);assert out['all_residuals_pass']
