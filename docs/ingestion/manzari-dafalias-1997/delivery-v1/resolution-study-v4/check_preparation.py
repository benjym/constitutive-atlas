"""Source-only exact fork, grid and semantics checks; no backend execution."""
from pathlib import Path
import ast,hashlib,json,math,struct
D=Path(__file__).resolve().parent;P=D.parent
old=json.loads((P/'execution-v3/requests.json').read_text());new=json.loads((D/'requests.json').read_text())
changes=json.loads((D/'changes.json').read_text());rows=[]
def add(name,passed,**extra):
 assert passed,name
 rows.append({'name':name,'passed':True,**extra})
for n in ['prepare.py','check_reports.py','check_parity.py']:
 original=(P/('parity-v6/check.py' if n=='check_parity.py' else 'execution-v3/'+n)).read_text()
 for c in changes[n]:
  assert c['old'] in original
  original=original.replace(c['old'],c['new'])
 add(n+'/only-listed-substitutions',original==(D/n).read_text())
for n in ['run_native.py','run_wasm.mjs']:add(n+'/byte-identical',(D/n).read_bytes()==(P/'execution-v3'/n).read_bytes())
for p in D.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
add('python-syntax',True)
add('all35cases',len(old['cases'])==len(new['cases'])==35)
head=lambda x:{k:v for k,v in x.items() if k not in ['cases','special','version']}
add('model-source-reference-parameters-settings',head(old)==head(new))
sp=json.loads(json.dumps(old['special']));sp['ad_parent_case']=sp['ad_parent_case'].replace('-512','-4096')
add('special-only-parent-id',sp==new['special'])
for a,b in zip(old['cases'],new['cases']):
 a=json.loads(json.dumps(a));res=a.get('resolution')
 if a['group'] in ['public','hydrostatic','elastic-cycle']:
  add(b['id']+'/entire-case-identical',a==b);continue
 count={128:2048,512:4096}[res];a['resolution']=count
 if a['group'] in ['axis','interior']:a['id']=a['id'].rsplit('-',1)[0]+'-'+str(count)
 if 'compare_to' in a:a['compare_to']=a['compare_to'].replace('-512','-4096')
 if 'restart_index'in a:a['restart_index']=2048
 keys=['coordinates','increments'] if a['kind']=='chain' else ['controls','controls_bits']
 for k in keys:a.pop(k)
 meta={k:v for k,v in b.items() if k not in keys}
 add(b['id']+'/unchanged-nongrid-semantics',a==meta)
 if b['kind']=='controls':
  coords=b['controls'];end=coords[-1];checks=[cp['axial_strain'] for cp in b['checkpoints']]
  expected=sorted(set([end*i/count for i in range(count+1)]+checks),reverse=end<0)
  add(b['id']+'/full-grid-and-all-checkpoints',coords==expected)
  add(b['id']+'/exact-binary64-bits',b['controls_bits']==[struct.pack('>d',x).hex() for x in coords])
  add(b['id']+'/existing-control-limit',len(coords)<=5001,points=len(coords))
 else:
  expected=sorted(set([.01*i/count for i in range(count+1)]+[cp['t'] for cp in b['checkpoints']]))
  add(b['id']+'/full-grid-and-all-checkpoints',b['coordinates']==expected)
  # Covariance intentionally rotates precomputed increments, preserving old operation order.
  if b['group']!='covariance':add(b['id']+'/all-increments-exact',b['increments']==[[b['direction'][j]*(v-u) for j in range(6)]for u,v in zip(expected,expected[1:])])
  else:add(b['id']+'/increment-count',len(b['increments'])==len(expected)-1)
add('fourteen-paths-two-resolutions',sum(c['group']in ['axis','interior'] for c in new['cases'])==28)
blocked=json.loads((D/'blocked-8192-v1/requests.json').read_text());over=[c['id'] for c in blocked['cases'] if c['kind']=='controls' and len(c['controls'])>5001]
add('blocked8192-eight-axis-calls-exceed-limit',len(over)==8,blocked_cases=over)
result={'identity':'md1997-resolution-preparation-checks-v4','status':'passed','compiled_calls':0,'checks':rows}
print(json.dumps(result,indent=2))
