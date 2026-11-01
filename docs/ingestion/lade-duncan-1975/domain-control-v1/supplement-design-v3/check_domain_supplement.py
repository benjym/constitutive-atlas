"""Separate stricter domain coverage; never rewrites original study."""
from pathlib import Path
import hashlib,json,math,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
EXE=ROOT/'.local/lade-domain-control-v1/native-build/atlas_lade_domain_candidate'
MODEL=json.loads((HERE/'model.json').read_text());POLICY=json.loads((HERE/'POLICY.json').read_text())
RAW=ROOT/'.local/lade-domain-control-v1/native-supplement-requests';RAW.mkdir(exist_ok=True)
checks=[];requests=[]
def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
def get(cmd,key):return cmd[cmd.index(key)+1]
def numbers(cmd,key):return list(map(float,get(cmd,key).split(',')))
def invariants(s):
    scale=max(map(abs,s[:6]));v=[x/scale for x in s[:6]];x,y,z,a,b,c=v;a/=math.sqrt(2);b/=math.sqrt(2);c/=math.sqrt(2)
    det=x*y*z+2*a*b*c-x*b*b-y*c*c-z*a*a
    assert x>0 and x*y-a*a>0 and det>0
    return (x+y+z)**3/det

def audit(row,r,index):
    cmd=row['command'];p=dict(zip(MODEL['parameters'],numbers(cmd,'--parameters')));parent=numbers(cmd,'--initial');de=numbers(cmd,'--strain');s=r.get('state',[])
    valid=len(s)==8 and all(type(x) in (float,int) and math.isfinite(x) for x in s)
    check(f'{index}_finite',valid)
    if not valid:return
    try:f=invariants(s);spd=True
    except (AssertionError,ZeroDivisionError,ValueError):f=math.inf;spd=False
    check(f'{index}_elastic_invariants',spd and f<p['ft'] and abs(max(p['ft'],f+max(s[6],0))-p['ft'])<=1e-8*p['ft'] and s[7]==0,{'f':f})
    if not r.get('ok'):
        check(f'{index}_rollback',s==parent);return
    if de[0]>=0:return
    mean=sum(parent[:3])/3;B=[x/mean for x in parent[:6]]
    proportional=math.sqrt(sum((de[i]-de[0]*B[i]/B[0])**2 for i in range(6)))<=abs(de[0])*1e-10
    if not proportional:return
    # All study tensors have min/mean ratio1(hydro) or .9(rotated prescribed B).
    ratio=1 if max(parent[:3])-min(parent[:3])<=mean*1e-12 and max(map(abs,parent[3:6]))<=mean*1e-12 else .9
    ec=(mean/p['pa'])**(1-p['n'])/((1-p['n'])*p['Kur']*ratio**p['n']);frac=-de[0]/B[0]/ec
    check(f'{index}_before_event',frac<1,{'remaining_lifetime_fraction':frac})
    amp=sum(s[i]*parent[i] for i in range(6))/sum(x*x for x in parent[:6]);norm=math.hypot(*s[:6])
    err=math.hypot(*(s[i]-amp*parent[i] for i in range(6)))/norm
    check(f'{index}_proportional',err<=1e-8,err)
    if abs(frac-.5)<1e-10:
        ref=[x*(1-frac)**(1/(1-p['n'])) for x in parent[:6]];err=math.hypot(*(s[i]-ref[i] for i in range(6)))/math.hypot(*ref)
        check(f'{index}_half_source_accuracy',err<=.005,err)

def audit_prefix(rows,responses,label):
    previous=None;previous_command=None;root=None;total=0
    for i,(row,r) in enumerate(zip(rows,responses)):
        cmd=row['command'];parent=numbers(cmd,'--initial');de=numbers(cmd,'--strain');params=numbers(cmd,'--parameters')
        p=dict(zip(MODEL['parameters'],params));mean=sum(parent[:3])/3;B=[x/mean for x in parent[:6]]
        proportional=de[0]<0 and math.hypot(*(de[j]-de[0]*B[j]/B[0] for j in range(6)))<=abs(de[0])*1e-10
        signature=(params,de)
        if not proportional or not r.get('ok'):previous=None;previous_command=None;continue
        if previous!=parent or previous_command!=signature:root=parent.copy();total=0
        total+=-de[0]/B[0]
        rootmean=sum(root[:3])/3;hydro=max(root[:3])-min(root[:3])<=rootmean*1e-12 and max(map(abs,root[3:6]))<=rootmean*1e-12;ratio=1 if hydro else .9
        ec=(rootmean/p['pa'])**(1-p['n'])/((1-p['n'])*p['Kur']*ratio**p['n'])
        check(f'{label}_{i}_cumulative_before_event',total<ec,{'cumulative_fraction':total/ec})
        previous=r['state'];previous_command=signature

def call(cmd):
    proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120);r=json.loads(proc.stdout);raw=RAW/f'{len(requests):04}.json';raw.write_text(proc.stdout)
    requests.append(dict(command=cmd,returncode=proc.returncode,raw_path=str(raw.relative_to(ROOT)),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest()));return r

def main():
    original=json.loads((HERE/'native-domain-results.json').read_text())
    responses=[json.loads((ROOT/row['raw_path']).read_text()) for row in original['requests']]
    audit_prefix(original['requests'],responses,'original')
    for i,row in enumerate(original['requests']):
        r=json.loads((ROOT/row['raw_path']).read_text());audit(row,r,f'original_{i}')
        if r.get('ok'):continue
        cmd=row['command'];p=dict(zip(MODEL['parameters'],numbers(cmd,'--parameters')));parent=numbers(cmd,'--initial');mean=sum(parent[:3])/3;B=[x/mean for x in parent[:6]]
        hydro=max(parent[:3])-min(parent[:3])<=mean*1e-12 and max(map(abs,parent[3:6]))<=mean*1e-12;ratio=1 if hydro else .9
        ec=(mean/p['pa'])**(1-p['n'])/((1-p['n'])*p['Kur']*ratio**p['n'])
        de=[-.001*ec*x for x in B];direct=cmd.copy();direct[direct.index('--strain')+1]=','.join(map(str,de));retry=direct.copy();retry[retry.index('--initial')+1]=','.join(map(str,r['state']))
        a=call(direct);b=call(retry);audit(requests[-2],a,f'recovery_{i}_direct');audit(requests[-1],b,f'recovery_{i}_retry')
        check(f'{i}_recovery',a.get('ok') and b.get('ok') and a['state']==b['state'])
    report=dict(id='lade1975-domain-supplement-native-v1',checks=checks,requests=requests,passed=all(c['passed'] for c in checks),bindings={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['model.json','POLICY.json','SUPPLEMENT_POLICY.json','check_domain_supplement.py','native-domain-results.json']})
    (HERE/'native-supplement-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],checks=len(checks),requests=len(requests),failures=[c for c in checks if not c['passed']]),indent=2));return report['passed']
if __name__=='__main__':raise SystemExit(0 if main() else 1)
