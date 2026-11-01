"""Prepare generic emitted/model/history fixtures; no compiled execution."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import migrate_formulation,load
from atlas.history_compiler import generate as history_generate
from atlas.dsl import cpp,parse
P=Path(__file__).parent

def expr(maximum,name):
 side,pair=('max','upper') if maximum else ('min','lower')
 return f'select(principal_range_le({name},0*p_ref),trace({name}/3),select(principal_{side}_repeated({name}),principal_{pair}_sum({name})/2,principal_{side}({name})))'

def prepare():
 m=migrate_formulation(load(ROOT/'models/linear-elastic.json'))
 m.update(id='synthetic-selected-principal-extrema',name='Generic selected extrema fixture',description='Generic numeric composite qualification; no constitutive law or model admission.',family='verification',derived=[{'name':'hi','expr':expr(True,'sigma')},{'name':'lo','expr':expr(False,'sigma')}],equations={'sigma':'(hi-lo)*I','e':'e-e_n'},domain=[])
 m['sources']=[{'url':'https://github.com/benjym/constitutive-atlas','locator':'spectral-multiplicity-v1/CONTRACT.md','role':'Synthetic verification fixture only'}]
 (P/'probe-model.json').write_text(json.dumps(m,indent=2)+'\n')
 generate(P/'generated',[P/'probe-model.json'])
 h=json.loads((ROOT/'tests/fixtures/log1p-history/log1p.json').read_text());h['id']='synthetic-spectral-multiplicity-history'
 h['phases'][0]['writes']['A']='select(g>0,('+expr(True,'X')+'-'+expr(False,'X')+')*I,I)'
 # History tensors here are dimensionless, so p_ref is a literal1.
 h['phases'][0]['writes']['A']=h['phases'][0]['writes']['A'].replace('p_ref','1')
 (P/'probe-history.json').write_text(json.dumps(h,indent=2)+'\n')
 (P/'generated/history.hpp').write_text(history_generate([h]))
 code=['#pragma once','#include "atlas/checked_expression.hpp"','#include "atlas/checked_spectral.hpp"','#include "atlas/checked_spectral_multiplicity.hpp"','#include "atlas/checked_principal_range.hpp"','namespace atlas {']
 for name,expression in [('maximum',expr(True,'A')),('minimum',expr(False,'A')),('lazy','select(1>0,7,principal_max(A))'),('masked','select(principal_max_repeated(A),7,9)')]:
  code.append(f'template<class T>T emitted_{name}(const Sym<T>&A,bool&atlas_eval_ok){{const T p_ref(1.);return {cpp(parse(expression))};}}')
 code.append('}')
 (P/'generated/expression.hpp').write_text('\n'.join(code)+'\n')
if __name__=='__main__':prepare()
