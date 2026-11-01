"""Read-only published fixture/source identity audit; no compiled calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,subprocess,difflib,math
D=Path(__file__).resolve().parent;C=D.parent;ROOT=C.parents[2]
A=C/'native-admissible-fixture-implementation-v3';V2=C/'native-admissible-fixture-implementation-v2';V1=C/'native-admissible-fixture-implementation-v1';R2=C/'native-admissible-fixture-implementation-review-v2';R1=C/'native-admissible-fixture-implementation-review-v1'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):checks.append({'id':n,'passed':bool(v)});assert v,n
pins={A:'8474f748278c1f44a6be33360826e295c0a3007ecebf44bb190f5c41358a32a5',V2:'9390abd41a29a54930a0eef9277fda0ad5b7992be3c17786f2e2aaec3f8b3ad3',V1:'a80f24bfd03f0d8717fc492449f77fb431de0e5812d7ffe94580c1071211cf3f',R2:'70a2fdf8fc8aa23b0b6bbe404d4ef0e0e69ca12690a5da771fde81fc67e74264',R1:'0a657dadd7d4d2c09f2e522101dc367b9771136b164d4d417669b9f40125faae'}
for folder,h in pins.items():
 ck('manifest/'+folder.name,sha(folder/'manifest.json')==h)
 receipt=load(folder/'manifest.json');files=receipt.get('files',receipt)
 ck('all immutable file bytes/'+folder.name,all(sha(folder/n)==v for n,v in files.items()))
f=load(A/'source-freeze.json');f2=load(V2/'source-freeze.json');S=Path(f['source_directory']);S2=Path(f2['source_directory'])
ck('new freeze exact',sha(A/'source-freeze.json')=='2cd561c853342b1f08b867a8ea2681e9ac9784f1d532746fd3cad73bbda131b3')
for folder,r in [(S,f),(S2,f2)]:
 ck('exact582 inventory/'+str(folder),len(r['source_files'])==582 and sorted(r['source_files'])==sorted(str(p.relative_to(folder))for p in folder.rglob('*')if p.is_file()))
 ck('all582 bytes/'+str(folder),all(sha(folder/n)==h for n,h in r['source_files'].items()))
 ck('no caches or symlinks/'+str(folder),not any(p.is_symlink()or '__pycache__'in p.parts or p.suffix in ['.pyc','.pyo']for p in folder.rglob('*')))
ck('identical path sets',f['source_files'].keys()==f2['source_files'].keys())
ck('only solver test changed',[n for n in f['source_files']if f['source_files'][n]!=f2['source_files'][n]]==['tests/test_solver.cpp'])
ck('new isolated/public test exact',sha(S/'tests/test_solver.cpp')==sha(A/'test_solver.cpp')=='1b4555f246d6b572b8f653e5ca771c37177ee48883e2466fda96dc7665d85623')
commit='37d70660e3561c342bb114716c233a3d06651bcb'
published=subprocess.check_output(['git','show',commit+':tests/test_solver.cpp'],cwd=ROOT)
ck('published snapshot verified from Git object',published==(A/'published37d-test_solver.cpp').read_bytes()and hashlib.sha256(published).hexdigest()=='9e5469b1970c68190be8850a3579bacfc1aa4920b6b659d2c0365fcbc5e1df6c')
# Independently specify the exact published block, not the author's receipt value.
block='''            if(atlas::models()[m].id=="ramberg-osgood-ansys242"){
                // Independently derived consistent source-compliance fixture.
                const double eps[]={0.0018750073153125002,0.0014583260180208333,0.0016666666666666668,4.166812972916667e-05,0.,0.};
                for(int j=0;j<6;++j)z[6+j]=eps[j];
                zr=z;atlas::put_tensor(zr,6,rotate(atlas::tensor_from(z,6)));
            }
'''
v3=(A/'test_solver.cpp').read_text();v2=(V2/'test_solver.cpp').read_text();pub=published.decode()
ck('one exact published six-line block',len(block.splitlines())==6 and pub.count(block)==v3.count(block)==1 and block==f['exact_published_block'])
ck('remove sole block recovers accepted v2',v3.replace(block,'',1)==v2)
ck('published minus block exact original582 fixture',pub.replace(block,'',1)==(V1/'original_test_solver.cpp').read_text())
ops=[x for x in difflib.SequenceMatcher(None,v2.splitlines(True),v3.splitlines(True),autojunk=False).get_opcodes()if x[0]!='equal']
ck('exact sole6line insertion no replacement',len(ops)==1 and ops[0][0]=='insert'and ops[0][4]-ops[0][3]==6)
anchor='            atlas::Sym<double>de;de.v={.0001,-.00002,.00001,.00003,.00001,-.00001};auto zr=z;\n'
nextline='            atlas::put_tensor(zr,0,rotate(atlas::tensor_from(z,0)));\n'
ck('published same semantic insertion location',anchor+block+nextline in pub and anchor+block+nextline in v3)
ck('all MD instructions/helper/selectors/labels exact',v3.replace(block,'')==v2 and v3[:v3.index('        // A fixed 90-degree')]==v2[:v2.index('        // A fixed 90-degree')])
ck('all25 original assertions preserved',all(line in v3 for line in (V1/'original_test_solver.cpp').read_text().splitlines()if 'require('in line))
policy=json.loads(subprocess.check_output(['git','show',commit+':catalogue/laboratory-package-policy.json'],cwd=ROOT))
ck('published15 source definitions preserved',len(policy['models'])==15 and all(sha(S/'models'/(n+'.json'))==h for n,h in policy['models'].items()))
# Independent source-compliance calculation for the exact restored parent.
m=load(S/'models/ramberg-osgood-ansys242.json');p={k:v['default']for k,v in m['parameters'].items()}
sigma=[105000.,95000.,100000.,1000.,0.,0.];pr=sum(sigma[:3])/3;dev=[x-(pr if i<3 else 0)for i,x in enumerate(sigma)]
q2=1.5*sum(x*x for x in dev)/p['sigma0']**2
factor=q2**((p['n']-1)/2)
eps=[((1+p['nu']+1.5*p['alpha']*factor)*x+((1-2*p['nu'])*pr if i<3 else 0))/p['E']for i,x in enumerate(dev)]
frozen=[.0018750073153125002,.0014583260180208333,.0016666666666666668,4.166812972916667e-05,0.,0.]
err=math.sqrt(sum((p['E']*(x-y))**2 for x,y in zip(eps,frozen)))
ck('restored eps satisfies published source compliance',err<1e-8*p['sigma0']and max(abs(x-y)for x,y in zip(eps,frozen))<1e-17)
ck('Ramberg-only scope and complete strain rotation','if(atlas::models()[m].id=="ramberg-osgood-ansys242")'in block and 'for(int j=0;j<6;++j)z[6+j]=eps[j]'in block and 'zr=z;atlas::put_tensor(zr,6,rotate(atlas::tensor_from(z,6)))'in block)
ck('prior review dispositions retained',load(R1/'manifest.json')['decision']=='BLOCKED'and load(R2/'manifest.json')['blocking_findings']==[]and load(R2/'manifest.json')['resolved_findings']==['B1'])
ck('prior all108 smooth domain receipts intact',len(load(R1/'probe-receipts.json')['receipts'])==108 and all(r['domain']and r['smooth']for r in load(R1/'probe-receipts.json')['receipts']))
result={'identity':'independent-native-fixture-published15-v3-review','decision':'ACCEPTED for prospective fixture implementation source only','reviewer':'/root/md1997_source','author':'coordinator /root; original numerical-v1 /root/md1997_reference','blocking_findings':[],'source_checks':len(checks),'checks':checks,'source_files':582,'Git_reads_only':True,'builds':0,'compiler_calls':0,'compiled_calls':0,'numerical_success_observed':False,'independent_Ramberg_compliance_residual_Pa':err,'later_published_drift_check_required':True,'CI_implementation_accepted':False}
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
(D/'inputs.json').write_text(json.dumps({'manifests':{str(p/'manifest.json'):h for p,h in pins.items()},'Git_commit':commit,'published_test_solver_sha256':hashlib.sha256(published).hexdigest(),'source_freeze_sha256':sha(A/'source-freeze.json')},indent=2)+'\n')
print(json.dumps({'decision':result['decision'],'source_checks':len(checks),'compiled_calls':0,'Ramberg_residual_Pa':err}))
