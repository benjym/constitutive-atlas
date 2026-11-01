"""Generic C++ evaluator generation for the declared controlled path profile."""
import hashlib,json
from pathlib import Path
from .dsl import cpp,parse


def generate_models(destination,models):
    dest=Path(destination);dest.mkdir(parents=True,exist_ok=True)
    lines=['// Generated declarative path ODE evaluator; no model-specific runtime.', '#pragma once','#include "atlas/expm.hpp"','#include "atlas/checked_trace.hpp"','#include "atlas/checked_expression.hpp"','namespace atlas { namespace path_generated {',
           'inline bool evaluate(int model,const std::vector<double>& z,const std::vector<double>& params,const std::vector<double>& inputs,std::vector<double>& rates,std::vector<double>& observables,std::vector<double>& scales,bool initial=false) { using T=double; bool atlas_eval_ok=true; const auto I=identity<T>(); std::vector<double> rr,oo,ss; switch(model) {']
    metadata=[]
    for index,m in enumerate(models):
        inputs=m['formulation']['inputs']['equation']; count=sum(6 if f['shape']=='sym' else 1 for f in m['state'])
        lines += [f'case {index}: {{',f'if(z.size()!={count} || params.size()!={len(m["parameters"])} || inputs.size()!={len(inputs)}) return false;', 'for(double x:z) if(!std::isfinite(x)) return false;','for(double x:inputs) if(!std::isfinite(x)) return false;']
        for j,(n,f) in enumerate(m['parameters'].items()):
            lines += [f'const T {n}=params[{j}];',f'if(!std::isfinite({n}) || {n}<{float(f["min"])!r} || {n}>{float(f["max"])!r}) return false;']
        for j,n in enumerate(inputs): lines += [f'const T {n}=inputs[{j}];']
        offset=0; scales=[]; states=[]
        for f in m['state']:
            n=f['name'];size=6 if f['shape']=='sym' else 1
            lines += [f'const auto {n}=tensor_from(z,{offset});' if size==6 else f'const T {n}=z[{offset}];']
            states.append(dict(name=n,offset=offset,size=size));offset+=size;scales.extend([cpp(parse(f['scale']))]*size)
        for f in m['derived']:
            lines += [f'const auto {f["name"]}={cpp(parse(f["expr"]))};',f'if(!atlas_eval_ok || !atlas::finite_value({f["name"]})) return false;']
        for condition in m['domain']:lines += [f'if(!({cpp(parse(condition))}) || !atlas_eval_ok) return false;']
        for condition in m.get('initial_checks',[]):lines += [f'if(initial && (!({cpp(parse(condition))}) || !atlas_eval_ok)) return false;']
        lines += [f'rr.resize({count});'];offset=0
        for f in m['state']:
            ex=cpp(parse(m['equations'][f['name']]));size=6 if f['shape']=='sym' else 1
            lines += [f'put_tensor(rr,{offset},{ex});' if size==6 else f'rr[{offset}]={ex};'];offset+=size
        obs=[];offset=0
        for f in m.get('observables',[]):
            size=6 if f['shape']=='sym' else 1;obs.append(dict(name=f['name'],offset=offset,size=size));offset+=size
        lines += [f'oo.resize({offset});'];offset=0
        for f in m.get('observables',[]):
            ex=cpp(parse(f['expr']));size=6 if f['shape']=='sym' else 1
            lines += [f'put_tensor(oo,{offset},{ex});' if size==6 else f'oo[{offset}]={ex};']
            if m['formulation']['kinematics']=='axisymmetric_x' and f['name']=='stress':lines += [f'if(!axisymmetric_x(tensor_from(oo,{offset}))) return false;']
            offset+=size
        lines += ['ss={'+','.join(scales)+'};','if(!atlas_eval_ok) return false;','for(double x:rr) if(!std::isfinite(x)) return false;','for(double x:oo) if(!std::isfinite(x)) return false;','for(double x:ss) if(!std::isfinite(x) || x<=0) return false;','rates=std::move(rr);observables=std::move(oo);scales=std::move(ss);return true;','}']
        metadata.append(dict(id=m['id'],state=states,observables=obs,parameters=list(m['parameters']),inputs=inputs,formulation=m['formulation'],model_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    lines += ['default:return false;','}}','}}']
    (dest/'path_models.hpp').write_text('\n'.join(lines)+'\n')
    (dest/'path_catalogue.json').write_text(json.dumps(dict(profile='controlled-path-ode-v1',models=metadata),indent=2)+'\n')
    return models
