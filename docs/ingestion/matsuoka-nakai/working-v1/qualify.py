"""Serial C-ABI observations and frozen independent finite-path gates."""
import argparse
import json
import hashlib
import subprocess
from pathlib import Path
import numpy as np
from reference import initial,augmented_state,rk4,terms,matrix,DEFAULT
P=Path(__file__).resolve().parent
ID='nakai-hinokio-2004-clay-appendix-v-be'
SETTINGS='2e-10,1e-6,45,14,20000,11'

def scale_error(a,b):
    v=np.array(a[:8])-np.array(b[:8]);v[:6]/=DEFAULT['p_ref'];return max(abs(v))

class Transport:
    def __init__(self,path):
        self.proc=subprocess.Popen([str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        self.raw=(P/'native-responses.jsonl').open('w');self.count=0
    def call(self,parent,strain,settings=SETTINGS):
        csv=lambda x:','.join(repr(float(v)) for v in x)
        fields=[ID,'',csv(parent),csv(strain),settings]
        line='\t'.join(fields)
        self.proc.stdin.write(line+'\n');self.proc.stdin.flush()
        response=self.proc.stdout.readline();assert response,'native transport died'
        result=json.loads(response);self.count+=1
        self.raw.write(json.dumps({'request':fields,'response':result})+'\n');self.raw.flush()
        return result
    def close(self):
        self.proc.stdin.close();assert self.proc.wait(timeout=20)==0;self.raw.close()

def main(binary):
    if (P/'native-responses.jsonl.gz').exists():raise RuntimeError('Retained study exists; copy scripts/inputs into a fresh study directory before recapturing.')
    report={'status':'running','paths':[],'failures':[]};tr=Transport(binary)
    def gate(ok,name,**extra):
        if not ok:report['failures'].append(dict(gate=name,**extra))
    try:
        z0=augmented_state(initial())
        hold=tr.call(z0,[0.]*6);gate(hold['ok'] and hold['state']==z0,'zero_hold')
        inc=[1e-5]*3+[0.]*3
        a=tr.call(z0,inc);b=tr.call(z0,inc);gate(a['ok'] and a==b,'repeated_trial_exact')
        invalid=z0.copy();invalid[0]=-98000.
        bad=tr.call(invalid,inc);gate(not bad['ok'] and bad.get('state',invalid)==invalid,'invalid_initial_rollback')
        invalid=z0.copy();invalid[8]=.8
        bad=tr.call(invalid,inc);gate(not bad['ok'] and bad.get('state',invalid)==invalid,'inconsistent_auxiliary_rejection')
        bad=tr.call(z0,[.01,0.,0.,0.,0.,0.],'2e-10,1e-6,1,0,1,0')
        gate(not bad['ok'] and bad.get('state')==z0,'budget_failure_rollback')
        recovery=tr.call(z0,inc);gate(recovery==a,'same_process_recovery')
        cases=[('hydro_nc',[.001,.001,.001,0.,0.,0.],initial()),
               ('hydro_unload',[-.0002,-.0002,-.0002,0.,0.,0.],initial()),
               ('triaxial_compression',[.003,-.0015,-.0015,0.,0.,0.],initial(rho=.03,e=.8)),
               ('triaxial_extension',[-.002,.001,.001,0.,0.,0.],initial(rho=.03,e=.8)),
               ('simple_shear',[0.,0.,0.,.003,0.,0.],initial(rho=.03,e=.8)),
               ('general_tensor',[.001,-.0003,-.0004,.001,.0005,-.0002],initial(rho=.03,e=.8))]
        for name,total,parent in cases:
            print('reference',name,flush=True)
            refs={str(n):list(rk4(parent,total,n)) for n in (256,512,1024)}
            refdiff=np.array(refs['1024'])-np.array(refs['512'])
            gate(max(abs(refdiff[:6]))/98000<=2e-6 and max(abs(refdiff[6:]))<=2e-7,'reference_refinement',path=name,difference=list(refdiff))
            path={'name':name,'total_strain':total,'initial':parent,'references':refs,'native_grids':[]}
            errors=[]
            for n in (32,64,128):
                current=augmented_state(parent);trajectory=[current];failure=None
                for step in range(n):
                    out=tr.call(current,[x/n for x in total])
                    if not out['ok']:failure={'step':step,'response':out};break
                    current=out['state'];trajectory.append(current)
                    eig=np.linalg.eigvalsh(matrix(current[:6]));at=matrix(current[8:14]);S=matrix(current[:6])/98000
                    inv=np.linalg.inv(S);target=inv/np.trace(inv)
                    aux=float(np.max(abs(at@at-target)))
                    gate(min(eig)>0 and min(np.linalg.eigvalsh(at))>0 and aux<=1e-8,'state_consistency',path=name,grid=n,step=step,auxiliary_error=aux)
                err=float(scale_error(current,refs['1024']))
                errors.append(err)
                path['native_grids'].append(dict(steps=n,trajectory=trajectory,failure=failure,scaled_endpoint_error=err))
                gate(failure is None,'path_success',path=name,grid=n)
                print('native',name,n,'error',err,'failed',failure is not None,flush=True)
            fine=path['native_grids'][-1]['trajectory'][-1];diff=np.array(fine[:8])-np.array(refs['1024'])
            gate(max(abs(diff[:6]))/98000<=3e-3 and max(abs(diff[6:]))<=3e-4,'finest_reference_accuracy',path=name,error=list(diff))
            gate(errors[-1]<errors[0] or errors[-1]<=1e-7,'native_refinement',path=name,errors=errors)
            if name.startswith('hydro'):
                c=DEFAULT['Cc'] if name=='hydro_nc' else DEFAULT['Ce']
                exact=98000*np.exp(sum(total[:3])/c)
                gate(abs(fine[0]-exact)/98000<=3e-3 and abs(fine[7]-(parent[7]-(1+DEFAULT['e_ref'])*sum(total[:3])))<=1e-10,'hydro_analytical',path=name,expected_pressure=float(exact))
            report['paths'].append(path)
        # Own-state hydro loading, unloading, reloading; no history reconstruction.
        current=z0;cycle=[]
        for amount in [1e-5]*12+[-1e-5]*8+[1e-5]*12:
            out=tr.call(current,[amount]*3+[0.]*3);cycle.append(out)
            if not out['ok']:break
            current=out['state']
        gate(len(cycle)==32 and all(x['ok'] for x in cycle),'continuous_unload_reload')
        report['hydro_cycle']=cycle
    finally:
        tr.close();report['native_calls']=tr.count;report['status']='pass' if not report['failures'] else 'failed'
        report['binary_sha256']=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
        (P/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['paths','hydro_cycle']},indent=2))
    return not report['failures']

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('binary');args=ap.parse_args()
    raise SystemExit(0 if main(args.binary) else 1)
