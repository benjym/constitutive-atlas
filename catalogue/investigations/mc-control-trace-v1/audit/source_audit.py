from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent;F=P/'frozen'
def function(text,signature):
 start=text.index(signature);b=text.index('){',start)+1;depth=0
 for i in range(b,len(text)):
  if text[i]=='{':depth+=1
  elif text[i]=='}':
   depth-=1
   if depth==0:return text[start:i+1]
 raise ValueError('unbalanced function')
def run():
 src=(F/'frozen/cpp/include/atlas/solver.hpp').read_text();d=(F/'driver.cpp').read_text();req=json.loads((F/'request.json').read_text());tr=json.loads((F/'transformation.json').read_text());checks={}
 original=function(src,'inline bool controlled_step(');traced=function(d,'inline bool traced_controlled_step(')
 reverse=traced.replace('traced_controlled_step','controlled_step')
 for role,it in [('direct','-1'),('trial','it'),('pert','it'),('test','it')]:reverse=reverse.replace(f'trace_integrate("{role}",{it},','integrate(')
 checks['controlled_step_reverse_exact']=reverse==original
 checks['original_solver_hash']=hashlib.sha256((F/'frozen/cpp/include/atlas/solver.hpp').read_bytes()).hexdigest()==tr['original_solver_sha256']
 control='cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps'
 orig_run=function(src,'inline Run run_protocol(')
 traced_run=function(d,'inline Run traced_run_protocol(').replace('traced_run_protocol','run_protocol').replace('traced_controlled_step','controlled_step').replace('literal_controls?common_controls[i-1]:('+control+')',control).replace('        active_step=i;\n','').replace('Sym<double> de;State parent;Advance result;','Sym<double> de;Advance result;')
 literal_run=function(d,'inline Run literal_run_protocol(').replace('literal_run_protocol','run_protocol').replace('double control=common_controls[i-1];','double control='+control+';').replace('Sym<double> de;State parent;Advance result;','Sym<double> de;Advance result;')
 checks['traced_run_reverse_exact_with_unused_parent_declaration_removed']=traced_run==orig_run
 checks['literal_run_reverse_exact_with_unused_parent_declaration_removed']=literal_run==orig_run
 vals=re.search(r'common_controls\[64\]=\{([^}]+)\}',d).group(1).split(',');checks['64_literal_control_bits']=len(vals)==len(req['common_controls_hex'])==64 and all(float.fromhex(a).hex()==b for a,b in zip(vals,req['common_controls_hex']))
 params=[float(x)for x in re.search(r'const State p=\{([^}]+)\}',d).group(1).split(',')];initial=[float(x)for x in re.search(r'const State initial=\{([^}]+)\}',d).group(1).split(',')]
 checks['parameters_request_bound']=params==req['parameters'];checks['initial_request_bound']=initial==req['initial']
 checks['64_two_stream_protocol_literal_binding']=req['protocol']==3 and req['target']==200000 and req['steps']==64 and req['cycles']==1 and req['streams']==['backend-sine','common-literal'] and 'model,initial,p,3,200000.,64,1,settings)'in d
 checks['wrapper_single_original_call_and_result_copy']='auto result=integrate(model,zn,de,p,settings);trace_calls.push_back({active_step,iteration,role,de,zn,result});return result;'in d
 checks['both_stream_baseline_and_traced_separate']='mode?literal_run_protocol'in d and ':run_protocol'in d and 'trace_calls.clear();auto traced=traced_run_protocol'in d
 result={'identity':'mc-control-trace-source-audit-v1','checks':checks,'status':'pass'if all(checks.values())else'fail','failed':[k for k,v in checks.items()if not v],'source_hashes':{'original_controlled_step_no_trailing_newline':hashlib.sha256(original.encode()).hexdigest(),'traced_controlled_step_no_trailing_newline':hashlib.sha256(traced.encode()).hexdigest()},'limitations':['Unused State parent declaration exists in both copied run loops; removal is required for textual reversal and does not change arithmetic.','Only call input/output is recorded; no direct raw tangent/correction/backtracking alpha trace.','Runtime fidelity against separate original baseline and complete original artifact remains a required later gate.']}
 (P/'source-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run()
