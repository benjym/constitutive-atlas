"""Prospectively identified hydrostatic zero-pressure event diagnostic."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
model=json.loads((HERE/'model.json').read_text());policy=json.loads((HERE/'hydro-domain-policy.json').read_text())
exe=ROOT/'.local/lade-duncan-candidate-v2/native-build/atlas_lade_gap_candidate'
rows=[]
for label,over in [('dense',{}),('loose',dict(k1=58,ft=33,A=.39,rf=.970,M=6.80e-4,l=1.17,Kur=1600,n=.86))]:
    p={n:v['default'] for n,v in model['parameters'].items()};p.update(over);p0=policy['p0_Pa'];ec=-(p0/p['pa'])**(1-p['n'])/((1-p['n'])*p['Kur'])
    for frac in policy['total_strain_as_fraction_of_negative_critical_strain']:
        for count in policy['uniform_external_steps']:
            state=[p0]*3+[0]*3+[p['ft']-27,0];requests=[];failed=None
            for i in range(count):
                parent=state.copy();de=[ec*frac/count]*3+[0]*3
                command=[str(exe),'--model',model['id'],'--mode','integrate','--parameters',','.join(str(p[n]) for n in model['parameters']),'--initial',','.join(map(str,parent)),'--strain',','.join(map(str,de))]
                proc=subprocess.run(command,text=True,capture_output=True,timeout=120);r=json.loads(proc.stdout);requests.append({'command':command,'returncode':proc.returncode,'response':r})
                if not r.get('ok'):
                    failed={'external_step':i+1,'rollback_exact':r.get('state')==parent};break
                state=r['state']
            ref=p0*(1-frac)**(1/(1-p['n'])) if frac<1 else None
            rows.append({'set':label,'critical_per_axis_strain':ec,'fraction':frac,'steps':count,'complete':failed is None,'failed':failed,'final_state':state,'source_final_pressure_Pa':ref,'relative_pressure_error':abs(state[0]-ref)/ref if ref else None,'domain_event_fidelity_failure':frac>1 and failed is None,'requests':requests})
report={'id':policy['id'],'model_sha256':hashlib.sha256((HERE/'model.json').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((HERE/'hydro-domain-policy.json').read_bytes()).hexdigest(),'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'cases':rows,'source_domain_gate_passed':not any(x['domain_event_fidelity_failure'] for x in rows),'limitations':'Diagnostic of hydrostatic source-domain event. No full candidate qualification; original studies remain unchanged.'}
(HERE/'hydro-domain-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:([{n:v for n,v in row.items() if n!='requests'} for row in rows] if k=='cases' else v) for k,v in report.items()},indent=2))
