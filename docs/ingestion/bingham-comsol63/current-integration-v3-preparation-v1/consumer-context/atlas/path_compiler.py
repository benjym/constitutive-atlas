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
        from .path import control_names
        metadata.append(dict(id=m['id'],controls=control_names(m),state=states,observables=obs,parameters=list(m['parameters']),inputs=inputs,formulation=m['formulation'],model_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    lines += ['default:return false;','}}','}}']
    # Preserve availability of every checked DSL helper in the new profile.
    helper_headers={
        'atlas::determinant_or_mark(': 'checked_determinant.hpp',
        'atlas::principal_centered_mid_gt_or_mark(': 'checked_centered_middle.hpp',
        'atlas::principal_max_repeated_or_mark(': 'checked_spectral_multiplicity.hpp',
        'atlas::principal_min_repeated_or_mark(': 'checked_spectral_multiplicity.hpp',
        'atlas::principal_range_le_or_mark(': 'checked_principal_range.hpp',
        'atlas::normalized_determinant_or_mark(': 'checked_normalized_determinant.hpp',
        'atlas::spectral_scalar_or_mark(': 'checked_spectral.hpp',
        'atlas::spectral_projector_or_mark(': 'checked_spectral.hpp',
    }
    needed={header for marker,header in helper_headers.items() if any(marker in line for line in lines)}
    for header in sorted(needed): lines.insert(2, '#include "atlas/'+header+'"')
    (dest/'path_models.hpp').write_text('\n'.join(lines)+'\n')
    (dest/'path_catalogue.json').write_text(json.dumps(dict(profile='controlled-path-ode-v1',models=metadata),indent=2)+'\n')
    generate_api(dest,models)
    return models


def generate_api(destination,models):
    """Flat checked C ABI, shared by native ctypes and Wasm memory callers."""
    from .path import control_names
    dest=Path(destination)
    definitions=[];shapes=[]
    for index,m in enumerate(models):
        controls=control_names(m);bindings=[]
        for n,f in m['formulation']['inputs']['equation'].items():
            bindings.append('{-1,0}' if n=='path_coordinate' else '{'+str(controls.index(f['binding']['control']))+','+str(f['binding']['derivative_order'])+'}')
        definitions.append('{'+str(len(controls))+',{'+','.join(bindings)+'},[](const auto& z,const auto& p,const auto& i,auto& r,auto& o,auto& s,bool initial){return atlas::path_generated::evaluate('+str(index)+',z,p,i,r,o,s,initial);}}')
        shapes.append('{'+','.join(str(x) for x in [sum(6 if f['shape']=='sym' else 1 for f in m['state']),len(m['parameters']),len(controls),len(m['formulation']['inputs']['equation']),sum(6 if f['shape']=='sym' else 1 for f in m.get('observables',[]))])+'}')
    code='''// Generated generic path C ABI. All output writes are committed after success.
#include "path_models.hpp"
#include "atlas/path_runtime.hpp"
#include <array>
using atlas::controlled_path::Definition;
static const std::vector<Definition> definitions={DEFINITIONS};
static const std::vector<std::array<int,5>> shapes={SHAPES};
static bool valid_model(int i){return i>=0&&size_t(i)<definitions.size();}
static bool pointer_ok(const double* p,int n){return n>=0&&(n==0||p!=nullptr);}
static std::vector<double> copy_values(const double* p,int n){return n?std::vector<double>(p,p+n):std::vector<double>();}
extern "C" int path_size(int model,int field){return valid_model(model)&&field>=0&&field<5?shapes[model][field]:-1;}
extern "C" int path_evaluate(int model,const double* state,int ns,const double* params,int np,const double* inputs,int ni,double* rates,double* observed,int no,double* scales,int initial){
 try{
  if(!valid_model(model)||ns!=shapes[model][0]||np!=shapes[model][1]||ni!=shapes[model][3]||no!=shapes[model][4]||!pointer_ok(state,ns)||!pointer_ok(params,np)||!pointer_ok(inputs,ni)||!pointer_ok(rates,ns)||!pointer_ok(observed,no)||!pointer_ok(scales,ns)||(initial!=0&&initial!=1))return 0;
  std::vector<double> r,o,s;
  if(!definitions[model].evaluate(copy_values(state,ns),copy_values(params,np),copy_values(inputs,ni),r,o,s,initial))return 0;
  std::copy(r.begin(),r.end(),rates);std::copy(o.begin(),o.end(),observed);std::copy(s.begin(),s.end(),scales);return 1;
 }catch(...){return 0;}
}
extern "C" int path_advance(int model,const double* state,int ns,double coordinate,const double* params,int np,const double* current,int nc,double progress,const double* start,const double* end,const double* settings,int nsettings,double* output,double* out_coordinate,double* observed,int no){
 try{
  if(!valid_model(model)||ns!=shapes[model][0]||np!=shapes[model][1]||nc!=shapes[model][2]||no!=shapes[model][4]||nsettings!=6||!pointer_ok(state,ns)||!pointer_ok(params,np)||!pointer_ok(current,nc)||!pointer_ok(start,nc)||!pointer_ok(end,nc)||!pointer_ok(settings,nsettings)||!pointer_ok(output,ns)||!out_coordinate||!pointer_ok(observed,no))return 0;
  for(int i=0;i<6;++i)if(!std::isfinite(settings[i]))return 0;
  if(settings[4]!=std::floor(settings[4])||settings[4]<1||settings[4]>60||settings[5]!=std::floor(settings[5])||settings[5]<1||settings[5]>1000000)return 0;
  atlas::controlled_path::Settings execution{settings[0],settings[1],settings[2],settings[3],int(settings[4]),int(settings[5])};
  atlas::controlled_path::Context parent{copy_values(state,ns),coordinate,copy_values(current,nc),copy_values(params,np)},committed;
  std::vector<double> obs;
  if(!atlas::controlled_path::advance(definitions[model],parent,progress,copy_values(start,nc),copy_values(end,nc),execution,committed,obs))return 0;
  std::copy(committed.state.begin(),committed.state.end(),output);std::copy(obs.begin(),obs.end(),observed);*out_coordinate=committed.coordinate;return 1;
 }catch(...){return 0;}
}
'''.replace('DEFINITIONS',','.join(definitions)).replace('SHAPES',','.join(shapes))
    (dest/'path_api.cpp').write_text(code)
