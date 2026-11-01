"""Run only the predeclared bounded native triaxial refinement study."""
from pathlib import Path
import json,hashlib,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EXE=ROOT/'.local/lade-derivative-tail-v1/native-build/atlas_lade_domain_candidate'
RAW=ROOT/'.local/lade-derivative-tail-v1/native-requests';RAW.mkdir(exist_ok=True)
policy=json.loads((HERE/'triaxial-policy.json').read_text());model=json.loads((HERE/'model.json').read_text());reference=json.loads((HERE/'triaxial-reference-results.json').read_text());records=[]
loose={'k1':58,'ft':33,'A':.39,'rf':.970,'M':6.80e-4,'l':1.17,'Kur':1600,'n':.86}
for row in reference['cases']:
    name=row['set'];ref=row['reference'];params={n:v['default'] for n,v in model['parameters'].items()}
    if name=='loose':params.update(loose)
    for steps in policy['native_refinement_steps']:
        cmd=[str(EXE),'--model',model['id'],'--parameters',','.join(str(params[n]) for n in model['parameters']),'--initial',','.join(map(str,[60000,60000,60000,0,0,0,params['ft']-27,0])),'--protocol','1','--target',str(ref['axial_strain']),'--steps',str(steps),'--response-contract','stress-scope-0.1']
        settings=json.loads((HERE/'POLICY.json').read_text())['numerics']['default_study_settings'].copy()
        factor=(100/steps)**2;settings[0]*=factor;settings[6]*=factor
        cmd += ['--integration-settings',','.join(map(str,settings))]
        process=subprocess.run(cmd,text=True,capture_output=True,timeout=120);path=RAW/f'{name}-{ref["axial_strain"]}-{steps}.json';path.write_text(process.stdout)
        response=json.loads(process.stdout);record={'set':name,'target':ref['axial_strain'],'steps':steps,'command':cmd,'returncode':process.returncode,'ok':response.get('ok'),'message':response.get('message'),'raw_path':str(path.relative_to(ROOT)),'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        if response.get('ok'):
            point=response['points'][-1];stress=point['state'][0];radial=point['strain'][1];wp=point['state'][7]
            errors={'relative_axial_stress':abs(stress-ref['axial_stress'])/ref['axial_stress'],'absolute_radial_strain':abs(radial-ref['radial_strain']),'relative_work_using_1Pa_floor':abs(wp-ref['wp'])/max(1,abs(ref['wp']))}
            record.update(final=point,errors=errors,within_bounds=all(errors[n]<=bound for n,bound in policy['native_final_reference_bounds'].items()))
        records.append(record)
finals=[r for r in records if r['steps']==policy['native_refinement_steps'][-1]]
refinement=[]
for row in reference['cases']:
    case=[r for r in records if r['set']==row['set'] and r['target']==row['reference']['axial_strain']]
    smoothplastic=row['reference']['wp']>0
    decreasing=all(case[i+1].get('errors',{}).get('relative_axial_stress',float('inf'))<=case[i].get('errors',{}).get('relative_axial_stress',0) for i in range(len(case)-1)) if smoothplastic else True
    refinement.append({'set':row['set'],'target':row['reference']['axial_strain'],'smooth_plastic':smoothplastic,'stress_error_decreases':decreasing})
report={'scope':policy['scope'],'exe_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((HERE/'model.json').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((HERE/'triaxial-policy.json').read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256((HERE/'triaxial-reference-results.json').read_bytes()).hexdigest(),'requests':records,'refinement':refinement,'passed':all(r.get('ok') for r in records) and all(r.get('within_bounds') for r in finals) and all(r['stress_error_decreases'] for r in refinement),'limitations':'Bounded native monotonic triaxial study only; not E4 full qualification, no Wasm, review, atlas or browser claim'}
(HERE/'native-triaxial-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'requests':len(records),'final_errors':[{'set':r['set'],'target':r['target'],'ok':r['ok'],'errors':r.get('errors')} for r in finals],'refinement':refinement},indent=2))
raise SystemExit(0 if report['passed'] else 1)
