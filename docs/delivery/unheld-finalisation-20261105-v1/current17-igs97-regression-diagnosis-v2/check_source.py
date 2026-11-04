"""Source/declared metadata classification only; no generation or material call."""
from pathlib import Path
import ast,hashlib,json,re,copy
P=Path(__file__).resolve().parent;g=json.loads((P/'GATES.json').read_text());checks=[]
def check(n,v):assert v,n;checks.append(n)
def sha(b):return hashlib.sha256(b).hexdigest()
for label,pin in g['references'].items():
 q=Path(pin['path']);check('reference '+label,q.stat().st_size==pin['bytes'] and sha(q.read_bytes())==pin['sha256'])
refs=g['references'];current=Path(refs['current640_solver']['path']).read_text();prior=Path(refs['original702_solver']['path']).read_text();candidate=(P/'proposed/cpp/include/atlas/solver.hpp').read_text();before=(P/'old-block.txt').read_text();after=(P/'new-block.txt').read_text();oldhead=(P/'old-head.txt').read_text();newhead=(P/'new-head.txt').read_text()
check('exact640 inverse outside singleprotocol1 dispatch',candidate.replace(after,before).replace(newhead,oldhead)==current)
check('newtrait uses declared generated bit','field.multiplier' in newhead and 'models().at(model).rate||models().at(model).physical_time' in newhead)
check('no modelID/name dispatch',not any(x in newhead+after for x in ['duncan','manzari','igs97','norsand','drucker','cam-clay']))
normalized='\n'.join(line[4:] for line in after.split('            }else{\n',1)[1].rsplit('            }\n',1)[0].splitlines())+'\n'
check('declaredmultiplier audited body exact640',normalized.replace('if(!slope.ok)return false;derivative=slope.value;','if(!slope.ok)return false;const double derivative=slope.value;')==before)
rate='''double h=std::max(1e-9,std::abs(axial)*1e-3);auto dd=de;dd.v[1]=dd.v[2]=lateral+h;auto pert=integrate(model,zn,dd,p,settings);
            if(!pert.ok)return false;double derivative=(.5*(pert.state[1]+pert.state[2])-.5*(trial.state[1]+trial.state[2]))/h;'''
check('702original directional block source',rate in prior)
check('noMultiplier original directional arithmetic',rate.replace('\n            ','\n                ').replace('double derivative=','derivative=') in after)
# The whole protocol3 production branch remains exact702 and640.
def protocol3(s):return s[s.index('    // protocol 3:'):s.index('    (void)current_axial;return false;')]
check('stresscontrol exact702',protocol3(candidate)==protocol3(prior))
check('stresscontrol exact640',protocol3(candidate)==protocol3(current))
# Execute ONLY original pure metadata functions, never load/validate/evaluate a model.
modelsource=Path(refs['model_semantics']['path']).read_text();tree=ast.parse(modelsource);functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['state_role','integration_kind','physical_time']];env={};exec(compile(ast.Module(body=functions,type_ignores=[]),'original-metadata-functions','exec'),env)
compiler=Path(refs['compiler']['path']).read_text();check('compiler declaredrole exact',"str(state_role(f) == 'plastic_multiplier').lower()" in compiler)
check('source validates residual multiplier',"integration_kind(model)!='residual'" in modelsource and 'multipliers must be dimensionless transient scalars in residual models' in modelsource)
header=Path(refs['saved_generated_header']['path']).read_text();catalogue=json.loads(Path(refs['saved_generated_catalogue']['path']).read_text());lines=header[header.index('inline const std::vector<Model>& models()'):header.index('}; return data; }')].splitlines();generated={}
for line in lines:
 match=re.match(r'^\{("(?:[^"\\]|\\.)*"),("(?:[^"\\]|\\.)*"),(true|false),(true|false),\{',line)
 if not match:continue
 fields=[]
 for m in re.finditer(r'\{("(?:[^"\\]|\\.)*"), (\d+), (\d+), \{([^{}]*)\}, (true|false), (true|false)\}',line):
  fields.append({'name':json.loads(m[1]),'transient':m[5]=='true','multiplier':m[6]=='true'})
 generated[json.loads(match[1])]={'rate':match[3]=='true','physical_time':match[4]=='true','fields':fields}
check('exact17 generated metadata parsed',len(generated)==len(catalogue['models'])==17)
rows=[]
for model in catalogue['models']:
 fields=[{'name':f['name'],'role':env['state_role'](f),'transient':env['state_role'](f)!='persistent','multiplier':env['state_role'](f)=='plastic_multiplier'} for f in model['state']]
 rate=env['integration_kind'](model)=='rate';physical=env['physical_time'](model);meta=generated[model['id']]
 check('exactgenerated field traits '+model['id'],meta=={'rate':rate,'physical_time':physical,'fields':[{k:f[k] for k in ['name','transient','multiplier']} for f in fields]})
 multipliers=[f['name'] for f in fields if f['multiplier']];audited=bool(multipliers)
 check('validdeclared residualprofile '+model['id'],not audited or not rate and not physical and env['integration_kind'](model)=='residual')
 rows.append({'id':model['id'],'definition_sha256':sha((json.dumps(model,indent=2)+'\n').encode()),'equation_form':model.get('formulation',{}).get('equation_form',model.get('integration')),'rate':rate,'physical_time':physical,'fields':fields,'declared_multiplier_fields':multipliers,'controller':'640-partition-audited' if audited else '702-original-directional-FD','meaning':'declared predictor/multiplier residual profile; not general plasticity' if audited else 'historical algorithm; no smoothness/plasticity inference'})
# Use exact source definition bytes rather than a JSON reserialization as identity.
S=P.parent/'current17-runtime-source-v1/source';paths={json.loads(q.read_text())['id']:q for q in (S/'models').glob('*.json')}
for row in rows:
 check('source matches savedgenerated '+row['id'],json.loads(paths[row['id']].read_text())==next(m for m in catalogue['models'] if m['id']==row['id']));row['definition_sha256']=sha(paths[row['id']].read_bytes())
md=next(row for row in rows if row['id']=='manzari-dafalias-1997-constant-m-be-v1');dc=next(row for row in rows if row['id']=='duncan-chang-1970-endpoint-average')
check('MD retains audited control',md['controller']=='640-partition-audited' and md['declared_multiplier_fields'])
check('Duncan noMultiplier retains702',dc['controller']=='702-original-directional-FD' and not dc['declared_multiplier_fields'])
# Label-independent metadata witnesses use the exact original state_role function.
for field,expected in [({'name':'arbitrary','semantics':{'role':'plastic_multiplier'}},True),({'name':'gamma','semantics':{'role':'persistent'}},False),({'name':'arbitrary','multiplier':True,'transient':True},True),({'name':'plastic','transient':True},False)]:
 check('semanticrole not fieldname '+str(field), (env['state_role'](field)=='plastic_multiplier') is expected)
(P/'classification17.json').write_text(json.dumps({'identity':'declared-generated-multiplier-profile-classification17-v1','source_generated_header':refs['saved_generated_header'],'source_generated_catalogue':refs['saved_generated_catalogue'],'models':rows},indent=2)+'\n')
(P/'source-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'count':len(checks),'model_compiler_or_material_calls':0},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'audited':[r['id'] for r in rows if r['controller']=='640-partition-audited'],'historical':[r['id'] for r in rows if r['controller']=='702-original-directional-FD']}))
