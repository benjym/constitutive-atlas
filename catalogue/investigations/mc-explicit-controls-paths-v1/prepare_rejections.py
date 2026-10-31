from pathlib import Path
import json,copy
p=Path(__file__).parent;requests=json.loads((p/'requests.json').read_text());base=next(x for x in requests if x['id']=='drained-default/100')
cases=[]
def add(name,**changes):
 r=copy.deepcopy(base);r.update(changes);r['id']=name;r['expected_ok']=False;cases.append(r)
add('initial-past-apex',initial='-20000,-20000,-20000,0,0,0')
add('initial-outside-yield',initial='1000000,100000,100000,0,0,0')
add('initial-nonaxisymmetric',initial='100000,100000,100000,0.001,0,0')
for index,name in [(3,'zero-cohesion'),(4,'zero-friction'),(5,'zero-dilation')]:
 values=base['parameters'].split(',');values[index]='0';add(name,parameters=','.join(values))
add('invalid-settings',integration_settings='-1,1e-6,45,14,20000,11')
add('missing-explicit-initial',initial='')
add('nonzero-control-origin',controls_bits_csv='3ff0000000000000,'+base['controls_bits_csv'].split(',',1)[1])
for original in cases[:3]:
 r=copy.deepcopy(original);r['id']='legacy-'+r['id'];r['mode']='run';cases.append(r)
(p/'rejection-requests.json').write_text(json.dumps({'recovery_request_id':base['id'],'expected_invalid_points':0,'cases':cases},indent=2,sort_keys=True)+'\n')
