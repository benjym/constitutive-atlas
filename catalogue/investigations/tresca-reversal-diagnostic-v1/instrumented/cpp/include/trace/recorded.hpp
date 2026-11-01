#pragma once
#include "trace/linearize.hpp"

namespace atlas_trace {
// Absolute linear targets in one fixed Mandel frame. Coordinate orders records;
// it is not physical time and does not drive material evolution.
struct RecordedControl { bool stress=false; Sym<double> coefficients; };
struct RecordedKnot { double coordinate=0; std::array<double,6> targets{}; };
struct RecordedPath {
    Sym<double> initial_strain;
    std::array<RecordedControl,6> controls;
    std::vector<RecordedKnot> knots;
};
struct RecordedSettings {
    IntegrationSettings material;
    double control_tolerance=1e-10;
    int max_iterations=30,max_backtracks=10,max_material_trials=20000;
    double finite_difference_step=1e-7;
    int max_restarts=0,restart_levels=8; double restart_step=1e-4;
};
struct RecordedPoint {
    double coordinate=0; Sym<double> strain; State state; Diagnostics diagnostics;
    double control_error=0;
};
struct RecordedResult {
    bool ok=false; std::string message; int failed_knot=-1;
    std::vector<RecordedPoint> points;
    State state; Sym<double> strain;
    int restart_searches=0,restart_trials=0,accepted_restarts=0;
    int material_trials=0,finite_difference_probes=0; long long attempted_substeps=0;
    double last_control_error=0; Sym<double> last_trial_increment;
};
inline bool valid_recorded_settings(const RecordedSettings& s){
    return valid_settings(s.material)&&std::isfinite(s.control_tolerance)&&s.control_tolerance>0&&s.control_tolerance<=1e-3&&
        s.max_iterations>=1&&s.max_iterations<=1000&&s.max_backtracks>=0&&s.max_backtracks<=30&&
        s.max_material_trials>=1&&s.max_material_trials<=1000000&&
        std::isfinite(s.finite_difference_step)&&s.finite_difference_step>0&&s.finite_difference_step<=1e-2&&s.max_restarts>=0&&s.max_restarts<=16&&
        s.restart_levels>=1&&s.restart_levels<=16&&std::isfinite(s.restart_step)&&s.restart_step>0&&s.restart_step<=1e-2;
}
// Temporary max-component-normalized rows avoid sensitivity to multiplying an equation by a
// constant. Raw document values remain untouched. Stress scale is fixed from
// the supplied parent/material scales, not adjusted to make a trial pass.
inline RecordedResult replay_recorded(int model,const State& initial,const State& parameters,
                                      const RecordedPath& path,const RecordedSettings& settings={}){
    RecordedResult result;result.state=initial;result.strain=path.initial_strain;
    auto invalid=[&](const std::string& message){result.message=message;return result;};
    if(!valid_recorded_settings(settings))return invalid("invalid recorded-path settings");
    if(model<0||model>=int(models().size()))return invalid("unknown recorded-path model");
    if(models()[model].physical_time||initial_state(model).size()<6||models()[model].fields.empty()||
       models()[model].fields[0].name!="sigma"||models()[model].fields[0].offset!=0||models()[model].fields[0].size!=6)
        return invalid("recorded incremental replay requires an untimed stress-first model");
    if(initial.size()!=initial_state(model).size()||!valid_parameters(model,parameters)||!domain(model,initial,parameters,true))
        return invalid("invalid recorded-path parameters or initial state");
    for(double x:path.initial_strain.v)if(!std::isfinite(x))return invalid("nonfinite initial recorded strain");
    if(path.knots.size()<2||path.knots.size()>5001)return invalid("recorded path requires 2 to 5001 knots");
    std::array<Sym<double>,6> rows;std::array<double,6> lengths;
    bool all_strain=true;
    for(int i=0;i<6;++i){
        const auto& c=path.controls[i];all_strain=all_strain&&!c.stress;
        double maximum=0;for(double x:c.coefficients.v){if(!std::isfinite(x))return invalid("nonfinite control coefficient");maximum=std::max(maximum,std::abs(x));}
        if(maximum==0)return invalid("zero recorded control row");
        lengths[i]=maximum;
        for(int j=0;j<6;++j)rows[i].v[j]=c.coefficients.v[j]/maximum;
    }
    if(all_strain){
        std::vector<State> a(6,State(6));State unused;
        for(int i=0;i<6;++i)for(int j=0;j<6;++j)a[i][j]=rows[i].v[j];
        if(!solve_linear(a,State(6,0.),unused))return invalid("dependent all-strain control rows");
    }
    for(size_t k=0;k<path.knots.size();++k){
        const auto& knot=path.knots[k];
        if(!std::isfinite(knot.coordinate)||(k&&!(knot.coordinate>path.knots[k-1].coordinate)))
            return invalid("recorded coordinates must be finite and strictly increasing in input order");
        for(int i=0;i<6;++i)if(!std::isfinite(knot.targets[i])||!std::isfinite(knot.targets[i]/lengths[i]))
            return invalid("nonfinite recorded target or normalized target");
    }
    const auto material_scales=model_scales(model,parameters);
    double stress_scale=1.;
    for(int i=0;i<6;++i){
        if(!std::isfinite(material_scales[i])||material_scales[i]<=0)return invalid("invalid stress scales");
        stress_scale=std::max(stress_scale,std::max(std::abs(initial[i]),material_scales[i]));
    }
    auto residual=[&](const State& state,const Sym<double>& strain,const RecordedKnot& knot,State& r){
        r.resize(6);
        const auto stress=tensor_from(state,0);
        for(int i=0;i<6;++i)r[i]=(dot(rows[i],path.controls[i].stress?stress:strain)-knot.targets[i]/lengths[i])/
            (path.controls[i].stress?stress_scale:1.);
        return finite(r);
    };
    auto error=[](const State& r){double e=0;for(double x:r)e=std::max(e,std::abs(x));return e;};
    State first;
    if(!residual(initial,path.initial_strain,path.knots[0],first)||error(first)>settings.control_tolerance)
        return invalid("first recorded targets do not match supplied initial state and strain; preparation is explicit");
    RecordedPoint origin;origin.coordinate=path.knots[0].coordinate;origin.state=initial;origin.strain=path.initial_strain;
    origin.control_error=error(first);result.points.push_back(origin);
    auto account=[&](const Advance& a){result.attempted_substeps+=a.diagnostics.substeps;};
    auto material=[&](const State& parent,const Sym<double>& increment,Advance& trial){
        if(result.material_trials>=settings.max_material_trials)return false;
        ++result.material_trials;trial=integrate(model,parent,increment,parameters,settings.material);account(trial);return trial.ok;
    };
    for(size_t k=1;k<path.knots.size();++k){
        const auto parent=result.points.back();const auto& knot=path.knots[k];
        auto fail=[&](const std::string& message){result.failed_knot=int(k);result.message=message+"; last committed knot retained";return result;};
        Sym<double> increment;Advance accepted;State r;
        bool converged=false;double control_error=0;
        if(!residual(parent.state,parent.strain,knot,r))return fail("nonfinite control residual");
        if(knot.targets==path.knots[k-1].targets&&error(r)<=settings.control_tolerance){
            // A repeated target is a recorded observation, not a new zero update
            // or a hidden history/preparation event. Preserve every state bit.
            accepted.ok=true;accepted.state=parent.state;converged=true;control_error=error(r);
        }else if(all_strain){
            std::vector<State> a(6,State(6));State rhs(6),solution;
            for(int i=0;i<6;++i){rhs[i]=-r[i];for(int j=0;j<6;++j)a[i][j]=rows[i].v[j];}
            if(!solve_linear(a,rhs,solution))return fail("singular strain controls");
            for(int j=0;j<6;++j)increment.v[j]=solution[j];
            if(!material(parent.state,increment,accepted))return fail("material update failed or trial budget exhausted");
            if(!residual(accepted.state,parent.strain+increment,knot,r)||error(r)>settings.control_tolerance)
                return fail("strain target precision failure");
            control_error=error(r);converged=true;
        }else{
            // Impose known strain projections before evaluating the material.
            // A line search must not attenuate the imposed loading along with
            // its unknown stress-control correction. Free coordinates start at
            // zero; rectangular pivot elimination avoids normal equations.
            std::vector<State> constraints;State rhs;std::vector<int> pivots;
            for(int i=0;i<6;++i)if(!path.controls[i].stress){
                constraints.emplace_back(rows[i].v.begin(),rows[i].v.end());rhs.push_back(-r[i]);
            }
            int rank=0;const int count=int(constraints.size());
            for(int column=0;column<6&&rank<count;++column){
                int pivot=rank;
                for(int i=rank+1;i<count;++i)if(std::abs(constraints[i][column])>std::abs(constraints[pivot][column]))pivot=i;
                if(std::abs(constraints[pivot][column])<1e-14)continue;
                std::swap(constraints[rank],constraints[pivot]);std::swap(rhs[rank],rhs[pivot]);
                const double diagonal=constraints[rank][column];
                for(double& x:constraints[rank])x/=diagonal;rhs[rank]/=diagonal;
                for(int i=0;i<count;++i)if(i!=rank){
                    const double factor=constraints[i][column];
                    for(int j=0;j<6;++j)constraints[i][j]-=factor*constraints[rank][j];rhs[i]-=factor*rhs[rank];
                }
                pivots.push_back(column);++rank;
            }
            if(rank!=count)return fail("dependent prescribed strain controls");
            for(int i=0;i<count;++i)increment.v[pivots[i]]=rhs[i];
            if(!finite(rhs))return fail("nonfinite prescribed strain solution");
            const auto particular=increment;
            std::vector<Sym<double>> directions;
            for(int column=0;column<6;++column){
                if(std::find(pivots.begin(),pivots.end(),column)!=pivots.end())continue;
                Sym<double> direction;direction.v[column]=1.;double scale=1.;
                for(int i=0;i<count;++i){direction.v[pivots[i]]=-constraints[i][column];scale=std::max(scale,std::abs(direction.v[pivots[i]]));}
                if(!std::isfinite(scale))return fail("nonfinite free control direction");
                for(double& x:direction.v)x/=scale;
                directions.push_back(direction);
            }
            std::vector<int> stress_rows;for(int i=0;i<6;++i)if(path.controls[i].stress)stress_rows.push_back(i);
            const int unknowns=int(directions.size());State free_values(unknowns,0.);
            auto construct=[&](const State& values){
                auto candidate=particular;
                for(int j=0;j<unknowns;++j)candidate=candidate+values[j]*directions[j];
                return candidate;
            };
            int restarts=0;
            // Bounded opt-in globalization for a locally singular stress map.
            // Search only the feasible nullspace and never advance the parent.
            auto restart=[&](double current_error){
                if(restarts>=settings.max_restarts)return false;
                ++restarts;++result.restart_searches;
                std::vector<State> offsets;
                if(unknowns>1){
                    Sym<double> sum;for(const auto& d:directions)sum=sum+d;
                    double scale=0;for(double x:sum.v)scale=std::max(scale,std::abs(x));
                    if(scale>0&&std::isfinite(scale))offsets.push_back(State(unknowns,1./scale));
                }
                for(int j=0;j<unknowns;++j){State offset(unknowns,0.);offset[j]=1.;offsets.push_back(offset);}
                for(int level=0;level<settings.restart_levels;++level){
                    const double radius=std::ldexp(settings.restart_step,level);
                    double best_error=current_error;State best_values;Sym<double> best_increment;
                    for(const auto& offset:offsets)for(double sign:{1.,-1.}){
                        auto values=free_values;for(int j=0;j<unknowns;++j)values[j]+=sign*radius*offset[j];
                        const auto candidate=construct(values);
                        bool valid=true;for(double x:candidate.v)valid=valid&&std::isfinite(x);
                        if(!valid||candidate.v==increment.v)continue;
                        Advance trial;const int before=result.material_trials;
                        const bool ok=material(parent.state,candidate,trial);
                        result.restart_trials+=result.material_trials-before;
                        if(ok){
                            State trial_r;
                            if(residual(trial.state,parent.strain+candidate,knot,trial_r)){
                                const double next_error=error(trial_r);
                                if(next_error<=settings.control_tolerance){
                                    increment=candidate;free_values=values;accepted=trial;control_error=next_error;converged=true;
                                    result.last_control_error=next_error;result.last_trial_increment=candidate;
                                    ++result.accepted_restarts;return true;
                                }
                                // Avoid selecting roundoff noise on a flat branch.
                                if(next_error<current_error*(1.-1e-8)&&next_error<best_error){
                                    best_error=next_error;best_values=values;best_increment=candidate;
                                }
                            }
                        }
                        if(result.material_trials>=settings.max_material_trials)break;
                    }
                    if(!best_values.empty()){
                        increment=best_increment;free_values=best_values;
                        result.last_control_error=best_error;result.last_trial_increment=increment;
                        ++result.accepted_restarts;return true;
                    }
                    if(result.material_trials>=settings.max_material_trials)return false;
                }
                return false;
            };
            for(int iteration=0;iteration<settings.max_iterations;++iteration){
                if(result.material_trials>=settings.max_material_trials)return fail("material trial budget exhausted");
                ++result.material_trials;
                auto linearized=linearize_update(model,parent.state,increment,parameters,settings.material);
                auto trial=linearized.advance;account(trial);
                if(!trial.ok)return fail("material trial failed");
                if(!residual(trial.state,parent.strain+increment,knot,r))return fail("nonfinite control residual");
                const double current_error=error(r);
                result.last_control_error=current_error;result.last_trial_increment=increment;
                if(current_error<=settings.control_tolerance){accepted=trial;control_error=current_error;converged=true;break;}
                // Stress derivatives only along the nullspace of prescribed
                // strains. Numerical probes also obey every strain constraint.
                std::vector<State> jacobian(unknowns,State(unknowns));
                for(int j=0;j<unknowns;++j){
                    State stress_derivative(6,0.);
                    if(linearized.tangent_ok){
                        for(int l=0;l<6;++l)for(int component=0;component<6;++component)
                            stress_derivative[l]+=linearized.state_tangent[l][component]*directions[j].v[component];
                    }else{
                        const double h=settings.finite_difference_step*std::max(1.,std::abs(free_values[j]));
                        auto values=free_values;values[j]+=h;Advance shifted;double signed_h=h;
                        auto probe=[&](){
                            const int before=result.material_trials;
                            const bool ok=material(parent.state,construct(values),shifted);
                            result.finite_difference_probes+=result.material_trials-before;
                            return ok;
                        };
                        if(!probe()){
                            values=free_values;values[j]-=h;signed_h=-h;
                            if(!probe())return fail("control derivative trial failed or trial budget exhausted");
                        }
                        for(int l=0;l<6;++l)stress_derivative[l]=(shifted.state[l]-trial.state[l])/signed_h;
                    }
                    for(int i=0;i<unknowns;++i)for(int l=0;l<6;++l)
                        jacobian[i][j]+=rows[stress_rows[i]].v[l]*stress_derivative[l]/stress_scale;
                }
                State load(unknowns),delta;
                for(int i=0;i<unknowns;++i)load[i]=-r[stress_rows[i]];
                for(const auto& row:jacobian)if(!finite(row))return fail("nonfinite mixed-control Jacobian");
                if(!solve_linear(jacobian,load,delta)){
                    if(restart(current_error)){if(converged)break;continue;}
                    return fail(settings.max_restarts?"singular mixed-control system; bounded restart failed or trial budget exhausted":"singular mixed-control system");
                }
                bool improved=false;
                for(int backtrack=0;backtrack<=settings.max_backtracks;++backtrack){
                    const double alpha=std::ldexp(1.,-backtrack);auto values=free_values;
                    for(int j=0;j<unknowns;++j)values[j]+=alpha*delta[j];
                    const auto candidate=construct(values);
                    Advance next;if(!material(parent.state,candidate,next))continue;
                    State next_r;
                    if(residual(next.state,parent.strain+candidate,knot,next_r)&&error(next_r)<current_error){
                        increment=candidate;free_values=values;improved=true;
                        if(error(next_r)<=settings.control_tolerance){
                            accepted=next;control_error=error(next_r);converged=true;
                            result.last_control_error=control_error;result.last_trial_increment=increment;
                        }
                        break;
                    }
                }
                if(converged)break;
                if(!improved)return fail("mixed-control line search failed or trial budget exhausted");
            }
        }
        if(!converged)return fail("mixed-control iteration limit");
        RecordedPoint point;point.coordinate=knot.coordinate;point.state=accepted.state;point.strain=parent.strain+increment;
        point.diagnostics=accepted.diagnostics;point.control_error=control_error;
        result.points.push_back(point);result.state=point.state;result.strain=point.strain;
    }
    result.ok=true;return result;
}
}
