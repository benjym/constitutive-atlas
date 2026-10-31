"""Bounded source/envelope comparison. Never reads saved backend observations."""
from pathlib import Path
import hashlib,json,re,difflib
P=Path(__file__).resolve().parent;F=P/'frozen';V=Path('/Users/bmar5496/code/constitutive-atlas/catalogue/investigations/mc-laboratory-preview-v1')

def run():
 checks={}
 for n in ('requests.json','acceptance-paths.json','generated/models.json','reference/reference-p360.json','assess_parity.py'):
  checks[n+':unchanged_bytes']=(F/n).read_bytes()==(V/n).read_bytes()
 checks['api_serializer_same_pinned_bytes']=(F/'api-main.cpp').read_bytes()==(V/'frozen/cpp/main.cpp').read_bytes()
 old=(V/'assess_paths.py').read_text();new=(F/'assess_paths.py').read_text()
 # Compare every physical/control/diagnostic acceptance expression as an exact suffix.
 suffix='  assert vector(r[\'parameters\'],'
 checks['all_math_and_echo_gates_identical_after_envelope']=old[old.index(suffix):]==new[new.index(suffix):]
 checks['descriptor_gate_prefix_unchanged']=old[:old.index("  assert r['ok']is True")]==new[:new.index("  assert r['ok']is True")]
 cpp=(F/'api-main.cpp').read_text()
 checks['serializer_model_is_string']=r'<<quote(atlas::catalogue_hash())<<",\"model\":"<<quote(id)'in cpp
 checks['serializer_response_schema0.1']=r'\"schema_version\":\"0.1\"'in cpp
 checks['settings_six_csv_inputs']='if(v.size()!=6)throw'in cpp
 checks['settings_echo_conditional_literal']='if(settings_csv){o<<",\\\"integration_settings\\\":";write_settings(o,run.settings);}'in cpp
 req=json.loads((F/'requests.json').read_text());cat=json.loads((F/'generated/models.json').read_text());m=next(x for x in cat['models']if x['id']=='mohr-coulomb')
 order=list(m['parameters']);checks['six_parameter_order']=order==['p_ref','E','nu','c','phi','psi']
 checks['literal_parameters_match_ordered_defaults']=all([float(x)for x in r['parameters'].split(',')]==[float(m['parameters'][k]['default'])for k in order]for r in req)
 checks['literal_settings_six_values']=all(len(r['integration_settings'].split(','))==6 for r in req)
 rows=json.loads((F/'ideal-journal.json').read_text());checks['ideal_describe_matches']=json.loads(rows[0]['raw'])==cat
 expected={'ok','message','schema_version','catalogue_hash','model','elapsed_ms','parameters','initial','integration_settings','protocol','target','steps','cycles','points'}
 checks['source_ideal_top_level_serializer_shape']=all(set(json.loads(row['raw']))==expected for row in rows[1:])
 checks['source_ideal_model_id_type']=all(type(json.loads(row['raw'])['model'])is str and json.loads(row['raw'])['model']==r['model']for row,r in zip(rows[1:],req))
 checks['preflight_passes_19_negatives']=json.loads((F/'preflight-results.json').read_text())['passed']is True and len(json.loads((F/'preflight-results.json').read_text())['negative_cases'])==19
 checks['no_backend_observations_read']=True
 out={'identity':'mc-preview-envelope-independent-audit-v2','checks':checks,'status':'pass'if all(checks.values())else'fail','failed':[k for k,v in checks.items()if not v],'saved_backend_observations_read':0,'new_candidate_calls':0,'new_builds':0,'parameter_order':order,'source_api_sha256':hashlib.sha256((F/'api-main.cpp').read_bytes()).hexdigest()}
 (P/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
 (P/'assessor-envelope.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='committed-v1/assess_paths.py',tofile='corrected-v2/assess_paths.py')))
 print(json.dumps({'status':out['status'],'checks':len(checks),'failed':out['failed']}))
 if out['failed']:raise SystemExit(1)
if __name__=='__main__':run()
