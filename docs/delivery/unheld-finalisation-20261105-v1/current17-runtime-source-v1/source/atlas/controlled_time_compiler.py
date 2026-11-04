"""Dedicated typed physical-time catalogue and transactional flat ABI generator."""
import hashlib,json
from pathlib import Path
from .dsl import cpp,parse
from .model import load,controlled_time
from .controlled_time import control_fields,size,identity

def generate(destination,model_paths):
    models=[load(p) for p in sorted(model_paths)]
    if not models or any(not controlled_time(m) for m in models):raise ValueError('dedicated controlled-time catalogue accepts controlled_ode models only')
    if len({m['id'] for m in models})!=len(models):raise ValueError('duplicate controlled-time model identity')
    dest=Path(destination);dest.mkdir(parents=True,exist_ok=True)
    lines=['// Generated generic controlled physical-time evaluator.', '#pragma once','#include "atlas/expm.hpp"','#include "atlas/checked_trace.hpp"','#include "atlas/checked_expression.hpp"','namespace atlas { namespace controlled_time_generated {','inline bool evaluate(int model,const std::vector<double>& z,const std::vector<double>& params,const std::vector<double>& inputs,std::vector<double>& rates,std::vector<double>& observables,std::vector<double>& scales,bool initial=false){using T=double;bool atlas_eval_ok=true;const auto I=identity<T>();std::vector<double>rr,oo,ss;switch(model){']
    metadata=[];definitions=[];shapes=[]
    for index,m in enumerate(models):
        controls=[];offset=0
        for f in control_fields(m):controls.append(dict(**f,offset=offset,size=size(f)));offset+=size(f)
        nc=offset;controlmap={f['name']:f for f in controls}
        inputs=[];offset=0;bindings=[]
        for n,f in m['formulation']['inputs']['equation'].items():
            inputs.append(dict(name=n,**f,offset=offset,size=size(f)));offset+=size(f)
            bindings.append('{-1,1,0}' if n=='time' else '{'+','.join(str(x) for x in (controlmap[f['binding']['control']]['offset'],size(f),f['binding']['derivative_order']))+'}')
        ni=offset;ns=sum(size(f) for f in m['state']);np=len(m['parameters']);no=sum(size(f) for f in m.get('observables',[]))
        lines += [f'case {index}:{{',f'if(z.size()!={ns}||params.size()!={np}||inputs.size()!={ni})return false;','for(double x:z)if(!std::isfinite(x))return false;','for(double x:inputs)if(!std::isfinite(x))return false;']
        for j,(n,f) in enumerate(m['parameters'].items()):lines += [f'const T {n}=params[{j}];',f'if(!std::isfinite({n})||{n}<{float(f["min"])!r}||{n}>{float(f["max"])!r})return false;']
        for f in inputs:lines.append(f'const auto {f["name"]}=tensor_from(inputs,{f["offset"]});' if f['size']==6 else f'const T {f["name"]}=inputs[{f["offset"]}];')
        if m['formulation']['kinematics']=='axisymmetric_x':lines.append('if(!axisymmetric_x(strain_rate))return false;')
        states=[];offset=0
        for f in m['state']:
            states.append(dict(name=f['name'],offset=offset,size=size(f),unit=f['unit'],semantics=f['semantics']))
            lines.append(f'const auto {f["name"]}=tensor_from(z,{offset});' if size(f)==6 else f'const T {f["name"]}=z[{offset}];');offset+=size(f)
        for f in m['derived']:lines += [f'const auto {f["name"]}={cpp(parse(f["expr"]))};',f'if(!atlas_eval_ok||!atlas::finite_value({f["name"]}))return false;']
        for c in m['domain']:lines.append(f'if(!({cpp(parse(c))})||!atlas_eval_ok)return false;')
        for c in m.get('initial_checks',[]):lines.append(f'if(initial&&(!({cpp(parse(c))})||!atlas_eval_ok))return false;')
        lines.append(f'rr.resize({ns});');offset=0
        for f in m['state']:
            expr=cpp(parse(m['equations'][f['name']]))
            lines.append(f'put_tensor(rr,{offset},{expr});' if size(f)==6 else f'rr[{offset}]={expr};');offset+=size(f)
        lines.append(f'oo.resize({no});');offset=0;obs=[]
        for f in m.get('observables',[]):
            obs.append(dict(name=f['name'],offset=offset,size=size(f),unit=f['unit']))
            expr=cpp(parse(f['expr']));lines.append(f'put_tensor(oo,{offset},{expr});' if size(f)==6 else f'oo[{offset}]={expr};')
            if m['formulation']['kinematics']=='axisymmetric_x' and f['name']=='stress':lines.append(f'if(!axisymmetric_x(tensor_from(oo,{offset})))return false;')
            offset+=size(f)
        lines += ['ss={'+','.join(cpp(parse(f['scale'])) for f in m['state'] for _ in range(size(f)))+'};','if(!atlas_eval_ok)return false;','for(double x:rr)if(!std::isfinite(x))return false;','for(double x:oo)if(!std::isfinite(x))return false;','for(double x:ss)if(!std::isfinite(x)||x<=0)return false;','rates=std::move(rr);observables=std::move(oo);scales=std::move(ss);return true;}']
        constraints=[{'finite':0,'positive_finite':1,'nonnegative_finite':2}[f['constraint']] for f in controls for _ in range(f['size'])]
        definitions.append('{'+str(nc)+',{'+','.join(map(str,constraints))+'},{'+','.join(bindings)+'},[](const auto&z,const auto&p,const auto&i,auto&r,auto&o,auto&s,bool initial){return atlas::controlled_time_generated::evaluate('+str(index)+',z,p,i,r,o,s,initial);}}')
        shapes.append('{'+','.join(map(str,[ns,np,nc,no,6,4]))+'}')
        metadata.append(dict(id=m['id'],model_sha256=identity(m),controls=controls,state=states,observables=obs,parameters=list(m['parameters']),inputs=inputs,formulation=m['formulation']))
    lines += ['default:return false;}}','}}']
    helpers={'atlas::determinant_or_mark(':'checked_determinant.hpp','atlas::principal_centered_mid_gt_or_mark(':'checked_centered_middle.hpp','atlas::principal_max_repeated_or_mark(':'checked_spectral_multiplicity.hpp','atlas::principal_min_repeated_or_mark(':'checked_spectral_multiplicity.hpp','atlas::principal_range_le_or_mark(':'checked_principal_range.hpp','atlas::normalized_determinant_or_mark(':'checked_normalized_determinant.hpp','atlas::spectral_scalar_or_mark(':'checked_spectral.hpp','atlas::spectral_projector_or_mark(':'checked_spectral.hpp'}
    for header in sorted({v for k,v in helpers.items() if any(k in l for l in lines)}):lines.insert(2,'#include "atlas/'+header+'"')
    (dest/'controlled_time_models.hpp').write_text('\n'.join(lines)+'\n')
    catalogue=dict(profile='controlled-time-ode-v1',models=metadata)
    catalogue_hash=hashlib.sha256(json.dumps(catalogue,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    catalogue['catalogue_sha256']=catalogue_hash
    catalogue_bytes=(json.dumps(catalogue,indent=2)+'\n').encode()
    catalogue_file_hash=hashlib.sha256(catalogue_bytes).hexdigest()
    (dest/'controlled_time_catalogue.json').write_bytes(catalogue_bytes)
    (dest/'controlled_time_api.cpp').write_text(API.replace('DEFINITIONS',','.join(definitions)).replace('SHAPES',','.join(shapes)).replace('MODEL_HASHES',','.join(json.dumps(identity(m)) for m in models)).replace('CATALOGUE_HASH',catalogue_hash).replace('CATALOGUE_FILE_HASH',catalogue_file_hash))
    return models

API=r'''// Generated checked controlled-time C ABI, all writes after success.
#include "controlled_time_models.hpp"
#include "atlas/controlled_time_runtime.hpp"
#include <array>
#include <cstdint>
using namespace atlas::controlled_time;
static const std::vector<Definition> definitions={DEFINITIONS};
static const std::vector<std::array<int,6>> shapes={SHAPES};
static const char* model_hashes[]={MODEL_HASHES};
extern "C" const char* controlled_time_model_hash(int m){return m>=0&&size_t(m)<definitions.size()?model_hashes[m]:nullptr;}
extern "C" const char* controlled_time_catalogue_hash(){return "CATALOGUE_HASH";}
extern "C" const char* controlled_time_catalogue_file_hash(){return "CATALOGUE_FILE_HASH";}
struct Range{std::uintptr_t lo,hi;};
static bool range(const double*p,int n,Range&r){if(n<0||(n>0&&!p))return false;const auto lo=reinterpret_cast<std::uintptr_t>(p);if(size_t(n)>std::numeric_limits<std::uintptr_t>::max()/sizeof(double))return false;const auto bytes=size_t(n)*sizeof(double);if(lo>std::numeric_limits<std::uintptr_t>::max()-bytes)return false;r={lo,lo+bytes};return true;}
static bool disjoint(Range a,Range b){return a.lo==a.hi||b.lo==b.hi||a.hi<=b.lo||b.hi<=a.lo;}
static bool buffers(const std::vector<std::pair<const double*,int>>&in,const std::vector<std::pair<double*,int>>&out){std::vector<Range>i,o;Range r;for(auto a:in){if(!range(a.first,a.second,r))return false;i.push_back(r);}for(auto a:out){if(!range(a.first,a.second,r))return false;o.push_back(r);}for(size_t k=0;k<o.size();++k){for(auto a:i)if(!disjoint(o[k],a))return false;for(size_t j=0;j<k;++j)if(!disjoint(o[k],o[j]))return false;}return true;}
static bool valid(int m){return m>=0&&size_t(m)<definitions.size();}
static std::vector<double>copy(const double*p,int n){return n?std::vector<double>(p,p+n):std::vector<double>();}
extern "C" int controlled_time_size(int m,int f){return valid(m)&&f>=0&&f<6?shapes[m][f]:-1;}
extern "C" int controlled_time_evaluate(int m,const double*z,int ns,const double*p,int np,double time,const double*v,int nc,const double*cr,int nr,int initial,double*rate,int nrate,double*obs,int no,double*scale,int nscale){try{
 if(!valid(m)||ns!=shapes[m][0]||np!=shapes[m][1]||nc!=shapes[m][2]||nr!=nc||no!=shapes[m][3]||nrate!=ns||nscale!=ns||(initial!=0&&initial!=1)||!buffers({{z,ns},{p,np},{v,nc},{cr,nr}},{{rate,nrate},{obs,no},{scale,nscale}}))return 0;
 Context parent{copy(z,ns),time,copy(v,nc),copy(cr,nr),copy(p,np)};std::vector<double>r,o,s;if(!evaluate(definitions[m],parent,initial,r,o,s)||o.size()!=size_t(no))return 0;
 std::copy(r.begin(),r.end(),rate);std::copy(o.begin(),o.end(),obs);std::copy(s.begin(),s.end(),scale);return 1;
 }catch(...){return 0;}}
extern "C" int controlled_time_advance(int m,const double*z,int ns,const double*p,int np,double time,double duration,const double*v,int nc,const double*cr,int nr,const double*start,int nstart,const double*end,int nend,const double*settings,int nsettings,double*out,int nout,double*outtime,int ntime,double*outv,int nv,double*outr,int nout_rates,double*obs,int no,double*diag,int nd){try{
 if(!valid(m)||ns!=shapes[m][0]||np!=shapes[m][1]||nc!=shapes[m][2]||nr!=nc||nstart!=nc||nend!=nc||nsettings!=6||nout!=ns||ntime!=1||nv!=nc||nout_rates!=nc||no!=shapes[m][3]||nd!=4||!buffers({{z,ns},{p,np},{v,nc},{cr,nr},{start,nstart},{end,nend},{settings,nsettings}},{{out,nout},{outtime,ntime},{outv,nv},{outr,nout_rates},{obs,no},{diag,nd}}))return 0;
 for(int i=0;i<6;++i)if(!std::isfinite(settings[i]))return 0;if(settings[4]!=std::floor(settings[4])||settings[4]<1||settings[4]>60||settings[5]!=std::floor(settings[5])||settings[5]<1||settings[5]>1000000)return 0;
 Settings s{settings[0],settings[1],settings[2],settings[3],int(settings[4]),int(settings[5])};Context parent{copy(z,ns),time,copy(v,nc),copy(cr,nr),copy(p,np)},result;std::vector<double>o;Diagnostics d;
 if(!advance(definitions[m],parent,duration,copy(start,nstart),copy(end,nend),s,result,o,d)||o.size()!=size_t(no))return 0;
 std::copy(result.state.begin(),result.state.end(),out);*outtime=result.time;std::copy(result.controls.begin(),result.controls.end(),outv);std::copy(result.rates.begin(),result.rates.end(),outr);std::copy(o.begin(),o.end(),obs);diag[0]=d.trials;diag[1]=d.accepted;diag[2]=d.rejected;diag[3]=d.error;return 1;
 }catch(...){return 0;}}
'''
