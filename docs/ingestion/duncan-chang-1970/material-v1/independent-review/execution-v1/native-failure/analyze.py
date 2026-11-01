"""Source-only root interval analysis of retained failed calls; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as Q,localcontext
import json,runpy,hashlib,struct
B=Path(__file__).resolve().parents[3];E=B/'execution-v1'
ref=runpy.run_path(str(B/'reference.py'));q=ref['q']
def main():
    requests=json.loads((E/'requests.json').read_text());obs=json.loads((E/'native-results.json').read_text());rows=[]
    with localcontext()as ctx:
        ctx.prec=160
        for path,raw in zip(requests['paths'],obs['paths']):
            if not path['id'].startswith('loose-max-crossing-'):continue
            failures=[(i,c)for i,c in enumerate(raw['calls'])if not json.loads(c['stdout'])['ok']];assert len(failures)==1
            index,call=failures[0];out=json.loads(call['stdout'],parse_int=float);zn=list(map(float,call['args'][2].split(',')));de=list(map(float,call['args'][3].split(',')));p=path['parameters']
            assert [struct.pack('>d',x)for x in zn]==[struct.pack('>d',x)for x in out['state']]
            nu=q(p['nu']);tr=sum(map(q,de[:3]));lam=nu/((1+nu)*(1-2*nu));shape=[q(de[i])/(1+nu)+lam*tr for i in range(3)]
            k=shape[0]-shape[1];br=shape[1];old=q(zn[0])-q(zn[1]);conf=q(zn[1]);history=q(zn[6]);distance=history-old;assert k>0 and distance>0
            sp=ref['sin'](q(p['phi']));alpha=2*sp/(1-sp);A=q(p['K'])*q(p['pa']);U=q(p['Kur'])*q(p['pa']);n=q(p['n']);pa=q(p['pa']);rf=q(p['Rf'])
            assert p['c_cohesion']==0 and n>0 and zn[1]==zn[2]
            assert k*conf-old*br>0 # S(E) strictly increases on positive-confinement interval
            def cbar(mod):return conf+mod*br/2
            def primary(mod):
                c=cbar(mod);S=(old+mod*k/2)/(alpha*c)
                return A*(c/pa)**n*(1-rf*S)**2
            boundary=distance/k
            strength=2*(alpha*conf-old)/(k-alpha*br)
            minc=min(conf,cbar(boundary));min_unload=U*(minc/pa)**n
            assert min_unload>boundary # every E below boundary misses unloading equation
            maxc=max(cbar(boundary),cbar(strength));s_boundary=(old+boundary*k/2)/(alpha*cbar(boundary));assert minc>0 and 0<s_boundary<1
            max_primary=A*(maxc/pa)**n*(1-rf*s_boundary)**2
            assert max_primary<boundary # every valid primary E exceeds its modulus
            assert old+q(p['E_failure'])*k<history # numerical failure modulus cannot rescue
            Eur=U*(conf/pa)**n;Ei=A*(conf/pa)**n;F=alpha*conf
            lo=distance/Eur;hi=distance/(Ei*(1-rf*(old+history)/(2*F))**2)
            fractions=sum(q(x)for x in out['diagnostics']['increment_fractions']);remaining=distance-Eur*k*fractions
            # Construct a valid source two-piece subdivision; no production algorithm.
            delta=distance/100;advance=distance-delta;c1=conf+br*advance/k
            E1=U*(((conf+c1)/2)/pa)**n;fraction=advance/(E1*k);assert 0<fraction<1
            current1=old+advance;kk=(1-fraction)*k;bb=(1-fraction)*br
            lower=delta/kk;upper=2*(alpha*c1-current1)/(kk-alpha*bb)
            def h2(mod):
                c=c1+mod*bb/2;S=(current1+mod*kk/2)/(alpha*c)
                return mod-A*(c/pa)**n*(1-rf*S)**2
            assert h2(lower)<0<h2(upper)
            for _ in range(530):
                mid=(lower+upper)/2
                if h2(mid)>0:upper=mid
                else:lower=mid
            root=(lower+upper)/2;finalD=current1+root*kk;assert finalD>history
            rows.append({'id':path['id'],'failed_call_index':index,'incoming_D':str(old),'h':str(history),'wire_axial_strain':str(q(de[0])),'fixed_confinement_gap_min':str(lo),'fixed_confinement_gap_max':str(hi),'actual_wire_boundary_required_modulus':str(boundary),'actual_wire_unload_modulus_lower_bound':str(min_unload),'actual_wire_primary_modulus_upper_bound':str(max_primary),'wire_lateral_shape':str(br),'tentative_accepted_substeps':out['diagnostics']['substeps'],'rejected':out['diagnostics']['rejected'],'accepted_fraction_sum':str(fractions),'estimated_remaining_D_to_history_after_tentative_unloading':str(remaining),'constructive_two_piece_first_fraction':str(fraction),'constructive_final_D':str(finalD),'actual_external_state_exactly_rolled_back':True,'conclusion':'genuine no-unsplit-root gap; full path has a valid alternative subdivision; depth-limited dyadic continuation failed'})
    return {'identity':'independent-loose-max-native-source-failure-v1','pass_root_analysis':True,'rows':rows,'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [E/'requests.json',E/'native-results.json',E/'native-assessment.json',E/'frozen/cpp/include/atlas/solver.hpp',B/'reference.py']},'compiled_calls':0,'material_updates':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
