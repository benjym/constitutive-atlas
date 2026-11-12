"""Build the usual Atlas wire over the isolated reviewed material profile."""
from pathlib import Path
import sys

root,output=map(Path,sys.argv[1:])
include=output/'atlas'
include.mkdir(parents=True,exist_ok=True)
src=root/'cpp/include/atlas'
solver=(src/'solver.hpp').read_text()
start=solver.index('inline Advance integrate(int model,')
end=solver.index('// Pore-pressure change',start)
solver=solver[:start]+'''inline Advance weighted_profile_advance(int,const State&,const Sym<double>&,const State&,const IntegrationSettings&);
inline Advance integrate(int model,const State& parent,const Sym<double>& de,const State& params,
                         const IntegrationSettings& settings={}) {
    return weighted_profile_advance(model,parent,de,params,settings);
}
'''+solver[end:]
(include/'solver.hpp').write_text(solver+'\n#include "bridge.hpp"\n')
lin=(src/'linearize.hpp').read_text()
start=lin.index('    if(!result.advance.ok)')
(include/'linearize.hpp').write_text(lin[:start]+'''    result.message="weighted profile uses central control probes; no update tangent";
    return result;
}
}
''')
main=(root/'cpp/main.cpp').read_text()

def replace(old,new):
    global main
    if main.count(old)!=1:raise ValueError('common wire anchor changed: '+old)
    main=main.replace(old,new)

replace('''        if(e.size()!=6||c.size()!=42||k.size()<14||k.size()>35007||k.size()%7)
            throw std::runtime_error("invalid recorded wire layout");
        atlas::RecordedPath path;path.initial_strain=atlas::tensor_from(e,0);
        for(int i=0;i<6;++i){''','''        const int rows=c.size()==49&&requested_scope?7:6, width=rows+1;
        if(e.size()!=6||c.size()!=size_t(7*rows)||k.size()<size_t(2*width)||
           k.size()>size_t(5001*width)||k.size()%width)
            throw std::runtime_error("invalid recorded wire layout");
        atlas::RecordedPath path;path.initial_strain=atlas::tensor_from(e,0);path.row_count=rows;
        for(int i=0;i<rows;++i){''')
replace('''            path.controls[i].stress=c[7*i]==1;
            for(int j=0;j<6;++j)path.controls[i].coefficients.v[j]=c[7*i+1+j];
        }
        for(size_t i=0;i<k.size();i+=7){atlas::RecordedKnot knot;knot.coordinate=k[i];
            for(int j=0;j<6;++j)knot.targets[j]=k[i+1+j];path.knots.push_back(knot);}
        atlas::RecordedSettings settings;settings.material=settings_for(material_settings);''','''            auto& control=i==6?path.extra_control:path.controls[i];
            control.stress=c[7*i]==1;
            for(int j=0;j<6;++j)control.coefficients.v[j]=c[7*i+1+j];
        }
        for(size_t i=0;i<k.size();i+=width){atlas::RecordedKnot knot;knot.coordinate=k[i];
            for(int j=0;j<6;++j)knot.targets[j]=k[i+1+j];
            if(rows==7)knot.extra_target=k[i+7];
            path.knots.push_back(knot);
        }
        atlas::RecordedSettings settings;settings.material=settings_for(material_settings);
        settings.stress_per_coordinate=true;settings.max_backtracks=10;settings.finite_difference_step=1e-8;''')
replace('''        auto run=atlas::replay_recorded(m,z,p,path,settings);''','''        if(!requested_scope)throw std::runtime_error("weighted recorded paths require explicit stress scope");
        auto run=atlas::replay_recorded(m,z,p,path,settings);''')
(output/'main.cpp').write_text(main)
