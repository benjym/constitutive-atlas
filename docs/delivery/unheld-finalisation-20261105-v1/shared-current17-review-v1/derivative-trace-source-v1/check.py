from pathlib import Path
import hashlib,json,re,struct
N=Path('docs/delivery/unheld-finalisation-20261105-v1');P=N/'current17-derivative-trace-plan-v1';Q=N/'shared-current17-review-v1/derivative-trace-source-v1'
sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
ck('manifest exact',sha((P/'manifest.json').read_bytes())=='6bacfb356d611df1e65f26c05b630dd576d6ec3e859bfca33c328cc0798be76e')
for pin in json.loads((P/'manifest.json').read_text())['files']:
 f=P/pin['path'];ck('manifest member '+pin['path'],not f.is_symlink() and f.stat().st_size==pin['size_bytes'] and sha(f.read_bytes())==pin['sha256'])
r=json.loads((P/'recipe.json').read_text());c=json.loads((P/'parent-case.json').read_text())
for p in r['source_inputs']+list(r['tools'].values())+c['parent_provenance']+[r['parent_case'],r['case_wire']]:
 f=Path(p['path']);ck('input '+str(f),f.stat().st_size==p['bytes'] and sha(f.read_bytes())==p['sha256'])
s=Path(r['source_inputs'][0]['path']).read_text();logged=(P/'logged-controlled-step.inc').read_text();original=s[s.index('inline bool controlled_step('):s.index('// Research range',s.index('inline bool controlled_step('))]
ck('four complete removable markers',logged.count('/*TRACE_BEGIN*/')==logged.count('/*TRACE_END*/')==4)
ck('full controller byte exact',re.sub(r'/\*TRACE_BEGIN\*/.*?/\*TRACE_END\*/','',logged,flags=re.S).replace('logged_controlled_step(','controlled_step(',1)==original)
ck('logging snippets are calls only',re.findall(r'/\*TRACE_BEGIN\*/(.*?)/\*TRACE_END\*/',logged)==['trace_advance("outer",it,lateral,trial);','trace_residual(it,residual);','trace_derivative(it,slope,trial);','trace_line_search(it,a,test);'])
cpp=(P/'trace.cpp').read_text()
ck('logging references const', 'const Advance&a' in cpp and 'const ControlDerivative&d,const Advance&base' in cpp)
ck('one original controller call',cpp.count('atlas::logged_controlled_step(')==1 and 'parameters,1,axial,reference,current_axial,de,result,settings)' in cpp)
ck('display stability expression identical',re.search(r'const bool stable=(.*?);',cpp).group(1).replace('p.slope','probe.slope')==re.search(r'const bool stable=(.*?);',s).group(1))
parent=json.loads(Path(c['parent_provenance'][1]['path']).read_text());last=parent['points'][-1]
ck('genuine exact failed93 parent',parent['ok']is False and len(parent['points'])==93 and 'step 93' in parent['message'] and c['state']==last['state'] and c['parameters']==parent['parameters'])
decode=lambda x:struct.unpack('>d',bytes.fromhex(x))[0]
ck('binary64 controls and committed parent',last['control']==decode(c['control_bits92']) and c['axial']==decode(c['control_bits93'])-decode(c['control_bits92']) and c['current_axial']==last['strain'][0])
lines=(P/'case.bits.txt').read_text().splitlines();settings=c['settings']
ck('all wire settings exact',[decode(x) for x in lines[7].split()]==[settings['residual_tolerance'],settings['rate_tolerance']] and list(map(int,lines[8].split()))==[settings[x] for x in ('max_iterations','max_depth','max_substeps','max_backtracks')])
ck('wire norm/version source defaults',settings['norm']=='scaled_component_max' and settings['version']=='incremental-settings-0.1')
ck('reference original110k',c['reference']==110000==.5*(parent['initial'][1]+parent['initial'][2]))
ck('line search lateral field is alpha', 'trace_advance("line_search",it,alpha,a)' in cpp)
ck('diagnostic exit distinct from scientific success','const bool ok=atlas::logged_controlled_step' in cpp and '<<ok<<' in cpp and 'return 0; // A completed diagnostic may report the genuine controller failure.' in cpp)
# Reproduce author pure checks without editing their frozen packet.
code=(P/'check.py').read_text().replace('O=Path(__file__).resolve().parent;',f'O=Path({str(P)!r});').replace("(O/'check.stdout.json').write_text", "(Path("+repr(str(Q))+")/'author-check.stdout.json').write_text")
exec(compile(code,str(P/'check.py'),'exec'),{'__file__':str(Q/'check.py')})
(Q/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'compiled_calls':0},indent=2)+'\n')
print(json.dumps({'passed':True,'independent_checks':len(checks)}))
