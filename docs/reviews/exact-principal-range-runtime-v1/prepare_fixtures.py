"""Normal generator fixtures; synthetic, no material admission."""
from pathlib import Path
import json,copy
from atlas.compiler import generate
from atlas.history_compiler import generate as history_generate
from atlas.dsl import cpp,parse
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent

def prepare(dest):
    dest=Path(dest);dest.mkdir(exist_ok=True,parents=True)
    m=json.loads((ROOT/'docs/reviews/tresca-pressure-split-v1/model.json').read_text())
    m.update(id='synthetic-exact-range-predicate',name='Synthetic exact range predicate',description='Generic predicate routing fixture; not a constitutive model.',family='verification',derived=[],domain=[],initial_checks=['principal_range_le(sigma, p_ref)'],equations={'sigma':'sigma-sigma_n','ep':'ep-ep_n'})
    m['sources']=[{'url':'https://github.com/benjym/constitutive-atlas','locator':'Synthetic generic predicate qualification fixture','role':'Project verification fixture; no physical law claim'}]
    (dest/'model.json').write_text(json.dumps(m,indent=2)+'\n');generate(dest/'generated',[dest/'model.json'])
    h=json.loads((ROOT/'tests/fixtures/log1p-history/log1p.json').read_text());h['id']='synthetic-exact-range-history';h['phases'][0]['writes']['A']='select(g>0,select(principal_range_le(X,g),I,2*I),I)'
    (dest/'history.json').write_text(json.dumps(h,indent=2)+'\n');bad=copy.deepcopy(h);bad['id']='synthetic-exact-range-history-invalid';bad['phases'][0]['writes']['A']='select(g>0,select(principal_range_le(X,-g),I,2*I),I)';(dest/'generated/history.hpp').write_text(history_generate([h,bad]))
    expr=cpp(parse('principal_range_le(A,Y)'))
    (dest/'generated/expression.hpp').write_text('#pragma once\n#include "atlas/checked_principal_range.hpp"\n#include "atlas/checked_expression.hpp"\nnamespace atlas { template<class T> bool emitted(const Sym<T>& A,const T& Y,bool& atlas_eval_ok){return '+expr+';} }\n')
    for name,expression in [('masked','select(principal_range_le(A,Y),7,9)'),('lazy','select(1>0,7,select(principal_range_le(A,Y),3,4))')]:
        with (dest/'generated/expression.hpp').open('a')as out:out.write('namespace atlas { template<class T> T emitted_'+name+'(const Sym<T>& A,const T& Y,bool& atlas_eval_ok){return '+cpp(parse(expression))+';} }\n')
    return m,h
if __name__=='__main__':
    import sys;prepare(sys.argv[1])
